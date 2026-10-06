"""Match ingredient text against data/ingredients.csv (all matches per token, then fuzzy)."""
import re
from difflib import get_close_matches
from pathlib import Path

import pandas as pd

from text_processor import split_ingredients

try:
    from rapidfuzz import fuzz, process
except ImportError:  # fallback if rapidfuzz is missing
    fuzz = process = None

DB_PATH = Path(__file__).parent / "data" / "ingredients.csv"
ORDER = {"bad": 0, "warn": 1, "good": 2, "ok": 3}


def load_db() -> pd.DataFrame:
    df = pd.read_csv(DB_PATH)
    df["alias_list"] = df.apply(
        lambda r: [r["name"].lower()] + [a.strip().lower() for a in str(r["aliases"]).split("|") if a.strip()],
        axis=1,
    )
    return df


def _span(alias: str, token: str):
    if len(alias) <= 3:  # short aliases (msg, bha) need word boundaries
        m = re.search(rf"(^|[^a-z0-9]){re.escape(alias)}([^a-z0-9]|$)", token)
        return (m.start() + len(m.group(1)), m.end() - len(m.group(2))) if m else None
    i = token.find(alias)
    return (i, i + len(alias)) if i >= 0 else None


def match_all(token: str, df: pd.DataFrame, category: str):
    """Find every database ingredient inside one token (merged OCR text can hold several)."""
    sub = df[df["category"] == category]
    cands = []
    for idx, row in sub.iterrows():
        best = None
        for a in row["alias_list"]:
            sp = _span(a, token)
            if sp and (best is None or sp[1] - sp[0] > best[1] - best[0]):
                best = sp
        if best:
            cands.append((best, idx))
    cands.sort(key=lambda c: -(c[0][1] - c[0][0]))  # longest match wins when spans overlap
    taken, out = [], []
    for (s, e), idx in cands:
        if all(e <= ts or s >= te for ts, te in taken):
            taken.append((s, e))
            out.append(idx)
    return [df.loc[i] for i in out]


def _fuzzy(token: str, df: pd.DataFrame, category: str):
    if len(token) < 5:
        return None
    sub = df[df["category"] == category]
    pool = {a: i for i, aliases in zip(sub.index, sub["alias_list"]) for a in aliases if len(a) >= 5}
    if not pool:
        return None
    if process:
        best = process.extractOne(token, list(pool), scorer=fuzz.ratio, score_cutoff=86)
        key = best[0] if best else None
    else:
        m = get_close_matches(token, list(pool), n=1, cutoff=0.86)
        key = m[0] if m else None
    return df.loc[pool[key]] if key else None


def match_token(token: str, df: pd.DataFrame, category: str):
    rows = match_all(token, df, category)
    if rows:
        return rows, "exact"
    f = _fuzzy(token, df, category)
    return ([f], "fuzzy") if f is not None else ([], None)


def analyze(text: str, category: str, df: pd.DataFrame):
    hits, unknown, seen = [], [], set()
    for tok in split_ingredients(text):
        rows, how = match_token(tok, df, category)
        if not rows:
            if tok not in unknown:
                unknown.append(tok)
            continue
        for row in rows:
            if row["name"] not in seen:
                seen.add(row["name"])
                hits.append({**row.to_dict(), "found_as": tok, "method": how})
    hits.sort(key=lambda h: ORDER[h["level"]])
    return hits, unknown


SAFE_LABEL = {"good": "✅ Safe", "ok": "✅ Safe", "warn": "⚠️ Limit", "bad": "❌ Avoid"}


def safety_verdict(hits, unknown_skeys=()):
    """Big, simple verdict: (key, emoji, title, subtitle). General guidance, not a medical ruling.
    unknown_skeys: guesses for unknown items ('ok' / 'limit' / 'check')."""
    bad = [h for h in hits if h["level"] == "bad"]
    warn = [h["name"] for h in hits if h["level"] == "warn"]
    limit_unknown = sum(k == "limit" for k in unknown_skeys)
    unclear = sum(k == "check" for k in unknown_skeys)
    total = len(hits) + len(unknown_skeys)
    n_warn = len(warn) + limit_unknown
    if bad:
        return "bad", "❌", "NOT RECOMMENDED", f"Contains {len(bad)} ingredient(s) worth avoiding: {', '.join(h['name'] for h in bad)}"
    if n_warn >= 3:
        return "warn", "⚠️", "LIMIT IT", f"{n_warn} ingredients to watch. Fine occasionally, not every day"
    if total and unclear / total > 0.4:
        return "mid", "🤔", "NOT ENOUGH INFO", f"We could not identify {unclear} of {total} items. Check the label manually"
    if n_warn:
        return "mid", "🙂", "MOSTLY OK", f"{n_warn} ingredient(s) to watch" + (": " + ", ".join(warn) if warn else "")
    return "good", "✅", "GENERALLY SAFE", "No flagged ingredients among those we recognise"


def verdict(hits):
    bad = [h["name"] for h in hits if h["level"] == "bad"]
    warn = [h for h in hits if h["level"] == "warn"]
    if bad:
        return "bad", f"Alert: {len(bad)} ingredient(s) worth avoiding: {', '.join(bad)}."
    if warn:
        return "warn", f"{len(warn)} ingredient(s) to use with care. No high-concern ingredient found."
    return "good", "No flagged ingredients found among those we recognise."


def search(query: str, df: pd.DataFrame):
    q = query.strip().lower()
    if len(q) < 2:
        return []
    return [r for _, r in df.iterrows() if q in r["name"].lower() or any(q in a for a in r["alias_list"])]


def compare(hits_a, hits_b):
    """Compare two products by ingredient overlap and number of flagged items."""
    names_a = {h["name"]: h for h in hits_a}
    names_b = {h["name"]: h for h in hits_b}

    def score(hits):  # lower = fewer concerns
        return sum({"bad": 3, "warn": 1, "good": -1, "ok": 0}[h["level"]] for h in hits)

    sa, sb = score(hits_a), score(hits_b)
    winner = "A" if sa < sb else "B" if sb < sa else "tie"
    return {
        "only_a": [names_a[n] for n in names_a if n not in names_b],
        "only_b": [names_b[n] for n in names_b if n not in names_a],
        "common": [names_a[n] for n in names_a if n in names_b],
        "score_a": sa, "score_b": sb, "fewer_concerns": winner,
    }