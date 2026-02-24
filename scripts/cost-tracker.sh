#!/bin/bash
# OpenClaw Cost Tracker
# Queries OpenRouter API for usage and balance

API_KEY="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"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$HOME/.openclaw/workspace/memory/costs-$DATE.json"

echo "Fetching OpenRouter usage and balance..."

# Get auth key info (includes daily/weekly/monthly usage)
RESPONSE=$(curl -s https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer $API_KEY")

# Get actual credit balance (purchased credits, not rate limit)
CREDITS=$(curl -s https://openrouter.ai/api/v1/credits \
  -H "Authorization: Bearer $API_KEY")

# Check if we got data
if echo "$RESPONSE" | grep -q "error"; then
  echo "❌ Error fetching data:"
  echo "$RESPONSE" | python3 -m json.tool
  exit 1
fi

# Merge both responses and save
python3 -c "
import json, sys
auth = json.loads('$(echo "$RESPONSE" | tr -d '\n')')
credits = json.loads('$(echo "$CREDITS" | tr -d '\n')')
combined = {'auth': auth, 'credits': credits}
with open('$LOG_FILE', 'w') as f:
    json.dump(combined, f, indent=2)
print(json.dumps(combined, indent=2))
"

# Extract key metrics
echo ""
echo "📊 Summary:"
python3 -c "
import json
try:
    with open('$LOG_FILE', 'r') as f:
        data = json.load(f)
    auth = data.get('auth', {}).get('data', {})
    cred = data.get('credits', {}).get('data', {})
    total_credits = cred.get('total_credits', 0)
    total_usage = cred.get('total_usage', 0)
    remaining = round(total_credits - total_usage, 2)
    print(f'  💰 Credits Purchased: \${total_credits}')
    print(f'  📊 Total Usage: \${round(total_usage, 2)}')
    print(f'  ✅ Remaining: \${remaining}')
    print(f'  📅 Today: \${auth.get(\"usage_daily\", \"N/A\")}')
    print(f'  📆 This Week: \${auth.get(\"usage_weekly\", \"N/A\")}')
    print(f'  📊 This Month: \${auth.get(\"usage_monthly\", \"N/A\")}')
except Exception as e:
    print(f'  Parse error: {e}')
"

echo ""
echo "✅ Saved to: $LOG_FILE"
