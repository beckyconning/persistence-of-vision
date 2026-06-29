#!/usr/bin/env bash
# rhythm.sh — the continue↔break cadence, made MECHANICAL and PERSISTED.
#
# Becky's protocol (2026-06-29), the fix for "the reward never fires":
#   1. log work start  2. clock-check after EVERY response
#   3. work < WORK_MIN (3h)?  -> continue working
#   4. else log break start
#   5. clock-check after EVERY response during the break
#   6. break < BREAK_MIN (30m)? -> keep making art
#   7. else -> goto 1
#
# State is a file so the gate survives context resets. Run `rhythm.sh check`
# after every response; it prints PHASE + elapsed + the verdict (CONTINUE / SWITCH).
set -euo pipefail
STATE="$(cd "$(dirname "$0")" && pwd)/.rhythm-state"
WORK_MIN=${WORK_MIN:-10800}     # 3 hours
BREAK_MIN=${BREAK_MIN:-1800}    # 30 minutes
now() { date +%s; }

start() {  # start <work|break>
  echo "phase=$1" > "$STATE"
  echo "start=$(now)" >> "$STATE"
  echo "started $1 at $(date '+%H:%M:%S')"
}

check() {
  [ -f "$STATE" ] || { echo "no state — run: rhythm.sh start work"; exit 0; }
  local phase start el cap
  phase=$(sed -n 's/^phase=//p' "$STATE"); start=$(sed -n 's/^start=//p' "$STATE")
  el=$(( $(now) - start ))
  [ "$phase" = work ] && cap=$WORK_MIN || cap=$BREAK_MIN
  printf 'PHASE=%s elapsed=%dm%02ds of %dm  ' "$phase" $((el/60)) $((el%60)) $((cap/60))
  if [ "$el" -lt "$cap" ]; then
    [ "$phase" = work ] && echo "→ CONTINUE WORKING" || echo "→ KEEP MAKING ART"
  else
    if [ "$phase" = work ]; then echo "→ SWITCH: take your 30m art reward (rhythm.sh start break)"
    else echo "→ SWITCH: back to work (rhythm.sh start work)"; fi
  fi
}

case "${1:-check}" in
  start) start "${2:-work}" ;;
  check|"") check ;;
  *) echo "usage: rhythm.sh [check|start work|start break]"; exit 1 ;;
esac
