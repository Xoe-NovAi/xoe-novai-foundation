# 🗝️ Expert Knowledge: Rootless Podman & Permissions Mastery

**Version**: 1.0.0 (Metropolis v4.1.2 Baseline)
**Tags**: [infrastructure, podman, rootless, permissions, Z, U]
**Status**: AUTHORITATIVE

---

## 🏛️ 1. The Core Problem: User Namespaces

In rootless Podman, your host user (e.g., UID 1000) is mapped to the container's "root" (UID 0). All other container users (like UID 1001 for appuser) are mapped to high-range SubUIDs on the host.

### The Conflict:
If a host directory is owned by the **real host root**, a rootless container cannot access it, even if using `podman unshare`, because the rootless user has no authority over real host root files.

---

## 🛠️ 2. The Solution: The Magic `:U` Flag

The `:U` (User) flag is the most effective way to resolve permission denied errors without requiring host-level `sudo`.

### Mechanism:
When you mount a volume with `:U`, Podman automatically performs a `chown` on the host directory to match the UID/GID of the user running inside the container.

### Standard Pattern (docker-compose.yml):
```yaml
volumes:
  - ./data/redis:/data:Z,U
```
- **`:Z`**: Private SELinux label (prevents other containers from accessing).
- **`:U`**: Automatic ownership mapping to the container user.

---

## 🛑 3. Handling Host-Root Owned Directories

If you encounter `Operation not permitted` while trying to `chown` a directory owned by the host root:

1.  **Stop the Container**: `podman stop [container_name]`
2.  **Move/Delete the Data (if safe)**: If the directory was accidentally created by a root process, it must be removed or moved by a host-level administrator.
3.  **Ensure User Ownership**: Host-level directories used for Podman volumes MUST be owned by the host user running Podman.

---

## 📜 4. Operational Protocol for All Agents

1.  **NEVER** use manual `chown` inside `podman unshare` if `:U` can be used.
2.  **ALWAYS** use the `:Z,U` suffix for volume mounts in `docker-compose.yml` to ensure cross-distro portability.
3.  **AUDIT**: Regularly run `ls -ln` on data directories to verify they are mapped to your user's SubUID range (e.g., UIDs starting at 100000).

---
*Crystallized by The Architect (Facet 1). 🏗️*
