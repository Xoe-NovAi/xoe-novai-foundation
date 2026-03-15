---
title: "Omega-Stack Decision Trees"
version: "1.0"
date: "2026-03-13"
purpose: "Diagnostic flowcharts for cloud Claude remote troubleshooting"
organization: "Xoe-NovAi Foundation (XNA)"
---

# Omega-Stack Decision Trees
## Diagnostic and Implementation Flowcharts for Cloud Claude

---

## TREE 1: Permission Denied Error (EACCES)

```
SYMPTOM: "Permission denied" on .gemini operations
         Error: EACCES: permission denied, access '.gemini'

┌─────────────────────────────────────────┐
│ STEP 1: Identify Current State           │
└─────────────────────────────────────────┘
         │
         ├─ Ask user: ls -la ~/.gemini | head -3
         │
         └─→ Look at ownership column (3rd and 4th columns)
                │
                ├─ Shows "arcana-novai arcana-novai" (1000:1000)?
                │  YES → STEP 2
                │  NO → Check UID (should be "1000" not "100999")
                │       └─→ Run Layer 1 Emergency Restore
                │           then return to STEP 2
                │
                └─ (If ownership unclear, ask: stat ~/.gemini)

┌─────────────────────────────────────────┐
│ STEP 2: Check ACL Status                 │
└─────────────────────────────────────────┘
         │
         ├─ Ask user: getfacl ~/.gemini | head -20
         │
         ├─ Look for lines with "user:1000:rwx"
         │  Found? → STEP 3
         │  Not found? → Permission issue!
         │              └─→ Run Layer 2 Fix (Default ACLs)

┌─────────────────────────────────────────┐
│ STEP 3: Test Direct Access               │
└─────────────────────────────────────────┘
         │
         ├─ Ask user: test -r ~/.gemini && echo "✓ Readable" || echo "✗ Not"
         ├─           test -w ~/.gemini && echo "✓ Writable" || echo "✗ Not"
         ├─           test -x ~/.gemini && echo "✓ Executable" || echo "✗ Not"
         │
         ├─ All three are "✓"?
         │  YES → Permission issue resolved!
         │        └─→ Test actual operation (e.g., ls ~/.gemini/.settings.json)
         │  NO → Some permission missing
         │       └─→ Problem identified, proceed to FIX

┌─────────────────────────────────────────┐
│ FIX: Choose Based on Root Cause          │
└─────────────────────────────────────────┘
         │
         ├─ Ownership wrong (100999 not 1000)?
         │  └─→ Run Layer 1 Emergency Restore (chown)
         │      Then verify: ls -la ~/.gemini
         │
         ├─ ACLs missing (no user:1000 or user:100999)?
         │  └─→ Run Layer 2 Fix (Default ACLs)
         │      Then verify: getfacl ~/.gemini | grep user:1000
         │
         ├─ ACLs present but still denied?
         │  └─→ Layer 4 Self-Healing timer broken
         │      Run: systemctl --user restart acl-monitor.timer
         │      Then verify: journalctl --user -u acl-monitor.service
         │
         └─ Still failing after all fixes?
            └─→ Escalate: Provide full diagnostic output to Archon
```

---

## TREE 2: Service Won't Start or Stay Running

