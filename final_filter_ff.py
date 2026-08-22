#!/usr/bin/env python3
"""Passe finale de pertinence thefieldandfarm — modèle final_filter_bh.py.
Un titre est gardé si : terme fort global agri OU vocabulaire de SON vertical.
+ hard-block sur les résidus (bread, phone, amazon, squish, etc.).
Sortie : outputs/titles_final/<vertical>.txt + titles_clean.jsonl (remplace)
"""
import json, re
from pathlib import Path
from collections import defaultdict

CLEAN = Path("/root/thefieldandfarm/outputs/titles_filtered")
FINAL = Path("/root/thefieldandfarm/outputs/titles_final")
OUT = Path("/root/thefieldandfarm/outputs/titles_clean.jsonl")

# --- Termes forts globaux agri/homestead ---
AGRI_STRONG = [
    "plant", "plants", "planting", "grow", "growing", "garden", "gardening",
    "soil", "fertilizer", "fertiliser", "compost", "seed", "seeds", "sow",
    "harvest", "crop", "crops", "yield", "sprout", "germinat", "seedling",
    "chicken", "chickens", "egg", "eggs", "goat", "goats", "cow", "cows",
    "pig", "pigs", "bee", "bees", "honey", "duck", "ducks", "rabbit", "rabbits",
    "turkey", "turkeys", "sheep", "cattle", "livestock", "hay", "pasture",
    "fence", "fencing", "barn", "coop", "feed", "water", "irrigation",
    "mulch", "prune", "pruning", "tomato", "tomatoes", "pepper", "peppers",
    "squash", "cucumber", "cucumbers", "lettuce", "kale", "spinach", "carrot",
    "carrots", "potato", "potatoes", "onion", "onions", "garlic", "herb",
    "herbs", "basil", "rosemary", "thyme", "mint", "sage", "berry", "berries",
    "strawberry", "blueberry", "apple", "apples", "peach", "pear", "plum",
    "cherry", "grape", "grapes", "corn", "wheat", "oats", "barley", "soybean",
    "beans", "peas", "cabbage", "broccoli", "cauliflower", "radish", "beet",
    "beets", "turnip", "parsnip", "leek", "shallot", "celery", "asparagus",
    "rhubarb", "okra", "eggplant", "melon", "watermelon", "pumpkin", "zucchini",
    "sunflower", "marigold", "lavender", "chamomile", "dill", "cilantro",
    "parsley", "oregano", "chives", "farm", "farming", "homestead", "orchard",
    "greenhouse", "raised bed", "container", "hydroponic", "aquaponics",
    "permaculture", "composting", "worm", "manure", "pesticide", "weed",
    "weeds", "pest", "pests", "disease", "fungus", "mold", "blight", "rot",
    "canning", "preserving", "pickling", "fermenting", "cheese", "milk",
    "yogurt", "butter", "soap", "candle", "wool", "fleece", "meat",
    "slaughter", "butcher", "incubat", "hatch", "chick", "brooder", "rooster",
    "hen", "layer", "broiler", "quail", "goose", "geese", "alpaca", "llama",
    "donkey", "horse", "mule", "apiary", "hive", "swarm", "pollinat",
    "cover crop", "crop rotation", "no-till", "till", "drip", "sprinkler",
    "rainwater", "barrel", "silo", "tractor", "tiller", "mower", "cold frame",
    "hoop house", "shade cloth", "trellis", "stake", "cage", "row cover",
    "frost", "zone", "usda", "hardiness", "forag", "mushroom", "maple",
    "sap", "syrup", "sourdough", "microgreen", "sprout", "root cellar",
    "off-grid", "square foot", "succession", "companion", "pollinator",
]

