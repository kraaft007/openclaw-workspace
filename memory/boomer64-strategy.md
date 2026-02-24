# Boomer64 — Cross-Session Strategic Summary
Date: February 17, 2026
Source: Synthesized from multiple Claude.ai sessions

-----

## Brand Identity

Boomer64 is a YouTube channel targeting older professionals and patient learners who want AI/automation tutorials delivered at a deliberate, step-by-step pace — the antidote to fast-talking tech content. The "64" is Steve's birth year (1964), though viewers can interpret it however they like. The name was locked in early with the decision to let content quality earn credibility rather than worrying about the "boomer" label.

Channel positioning: "Vibe Coding for Boomers" — AI-assisted development tutorials for experienced professionals who prefer methodical, slower-paced instruction.

Tone: Experienced, practical, no hype. Slow, deliberate, nothing skipped.

Target audience: Older professionals, career-changers, patient learners, small business owners curious about AI, and younger viewers who prefer a slower pace.

-----

## Content Strategy

### Topic Sources (6 pillars)

1. Problems solved — FlyerApp, Claude Code billing fix, automation challenges
2. Learning journey — "Here's how I figured out X as a non-traditional coder"
3. Tool discoveries — n8n vs Zapier, screen recording options, macOS workflows
4. Commercial angles — "Can this become a product/service?"
5. Audience questions — Future: comments, DMs, community
6. AI for small business — Practical AI applications for everyday entrepreneurs (bakery, trades, local shops) — inspired by Marc Andreessen's "Democratization of AI" podcast

### 3-Stage Topic Refinement Funnel

- Stage 1: Brainstorm — Generate 10-15 raw topic ideas (simple list)
- Stage 2: Score — Rate top candidates on: Audience Interest, Credibility, Commercial Potential, Competition Level, Brand Fit (1-5 scale)
- Stage 3: Full Brief — Target audience, why it works, key points, hook angles

### First Video Topic (Pipeline Tested)

Winner: "How I Built a YouTube Transcript Tool Without Knowing How to Code"
Based on Steve's actual first Claude Code project — an automation script that takes a YouTube URL, extracts the transcript, uses Claude AI to organize it into paragraph sections with timestamps, and outputs a clean .MD file.

-----

## Content Production System

### 13-Step Creator Workflow

1. Topic generation
2. Hooks
3. Intros
4. Titles
5. Thumbnails
6. Script
7. Film
8. Edit
9. Publish
10. Repurpose (clips for Reels/X/Facebook/LinkedIn)
11. Cross-posting & scheduling
12. Engagement & analytics
13. Monetization tracking

Key design principle: Brand-agnostic. Build it once for Boomer64, hand the playbook to family for Willowood WildCraft. Same process, different content going in.

-----

## Digital Twin / Avatar

Explored using HeyGen to create a photorealistic digital twin for content production. A comprehensive workflow page was saved to Notion covering:
- Lighting setup (budget-conscious)
- iPhone 16 recording best practices
- Gesture capture strategy
- Platform selection (HeyGen vs alternatives)
- Integration into the Boomer64 content pipeline

-----

## Infrastructure — The Digital Workshop

### Architecture

- Host: Hawk Host VPS ($20 USD/mo), Toronto data center
- AI Gateway: OpenClaw, paired with Telegram for mobile management
- Blogging: Ghost (self-hosted) for all three brands
- Web Server: Nginx reverse proxy with Let's Encrypt SSL
- Containerization: Docker sandbox for tool execution
- AI Routing: Multi-model via OpenRouter (cost optimization)

### Cost Consolidation

| Item | DIY (VPS) | Scattered Services |
|------|-----------|-------------------|
| VPS Hosting | $20/mo | — |
| Website Hosting (x3) | Included | $15–45/mo |
| Blog Platform | Included (Ghost) | $10–15/mo |
| AI Gateway | Included (OpenClaw) | N/A |
| SSL Certificates | Free (Let's Encrypt) | $0–10/mo |
| OpenRouter API | ~$5–20/mo | $50–200/mo |
| **Total** | **~$25–40/mo** | **$75–270/mo** |

### Documentation

OpenClaw Digital Workshop Guide (Revision 9) — comprehensive .docx with architecture diagrams, step-by-step installation, security configuration, social media API appendices, troubleshooting, and Phase 2 roadmap (Nextcloud, Gitea).

-----

## Social Media Distribution Plan

| Platform | Approach | Cost |
|----------|----------|------|
| YouTube | Primary channel, API management (free) | Free |
| X (Twitter) | Content prep (free), optional API upgrade | Free / $100/mo opt. |
| Facebook | Content prep via Graph API | Free |
| Instagram | Content prep via Instagram Graph API | Free |
| LinkedIn Company Page | Boomer64 brand distribution | Free |
| LinkedIn Personal | Robotics XYZ visibility (separate) | Free |

Recommended start order: YouTube first (free API, natural fit), then X (content prep at no cost). OpenClaw manages distribution from Telegram — draft posts, schedule uploads, monitor mentions.

-----

## Cost Optimization — AI Billing

### Final Configuration

- Primary work: Claude Max subscription
- Overflow: Gemini Flash + DeepSeek/Gemini Lite via OpenRouter
- Total: ~$120/mo (subscriptions + API usage)

### Lessons Learned

- Claude Code context window bloat caused $28–159 billing spikes in early sessions
- Mitigation: .claudeignore files, hybrid subscription/API approach, cost monitoring via OpenRouter dashboard

-----

## Relationship to Other Ventures

| Venture | Focus | Lead | Platform |
|---------|-------|------|----------|
| **Boomer64** | AI/Claude Code/vibe coding tutorials | Steve (primary) | YouTube + social |
| **Willowood WildCraft** | Homesteading, bushcraft, traditional farming | Family (Steve contributes) | YouTube + social |
| **Robotics XYZ** | Industrial robotics consulting (Fanuc ASI) | Steve (selective) | LinkedIn personal |

All three share the same backend infrastructure (VPS, Ghost blogs, OpenClaw) and production system (13-step workflow).

-----

## Open Items / Next Steps

- [ ] Publish first Boomer64 video
- [ ] Complete VPS cover graphic (v3 needs beige CRT + wood plank desk)
- [ ] Finalize OpenClaw Mac Mini ↔ VPS connectivity (WebSocket auth issues)
- [ ] Regenerate exposed Telegram bot token (@smcc007_bot)
- [ ] Build out remaining stages of the 13-step workflow with Claude prompts
- [ ] Family discussion on Willowood WildCraft timeline and division of labor

-----

*Summary compiled from Claude.ai conversation history — February 17, 2026*
