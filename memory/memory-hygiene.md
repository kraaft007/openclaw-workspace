# Memory Hygiene (Process)

Goal: Keep MEMORY.md small, curated, and high-signal so it stays <200 lines and remains useful.

## Rule of thumb
- MEMORY.md = durable facts, preferences, and stable infrastructure notes.
- memory/YYYY-MM-DD.md = daily log / raw notes.
- memory/<topic>.md = detailed reference docs (DNS, email, backups, etc.).

## What goes where
### Put in MEMORY.md
- Stable architecture facts (e.g., node/gateway topology)
- User preferences (e.g., daily cost report expectation)
- Critical “gotchas” learned once (e.g., Canvas workflow)
- Links to deeper topic files

### Put in daily notes (memory/YYYY-MM-DD.md)
- What we did today
- Temporary statuses, experiments, short-lived tasks
- One-off troubleshooting

### Create topic files when details matter
Create/append a topic file when the details are needed later:
- memory/dns-cloudflare.md
- memory/email-setup.md
- memory/openclaw-config-changes.md
- memory/automation-cron-jobs.md

## Maintenance workflow
- After any infra/config change, write a short entry in today’s daily note.
- If it’s likely to matter later, also update or create a topic file.
- When MEMORY.md approaches ~150–180 lines:
  - Move long sections into topic files
  - Leave only the summary + link in MEMORY.md

## Verification
- Periodically run: `wc -l MEMORY.md` and keep it comfortably <200.
