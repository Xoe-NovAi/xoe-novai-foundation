# Sovereign Development Workflow
**Status**: Ready for Production / PR-Ready
**Version**: v0.1.0-alpha

## 🔱 Overview
The Xoe-NovAi Foundation Stack uses a "Security-First, Local-Always" development workflow. This guide explains how to evolve the stack while maintaining its sovereign integrity.

---

## 🛠️ The Core Toolkit
Before you begin development, familiarize yourself with our primary orchestration tools:

- **`make setup`**: The entry point. Detects hardware and builds the 7-service stack.
- **`make pr-check`**: The mandatory gatekeeper. Checks security, telemetry, and logic.
- **`scripts/infra/butler.sh`**: The infrastructure orchestrator for managing Podman services.
- **`scripts/security_audit.py`**: The "Security Trinity" auditor (Syft + Grype + Trivy).

---

## 🔄 The Inner Loop (Develop & Verify)

### 1. Feature Implementation
When adding features (e.g., a new RAG endpoint or a UI component):
- **Follow the Ma'at Ideals**: Ensure zero telemetry and resource stewardship.
- **Stay Rootless**: Never write code that requires root privileges.
- **Use `uv`**: Manage Python dependencies via `uv pip install` inside the container context.

### 2. Local Verification
```bash
# Start the stack to test your changes
make start

# Check the health of all 7 services
make status
```

### 3. The Security Audit (Manual)
Before submitting code, run a manual security pass:
```bash
# Update local CVE databases first
make update-security-db

# Run the Trinity audit
make security-audit
```

---

## 🏁 The PR Gatekeeper (`make pr-check`)
This is the most critical step in the workflow. **No PR will be accepted unless this command passes.**

**What it verifies:**
1.  **Sovereign Smoke Test**: Core API and UI functionality.
2.  **Zero-Telemetry Audit**: Verifies 8 mandatory privacy disables.
3.  **Security Trinity**: Zero Critical CVEs and zero secrets in the image.
4.  **Documentation Freshness**: Verifies that knowledge has kept pace with code.

---

## 🗺️ Post-PR Vision (Phase 2 & 3)
Once the foundation is stabilized, our development focus shifts to:
- **Vulkan-Native Inference**: Offloading LLM/STT tasks to the Ryzen iGPU.
- **WASM Plugin System**: Enabling "soft-isolation" for third-party extensions.
- **Qdrant Agentic Filtering**: Enhancing RAG precision beyond the 90% threshold.

---

## 📞 Support & Troubleshooting
- **Logs**: `make logs` (Tail all services).
- **Diagnostics**: `make doctor` (System-level health check).
- **Expert Knowledge**: Consult `expert-knowledge/` for deep architectural patterns.