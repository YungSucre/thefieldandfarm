#!/usr/bin/env python3
"""Filtre les titres bruts Bing de thefieldandfarm → titres d'articles propres.
Garde les vraies questions (angles), retire le bruit d'autocomplete (homonymes,
sujets hors-niche, requêtes trop longues). Sortie : outputs/titles_clean.jsonl
"""
import json, re
from pathlib import Path

RAW = Path("outputs/titles_raw")
OUT = Path("outputs/titles_clean.jsonl")

# angles acceptés (au moins un pattern)
GOOD = [
    r"^how to (grow|plant|start|care|raise|keep|build|make|harvest|store|prune|water|feed|compost|pickle|can|preserve|dry|cure|save|choose|tell|fix|prevent|protect|attract)",
    r"^when to (plant|harvest|start|pick|prune|sow|transplant|feed|collect)",
    r"^best (soil|fertilizer|compost|seeds|varieties|plants|tools|equipment|feed|coop|fence|mulch|spacing|way|methods?)",
    r"^what is the best",
    r"^why (is|are|do|does) my",
    r" for beginners$",
    r"(problems|issues) (and|&)? ?(solutions|fixes)?$",
    r"^how (long|much|often|deep|far|big|many)",
    r" vs ",
    r"^how to get (rid of|more|started)",
    r"^what (can|cannot|should|to) (i |you )?(plant|feed|compost|do)",
    r"^do (chickens|goats|cows|pigs|bees|ducks|rabbits|turkeys|sheep)",
]

# bruit d'autocomplete (homonymes, hors-niche, produits)
NOISE = [
    "air fryer", "recipe", "recipes", "troubleshooting", "wireless", "bluetooth",
    "songs", "lyrics", "movies", "netflix", "games", "meme", "quiz", "tattoo",
    "salary", "career", "jobs", "near me", "delivery", "walmart", "costco",
    "lowes", "home depot", "petsmart", "for dogs", "for cats", "reddit",
    "for sale", "amazon echo", "soundbar", "headphones", "iphone", "android",
    "laptop", "macbook", "ps5", "xbox", "instagram", "tiktok", "youtube",
    "google", "facebook", "certification", "degree", "how to become",
    "how to make money", "way to cook", "recipes", "recipe", "cooking", "cook ", "beats ", " beats", "airpods", "speaker", "tv ",
    "monitor", "printer", "router", "wifi", "lifespan of a", "car ", "truck ",
    "motorcycle", "bicycle", "fishing", "hunting", "gun", "knife", "dog ",
    "cat ", "guitar", "piano", "workout", "gym", "meditation app", "dating",
    "hair", "skin", "makeup", "weight loss", "diet ", "fast food", "pizza",
    "burger", "coffee shop", "bakery", "restaurant", "hotel", "wedding",
    "birthday", "christmas gifts", "valentine", "halloween costume",
]

def clean(vertical):
    f = RAW / f"{vertical}.txt"
    if not f.exists():
        return []
    out = []
    seen = set()
    for line in f.read_text().splitlines():
        q = line.strip()
        if len(q) < 10 or len(q) > 90:
            continue
        ql = q.lower()
        if any(n in ql for n in NOISE):
            continue
        if not any(re.search(p, ql) for p in GOOD):
            continue
        # titre propre (capitaliser)
        title = q[0].upper() + q[1:]
        if title in seen:
            continue
        seen.add(title)
        out.append(title)
    return out

def main():
    all_items = []
    for f in sorted(RAW.glob("*.txt")):
        vertical = f.stem
        if vertical == "ALL":
            continue
        titles = clean(vertical)
        # 3 max par vertical pour le spécimen (les meilleurs d'abord)
        for t in titles[:3]:
            tl = t.lower()
            if tl.startswith(("when to", "how long", "how much")):
                angle = "timing"
            elif tl.startswith(("why", "what can", "problems", "do ")):
                angle = "problems"
            elif tl.startswith("best"):
                angle = "best"
            else:
                angle = "how-to"
            slug = re.sub(r"[^a-z0-9]+", "-", tl).strip("-")
            all_items.append({"title": t, "vertical": vertical, "slug": slug,
                              "angle": angle, "format": "guide",
                              "sub": "gardeners and homesteaders",
                              "img_query": t.replace("How To ", "").replace("Best ", "")[:40]})
    print(f"{len(all_items)} titres propres sélectionnés sur {len(list(RAW.glob('*.txt'))) - 1} verticals")
    with open(OUT, "w") as fp:
        for it in all_items:
            fp.write(json.dumps(it) + "\n")
    # aperçu
    for it in all_items[:12]:
        print(f"  [{it['vertical']}] {it['title']}  [{it['angle']}]")

if __name__ == "__main__":
    main()
