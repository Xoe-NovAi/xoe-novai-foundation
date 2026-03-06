# Sovereign Setup: Podman Rootless Mastery
**Status**: Elite Hardened
**Goal**: Zero-Root Security & Sovereign Data Ownership

## 1. Why Rootless Podman?
Traditional container engines (like legacy Docker) often run as root, creating a massive security hole. Xoe-NovAi uses **Podman Rootless** to ensure that even if a container is compromised, the attacker has zero privileges on your host system.

---

## 2. UID Mapping (The 1001:1001 Standard)
Inside the Xoe-NovAi containers, all processes run as a non-root user with UID `1001` (appuser).

### 2.1 The "Permission Denied" Trap
Because you are running rootlessly, your host UID (e.g., 1000) does not directly match the internal 1001 UID. Standard `chown` commands on the host will often result in permission errors inside the container.

### 2.2 The Sovereign Solution: `podman unshare`
To correctly set permissions for your data volumes, you must use the `unshare` command. This executes a command inside the same user namespace as your containers.

**The Mandatory Command**:
```bash
# Correctly set ownership for all data directories
podman unshare chown -R 1001:1001 library knowledge data backups logs
```

---

## 3. Advanced Volume Flags (:Z,U)
Xoe-NovAi uses specialized volume flags in `podman-compose.yml` to handle SELinux and UID shifting automatically.

- **`:z` (Lowercase)**: Shared mode. Use this for directories accessed by multiple containers (e.g., the FAISS index).
- **`:Z` (Uppercase)**: Private mode. Use this for service-specific paths (e.g., logs) to prevent inter-service interference.
- **`,U` (UID Shift)**: Tells Podman to automatically shift the ownership of the host directory to match the container's internal user.

**Example Wiring**:
```yaml
volumes:
  - ./library:/library:z,U
  - ./logs:/app/logs:Z,U
```

---

## 4. 🔱 The Sovereign Security Trinity (NEW)
As of **January 27, 2026**, every Xoe-NovAi setup includes an automated security auditor. This ensures your sovereign stack remains untainted by upstream vulnerabilities or leaked secrets.

- **Inventory**: `syft` generates an SBOM (CycloneDX) for every image.
- **Audit**: `grype` precision-scans the SBOM for CVEs.
- **Safety**: `trivy` scrubs raw layers for accidental secrets.

### 4.1 Bulletproof Tarball Scanning
To bypass rootless socket permission issues, the stack exports images to local tarballs before scanning. 
**Verification**: `make security-audit`

---

## 5. Socket Resolution & Persistence
Rootless Podman can place its control socket in different locations depending on your Linux distribution (Ubuntu vs Fedora vs RHEL).

### 5.1 The Socket Resolver
We use `scripts/socket_resolver.py` to dynamically locate your rootless socket. This is used by our PR Auditor and Monitoring stacks to ensure they can talk to the container engine without manual configuration.

---

## 6. Secret Management (Zero-Telemetry)
To maintain sovereignty, sensitive keys (like your `REDIS_PASSWORD`) are never hardcoded in `.env` files.

1.  **Create Secret**: Store your password in `secrets/redis_password.txt`.
2.  **Mount Secret**: Podman mounts this file into `/run/secrets/` inside the container.

---

## 7. Verification SOP
To ensure your sovereign setup is correct:
1.  **Check UID**: `podman exec xnai-ui id` (Should show `uid=1001`).
2.  **Verify Write**: `podman exec xnai-rag touch /library/test.txt`.
3.  **Run Gatekeeper**: `make pr-check` (The ultimate verification of security, telemetry, and logic).
