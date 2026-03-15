---
title: "Sonnet Manual Enhancement Report"
version: "1.0"
date: "2026-03-13"
purpose: "Deliverable for Sonnet to enhance existing manuals based on cloud Claude testing"
status: "Ready for Implementation"
from: "Cloud Claude (via Haiku analysis) → Sonnet"
organization: "Xoe-NovAi Foundation (XNA)"
---

# Sonnet Manual Enhancement Report
## Omega-Stack Implementation Manual Improvements

**For**: Claude Sonnet (other session)  
**From**: Cloud Claude analysis + Copilot Haiku review  
**Status**: Ready for implementation  
**Estimated effort**: 2-3 hours  
**Impact**: Substantial improvements in field applicability and clarity  

---

## EXECUTIVE SUMMARY

Haiku's analysis of the current implementation manuals (created by Sonnet) and testing against actual Omega-Stack requirements has identified **7 critical enhancement opportunities** across 6 manuals. These are not issues with Sonnet's work, but natural refinements based on practical cloud Claude testing.

### High-Priority Updates (Do These First)
1. **IMPL-07** — Explicit UID specifications in ACL commands
2. **IMPL-02** — Memory management and OOM prevention section
3. **SUPP-02** — Emergency plaintext secret remediation procedures
4. **IMPL-01** — Disk space emergency procedures

### Medium-Priority Updates (Next)
1. **IMPL-02** — Quadlet migration step-by-step guide
2. **ARCH-02** — Facet unavailability and circuit breaker patterns
3. **IMPL-01** — Long-term storage reorganization strategy

---

## ENHANCEMENT #1: IMPL-07 (Permissions 4-Layer Model)

### Location: §2 (Layer 2 — POSIX Default ACLs)

### Current Gap
The current section explains the concept but doesn't specify exactly which UIDs to grant. Field testing showed that unclear UID specifications led to Haiku having to infer the correct approach.

### Proposed Enhancement

**Section to Update**: IMPL-07 §2.3 (Default ACL Implementation)

**Current Text** (approximate):
```
Grant appropriate file permissions via setfacl -m on key directories
to bridge the UID 1000 / UID 100999 gap...
```

**Proposed Replacement**:
```
Layer 2 — POSIX Default ACLs: Permanent Bridge Between UIDs

The 4-Layer model's permanent fix uses POSIX Default ACLs to grant 
rwx permissions to BOTH the host user (UID 1000) and the Podman 
rootless app user (UID 100999).

CRITICAL: Apply to all 3 user contexts:

1. Host User Context (UID 1000):
   setfacl -R -m u:1000:rwx ~/.gemini
   → Grants host user read-write-execute

2. Podman App User Context (UID 100999):
   setfacl -R -m u:100999:rwx ~/.gemini
   → Grants Podman rootless user read-write-execute

3. Default ACL (inherited by new files):
   setfacl -R -d -m u:1000:rwx ~/.gemini
   setfacl -R -d -m u:100999:rwx ~/.gemini
   → Ensures new files inherit both UID contexts

Verification Command:
  getfacl ~/.gemini | head -20
  
Expected Output Includes:
  user::rwx
  user:1000:rwx
  user:100999:rwx
  default:user:1000:rwx
  default:user:100999:rwx

Why Both UIDs?
  - Container writes create files as UID 100999
  - Host user (UID 1000) needs to read/write those files
  - Default ACLs ensure new files inherit both grants
  - Layer 3 (--userns=keep-id) prevents UID drift
  - Layer 4 (systemd timer) repairs broken ACLs
```

### Testing Recommendation
Include in IMPL-09 (Verification Suite) a test case:
```bash
test_acl_both_uids() {
  getfacl ~/.gemini | grep -q "user:1000:rwx" || return 1
  getfacl ~/.gemini | grep -q "user:100999:rwx" || return 1
  getfacl ~/.gemini | grep -q "default:user:1000:rwx" || return 1
  getfacl ~/.gemini | grep -q "default:user:100999:rwx" || return 1
}
```

---

## ENHANCEMENT #2: IMPL-07 (Permissions 4-Layer Model)

### Location: §4 (Layer 4 — Systemd Self-Healing Timer)

