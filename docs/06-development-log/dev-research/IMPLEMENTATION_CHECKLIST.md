# 🚀 Xoe-NovAi Security Trinity: Implementation Checklist

**Quick Reference for Developers & Project Managers**

---

## 📋 Phase 0: Preparation (Pre-Implementation)

- [ ] **Read Documentation**
  - [ ] `00_MASTER_SUMMARY.md` (15 min)
  - [ ] `01_REMEDIATION_PLAN_TOC.md` (20 min)
  - [ ] `02_CRITICAL_FIXES_WITH_CODE.md` (60 min)

- [ ] **Environment Validation**
  - [ ] Verify Podman 5.x installed: `podman --version`
  - [ ] Check rootless mode: `podman info | grep Rootless`
  - [ ] Test socket access: `ls -la $XDG_RUNTIME_DIR/podman/podman.sock`
  - [ ] Verify Internet access (for initial DB download)

- [ ] **Dependencies**
  - [ ] Python 3.9+ available
  - [ ] PyYAML installed: `pip install pyyaml`
  - [ ] Syft, Grype, Trivy container images available

- [ ] **Directory Setup**
  - [ ] Create `~/.xnai/security-db/` directory
  - [ ] Create `scripts/` directory for new files
  - [ ] Create `configs/` directory for policy YAML
  - [ ] Verify `reports/security/` exists

---

## 🔨 Phase 1: Core Fixes (Critical Issues #1-3)

### Issue #1: Podman Socket Resolution

- [ ] **Create `scripts/socket_resolver.py`**
  - [ ] Copy code from Issue #1 section
  - [ ] Verify imports: `from pathlib import Path`
  - [ ] Test file: `python3 scripts/socket_resolver.py`
  - [ ] Expected output: `✅ Podman socket: /run/user/{UID}/podman/podman.sock`

- [ ] **Update `security_audit.py`**
  - [ ] Add import: `from socket_resolver import get_podman_socket`
  - [ ] Replace lines 22-23 with new code
  - [ ] Test: Run `security_audit.py` (should not fail on socket)

- [ ] **Verify**
  - [ ] Test on local system: socket resolves correctly
  - [ ] Test with missing socket: diagnostic output is helpful
  - [ ] Test with `PODMAN_SOCK` override: environment variable honored

### Issue #2: Exit Code Conflation

- [ ] **Create `scripts/security_utils.py`**
  - [ ] Copy code from Issue #2 section
  - [ ] Verify imports: `from enum import Enum`
  - [ ] Run unit tests: `python3 scripts/security_utils.py`
  - [ ] Expected: 9 tests passing (3 each tool × 3 scenarios)

- [ ] **Update `security_audit.py`**
  - [ ] Add import: `from security_utils import ScanTool, classify_scan_result`
  - [ ] Replace `execute_command()` function with new version
  - [ ] Update `run_audit()` to use semantic classification

- [ ] **Verify**
  - [ ] Grype exit 1 (vulns found) treated as success: ✅
  - [ ] Syft exit 1 (error) treated as failure: ❌
  - [ ] Trivy exit 4 (timeout) identified correctly: ⏱️
  - [ ] Error messages are semantic, not just exit codes

### Issue #3: Missing DB Initialization

- [ ] **Create `scripts/db_manager.py`**
  - [ ] Copy code from Issue #3 section
  - [ ] Test: `python3 scripts/db_manager.py status`
  - [ ] If DBs don't exist: message indicates need to init

- [ ] **Update Makefile**
  - [ ] Add `init-security-db` target
  - [ ] Add `verify-security-db` target
  - [ ] Add `update-security-db` target
  - [ ] Update `security-audit` target to verify first

- [ ] **Initialize Databases** (First Run Only)
  - [ ] Run: `make init-security-db`
  - [ ] Wait: 10-15 minutes for downloads
  - [ ] Verify: `ls -lh ~/.xnai/security-db/` shows files
  - [ ] Check size: Should be ~800MB total

- [ ] **Verify**
  - [ ] `make verify-security-db` returns success
  - [ ] Databases don't re-download on second run
  - [ ] `make security-audit` runs without DB initialization errors

---

## 💪 Phase 2: Robustness Fixes (Issues #4-5)

### Issue #4: Over-Rigid Security Gatekeeping

- [ ] **Create `configs/security_policy.yaml`**
  - [ ] Copy policy from Issue #4 section
  - [ ] Customize thresholds if needed
  - [ ] Verify YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('configs/security_policy.yaml'))"`

