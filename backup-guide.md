# VPS Backup Strategy Guide
**Created:** 2026-02-12  
**For:** Steven's Hawk Host VPS

---

## Part 1: Hawk Host Snapshot Backups

### What Hawk Host Offers

**For Shared Hosting (NOT your VPS):**
- Acronis backup with 7-day rolling snapshots
- Accessible via cPanel
- Includes files, emails, databases
- **This does NOT apply to VPS services**

**For VPS (Cloud Compute):**
- **Optional paid snapshot add-on**
- Available for Los Angeles USA and Hong Kong locations
- Full compute snapshot (entire VPS state)
- NOT incremental - full system restore point
- Purchase through client area upgrade/downgrade

### How to Enable VPS Snapshots

1. Login to https://my.hawkhost.com/clientarea.php
2. Navigate: Services → My Services
3. Click the green "Active" button next to your VPS
4. Select "Upgrade/Downgrade Options" from left menu
5. Add snapshot backup option

### Pricing
**STATUS: Need to check your client area for exact pricing**
- Varies by VPS plan and snapshot frequency
- Typically $2-10/month depending on VPS size
- Check: https://my.hawkhost.com/clientarea.php

### Limitations
- Snapshots are full system images (no individual file restore)
- Restore = revert entire VPS to snapshot date
- Not suitable for granular file recovery
- Best as "disaster recovery" option

### Recommendation
**Good for:** Complete system failure, ransomware recovery, major mistakes  
**Not good for:** "Oops I deleted one file" scenarios  
**Verdict:** Worth having as insurance ($2-5/mo) + use Mac Mini for files

---

## Part 2: Mac Mini Backup Strategy

### Why Mac Mini Backups?

**Advantages:**
- Full control over what/when/how
- Granular file recovery
- No monthly fees
- Can backup specific directories
- Automated via cron
- Good for incremental backups

**Best Use:**
- Important files/documents
- Website content (/var/www/)
- Ghost blog content
- Configuration files
- Database dumps
- User home directory

### Option A: rsync (Simple, Efficient)

**What it does:** Copies only changed files over SSH

**Setup on Mac Mini:**

```bash
# Create backup directory
mkdir -p ~/vps-backups/openclaw-workspace

# Test backup (dry-run)
rsync -avz --dry-run openclaw@141.193.23.119:/home/openclaw/.openclaw/workspace/ ~/vps-backups/openclaw-workspace/

# Real backup
rsync -avz openclaw@141.193.23.119:/home/openclaw/.openclaw/workspace/ ~/vps-backups/openclaw-workspace/

# Add more directories as needed
rsync -avz openclaw@141.193.23.119:/var/www/ ~/vps-backups/websites/
```

**Automated Daily Backup Script:**

Save as `~/bin/backup-vps.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
LOG=~/vps-backups/logs/backup-$DATE.log

echo "Starting VPS backup at $(date)" > $LOG

# Workspace
rsync -avz openclaw@141.193.23.119:/home/openclaw/.openclaw/workspace/ \
    ~/vps-backups/openclaw-workspace/ >> $LOG 2>&1

# Future: websites when set up
# rsync -avz openclaw@141.193.23.119:/var/www/ \
#     ~/vps-backups/websites/ >> $LOG 2>&1

echo "Backup completed at $(date)" >> $LOG

# Keep logs for 30 days
find ~/vps-backups/logs/ -name "backup-*.log" -mtime +30 -delete
```

Make executable: `chmod +x ~/bin/backup-vps.sh`

**Schedule with cron (Mac Mini):**
```bash
# Edit crontab
crontab -e

# Add line (backup daily at 3 AM):
0 3 * * * /Users/steven/bin/backup-vps.sh
```

### Option B: borgbackup (Advanced, Deduplication)

**What it does:** Encrypted, deduplicated, compressed backups

**Advantages:**
- Space efficient (only stores changed data)
- Built-in encryption
- Can restore from specific dates
- Compression saves space

**Setup (more complex, recommend starting with rsync first)**

Will document if you want this option.

---

## Part 3: Database Backup Strategy

**When you have Ghost/MySQL running:**

### Automated DB Dumps on VPS

Create `/home/openclaw/bin/backup-databases.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d-%H%M)
BACKUP_DIR=/home/openclaw/backups/databases

mkdir -p $BACKUP_DIR

# Dump all databases (when MySQL is set up)
# mysqldump --all-databases > $BACKUP_DIR/all-databases-$DATE.sql
# gzip $BACKUP_DIR/all-databases-$DATE.sql

# Keep last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

Then Mac Mini rsync pulls these dumps daily.

---

## Part 4: Recommended Combined Strategy

### Tier 1: Hawk Host Snapshots (Monthly)
- Enable basic snapshot backup ($2-5/mo)
- Frequency: Weekly or bi-weekly
- **Purpose:** Disaster recovery only

### Tier 2: Mac Mini Daily Backups (Free)
- rsync workspace daily (automated)
- rsync websites daily (when set up)
- Pull database dumps daily
- **Purpose:** Day-to-day recovery, file restoration

### Tier 3: Critical Config Tracking (Git)
- Keep important configs in git repo
- Push to GitHub/private repo
- **Purpose:** Version control, easy restore

---

## Recovery Procedures

### Scenario 1: Deleted a File
1. SSH to Mac Mini
2. Browse ~/vps-backups/openclaw-workspace/
3. Copy file back to VPS via scp/rsync

### Scenario 2: Broke a Configuration
1. Check git history first
2. Or restore from Mac Mini backup
3. rsync specific config file back

### Scenario 3: Complete VPS Failure
1. Restore from Hawk Host snapshot (if available)
2. OR rebuild VPS from scratch
3. Restore files from Mac Mini backup
4. Restore databases from dumps

---

## Action Items for Tonight

**Immediate (No Cost):**
1. ⬜ Create backup script on Mac Mini
2. ⬜ Test manual rsync backup
3. ⬜ Set up cron job for daily backups
4. ⬜ Create backup log directory

**Optional (Small Cost):**
1. ⬜ Check Hawk Host snapshot pricing in client area
2. ⬜ Enable if $5/mo or less

**Future (When websites live):**
1. ⬜ Add /var/www to rsync script
2. ⬜ Set up database dump automation
3. ⬜ Test full restore procedure

---

## Questions for Steven

1. **SSH keys set up on Mac Mini?** (needed for automated backups)
2. **How much disk space available on Mac Mini?** (to plan retention)
3. **Hawk Host snapshot pricing in your client area?**
4. **Want me to create the backup script for you?** (I can prep it for review)

---

**STATUS: Draft complete, ready for review**
