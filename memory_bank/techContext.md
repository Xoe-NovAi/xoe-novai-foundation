# Technical Context: Xoe-NovAi Sovereignty & Performance

## 💻 Hardware: AMD Ryzen 7 5700U (Zen 2)
- **Cores**: 8 Cores / 16 Threads (Optimized for 6 AI threads).
- **RAM**: 8GB DDR4-3200 (Expandable to 32GB).
- **GPU**: AMD Radeon Vega 8 iGPU (Vulkan 1.2 / RADV GPL).
- **Architecture**: Zen 2 with improved IPC and efficiency.

## 🛠️ Infrastructure: Podman 5.x Rootless with tmpfs-First Strategy
- **Networking**: `pasta` driver with MTU 1500 alignment.
- **Build Engine**: BuildKit-enabled (native rootless support).
- **Volume Management**: Sticky bit pattern (mode=1777) for rootless permissions.
- **Service Orchestration**: Podman Compose + Quadlet readiness.

## 🛡️ Sovereign Security Trinity (Audit Toolset)
- **Inventory**: **Syft** (CycloneDX SBOM generation).
- **Auditor**: **Grype** (Precision CVE scanning via SBOM).
- **Guardrail**: **Trivy** (Layer-level safety scrub for secrets/configs).
- **Strategy**: **Tarball-to-Scan** (Exports image to `.tar` to ensure scanning reliability in rootless environments).

## 🏁 PR Readiness & Gatekeeping
- **Logic Engine**: `scripts/pr_check.py`.
- **Policy Engine**: `scripts/security_policy.py` consuming `configs/security_policy.yaml`.
- **Gatekeepers**: 
    - E2E Smoke Tests (IAM, RAG, Resilience).
    - Documentation Linting (`mkdocs-lint`).
    - Zero-Telemetry Audit (8 mandatory disables).
    - Trinity Security Pass (Zero Critical CVEs/Secrets).

## 📦 Package Management & Sovereignty
- **Primary Tool**: `uv` (Fast Python package installer) pinned in `xnai-base`.
- **Build Restoration**: BuildKit Cache Mounts (`type=cache`) for `apt`, `pip`, and `uv`.
- **Offline Readiness**: Cache mounts persist between builds; `scripts/db_manager.py` manages offline security DBs.

## ⚙️ Performance Standards
- **OpenBLAS**: `OPENBLAS_CORETYPE=ZEN` (Mandatory Ryzen optimization).
- **Memory**: 400MB Rule (Soft-stop protection).
- **Inference**: Llama-cpp-python (Vulkan-accelerated).

## 🧠 Knowledge & Strategy
- **Expert Knowledge**: High-fidelity technical mastery repository in `expert-knowledge/`.
- **Knowledge Graph**: Bidirectional relationship mapping for AI reasoning.
- **Living Brain Protocol**: Mandatory AI-population of mastery after every verified fix.

*Updated by Gemini CLI (Hardened Security Trinity & PR Readiness Audit)*