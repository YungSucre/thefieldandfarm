#!/usr/bin/env python3
"""Filtre étendu thefieldandfarm — modèle thebighauler.
Angles élargis (toutes les vraies questions), PAS de plafond par vertical,
pertinence par vocabulaire du vertical, dédup exact + quasi.
Sortie : outputs/titles_filtered/<vertical>.txt + outputs/titles_clean.jsonl
"""
import json, re
from pathlib import Path
from collections import defaultdict

RAW = Path("/root/thefieldandfarm/outputs/titles_raw")
OUTDIR = Path("/root/thefieldandfarm/outputs/titles_filtered")
OUT = Path("/root/thefieldandfarm/outputs/titles_clean.jsonl")

# --- angles : toute vraie question (beaucoup plus large que l'ancien filtre) ---
GOOD = [
    r"^how (to|do|can|long|much|often|deep|far|big|many)",
    r"^when (to|do|can|should)",
    r"^what (is|are|can|does|should|to|the)",
    r"^why (is|are|do|does|can|won't|wont)",
    r"^which ",
    r"^best ",
    r"^do (chickens|goats|cows|pigs|bees|ducks|rabbits|turkeys|sheep|plants|tomatoes)",
    r"^can (you|i|chickens|goats|pigs|bees|ducks|rabbits)",
    r"^should (you|i)",
    r"^is |^are ",
    r" vs ",
    r" for beginners$",
    r"(problems|issues) (and|&)? ?(solutions|fixes)?$",
    r"\btips$",
    r"\bguide$",
    r"^growing |^planting |^raising ",
]

# --- bruit (étendu) ---
NOISE = [
    "air fryer", "recipe", "recipes", "troubleshooting", "wireless", "bluetooth",
    "songs", "lyrics", "movies", "netflix", "games", "meme", "quiz", "tattoo",
    "salary", "career", "jobs", "near me", "delivery", "walmart", "costco",
    "lowes", "home depot", "petsmart", "for dogs", "for cats", "reddit",
    "for sale", "amazon echo", "soundbar", "headphones", "iphone", "android",
    "laptop", "macbook", "ps5", "xbox", "instagram", "tiktok", "youtube",
    "google", "facebook", "certification", "degree", "how to become",
    "how to make money", "way to cook", "cooking", "cook ", "beats ", " beats",
    "airpods", "speaker", "tv ", "monitor", "printer", "router", "wifi",
    "lifespan of a", "car ", "truck ", "motorcycle", "bicycle", "fishing",
    "hunting", "gun", "knife", "dog ", "cat ", "guitar", "piano", "workout",
    "gym", "meditation app", "dating", "hair", "skin", "makeup", "weight loss",
    "diet ", "fast food", "pizza", "burger", "coffee shop", "bakery",
    "restaurant", "hotel", "wedding", "birthday", "christmas gifts",
    "valentine", "halloween costume", "porn", "sex", "fortnite", "minecraft",
    "conspiracy", "aliens", "ufo", "ghost", "haunted",
    # bruit supplémentaire détecté sur échantillon
    "bread", "pie from", "per meal", "meal prep", "per person",
    "phone cost", "phone price", "ship phone", "vs amazon", "sales on amazon",
    "on amazon", "amazon echo", "amazon prime", "squish", "productive bees",
    "gutter material", "computer vision", "software",
]

STOP = set("the a an of to for and in on with your you best how what is are do does it s this week uk us can i my should need guide complete ways way about from per new vs or not at be by as".split())

def tokens(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 3]

def jaccard(a, b):
    ta, tb = set(tokens(a)), set(tokens(b))
    if not ta or not tb:
        return 0
    return len(ta & tb) / len(ta | tb)

def norm(s):
    return " ".join(sorted(re.findall(r"[a-z0-9]+", s.lower())))

