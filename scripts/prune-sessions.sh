#!/usr/bin/env bash
# prune-sessions.sh — Remove skillsSnapshot from cron entries in sessions.json
# Safe to run anytime; the snapshots regenerate on next cron run.

SESSIONS_FILE="/home/openclaw/.openclaw/agents/main/sessions/sessions.json"

if [ ! -f "$SESSIONS_FILE" ]; then
  echo "sessions.json not found, nothing to do."
  exit 0
fi

BEFORE=$(stat -c%s "$SESSIONS_FILE" 2>/dev/null || echo 0)

# Use jq to strip skillsSnapshot from any entry that has one
if command -v jq &>/dev/null; then
  tmp=$(mktemp)
  jq 'walk(if type == "object" and has("skillsSnapshot") then del(.skillsSnapshot) else . end)' "$SESSIONS_FILE" > "$tmp" && mv "$tmp" "$SESSIONS_FILE"
  AFTER=$(stat -c%s "$SESSIONS_FILE" 2>/dev/null || echo 0)
  SAVED=$(( (BEFORE - AFTER) / 1024 ))
  echo "Pruned sessions.json: ${BEFORE}B → ${AFTER}B (saved ~${SAVED}KB)"
else
  echo "jq not installed, skipping."
  exit 1
fi
