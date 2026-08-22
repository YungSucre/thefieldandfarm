#!/usr/bin/env python3
"""COLLECT_PO_TITLES — collecte Google/Bing Suggest pour practiceownerpro.

Re-application du process niche-finder (ARCHITECTURE.md du grimoire :
angle_research.py = collecte question-first via Google/Bing Suggest) au
domaine practice owner. ZÉRO token LLM (HTTP direct).

Seeds :
  1. Par sous-niche × angle : "{sub} {kw}", "{kw} for {sub}" (formulations réelles)
  2. Localisation : "{vertical} {kw} {state}" pour les angles sensibles à l'état
     (taxes, compliance, insurance, legal structure, payroll) × états US
  3. États génériques : "{sub} requirements by state" (le pattern qui fonctionne)

Filtre : garde les requêtes pertinentes (business/angle), drop achat pur et
hors-sujet. Sortie : outputs/suggest_titles.jsonl (title, vertical, sub, angle,
engine). Reprise possible (state dans outputs/collect_state.json).

Usage : python3 scripts/collect_po_titles.py [--limit N] [--states 10]
"""
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "suggest_titles.jsonl")
STATE = os.path.join(ROOT, "outputs", "collect_state.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

ANGLES = {
    "taxes": ["taxes", "tax deductions", "sales tax", "franchise tax", "estimated taxes"],
    "accounting": ["accounting", "bookkeeping", "chart of accounts"],
    "software": ["software", "practice management software", "billing software"],
    "hiring": ["hire employees", "hiring", "job description", "staff"],
    "compliance": ["compliance", "license requirements", "regulations", "HIPAA", "record keeping"],
    "insurance": ["insurance", "malpractice insurance", "workers comp", "business insurance"],
    "marketing": ["marketing", "SEO", "advertising", "social media"],
    "startup": ["start a practice", "startup costs", "business plan"],
    "equipment": ["equipment", "supplies", "furniture"],
    "billing": ["billing", "invoicing", "pricing services"],
    "payroll": ["payroll", "pay employees", "payroll taxes"],
    "legal structure": ["LLC", "PLLC", "S-Corp", "legal structure", "business entity"],
    "cash flow": ["cash flow", "get paid faster"],
    "staffing": ["how many employees", "staffing"],
    "retirement": ["retirement plan", "SEP IRA", "401k"],
    "pricing": ["how much to charge", "pricing", "rates"],
}
# Angles où l'état compte vraiment (localisation)
STATE_SENSITIVE = ["taxes", "compliance", "insurance", "payroll", "legal structure"]
STATES = ["texas", "california", "new york", "florida", "illinois", "ohio", "georgia",
          "north carolina", "pennsylvania", "michigan", "arizona", "colorado", "washington",
          "massachusetts", "virginia", "new jersey", "tennessee", "indiana", "maryland",
          "wisconsin", "minnesota", "oregon", "nevada", "utah", "louisiana", "kentucky",
          "alabama", "oklahoma", "connecticut", "iowa", "arkansas", "kansas", "mississippi",
          "missouri", "south carolina", "new mexico", "nebraska", "idaho", "hawaii", "west virginia",
          "montana", "delaware", "new hampshire", "maine", "rhode island", "alaska",
          "wyoming", "vermont", "north dakota", "south dakota"]
# Pays (22/08, user : « oublie pas les pays, on va traduire et localiser à terme »)
COUNTRIES = ["uk", "united kingdom", "canada", "australia", "ireland", "new zealand",
             "india", "singapore", "uae", "south africa", "germany", "france", "spain"]

# Drop achat pur / hors-sujet (même logique que le grimoire : merch = drop)
DROP = re.compile(r"\b(buy|purchase|order|price of|cost of a new|near me|gift|outfit|tee|shirt|"
                  r"salary of|how much does a \w+ make|jobs?|hiring near|degree|school near|"
                  r"course|certification program|online classes|for sale|real estate for)\b", re.I)
KEEP = re.compile(r"\b(tax|deduct|irs|license|insurance|compliance|software|hire|payroll|"
                  r"llc|pllc|scorp|s corp|billing|equipment|startup|bookkeeping|accounting|"
                  r"malpractice|workers comp|deductible|franchise|entity|record|hipaa|"
                  r"retirement|401k|sep ira|marketing|seo|cash flow|revenue|profit|"
                  r"requirements?|regulations?|state|federal)\b", re.I)


def load_seeds():
    """Sous-niches depuis la banque existante + verticals."""
    subs = set()
    verts = set()
    for line in open(os.path.join(ROOT, "outputs", "titles_all.jsonl")):
        r = json.loads(line)
        subs.add((r["vertical"], r["sub"]))
        verts.add(r["vertical"])
    return sorted(subs), sorted(verts)


def suggest_google(q):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&q="
           + urllib.parse.quote(q))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read().decode("utf-8", "replace"))
    return d[1] if isinstance(d, list) and len(d) > 1 else []


