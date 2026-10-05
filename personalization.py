<<<<<<< HEAD
"""Personal profile (skin tone, concern, food goal) and rule-based personal notes."""
from dataclasses import asdict, dataclass

SKIN_TONES = ["Fair", "Medium / wheatish", "Tan / brown", "Deep / dark brown"]
CONCERNS = ["Dark spots / uneven tone", "Dull skin", "Acne-prone", "Dry skin", "Sun protection"]
FOOD_GOALS = ["None", "Lower sugar", "Lower sodium"]


@dataclass
class Profile:
    skin_tone: str = "Medium / wheatish"
    concern: str = "Dark spots / uneven tone"
    food_goal: str = "None"
    kids_mode: bool = False

    def to_dict(self):
        return asdict(self)


_IRRITANT_ACTIVES = {"Glycolic / lactic acid (AHA)", "Hydroquinone", "Retinol / retinoids", "Kojic acid", "Salicylic acid", "Benzoyl peroxide"}
_DRYING = {"Sulfates (SLS / SLES)", "Alcohol denat.", "Benzoyl peroxide", "Salicylic acid", "Retinol / retinoids"}
_COMEDOGENIC = {"Mineral oil / petrolatum", "Shea butter", "Dimethicone / silicones"}
_SUGAR = {"Sugar", "High fructose corn syrup"}
_SODIUM = {"Salt / sodium", "MSG (monosodium glutamate)", "Sodium benzoate"}


def personal_notes(hits, category: str, p: Profile):
    names = {h["name"] for h in hits}
    notes = []
    if category == "s":
        deep = p.skin_tone in ("Tan / brown", "Deep / dark brown")
        if deep and names & _IRRITANT_ACTIVES:
            notes.append("Your tone is more prone to dark marks after irritation. Patch-test, start slowly and use sunscreen with: " + ", ".join(sorted(names & _IRRITANT_ACTIVES)) + ".")
        if p.skin_tone == "Deep / dark brown" and "Zinc oxide / mineral UV filter" in names:
            notes.append("Untinted mineral sunscreen can look ashy on deep skin. Look for a tinted or clear-gel version.")
        if p.concern == "Acne-prone" and names & _COMEDOGENIC:
            notes.append("May feel heavy on acne-prone skin: " + ", ".join(sorted(names & _COMEDOGENIC)) + ".")
        if p.concern == "Dry skin" and names & _DRYING:
            notes.append("Could dry your skin further: " + ", ".join(sorted(names & _DRYING)) + ".")
        if p.concern == "Dark spots / uneven tone" and names & {"Niacinamide (vitamin B3)", "Vitamin C (ascorbic acid)"}:
            notes.append("Helpful for your concern: niacinamide / vitamin C are commonly used for uneven tone. Pair with daily sunscreen.")
        if "Fragrance / parfum" in names:
            notes.append("Contains fragrance, a common irritant. Patch-test if your skin is sensitive.")
    else:
        if p.food_goal == "Lower sugar" and names & _SUGAR:
            notes.append("Matches your goal to cut sugar: contains " + ", ".join(sorted(names & _SUGAR)) + ".")
        if p.food_goal == "Lower sodium" and names & _SODIUM:
            notes.append("Matches your goal to cut sodium: contains " + ", ".join(sorted(names & _SODIUM)) + ".")
    return notes


_KIDS_FOOD = {"MSG (monosodium glutamate)", "Artificial sweeteners", "BHA / BHT", "Sodium benzoate", "Caramel colour", "Maltodextrin"}
_KIDS_SKIN = {"Fragrance / parfum", "Retinol / retinoids", "Salicylic acid", "Glycolic / lactic acid (AHA)", "Benzoyl peroxide",
              "Kojic acid", "Sulfates (SLS / SLES)", "Parabens"}


def apply_kids(hits, category: str):
    """Kids mode: treat extra ingredients as 'avoid' because children are more sensitive."""
    kid_set = _KIDS_FOOD if category == "f" else _KIDS_SKIN
    out = []
    for h in hits:
        h = dict(h)
        if h["name"] in kid_set and h["level"] in ("warn", "ok"):
            h["level"] = "bad"
            h["disadvantage"] = "Kids mode: best avoided for children. " + h["disadvantage"]
        out.append(h)
    out.sort(key=lambda x: {"bad": 0, "warn": 1, "good": 2, "ok": 3}[x["level"]])
