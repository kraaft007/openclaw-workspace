# Health Monitor PRD & Implementation Plan
## System Health Check Cron Job — Specification Document

**Author:** OpenClaw Agent (Opus)
**Date:** 2026-02-15
**Status:** DRAFT v2 — Revised per Opus critique
**Reference:** Steven's task prompt spec (2026-02-15 03:19 AM EST)
**Reviewer:** Claude Opus (critique received 2026-02-15 01:18 PM EST)

---

## 1. Purpose

**Why are we building this?**

Right now, if a service crashes, memory spikes, or the proxy starts throwing errors, nobody knows until something visibly breaks. Steven discovers problems by accident — a failed message, a hung session, a surprise bill.

This health monitor eliminates that gap. It runs autonomously every 30 minutes, checks the five things that matter most (services, errors, resources, kernel, proxy), and only speaks up when something is wrong. Silent when healthy. Loud when not.

**The problem it solves:**
- No automated monitoring of claude-max-proxy or openclaw-gateway
- No alerting on resource exhaustion (memory, disk)
- No visibility into error patterns (rate limits, billing, timeouts)
- No OOM kill or kernel error detection
- Manual checks are sporadic and easily forgotten

---

## 2. Success Criteria

**What "done" looks like:**

| Criterion | Measure |
|-----------|---------|
| Cron job runs every 30 min | Verified in `openclaw cron list` with consistent execution history |
| ALL CLEAR when healthy | No Telegram messages during normal operation |
| ALERT on real issues | Telegram message within ~1 min of detection |
| No false positives | Zero spurious alerts over 48-hour burn-in period |
| No token waste | Haiku via Max subscription = $0.00 per run |
| Fault-tolerant | Missing log files or command failures don't crash the monitor |
| Self-documenting | Alert messages are actionable without needing to SSH in |
| No alert fatigue | Duplicate alerts suppressed after first notification |

**What "done" does NOT look like:**
- Raw log dumps in Telegram
- Alerts for routine events (normal restarts, expected warnings)
- Multiple messages per check cycle (one message, one verdict)
- Alerts during scheduled maintenance windows
- 48 identical Telegram alerts over 24 hours for the same issue

---

## 3. Architecture

```
┌─────────────────────────────────────────────────┐
│                  OpenClaw Gateway                │
│                                                  │
│  ┌──────────┐    every 30 min    ┌───────────┐  │
│  │   Cron   │ ──────────────────>│  Haiku    │  │
│  │ Scheduler│                    │ Sub-agent │  │
│  └──────────┘                    └─────┬─────┘  │
│                                        │        │
│                              ┌─────────┴────────┤
│                              │   Tool Calls      │
│                              │                   │
│                    ┌─────────┼─────────┐         │
│                    ▼         ▼         ▼         │
│              ┌─────────┐ ┌──────┐ ┌────────┐    │
│              │  read   │ │ exec │ │message │    │
│              │ (files) │ │(cmds)│ │(alert) │    │
│              └────┬────┘ └──┬───┘ └───┬────┘    │
│                   │         │         │         │
└───────────────────┼─────────┼─────────┼─────────┘
                    │         │         │
          ┌─────────┘         │         └──────────┐
          ▼                   ▼                    ▼
   ┌─────────────┐  ┌──────────────┐      ┌────────────┐
   │ Log Files   │  │  systemctl   │      │  Telegram   │
   │ (~/.openclaw│  │  journalctl  │      │  (Steven)   │
   │  /logs/)    │  │              │      │             │
   └─────────────┘  └──────────────┘      └────────────┘

   ┌─────────────┐
   │ State File  │  <── alert-state.json (dedup tracking)
   │ (workspace) │
   └─────────────┘
```

**Flow:**
1. Gateway cron scheduler triggers every 30 minutes
2. Spawns isolated Haiku sub-agent with the health check prompt
3. Haiku reads 3 log files + runs 3 system commands
4. Haiku evaluates 5 check categories against thresholds
5. Haiku reads `alert-state.json` to check for duplicate alerts
6. **If ALL CLEAR:** Responds with `HEARTBEAT_OK` → Gateway discards (no delivery). Clears alert state.
7. **If ALERT(s) found (new):** Uses `message` tool to send alert to Telegram → Writes alert state → Responds `HEARTBEAT_OK`
8. **If ALERT(s) found (duplicate):** Suppresses Telegram send. If >2h since last alert for same issue, sends a reminder at reduced frequency.

