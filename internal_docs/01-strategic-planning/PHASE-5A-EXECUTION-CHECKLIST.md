# PHASE 5A EXECUTION CHECKLIST

## Pre-Execution
- [ ] Read `PHASE-5A-MEMORY-OPTIMIZATION.md` (Tier 2 Guide)
- [ ] Understand success metrics
  - Zero OOM events under 5x load
  - Compression ≥2.0:1
  - Peak memory <95%
- [ ] Have sudo access or run as root (required for many steps)
- [ ] Required tools installed: `zramctl`, `systemctl`, `swapon`, `podman` or `docker` (verify with `which zramctl systemctl swapon podman || which docker`)
- [ ] Ensure available memory headroom before stress test: `free -h` (recommended: at least 2GB free / >20% available)
- [ ] Backup current configuration:
  ```bash
  mkdir -p /tmp/phase5a-backup
  cp /proc/sys/vm/swappiness /tmp/phase5a-backup/
  swapon --show > /tmp/phase5a-backup/swaps.txt
  ```
- [ ] Run preflight validation (recommended):
  ```bash
  sudo python3 scripts/validate-phase-5a.py
  ```


---

## Task 5A.1: Collect Baseline (30 minutes)

**Objective**: Capture system state before modifications

### Checklist
- [ ] Create baseline directory: `mkdir -p /tmp/phase5a-baseline`
- [ ] Run baseline collection script:
  ```bash
  scripts/phase-5a-stress-test.py --baseline-only
  # Or manually:
  free -h > /tmp/phase5a-baseline/memory-start.txt
  sysctl vm.swappiness vm.page-cluster > /tmp/phase5a-baseline/kernel-params-start.txt
  dmesg | tail -20 > /tmp/phase5a-baseline/dmesg-start.txt
  ```
- [ ] Record baseline metrics:
  - Physical RAM: _____ GB
  - Available: _____ MB
  - Current swappiness: _____
  - Current zRAM: _____ (active/not active)
  - OOM events (24h): _____

### Success Criteria
- [ ] Baseline data saved to `/tmp/phase5a-baseline/`
- [ ] Current kernel parameters documented
- [ ] Memory state captured

---

## Task 5A.2: Apply Kernel Parameters (15 minutes)

**Objective**: Configure kernel for zRAM optimization

### Checklist
- [ ] Create `/etc/sysctl.d/99-xnai-zram-tuning.conf`:
  ```bash
  sudo cp TEMPLATE-sysctl-zram-tuning.conf /etc/sysctl.d/99-xnai-zram-tuning.conf
  ```
- [ ] Apply configuration:
  ```bash
  sudo sysctl -p /etc/sysctl.d/99-xnai-zram-tuning.conf
  ```
- [ ] Verify each parameter:
  - [ ] `vm.swappiness = 180`: `cat /proc/sys/vm/swappiness | grep 180`
  - [ ] `vm.page-cluster = 0`: `cat /proc/sys/vm/page-cluster | grep 0`
  - [ ] `vm.watermark_boost_factor = 0`: `sysctl vm.watermark_boost_factor | grep 0`

### Success Criteria
- [ ] All 5 kernel parameters set to target values
- [ ] No errors in sysctl output
- [ ] Parameters readable via `/proc/sys/`

---

## Task 5A.3: Configure zRAM Device (20 minutes)

**Objective**: Create and activate zRAM swap device

### Checklist
- [ ] Verify zramctl is installed:
  ```bash
  which zramctl || sudo apt install util-linux
  ```
- [ ] Create systemd service:
  ```bash
  sudo cp TEMPLATE-xnai-zram.service /etc/systemd/system/xnai-zram.service
  ```
