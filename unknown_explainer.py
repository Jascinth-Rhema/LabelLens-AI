"""Explain ingredients that are NOT in the database, using safe pattern rules.
These are educated guesses (never a safety verdict) and are always shown with a confidence level."""
import re

ADVICE = "Check the spelling on the label. If it matters for your health or skin, ask a doctor, dietitian or pharmacist."


def _e_role(n: int) -> str:
    if 100 <= n < 200:
        return "a colour (dye)"
    if 200 <= n < 300:
        return "a preservative"
    if 300 <= n < 400:
        return "an antioxidant or acidity regulator"
    if 400 <= n < 500:
        return "a thickener, stabiliser or emulsifier"
    if 500 <= n < 600:
        return "an acidity regulator or anti-caking agent"
    if 600 <= n < 700:
        return "a flavour enhancer"
    if 900 <= n < 1000:
        return "a glazing agent, sweetener or flour improver"
    return "a food additive"


# (pattern, kind, explanation, confidence, categories or None for both)
RULES = [
    (r"acidity regulator|acidulant", "Acidity regulator", "Controls sourness and pH so the food stays fresh and stable.", "Medium", None),
    (r"inosinate|guanylate|glutamate", "Flavour enhancer", "Boosts savoury (umami) taste so less salt or spice is needed. Usually used in tiny amounts.", "Medium", None),
    (r"phenoxyethanol|sorbate|chlorphenesin|ethylhexylglycerin|dehydroacetic|benzyl alcohol|preservative", "Preservative", "Stops bacteria and mould from growing so the product lasts longer.", "Medium", None),
    (r"edta|chelat", "Chelating agent", "Keeps the formula stable and fresh by binding metal traces.", "Medium", None),
    (r"flavou?r|aroma\b|essence", "Flavouring", "Adds taste or smell. Labels rarely list the exact chemicals, and 'natural' does not automatically mean healthier.", "Medium", ("f",)),
    (r"colou?r|\bdye\b|caramel|\bci ?\d{5}\b|\blake\b|\bmica\b|iron oxide", "Colour / pigment", "Adds colour or shimmer only. Check the exact code or name if you want to know the type.", "Medium", None),
    (r"emulsifier|lecithin|glyceride|polysorbate|stearate|polyglycerol", "Emulsifier", "Keeps oil and water mixed so the texture stays smooth.", "Medium", None),
    (r"\bgum\b|pectin|carrageenan|cellulose|\bagar\b|gelatin|carbomer|thickener|stabili[sz]er", "Thickener / stabiliser", "Gives body and a smooth texture. Large amounts of some gums can cause bloating.", "Medium", None),
    (r"\bpeg-?\d*|ppg-|polyethylene glycol", "PEG-based ingredient", "Helps oils and water mix or acts as a solvent. Usually fine, but can irritate broken skin.", "Low", ("s",)),
    (r"cetyl|stearyl|cetearyl|behenyl", "Fatty alcohol", "Softens and thickens creams. Unlike drying alcohols, it is usually gentle.", "Medium", ("s",)),
    (r"glycol|propanediol|humectant", "Humectant / solvent", "Helps hold moisture and lets other ingredients spread and absorb.", "Medium", None),
    (r"sulfate|sulfonate|betaine|glucoside|cocamide|surfactant", "Cleansing agent", "Makes foam and lifts dirt and oil. Strength varies, so milder ones suit dry skin better.", "Medium", ("s",)),
    (r"vitamin|tocopher|retinyl|panthenol|riboflavin|thiamine|folic|cobalamin|biotin|niacin", "Vitamin", "Added for nutrition (food) or to protect and condition skin. Usually low concern at label amounts.", "Medium", None),
    (r"\b(iron|zinc|calcium|magnesium|potassium|selenium|copper|iodine)\b|mineral", "Mineral", "A nutrient mineral in food, or a mineral ingredient in skincare. Amount decides the effect.", "Low", None),
    (r"yeast|enzyme|amylase|protease|lipase|ferment", "Yeast / enzyme / ferment", "A natural helper used to make dough rise, process food or condition skin.", "Medium", None),
    (r"protein|whey|casein|gluten|soy|collagen|keratin|peptide", "Protein ingredient", "A protein source in food, or a conditioning ingredient in skin and hair care.", "Medium", None),
    (r"flour|starch|maida|atta|semolina|rava|\bgrain\b|\brice\b|maize|\bcorn\b|\boats?\b", "Grain / starch", "A base that gives bulk and energy. Whole grains have more fibre than refined ones.", "Medium", ("f",)),
    (r"sweeten|syrup|\w+ose\b|sorbitol|xylitol|mannitol|erythritol|maltodextrin", "Sweetener / sugar", "Adds sweetness or bulk. Many types count as sugar for your daily limit.", "Medium", ("f",)),
    (r"\b(milk|cream|curd|paneer|cheese|butter|ghee)\b", "Dairy ingredient", "Adds richness and protein. Not suitable if you avoid dairy.", "Medium", ("f",)),
    (r"\b(spice|masala|pepper|chilli|chili|garlic|onion|cumin|coriander|cardamom|clove|cinnamon|herb)s?\b", "Spice / seasoning", "Adds flavour. Spices are generally fine in food amounts.", "Medium", ("f",)),
    (r"\bextract\b|\bleaf\b|\broot\b|\bseed\b|\bpowder\b|flower|\bbark\b", "Plant extract / powder", "A concentrated part of a plant. Benefit depends on the plant and amount, which labels rarely show. Plant ingredients can still irritate sensitive skin.", "Medium", None),
    (r"\boil\b|\bfat\b|tallow", "Oil or fat", "Gives texture and flavour in food, or softens skin in skincare. In food, check whether it is saturated or hydrogenated.", "Medium", None),
    (r"\bacid\b", "Acid", "In food, adjusts sourness and keeps it fresh. In skincare it can exfoliate or adjust pH. Strength matters.", "Low", None),
    (r"water|aqua|solution", "Water / solvent", "The base that carries the other ingredients.", "Medium", None),
    (r"sodium|potassium|\bsalt\b", "Salt-type compound", "Sodium and potassium compounds are often salts used for taste, preserving or pH control.", "Low", None),
    (r"(ate|ide|ine|ol|yl|ene)\b", "Chemical-sounding name", "The name suggests a purified or lab-made compound. That alone does not make it harmful; many are common and safe.", "Low", None),
]


