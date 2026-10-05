<<<<<<< HEAD
"""Product-type guides and skin-tone suggestions."""

PRODUCTS = {
    "Sunscreen": (["sunscreen", "spf", "sun cream"], ["Prevents tanning, dark spots and ageing", "Lowers skin-cancer risk"], ["Untinted mineral types leave a white cast", "Some chemical filters irritate eyes or sensitive skin"], "SPF 30+, broad spectrum, PA+++; zinc oxide or tinosorb"),
    "Face wash": (["face wash", "cleanser"], ["Removes oil and dirt", "Gel types suit oily skin"], ["Sulfates and strong soaps can dry the face"], "Glycerin, mild surfactants; avoid SLS and heavy fragrance"),
    "Moisturiser": (["moisturiser", "moisturizer", "cream", "lotion"], ["Repairs the skin barrier", "Reduces dryness"], ["Heavy oils may clog pores on oily skin"], "Glycerin, ceramides, hyaluronic acid, niacinamide"),
    "Fairness / whitening cream": (["fairness", "whitening", "lightening"], ["May reduce dark patches (only with proven actives)"], ["Some contain hydroquinone, steroids or mercury", "Skin thinning and rebound darkening"], "Niacinamide, vitamin C, azelaic acid; avoid unlabelled strong creams"),
    "Shampoo": (["shampoo", "hair wash"], ["Cleans scalp and removes buildup"], ["Sulfates can dry the scalp and fade colour"], "Mild cleansers, glycerin; ketoconazole or zinc pyrithione for dandruff"),
    "Instant noodles": (["noodles", "maggi", "pasta"], ["Quick and cheap meal"], ["High sodium, refined flour, palm oil", "Low protein and fibre"], "Check sodium per serving; add vegetables and egg"),
    "Chips / snacks": (["chips", "snack", "namkeen"], ["Occasional treat"], ["High salt and fat, sometimes trans fat", "Colours and flavour enhancers"], "Baked, lower sodium, no hydrogenated oil"),
    "Soft drinks / juice": (["soft drink", "cola", "soda", "juice", "energy drink"], ["Fast energy"], ["Lots of sugar or sweeteners", "Colours and benzoate; enamel erosion"], "Under 5 g sugar per 100 ml; prefer buttermilk or coconut water"),
}

TONES = {
    "Fair": "Fair skin burns and shows redness easily, so sun protection and gentle actives matter most.",
    "Medium / wheatish": "Medium skin tans easily and can get uneven patches; SPF plus a brightening active works well.",
    "Tan / brown": "Tan to brown skin is more prone to dark marks after pimples or irritation. Go slow with strong acids and never scrub hard.",
    "Deep / dark brown": "Deep skin is the most prone to lasting dark marks. Avoid irritation and choose sunscreens that do not leave a white cast.",
}

SUNSCREEN_TIP = {
    "Fair": "Mineral or chemical both work. Avoid fragrance if you flush easily.",
    "Medium / wheatish": "Sheer chemical filters or lightly tinted mineral sunscreen blend best.",
    "Tan / brown": "Choose a tinted mineral or sheer-gel chemical sunscreen to avoid grey cast.",
    "Deep / dark brown": "Pick a tinted mineral (iron oxide) or clear-gel sunscreen. Plain zinc often looks ashy.",
}

CONCERNS = {
    "Dark spots / uneven tone": (["Niacinamide 5%", "Vitamin C serum (morning)", "Azelaic acid", "Sunscreen daily"], ["Hydroquinone without a doctor", "Unknown fairness creams (mercury / steroids)", "Harsh scrubs"]),
    "Dull skin": (["Gentle lactic acid 1-2 nights a week", "Vitamin C", "Hyaluronic acid", "Sunscreen daily"], ["Over-exfoliating", "Alcohol-heavy toners"]),
    "Acne-prone": (["Salicylic acid 0.5-2%", "Niacinamide", "Light gel moisturiser", "Non-comedogenic sunscreen"], ["Coconut oil on the face", "Heavy mineral oil creams", "Picking pimples"]),
    "Dry skin": (["Ceramides", "Glycerin and hyaluronic acid", "Shea butter at night", "Mild cream cleanser"], ["Sulfate cleansers", "Alcohol denat.", "Very hot water"]),
    "Sun protection": (["SPF 30-50, PA+++", "Reapply every 2-3 hours outdoors"], ["Skipping sunscreen on cloudy days"]),
}