```
SYMPTOM: Service fails to start, crashes, or won't restart
         Error varies: OOM, segfault, connection refused, config error

┌──────────────────────────────────────────────┐
│ STEP 1: Check Service Status                  │
└──────────────────────────────────────────────┘
         │
         ├─ Ask user: systemctl --user status SERVICE_NAME
         │
         ├─ Status output shows:
         │  ├─ "active (running)" → Service is healthy, problem elsewhere
         │  ├─ "inactive (dead)" → Service crashed or stopped
         │  ├─ "failed" → Service failed, needs debugging
         │  ├─ "activating" → Service still starting (wait 30 sec)
         │  └─ "timeout" → Service took too long to start

┌──────────────────────────────────────────────┐
│ STEP 2: Check Service Logs                    │
└──────────────────────────────────────────────┘
         │
         ├─ Ask user: journalctl --user -u SERVICE_NAME -n 100 --no-pager
         │
         ├─ Look for error message in last 100 lines:
         │  ├─ "Out of memory" or "Killed" → OOM issue (IMPL-02 §4)
         │  ├─ "Address already in use" → Port conflict
         │  ├─ "Connection refused" → Dependency not running
         │  ├─ "Configuration error" or "YAML" → Config issue
         │  ├─ "Segmentation fault" → Service bug, needs restart
         │  └─ Other error → Analyze error message

┌──────────────────────────────────────────────┐
│ STEP 3: Check Resource Availability           │
└──────────────────────────────────────────────┘
         │
         ├─ Ask user: free -h && echo "---" && df -h && echo "---" && podman stats --no-stream
         │
         ├─ Check:
         │  ├─ Disk space: Is "/" < 10% free?
         │  │  YES → CRISIS, free space immediately (IMPL-01 §4)
         │  │  NO → Proceed
         │  │
         │  ├─ Memory: Is "available" < 500MB?
         │  │  YES → High memory pressure (IMPL-02 §4)
         │  │  NO → Proceed
         │  │
         │  └─ Service memory: Is SERVICE using > 1GB?
         │     YES → Memory limit too high, reduce it
         │     NO → Proceed

┌──────────────────────────────────────────────┐
│ FIX: Choose Based on Root Cause               │
└──────────────────────────────────────────────┘
         │
         ├─ Out of memory (OOM)?
         │  └─→ IMPL-02 §4: Reduce memory limit, stop competing services
         │      Example: If qdrant using 1.5GB, reduce limit to 1GB
         │
         ├─ Port already in use?
         │  └─→ Ask: netstat -tuln | grep :PORT_NUMBER
         │      Kill competing process or change service port
         │      Then restart: systemctl --user restart SERVICE_NAME
         │
         ├─ Connection refused (dependency)?
         │  └─→ Check if dependency is running:
         │      systemctl --user is-active DEPENDENCY
         │      If not, start it first, then restart main service
         │
         ├─ Configuration error (YAML/JSON)?
         │  └─→ Ask user to review config file for syntax:
         │      cat ~/.config/containers/systemd/SERVICE.container
         │      Check for: unclosed brackets, wrong indentation, typos
         │      Fix and run: systemctl --user daemon-reload
         │      Then restart: systemctl --user restart SERVICE_NAME
         │
         ├─ Segmentation fault?
         │  └─→ Container image issue, try:
         │      1. Stop service: systemctl --user stop SERVICE_NAME
         │      2. Pull fresh image: podman pull image:tag
         │      3. Remove old: podman rmi old-image:old-tag
         │      4. Restart: systemctl --user start SERVICE_NAME
         │
         └─ Still failing?
            └─→ Provide full logs to Archon for investigation
```

---

## TREE 3: Storage/Disk Space Crisis

```
SYMPTOM: "No space left on device"
         Root filesystem 90%+ full
         Writes failing, services crashing

┌─────────────────────────────────────────┐
│ STEP 1: Verify Crisis Level              │
└─────────────────────────────────────────┘
         │
         ├─ Ask user: df -h | grep "/$"
         │
         ├─ Output analysis:
         │  ├─ 95%+ full → CRITICAL, immediate action needed
         │  ├─ 90-95% full → URGENT, action required within 1 hour
         │  └─ 80-90% full → HIGH, action needed within 24 hours

┌─────────────────────────────────────────┐
│ STEP 2: Find Space Hogs                  │
└─────────────────────────────────────────┘
         │
         ├─ Ask user: du -sh /* | sort -hr | head -10
         │
         ├─ Identify largest directories:
         │  ├─ /home (user data) — largest?
         │  ├─ /var (logs, cache) — large?
         │  ├─ /usr (system) — shouldn't grow much
         │  └─ Others?

┌─────────────────────────────────────────┐
│ STEP 3: Analyze Safe Deletions            │
└─────────────────────────────────────────┘
         │
         ├─ If /home is large:
         │  └─→ Ask: du -sh /home/* | sort -hr
         │      Then for each: du -sh /home/USER/* | sort -hr
         │      Look for: Downloads/, Documents/, cache
         │
         ├─ If /var is large:
         │  └─→ Ask: du -sh /var/* | sort -hr
         │      Common culprits:
         │      ├─ /var/log/ — Old logs (can truncate)
         │      ├─ /var/cache/ — Apt cache (safe to clean)
         │      └─ /var/tmp/ — Temp files (safe to delete)
         │
         └─ If other — investigate specifically

┌─────────────────────────────────────────┐
│ FIX: Safe Cleanup Sequence                │
└─────────────────────────────────────────┘
         │
         ├─ STEP 1: Remove Podman cruft (safest first)
         │  └─→ podman system prune -a --force
         │      Removes: unused images, containers, networks
         │      Freed: typically 2-5 GB
         │      Then verify: df -h | grep "/$"
         │
         ├─ STEP 2: Clean apt cache (very safe)
         │  └─→ sudo apt clean
         │      Removes: old .deb files
         │      Freed: typically 500MB-2GB
         │      Then verify: df -h | grep "/$"
         │
         ├─ STEP 3: Clean logs (safe if >30 days)
         │  └─→ sudo journalctl --vacuum-time=30d
         │      Removes: old systemd journal entries
         │      Freed: depends on usage, typically 1-5 GB
         │      Then verify: df -h | grep "/$"
         │
         ├─ STEP 4: Remove old downloads (if present, >30 days)
         │  └─→ find ~/Downloads -mtime +30 -delete
         │      Removes: archives older than 30 days
         │      Freed: depends on contents
         │      Then verify: df -h | grep "/$"
         │
         └─ STEP 5: If still not enough
            └─→ Analyze remaining space carefully
                Ask: du -sh ~/* | sort -hr
                Only delete with explicit user confirmation

┌─────────────────────────────────────────┐
│ VERIFICATION                              │
└─────────────────────────────────────────┘
         │
         ├─ After cleanup, ask user: df -h | grep "/$"
         │
         ├─ Success criteria:
         │  ├─ Free space > 20 GB (for Phase 1)
         │  ├─ Usage < 80%
         │  └─ Root FS stable (not growing further)
         │
         └─ If still critical → Escalate to Archon
```

