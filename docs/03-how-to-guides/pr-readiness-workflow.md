# PR Readiness & Gatekeeping Workflow
**Status**: Mandatory for Production Merge
**Command**: `make pr-check`

## 🏁 Overview
The PR Readiness Auditor (`scripts/pr_check.py`) is the final gatekeeper for the Xoe-NovAi Foundation stack. It ensures that every change complies with our **Sovereignty**, **Security**, and **Stability** standards.

## 🛠️ The 5 Pillars of Readiness

### 1. Sovereign Smoke Test
Verifies the core E2E flow of the stack:
- Can the RAG API start?
- Can it authenticate a user?
- Can it process a retrieval request?
- Does the circuit breaker handle failures gracefully?

### 2. Documentation Audit
Ensures that knowledge keeps pace with code:
- **Linting**: Verifies `mkdocs.yml` structure and internal links.
- **Freshness**: Checks for `TODO` items and outdated technical references.

### 3. Containerized Import Audit
Prevents "It works on my machine" bugs:
- Executes `scripts/verify_imports.py` inside the `xnai-base` container.
- Verifies that all required libraries (FastAPI, Redis, etc.) are correctly installed in the image.

### 4. Zero-Telemetry Verification
Enforces **Ma'at Ideal 40 (Privacy)**:
- Audits the environment for 8 mandatory telemetry disables:
  - `CRAWL4AI_TELEMETRY=0`
  - `OTEL_SDK_DISABLED=true`
  - `ANALYTICS_OPT_OUT=true`
  - (and more...)

### 5. 🔱 Security Trinity Audit
Executes the automated vulnerability and safety scan:
- **SBOM Generation** (Syft).
- **CVE Audit** (Grype).
- **Secret Scrub** (Trivy).
- **Policy Check**: Blocks the PR if it violates `configs/security_policy.yaml`.

## 🚀 How to Run the Check

### Local Audit
```bash
# Run the full suite (takes ~3.5 minutes)
make pr-check
```

### Partial Audits (Quick Feedback)
```bash
# Run only the security scans
make security-audit

# Run only the smoke tests
./scripts/smoke_test.py
```

## 📈 Understanding Results
The auditor uses **Semantic Exit Codes**:
- **0**: Success. PR is ready for merge.
- **1**: Policy Violation (e.g., Critical CVE found). **Fix required.**
- **2**: Engine Failure (e.g., Podman socket not found). **System triage required.**
- **3**: Smoke Test Failure. **Logic fix required.**

## 🛡️ Handling Security Blockers
If the audit blocks on a CVE (e.g., `CVE-2025-13836`):
1.  **Update**: Try updating the base image or specific library.
2.  **Suppress**: If the CVE is a false positive or unfixable, add it to the suppression list (only with Architect approval).