### Current Gap
The section mentions Ed25519 DID verification but doesn't explain what this means or how it works in practice. Haiku's testing showed this needs clarification.

### Proposed Enhancement

**New Subsection**: IMPL-07 §4.2 (Ed25519 DID Self-Healing)

**Add Content**:
```
Ed25519 DID (Decentralized Identifier) Self-Healing

Background:
  Layer 4 uses Ed25519 cryptographic signatures to verify that 
  ACL repairs are legitimate. This prevents unauthorized or 
  accidental modifications while allowing automated healing.

What is a DID in This Context?
  A Decentralized Identifier (DID) is a cryptographic identity 
  that proves:
  - The systemd timer is authorized to modify ACLs
  - The changes haven't been tampered with
  - The repair operation is traceable and auditable

How Self-Healing Works:

  1. Hourly Systemd Timer Fires:
     systemctl --user list-timers | grep acl-monitor
     
  2. Timer Reads ACL Status:
     getfacl ~/.gemini > /tmp/acl-before.txt
     
  3. Verifies Against DID Certificate:
     - Reads Ed25519 public key from ~/.omega/did-keys/
     - Confirms timer has authority to repair
     
  4. Repairs If Needed:
     - Detects missing ACLs (e.g., from accidental chmod)
     - Re-applies Layer 2 ACLs
     - Signs repair with private key
     
  5. Logs Change:
     - Writes to ~/.omega/logs/acl-repairs.log
     - Entry format: timestamp | action | signature | result

Monitoring Repairs:
  tail -n 20 ~/.omega/logs/acl-repairs.log
  
Example Output:
  2026-03-13T10:00:00Z | acl-repair | sig_abc123... | success
  2026-03-13T11:00:00Z | acl-verify | sig_def456... | no_changes
  2026-03-13T12:00:00Z | acl-repair | sig_ghi789... | success

Implementation Checklist:
  [ ] Generate Ed25519 key pair: ssh-keygen -t ed25519 -f ~/.omega/did-keys/omega
  [ ] Create systemd timer: ~/.config/containers/systemd/acl-monitor.timer
  [ ] Create systemd service: ~/.config/containers/systemd/acl-monitor.service
  [ ] Configure hourly execution
  [ ] Enable and start: systemctl --user enable --now acl-monitor.timer
  [ ] Verify: systemctl --user status acl-monitor.timer
  [ ] Test: journalctl --user -u acl-monitor.service -n 20
```

### Systemd Timer Template to Add
```
**Systemd Service Definition** (~/.config/containers/systemd/acl-monitor.service):

[Unit]
Description=Omega-Stack ACL Self-Healing Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/scripts/permissions/acl-monitor.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target

---

**Systemd Timer Definition** (~/.config/containers/systemd/acl-monitor.timer):

[Unit]
Description=Omega-Stack ACL Monitor Hourly Check
Requires=acl-monitor.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h

[Install]
WantedBy=timers.target
```

---

## ENHANCEMENT #3: IMPL-02 (Container Orchestration)

### Location: §4 (Resource Limits) — NEW SUBSECTION

### Current Gap
The manual mentions resource limits exist but doesn't address the critical 350% memory overcommit issue or provide step-by-step guidance. Field testing showed this is a high-risk situation requiring clear procedures.

### Proposed Enhancement

**New Subsection**: IMPL-02 §4b (Memory Management and OOM Prevention)

