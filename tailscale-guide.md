# Tailscale VPS Security Guide
**Created:** 2026-02-12  
**For:** Steven's Hawk Host VPS

---

## What is Tailscale?

**Simple explanation:** Creates a private network (like your home WiFi) that connects all your devices securely, no matter where they are physically located.

**Key Benefits:**
- Connect to VPS from anywhere without exposing SSH to public internet
- No need to remember IP addresses (use device names)
- Encrypted tunnel (WireGuard protocol)
- Free for personal use (up to 100 devices)
- Works even if your home IP changes
- Much simpler than traditional VPN setup

---

## How It Works

**Before Tailscale:**
```
Internet → Your VPS (port 22 open to EVERYONE)
          ↑ Constant attacks from bots
```

**After Tailscale:**
```
Your Mac Mini ←→ Tailscale Network ←→ Your VPS
       (private tunnel, encrypted)

Internet → Your VPS port 22 (BLOCKED to public)
          ↑ Bots can't even attempt connection
```

---

## Comparison: IP Restriction vs Tailscale

### IP Restriction (Static Home IP)
✅ **Pros:**
- Simple to set up
- No additional software needed
- Works with existing SSH

❌ **Cons:**
- Only works from home
- Locked out if IP changes (ISP upgrade, modem reset, etc.)
- Can't access from phone/laptop when traveling
- Can't access from other locations

### Tailscale
✅ **Pros:**
- Access from anywhere (home, coffee shop, phone data)
- Works even if home IP changes
- Can add multiple devices (Mac, laptop, phone)
- Free for personal use
- More secure than exposed SSH
- Easy device management via web dashboard

❌ **Cons:**
- Need to install client on each device
- Relies on Tailscale service (though rare outages)
- Slightly more complex initial setup

### Recommended: **Both!**
- Use Tailscale for flexibility and security
- Keep static IP as backup (in case Tailscale ever has issues)

---

## Setup Instructions

### Part 1: Install on VPS (Ubuntu)

**Step 1: Install Tailscale**
```bash
# Install
curl -fsSL https://tailscale.com/install.sh | sh

# Connect to your tailnet
sudo tailscale up

# Click the link that appears, authenticate in browser
# Optional: In Tailscale admin, disable key expiry for this device
```

**Step 2: Name Your Device**
In the Tailscale admin panel (tailscale.com/admin):
- Find your VPS
- Rename it to something memorable: `openclaw-vps`
- Disable key expiry so it doesn't disconnect

**Step 3: Test Connection**
```bash
# Check Tailscale status
sudo tailscale status

# Note the Tailscale IP (100.x.x.x)
```

### Part 2: Install on Mac Mini

**Step 1: Download & Install**
- Go to https://tailscale.com/download
- Download macOS client
- Install and authenticate (same account as VPS)

**Step 2: Test Connection**
```bash
# Ping VPS by Tailscale name
ping openclaw-vps

# SSH via Tailscale
ssh openclaw@openclaw-vps
```

Should work! No public internet involved.

### Part 3: Secure the VPS (Lock Down SSH)

**IMPORTANT:** Only do this AFTER confirming Tailscale SSH works!

**Step 1: Configure UFW Firewall**
```bash
# Enable firewall
sudo ufw enable

# Default policies
sudo ufw default allow outgoing
sudo ufw default deny incoming

# Allow web traffic (for future websites)
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Allow SSH ONLY from Tailscale network
sudo ufw allow in on tailscale0 to any port 22 comment 'SSH via Tailscale'

# Reload firewall
sudo ufw reload
```

**Step 2: Verify Rules**
```bash
sudo ufw status verbose
```

Should show:
- Port 22: ALLOW from tailscale0 only
- Ports 80, 443: ALLOW from anywhere
- Default: DENY incoming

**Step 3: Test Access**

From Mac Mini (via Tailscale): ✅ Should work
```bash
ssh openclaw@openclaw-vps
```

From public internet: ❌ Should fail (timeout)
```bash
ssh openclaw@141.193.23.119
# (This will timeout/be refused)
```

**Step 4: Restart SSH**
```bash
sudo systemctl restart sshd
```

---

## Daily Use

### Connecting to VPS

**Old way (public IP):**
```bash
ssh openclaw@141.193.23.119
```

