#!/usr/bin/env python3
"""PRODUCTEUR D'ARTICLES thefieldandfarm — spécimen GSC.
Pattern practiceownerpro : JSON contraint, température 0.5, re-prompt sur vide,
preflight (mots, H2, em dash, description). VOIX : factuelle, pratique, sans tics IA.
Images : Pexels (hero + 2 sections) via API.
Usage : python3 produce_ff.py [--limit N]
"""
import json, os, re, sys, time, urllib.request, datetime
from pathlib import Path

ROOT = Path("/root/thefieldandfarm")
CONTENT = ROOT / "src" / "content" / "articles"
PUBLIC = ROOT / "public" / "images" / "articles"
OUTPUTS = ROOT / "outputs"
STATE = OUTPUTS / "produce_ff_state.json"
TITLES = ROOT / "demo_titles.jsonl"

sys.path.insert(0, "/root/niche-finder/scripts")
def load_key(name):
    for p in ["/root/.hermes/.env", "/root/niche-finder/.env"]:
        if os.path.exists(p):
            for line in open(p):
                if line.startswith(name + "="):
                    return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return None

KEY = load_key("DEEPSEEK_API_KEY")
PEXELS_KEY = load_key("PEXELS_API_KEY")
API = "https://api.deepseek.com/chat/completions"

EMDASH_RULE = "NEVER use em dashes (—). Use colons or commas instead."

SYSTEM = """You write for The Field & Farm, an EN-US editorial site for gardeners, homesteaders, and small farmers. Voice: a trusted neighbor-farmer who has made every mistake so the reader does not have to. Direct and concrete: answer the question in the first two sentences, no teasing, no weather intro. Experienced but never condescending: at most 1-2 warm asides per article, never repeated. Honest about what works and what does not (say when a method is pricier, slower, or more fragile). Real numbers only: planting dates by USDA zone, spacing in inches, depth, realistic 2026 price ranges (e.g. $40-$60), realistic yields. Simple: explain the why in one sentence when useful, never a lecture. No forced humor, no emoji. Specificity is mandatory: real varieties, real tools, real steps. """ + EMDASH_RULE + """

Output STRICT JSON with exactly these keys:
- "title": the article title (must match the requested title)
- "description": one sentence, 120-160 chars, SEO meta description
- "body": the full article in Markdown. Structure: intro paragraph (2-3 sentences answering the question directly), then H2 sections with concrete information, tables where useful (e.g. planting times, varieties), a FAQ section with 3-4 questions, and a final "The bottom line" section. 700-1100 words. Use H2 (##) headings, not H1. Bullet lists where natural. NEVER use em dashes. Never promise exaggerated results ("guaranteed harvest", "100 pounds in a weekend"). Mention realistic varieties and dates for US growing zones."""

def call_llm(system, user, temperature=0.5):
    req = urllib.request.Request(API, data=json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "max_tokens": 3500,
    }).encode(), headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    for a in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
                return d["choices"][0]["message"]["content"]
        except Exception as e:
            if a == 3:
                raise
            time.sleep(2 * (a + 1))

def parse_llm_out(raw):
    try:
        return json.loads(raw)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def preflight(slug, title, desc, body, n_words_min=600):
    probs = []
    words = len(body.split())
    if words < n_words_min:
        probs.append(f"court ({words} mots < {n_words_min})")
    h2 = body.count("\n## ")
    if h2 < 4:
        probs.append(f"H2 insuffisants ({h2} < 4)")
    if "—" in body:
        probs.append("em dash présent")
    if not desc or len(desc) < 100:
        probs.append("description trop courte")
    return probs

def build_prompt(item):
    return f"""Write the article for this title:

TITLE: {item['title']}

Context: this guide is for {item.get('sub', 'gardeners and small farmers')}, vertical: {vertical_name(item['vertical'])}, topic: {item.get('angle', 'how-to')}. Format: {item.get('format', 'guide')}.

Requirements:
- Answer the question the title asks, directly and concretely
- Realistic current figures (2026) with ranges where exact numbers vary
- Practical steps the reader can take this week
- Name real varieties, real tools, real prices where relevant
- FAQ section at the end (3-4 questions)
- "The bottom line" final section
- 700-1100 words, H2 sections only (no H1)
- NEVER use em dashes (—)"""

def fetch_pexels(query, slug, kind):
    """hero.jpg / section-1.jpg / section-2.jpg depuis Pexels."""
    if not PEXELS_KEY:
        return None, None
    q = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={q}&per_page=5&orientation=landscape"
    try:
        req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read())
        photos = d.get("photos", [])
        if not photos:
            return None, None
        p = photos[0]
        img_url = p["src"]["large2x"]
        outdir = PUBLIC / slug
        outdir.mkdir(parents=True, exist_ok=True)
        fname = "hero.jpg" if kind == "hero" else f"section-{kind}.jpg"
        out = outdir / fname
        req2 = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"})
        with urllib.request.urlopen(req2, timeout=30) as r2:
            out.write_bytes(r2.read())
        return f"/images/articles/{slug}/{fname}", p.get("alt", query)
    except Exception as e:
        print(f"    image err {kind}: {e}", flush=True)
        return None, None