# --- vocabulaire par vertical (pertinence) : générique agri + spécifique ---
AGRI_TERMS = [
    "plant", "plants", "planting", "grow", "growing", "garden", "gardening",
    "soil", "fertilizer", "compost", "seed", "seeds", "harvest", "crop", "crops",
    "chicken", "chickens", "egg", "eggs", "goat", "goats", "cow", "cows", "pig", "pigs",
    "bee", "bees", "honey", "duck", "ducks", "rabbit", "rabbits", "turkey", "turkeys",
    "sheep", "cattle", "livestock", "hay", "pasture", "fence", "fencing", "barn",
    "coop", "feed", "watering", "irrigation", "mulch", "prune", "pruning", "tomato",
    "tomatoes", "pepper", "peppers", "squash", "cucumber", "cucumbers", "lettuce",
    "kale", "spinach", "carrot", "carrots", "potato", "potatoes", "onion", "onions",
    "garlic", "herb", "herbs", "basil", "rosemary", "thyme", "mint", "sage",
    "berry", "berries", "strawberry", "blueberry", "apple", "apples", "peach",
    "pear", "plum", "cherry", "grape", "grapes", "corn", "wheat", "oats", "barley",
    "soybean", "beans", "peas", "cabbage", "broccoli", "cauliflower", "brussels",
    "radish", "beet", "beets", "turnip", "parsnip", "leek", "shallot", "celery",
    "asparagus", "rhubarb", "okra", "eggplant", "melon", "watermelon", "pumpkin",
    "zucchini", "sunflower", "marigold", "lavender", "chamomile", "dill", "cilantro",
    "parsley", "oregano", "sage", "chives", "farm", "farming", "homestead",
    "orchard", "greenhouse", "raised bed", "container", "hydroponic", "aquaponics",
    "permaculture", "composting", "worm", "manure", "pesticide", "weed", "weeds",
    "pest", "pests", "disease", "fungus", "mold", "blight", "rot", "yield",
    "harvesting", "canning", "preserving", "pickling", "fermenting", "cheese",
    "milk", "yogurt", "butter", "soap", "candle", "wool", "fleece", "meat",
    "slaughter", "butcher", "incubat", "hatch", "chick", "brooder", "rooster",
    "hen", "layer", "broiler", "quail", "goose", "geese", "alpaca", "llama",
    "donkey", "horse", "mule", "apiary", "hive", "nuc", "swarm", "pollinat",
    "cover crop", "green manure", "crop rotation", "no-till", "till",
    "irrigation", "drip", "sprinkler", "rainwater", "barrel", "silo", "tractor",
    "tiller", "mower", "greenhouse", "cold frame", "hoop house", "shade cloth",
    "trellis", "stake", "cage", "row cover", "frost", "zone", "usda",
    "season", "spring", "summer", "fall", "winter", "autumn", "hardiness",
]

def is_pertinent(vertical, t):
    tl = t.lower()
    if any(a in tl for a in AGRI_TERMS):
        return True
    # sinon : le mot du vertical lui-même (ex "chickens" dans chickens)
    vbase = re.sub(r"[-_]", " ", vertical)
    return vbase in tl or vbase.rstrip("s") in tl

def clean(vertical):
    f = RAW / f"{vertical}.txt"
    if not f.exists():
        return []
    out = []
    seen = set()
    for line in f.read_text().splitlines():
        q = line.strip()
        if len(q) < 10 or len(q) > 95:
            continue
        ql = q.lower()
        if any(n in ql for n in NOISE):
            continue
        if not any(re.search(p, ql) for p in GOOD):
            continue
        if not is_pertinent(vertical, ql):
            continue
        title = q[0].upper() + q[1:]
        if title in seen:
            continue
        seen.add(title)
        out.append(title)
    return out

def main():
    all_items = []
    OUTDIR.mkdir(parents=True, exist_ok=True)
    vids = sorted(f.stem for f in RAW.glob("*.txt") if f.stem != "ALL")

    for vertical in vids:
        titles = clean(vertical)
        # PAS de plafond : tous les titres propres du vertical
        for t in titles:
            tl = t.lower()
            if tl.startswith(("when to", "how long", "how much", "how often", "how deep", "how far", "how big")):
                angle = "timing"
            elif tl.startswith(("why", "what can", "problems", "issues", "do ", "can ")):
                angle = "problems"
            elif tl.startswith("best") or " vs " in tl:
                angle = "best"
            else:
                angle = "how-to"
            slug = re.sub(r"[^a-z0-9]+", "-", tl).strip("-")
            all_items.append({"title": t, "vertical": vertical, "slug": slug,
                              "angle": angle, "format": "guide",
                              "sub": "gardeners and homesteaders",
                              "img_query": t.replace("How To ", "").replace("Best ", "")[:40]})
        OUTDIR.joinpath(vertical + ".txt").write_text("\n".join(titles))

    # dédup exact inter-vertical (garde le 1er)
    by_norm = defaultdict(list)
    for i, it in enumerate(all_items):
        by_norm[norm(it["title"])].append(i)
    seen_n = set()
    dedup = []
    for it in all_items:
        n = norm(it["title"])
        if n in seen_n:
            continue
        seen_n.add(n)
        dedup.append(it)

    with open(OUT, "w") as fp:
        for it in dedup:
            fp.write(json.dumps(it) + "\n")

    print(f"{len(all_items)} titres bruts filtrés ({len(vids)} verticals) -> {len(dedup)} après dédup inter")
    from collections import Counter
    vc = Counter(it["vertical"] for it in dedup)
    print("top verticals:", vc.most_common(8))
    print("min/max par vertical:", min(vc.values()), "/", max(vc.values()))

if __name__ == "__main__":
    main()