def suggest_bing(q):
    url = "https://api.bing.com/osjson.aspx?query=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read().decode("utf-8", "replace"))
    return d[1] if isinstance(d, list) and len(d) > 1 else []


def keep(s):
    return bool(KEEP.search(s)) and not DROP.search(s) and len(s) > 15


def main():
    limit = 0
    n_states = 10
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    if "--states" in sys.argv:
        n_states = int(sys.argv[sys.argv.index("--states") + 1])

    subs, verts = load_seeds()
    print(f"{len(subs)} sous-niches · {len(verts)} verticals · états: {n_states}")

    # reprise
    done = set()
    if os.path.exists(STATE):
        done = set(json.load(open(STATE)))
    fout = open(OUT, "a")

    seeds = []
    # 1. par sous-niche × angle (formulations générales)
    for v, sub in subs:
        for angle, kws in ANGLES.items():
            for kw in kws[:2]:
                seeds.append((f"{sub} {kw}", v, sub, angle))
                seeds.append((f"{kw} for {sub}", v, sub, angle))
    # 2. localisation par vertical × angle sensible × états + pays
    loc = STATES[:n_states] + COUNTRIES
    for v in verts:
        vname = v.replace("-", " ")
        for angle in STATE_SENSITIVE:
            kw = ANGLES[angle][0]
            for geo in loc:
                seeds.append((f"{vname} {kw} {geo}", v, "", angle))
        seeds.append((f"{vname} license requirements by state", v, "", "compliance"))
        seeds.append((f"{vname} tax requirements by state", v, "", "taxes"))
        seeds.append((f"{vname} license requirements uk", v, "", "compliance"))
        seeds.append((f"{vname} tax requirements uk", v, "", "taxes"))

    if limit:
        seeds = seeds[:limit]
    print(f"{len(seeds)} seeds à collecter (Google + Bing)")
    random.seed(42)
    random.shuffle(seeds)

    n_ok = n_skip = 0
    t0 = time.time()
    for i, (q, v, sub, angle) in enumerate(seeds):
        key = f"{q}|{v}|{angle}"
        if key in done:
            continue
        hits = set()
        for engine, fn in (("google", suggest_google), ("bing", suggest_bing)):
            try:
                for s in fn(q):
                    s = s.strip()
                    if keep(s):
                        hits.add(s)
            except Exception:
                pass
            time.sleep(0.15)
        for s in hits:
            fout.write(json.dumps({"title": s, "seed": q, "vertical": v, "sub": sub,
                                   "angle": angle, "engine": "suggest"}) + "\n")
        done.add(key)
        n_ok += 1
        if i % 25 == 0:
            json.dump(sorted(done), open(STATE, "w"))
            el = time.time() - t0
            rate = (i + 1) / max(el, 0.1)
            print(f"  {i+1}/{len(seeds)} · {rate:.1f} seeds/s · {len(hits)} hits (last: {q[:60]})", flush=True)
        if limit and i + 1 >= limit:
            break
    fout.close()
    json.dump(sorted(done), open(STATE, "w"))
    n = sum(1 for _ in open(OUT))
    print(f"Terminé : {n} suggestions dans {OUT} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
