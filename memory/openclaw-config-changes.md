# OpenClaw Config Changes (durable reference)

## 2026-02-22

### Reduced per-turn prompt injection
- Set `commands.nativeSkills=false` to stop injecting the large native skills catalog every turn (reduces context bloat).

### Token-saving “sleep mode” changes
- Disabled all cron jobs:
  - System health monitor
  - Hourly status update
  - Morning briefing (cost + weather + tokens)
- Reduced heartbeat to once/day:
  - `agents.defaults.heartbeat.every = "24h"`
  - active window: `10:00–10:05` `America/Toronto`

Notes:
- Disabling cron/heartbeat affects background autonomy/monitoring only; interactive Telegram messages still work normally.