SWAPS = {
    "Sugar": "choose unsweetened or 'no added sugar' versions; sweeten with fruit or dates.",
    "High fructose corn syrup": "pick drinks sweetened with fruit only, or buttermilk and coconut water.",
    "Palm oil": "look for products made with groundnut, sunflower or rice bran oil.",
    "Trans fat (hydrogenated oil)": "choose items that say 'no hydrogenated fat' or bake and cook at home with fresh oil.",
    "Sodium nitrite / nitrate": "eat fresh chicken, egg or fish instead of processed meats.",
    "Tartrazine and azo colours": "choose foods coloured with turmeric, beetroot or annatto, or uncoloured versions.",
    "Potassium bromate": "buy bread that says 'no bromate' or from a trusted bakery.",
    "MSG (monosodium glutamate)": "season with home-made masala, herbs and a little salt.",
    "Artificial sweeteners": "reduce sweetness gradually; fresh fruit is a better dessert.",
    "Salt / sodium": "pick lower-sodium versions and use only part of the seasoning sachet.",
    "Maltodextrin": "choose products with a shorter ingredient list and whole-food ingredients.",
    "Hydroquinone": "ask a dermatologist; niacinamide and vitamin C with daily sunscreen are gentler options.",
    "Mercury / steroid creams": "stop using it and show it to a doctor. Choose a labelled product from a trusted brand.",
    "Fragrance / parfum": "choose 'fragrance-free' products, especially for sensitive skin.",
    "Sulfates (SLS / SLES)": "try a sulfate-free or mild cleanser (look for glucoside or betaine cleansers).",
    "Alcohol denat.": "choose alcohol-free toners and serums.",
    "Parabens": "if your skin is sensitive, pick paraben-free products with gentler preservatives.",
    "Retinol / retinoids": "start with a low strength, 2 nights a week, and always use sunscreen.",
    "Triclosan / formaldehyde releasers": "choose products without antibacterial or formaldehyde-releasing preservatives.",
}


def swaps_for(hits):
    """Return [(ingredient, suggestion)] for flagged ingredients."""
=======
"""Product-type guides and skin-tone suggestions."""

PRODUCTS = {
    "Sunscreen": (["sunscreen", "spf", "sun cream"], ["Prevents tanning, dark spots and ageing", "Lowers skin-cancer risk"], ["Untinted mineral types leave a white cast", "Some chemical filters irritate eyes or sensitive skin"], "SPF 30+, broad spectrum, PA+++; zinc oxide or tinosorb"),
    "Face wash": (["face wash", "cleanser"], ["Removes oil and dirt", "Gel types suit oily skin"], ["Sulfates and strong soaps can dry the face"], "Glycerin, mild surfactants; avoid SLS and heavy fragrance"),
    "Moisturiser": (["moisturiser", "moisturizer", "cream", "lotion"], ["Repairs the skin barrier", "Reduces dryness"], ["Heavy oils may clog pores on oily skin"], "Glycerin, ceramides, hyaluronic acid, niacinamide"),
    "Fairness / whitening cream": (["fairness", "whitening", "lightening"], ["May reduce dark patches (only with proven actives)"], ["Some contain hydroquinone, steroids or mercury", "Skin thinning and rebound darkening"], "Niacinamide, vitamin C, azelaic acid; avoid unlabelled strong creams"),
    "Shampoo": (["shampoo", "hair wash"], ["Cleans scalp and removes buildup"], ["Sulfates can dry the scalp and fade colour"], "Mild cleansers, glycerin; ketoconazole or zinc pyrithione for dandruff"),
    "Instant noodles": (["noodles", "maggi", "pasta"], ["Quick and cheap meal"], ["High sodium, refined flour, palm oil", "Low protein and fibre"], "Check sodium per serving; add vegetables and egg"),
    "Chips / snacks": (["chips", "snack", "namkeen"], ["Occasional treat"], ["High salt and fat, sometimes trans fat", "Colours and flavour enhancers"], "Baked, lower sodium, no hydrogenated oil"),
    "Soft drinks / juice": (["soft drink", "cola", "soda", "juice", "energy drink"], ["Fast energy"], ["Lots of sugar or sweeteners", "Colours and benzoate; enamel erosion"], "Under 5 g sugar per 100 ml; prefer buttermilk or coconut water"),
}