**Add Content**:
```
Memory Management and OOM Prevention

Current Risk Assessment:
  - Physical RAM: 6.6 GB
  - zRAM Swap: 8 GB
  - Total: 14.6 GB
  - Current estimated peak demand: 21 GB
  - Overcommit ratio: ~145% → 350% (DANGEROUS)
  
OOM Killer Danger:
  When system hits 100% memory pressure:
  1. kernel triggers oom-killer
  2. Kills highest oom_score_adj processes first
  3. Critical services (memory-bank, qdrant) at risk
  4. Cascade failure likely without protection

Safe Configuration:
  - Per-service limits: 512MB-1GB
  - Ensure total < 10 GB (under 6.6 GB physical + 1GB headroom)
  - Use oom_score_adj to protect critical services
  
Procedure 1: Check Current Memory Pressure

  free -h
  # If Swap in use > 2GB: DANGER, reduce services
  
  podman stats --no-stream
  # Identify highest-memory services:
  # - qdrant (vector DB): typically 800MB-1GB
  # - crawl4ai (browser): typically 600MB-1GB
  # - postgres (database): typically 400MB-600MB
  
Procedure 2: Set Per-Service Memory Limits

  For Podman containers in quadlet files:
  
  [Container]
  Image=service-image
  Memory=1G            # Hard limit
  MemorySwap=1.5G      # Swap quota
  MemoryReservation=800M  # Soft limit
  MemorySwappiness=30  # Prefer not to swap

  For Systemd services (native processes):
  
  [Service]
  MemoryLimit=512M
  MemoryMax=768M
  MemoryAccounting=yes

Procedure 3: Protect Critical Services

  Critical services (must survive OOM):
  - memory-bank-mcp (8005) — state hub
  - prometheus (9090) — monitoring
  - redis (6379) — cache

  Protect via oom_score_adj:
  
  # Reduce OOM priority (won't be killed)
  echo -100 | sudo tee /proc/PID/oom_score_adj
  
  Alternatively, in systemd service:
  
  [Service]
  OOMScoreAdjust=-100  # Negative = less likely to kill

Procedure 4: Monitor Memory Trends

  Daily:
    free -h && echo "---" && podman stats --no-stream
    
  Weekly:
    Review prometheus memory metrics
    Check for memory leaks in services
    
  Trigger alerts if:
    - Available mem < 500MB
    - Swap in use > 3GB
    - Any service > 1GB

Procedure 5: Respond to OOM Events

  If OOM killer activates:
  1. Check which service died: journalctl | grep oom-killer
  2. Identify root cause: memory leak? overcommit?
  3. Reduce service memory: Edit quadlet/service definition
  4. Restart service: systemctl restart SERVICE
  5. Verify new memory usage: podman stats SERVICE --no-stream
  
Acceptable zRAM Swap Levels:
  - Ideal: 0-500MB zRAM in use
  - Acceptable: 500MB-1.5GB zRAM in use
  - WARNING: 1.5GB-3GB (reduce load)
  - CRITICAL: >3GB (OOM imminent)
```

---

## ENHANCEMENT #4: IMPL-02 (Container Orchestration)

### Location: §5 (Replacing podman-compose with Quadlets) — NEW SUBSECTION

### Current Gap
The section mentions quadlets are preferred but doesn't provide a step-by-step migration guide. Cloud testing showed users need clear procedures.

### Proposed Enhancement

**New Subsection**: IMPL-02 §5b (Quadlet Migration Procedures)

**Add Content**:
```
Step-by-Step Quadlet Migration from podman-compose

Background:
  podman-compose: Python wrapper, orchestrates via compose.yaml
  Quadlets: Native systemd integration, better resource control
  
Benefit of Quadlets:
  - Automatic startup/restart via systemd
  - Integrated with systemd resource limits
  - Simpler debugging (journalctl output)
  - No Python dependency overhead

Migration Strategy:

STEP 1: Create Quadlet Directory
  mkdir -p ~/.config/containers/systemd/
  # All .container files go here

STEP 2: Convert One Service (Test Case)
  Choose: redis (stateless, easier to test)
  
  FROM podman-compose.yaml:
    redis:
      image: redis:7.4.1-alpine
      ports:
        - "6379:6379"
      volumes:
        - ./redis-data:/data
      command: redis-server --requirepass CHANGEME

  TO ~/.config/containers/systemd/redis.container:
    [Unit]
    Description=Omega-Stack Redis Cache
    After=network.target
    
    [Container]
    Image=redis:7.4.1-alpine
    PublishPort=6379:6379
    Volume=/home/arcana-novai/redis-data:/data:Z
    Exec=redis-server --requirepass CHANGEME
    
    [Service]
    Restart=always
    RestartSec=5s
    
    [Install]
    WantedBy=default.target

STEP 3: Test Single Service Conversion
  # Enable and start the quadlet
  systemctl --user daemon-reload
  systemctl --user enable redis.container
  systemctl --user start redis.container
  
  # Verify it's running
  systemctl --user status redis.container
  journalctl --user -u redis.container -n 20
  
  # Test functionality
  redis-cli -a CHANGEME ping
  # Expected: PONG
  
  # Verify resource limits work
  systemctl --user show redis.container --property=MemoryLimit

STEP 4: Rollback if Needed
  systemctl --user stop redis.container
  systemctl --user disable redis.container
  # Re-enable podman-compose
  podman-compose up -d redis

STEP 5: Convert All Services
  For each service in podman-compose.yaml:
    - Create .container file
    - Test individually
    - Verify all ports/volumes/env vars
    - Document any custom settings

STEP 6: Multi-Service Orchestration
  If services have dependencies (e.g., postgres before app):
  
  Create ~/.config/containers/systemd/omega.target:
    [Unit]
    Description=Omega-Stack Services
    Documentation=man:systemd.target(5)
    
    [Install]
    WantedBy=default.target

  In each .container file, add:
    [Unit]
    PartOf=omega.target
    
  Then control all at once:
    systemctl --user start omega.target
    systemctl --user stop omega.target

STEP 7: Decommission podman-compose
  Once all services converted and tested:
    rm podman-compose.yaml
    podman-compose down  # Clean up old containers

Performance Comparison:
  podman-compose:
    - Python interpreter overhead: ~100ms startup per command
    - Requires compose.yaml parsing
    - Manual health checks
    
  Quadlets:
    - Native systemd: <5ms overhead
    - No parsing, direct systemd integration
    - Automatic restart + health monitoring
```