# --- Vocabulaire par vertical (le vertical prouve la pertinence) ---
VERT_KEYWORDS = {
    "agritourism": ["farm stay", "agritourism", "pumpkin patch", "u-pick", "corn maze", "hayride", "hay ride"],
    "alliums": ["onion", "onions", "garlic", "leek", "leeks", "shallot", "chive", "chives", "scallion"],
    "alpacas-llamas": ["alpaca", "llama"],
    "beans-legumes": ["bean", "beans", "pea", "peas", "legume", "lentil", "soybean", "fava", "chickpea"],
    "beekeeping": ["bee", "bees", "honey", "hive", "apiary", "beekeeper", "wax", "nuc"],
    "berries": ["berry", "berries", "strawberry", "blueberry", "raspberry", "blackberry", "gooseberry", "currant"],
    "brassicas": ["cabbage", "broccoli", "cauliflower", "brussels", "kale", "collard", "turnip", "radish", "arugula"],
    "breeding-incubation": ["breed", "breeding", "incubat", "hatch", "chick", "brooder", "fertile"],
    "business-accounting": ["business", "accounting", "tax", "profit", "income", "insurance", "llc", "record"],
    "canning": ["canning", "can ", "jar", "jars", "water bath", "pressure canner", "seal"],
    "cattle": ["cattle", "cow", "cows", "calf", "calves", "beef", "steer", "heifer", "bull"],
    "cheese-dairy": ["cheese", "milk", "dairy", "yogurt", "butter", "cream", "curd", "whey", "pasteur"],
    "chickens": ["chicken", "chickens", "hen", "rooster", "egg", "eggs", "layer", "broiler", "coop"],
    "citrus": ["citrus", "lemon", "orange", "lime", "grapefruit", "mandarin", "kumquat"],
    "companion-planting": ["companion", "planting together", "good neighbors"],
    "composting": ["compost", "composting", "worm bin", "browns", "greens"],
    "container-gardening": ["container", "pot", "pots", "balcony", "patio"],
    "corn-grains": ["corn", "maize", "wheat", "oats", "barley", "grain", "grains", "rye", "millet", "sorghum"],
    "csa-u-pick": ["csa", "u-pick", "pick your own", "community supported"],
    "culinary-herbs": ["basil", "rosemary", "thyme", "mint", "sage", "oregano", "parsley", "cilantro", "dill", "chives", "herb", "herbs"],
    "cut-flowers": ["flower", "flowers", "cut flower", "bouquet", "peony", "dahlia", "zinnia", "snapdragon"],
    "dehydrating-freezing": ["dehydrat", "freez", "freeze", "dry ", "drying", "jerky", "fruit leather"],
    "ducks-waterfowl": ["duck", "ducks", "goose", "geese", "waterfowl", "mallard"],
    "eggplant-nightshades": ["eggplant", "nightshade", "tomato", "pepper", "potato"],
    "farmers-markets": ["farmers market", "market stand", "vendor", "selling at"],
    "fencing-structures": ["fence", "fencing", "gate", "post", "electric fence", "woven wire"],
    "fermenting-pickling": ["ferment", "fermenting", "pickle", "pickling", "brine", "kraut", "kombucha"],
    "fertilizers": ["fertilizer", "fertiliser", "n-p-k", "nitrogen", "phosphorus", "potassium", "amend"],
    "foraging": ["forag", "wild", "mushroom", "morel", "chanterelle", "ramp", "nettle", "elderberry"],
    "garden-pests": ["pest", "pests", "bug", "bugs", "aphid", "beetle", "caterpillar", "slug", "snail", "mite"],
    "goats": ["goat", "goats", "kid", "does", "buck", "milk goat", "fainting"],
    "grants-usda": ["grant", "grants", "usda", "loan", "funding", "subsidy", "cost share"],
    "grapes-vines": ["grape", "grapes", "vine", "vines", "winemaking", "viticulture", "trellis"],
    "greenhouse": ["greenhouse", "glasshouse", "polytunnel", "hoop house"],
    "hand-tools": ["tool", "tools", "shovel", "hoe", "rake", "trowel", "pruner", "axe", "scythe"],
    "heirloom-exotic": ["heirloom", "heritage", "exotic", "rare", "unusual", "unique variety"],
    "herbal-remedies": ["herbal", "remedy", "tincture", "salve", "tea", "infusion", "medicinal"],
    "hydroponics": ["hydroponic", "hydroponics", "nutrient solution", "deep water", "dwc", "kratky"],
    "indoor-gardening": ["indoor", "houseplant", "grow light", "windowsill", "apartment"],
    "insurance-compliance": ["insurance", "liability", "compliance", "regulation", "inspection", "license"],
    "irrigation": ["irrigat", "drip", "sprinkler", "soaker", "water line", "emitter", "well"],
    "land-property": ["land", "property", "acre", "acres", "deed", "zoning", "easement", "buying land"],
    "leafy-greens": ["lettuce", "spinach", "kale", "chard", "arugula", "mesclun", "greens", "salad"],
    "livestock-health": ["livestock", "vaccin", "vet", "deworm", "parasite", "health", "sick", "disease"],
    "maple-syrup": ["maple", "sap", "syrup", "sugar bush", "tap", "boiling"],
    "meat-processing": ["meat", "butcher", "slaughter", "processing", "quarter", "carcass", "sausage"],
    "medicinal-herbs": ["medicinal", "herbal", "echinacea", "calendula", "chamomile", "yarrow", "plantain"],
    "microgreens-sprouts": ["microgreen", "sprout", "sprouts", "shoot", "pea shoot", "broccoli sprout"],
    "mulching-weeds": ["mulch", "mulching", "straw", "wood chip", "cardboard", "landscape fabric"],
    "mushrooms": ["mushroom", "mushrooms", "shiitake", "oyster", "lion's mane", "spawn", "mycelium"],
    "no-till": ["no-till", "notill", "till", "tilling", "lasagna", "sheet mulch"],
    "nutrient-deficiencies": ["deficien", "nutrient", "yellow leaves", "nitrogen", "iron", "magnesium", "calcium"],
    "off-grid": ["off-grid", "off grid", "solar", "rainwater", "compost toilet", "wood stove", "generator"],
    "permaculture": ["permaculture", "food forest", "swale", "guild", "zones"],
    "pigs": ["pig", "pigs", "hog", "hogs", "boar", "sow", "piglet", "bacon"],
    "plant-diseases": ["disease", "blight", "mildew", "rust", "wilt", "rot", "virus", "fungus"],
    "pollinators": ["pollinat", "butterfly", "native", "bumble", "hummingbird", "nectar"],
    "propagation": ["propagat", "cutting", "cuttings", "division", "graft", "layering", "rooting"],
    "pruning-training": ["prune", "pruning", "train", "training", "espalier", "cordon", "pollard"],
    "rabbits": ["rabbit", "rabbits", "bunny", "hutch", "buck", "doe", "kit"],
    "rainwater": ["rainwater", "rain barrel", "cistern", "gutter", "collection"],
    "raised-bed": ["raised bed", "raised garden", "bed depth", "bed soil"],
    "root-cellars": ["root cellar", "cold storage", "cellar", "underground storage"],
    "root-vegetables": ["carrot", "carrots", "potato", "potatoes", "beet", "beets", "turnip", "parsnip", "radish", "sweet potato"],
    "season-extension": ["season extension", "cold frame", "row cover", "low tunnel", "high tunnel", "hoop"],
    "seed-saving": ["seed saving", "save seeds", "heirloom seed", "open-pollinated", "harvest seeds"],
    "seed-starting": ["seed starting", "start seeds", "germinat", "seedling", "grow light", "dome"],
    "sheep-wool": ["sheep", "ewe", "ram", "lamb", "wool", "fleece", "spinning"],
    "soap-candles": ["soap", "candle", "candles", "lye", "melt and pour", "cold process", "wax"],
    "soil-amendments": ["amendment", "lime", "gypsum", "biochar", "azomite", "rock dust", "green sand"],
    "soil-health": ["soil health", "soil test", "ph", "organic matter", "microbe", "earthworm"],
    "sourdough-baking": ["sourdough", "starter", "bread", "loaf", "ferment", "bake"],
    "square-foot": ["square foot", "sfg", "grid"],
    "squash-cucurbits": ["squash", "zucchini", "cucumber", "melon", "pumpkin", "gourd", "butternut", "acorn"],
    "succession-planting": ["succession", "stagger", "continuous harvest", "second planting"],
    "tomatoes-peppers": ["tomato", "tomatoes", "pepper", "peppers", "roma", "cherry tomato", "jalapeno", "bell pepper"],
    "tractors": ["tractor", "tractors", "implement", "pto", "mower deck", "loader", "hydraulic"],
    "tree-fruit": ["apple", "apples", "peach", "pear", "plum", "cherry", "apricot", "nectarine", "orchard"],
    "turkeys-game-birds": ["turkey", "turkeys", "poult", "game bird", "pheasant", "quail", "guinea"],
    "vertical-gardening": ["vertical", "trellis", "wall garden", "climbing"],
    "weed-management": ["weed", "weeds", "weeding", "herbicide", "pre-emergent", "smother"],
    "wildlife-control": ["deer", "rabbit fence", "squirrel", "raccoon", "mole", "vole", "groundhog", "bird netting"],
    "winter-vegetables": ["winter", "cold hardy", "overwinter", "frost", "snow"],
    "worm-composting": ["worm", "worms", "vermicompost", "castings", "bin"],
}