---

## TREE 4: Memory Pressure / OOM Events

```
SYMPTOM: System slow, services crash randomly
         OOM killer active ("Killed" in logs)
         Swap usage high

┌──────────────────────────────────────────┐
│ STEP 1: Check Memory Pressure             │
└──────────────────────────────────────────┘
         │
         ├─ Ask user: free -h
         │
         ├─ Analyze output:
         │  ├─ Available < 500MB → HIGH pressure
         │  ├─ Swap in use > 2GB → Serious OOM risk
         │  └─ Swap in use > 5GB → CRITICAL
         │
         └─ If serious, proceed to FIX immediately

┌──────────────────────────────────────────┐
│ STEP 2: Identify Memory Hogs               │
└──────────────────────────────────────────┘
         │
         ├─ Ask user: podman stats --no-stream
         │
         ├─ Look for services using > 500MB:
         │  ├─ qdrant (vector DB) — often 800MB-1GB
         │  ├─ crawl4ai (browser) — often 600MB-1GB
         │  ├─ postgres (database) — often 400MB-600MB
         │  └─ Others?

┌──────────────────────────────────────────┐
│ FIX: Reduce Memory Pressure                │
└──────────────────────────────────────────┘
         │
         ├─ IMMEDIATE: Stop lowest-priority service
         │  └─→ systemctl --user stop lowest-priority-service
         │      Free ~500MB-1GB immediately
         │      Verify: free -h
         │
         ├─ SHORT-TERM: Reduce limits on high-memory services
         │  └─→ Edit ~/.config/containers/systemd/SERVICE.container
         │      Change: Memory=1G → Memory=512M (or appropriate)
         │      Reload: systemctl --user daemon-reload
         │      Restart: systemctl --user restart SERVICE
         │      Verify: podman stats SERVICE --no-stream
         │
         ├─ Monitor: Ensure Swap usage drops
         │  └─→ Wait 5 minutes, then: free -h
         │      Swap should decrease as services use less
         │
         └─ If still critical: Stop additional services until stable
```

---

## TREE 5: Plaintext Secret Found

