<<<<<<< HEAD
"""Parse a nutrition table, scale to the quantity eaten, and give general guidance."""
import re

# label -> (regex that must appear on the line, words that must NOT appear)
LABELS = {
    "calories": (r"energy|calories?", r""),
    "protein": (r"protein", r""),
    "carbs": (r"carbohydrate", r""),
    "sugar": (r"sugars?", r""),
    "fat": (r"\bfat", r"saturated|trans|polyunsat|monounsat|\bsat\b"),
    "sat_fat": (r"saturated|\bsat\.? ?fat", r""),
    "fibre": (r"fib(re|er)", r""),
    "sodium_mg": (r"sodium", r""),
}
NUM = r"(\d+(?:[.,]\d+)?)\s*(kcal|mg|g|mcg|kj)?"
NAMES = {"calories": "Energy (kcal)", "protein": "Protein (g)", "carbs": "Carbohydrate (g)", "sugar": "Sugar (g)",
         "fat": "Total fat (g)", "sat_fat": "Saturated fat (g)", "fibre": "Fibre (g)", "sodium_mg": "Sodium (mg)"}

# General per-100 g bands (low, high), based on common front-of-pack traffic-light guidance
BANDS = {"sugar": (5, 22.5), "fat": (3, 17.5), "sat_fat": (1.5, 5), "sodium_mg": (120, 600)}
# Rough adult daily reference (2000 kcal diet)
DAILY = {"calories": 2000, "protein": 50, "carbs": 260, "sugar": 50, "fat": 70, "sat_fat": 20, "fibre": 25, "sodium_mg": 2000}

WHY = {
    "sugar": "WHO advises keeping free sugars below about 10% of daily energy (roughly 50 g). Regular excess raises the risk of weight gain, tooth decay and type 2 diabetes.",
    "sodium_mg": "WHO advises under 5 g salt (about 2000 mg sodium) a day. Regular excess raises blood pressure and heart-disease risk.",
    "sat_fat": "Health bodies advise keeping saturated fat low (about 10% of energy). Regular excess raises LDL cholesterol.",
    "fat": "High total fat means high calories; fat type matters more than the total.",
    "calories": "Eating more energy than you use over time leads to weight gain.",
}


def _num(s):
    return float(s.replace(",", "."))


def parse_nutrition(text: str) -> dict:
    """Return {'values': {...}, 'serving_g': float|None, 'per100_hint': bool}."""
    values, salt_g = {}, None
    for line in text.lower().splitlines():
        if "salt" in line and salt_g is None:
            m = re.search(r"salt[^0-9]{0,15}" + NUM, line)
            if m:
                salt_g = _num(m.group(1))
        for key, (pat, skip) in LABELS.items():
            if key in values:
                continue
            m = re.search(pat, line)
            if not m or (skip and re.search(skip, line)):
                continue
            rest = line[m.end():]
            if key == "calories":
                k = re.search(r"(\d+(?:[.,]\d+)?)\s*kcal", rest) or re.search(r"(\d+(?:[.,]\d+)?)\s*kcal", line)
                if k:
                    values[key] = _num(k.group(1))
                continue
            n = re.search(NUM, rest)
            if n:
                v, unit = _num(n.group(1)), n.group(2)
                if key == "sodium_mg" and unit == "g":
                    v *= 1000
                values[key] = v
    if "sodium_mg" not in values and salt_g is not None:
        values["sodium_mg"] = salt_g * 400  # 1 g salt is about 400 mg sodium
    sv = re.search(r"serv(?:ing|e)\s*size[^0-9\n]{0,15}(\d+(?:[.,]\d+)?)\s*(g|ml)", text.lower())
    return {"values": values, "serving_g": _num(sv.group(1)) if sv else None, "per100_hint": "per 100" in text.lower()}


def scale(values: dict, basis_amount: float, eaten: float) -> dict:
    """values are for `basis_amount` (g); return amounts for `eaten` (g)."""
    f = eaten / basis_amount if basis_amount else 0
    return {k: v * f for k, v in values.items()}


def traffic_lights(values: dict, basis_amount: float) -> dict:
    """Classify per-100 g amounts as low / medium / high."""
    out = {}
    for k, (lo, hi) in BANDS.items():
        if k in values and basis_amount:
            v = values[k] * 100 / basis_amount
            out[k] = ("low" if v <= lo else "high" if v > hi else "medium", round(v, 1))
    return out


def daily_share(eaten_values: dict):
    return [
        {"Nutrient": NAMES[k], "Amount": round(v, 1), "% of daily reference": round(v / DAILY[k] * 100)}
        for k, v in eaten_values.items() if k in DAILY
    ]


def excess_notes(eaten_values: dict):
    """Plain-language notes when the chosen quantity gives a large share of the daily reference."""
    notes = []
    for k in ("sugar", "sodium_mg", "sat_fat", "fat", "calories"):
        if k in eaten_values:
            pct = eaten_values[k] / DAILY[k] * 100
            if pct >= 40:
                notes.append(f"{NAMES[k]}: this amount gives about {pct:.0f}% of the daily reference. {WHY[k]}")