---

## ENHANCEMENT #5: SUPP-02 (Secrets Management)

### Location: §2 (SOPS Encryption Setup) — NEW SUBSECTION

### Current Gap
The current section doesn't address the 5 plaintext passwords currently in environment files. This is a P1 security issue that needs emergency procedures.

### Proposed Enhancement

**New Subsection**: SUPP-02 §2b (Emergency Plaintext Secret Remediation)

**Add Content**:
```
Emergency Plaintext Secret Remediation

Current Status Assessment:
  Plaintext passwords found in:
  1. qdrant PASSWORD env var
  2. minio ADMIN_PASSWORD
  3. postgres POSTGRES_PASSWORD
  4. redis requirepass
  5. rabbitmq guest password

Risk Level: P1 SECURITY — Requires immediate action

Remediation Procedure:

PHASE 1: Identify All Plaintext Secrets (Emergency)

  Scan for exposed secrets:
    grep -r "password\|PASSWORD\|secret\|SECRET" ~/.env ~/Documents/Xoe-NovAi/
    
  For each found:
    - Document the service it belongs to
    - Note current value
    - Note which file contains it
    - Assess rotation urgency

PHASE 2: Rotate Compromised Credentials (Immediate)

  For each service, follow pattern:
  
  QDRANT:
    1. Access qdrant admin UI (if exposed): not good
    2. Generate new password: openssl rand -base64 32
    3. Update in .env: QDRANT_ADMIN_PASSWORD=<new>
    4. Restart service: podman restart qdrant
    5. Verify access works: curl -u admin:<new> http://localhost:6333/api/health
    6. Document change in /tmp/rotated-secrets.log
  
  MINIO:
    1. Generate new password: openssl rand -base64 32
    2. Update .env: MINIO_ROOT_PASSWORD=<new>
    3. Restart: podman restart minio
    4. Verify: mc alias set local http://localhost:9000 minioadmin <new>
  
  POSTGRES:
    1. Generate new password: openssl rand -base64 32
    2. Update .env: POSTGRES_PASSWORD=<new>
    3. Restart: podman restart postgres
    4. Verify: psql -U postgres -h localhost -c "SELECT 1"
  
  REDIS:
    1. Generate new password: openssl rand -base64 32
    2. Update .env: REDIS_PASSWORD=<new>
    3. Restart: podman restart redis
    4. Verify: redis-cli -a <new> ping
  
  RABBITMQ:
    1. Generate new password: openssl rand -base64 32
    2. Update .env: RABBITMQ_DEFAULT_PASS=<new>
    3. Restart: podman restart rabbitmq
    4. Verify: curl -u guest:<new> http://localhost:15672/api/aliveness-test/%2F

PHASE 3: Encrypt Secrets with SOPS+age (Phase 4, but start now)

  Install SOPS:
    sudo apt-get install sops
    
  Generate age key:
    age-keygen -o ~/.sops/age.key
    chmod 600 ~/.sops/age.key
    
  Create SOPS configuration:
    cat > ~/.sops.yaml << 'EOF'
    creation_rules:
      - path_regex: '.env.enc$'
        encrypted_regex: '^(PASSWORD|SECRET|API_KEY|TOKEN)='
        key_groups:
          - age:
              - [public key from ~/.sops/age.key]
    EOF

PHASE 4: Secure .env Files

  DO NOT COMMIT plaintext .env to git:
    echo ".env" >> .gitignore
    git rm --cached .env
    git commit -m "Remove plaintext secrets from git history"
    
  DO commit encrypted versions:
    sops -e .env > .env.enc
    git add .env.enc
    git commit -m "Add encrypted secrets"

PHASE 5: Audit Trail and Verification

  Log all rotations:
    cat > /tmp/rotated-secrets.log << 'EOF'
    Service: qdrant
    Rotated: 2026-03-13T14:30:00Z
    By: cloud-claude-security-hardening
    Action: Password rotated due to plaintext exposure
    Verification: curl passed
    Status: Success
    EOF
    
  Verify no plaintext remain:
    grep -r "changeme\|default_password\|PASSWORD=" ~/.env ~/Documents/Xoe-NovAi/
    # Should return ZERO results

PHASE 6: Implement Monitoring

  Add to security audit routine:
    - Monthly password rotation schedule
    - Quarterly secret key rotation
    - Real-time detection of plaintext in git commits
    - Pre-commit hook to prevent secret leaks
    
  Pre-commit hook (~/.git/hooks/pre-commit):
    #!/bin/bash
    git diff --cached | grep -iE "password|secret|api_key" && {
      echo "❌ Plaintext secrets detected in commit!"
      exit 1
    }
```

