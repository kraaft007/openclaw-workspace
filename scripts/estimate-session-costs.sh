#!/bin/bash
# Estimate costs based on token usage
# Uses pricing from TOOLS.md

DATE=$(date +%Y-%m-%d)
LOG_FILE="$HOME/.openclaw/workspace/memory/daily-costs.md"

# Get session status
STATUS=$(openclaw status --all 2>/dev/null)

# Extract token counts (this is rough - adjust as needed)
echo "## Session Cost Estimate - $DATE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Pricing (per 1M tokens)
# Gemini Flash: FREE
# Claude Sonnet: FREE (subscription)
# DeepSeek: $0.14 input / $1.10 output
# Flash Lite: $0.075 input / $0.30 output

echo "**Current Session:**" | tee -a "$LOG_FILE"
echo "$STATUS" | grep -A5 "Sessions" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "**Pricing Notes:**" | tee -a "$LOG_FILE"
echo "- Gemini Flash: FREE (rate limited)" | tee -a "$LOG_FILE"
echo "- Claude Sonnet: FREE (your subscription)" | tee -a "$LOG_FILE"
echo "- DeepSeek: \$0.14 input / \$1.10 output per 1M" | tee -a "$LOG_FILE"
echo "- Flash Lite: \$0.075 input / \$0.30 output per 1M" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "✅ Logged to: $LOG_FILE"
