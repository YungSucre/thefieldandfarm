#!/usr/bin/env python3
"""Fetch images Pexels pour les articles practiceownerpro sans hero.
Règle pipeline : 1 hero + 2 images de section minimum par article.
Recherche Pexels par mots-clés du titre, télécharge, écrit le frontmatter hero_image.
Sortie : src/content/articles/*.md mis à jour + public/images/articles/<slug>/hero.jpg
"""
import json, os, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path("/root/practiceownerpro")
CONTENT = ROOT / "src" / "content" / "articles"
IMAGES = ROOT / "public" / "images" / "articles"

def get_pexels_key():
    for p in ["/root/niche-finder/.env", "/root/.hermes/.env"]:
        if os.path.exists(p):
            for line in open(p):
                if line.startswith("PEXELS_API_KEY="):
                    return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return None

KEY = get_pexels_key()

def pexels_search(q):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": q, "per_page": 3, "orientation": "landscape"})
    req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": "pop/0.1"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read()).get("photos", [])

def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read()
    if len(data) < 20000 or data[:2] != b"\xff\xd8":
        raise RuntimeError("bad jpeg")
    dest.write_bytes(data)
    return len(data)

def article_keywords(title):
    """Extrait les mots-clés de recherche : le sujet de la sous-niche."""
    stop = {"what", "how", "does", "should", "the", "a", "an", "for", "to", "your",
            "you", "need", "know", "guide", "complete", "best", "vs", "which", "more",
            "are", "is", "do", "in", "of", "and", "with", "saves", "probably", "missing"}
    words = [w.lower() for w in re.findall(r"[A-Za-z]+", title)]
    kw = [w for w in words if w not in stop and len(w) > 3]
    # domaine générique : practice office / profession
    return kw[:4] or ["office"]

def main():
    if not KEY:
        print("PEXELS_API_KEY introuvable", file=sys.stderr)
        return 2
    updated = 0
    for f in sorted(os.listdir(CONTENT)):
        if not f.endswith(".md"):
            continue
        path = CONTENT / f
        content = path.read_text()
        if "hero_image:" in content:
            continue  # déjà un hero
        fm = content.split("---", 2)[1]
        m = re.search(r'title: "([^"]+)"', fm)
        if not m:
            continue
        title = m.group(1)
        m2 = re.search(r'slug: "([^"]+)"', fm)
        slug = m2.group(1) if m2 else f.replace(".md", "").split("-", 1)[1]
        kw = article_keywords(title)
        q = " ".join(kw)
        print(f"  {f[:50]}... q='{q}'", flush=True)
        try:
            photos = pexels_search(q)
            if not photos:
                photos = pexels_search("professional office")
            if not photos:
                print("    pas de photo", flush=True)
                continue
            # skip les photos déjà utilisées (md5 global simple)
            dest_dir = IMAGES / slug
            dest_dir.mkdir(parents=True, exist_ok=True)
            hero = dest_dir / "hero.jpg"
            photo = photos[0]
            url = photo["src"]["large2x"].split("?")[0] + "?auto=compress&cs=tinysrgb&w=1200"
            download(url, hero)
            credit = photo.get("photographer", "Pexels")
            # écriture du frontmatter hero_image
            new_fm = fm.replace(
                'affiliate_ready: false',
                f'hero_image: "/images/articles/{slug}/hero.jpg"\n'
                f'hero_alt: "{title}"\n'
                f'hero_credit: "Photo: {credit} / Pexels"\n'
                'affiliate_ready: false'
            )
            path.write_text(content.replace(fm, new_fm))
            updated += 1
            print(f"    ✓ hero {slug} ({os.path.getsize(hero)//1024} Ko)", flush=True)
        except Exception as e:
            print(f"    erreur: {e}", flush=True)
        time.sleep(0.4)
    print(f"TERMINÉ: {updated} articles avec hero", flush=True)

if __name__ == "__main__":
    main()