def vertical_name(vid):
    """Nom propre du vertical depuis src/config.ts (parse texte)."""
    try:
        txt = (ROOT / "src" / "config.ts").read_text()
        for m in re.finditer(r"\{ id: '([^']+)', name: '([^']+)' \}", txt):
            if m.group(1) == vid:
                return m.group(2)
    except Exception:
        pass
    return vid.title()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    if not KEY:
        print("DEEPSEEK_API_KEY introuvable", file=sys.stderr)
        return 2
    titles = [json.loads(l) for l in open(TITLES)]
    st = {"done": []}
    if STATE.exists():
        try:
            st = json.load(open(STATE))
        except Exception:
            pass
    done = set(st["done"])
    todo = [t for t in titles if t["slug"] not in done]
    print(f"{len(todo)} à produire ({len(done)} déjà faits)", flush=True)
    produced = 0
    for item in todo[: args.limit]:
        slug = item["slug"]
        print(f"  [{produced+1}/{min(args.limit, len(todo))}] {item['title']}", flush=True)
        ok = False
        for attempt in range(3):
            try:
                raw = call_llm(SYSTEM, build_prompt(item))
                d = parse_llm_out(raw)
                if not d or not d.get("body"):
                    print(f"    réponse vide (tentative {attempt+1})", flush=True)
                    continue
                body = d["body"]
                title = d.get("title", item["title"])
                desc = d.get("description", "")
                probs = preflight(slug, title, desc, body)
                if probs:
                    print(f"    preflight: {', '.join(probs)}", flush=True)
                    fix = call_llm(SYSTEM, build_prompt(item) + f"\n\nYour previous draft was rejected: {', '.join(probs)}. Fix these issues. Keep the same title. Also ensure at least 700 words and 4 H2 sections. NO em dashes.")
                    d2 = parse_llm_out(fix)
                    if d2 and d2.get("body"):
                        body = d2["body"]
                        desc = d2.get("description", desc)
                        title = d2.get("title", title)
                # images Pexels
                hero_img, hero_alt = fetch_pexels(item.get("img_query", item["title"]), slug, "hero")
                time.sleep(0.5)
                sec1, _ = fetch_pexels(item.get("img_query", item["title"]), slug, "1")
                time.sleep(0.5)
                sec2, _ = fetch_pexels(item.get("img_query", item["title"]), slug, "2")
                # insérer les images de section dans le body (après les 2 premiers H2)
                body2 = body
                h2s = [m.start() for m in re.finditer(r"\n## ", body)]
                if len(h2s) >= 2 and sec1:
                    body2 = body2[: h2s[0]] + f"\n![{item['title']}]({sec1})\n" + body2[h2s[0]:]
                if len(h2s) >= 3 and sec2:
                    body2 = body2[: h2s[1]] + f"\n![{item['title']}]({sec2})\n" + body2[h2s[1]:]
                # frontmatter
                today = datetime.date.today().isoformat()
                fm = (
                    "---\n"
                    f'title: "{title.replace(chr(34), chr(39))}"\n'
                    f'description: "{desc.replace(chr(34), chr(39))}"\n'
                    f'vertical: "{item["vertical"]}"\n'
                    f'verticalName: "{vertical_name(item["vertical"])}"\n'
                    f'slug: "{slug}"\n'
                    'status: "published"\n'
                    f"pubDate: {today}\n"
                    'affiliate_ready: false\n'
                )
                if hero_img:
                    fm += f'hero_image: "{hero_img}"\nhero_alt: "{str(hero_alt or "").replace(chr(34), chr(39))}"\n'
                fm += "---\n\n"
                path = CONTENT / f"{item['vertical']}-{slug}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(fm + body2.strip() + "\n")
                done.add(slug)
                st["done"] = list(done)
                STATE.write_text(json.dumps(st, indent=1))
                produced += 1
                ok = True
                print(f"    ✓ {path.name} ({len(body2.split())} mots, hero={'oui' if hero_img else 'NON'})", flush=True)
                break
            except Exception as e:
                print(f"    erreur: {e}", flush=True)
                time.sleep(3)
        if not ok:
            print(f"    ✗ ÉCHEC {slug}", flush=True)
        time.sleep(1)
    print(f"TERMINÉ: {produced} articles produits", flush=True)

if __name__ == "__main__":
    import urllib.parse
    main()
