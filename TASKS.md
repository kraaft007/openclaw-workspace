# Active Tasks

## [x] Get access to an Image Generation tool
- **Added:** 2026-02-17
- **Completed:** 2026-02-18
- **Notes:** ✅ Using Google Gemini API (Nano Banana Pro) via `gemini-image-simple` skill. API key stored in TOOLS.md. Pay-as-you-go billing enabled.

## [x] Build Supadata Transcripts skill
- **Added:** 2026-02-18
- **Completed:** 2026-02-18
- **Priority:** Medium
- **Notes:** ✅ Built custom skill at `skills/supadata-transcripts/`. Python script fetches transcripts from YouTube, TikTok, Instagram, X/Twitter, Facebook via Supadata API. Handles sync and async responses. API key stored in TOOLS.md and as `SUPADATA_API_KEY` env var. Tested and working.

## [ ] Set up boomer64.tv and boomer64.life redirects
- **Added:** 2026-02-18
- **Priority:** Low
- **Notes:** Both domains purchased on GoDaddy. Need to onboard to Cloudflare (like boomer64.com) and set up 301 redirects to boomer64.com. Can use Cloudflare API token.

## [ ] Build custom thumbnail-moodboard skill
- **Added:** 2026-02-18
- **Priority:** Medium
- **Notes:** Not available publicly. Build using writing-skills skill. Visual moodboard generation for YouTube thumbnails.

## [ ] Build custom video-input-analysis skill
- **Added:** 2026-02-18
- **Priority:** Medium
- **Notes:** Not available publicly. Build using writing-skills skill. Analyze video content for insights, competitor research.

## [x] Regenerate exposed Telegram bot token (@smcc007_bot)
- **Added:** 2026-02-17
- **Completed:** 2026-02-18
- **Priority:** High
- **Notes:** ✅ Steven deleted the token on 2026-02-18.

## [ ] Automate Albert inbox monitoring (Gmail API)
- **Added:** 2026-02-23
- **Priority:** Medium
- **Notes:** Set up Gmail API OAuth for albert@boomer64.com and run a VPS script/service to poll unread mail and send summaries to Steven via Telegram. Decide polling interval and whether to mark as read/label after notifying.

*Last updated: 2026-02-23*