=======
"""Parse a nutrition table, scale to the quantity eaten, and give general guidance."""
import re

# label -> (regex that must appear on the line, words that must NOT appear)
LABELS = {
    "calories": (r"energy|calories?", r""),
    "protein": (r"protein", r""),
    "carbs": (r"carbohydrate", r""),
    "sugar": (r"sugars?", r""),
    "fat": (r"\bfat", r"saturated|trans|polyunsat|monounsat|\bsat\b"),
    "sat_fat": (r"saturated|\bsat\.? ?fat", r""),
    "fibre": (r"fib(re|er)", r""),
    "sodium_mg": (r"sodium", r""),
}
NUM = r"(\d+(?:[.,]\d+)?)\s*(kcal|mg|g|mcg|kj)?"
NAMES = {"calories": "Energy (kcal)", "protein": "Protein (g)", "carbs": "Carbohydrate (g)", "sugar": "Sugar (g)",
         "fat": "Total fat (g)", "sat_fat": "Saturated fat (g)", "fibre": "Fibre (g)", "sodium_mg": "Sodium (mg)"}

# General per-100 g bands (low, high), based on common front-of-pack traffic-light guidance
BANDS = {"sugar": (5, 22.5), "fat": (3, 17.5), "sat_fat": (1.5, 5), "sodium_mg": (120, 600)}
# Rough adult daily reference (2000 kcal diet)
DAILY = {"calories": 2000, "protein": 50, "carbs": 260, "sugar": 50, "fat": 70, "sat_fat": 20, "fibre": 25, "sodium_mg": 2000}

WHY = {
    "sugar": "WHO advises keeping free sugars below about 10% of daily energy (roughly 50 g). Regular excess raises the risk of weight gain, tooth decay and type 2 diabetes.",
    "sodium_mg": "WHO advises under 5 g salt (about 2000 mg sodium) a day. Regular excess raises blood pressure and heart-disease risk.",
    "sat_fat": "Health bodies advise keeping saturated fat low (about 10% of energy). Regular excess raises LDL cholesterol.",
    "fat": "High total fat means high calories; fat type matters more than the total.",
    "calories": "Eating more energy than you use over time leads to weight gain.",
}


def _num(s):
    return float(s.replace(",", "."))


def parse_nutrition(text: str) -> dict:
    """Return {'values': {...}, 'serving_g': float|None, 'per100_hint': bool}."""
    values, salt_g = {}, None
    for line in text.lower().splitlines():
        if "salt" in line and salt_g is None:
            m = re.search(r"salt[^0-9]{0,15}" + NUM, line)
            if m:
                salt_g = _num(m.group(1))
        for key, (pat, skip) in LABELS.items():
            if key in values:
                continue
            m = re.search(pat, line)
            if not m or (skip and re.search(skip, line)):
                continue
            rest = line[m.end():]
            if key == "calories":
                k = re.search(r"(\d+(?:[.,]\d+)?)\s*kcal", rest) or re.search(r"(\d+(?:[.,]\d+)?)\s*kcal", line)
                if k:
                    values[key] = _num(k.group(1))
                continue
            n = re.search(NUM, rest)
            if n:
                v, unit = _num(n.group(1)), n.group(2)
                if key == "sodium_mg" and unit == "g":
                    v *= 1000
                values[key] = v
    if "sodium_mg" not in values and salt_g is not None:
        values["sodium_mg"] = salt_g * 400  # 1 g salt is about 400 mg sodium
    sv = re.search(r"serv(?:ing|e)\s*size[^0-9\n]{0,15}(\d+(?:[.,]\d+)?)\s*(g|ml)", text.lower())
    return {"values": values, "serving_g": _num(sv.group(1)) if sv else None, "per100_hint": "per 100" in text.lower()}


def scale(values: dict, basis_amount: float, eaten: float) -> dict:
    """values are for `basis_amount` (g); return amounts for `eaten` (g)."""
    f = eaten / basis_amount if basis_amount else 0
    return {k: v * f for k, v in values.items()}


def traffic_lights(values: dict, basis_amount: float) -> dict:
    """Classify per-100 g amounts as low / medium / high."""
    out = {}
    for k, (lo, hi) in BANDS.items():
        if k in values and basis_amount:
            v = values[k] * 100 / basis_amount
            out[k] = ("low" if v <= lo else "high" if v > hi else "medium", round(v, 1))
    return out


def daily_share(eaten_values: dict):
    return [
        {"Nutrient": NAMES[k], "Amount": round(v, 1), "% of daily reference": round(v / DAILY[k] * 100)}
        for k, v in eaten_values.items() if k in DAILY
    ]


def excess_notes(eaten_values: dict):
    """Plain-language notes when the chosen quantity gives a large share of the daily reference."""
    notes = []
    for k in ("sugar", "sodium_mg", "sat_fat", "fat", "calories"):
        if k in eaten_values:
            pct = eaten_values[k] / DAILY[k] * 100
            if pct >= 40:
                notes.append(f"{NAMES[k]}: this amount gives about {pct:.0f}% of the daily reference. {WHY[k]}")
>>>>>>> e5d2695 (LabelLens AI)
    return notes