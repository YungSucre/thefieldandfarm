#!/usr/bin/env python3
"""Génère les intros des 84 hubs de verticals thefieldandfarm (voix du site).
Sortie : src/data/hub_intros.json (importable par Astro).
"""
import json, os, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path("/root/thefieldandfarm")

def load_key():
    for p in ["/root/.hermes/.env", "/root/niche-finder/.env"]:
        if os.path.exists(p):
            for line in open(p):
                if line.startswith("DEEPSEEK_API_KEY="):
                    return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return None

KEY = load_key()
API = "https://api.deepseek.com/chat/completions"

# extraire les verticals du config.ts
txt = (ROOT / "src" / "config.ts").read_text()
verts = re.findall(r"\{ id: '([^']+)', name: '([^']+)' \}", txt)

SYSTEM = """You write for The Field & Farm, an EN-US gardening/homesteading site. Voice: a trusted neighbor-farmer, practical and concrete, no fluff, no em dashes. NEVER use em dashes (—), use colons or commas instead.

Write the intro paragraph for a topic hub page. Output STRICT JSON with exactly one key:
- "intro": a 2-3 sentence paragraph (45-70 words) that tells readers what this topic covers: how to grow or care for it, common problems solved, and what kinds of guides they will find here. Direct, factual, no hype, no "welcome to", no "whether you are a beginner or expert" filler."""

def call_llm(vertical_name):
    user = f'Topic: {vertical_name}. Write the hub intro paragraph.'
    req = urllib.request.Request(API, data=json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
        "temperature": 0.6,
        "response_format": {"type": "json_object"},
        "max_tokens": 300,
    }).encode(), headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
                raw = d["choices"][0]["message"]["content"]
                return json.loads(raw).get("intro", "")
        except Exception:
            time.sleep(2)
    return ""

def main():
    intros = {}
    for vid, vname in verts:
        intro = call_llm(vname)
        if intro:
            intros[vid] = intro
            print(f"  {vid}: {intro[:60]}...", flush=True)
        else:
            print(f"  {vid}: ÉCHEC", flush=True)
        time.sleep(0.5)
    out = ROOT / "src" / "data" / "hub_intros.json"
    out.write_text(json.dumps(intros, indent=1, ensure_ascii=False))
    print(f"DONE: {len(intros)}/{len(verts)} intros → {out}")

if __name__ == "__main__":
    main()