INS = {100: "Curcumin (turmeric colour)", 102: "Tartrazine (yellow dye)", 110: "Sunset yellow (dye)", 129: "Allura red (dye)",
       150: "Caramel colour", 160: "Carotenoid / paprika / annatto colour", 200: "Sorbic acid", 202: "Potassium sorbate",
       211: "Sodium benzoate", 220: "Sulphur dioxide", 250: "Sodium nitrite", 260: "Acetic acid (vinegar)", 270: "Lactic acid",
       296: "Malic acid", 300: "Ascorbic acid (vitamin C)", 306: "Tocopherols (vitamin E)", 322: "Lecithin", 330: "Citric acid",
       331: "Sodium citrates", 338: "Phosphoric acid", 339: "Sodium phosphates", 401: "Sodium alginate", 407: "Carrageenan",
       410: "Locust bean gum", 412: "Guar gum", 414: "Gum arabic", 415: "Xanthan gum", 440: "Pectin", 450: "Diphosphates",
       451: "Triphosphates (water-holding salts)", 452: "Polyphosphates", 460: "Cellulose", 466: "Carboxymethyl cellulose",
       471: "Mono- and diglycerides", 500: "Sodium carbonates (baking soda)", 501: "Potassium carbonates", 503: "Ammonium carbonates",
       508: "Potassium chloride (salt substitute)", 509: "Calcium chloride", 551: "Silicon dioxide (anti-caking)", 621: "MSG",
       627: "Disodium guanylate", 631: "Disodium inosinate", 635: "Ribonucleotides", 950: "Acesulfame K", 951: "Aspartame",
       955: "Sucralose", 1442: "Modified starch"}
INS_OK = {100, 160, 260, 270, 296, 300, 306, 322, 330, 331, 401, 410, 412, 414, 415, 440, 460, 466, 471, 500, 501, 503, 508, 509, 551, 1442}
INS_LIMIT = {102, 110, 129, 150, 211, 220, 250, 338, 339, 450, 451, 452, 621, 627, 631, 635, 950, 951, 955}

KIND_SAFETY = {
    "Preservative": "ok", "Acidity regulator": "ok", "Vitamin": "ok", "Mineral": "ok", "Spice / seasoning": "ok", "Plant extract / powder": "ok",
    "Grain / starch": "ok", "Dairy ingredient": "ok", "Water / solvent": "ok", "Yeast / enzyme / ferment": "ok", "Emulsifier": "ok",
    "Thickener / stabiliser": "ok", "Fatty alcohol": "ok", "Humectant / solvent": "ok", "Protein ingredient": "ok", "Chelating agent": "ok",
    "Flavouring": "ok", "Oil or fat": "limit", "Sweetener / sugar": "limit", "Flavour enhancer": "limit", "Salt-type compound": "limit",
}
SAFETY_TEXT = {"ok": "Probably OK", "limit": "Limit", "check": "Can't tell"}


def explain(token: str, category: str) -> dict:
    t = token.lower().strip()
    m = re.search(r"\b(?:e|ins)\s?-?(\d{3,4})[a-z]?\b", t) or re.fullmatch(r"()(\d{3,4})[a-z]?", t) and re.fullmatch(r"(\d{3,4})[a-z]?", t)
    if m:
        n = int(m.group(1))
        if 1500 <= n < 1510:  # OCR often turns 150d into 1504
            n //= 10
        name = INS.get(n)
        safety = "ok" if n in INS_OK else "limit" if n in INS_LIMIT else "check"
        text = f"Code {n} (E{n} / INS {n}) is " + (f"{name}. It works as {_e_role(n)}." if name else f"usually {_e_role(n)}.")
        return {"kind": name or f"E{n} additive", "text": text, "conf": "High" if name else "Medium", "safety": SAFETY_TEXT[safety], "skey": safety,
                "advice": "Approved food additives are allowed only up to set limits. Limit them if you eat the product daily."}
    for pat, kind, text, conf, cats in RULES:
        if cats and category not in cats:
            continue
        if re.search(pat, t):
            sk = KIND_SAFETY.get(kind, "check")
            return {"kind": kind, "text": text, "conf": conf, "safety": SAFETY_TEXT[sk], "skey": sk, "advice": ADVICE}
    return {"kind": "Unrecognised", "text": "We could not identify this. It may be an OCR typo, a brand-specific name or a rare ingredient.",
            "conf": "Unknown", "safety": SAFETY_TEXT["check"], "skey": "check", "advice": ADVICE}