TONES = {
    "Fair": "Fair skin burns and shows redness easily, so sun protection and gentle actives matter most.",
    "Medium / wheatish": "Medium skin tans easily and can get uneven patches; SPF plus a brightening active works well.",
    "Tan / brown": "Tan to brown skin is more prone to dark marks after pimples or irritation. Go slow with strong acids and never scrub hard.",
    "Deep / dark brown": "Deep skin is the most prone to lasting dark marks. Avoid irritation and choose sunscreens that do not leave a white cast.",
}

SUNSCREEN_TIP = {
    "Fair": "Mineral or chemical both work. Avoid fragrance if you flush easily.",
    "Medium / wheatish": "Sheer chemical filters or lightly tinted mineral sunscreen blend best.",
    "Tan / brown": "Choose a tinted mineral or sheer-gel chemical sunscreen to avoid grey cast.",
    "Deep / dark brown": "Pick a tinted mineral (iron oxide) or clear-gel sunscreen. Plain zinc often looks ashy.",
}

CONCERNS = {
    "Dark spots / uneven tone": (["Niacinamide 5%", "Vitamin C serum (morning)", "Azelaic acid", "Sunscreen daily"], ["Hydroquinone without a doctor", "Unknown fairness creams (mercury / steroids)", "Harsh scrubs"]),
    "Dull skin": (["Gentle lactic acid 1-2 nights a week", "Vitamin C", "Hyaluronic acid", "Sunscreen daily"], ["Over-exfoliating", "Alcohol-heavy toners"]),
    "Acne-prone": (["Salicylic acid 0.5-2%", "Niacinamide", "Light gel moisturiser", "Non-comedogenic sunscreen"], ["Coconut oil on the face", "Heavy mineral oil creams", "Picking pimples"]),
    "Dry skin": (["Ceramides", "Glycerin and hyaluronic acid", "Shea butter at night", "Mild cream cleanser"], ["Sulfate cleansers", "Alcohol denat.", "Very hot water"]),
    "Sun protection": (["SPF 30-50, PA+++", "Reapply every 2-3 hours outdoors"], ["Skipping sunscreen on cloudy days"]),
}


SWAPS = {
    "Sugar": "choose unsweetened or 'no added sugar' versions; sweeten with fruit or dates.",
    "High fructose corn syrup": "pick drinks sweetened with fruit only, or buttermilk and coconut water.",
    "Palm oil": "look for products made with groundnut, sunflower or rice bran oil.",
    "Trans fat (hydrogenated oil)": "choose items that say 'no hydrogenated fat' or bake and cook at home with fresh oil.",
    "Sodium nitrite / nitrate": "eat fresh chicken, egg or fish instead of processed meats.",
    "Tartrazine and azo colours": "choose foods coloured with turmeric, beetroot or annatto, or uncoloured versions.",
    "Potassium bromate": "buy bread that says 'no bromate' or from a trusted bakery.",
    "MSG (monosodium glutamate)": "season with home-made masala, herbs and a little salt.",
    "Artificial sweeteners": "reduce sweetness gradually; fresh fruit is a better dessert.",
    "Salt / sodium": "pick lower-sodium versions and use only part of the seasoning sachet.",
    "Maltodextrin": "choose products with a shorter ingredient list and whole-food ingredients.",
    "Hydroquinone": "ask a dermatologist; niacinamide and vitamin C with daily sunscreen are gentler options.",
    "Mercury / steroid creams": "stop using it and show it to a doctor. Choose a labelled product from a trusted brand.",
    "Fragrance / parfum": "choose 'fragrance-free' products, especially for sensitive skin.",
    "Sulfates (SLS / SLES)": "try a sulfate-free or mild cleanser (look for glucoside or betaine cleansers).",
    "Alcohol denat.": "choose alcohol-free toners and serums.",
    "Parabens": "if your skin is sensitive, pick paraben-free products with gentler preservatives.",
    "Retinol / retinoids": "start with a low strength, 2 nights a week, and always use sunscreen.",
    "Triclosan / formaldehyde releasers": "choose products without antibacterial or formaldehyde-releasing preservatives.",
}


def swaps_for(hits):
    """Return [(ingredient, suggestion)] for flagged ingredients."""
>>>>>>> e5d2695 (LabelLens AI)
    return [(h["name"], SWAPS[h["name"]]) for h in hits if h["level"] in ("bad", "warn") and h["name"] in SWAPS]