```
SYMPTOM: Found password in .env file
         Audit reveals plaintext credentials
         Security compliance issue

┌──────────────────────────────────────────┐
│ STEP 1: Assess Exposure Risk              │
└──────────────────────────────────────────┘
         │
         ├─ Is the file committed to git?
         │  ├─ YES → HIGH risk (visible in git history)
         │  └─ NO → MEDIUM risk (visible on filesystem)
         │
         ├─ Is the file world-readable?
         │  └─→ ls -la .env | awk '{print $1}'
         │      ├─ Starts with "-rw-------" → Restricted (lower risk)
         │      └─ Other (e.g., "-rw-r--r--") → Exposed (higher risk)

┌──────────────────────────────────────────┐
│ STEP 2: Immediately Rotate Credential      │
└──────────────────────────────────────────┘
         │
         ├─ Generate new secure password:
         │  └─→ openssl rand -base64 32
         │
         ├─ Update the service:
         │  ├─ For qdrant: Update admin password via API
         │  ├─ For minio: Update root user via API
         │  ├─ For postgres: Update via SQL ALTER USER
         │  ├─ For redis: Update requirepass via CONFIG
         │  └─ For rabbitmq: Update via API
         │
         ├─ Update .env file:
         │  └─→ sed -i 's/OLD_PASSWORD/NEW_PASSWORD/g' .env
         │      (Or manually edit for safety)
         │
         └─ Restart service:
            └─→ systemctl --user restart SERVICE_NAME

┌──────────────────────────────────────────┐
│ STEP 3: Encrypt for Long-Term              │
└──────────────────────────────────────────┘
         │
         ├─ Install SOPS (if needed):
         │  └─→ sudo apt-get install sops
         │
         ├─ Create age encryption key:
         │  └─→ age-keygen -o ~/.sops/age.key
         │
         ├─ Encrypt .env:
         │  └─→ sops -e .env > .env.enc
         │
         ├─ Remove plaintext:
         │  └─→ rm .env  (or mv to archive)
         │
         └─ Update git:
            └─→ git rm .env
                git add .env.enc
                git commit -m "Encrypt secrets with SOPS"

┌──────────────────────────────────────────┐
│ STEP 4: Audit Trail                       │
└──────────────────────────────────────────┘
         │
         ├─ Log the rotation:
         │  └─→ echo "SERVICE: rotated password on 2026-03-13" >> ~/.omega/secret-audit.log
         │
         └─ Verify no plaintext remains:
            └─→ grep -r "password\|PASSWORD" .env ~/Documents/Xoe-NovAi/ | grep -v "^#"
                Should return: ZERO results
```

---

## TREE 6: Service Health Check Baseline

```
SYMPTOM: General health check needed
         Routine maintenance
         Verification after changes

┌──────────────────────────────────────────┐
│ STEP 1: System Health                     │
└──────────────────────────────────────────┘
         │
         ├─ Ask user: Run health check script
         │  └─→ bash ~/Documents/Xoe-NovAi/omega-stack/scripts/monitoring/omega_health.sh
         │
         └─ Review output for any RED or YELLOW indicators

┌──────────────────────────────────────────┐
│ STEP 2: Service Status Summary             │
└──────────────────────────────────────────┘
         │
         ├─ Ask user: systemctl list-units --type=service | grep omega
         │
         ├─ Expected: All services show "active" and "running"
         │  ├─ If any "failed" → Investigate that service
         │  ├─ If any "inactive" → Start it or check if intentional
         │  └─ If all "active" → Continue

┌──────────────────────────────────────────┐
│ STEP 3: Container Status                  │
└──────────────────────────────────────────┘
         │
         ├─ Ask user: podman ps --format "table {{.Names}}\t{{.Status}}"
         │
         ├─ Expected: All containers show "Up" with uptime
         │  ├─ If "Exited" → Container crashed, check logs
         │  ├─ If "Restarting" → Rapid restart, investigate
         │  └─ If all "Up" → Continue

┌──────────────────────────────────────────┐
│ STEP 4: Resource Status                   │
└──────────────────────────────────────────┘
         │
         ├─ Ask user: free -h && echo "---" && df -h && echo "---" && podman stats --no-stream
         │
         ├─ Check:
         │  ├─ Disk: Root FS should be <80%
         │  ├─ Memory: Available should be >500MB
         │  ├─ Swap: Should be <1.5GB in use
         │  └─ Service memory: No single service >1GB
         │
         └─ If all green → Health check PASSED

┌──────────────────────────────────────────┐
│ STEP 5: Security Status                   │
└──────────────────────────────────────────┘
         │
         ├─ Ask user: grep -r "password\|PASSWORD" ~/.env ~/.gemini/ | grep -v "^#"
         │
         ├─ Expected: ZERO plaintext secrets found
         │  ├─ If any found → Escalate to Sonnet for remediation
         │  └─ If none → Continue
         │
         └─ Ask: aa-status | grep apparmor
            Expected: "apparmor module is loaded"
```

---

## Quick Navigation

| Problem | Decision Tree | Location |
|---------|---------------|----------|
| Permission denied (EACCES) | Tree 1 | Above |
| Service won't start | Tree 2 | Above |
| Disk space full | Tree 3 | Above |
| Memory pressure / OOM | Tree 4 | Above |
| Plaintext secret found | Tree 5 | Above |
| Routine health check | Tree 6 | Above |

---

**Usage**: When troubleshooting, follow the appropriate tree from start to finish. Provide diagnostic output at each "Ask user" step.

