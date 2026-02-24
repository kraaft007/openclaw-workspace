#!/usr/bin/env bash
# token-summary.sh — Summarize Claude Max proxy token usage from JSONL logs
# Usage: bash scripts/token-summary.sh [date]
# Default: today's date

set -euo pipefail

LOG_DIR="$HOME/.openclaw/workspace/logs/token-usage"
DATE="${1:-$(date +%Y-%m-%d)}"
LOG_FILE="$LOG_DIR/$DATE.jsonl"

if [[ ! -f "$LOG_FILE" ]]; then
  echo "No token usage data for $DATE"
  exit 0
fi

# Use jq to aggregate
jq -s '
  {
    date: "'$DATE'",
    total_requests: length,
    total_input: (map(.input_tokens) | add // 0),
    total_output: (map(.output_tokens) | add // 0),
    total_cache_read: (map(.cache_read) | add // 0),
    total_cache_create: (map(.cache_create) | add // 0),
    by_model: (group_by(.model) | map({
      model: .[0].model,
      requests: length,
      input: (map(.input_tokens) | add // 0),
      output: (map(.output_tokens) | add // 0),
      cache_read: (map(.cache_read) | add // 0),
      cache_create: (map(.cache_create) | add // 0)
    }))
  }
' "$LOG_FILE"
