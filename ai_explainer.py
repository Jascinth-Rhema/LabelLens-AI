"""Plain-language explanation + confidence. Works offline; Claude API is optional."""
import os


def confidence(n_hits: int, n_unknown: int, ocr_conf: float | None):
    total = n_hits + n_unknown
    coverage = n_hits / total if total else 0
    level = "High" if coverage >= 0.7 else "Medium" if coverage >= 0.4 else "Low"
    reason = f"We recognised {n_hits} of {total} items ({coverage:.0%})."
    if ocr_conf is not None and ocr_conf < 60:
        level = "Low"
        reason += f" OCR confidence was only {ocr_conf:.0f}%, so verify the label manually."
    if n_unknown:
        reason += " Unrecognised items are shown as Unknown, not guessed."
    return level, reason


def summarize(hits, unknown, level: str, category: str) -> str:
    kind = "food" if category == "f" else "skincare / personal-care"
    bad = [h["name"] for h in hits if h["level"] == "bad"]
    warn = [h["name"] for h in hits if h["level"] == "warn"]
    good = [h["name"] for h in hits if h["level"] == "good"]
    parts = [f"This {kind} label has {len(hits)} ingredients we recognise."]
    if bad:
        parts.append("Worth avoiding or limiting: " + ", ".join(bad) + ".")
    if warn:
        parts.append("Use with care: " + ", ".join(warn) + ".")
    if good:
        parts.append("Helpful ingredients: " + ", ".join(good) + ".")
    if not (bad or warn or good):
        parts.append("None of them raised a concern, but the list may be incomplete.")
    if category == "s":
        parts.append("Labels do not show concentrations, so this cannot say the whole product is safe or unsafe.")
    else:
        parts.append("Amounts are not on the ingredient list; check the nutrition table for quantities.")
    return " ".join(parts)


def llm_available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def llm_explain(ingredients_text: str, category: str) -> str:
    """Optional: richer explanation from Claude. Needs `pip install anthropic` and ANTHROPIC_API_KEY."""
    try:
        import anthropic

        client = anthropic.Anthropic()
        kind = "food" if category == "f" else "skincare"
        msg = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=700,
            messages=[{"role": "user", "content": (
                f"Explain this {kind} ingredient list in simple language: what each main ingredient does, one benefit "
                "and one possible concern. Do not call the product safe or unsafe, and say when you are unsure.\n\n" + ingredients_text)}],
        )
        return msg.content[0].text
    except Exception as e:
        return f"AI explanation unavailable: {e}"


def llm_explain_unknown(items: list, category: str) -> str:
    """Optional: ask Claude to explain unrecognised ingredients. Needs `pip install anthropic` and ANTHROPIC_API_KEY."""
    try:
        import anthropic

        client = anthropic.Anthropic()
        kind = "food" if category == "f" else "skincare"
        msg = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=900,
            messages=[{"role": "user", "content": (
                f"These {kind} label items were not recognised: {', '.join(items)}. For each, say what it most likely is "
                "and what it is used for, in simple words. If it could be an OCR typo, say so. Do not call anything safe or unsafe, "
                "and say clearly when you are unsure.")}],
        )
        return msg.content[0].text
    except Exception as e:
        return f"AI explanation unavailable: {e}"


SAFE_TA = {
    "good": "பொதுவாக பாதுகாப்பானது",
    "mid": "பெரும்பாலும் சரி, சில ingredients-ஐ கவனிக்கவும்",
    "warn": "அடிக்கடி வேண்டாம், அளவோடு எடுத்துக்கொள்ளவும்",
    "bad": "தவிர்ப்பது நல்லது",
}


def tamil_summary(hits, unknown, category: str, key: str) -> str:
    kind = "உணவு" if category == "f" else "அழகு / தோல் பராமரிப்பு"
    bad = [h["name"] for h in hits if h["level"] == "bad"]
    warn = [h["name"] for h in hits if h["level"] == "warn"]
    good = [h["name"] for h in hits if h["level"] == "good"]
    p = [f"இந்த {kind} label-ல் நமக்கு தெரிந்த {len(hits)} ingredients உள்ளன."]
    if bad:
        p.append("❌ தவிர்க்க வேண்டியவை: " + ", ".join(bad) + ".")
    if warn:
        p.append("⚠️ அளவோடு / கவனமாக பயன்படுத்தவும்: " + ", ".join(warn) + ".")
    if good:
        p.append("✅ நல்லவை: " + ", ".join(good) + ".")
    if unknown:
        p.append(f"{len(unknown)} ingredients பற்றி நம்மிடம் தகவல் இல்லை; label-ஐ நேரில் சரிபார்க்கவும்.")
    p.append("மொத்தத்தில்: " + SAFE_TA[key] + ".")
    p.append("இது பொதுவான தகவல் மட்டுமே, மருத்துவ ஆலோசனை அல்ல.")
    return " ".join(p)


def build_report(hits, unknown, category: str, title: str, subtitle: str, swaps) -> str:
    from datetime import datetime

    kind = "Food" if category == "f" else "Skincare / personal care"
    lines = ["LABELLENS AI REPORT", "=" * 40, f"Date: {datetime.now():%Y-%m-%d %H:%M}", f"Type: {kind}", "",
             f"VERDICT: {title}", subtitle, "", "RECOGNISED INGREDIENTS"]
    for h in hits:
        tag = {"good": "SAFE", "ok": "SAFE", "warn": "LIMIT", "bad": "AVOID"}[h["level"]]
        lines += [f"- [{tag}] {h['name']}", f"    What: {h['what']}", f"    Advantage: {h['advantage']}", f"    Disadvantage: {h['disadvantage']}"]
    if unknown:
        lines += ["", "UNKNOWN (check manually): " + ", ".join(unknown)]
    if swaps:
        lines += ["", "HEALTHIER SWAPS"] + [f"- Instead of {n}: {t}" for n, t in swaps]
    lines += ["", "General information only, not medical advice. Ingredient amounts are usually not on labels."]
    return "\n".join(lines)