# --- hard-block résidus ---
HARD_BLOCK = [
    r"\b(bread|loaf|bagel|pizza|pasta|rice)\b",      # cuisine (hors sourdough volontaire)
    r"\b(phone|iphone|android|laptop|computer|app for|apps for|software)\b",
    r"\b(amazon|walmart|costco|lowes|homedepot|etsy)\b",
    r"\b(near me|for sale|jobs|salary|career|hire)\b",
    r"\b(recipe|recipes|cooking|meal prep|per meal|per person)\b",
    r"\b(porn|sex|dating|girlfriend|boyfriend)\b",
    r"\b(weight loss|diet plan|keto|workout|gym|makeup|hair|skin)\b",
    r"\b(movie|movies|netflix|songs|lyrics|games|gaming|tiktok|instagram)\b",
    r"\b(ship|shipping|delivery|tracking)\b",
    r"\b(squish|vape|e-cigarette|cbd)\b",
    r"\b(gutter material|computer vision|ai |artificial intelligence)\b",
    r"\bosrs\b",                       # Old School RuneScape
    r"\bstardew\b",                    # jeu
    r"\bprotein in\b",                 # nutrition
    r"\bcalories in\b",
    r"\bcarbs in\b",
    r"\bsugar in\b",
    r"\bfat in\b",
]

