# Security Notes (OpenClaw Workspace)

## Do not commit secrets
This repository must **never** contain:
- API keys (OpenRouter, Google, Groq, Supadata, Pexels, etc.)
- Bot tokens (Telegram)
- OAuth refresh tokens
- Private keys (SSH)

Store secrets in:
- `/home/openclaw/.openclaw/openclaw.json` (redacted when exported)
- environment variables
- a local-only `TOOLS.md` (this file is **gitignored**)
- password managers / provider dashboards

## Redaction policy
If a secret is accidentally written to a tracked file:
1) Replace it with a placeholder like `[REDACTED]`
2) Amend/rewrite the commit before pushing
3) Rotate the secret in the provider dashboard if it may have been exposed

## Push protection
GitHub secret scanning may block pushes if it detects known key patterns.
This is a feature, not a bug — treat it as a safety net.

## Recommended git hygiene
- Keep `.gitignore` up to date (logs/output/tmp/media/secrets)
- Prefer adding new secrets to `TOOLS.md` (which stays local) or env vars
