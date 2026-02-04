# Deep Dive: Sovereign Security Trinity
**Architectural Pattern**: Waterfall of Proof
**Implementation Version**: 2.0.5

## 🎭 The Philosophy of Sovereignty
Traditional container security relies on "calling home" to centralized registries or trusting opaque scan results. The **Sovereign Security Trinity** is designed for the air-gap: we generate our own inventory, audit it with local databases, and enforce our own policies.

## 🏗️ The Three Layers

### 1. The Identity Layer (Syft)
We use **Syft** to generate a "Software Bill of Materials" (SBOM). 
- **Format**: CycloneDX JSON v1.5.
- **Why**: An SBOM is a static manifest. By scanning the SBOM instead of the running container, we ensure that the audit is repeatable and doesn't miss transient build-time dependencies.

### 2. The Precision Layer (Grype)
**Grype** takes the SBOM and maps it against vulnerability databases.
- **Pattern**: SBOM-to-CVE mapping.
- **Optimization**: Grype is significantly faster and more precise than scanning image layers directly because it uses the metadata provided by Syft to identify package versions with high confidence.

### 3. The Safety Layer (Trivy)
While Syft/Grype handle *vulnerabilities*, **Trivy** handles *safety*.
- **Secret Scanning**: Scans every layer of the Docker image for API keys, private keys, or credentials that may have been accidentally committed.
- **Config Audit**: Checks for dangerous Dockerfile patterns (e.g., `USER root`).

## 📡 The "Tarball Scanning" Pattern
In rootless environments, many scanners struggle to mount the `/var/run/podman/podman.sock` because of filesystem namespace isolation. 

**The Solution**:
```bash
# 1. Export the image to a standard tar archive
podman save -o xnai-api.tar xnai-api:latest

# 2. Scan the archive file directly
syft scan file:xnai-api.tar -o cyclonedx-json > sbom.json
trivy image --input xnai-api.tar
```
This pattern is **bulletproof**. It works on any Linux distribution (Fedora, Ubuntu, RHEL) because it treats the container image as a simple file, bypassing the complexities of the container daemon socket.

## 🚦 Policy as Code (`security_policy.yaml`)
We do not hardcode security "fail" conditions. We use a declarative policy engine:
```yaml
policy:
  gatekeeper:
    block_on_secrets: true
    thresholds:
      critical:
        max_total: 0
        max_exploitable: 0
      high:
        max_total: 5
```
This allows the development team to graduate security requirements as the project matures from Prototype to Release Candidate.

## 🔌 Offline Management
The Trinity is air-gap ready. Use `make update-security-db` to fetch the latest vulnerability data while connected, then switch to a 100% offline audit mode for production deployments.