---

## ENHANCEMENT #6: IMPL-01 (Infrastructure)

### Location: §4 (Storage Crisis Resolution) — NEW SUBSECTION

### Current Gap
The section has cleanup procedures but lacks comprehensive disk space analysis and long-term strategy. Field testing showed users need decision trees for what to keep vs delete.

### Proposed Enhancement

**New Subsection**: IMPL-01 §4c (Long-Term Storage Strategy and Analysis)

**Add Content**:
```
Long-Term Storage Strategy and Safe Analysis

Current Crisis: 93% full (8.2 GB free)
Target: <80% (>20 GB free)
Long-term: Maintain <70% for sustainable operations

Safe Analysis Procedure:

STEP 1: Identify Space Hogs Safely

  # Analyze by top-level directory (safe)
  du -sh /* | sort -hr | head -10
  
  Example output:
    100G  /home           ← User data
    8.5G  /var            ← Logs, cache, temp
    2.1G  /usr            ← System packages
    1.5G  /opt            ← Optional software
    
  # For each large directory, drill down
  du -sh /home/* | sort -hr | head -5
  du -sh /var/* | sort -hr | head -5

STEP 2: Classify by Safety

  SAFE TO DELETE (if >30 days old):
    - /home/*/Downloads/*.{zip,tar.gz}
    - /var/cache/apt/*.deb
    - /tmp/* (temporary files)
    - Old backup archives
    
  SAFE TO ARCHIVE (keep but move):
    - Documentation > 2 years old
    - Project backups > 6 months old
    - Old log archives
    
  UNSAFE TO DELETE (keep always):
    - /var/lib/podman/ (container data)
    - ~/.gemini/ (configuration)
    - /media/arcana-novai/ (library/vault drives)
    - Documents/ (project files)

STEP 3: Calculate Safe Cleanup

  # Find candidate files
  find /home -name "*.zip" -mtime +30 -exec du -sh {} \; | awk '{sum+=$1} END {print sum}'
  # Replace 30 with days threshold, .zip with file patterns
  
  # Estimate total reclaimable space
  # Only delete when confident it's safe

STEP 4: Delete Systematically

  # Example: Old download archives
  find ~/Downloads -name "*.zip" -mtime +30 -delete
  find ~/Downloads -name "*.tar.gz" -mtime +30 -delete
  
  # Example: Apt cache
  sudo apt autoclean  # Remove partial packages
  sudo apt clean      # Remove all cached .deb files
  
  # Example: Podman cleanup
  podman image prune -a --force  # Remove unused images
  podman volume prune -f         # Remove unused volumes
  
  # Verify freed space
  df -h | grep "/$"

STEP 5: Monitor and Prevent Future Crisis

  Weekly:
    df -h / | awk '{if (NR==2 && $5+0 > 80) print "⚠️ Disk >80%"}'
    
  Monthly:
    du -sh /* | sort -hr | head -10
    # Watch for rapid growth
    
  Set up alert:
    # Create a systemd timer that warns at 85%
    # See SUPP-06 for alerting procedures

STEP 6: Long-Term Disk Management Strategy

  Tier 1: Hot Storage (keep on root FS)
    - Active projects (<1 GB)
    - Configuration files (.gemini/)
    - Current logs (last 30 days)
    - Target: <70% root FS usage
    
  Tier 2: Warm Storage (move to omega_library)
    - Completed projects (year-old)
    - Documentation archives
    - Old backup sets
    - Move to: /media/arcana-novai/omega_library/archives/
    
  Tier 3: Cold Storage (move to omega_vault)
    - Historical backups (>1 year)
    - Compliance archives (GDPR/SOC2 evidence)
    - Immutable records
    - Move to: /media/arcana-novai/omega_vault/archive/
    
  Tier 4: External/Cloud Storage
    - Redundant backups
    - Offsite copies
    - S3-compatible cloud (Wasabi/Backblaze)

STEP 7: Archival Procedure

  # Move old project to library
  tar czf ~/old-project.tar.gz ~/Documents/old-project/
  mv ~/old-project.tar.gz /media/arcana-novai/omega_library/archives/
  rm -rf ~/Documents/old-project/
  
  # Index for future reference
  echo "old-project | 2024-01-15 | /media/.../archives/old-project.tar.gz" >> ~/.omega/archive-index.txt

STEP 8: Verify Cleanup Success

  df -h /
  # Should show: >20 GB free and <80% used
  
  du -sh ~/* | sort -hr | head -5
  # Should show no unexpected large directories
```

