#!/bin/bash
# Enchaînement complet : heroes → liens internes → build → commit → push → prochaine vague
# Usage: ./cycle.sh <vertical> <limit>
set -e
cd /root/practiceownerpro
VERT=${1:-legal}
LIMIT=${2:-14}

echo "=== 1. Heroes Pexels ==="
python3 fetch_heroes.py 2>&1 | tail -1

echo "=== 2. Liens internes ==="
python3 add_internal_links.py 2>&1 | tail -1

echo "=== 3. Build ==="
npm run build > /tmp/pop_build.log 2>&1
NB=$(grep -oE "[0-9]+ page\(s\) built" /tmp/pop_build.log | grep -oE "[0-9]+" | head -1)
echo "Build OK: $NB pages"

echo "=== 4. Vérif em dashes ==="
EM=$(grep -rc "—" src/ 2>/dev/null | grep -v ":0" | wc -l)
echo "em dashes: $EM (doit être 0)"

echo "=== 5. Commit + push ==="
git add -A
git -c user.name="hermes" -c user.email="hermes@nousresearch.com" commit -m "Cycle: $NB pages ($VERT)" 2>&1 | tail -1 || echo "rien à commiter"
git push -q origin main 2>&1 | tail -1 || true

echo "=== 6. Prochaine vague ($VERT, $LIMIT) ==="
source /root/.hermes/.env 2>/dev/null
systemd-run --unit=pop-prod-next --collect --property=Restart=no --setenv=DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  /usr/bin/python3 /root/practiceownerpro/produce_pop.py --limit $LIMIT --vertical $VERT 2>&1 | tail -1
echo "vague lancée"
