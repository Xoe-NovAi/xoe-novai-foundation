# 🏆 Xoe-NovAi Official BuildKit Optimization Standard

## 🎯 Strategic Purpose
To achieve elite build performance (2-4x speedups) while maintaining absolute data sovereignty and local-first reliability. BuildKit cache mounts are our primary mechanism for accelerating Debian and Python package installation without external infrastructure.

---

## 🛠️ The Hardened Implementation Standard

### 1. The "Line 1" Syntax Rule
Every Dockerfile **MUST** begin with the BuildKit syntax directive on the very first line.
```dockerfile
# syntax=docker/dockerfile:1
```
*   **Rationale**: Podman and Buildah require this to enable advanced features like `--mount`.

### 2. Isolated Cache IDs
All cache mounts **MUST** use a unique `id` prefixed with `xnai-`.
```dockerfile
RUN --mount=type=cache,id=xnai-apt-cache,target=/var/cache/apt ...
```
*   **Rationale**: Prevents different project builds on the same host from corrupting each other's metadata.

### 3. Rootless Permission Stability (UID/GID Mapping)
Cache mounts **MUST** explicitly specify the non-root UID/GID used in the Xoe-NovAi Foundation stack (`1001:1001`).
```dockerfile
RUN --mount=type=cache,id=xnai-pip-cache,target=/root/.cache/pip,uid=1001,gid=1001 ...
```
*   **Rationale**: Prevents "Permission Denied" errors in rootless Podman 5.x environments.

### 4. Debian Auto-Clean Disable
Debian-based base images automatically clean the package cache. This **MUST** be disabled.
```dockerfile
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
```

---

## 🚨 Troubleshooting & Edge Cases

### The `sharing=locked` Edge Case
*   **Status**: **DEPRECATED/OVERRIDDEN**.
*   **Finding**: Many Podman versions (5.0-5.3) return an "invalid mount option" for `sharing=locked`.
*   **Standard**: Omit `sharing=locked`. Podman's default sharing behavior is safer for rootless environments.

### Stale Cache Remediation
If packages fail to install or permissions become corrupted:
```bash
make cache-clear
make cache-warm
```

---

## 📈 Performance Targets
- **Apt Installs**: < 8s (Warm) vs 45s (Cold).
- **Pip Installs**: < 12s (Warm) vs 120s (Cold).
- **Iteration Loop**: < 60s total build time for service updates.

---
**Reviewer**: Claude (Senior Auditor) & Gemini CLI (Infrastructure Lead)
**Status**: 🟢 AUTHORITATIVE
