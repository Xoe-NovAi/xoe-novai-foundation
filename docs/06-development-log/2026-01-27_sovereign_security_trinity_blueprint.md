# 🔱 Xoe-NovAi Sovereign Security Trinity: Detailed Blueprint

**Date:** January 27, 2026  
**Status:** Approved for Implementation  
**ToC:**
1. [Architecture](#architecture)
2. [Sovereign Auditor Logic](#sovereign-auditor-logic)
3. [Makefile Integration](#makefile-integration)
4. [PR Gatekeeping](#pr-gatekeeping)
5. [Implementation Roadmap](#implementation-roadmap)

---

## 🏗️ Architecture
The Trinity ensures sovereignty by separating **Inventory**, **Audit**, and **Safety**.

1.  **Syft**: Generates `sbom.json` (CycloneDX).
2.  **Grype**: Scans `sbom.json` for precise CVEs.
3.  **Trivy**: Scans image for leaked secrets and misconfigs.

---

## 🐍 Sovereign Auditor Logic
File: `scripts/security_audit.py`

```python
import subprocess
import json
import os
from pathlib import Path

REPORT_DIR = Path("reports/security")
DB_DIR = Path(os.path.expanduser("~/.xnai/security-db"))
IMAGE = "xnai-rag:latest"

def execute_scan(command, layer_name):
    print(f"🔱 Auditing {layer_name}...")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode > 1: # Engine failures
        raise Exception(f"{layer_name} CRASHED: {result.stderr}")
    return result

def run_trinity():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Syft
    execute_scan(["podman", "run", "--rm", 
        "-v", "/var/run/podman/podman.sock:/var/run/podman/podman.sock",
        "-v", f"{REPORT_DIR.absolute()}:/out:Z",
        "anchore/syft", IMAGE, "-o", "cyclonedx-json", "--file", "/out/sbom.json"], "Inventory")

    # 2. Grype
    execute_scan(["podman", "run", "--rm", 
        "-v", f"{REPORT_DIR.absolute()}:/in:Z",
        "-v", f"{DB_DIR.absolute()}:/cache:Z",
        "anchore/grype", "sbom:/in/sbom.json", "--db", "/cache", "-o", "json", "--file", "/in/vulns.json"], "CVE Audit")

    # 3. Trivy
    execute_scan(["podman", "run", "--rm", 
        "-v", "/var/run/podman/podman.sock:/var/run/podman/podman.sock",
        "-v", f"{REPORT_DIR.absolute()}:/out:Z",
        "aquasec/trivy", "image", "--security-checks", "secret", "-f", "json", "-o", "/out/secrets.json", IMAGE], "Safety")
```

---

## 🛠️ Makefile Integration
File: `Makefile`

```makefile
SECURITY_DB_DIR := $(HOME)/.xnai/security-db

update-security-db: ## 💾 Sync vulnerability databases for air-gap usage
	@mkdir -p $(SECURITY_DB_DIR)
	@podman run --rm -v $(SECURITY_DB_DIR):/cache:Z aquasec/trivy:latest image --download-db-only --cache-dir /cache
	@podman run --rm -v $(SECURITY_DB_DIR):/cache:Z anchore/grype:latest db update

security-audit: ## 🔱 Execute the Trinity Audit (Syft + Grype + Trivy)
	@echo "$(CYAN)🛡️ Starting Security Audit Trinity...$(NC)"
	@$(PYTHON) scripts/security_audit.py
```

---

## 🏁 PR Gatekeeping
File: `scripts/pr_check.py`

```python
def check_security_results():
    with open("reports/security/vulns.json") as f:
        v = json.load(f)
        criticals = [m for m in v['matches'] if m['vulnerability']['severity'] == 'Critical']
    
    with open("reports/security/secrets.json") as f:
        s = json.load(f)
        leaks = s.get('Results', [{}])[0].get('Secrets', [])

    if criticals or leaks:
        return False, f"Found {len(criticals)} Criticals and {len(leaks)} Secrets"
    return True, "Passed"
```

---

## 📊 Implementation Roadmap
1.  **Setup**: Create the `scripts/security_audit.py` orchestrator.
2.  **Wiring**: Add `security-audit` and `update-security-db` targets to Makefile.
3.  **Integration**: Update `scripts/pr_check.py` to block on security failures.
4.  **Verification**: Run a full PR audit and verify the generated JSON reports.