#!/bin/bash
# Token usage report for Claude Max proxy
# Reads JSONL logs from logs/token-usage/ and produces a summary
# Usage: bash scripts/token-report.sh [date] (default: today)

LOG_DIR="$HOME/.openclaw/workspace/logs/token-usage"
DATE="${1:-$(date +%Y-%m-%d)}"
LOG_FILE="$LOG_DIR/$DATE.jsonl"

if [ ! -f "$LOG_FILE" ]; then
    echo '{"date":"'"$DATE"'","requests":0,"total_input":0,"total_output":0,"total_cache_read":0,"total_cache_create":0,"by_model":{}}'
    exit 0
fi

# Use jq to aggregate
jq -s --arg date "$DATE" '
{
    date: $date,
    requests: length,
    total_input: (map(.input_tokens) | add // 0),
    total_output: (map(.output_tokens) | add // 0),
    total_cache_read: (map(.cache_read) | add // 0),
    total_cache_create: (map(.cache_create) | add // 0),
    by_model: (group_by(.model) | map({
        key: .[0].model,
        value: {
            requests: length,
            input: (map(.input_tokens) | add // 0),
            output: (map(.output_tokens) | add // 0),
            cache_read: (map(.cache_read) | add // 0),
            cache_create: (map(.cache_create) | add // 0)
        }
    }) | from_entries),
    first_request: (sort_by(.ts) | first.ts),
    last_request: (sort_by(.ts) | last.ts)
}' "$LOG_FILE"
