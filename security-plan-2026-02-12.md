# VPS Security Remediation Plan
**Date:** 2026-02-12  
**Target Profile:** VPS Hardened  
**System:** Ubuntu 22.04.5 LTS (Hawk Host)

---

## Current Posture Summary

### ✅ Good
- OpenClaw gateway: loopback-only (127.0.0.1:18789)
- Non-root user with sudo (openclaw)
- Automatic security updates enabled
- OpenClaw security: 0 critical issues

### ⚠️ Needs Attention
- **No firewall configured** - all ports exposed
- **SSH open to public internet** (port 22) - no IP restriction
- **OpenClaw update available** (npm 2026.2.9)
- **No backup system verified**
- **No disk encryption** (typical for VPS, acceptable)

---

## Gaps vs VPS Hardened Target

| Area | Current | Target | Priority |
|------|---------|--------|----------|
| Firewall | None | UFW deny-by-default | HIGH |
| SSH Access | Public | IP-restricted OR key-only | HIGH |
| Backups | Unknown | Verified system | MEDIUM |
| OpenClaw | 2026.2.x | Latest stable | LOW |
| Fail2ban | Not checked | SSH brute-force protection | MEDIUM |

---

## Remediation Steps

### Step 1: Install and Configure UFW Firewall
**Impact:** Blocks all inbound except SSH and services you approve  
**Rollback:** `sudo ufw disable`

```bash
# Install UFW
sudo apt update && sudo apt install -y ufw

# Default policies: deny incoming, allow outgoing
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (your current connection)
sudo ufw allow 22/tcp comment 'SSH access'

# Enable firewall
sudo ufw enable
```

**Risk:** If SSH is blocked, you'd lose access. We'll test first.

---

### Step 2: Restrict SSH Access (Choose One)

#### Option A: IP Restriction (Your Static Home IP)
**Pros:** Simple, effective if IP doesn't change  
**Cons:** Locked out if IP changes or traveling

```bash
# Replace with your actual static IP
sudo ufw delete allow 22/tcp
sudo ufw allow from YOUR_STATIC_IP to any port 22 comment 'SSH from home'
```

#### Option B: SSH Key-Only + Disable Password Auth
**Pros:** More secure, works from anywhere  
**Cons:** Need to set up keys first

```bash
# 1. First, ensure you have SSH key on Mac mini
# 2. Copy key to VPS (run from Mac):
ssh-copy-id openclaw@141.193.23.119

# 3. Then on VPS, disable password auth:
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

#### Option C: Both (Most Secure)
IP restriction + key-only auth

**Your call - which do you prefer?**

---

### Step 3: Install Fail2ban (SSH Brute-Force Protection)
**Impact:** Auto-bans IPs after failed login attempts  
**Rollback:** `sudo systemctl stop fail2ban`

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

### Step 4: OpenClaw Fixes

#### 4a: Fix Trusted Proxies Warning
Since gateway is loopback-only and you're not using a reverse proxy yet:

```bash
openclaw security audit --fix
```

#### 4b: Update OpenClaw (Optional)
```bash
cd /home/openclaw/.npm-global/lib/node_modules/openclaw
pnpm update
openclaw gateway restart
```

---

### Step 5: Future Ports (When Websites/Ghost Set Up)

When you add websites/Ghost blogs, we'll need:

```bash
# HTTP
sudo ufw allow 80/tcp comment 'HTTP web traffic'

# HTTPS
sudo ufw allow 443/tcp comment 'HTTPS web traffic'
```

**Not doing this now** - only when services are ready.

---

## Access Preservation Strategy

1. **Always test firewall rules before enabling**
2. **Keep current SSH session open** while testing
3. **Open second SSH connection** to verify before closing first
4. **If locked out:** Use Hawk Host console/KVM access

---

## Recommended Execution Order

**Which approach do you prefer?**

1. **Guided Step-by-Step** - I walk you through each command, you approve
2. **Show Full Script** - Review everything first, then execute
3. **Critical Only** - Just firewall + SSH hardening, skip optional items
4. **Export for Later** - Give you the commands to run manually

**Also decide:** SSH restriction method (IP-only, key-only, or both)?

---

## Post-Remediation Verification

After changes, I'll re-run:
- `sudo ufw status verbose`
- `ss -ltnp` (check listening ports)
- `openclaw security audit --deep`
- Test SSH from Mac mini

---

## Backup Plan (Separate Task)
- Research Hawk Host snapshot/backup options
- Set up automated backups to Mac mini (rsync/borgbackup)
- Document backup restoration procedure

---

**Ready to proceed? Pick your execution method and SSH restriction preference!**
