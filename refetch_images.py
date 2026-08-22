#!/usr/bin/env python3
"""Re-fetch Pexels pour les articles thefieldandfarm sans images (403 du 1er run)."""
import json, os, re, sys, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path("/root/thefieldandfarm")
CONTENT = ROOT / "src" / "content" / "articles"
PUBLIC = ROOT / "public" / "images" / "articles"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"

PEXELS_KEY = None
for p in ["/root/niche-finder/.env", "/root/.hermes/.env"]:
    if os.path.exists(p):
        for line in open(p):
            if line.startswith("PEXELS_API_KEY="):
                PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

def pexels_search(q):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": q, "per_page": 5, "orientation": "landscape"})
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read())
    return d.get("photos", [])

def fetch_img(url, out):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        out.write_bytes(r.read())

def parse_fm(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, m.group(2)

def main():
    n = 0
    for md in sorted(CONTENT.glob("*.md")):
        text = md.read_text()
        fm, body = parse_fm(text)
        if not fm:
            continue
        slug = fm["slug"]
        outdir = PUBLIC / slug
        outdir.mkdir(parents=True, exist_ok=True)
        # hero déjà présent ?
        hero_ok = (outdir / "hero.jpg").exists()
        sec1_ok = (outdir / "section-1.jpg").exists()
        sec2_ok = (outdir / "section-2.jpg").exists()
        if hero_ok and sec1_ok and sec2_ok:
            continue
        q = fm.get("title", slug)
        try:
            photos = pexels_search(q)
            if not photos:
                print(f"  {slug}: aucune photo", flush=True)
                continue
            if not hero_ok:
                p = photos[0]
                fetch_img(p["src"]["large2x"], outdir / "hero.jpg")
                fm["hero_image"] = f"/images/articles/{slug}/hero.jpg"
                fm["hero_alt"] = p.get("alt", q)[:200]
                print(f"  {slug}: hero OK", flush=True)
                time.sleep(0.4)
            if not sec1_ok and len(photos) > 1:
                fetch_img(photos[1]["src"]["large2x"], outdir / "section-1.jpg")
                print(f"  {slug}: section-1 OK", flush=True)
                time.sleep(0.4)
            if not sec2_ok and len(photos) > 2:
                fetch_img(photos[2]["src"]["large2x"], outdir / "section-2.jpg")
                print(f"  {slug}: section-2 OK", flush=True)
                time.sleep(0.4)
            n += 1
        except Exception as e:
            print(f"  {slug}: erreur {e}", flush=True)
            time.sleep(2)
        # réécriture du frontmatter (ajout hero_image/hero_alt si manquants)
        lines = []
        for k, v in fm.items():
            lines.append(f'{k}: "{str(v).replace(chr(34), chr(39))}"')
        new_text = "---\n" + "\n".join(lines) + "\n---\n\n" + body
        if new_text != text:
            md.write_text(new_text)
    print(f"TERMINÉ: {n} articles imagés", flush=True)

if __name__ == "__main__":
    main()
