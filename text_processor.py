"""Clean OCR text, find the ingredient / nutrition sections, split into tokens."""
import re
import unicodedata

OCR_FIXES = {"equator": "regulator", "flouy": "flour", "depper": "pepper", "olls": "oils", "oll": "oil", "contin": "contain", "sugsr": "sugar"}

_STOP = r"(nutrition|nutritional|allergen|note\s*:|may contain|contains (wheat|milk|soy|nuts?|gluten|mustard|egg)|manufactured|marketed|best before|mfg|net (wt|qty)|directions|how to use|storage)"
_CLASS = r"(?:thickeners?|acidity regulators?|colou?rs?|colou?ring|humectants?|emulsifiers?|preservatives?|antioxidants?|stabili[sz]ers?|flavou?r enhancers?|raising agents?|anti-?caking agents?|sweeteners?|minerals?)"
_ITEM = r"\d{3,4}[a-d]?(?:\s*\([ivx]+\)?)?"
_GROUP = re.compile(_CLASS + r"s?\s*\(\s*(" + _ITEM + r"(?:\s*(?:&|,|/|and)\s*" + _ITEM + r")*)\s*\)?", re.I)
_STOPWORDS = {"and", "of", "with", "contains", "may", "contain", "note", "allergen"}


def clean_ocr_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("|", "I")
    text = re.sub(r"-\s*\n\s*", "", text)               # re-join words split across lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\b[l1I]ngredients?\b", "Ingredients", text, flags=re.I)  # 'lngredients'
    return text.strip()


def apply_ocr_fixes(text: str) -> str:
    """Fix common OCR slips such as 'equator' -> 'regulator' and 'flouy' -> 'flour'."""
    for bad, good in OCR_FIXES.items():
        text = re.sub(rf"\b{bad}\b", good, text, flags=re.I)
    return text


def extract_ingredients(text: str) -> str:
    """Keep only the ingredient section (tolerates OCR typos in the word 'Ingredients')."""
    flat = re.sub(r"\s+", " ", apply_ocr_fixes(clean_ocr_text(text))).strip()
    m = re.search(r"\b\w{0,3}ngred\w{0,6}\s*[:\-]", flat, re.I)
    rest = flat[m.end():] if m else flat
    stop = re.search(_STOP, rest, re.I)
    return (rest[: stop.start()] if stop else rest).strip()


def extract_nutrition_block(text: str) -> str:
    """Return the text from 'Nutrition' onwards (keeps line breaks for the parser)."""
    cleaned = clean_ocr_text(text)
    m = re.search(r"nutrition(al)?\s*(information|facts|value)?", cleaned, re.I)
    return cleaned[m.start():] if m else cleaned


def _codes(inner: str):
    out = []
    for num, suf in re.findall(r"(\d{3,4})\s*([a-d])?", inner.lower()):
        if len(num) == 4 and num.startswith("150") and not suf and num[3] in "1234":
            num, suf = "150", "abcd"[int(num[3]) - 1]  # OCR often reads 150d as 1504
        out.append(f"e{num}{suf}")
    return out


def split_ingredients(text: str):
    """Split into items. Understands 'Thickeners (508 & 412)' and sub-lists in brackets."""
    t = apply_ocr_fixes(re.sub(r"[®™*]", "", text))
    codes = []

    def grab(m):
        codes.extend(_codes(m.group(1)))
        return " , "

    t = _GROUP.sub(grab, t)
    t = re.sub(r"[()\[\]]", ",", t)
    out = []
    for p in re.split(r"[,;:\n•]+|\.\s", t) + codes:
        p = re.sub(r"\s+", " ", p).strip(" .:-&").lower()
        p = re.sub(r"^(and|contains|with)\s+", "", p)
        if len(p) < 2 or p in _STOPWORDS or not re.search(r"[a-z]", p):
            continue
        out.append(p)
    return out