def is_hard_blocked(t):
    tl = t.lower()
    # exception : sourdough-baking garde "bread" (c'est SON sujet)
    return any(re.search(p, tl) for p in HARD_BLOCK)

def is_pertinent(v, t):
    tl = t.lower()
    if any(s in tl for s in AGRI_STRONG):
        return True
    kws = VERT_KEYWORDS.get(v, [])
    return any(k in tl for k in kws)

items = []
for f in sorted(CLEAN.glob("*.txt")):
    for line in f.read_text().splitlines():
        t = line.strip()
        if t:
            items.append((f.stem, t))

kept = []
removed = []
for v, t in items:
    if is_hard_blocked(t):
        removed.append((v, t, "hard"))
    elif not is_pertinent(v, t):
        removed.append((v, t, "pas pertinent"))
    else:
        kept.append((v, t))

FINAL.mkdir(parents=True, exist_ok=True)
by_v = defaultdict(list)
for v, t in kept:
    by_v[v].append(t)
total = 0
for v, titles in sorted(by_v.items()):
    FINAL.joinpath(v + ".txt").write_text("\n".join(titles))
    total += len(titles)

# régénère titles_clean.jsonl depuis le final (ordre : triés par vertical)
with open(OUT, "w") as fp:
    for v in sorted(by_v):
        for t in by_v[v]:
            tl = t.lower()
            if tl.startswith(("when to", "how long", "how much", "how often")):
                angle = "timing"
            elif tl.startswith(("why", "what can", "problems", "do ", "can ")):
                angle = "problems"
            elif tl.startswith("best") or " vs " in tl:
                angle = "best"
            else:
                angle = "how-to"
            slug = re.sub(r"[^a-z0-9]+", "-", tl).strip("-")
            fp.write(json.dumps({"title": t, "vertical": v, "slug": slug,
                                 "angle": angle, "format": "guide",
                                 "sub": "gardeners and homesteaders",
                                 "img_query": t.replace("How To ", "").replace("Best ", "")[:40]}) + "\n")

print(f"AVANT: {len(items)} | APRÈS: {total} titres pertinents, {len(by_v)} verticals")
print(f"Retirés: {len(removed)}")
print("\nExemples retirés (15):")
for v, t, why in removed[:15]:
    print(f"  [{v}] {t[:65]} ({why})")
print("\nTop verticals:")
for v, titles in sorted(by_v.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"  {v}: {len(titles)}")
