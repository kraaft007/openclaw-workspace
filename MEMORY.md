# MEMORY.md - Long-Term Memory

## Canvas Rendering (Learned 2026-02-17)

**How to display HTML on the Mac Canvas:**

1. `canvas.present` — opens the Canvas window on the Mac node (must be connected)
2. `canvas.eval` — inject full HTML directly via JavaScript (e.g., `document.documentElement.innerHTML = '...'`)

**What works:**
- `canvas.present` → `canvas.eval` with the full HTML content. This is the reliable method.

**What doesn't work:**
- `canvas.navigate` to a VPS-local file path — the Mac can't reach it
- CLI commands like `openclaw canvas` — Canvas is an internal agent tool, not a CLI command
- `openclaw nodes list` can show stale data — the Mac app Instances page is more reliable

**Prerequisites:**
- Mac node must be connected (check Instances page in Mac app or system Node events in session)
- Dashboard/webchat connection alone is NOT enough — the native node connection is needed

## Mac Node Architecture (Learned 2026-02-17)

The Mac app has **two separate connections** to the VPS gateway:
1. **Dashboard/webchat** (Safari-based) — mirrors Telegram chat, re-pairs easily
2. **Node** (native background service via Tailscale) — needed for Canvas, camera, Apple Notes

These can be in different states. A gateway restart can break the node connection while the Dashboard reconnects fine. Full app restart (Cmd+Q → relaunch) usually fixes the node connection.

**Instances page** shows all connections. Typical healthy state:
- `digital-workshop.hawkhost.com` — Active, gateway (VPS)
- `Mac mini` (local IP) — Active, remote mode (Dashboard)
- `Mac mini` (Tailscale IP) — Active/Idle, node mode (native node)

## Steven's Preferences

### Daily Cost Report (Set 2026-02-17)
- **Always relay the 8:30 AM cost report**, even when everything is green / $0 usage
- Steven wants it as a daily proof-of-life signal, not just for alerts

### Memory Hygiene (Set 2026-02-22)
- Steven asked Albert to write more aggressively to memory files (MEMORY.md / memory/*.md), especially after infrastructure/config changes (e.g., DNS/Cloudflare, model chain changes), so critical setup context isn’t lost.

## Backup System (Learned 2026-02-17)

**Two-tier backup strategy:**
1. **Mac Mini full backup** (weekly, Mon 4 AM) — rsync over Tailscale, ~360MB, 4 weeks retained. Covers entire VPS: home dir, /etc, systemd, crontabs, tailscale, firewall, package manifests, generated REBUILD.md. Script: `~/bin/backup-vps.sh` on Mac. Excludes session .jsonl, node_modules, caches.
2. **VPS config-only backup** (manual) — 6 critical config files, last 10 snapshots. Script: `~/bin/openclaw-backup.sh`. For quick rollbacks before risky changes.

Full details: `memory/backup-guide.md`

## Boomer64 YouTube Channel (Learned 2026-02-17)

Steven is building a YouTube channel called **Boomer64** — "Vibe Coding for Boomers." AI/automation tutorials at a deliberate, step-by-step pace for older professionals and patient learners. The "64" is his birth year (1964).

**Key facts:**
- First video topic: "How I Built a YouTube Transcript Tool Without Knowing How to Code"
- 13-step creator workflow (brand-agnostic — reusable for family's Willowood WildCraft channel)
- 6 content pillars: problems solved, learning journey, tool discoveries, commercial angles, audience questions, AI for small business
- Explored HeyGen digital twin/avatar for content production
- Social distribution plan: YouTube first, then X, Facebook, Instagram, LinkedIn
- All three ventures (Boomer64, Willowood WildCraft, Robotics XYZ) share VPS infrastructure

**Three ventures:**
1. **Boomer64** — AI/coding tutorials (primary, Steve leads)
2. **Willowood WildCraft** — Homesteading/bushcraft (family, Steve contributes)
3. **Robotics XYZ** — Industrial robotics consulting, Fanuc ASI (Steve, selective/LinkedIn)

Full strategy doc: `memory/boomer64-strategy.md`

**Open items:** First video still unpublished, VPS cover graphic needs v3, exposed @smcc007_bot token needs regenerating

## Ghost Blog (Set up 2026-02-17)

**Private blog running on VPS via Docker + Tailscale.**

- **Container**: `ghost-blog` (ghost:5-alpine, SQLite backend)
- **Docker Compose**: `/home/openclaw/docker/ghost/docker-compose.yml`
- **Data volume**: `ghost_ghost-content` (Docker managed)
- **Internal port**: `127.0.0.1:2368`
- **Access URL**: `https://digital-workshop.tail49c145.ts.net:8443`
- **Admin panel**: `https://digital-workshop.tail49c145.ts.net:8443/ghost/`
- **Memory footprint**: ~170MB
- **Tailscale Serve**: port 8443 → localhost:2368
- **First step**: Steven needs to visit `/ghost/` to create admin account
- **Future**: Add custom domain, Nginx reverse proxy when going public
