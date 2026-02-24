# Supadata Transcripts Skill

Extract transcripts from video URLs using the Supadata API.

## Supported Platforms
- YouTube
- TikTok
- Instagram
- X / Twitter
- Facebook

## Usage

```bash
# Basic usage (uses SUPADATA_API_KEY env var)
python3 /home/openclaw/.openclaw/workspace/skills/supadata-transcripts/scripts/get_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"

# With explicit API key
SUPADATA_API_KEY=sd_xxx python3 /home/openclaw/.openclaw/workspace/skills/supadata-transcripts/scripts/get_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Save output to file
python3 /home/openclaw/.openclaw/workspace/skills/supadata-transcripts/scripts/get_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" > transcript.txt
```

## How It Works

1. Sends `GET https://api.supadata.ai/v1/transcript?url=<video_url>` with the API key in the `x-api-key` header.
2. **Sync response** (short videos): The API returns the transcript immediately in the response body.
3. **Async response** (long videos): The API returns HTTP 202 with a `jobId`. The script polls `GET https://api.supadata.ai/v1/transcript/job/{jobId}` every 5 seconds until the transcript is ready (up to 5 minutes).

## Output Format

The script prints the plain-text transcript to stdout. If the API returns structured content (segments with timestamps), each segment is printed on its own line prefixed with the timestamp.

## Environment

- **Env var**: `SUPADATA_API_KEY`
- **Free tier**: 100 credits/month
- **Dashboard**: https://dash.supadata.ai

## API Reference

Full Supadata API docs (Transcript, Metadata, Web endpoints):
https://docs.supadata.ai/api-reference/introduction

## Product Links

- [YouTube Transcript API](https://supadata.ai/youtube-transcript-api)
- [TikTok Transcript API](https://supadata.ai/tiktok-transcript-api)
- [Instagram Transcript API](https://supadata.ai/instagram-transcript-api)
- [X (Twitter) Transcript API](https://supadata.ai/twitter-transcript-api)
- [Whisper V3 Turbo API](https://supadata.ai/video-transcript-api)
- [YouTube Data API](https://supadata.ai/youtube-api)
- [RapidAPI (YouTube)](https://rapidapi.com/8v2FWW4H6AmKw89/api/youtube-transcripts)
- [RapidAPI (Web)](https://rapidapi.com/8v2FWW4H6AmKw89/api/ai-content-scraper)

## Integrations

- [Make](https://supadata.ai/nocode#make)
- [Zapier](https://supadata.ai/nocode#zapier)
- [n8n](https://supadata.ai/nocode#n8n)
- [Active Pieces](https://supadata.ai/nocode#active-pieces)
- [MCP](https://github.com/supadata-ai/mcp)

## Error Handling

- Missing API key: exits with clear error message
- Invalid URL or unsupported platform: prints API error
- Network errors: prints error and exits with code 1
- Async timeout (5 min): prints timeout message and exits with code 1