**New way (Tailscale name):**
```bash
ssh openclaw@openclaw-vps
```

Much cleaner! No need to remember the IP.

### From Your Phone

1. Install Tailscale app (iOS/Android)
2. Authenticate
3. Install a terminal app (like Termius)
4. SSH to `openclaw-vps`

Now you can manage your VPS from anywhere!

---

## Security Benefits

### What You Just Eliminated

**Before:**
- 1000s of daily SSH brute-force attempts
- Exposed to every bot scanning the internet
- Password/key compromise risk from attacks
- Server resources wasted handling attacks

**After:**
- Port 22 not visible to public internet
- Only your Tailscale devices can even attempt connection
- Bots can't reach SSH at all
- Cleaner logs, less noise

### UFW Logs Will Show

Before Tailscale: Pages of blocked SSH attempts  
After Tailscale: Blocked web scans only (normal)

---

## Backup Access Plan

**"What if Tailscale stops working?"**

### Option 1: Keep Static IP as Fallback

Add your home IP as backup:
```bash
# Get your current public IP
curl ifconfig.me

# Add it as backup SSH access
sudo ufw allow from YOUR_HOME_IP to any port 22 comment 'Backup SSH from home'
```

### Option 2: Hawk Host Console Access

- Login to https://my.hawkhost.com
- Access VPS console (KVM)
- Fix Tailscale from there

### Option 3: Phone via Tailscale

- Keep Tailscale installed on your phone
- If Mac mini dies, use phone to access VPS
- Install Termius or similar SSH app

---

## Advanced: Tailscale SSH (Optional)

Tailscale has its own SSH feature that replaces traditional SSH entirely:

**Benefits:**
- No SSH keys to manage
- Uses Tailscale auth
- Can record sessions (audit trail)
- ACL-based access control

**Setup:**
```bash
# Enable Tailscale SSH on VPS
sudo tailscale up --ssh

# Now connect without user@
ssh openclaw-vps
```

**Recommendation:** Start with regular SSH over Tailscale first, explore Tailscale SSH later.

---

## Cost

**Tailscale Personal Plan:**
- ✅ Free forever
- Up to 100 devices
- 3 users
- Unlimited network usage

**Perfect for your use case!**

---

## Troubleshooting

### Can't Connect via Tailscale

**Check Tailscale status on VPS:**
```bash
sudo tailscale status
# Should show "Connected"
```

**Check Mac Mini Tailscale:**
```bash
tailscale status
# Should show openclaw-vps in the list
```

**Restart Tailscale:**
```bash
# VPS
sudo systemctl restart tailscaled

# Mac Mini
# Just quit and reopen the Tailscale app
```

### Locked Out Completely

**Use Hawk Host console:**
1. Login to https://my.hawkhost.com
2. Find your VPS
3. Open console/KVM access
4. Login directly
5. Fix UFW rules:
```bash
sudo ufw allow 22/tcp
sudo ufw reload
```

---

## Recommended Setup Timeline

**Tonight (15 minutes):**
1. ⬜ Create Tailscale account (free)
2. ⬜ Install on Mac Mini
3. ⬜ Install on VPS
4. ⬜ Test SSH connection via Tailscale

**After Testing (10 minutes):**
1. ⬜ Configure UFW to allow Tailscale only
2. ⬜ Add home IP as backup
3. ⬜ Test both Tailscale and backup access
4. ⬜ Reload UFW and restart SSH

**Optional (Later):**
1. ⬜ Install Tailscale on phone
2. ⬜ Set up SSH app on phone
3. ⬜ Explore Tailscale SSH feature

---

## Questions for Steven

1. **Want to try Tailscale tonight?** (I can walk you through each step)
2. **Do you want to keep home IP as backup?** (recommended: yes)
3. **Any other devices to add?** (laptop, iPad, phone?)

---

## Summary: Why This is Better

**Current Security (No Firewall):**
- SSH exposed to entire internet
- Constant brute-force attempts
- Relying only on key auth for protection
- Resource drain from attacks

**With Tailscale + UFW:**
- SSH only accessible via private network
- Bots can't even attempt connection
- Access from anywhere (not just home)
- Cleaner logs, better security
- Free!

**Bottom line:** This is how most security-conscious developers run their VPS servers. It's the modern standard.

---

**STATUS: Ready for review and implementation**
