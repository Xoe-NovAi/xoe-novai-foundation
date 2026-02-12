---
priority: critical
context: general
activation: always
last_updated: 2026-01-20
version: 1.0
---

# Security and Hardening Guidelines

- **Principle of Least Privilege**: Rootless Podman primary. Use `userns_mode: keep-id` for 1:1 UID/GID mapping (avoids chown side effects). Fall back to `:U` with pre-chown via `podman unshare` if needed.
- **Volume Mounts**: `:z` for confinement. Use `:U` only after verifying host ownership (prevents "lchown operation not permitted"). Avoid if host files are git-tracked.
- **Non-Root Containers**: Always `USER 1001` (or non-root) in Dockerfiles/Podman images.
- **Secrets**: Never hardcode. Use Podman secrets or env files (chmod 600).
- **Privacy & Sovereignty**: Zero-telemetry architecture. No external calls. Enforce Ma'at ideals: data never leaves user control, (harm prevention, truth verification).
- **Permissions Checks**: After creation, verify user-owned (755 dirs, 644 files) with `ls -la`. Use `podman unshare chown -R $(id -u):$(id -g) dir/` for fixes.
- **Updates**: Latest Podman via Kubic repo + gpg dearmor key management. Install fuse-overlayfs and slirp4netns.

Example podman-compose:
```yaml
userns_mode: keep-id
volumes:
  - ./docs:/workspace/docs:z
