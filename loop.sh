#!/bin/bash
# BOUCLE AUTONOME practiceownerpro v2 — pour la nuit.
# Production par vagues (14 articles) → heroes → liens → build → deploy, en alternant
# les 37 verticals. Seuil d'arrêt bas (1.00$) pour maximiser la production.
# Timeout anti-blocage : une vague bloquée > 12 min est tuée et on continue.
set -e
cd /root/practiceownerpro
source /root/.hermes/.env 2>/dev/null
export DEEPSEEK_API_KEY

VERTICALS=("legal" "medical" "dental" "therapy" "vet" "physical-therapy" "pharmacy" "chiro" "optometry" "podiatry" "audiology" "speech-therapy" "medspa" "accounting" "financial-advisory" "occupational-therapy" "acupuncture" "naturopathy" "nutrition" "midwifery" "nurse-practice" "home-health" "aba-therapy" "functional-medicine" "plastic-surgery" "fertility" "architecture" "engineering" "consulting" "real-estate" "insurance-agency" "tutoring" "music-school" "martial-arts" "fitness-studio" "yoga-studio" "salon")
LOG=/tmp/pop_loop.log
VAGUE=0
SEUIL=1.00

log() { echo "[$(date +%H:%M)] $1" >> $LOG; }

get_balance() {
  curl -s --max-time 15 "https://api.deepseek.com/user/balance" -H "Authorization: Bearer $DEEPSEEK_API_KEY" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['balance_infos'][0]['total_balance'])" 2>/dev/null || echo 99
}

while true; do
  VAGUE=$((VAGUE+1))
  VERT=${VERTICALS[$(( (VAGUE-1) % ${#VERTICALS[@]} ))]}
  log "=== VAGUE $VAGUE ($VERT) ==="

  # 1. production avec timeout : 12 min max, sinon kill et continue
  systemd-run --unit=pop-prod-loop --collect --property=Restart=no \
    --property=TimeoutStopSec=20 \
    --setenv=DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
    /usr/bin/python3 /root/practiceownerpro/produce_pop.py --limit 14 --vertical $VERT \
    > /dev/null 2>&1 || true

  # attendre la fin avec timeout
  WAIT=0
  while systemctl is-active --quiet pop-prod-loop; do
    sleep 15
    WAIT=$((WAIT+15))
    if [ $WAIT -gt 720 ]; then
      log "  TIMEOUT 12min — kill vague bloquée"
      systemctl kill pop-prod-loop 2>/dev/null || true
      sleep 5
      break
    fi
  done
  N=$(journalctl -u pop-prod-loop --no-pager 2>/dev/null | grep -cE "✓" || true)
  log "  produits: $N"

  # 2. heroes (avec timeout)
  timeout 240 python3 fetch_heroes.py >> $LOG 2>&1 || log "  heroes timeout"

  # 3. liens internes
  timeout 120 python3 add_internal_links.py >> $LOG 2>&1 || log "  liens timeout"

  # 4. build (ne bloque jamais la boucle en cas d'échec)
  if npm run build > /tmp/pop_build.log 2>&1; then
    NB=$(grep -oE "[0-9]+ page\(s\) built" /tmp/pop_build.log | grep -oE "[0-9]+" | head -1)
    TOTAL=$(ls src/content/articles/*.md | wc -l)
    log "  build: $NB pages ($TOTAL articles)"
    # 5. deploy
    git add -A
    git -c user.name="hermes" -c user.email="hermes@nousresearch.com" commit -m "Auto-vague $VAGUE: $TOTAL articles" 2>&1 | tail -1 >> $LOG || true
    git push -q origin main 2>&1 | tail -1 >> $LOG || true
  else
    log "  BUILD FAIL — on continue (prochaine vague)"
    grep -a "ERROR" /tmp/pop_build.log | tail -2 >> $LOG || true
  fi

  # 6. solde — stop si < SEUIL
  BAL=$(get_balance)
  log "  solde: $BAL"
  if (( $(echo "$BAL < $SEUIL" | bc -l 2>/dev/null || echo 0) )); then
    log "SOLDE BAS ($BAL) — arrêt propre"
    break
  fi
  sleep 20
done
log "BOUCLE TERMINÉE"