- [ ] **Create `scripts/security_policy.py`**
  - [ ] Copy code from Issue #4 section
  - [ ] Verify imports: `import yaml`
  - [ ] Test with sample reports (if available)

- [ ] **Update `pr_check.py`**
  - [ ] Import `SecurityPolicy` class
  - [ ] Load policy: `policy = SecurityPolicy("configs/security_policy.yaml")`
  - [ ] Call `policy.evaluate_cves()` instead of simple count
  - [ ] Call `policy.evaluate_secrets()` instead of simple block

- [ ] **Verify**
  - [ ] Code with minor CVEs (5 Medium) passes policy: ✅
  - [ ] Code with Critical exploitable CVE fails: ❌
  - [ ] Code with API key secret fails: ❌
  - [ ] Code with test credential warning: ⚠️

### Issue #5: No JSON Validation

- [ ] **Add validation to `scripts/security_utils.py`**
  - [ ] Copy `validate_json_report()` function
  - [ ] Test: Call on valid/invalid JSON files

- [ ] **Update `security_audit.py`**
  - [ ] After Syft: validate SBOM exists and has required keys
  - [ ] After Grype: validate vulns.json structure
  - [ ] After Trivy: validate safety.json structure
  - [ ] Fail scan if validation fails

- [ ] **Verify**
  - [ ] Missing JSON file caught immediately: ❌
  - [ ] Corrupted JSON caught immediately: ❌
  - [ ] Valid reports pass validation: ✅
  - [ ] Error messages are helpful (file size, missing keys)

---

## ⚙️ Phase 3: Air-Gap & Optimization (Issues #6-8)

### Issue #6: Memory Pressure (Optional for Standard Deployments)

