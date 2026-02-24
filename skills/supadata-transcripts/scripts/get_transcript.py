#!/usr/bin/env python3
"""
Supadata Transcript Fetcher
Extracts transcripts from video URLs (YouTube, TikTok, Instagram, X/Twitter, Facebook)
using the Supadata API.

Usage:
    python3 get_transcript.py <video_url>

Environment:
    SUPADATA_API_KEY - Your Supadata API key (required)
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error

API_BASE = "https://api.supadata.ai/v1"
POLL_INTERVAL = 5      # seconds between async polls
MAX_POLL_TIME = 300     # 5 minutes max wait for async jobs
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"


def get_api_key():
    key = os.environ.get("SUPADATA_API_KEY", "").strip()
    if not key:
        print("ERROR: SUPADATA_API_KEY environment variable is not set.", file=sys.stderr)
        print("Set it with: export SUPADATA_API_KEY=sd_yourkey", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(url, api_key):
    """Make a GET request to the Supadata API and return (status_code, parsed_json | raw_text)."""
    req = urllib.request.Request(url)
    req.add_header("x-api-key", api_key)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", USER_AGENT)

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        status = resp.status
        body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"ERROR: Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = body

    return status, data


def format_timestamp(ms):
    """Convert milliseconds to MM:SS or HH:MM:SS format."""
    if ms is None:
        return ""
    try:
        total_seconds = int(ms) // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    except (ValueError, TypeError):
        return str(ms)


def format_transcript(data):
    """Extract and format the transcript text from the API response."""
    if isinstance(data, str):
        return data

    if isinstance(data, dict):
        lang = data.get("lang", "unknown")

        # The API returns "content" as a list of segment objects
        content = data.get("content")
        if isinstance(content, list) and content:
            lines = []
            for seg in content:
                if isinstance(seg, dict):
                    text = seg.get("text", "").strip()
                    offset = seg.get("offset")
                    if text:
                        ts = format_timestamp(offset)
                        if ts:
                            lines.append(f"[{ts}] {text}")
                        else:
                            lines.append(text)
                elif isinstance(seg, str):
                    lines.append(seg)
            if lines:
                header = f"Language: {lang}"
                return header + "\n\n" + "\n\n".join(lines)

        # If content is a plain string
        if isinstance(content, str):
            return content

        # Check for "transcript" key as fallback
        if "transcript" in data:
            return format_transcript(data["transcript"])

        # Segments / subtitles array (alternate response format)
        segments = data.get("segments") or data.get("subtitles") or data.get("results")
        if isinstance(segments, list):
            lines = []
            for seg in segments:
                if isinstance(seg, dict):
                    text = seg.get("text", "").strip()
                    offset = seg.get("start") or seg.get("offset") or seg.get("timestamp")
                    if text:
                        ts = format_timestamp(offset)
                        if ts:
                            lines.append(f"[{ts}] {text}")
                        else:
                            lines.append(text)
                elif isinstance(seg, str):
                    lines.append(seg)
            if lines:
                return "\n\n".join(lines)

        # Last resort: dump the JSON
        return json.dumps(data, indent=2)

    if isinstance(data, list):
        return "\n".join(str(item) for item in data)

    return str(data)


def poll_async_job(job_id, api_key):
    """Poll an async transcript job until it completes or times out."""
    url = f"{API_BASE}/transcript/job/{job_id}"
    elapsed = 0
    print(f"Async job started (ID: {job_id}). Polling every {POLL_INTERVAL}s...", file=sys.stderr)

    while elapsed < MAX_POLL_TIME:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        status, data = api_request(url, api_key)

        if isinstance(data, dict):
            job_status = data.get("status", "").lower()

            if job_status in ("completed", "done", "finished", "ready"):
                print(f"Job completed after {elapsed}s.", file=sys.stderr)
                return data

            if job_status in ("failed", "error"):
                error_msg = data.get("error") or data.get("message") or "Unknown error"
                print(f"ERROR: Async job failed: {error_msg}", file=sys.stderr)
                sys.exit(1)

            # Still processing
            print(f"  [{elapsed}s] Status: {job_status}...", file=sys.stderr)

        # If we got 200 with transcript content directly
        if status == 200 and isinstance(data, dict) and ("content" in data or "transcript" in data or "segments" in data):
            print(f"Job completed after {elapsed}s.", file=sys.stderr)
            return data

    print(f"ERROR: Async job timed out after {MAX_POLL_TIME}s.", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 get_transcript.py <video_url>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Supported: YouTube, TikTok, Instagram, X/Twitter, Facebook", file=sys.stderr)
        sys.exit(1)

    video_url = sys.argv[1]
    api_key = get_api_key()

    # Build request URL
    encoded_url = urllib.parse.quote(video_url, safe="")
    request_url = f"{API_BASE}/transcript?url={encoded_url}"

    print(f"Fetching transcript for: {video_url}", file=sys.stderr)

    status, data = api_request(request_url, api_key)

    # Handle async response (202 Accepted)
    if status == 202:
        if isinstance(data, dict) and "jobId" in data:
            data = poll_async_job(data["jobId"], api_key)
        else:
            print("ERROR: Got 202 but no jobId in response.", file=sys.stderr)
            print(f"Response: {json.dumps(data, indent=2) if isinstance(data, dict) else data}", file=sys.stderr)
            sys.exit(1)

    # Handle errors
    if status >= 400:
        if isinstance(data, dict):
            error_msg = data.get("error") or data.get("message") or json.dumps(data)
        else:
            error_msg = str(data)
        print(f"ERROR (HTTP {status}): {error_msg}", file=sys.stderr)
        sys.exit(1)

    # Format and print the transcript
    transcript = format_transcript(data)
    print(transcript)


if __name__ == "__main__":
    main()
