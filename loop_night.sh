#!/bin/bash
# BOUCLE NOCTURNE thefieldandfarm — production jusqu'au seuil solde 0.20$.
set -e
cd /root/thefieldandfarm
source /root/.hermes/.env 2>/dev/null
export DEEPSEEK_API_KEY
source /root/.env.github.global 2>/dev/null

LOG=/tmp/ff_loop.log
VAGUE=0
SEUIL=0.20
REPO_URL="https://x-access-token:${GH_TOKEN_GLOBAL}@github.com/YungSucre/thefieldandfarm.git"

log() { echo "[$(date +%H:%M)] $1" >> $LOG; }

get_balance() {
  curl -s --max-time 15 "https://api.deepseek.com/user/balance" -H "Authorization: Bearer $DEEPSEEK_API_KEY" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['balance_infos'][0]['total_balance'])" 2>/dev/null || echo 99
}

while true; do
  VAGUE=$((VAGUE+1))
  log "=== VAGUE $VAGUE ==="

  # 1. production 25 articles avec timeout 15 min
  timeout 900 python3 produce_ff.py --limit 25 > /tmp/ff_wave.log 2>&1 || true
  N=$(grep -c "✓" /tmp/ff_wave.log || echo 0)
  log "  produits: $N"
  [ "$N" = "0" ] && log "  rien produit — registre vide ou erreur" && break

  # 2. heroes (timeout)
  timeout 300 python3 fetch_heroes.py >> $LOG 2>&1 || log "  heroes timeout"

  # 3. build + push
  if npm run build > /tmp/ff_build.log 2>&1; then
    TOTAL=$(ls src/content/articles/*.md | wc -l)
    log "  build OK ($TOTAL articles)"
    git add -A
    git -c user.name="hermes" -c user.email="hermes@nousresearch.com" commit -q -m "Auto-vague $VAGUE: $TOTAL articles" 2>&1 | tail -1 >> $LOG || true
    git push -q "$REPO_URL" HEAD:main 2>&1 | tail -1 >> $LOG || log "  push échoué"
  else
    log "  BUILD FAIL — on continue"
  fi

  # 4. solde — stop si < SEUIL
  BAL=$(get_balance)
  log "  solde: $BAL"
  if (( $(echo "$BAL < $SEUIL" | bc -l 2>/dev/null || echo 0) )); then
    log "SOLDE BAS ($BAL) — arrêt propre"
    break
  fi
  sleep 10
done
log "BOUCLE TERMINÉE"