=======
"""Personal profile (skin tone, concern, food goal) and rule-based personal notes."""
from dataclasses import asdict, dataclass

SKIN_TONES = ["Fair", "Medium / wheatish", "Tan / brown", "Deep / dark brown"]
CONCERNS = ["Dark spots / uneven tone", "Dull skin", "Acne-prone", "Dry skin", "Sun protection"]
FOOD_GOALS = ["None", "Lower sugar", "Lower sodium"]


@dataclass
class Profile:
    skin_tone: str = "Medium / wheatish"
    concern: str = "Dark spots / uneven tone"
    food_goal: str = "None"
    kids_mode: bool = False

    def to_dict(self):
        return asdict(self)


_IRRITANT_ACTIVES = {"Glycolic / lactic acid (AHA)", "Hydroquinone", "Retinol / retinoids", "Kojic acid", "Salicylic acid", "Benzoyl peroxide"}
_DRYING = {"Sulfates (SLS / SLES)", "Alcohol denat.", "Benzoyl peroxide", "Salicylic acid", "Retinol / retinoids"}
_COMEDOGENIC = {"Mineral oil / petrolatum", "Shea butter", "Dimethicone / silicones"}
_SUGAR = {"Sugar", "High fructose corn syrup"}
_SODIUM = {"Salt / sodium", "MSG (monosodium glutamate)", "Sodium benzoate"}


def personal_notes(hits, category: str, p: Profile):
    names = {h["name"] for h in hits}
    notes = []
    if category == "s":
        deep = p.skin_tone in ("Tan / brown", "Deep / dark brown")
        if deep and names & _IRRITANT_ACTIVES:
            notes.append("Your tone is more prone to dark marks after irritation. Patch-test, start slowly and use sunscreen with: " + ", ".join(sorted(names & _IRRITANT_ACTIVES)) + ".")
        if p.skin_tone == "Deep / dark brown" and "Zinc oxide / mineral UV filter" in names:
            notes.append("Untinted mineral sunscreen can look ashy on deep skin. Look for a tinted or clear-gel version.")
        if p.concern == "Acne-prone" and names & _COMEDOGENIC:
            notes.append("May feel heavy on acne-prone skin: " + ", ".join(sorted(names & _COMEDOGENIC)) + ".")
        if p.concern == "Dry skin" and names & _DRYING:
            notes.append("Could dry your skin further: " + ", ".join(sorted(names & _DRYING)) + ".")
        if p.concern == "Dark spots / uneven tone" and names & {"Niacinamide (vitamin B3)", "Vitamin C (ascorbic acid)"}:
            notes.append("Helpful for your concern: niacinamide / vitamin C are commonly used for uneven tone. Pair with daily sunscreen.")
        if "Fragrance / parfum" in names:
            notes.append("Contains fragrance, a common irritant. Patch-test if your skin is sensitive.")
    else:
        if p.food_goal == "Lower sugar" and names & _SUGAR:
            notes.append("Matches your goal to cut sugar: contains " + ", ".join(sorted(names & _SUGAR)) + ".")
        if p.food_goal == "Lower sodium" and names & _SODIUM:
            notes.append("Matches your goal to cut sodium: contains " + ", ".join(sorted(names & _SODIUM)) + ".")
    return notes


_KIDS_FOOD = {"MSG (monosodium glutamate)", "Artificial sweeteners", "BHA / BHT", "Sodium benzoate", "Caramel colour", "Maltodextrin"}
_KIDS_SKIN = {"Fragrance / parfum", "Retinol / retinoids", "Salicylic acid", "Glycolic / lactic acid (AHA)", "Benzoyl peroxide",
              "Kojic acid", "Sulfates (SLS / SLES)", "Parabens"}


def apply_kids(hits, category: str):
    """Kids mode: treat extra ingredients as 'avoid' because children are more sensitive."""
    kid_set = _KIDS_FOOD if category == "f" else _KIDS_SKIN
    out = []
    for h in hits:
        h = dict(h)
        if h["name"] in kid_set and h["level"] in ("warn", "ok"):
            h["level"] = "bad"
            h["disadvantage"] = "Kids mode: best avoided for children. " + h["disadvantage"]
        out.append(h)
    out.sort(key=lambda x: {"bad": 0, "warn": 1, "good": 2, "ok": 3}[x["level"]])
>>>>>>> e5d2695 (LabelLens AI)
    return out