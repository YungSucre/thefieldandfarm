#!/bin/bash
# Déploiement practiceownerpro : build → commit → push → vérif live
set -e
cd /root/practiceownerpro

echo "=== 1. Build ==="
npm run build > /tmp/pop_build.log 2>&1
NB=$(grep -oE "[0-9]+ page\(s\) built" /tmp/pop_build.log | grep -oE "[0-9]+")
echo "Build OK: $NB pages"

echo "=== 2. Vérif em dashes ==="
EM=$(grep -rc "—" src/ 2>/dev/null | grep -v ":0" | wc -l)
if [ "$EM" -gt 0 ]; then
  echo "⚠ $EM fichiers avec em dashes — correction"
  python3 << 'PYEOF'
import os
for root, dirs, files in os.walk('src'):
    for f in files:
        if not f.endswith(('.astro', '.md', '.ts')):
            continue
        p = os.path.join(root, f)
        c = open(p).read()
        if '—' in c:
            open(p, 'w').write(c.replace(' — ', ': ').replace('—', ': '))
            print(f'  corrigé: {p}')
PYEOF
  npm run build > /tmp/pop_build.log 2>&1
fi

echo "=== 3. Commit + push ==="
git add -A
git -c user.name="hermes" -c user.email="hermes@nousresearch.com" commit -m "Deploy: $NB pages" 2>&1 | tail -1 || echo "rien à commiter"
git push -q origin main 2>&1 | tail -1 || true

echo "=== 4. Vérif live (attente rebuild CF ~90s) ==="
sleep 90
CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "https://practiceownerpro.pages.dev")
echo "pages.dev: $CODE"
CODE2=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "https://practiceownerpro.com")
echo "domaine: $CODE2"
echo "=== 5. Sitemap ==="
curl -s --max-time 15 "https://practiceownerpro.com/sitemap-0.xml" | grep -c "<loc>" || echo "sitemap à vérifier"
echo "DONE"