---

## ENHANCEMENT #7: ARCH-02 (Facet Orchestration)

### Location: NEW SECTION (Facet Resilience and Fallbacks)

### Current Gap
The orchestration manual assumes all facets are available. Field testing showed systems need to handle unavailable services gracefully.

### Proposed Enhancement

**New Section**: ARCH-02 §5 (Facet Resilience and Fallback Strategies)

**Add Content**:
```
Facet Resilience: Handling Unavailable Services

Background:
  In real-world systems, facets may become unavailable due to:
  - Memory pressure (OOM killer)
  - Network issues (service timeout)
  - Configuration problems
  - Planned maintenance
  
Challenge:
  Archon should continue operating even if some facets fail

Solution Framework:

PATTERN 1: Detect Unavailability

  Before delegating, check facet health:
  
  omega-facet status FACET_NAME
  # Returns: ready, unhealthy, unavailable, timeout
  
  If status != "ready":
    - Log unavailability: "Researcher facet unavailable"
    - Continue with available facets
    - Plan fallback action

PATTERN 2: Fallback Strategies

  Strategy 1: Act Directly as Archon
    Problem: Researcher unavailable for literature review
    Action: Perform research synthesis directly using Archon's knowledge
    Benefit: Slower but functional
    Tradeoff: Less depth than specialist facet
    
  Strategy 2: Delegate to Alternative Facet
    Problem: Engineer unavailable for code review
    Action: Delegate to General-Legacy (broader but less specialized)
    Benefit: Similar capability, different context
    Tradeoff: Less specialized expertise
    
  Strategy 3: Queue for Later
    Problem: DataScientist unavailable for experiment design
    Action: Queue task for retry when facet recovers
    Benefit: Perfect quality when available
    Tradeoff: Delayed result

PATTERN 3: Circuit Breaker Implementation

  Prevent cascading failures with circuit breaker:
  
  [Closed State] ← Normal operation, facet healthy
      ↓
      (Failures accumulate)
      ↓
  [Open State] ← Facet returning errors, skip delegation
      ↓
      (Wait for recovery)
      ↓
  [Half-Open State] ← Test if facet recovered
      ↓
      If healthy → [Closed State]
      If unhealthy → [Open State]

  Implementation:
  
    Track per facet:
    - consecutive_failures: counter (reset on success)
    - last_failure_time: timestamp
    - circuit_state: closed | open | half_open
    
    Rules:
    - If consecutive_failures >= 3: Open circuit
    - If circuit open and 5 minutes passed: Half-open
    - If half-open test succeeds: Close circuit
    - If half-open test fails: Re-open circuit

PATTERN 4: Graceful Degradation

  Archon operating modes by facet availability:
  
  Full Capability Mode:
    All 9 facets healthy
    Actions: Delegate to specialists
    Quality: Maximum depth
    
  Degraded Mode:
    5-8 facets healthy
    Actions: Delegate to available, Archon covers gaps
    Quality: Good
    
  Reduced Mode:
    2-4 facets healthy
    Actions: Archon leads, limited delegation
    Quality: Acceptable
    
  Single-Agent Mode:
    All facets unavailable
    Actions: Archon operates solo
    Quality: Reduced but functional
    Recovery: Resume full mode when facets recover

PATTERN 5: Monitoring and Alert

  Daily facet health check:
    omega-facet status
    # Should show: all 9 ready
    
  Alert thresholds:
    - Any facet unhealthy > 5 minutes: WARNING
    - Any facet unhealthy > 1 hour: CRITICAL
    - >3 facets unavailable: CRITICAL
    
  Response:
    1. Check facet logs: journalctl -u facet-SERVICE
    2. Check resource pressure: free -h, df -h, podman stats
    3. Restart service if safe: systemctl restart SERVICE
    4. If pattern repeats: File incident for investigation

PATTERN 6: Recovery Procedures

  When facet becomes unhealthy:
  
  1. Immediate (within 1 minute):
    - Detect via healthcheck
    - Notify Archon
    - Switch to fallback
    
  2. Short-term (1-5 minutes):
    - Log symptoms
    - Check resources (memory, disk, CPU)
    - Attempt restart if resource-constrained
    
  3. Medium-term (5-30 minutes):
    - Review error logs
    - Check network connectivity
    - Verify configuration validity
    - Restart with diagnostics
    
  4. Long-term (>30 minutes):
    - File incident ticket
    - Analyze root cause
    - Implement permanent fix
    - Verify with stress testing

IMPLEMENTATION CHECKLIST:

  [ ] Add facet health check before delegation
  [ ] Implement circuit breaker state machine
  [ ] Define graceful degradation modes
  [ ] Set up monitoring and alerts
  [ ] Create recovery runbook
  [ ] Document fallback strategies
  [ ] Test with facet failures (chaos engineering)
```

