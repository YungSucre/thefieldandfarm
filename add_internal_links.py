#!/usr/bin/env python3
"""Ajoute des liens internes (Related guides) aux articles sans liens.
2-3 liens vers des articles du MÊME vertical (priorité même angle).
Le pattern du grimoire : liens internes = maillage SEO obligatoire.
"""
import os, re, json
from pathlib import Path

ROOT = Path("/root/thefieldandfarm")
CONTENT = ROOT / "src" / "content" / "articles"

def load_articles():
    arts = []
    for f in sorted(os.listdir(CONTENT)):
        if not f.endswith(".md"):
            continue
        path = CONTENT / f
        content = path.read_text()
        fm = content.split("---", 2)[1]
        def get(k):
            m = re.search(rf'^{k}: "([^"]+)"', fm, re.M)
            return m.group(1) if m else None
        arts.append({
            "file": f, "path": path, "content": content, "fm": fm,
            "vertical": get("vertical"), "slug": get("slug"), "title": get("title"),
        })
    return arts

def main():
    arts = load_articles()
    by_vertical = {}
    for a in arts:
        by_vertical.setdefault(a["vertical"], []).append(a)

    added = 0
    for a in arts:
        body = a["content"].split("---", 2)[2]
        if "/guides/" in body:
            continue  # déjà des liens internes
        # candidats : même vertical, autre article, avec hero
        cands = [c for c in by_vertical.get(a["vertical"], []) if c["file"] != a["file"]]
        # priorité aux titres partageant un mot-clé du titre courant
        kw = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", a["title"] or "") if w.lower() not in
              {"what", "does", "should", "the", "your", "you", "need", "know", "guide", "complete",
               "best", "vs", "which", "more", "are", "is", "do", "with", "saves", "probably", "missing",
               "first", "things", "mistakes", "before", "questions", "ask", "buying", "practice"}]
        def score(c):
            ck = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", c["title"] or "")]
            return sum(1 for w in kw if w in ck)
        cands.sort(key=score, reverse=True)
        picks = cands[:3]
        if len(picks) < 2:
            picks = (cands + [c for c in by_vertical.get(a["vertical"], []) if c["file"] != a["file"]])[:3]
        if not picks:
            continue
        links = []
        for c in picks:
            links.append(f'- [{c["title"]}](/guides/{c["vertical"]}/{c["slug"]}/)')
        related = "\n## Related guides\n\n" + "\n".join(links) + "\n"
        # insère avant le dernier H2 "The bottom line" si présent, sinon à la fin
        new_body = body
        if "## The bottom line" in body:
            idx = body.index("## The bottom line")
            new_body = body[:idx] + related + "\n" + body[idx:]
        else:
            new_body = body.rstrip() + "\n\n" + related
        a["path"].write_text(a["content"].split("---", 2)[0] + "---" + a["fm"] + "---" + new_body)
        added += 1

    print(f"liens internes ajoutés à {added} articles", flush=True)

if __name__ == "__main__":
    main()