- [ ] Enable and start service:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable xnai-zram.service
  sudo systemctl start xnai-zram.service
  ```
- [ ] Verify zRAM active:
  - [ ] `zramctl` shows zram0
  - [ ] Algorithm is zstd
  - [ ] `swapon --show` includes /dev/zram0
  - [ ] `systemctl status xnai-zram.service` shows active

### Success Criteria
- [ ] `/dev/zram0` active with 4GB size
- [ ] zstd compression confirmed
- [ ] Systemd service enabled and running
- [ ] Swap configuration includes zram0

---

## Task 5A.4: Execute Stress Test (45 minutes)

**Objective**: Validate zero OOM events under 5x load

### Checklist
- [ ] Prepare stress test (default: staging/ramp):
  ```bash
  # Staging (recommended): incremental ramp, safer defaults
  python scripts/phase-5a-stress-test.py --staging --duration 600 --workers 5

  # Production intensity (ONLY with approval):
  python scripts/phase-5a-stress-test.py --confirm-prod --duration 600 --workers 5
  ```
- [ ] Monitor during test (separate terminal):
  ```bash
  watch -n 2 'zramctl && echo "" && free -h'
  ```
- [ ] Record results:
  - OOM events: _____
  - Compression ratio: _____ : 1
  - Peak memory %: _____
  - System responsiveness: _____

### Success Criteria - CRITICAL
- [ ] ✅ Zero OOM killer invocations
- [ ] ✅ Compression ratio ≥1.5:1 (target ≥2.0)
- [ ] ✅ Peak memory <95%
- [ ] ✅ System remains responsive (no hangs)

**If FAILED**: Skip Task 5A.5 and run rollback (see PHASE-5A-MEMORY-OPTIMIZATION.md section 7)

---

## Task 5A.5: Production Deployment (15 minutes)

**Objective**: Make configuration persistent and document

### Checklist
- [ ] Verify persistence:
  ```bash
  ls -la /etc/sysctl.d/99-xnai-zram-tuning.conf
  ls -la /etc/systemd/system/xnai-zram.service
  systemctl is-enabled xnai-zram.service | grep enabled
  ```
- [ ] Create team documentation:
  ```bash
  cat > memory_bank/PHASE-5A-DEPLOYED.md << 'EOF'
  # Phase 5A Deployed: 2026-02-12
  
  ## Configuration
  - Kernel parameters: Applied via `/etc/sysctl.d/99-xnai-zram-tuning.conf`
  - zRAM service: `/etc/systemd/system/xnai-zram.service`
  - Status: Active and persistent
  
  ## Monitoring
  - Daily check: `./scripts/zram-health-check.sh`
  - Real-time: `watch zramctl`
  - Logs: `journalctl -u xnai-zram.service -f`
  
  ## Rollback
  See PHASE-5A-MEMORY-OPTIMIZATION.md section 7
  EOF
  ```
- [ ] Create health check script:
  ```bash
  chmod +x scripts/zram-health-check.sh
  ./scripts/zram-health-check.sh  # First run
  ```
- [ ] Team briefing document created
- [ ] All documentation updated

### Success Criteria
- [ ] Configuration files in `/etc/` 
- [ ] Systemd service enabled
- [ ] Documentation complete
- [ ] Team briefed
- [ ] Monitoring script ready

---

## Phase 5A Validation (Post-Deployment)

### Run Final Validation
```bash
python scripts/validate-phase-5a.py
```

Should show:
```
✅ 1. zRAM Device Active
✅ 2. zRAM Algorithm = zstd
✅ 3. vm.swappiness = 180
✅ 4. vm.page-cluster = 0
✅ 5. Swap Configured
✅ 6. Systemd Service Exists
✅ 7. Systemd Service Enabled
✅ 8. Systemd Service Active
✅ 9. Sysctl Config Persistent
✅ 10. No Recent OOM Events

🎉 Phase 5A validation PASSED!
```

---

## Optional: Test Persistence (Reboot)

### Before Reboot
```bash
zramctl > /tmp/zram-pre.txt
sysctl vm.swappiness > /tmp/swappiness-pre.txt
```

### Reboot
```bash
sudo reboot
```

### After Reboot
```bash
# Verify persistence
zramctl > /tmp/zram-post.txt
diff /tmp/zram-pre.txt /tmp/zram-post.txt  # Should be identical

# Verify kernel params
sysctl vm.swappiness  # Should be 180

# Check service
systemctl status xnai-zram.service  # Should be active
```

---

## Troubleshooting During Execution

### If OOM events occur during stress test:
```bash
# Stop test immediately
pkill -9 python

# Check what was OOM killed
dmesg | grep "Out of memory" | tail -5

# Options:
# 1. Increase zRAM size to 6GB
# 2. Reduce container limits
# 3. Run rollback and retry (see PHASE-5A-MEMORY-OPTIMIZATION.md)
```

### If stress test hangs:
```bash
# In another terminal
pkill -9 python
# Or kill the entire terminal session and try again
```

### If kernel parameters won't apply:
```bash
# Requires sudo
sudo sysctl -w vm.swappiness=180

# Check kernel version (need 5.10+)
uname -r
```

---

## Sign-Off

- [ ] Task 5A.1 Complete: _____________ Date: _______
- [ ] Task 5A.2 Complete: _____________ Date: _______
- [ ] Task 5A.3 Complete: _____________ Date: _______
- [ ] Task 5A.4 Complete: _____________ Date: _______
- [ ] Task 5A.5 Complete: _____________ Date: _______
- [ ] Validation Passed: _____________ Date: _______

**Phase 5A Status**: 
- [ ] ✅ COMPLETE AND VALIDATED
- [ ] ⏳ IN PROGRESS
- [ ] ❌ FAILED - Rollback executed

**Notes**:
_________________________________________________
_________________________________________________

---

## Next: Phase 5B

**Phase 5B**: Observable Stack (Prometheus + Grafana + OpenTelemetry)
- Start immediately (no blockers after Phase 5A)
- See: `PHASE-5B-OBSERVABLE-FOUNDATION.md` (when available)

---

**Execution Guide**: Phase 5A Memory Optimization  
**Version**: Tier 3 Implementation Module  
**Created**: 2026-02-12  
**Status**: Ready for Execution