---

## SUMMARY OF ALL ENHANCEMENTS

| Enhancement | Manual | Effort | Priority | Impact |
|-------------|--------|--------|----------|--------|
| 1. Explicit UID specs in ACLs | IMPL-07 | 30 min | HIGH | Critical clarity |
| 2. Ed25519 DID self-healing | IMPL-07 | 45 min | HIGH | New functionality |
| 3. Memory mgmt + OOM prevention | IMPL-02 | 1 hour | HIGH | Safety critical |
| 4. Quadlet migration guide | IMPL-02 | 1 hour | MEDIUM | Modernization |
| 5. Plaintext secret remediation | SUPP-02 | 45 min | HIGH | Security fix |
| 6. Long-term storage strategy | IMPL-01 | 45 min | MEDIUM | Operations |
| 7. Facet resilience patterns | ARCH-02 | 1 hour | MEDIUM | Reliability |

**Total Effort**: 5-6 hours  
**Priority Order**: 1, 2, 3, 5 → then 4, 6, 7

---

## IMPLEMENTATION INSTRUCTIONS FOR SONNET

1. **Review** each enhancement above
2. **Integrate** into existing manual at specified location
3. **Verify** cross-references in other manuals remain correct
4. **Test** code examples if provided
5. **Update** IMPL-09 (Verification Suite) with new test cases
6. **Create** SONNET_MANUAL_UPDATES_CHANGELOG.md documenting all changes

Once updated manuals are ready, provide to cloud Claude for testing.

---

**From**: Cloud Claude via Haiku analysis  
**To**: Sonnet  
**Status**: Ready for implementation  
**Timeline**: 2-3 hours of focused work  

