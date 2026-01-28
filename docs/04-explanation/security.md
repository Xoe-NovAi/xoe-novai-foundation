# Security Model: Sovereign Security Trinity
**Status**: Hardened (v2.0.5)
**Policy**: Defense-in-Depth Rootless Execution & Automated Gatekeeping

## 1. Container Security (Podman Rootless)
Xoe-NovAi runs exclusively in **rootless Podman** namespaces. 

- **Mapping**: Host UIDs are mapped to high-range subordinate UIDs via `podman unshare`.
- **Ownership**: All data directories are mapped to internal UID `1001` (appuser).
- **Filesystem**: Containers use `read_only: true` with `tmpfs` mounts for transient state.

## 2. 🔱 The Sovereign Security Trinity
As of v2.0.5, the stack utilizes a three-layered automated audit pipeline to ensure supply-chain integrity and runtime safety.

| Layer | Tool | Rationale | Output |
| :--- | :--- | :--- | :--- |
| **1. Inventory** | **Syft** | Generates a **CycloneDX JSON** SBOM. This provides an immutable identity for every library in the stack. | `sbom.json` |
| **2. Precision Audit** | **Grype** | Scans the SBOM for vulnerabilities. Lower false-positives than raw image scanners. | `vulns.json` |
| **3. Safety Scrub** | **Trivy** | Scans raw image layers specifically for **Secrets** (leaked keys) and **Misconfigurations**. | `secrets.json` |

### 📦 Bulletproof Tarball Scanning
To bypass complex rootless Podman socket permission issues across different Linux distributions, the audit pipeline uses an **Export-to-Scan** strategy:
1.  The target image is exported to a local tarball via `podman save`.
2.  The scanners audit the tarball directly, eliminating the need for socket mounts or network access.

## 3. 🚦 Graduated Policy Enforcement
Security is not binary. The stack uses `configs/security_policy.yaml` to define nuanced gatekeeping rules:
- **Zero Tolerance**: Any `Critical` severity CVE or any `Secret` (API Key, Private Key) found in the image.
- **Graduated Alerting**: `High` severity CVEs are allowed up to a threshold (default: 5) before blocking, enabling operational flexibility while maintaining safety.

## 4. 🏁 PR Readiness Auditor
The Trinity is integrated into `make pr-check`. No code is merged into production until it passes the full security pass and the **Zero-Telemetry Audit** (verifying 8 mandatory privacy disables).

## 5. 🔌 Infrastructure Resilience
- **Socket Resolver**: `scripts/socket_resolver.py` dynamically locates the rootless Podman socket across Fedora, RHEL, and Ubuntu.
- **Offline DBs**: `scripts/db_manager.py` maintains persistent, air-gap-ready vulnerability databases in `~/.xnai/security-db`.