---

## 4. Process Flow

### 4.1 Inputs

| # | Input | Type | Source | Purpose |
|---|-------|------|--------|---------|
| 1 | `syslog-filtered.log` | File read | `~/.openclaw/logs/` | System-level events, errors, warnings |
| 2 | `system-info.txt` | File read | `~/.openclaw/logs/` | Resource snapshot (memory, disk, load, ports) |
| 3 | `kernel-alerts.log` | File read | `~/.openclaw/logs/` | OOM kills, kernel errors |
| 4 | claude-max-proxy journal | Command | `journalctl --user -u claude-max-proxy --since "35 min ago"` | Proxy health, exit codes, crashes |
| 5 | openclaw-gateway journal | Command | `journalctl --user -u openclaw-gateway --since "35 min ago"` | Gateway health, restarts |
| 6 | Service status | Command | `systemctl --user is-active` | Current service state |
| 7 | `alert-state.json` | File read | `~/.openclaw/workspace/` | Previous alert state for deduplication |

**Root cron dependency:** Inputs 1-3 are refreshed by a root cron job every 5 minutes. The health monitor reads stale-but-recent snapshots, not live logs.

**Time window overlap (critique #2 fix):** Journal queries use `--since "35 min ago"` instead of `"30 min ago"` to ensure 5-minute overlap between cycles. This prevents gaps if a check takes 2+ minutes to complete.

### 4.2 Checks (Processing)

| # | Check | What to Look For | Threshold | Source |
|---|-------|-------------------|-----------|--------|
| 1 | **Services** | Are both services `active`? Any restarts/crashes in last 35 min? | Status ≠ active, or restart detected | Input 4, 5, 6 |
| 2 | **Errors** | Pattern-matched keywords (see 4.2.1) | Any match after exclusion filtering | Input 1, 4, 5 |
| 3 | **Resources** | Memory usage, disk usage, load average | Memory > 85%, Disk > 80%, Load > 3.0 | Input 2 |
| 4 | **Kernel** | OOM kills, kernel-level errors | Any occurrence | Input 3 |
| 5 | **Proxy** | Non-zero exit codes, crash loops | Any non-zero exit or repeated restarts | Input 4 |

#### 4.2.1 Error Keyword Matching (critique #1 fix)

**Problem:** Bare `"error"` matches benign proxy stderr output like `[Subprocess stderr]:` which is normal debug logging.

**Solution:** Use word-boundary-aware patterns and explicit exclusions:

**Match patterns (case-insensitive):**
- ` error:` or ` error ` (with surrounding spaces/punctuation — avoids `stderr`)
- `fatal`
- `panic`
- `billing`
- `rate_limit` or `rate limit`
- `cooldown`
- `refused`
- `timeout`
- `OOM` or `out of memory`

**Exclude patterns (known-benign):**
- Lines containing `[Subprocess stderr]:` (proxy debug output)
- Lines containing `error_format` (config key, not an error)
- Lines containing `error.log` (log path reference, not an error)

**Implementation note:** Haiku performs the matching. The prompt instructs it to apply these specific patterns rather than naive keyword search.

### 4.3 Outputs

| Condition | Output | Delivery |
|-----------|--------|----------|
| All checks pass | `HEARTBEAT_OK` | Discarded by Gateway (no delivery) |
| New alert(s) found | ALERT lines via `message` tool | Sent to Telegram immediately |
| Duplicate alert(s) only | `HEARTBEAT_OK` + state update | Suppressed (no Telegram). Reminder at 2h intervals. |
| All-clear after previous alert | `HEARTBEAT_OK` + state cleared | Optional: send ✅ RESOLVED message |

**Alert format (one line per issue):**
```
🔴 HEALTH ALERT

ALERT: claude-max-proxy crashed and restarted at 03:12
ALERT: Memory at 91% (3.5G/3.8G)
ALERT: rate_limit errors in syslog (3 occurrences)
```

### 4.4 Deduplication Logic (critique #3 fix)

**Problem:** If a service crashes and stays down, every 30-min cycle fires the same alert. 48 identical Telegram messages over 24 hours = alert fatigue.

**Solution:** Track alert state in `~/.openclaw/workspace/alert-state.json`:

```json
{
  "activeAlerts": {
    "claude-max-proxy-down": {
      "firstSeen": "2026-02-15T03:12:00Z",
      "lastAlerted": "2026-02-15T03:12:00Z",
      "count": 1,
      "message": "claude-max-proxy is not active"
    }
  },
  "lastCheckTime": "2026-02-15T03:42:00Z"
}
```

**Rules:**
1. **New alert** (key not in `activeAlerts`): Send immediately. Write to state.
2. **Duplicate alert** (key exists, `lastAlerted` < 2 hours ago): Suppress. Increment `count`.
3. **Stale duplicate** (key exists, `lastAlerted` ≥ 2 hours ago): Send reminder: `🟡 ONGOING: claude-max-proxy still down (first detected 03:12, 4 cycles ago)`. Update `lastAlerted`.
4. **Resolved** (key exists but check now passes): Send: `✅ RESOLVED: claude-max-proxy is back up (was down for 2h)`. Remove from state.
5. **State file missing/corrupt**: Treat all alerts as new. Recreate state file.

### 4.5 Responsibilities

| Component | Owner | Responsibility |
|-----------|-------|----------------|
| Log file refresh | Root cron (every 5 min) | Keep `~/.openclaw/logs/` current |
| Cron scheduling | OpenClaw Gateway | Trigger health check every 30 min |
| Health evaluation | Haiku sub-agent | Read inputs, run checks, decide verdict |
| Alert delivery | Haiku via `message` tool | Send alerts to Telegram |
| Alert dedup | Haiku via `alert-state.json` | Suppress duplicate alerts |
| Alert silence | Gateway | Discard `HEARTBEAT_OK` responses |
| Threshold tuning | Steven | Adjust thresholds based on false positive/negative rate |
| Escalation | Opus (main session) | Investigate if Haiku reports repeated failures |

---

## 5. Edge Cases & Fault Handling

### 5.1 Missing or Empty Log Files

**Scenario:** Root cron hasn't run yet, or a log file is missing/empty.
**Handling:** Haiku should note the missing file but NOT treat it as an alert. Report: `INFO: kernel-alerts.log is empty (no kernel errors — this is normal)`
**Rationale:** `kernel-alerts.log` is often empty. Missing `syslog-filtered.log` would be unusual but not an emergency.

### 5.2 Command Execution Failure

**Scenario:** `journalctl` or `systemctl` command fails (permission denied, service not found).
**Handling:** Report as alert: `ALERT: Failed to query claude-max-proxy journal — command returned error`
**Rationale:** If we can't check, we should say so. A monitoring blind spot is itself a problem.

### 5.3 Sub-Agent Failure (Haiku Crash/Timeout)

**Scenario:** Haiku sub-agent crashes, times out, or returns garbage.
**Handling:** Gateway's built-in cron error handling logs the failure. Next cycle retries automatically with exponential backoff (30s → 1m → 5m → 15m → 60m). Backoff resets after next successful run.
**Escalation:** If 3+ consecutive failures, Gateway surfaces the error to the main session.

### 5.4 False Positives — Routine Warnings

**Scenario:** Syslog contains expected warnings (e.g., routine systemd messages, SSH login attempts, proxy stderr debug lines).
**Handling:** Error matching uses word-boundary patterns and explicit exclusion list (see 4.2.1). Generic `warning` is excluded. `[Subprocess stderr]:` lines are excluded.
**Tuning:** If false positives occur, we add exclusion patterns to the prompt.

### 5.5 Telegram Delivery Failure

**Scenario:** `message` tool fails (Telegram API down, bot token expired, network issue).
**Handling:** Alert is lost for this cycle. The alert remains in `alert-state.json` as "new" (since `lastAlerted` was never updated). Next cycle will re-attempt delivery.
**Mitigation:** `bestEffort: true` on the cron job delivery config prevents the job itself from failing.

### 5.6 Stale Log Files

**Scenario:** Root cron stops running, log files become hours old.
**Handling:** Haiku should check file modification timestamps. If `syslog-filtered.log` is older than 15 minutes, report: `ALERT: syslog-filtered.log is stale (last updated X min ago) — root cron may have stopped`
**Rationale:** Stale monitoring data is a silent failure. Catch it.

### 5.7 Rate Limiting / Model Unavailability

**Scenario:** Haiku is rate-limited or unavailable via Max proxy.
**Handling:** Gateway's fallback chain handles this automatically (Haiku → Flash → DeepSeek).
**Note:** The health check prompt is simple enough for any model in the chain.

### 5.8 Alert State File Corruption

**Scenario:** `alert-state.json` is malformed or deleted.
**Handling:** Haiku treats all current alerts as new (worst case: one duplicate alert sent). Recreates the state file from scratch.

### 5.9 Sub-Agent Tool Availability (critique #4 fix)

**Scenario:** Haiku sub-agent spawned by cron may not have access to all OpenClaw tools.
**Verification required:** Before implementation, we must confirm that isolated cron sub-agents have access to:
- `read` (file reading) — needed for log files and alert-state.json
- `exec` (command execution) — needed for journalctl/systemctl
- `write` (file writing) — needed for alert-state.json updates
- `message` (Telegram delivery) — needed for alert sending

**Test plan:** Run a one-shot test job that attempts each tool and reports back. See Phase 1 in Section 7.

---

## 6. Sub-Agent Prompt (Complete)

```
You are a system health monitor. Be terse. No explanations.

FILES TO READ:
1. ~/.openclaw/logs/syslog-filtered.log
2. ~/.openclaw/logs/system-info.txt
3. ~/.openclaw/logs/kernel-alerts.log
4. ~/.openclaw/workspace/alert-state.json (for deduplication — may not exist yet)

COMMANDS TO RUN:
- journalctl --user -u claude-max-proxy --no-pager -n 20 --since "35 min ago"
- journalctl --user -u openclaw-gateway --no-pager -n 20 --since "35 min ago"
- systemctl --user is-active claude-max-proxy openclaw-gateway

CHECKS:
1. Services: Are claude-max-proxy and openclaw-gateway both active? Any restarts or crashes in the last 35 min?
2. Errors: Search syslog and journal output for these patterns (case-insensitive):
   MATCH: " error:" or " error " (word boundaries), "fatal", "panic", "billing", "rate_limit", "rate limit", "cooldown", "refused", "timeout", "OOM", "out of memory"
   EXCLUDE: lines containing "[Subprocess stderr]:", "error_format", "error.log"
3. Resources: Memory usage above 85%? Disk usage above 80%? Load average above 3.0?
4. Kernel: Any OOM kills or kernel errors?
5. Proxy: Any non-zero exit codes or crash loops in the proxy journal?
6. Staleness: Is syslog-filtered.log older than 15 minutes? (check file modification time)

DEDUPLICATION:
- Read alert-state.json. If it doesn't exist or is malformed, treat all alerts as new.
- For each alert found, generate a short key (e.g. "proxy-down", "memory-high", "rate-limit").
- If the key exists in activeAlerts AND lastAlerted was less than 2 hours ago: SUPPRESS (don't send).
- If the key exists but lastAlerted was 2+ hours ago: send as "🟡 ONGOING" reminder.
- If the key is new: send immediately.
- If a previous alert key is NOT found in this check: it resolved. Send "✅ RESOLVED" message.
- Write updated alert-state.json after all checks.

RESPONSE RULES:
- If everything is normal: respond with exactly HEARTBEAT_OK
- If ANY new or reminder alert is found: use the message tool to send to Telegram, then respond HEARTBEAT_OK
- Alert format — one line per issue:

  🔴 HEALTH ALERT
  ALERT: claude-max-proxy crashed and restarted at 03:12
  ALERT: Memory at 91% (3.5G/3.8G)

  For ongoing issues:
  🟡 ONGOING (first detected 2h ago)
  ALERT: claude-max-proxy still not active

  For resolved issues:
  ✅ RESOLVED
  OK: claude-max-proxy is back up (was down 2h)

- If a file is missing or empty: note it as INFO, not ALERT (kernel-alerts.log is often empty)
- If a command fails: report as ALERT (monitoring blind spot)
- Do NOT include raw log dumps
- Do NOT explain what you checked
- Only output the verdict
```

---

## 7. Implementation Plan (critique #5 fix — concrete config)

### Phase 0: Verify Sub-Agent Tool Access

**Action:** Create a one-shot test job to confirm Haiku cron sub-agents can use all required tools.

**Exact cron tool call:**
```json
{
  "action": "add",
  "name": "Health monitor tool test",
  "schedule": { "kind": "at", "at": "<5 min from now, ISO 8601>" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Test tool access. Do each of these and report pass/fail:\n1. Read file: ~/.openclaw/logs/syslog-filtered.log (first 5 lines)\n2. Run command: systemctl --user is-active openclaw-gateway\n3. Write file: ~/.openclaw/workspace/tool-test-result.txt with content 'tools work'\n4. Use message tool to send 'Tool test passed' to Telegram\nReport which tools worked and which didn't.",
    "model": "copilot-proxy/claude-haiku-4-5",
    "timeoutSeconds": 60
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "bestEffort": true
  },
  "deleteAfterRun": true
}
```

**Success criteria:** All 4 tools work. If `message` tool is unavailable, fall back to `delivery.mode: "announce"` for alerts (Gateway delivers instead of Haiku).

### Phase 1: Create the Health Monitor Cron Job

**Exact cron tool call:**
```json
{
  "action": "add",
  "name": "System health monitor",
  "schedule": {
    "kind": "cron",
    "expr": "*/30 * * * *",
    "tz": "America/Toronto"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "<full sub-agent prompt from Section 6>",
    "model": "copilot-proxy/claude-haiku-4-5",
    "timeoutSeconds": 120
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "bestEffort": true
  }
}
```

**Notes:**
- `delivery.mode: "announce"` — HEARTBEAT_OK responses are automatically discarded by Gateway
- `bestEffort: true` — prevents job failure if Telegram delivery fails
- `timeoutSeconds: 120` — generous timeout for file reads + command execution
- Model explicitly set to Haiku via Max proxy ($0.00/run)
- If Phase 0 shows `message` tool works: Haiku sends alerts directly, Gateway discards the HEARTBEAT_OK
- If Phase 0 shows `message` tool doesn't work: Haiku includes alerts in its response text, Gateway `announce` delivers them to Telegram

### Phase 2: Verify First Run

- Watch for first execution: `cron.runs` with the job ID
- Confirm Haiku can read all 3 log files
- Confirm Haiku can run all 3 commands
- Confirm ALL CLEAR produces no Telegram message
- Manually trigger an alert condition to test delivery (e.g., `systemctl --user stop openclaw-gateway` briefly)

### Phase 3: Burn-In (48 hours)

- Monitor for false positives
- Check that alerts are actionable
- Tune error keyword patterns if needed
- Verify no token cost (all Haiku via Max)
- Validate deduplication: simulate a sustained failure and confirm only 1 alert + 2h reminders

### Phase 4: Production

- Disable the 15-minute status cron (`cron.update` with `enabled: false` for job `4a0de8dd-f061-40f8-acae-a7f68d265fa3`)
- Document in TOOLS.md
- Add to HEARTBEAT.md awareness (so main session knows about it)
- Initialize empty `alert-state.json`: `{ "activeAlerts": {}, "lastCheckTime": null }`

---

## 8. Cost Analysis

| Component | Model | Auth | Cost per Run | Runs per Day | Daily Cost |
|-----------|-------|------|-------------|--------------|------------|
| Health check | Haiku 4.5 | Max Proxy | $0.00 | 48 | **$0.00** |
| Alert delivery | Telegram API | Bot token | $0.00 | ~0-2 | **$0.00** |
| **Total** | | | | | **$0.00/day** |

**Note:** All runs through the Anthropic Max subscription via copilot-proxy. No OpenRouter or per-token costs.

**Comparison with current 15-min cron:** The existing 15-min status update runs 96 times/day doing nothing useful. Replacing it with this 30-min health monitor cuts cron runs in half while adding real monitoring value.

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| False positives (especially from proxy stderr) | Medium | Low | Word-boundary matching + explicit exclusion list (see 4.2.1) |
| Alert fatigue from repeated issues | Medium | Medium | Deduplication via alert-state.json (see 4.4) |
| Root cron stops refreshing logs | Low | Medium | Staleness check built into prompt |
| Haiku misinterprets logs | Low | Low | Simple pattern matching, not semantic analysis |
| Max proxy rate limits Haiku | Low | Low | Gateway fallback chain handles automatically |
| Sub-agent lacks `message` tool | Unknown | Medium | Phase 0 test; fallback to `announce` delivery |
| alert-state.json corruption | Low | Low | Graceful fallback: treat all as new, recreate file |

---

## 10. Open Questions for Steven

1. **Error keyword list:** The refined patterns (see 4.2.1) use word boundaries to avoid the `[Subprocess stderr]` false positive. Should we add: `denied`, `failed`, `crash`? Or keep it narrow for burn-in?

2. **Night mode:** Should the monitor run 24/7, or pause during sleeping hours (e.g., 11 PM - 8 AM)? Alerts at 3 AM aren't useful if you're asleep. Options:
   a. Run 24/7, always alert (simplest)
   b. Run 24/7, suppress Telegram at night (check in morning)
   c. Pause cron at night (miss issues entirely)

3. **15-minute cron replacement:** The current 15-min status cron (job `4a0de8dd`) reports "Idle — no active tasks" every cycle. Recommend disabling it once health monitor is verified. Agree?

4. **Staleness threshold:** Currently set to 15 minutes for log file freshness. The root cron runs every 5 minutes, so 15 min means 3 missed refreshes. Is this the right threshold?

5. **Alert escalation:** Dedup now suppresses duplicates with 2-hour reminders. Should we also escalate differently after, say, 6 hours of the same issue? (e.g., more urgent message, ping via different channel)

6. **Additional checks:** Anything else you want monitored? (e.g., disk I/O, network connectivity, specific process, Tailscale status)

---

## 11. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Root cron (log refresh) | ✅ Active | Refreshes every 5 min |
| OpenClaw cron tool | ✅ Available | Native tool, schema documented in Section 7 |
| Haiku via Max proxy | ✅ Available | Free via subscription |
| Telegram bot | ✅ Active | @openclaw_workshop_bot |
| Log files exist | ✅ Verified | All 3 files present at ~/.openclaw/logs/ |
| Proxy isolation patch | ✅ Applied | Tools route through OpenClaw runtime |
| Sub-agent tool access | ❓ Unverified | Phase 0 test required before Phase 1 |

---

## 12. Critique Response Summary

| # | Critique | Resolution |
|---|----------|------------|
| 1 | Error keyword too broad ("error" matches stderr) | Word-boundary patterns + exclusion list (Section 4.2.1) |
| 2 | journalctl 30-min window gap | Changed to `--since "35 min ago"` for 5-min overlap (Section 4.1) |
| 3 | No deduplication (alert fatigue) | alert-state.json tracking with 2-hour reminder cadence (Section 4.4) |
| 4 | message tool assumption unverified | Phase 0 test job + fallback to announce delivery (Section 7) |
| 5 | Section 7 too vague | Full cron tool JSON config provided (Section 7) |
| 6 | Typo: "Tailscine" | Fixed to "Tailscale" (Section 10, Q6) |

---

## 13. Changelog

| Date | Change |
|------|--------|
| 2026-02-15 (v1) | Initial draft based on Steven's 03:19 AM task prompt spec |
| 2026-02-15 (v2) | Revised per Opus critique: fixed error matching, time window overlap, added deduplication, verified tool access plan, concrete cron config, typo fix |

---

*This document is for review only — no code. Implementation begins after Steven's approval.*