- [ ] **Review layer scanner documentation** (in Issue #6)
  - [ ] Understand layer-by-layer scanning concept
  - [ ] Note: Optional optimization, not required

- [ ] **If implementing layer scanner:**
  - [ ] Create `scripts/layer_scanner.py`
  - [ ] Update `security_audit.py` to support `--layer-mode` flag
  - [ ] Test with large image (>4GB if available)

- [ ] **Verify**
  - [ ] Standard images scan normally: ✅
  - [ ] Large images don't OOM: ✅
  - [ ] Memory usage monitored during scan: ✅

### Issue #7: Trivy Configuration

- [ ] **Create `.trivy.yaml`**
  - [ ] Copy configuration from Issue #7 section
  - [ ] Customize secret detection rules if needed

- [ ] **Update Trivy command in `security_audit.py`**
  - [ ] Add volume mount: `-v $(pwd)/.trivy.yaml:/root/.trivy.yaml:ro`
  - [ ] Add config flag: `--config /root/.trivy.yaml`
  - [ ] Enable secret detection: `--security-checks secret`

- [ ] **Verify**
  - [ ] Trivy loads configuration without errors: ✅
  - [ ] Secret detection rules applied: ✅
  - [ ] Test fixtures excluded if configured: ✅

### Issue #8: Rollback Mechanism

- [ ] **Add checkpoint functions to `security_audit.py`**
  - [ ] Implement `checkpoint_reports()` function
  - [ ] Implement `rollback_reports()` function
  - [ ] Call checkpoint before scanning
  - [ ] Call rollback on error

- [ ] **Verify**
  - [ ] Before-scan reports backed up: ✅
  - [ ] Rollback restores previous state: ✅
  - [ ] Backup directory not polluted: ✅

---

## ✅ Testing Checklist

### Unit Tests
- [ ] `socket_resolver.py` unit tests pass
- [ ] `security_utils.py` unit tests pass (9/9 passing)
- [ ] `db_manager.py` verify command succeeds
- [ ] Policy YAML parses without errors

### Integration Tests
- [ ] Full Trinity scan completes without crashes
- [ ] Semantic exit codes interpreted correctly
- [ ] Database initialization succeeds
- [ ] Security policy evaluation correct
- [ ] JSON validation catches errors

### Functional Tests
- [ ] Scanner works on multiple distros (test ≥2):
  - [ ] Fedora 39+
  - [ ] Ubuntu 22.04+
  - [ ] (Optional) Alpine, RHEL, Debian
- [ ] Air-gap mode (no Internet) works
- [ ] Large images (~5GB) scan without OOM
- [ ] Rollback recovers from failed scan

### Regression Tests
- [ ] Existing smoke tests still pass
- [ ] Performance not degraded >10%
- [ ] No new security warnings from dependencies
- [ ] Logs are clean (no spurious warnings)

---

## 📊 Validation Metrics

| Metric | Target | Method |
|--------|--------|--------|
| **Unit Test Coverage** | >90% | `pytest --cov` |
| **Integration Test Pass Rate** | 100% | Run full test suite |
| **Scanner Startup Time** | <5s | Time `make security-audit` |
| **Database Size** | <1GB | `du -sh ~/.xnai/security-db/` |
| **False Positive Rate** | <5% | Manual test cases |
| **Memory Usage (3GB image)** | <4GB peak | Monitor during scan |
| **Policy Accuracy** | 100% | Test case validation |

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All tests pass (unit + integration)
- [ ] Documentation updated
- [ ] Team trained on new tools
- [ ] Rollback procedure documented
- [ ] Monitoring/alerting configured

### Deployment Day
- [ ] Database initialized: `make init-security-db`
- [ ] Databases verified: `make verify-security-db`
- [ ] Test scan runs successfully
- [ ] Baseline metrics recorded
- [ ] Team standing by for support

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Track performance vs. baseline
- [ ] Gather team feedback
- [ ] Document any issues
- [ ] Plan improvements

---

## 🔧 Troubleshooting Quick Links

### Socket Issues
- **Error:** "Podman socket not found"
- **Fix:** See Issue #1 (socket_resolver.py)
- **Diagnostic:** Run `python3 scripts/socket_resolver.py`

### Exit Code Issues
- **Error:** "Scan failed with exit 1" (but vulns found, not error)
- **Fix:** See Issue #2 (security_utils.py semantic classification)
- **Test:** `python3 scripts/security_utils.py`

### Database Issues
- **Error:** "Database not found"
- **Fix:** Run `make init-security-db`
- **Verify:** `make verify-security-db`

### Policy Issues
- **Problem:** Legitimate code rejected
- **Fix:** See Issue #4 (adjust thresholds in security_policy.yaml)
- **Test:** Add suppressions for known-good vulns

### Memory Issues
- **Error:** Process killed (OOM)
- **Fix:** See Issue #6 (enable layer scanning)
- **Monitor:** Check `free -h` during scan

---

## 📞 Support Decision Tree

```
Scanner doesn't start
├─ Socket error → Issue #1 (socket_resolver.py)
├─ DB not found → Issue #3 (db_manager.py)
└─ Other error → Check logs with `-v` flag

Scan completes but results wrong
├─ Exit code misinterpreted → Issue #2 (security_utils.py)
├─ Policy too strict → Issue #4 (security_policy.yaml)
├─ JSON validation error → Issue #5 (validate_json_report)
└─ Missing secrets → Issue #7 (Trivy config)

Scan crashes/OOM
├─ Large image → Issue #6 (layer_scanner.py)
├─ Memory pressure → Increase swap/zram
└─ File descriptor limit → `ulimit -n`

Can't recover from bad scan
└─ No checkpoint → Issue #8 (rollback_mechanism)
```

---

## 📈 Success Indicators

✅ **All should be true after implementation:**

- [ ] Scanner runs on all major Linux distros
- [ ] Exit codes interpreted semantically
- [ ] Databases initialize automatically
- [ ] Graduated security policy works
- [ ] JSON validation prevents silent failures
- [ ] Memory usage optimized
- [ ] Secrets detected correctly
- [ ] Failed scans can be rolled back
- [ ] Monitoring/alerting configured
- [ ] Team trained and confident

---

## 🎯 Final Go/No-Go Criteria

**STOP if any of these are true:**
- ❌ Unit tests don't pass
- ❌ Critical distro not supported
- ❌ Security policy produces false positives >10%
- ❌ Database initialization fails
- ❌ Memory usage exceeds 6GB on standard images

**PROCEED if all true:**
- ✅ All tests passing
- ✅ Scanner works on ≥2 distros
- ✅ Security policy accurate
- ✅ Deployment documented
- ✅ Team confident in procedures

---

**For detailed implementation instructions, see:**
- `00_MASTER_SUMMARY.md` - Overview & quick start
- `01_REMEDIATION_PLAN_TOC.md` - Complete roadmap
- `02_CRITICAL_FIXES_WITH_CODE.md` - Full code implementations

**Questions? Each issue section has detailed troubleshooting.**

