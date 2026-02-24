# VPS Backup System

## Overview
Weekly automated backup of the entire VPS (`digital-workshop`, 141.193.23.119) to the Mac over Tailscale. Captures everything needed to rebuild the VPS from a fresh Ubuntu 22.04 install.

- **Schedule:** Every Monday at 4:00 AM (Mac crontab)
- **Retention:** Last 4 weekly backups
- **Size:** ~360MB per snapshot
- **Duration:** ~2 minutes over Tailscale
- **Script:** `~/bin/backup-vps.sh`
- **Destination:** `~/vps-backups/YYYY-MM-DD/`
- **Log:** `~/vps-backups/backup.log`

## What's Backed Up

| Directory | Source on VPS | Contents |
|-----------|--------------|----------|
| `openclaw-home/` | `/home/openclaw/` | Full home dir (excludes .npm, .cache, node_modules, session .jsonl files) |
| `etc/` | `/etc/` | All system configs — sshd, cron.d, network, hostname, sudoers, etc. |
| `root-home/` | `/root/` | Root's home — .bashrc, .ssh, scripts |
| `srv/` | `/srv/` | Shared file exchange folder |
| `usr-local/` | `/usr/local/` | Manually installed binaries |
| `crontabs/` | `/var/spool/cron/` | All user crontabs (root + openclaw) |
| `systemd/system/` | `/etc/systemd/system/` | System-level service files |
| `systemd/user/` | `~openclaw/.config/systemd/user/` | User services (gateway, proxy) |
| `tailscale/` | various | Auth state, status JSON, defaults |
| `firewall/` | runtime | iptables rules, ufw status |
| `manifests/` | runtime | Package lists |
| `REBUILD.md` | generated | Step-by-step rebuild instructions |

### Excluded
- Session logs (`*.jsonl`) — transient
- npm/pip cache — reinstallable
- node_modules — reinstallable

## VPS-Side Config Backup (Separate)
- **Script:** `/home/openclaw/bin/openclaw-backup.sh`
- **Scope:** 6 critical config files only
- **Location:** `~/.openclaw/backups/YYYYMMDD-HHMMSS/`
- **Retention:** Last 10 snapshots
- **Not on cron** — manual, for quick rollbacks before risky changes

## Monitoring
```bash
# Check for failures
grep FAILED ~/vps-backups/backup.log
# Check backup age (should be < 7 days)
ls -lt ~/vps-backups/ | head -5
```
