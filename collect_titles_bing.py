#!/usr/bin/env python3
"""Collecte de titres Bing Suggest pour thefieldandfarm — process niche-finder.
Vraies questions utilisateurs (osjson), templates jamais source unique (leçon 22/08).
Usage : python3 collect_titles_bing.py [--limit N verticals] [--vertical ID]
Sortie : outputs/titles_raw/<vertical>.txt + outputs/titles_raw/ALL.txt
"""
import json, time, urllib.request, urllib.parse, os, sys, pathlib

ANGLES = [
    "how to {s}",
    "best {s}",
    "when to plant {s}",
    "why is my {s}",
    "{s} problems",
    "{s} for beginners",
    "how much {s}",
    "{s} vs",
    "how long does {s} take",
    "common {s}",
    "how to grow {s}",
    "tips for {s}",
]

def suggest_bing(q):
    url = "https://api.bing.com/osjson.aspx?query=" + urllib.parse.quote(q)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8", "ignore"))
            return [s for s in data[1]] if len(data) > 1 else []
    except Exception:
        return []

def main():
    seeds = json.load(open("data/seeds.json"))
    vids = list(seeds.keys())
    # filtres
    for i, a in enumerate(sys.argv):
        if a == "--limit" and i + 1 < len(sys.argv):
            vids = vids[: int(sys.argv[i + 1])]
        if a == "--vertical" and i + 1 < len(sys.argv):
            vids = [sys.argv[i + 1]]
    outdir = pathlib.Path("outputs/titles_raw")
    outdir.mkdir(parents=True, exist_ok=True)
    all_seen = set()
    all_lines = []
    t0 = time.time()
    for vi, vid in enumerate(vids):
        subjects = seeds[vid]
        seen = set()
        lines = []
        for s in subjects:
            for angle in ANGLES:
                q = angle.format(s=s)
                for comp in suggest_bing(q):
                    c = comp.strip().lower()
                    if c and c not in seen:
                        seen.add(c)
                        all_seen.add(c)
                        lines.append(c)
                time.sleep(0.25)
        outdir.joinpath(vid + ".txt").write_text("\n".join(sorted(lines)))
        all_lines.extend(lines)
        elapsed = time.time() - t0
        print(f"[{vi+1}/{len(vids)}] {vid}: {len(lines)} titres (total {len(all_seen)}, {elapsed/60:.0f} min)", flush=True)
    outdir.joinpath("ALL.txt").write_text("\n".join(sorted(all_lines)))
    print(f"DONE: {len(all_seen)} titres uniques en {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
