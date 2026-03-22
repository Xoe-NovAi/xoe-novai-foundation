# 🛡️ PERMISSIONS REMEDIATION PROTOCOL v2.0
**Epoch**: SESS-27.7 | **Status**: RATIFIED | **Target**: 16GB AnyIO Sovereign Stack

---

## 1. The Core Conflict: Host vs. Container
- **Host User**: `arcana-novai` (UID 1000).
- **Container User**: Often `root` (UID 0) or specific users (e.g., `postgres` UID 999).
- **Rootless Podman Mapping**:
    - Container UID 0 -> Host UID 100000
    - Container UID 1000 -> Host UID 1000 (Keep-ID) or 100999 (Mapped)
    - **The Friction**: When a container writes a file as UID 100999, the host (UID 1000) cannot read/write it without `sudo`.

## 2. The Solution: "Fixed Primary Roles" with ACL Healing
We employ a **Hybrid Strategy**:
1.  **Service Configuration**: Where possible, force containers to run as UID 1000:1000 (e.g., `user: "1000:1000"` in `docker-compose.yml`).
2.  **ACL Healing**: For services that *must* run as other UIDs (like Postgres), we use Access Control Lists (ACLs) to grant R/W access to *both* UID 1000 and the mapped UID.

## 3. The "Healer" Script: `scripts/omega-permissions-heal.sh`
This script is the **Source of Truth** for permissions. It applies:
- **Layer 1 (Ownership)**: `chown -R 1000:1000` (Resets base ownership).
- **Layer 2 (ACLs)**: `setfacl -R -m u:1000:rwx,u:100999:rwx` (Grants shared access).
- **Layer 3 (Defaults)**: `setfacl -R -d ...` (Ensures *future* files inherit these rules).

## 4. Remediation Workflow
**If you encounter `Permission denied` errors:**

1.  **Stop the Stack**:
    ```bash
    podman-compose down
    ```

2.  **Run the Healer**:
    ```bash
    sudo ./scripts/omega-permissions-heal.sh
    ```

3.  **Verify & Restart**:
    ```bash
    ls -l data/  # Check ownership
    ./start_stack.sh
    ```

## 5. Service-Specific Rules
| Service | Internal UID | Host Strategy | Notes |
| :--- | :--- | :--- | :--- |
| **RAG API** | 1000 | `user: "1000:1000"` | Fixed in SESS-27.7. Direct access. |
| **Redis** | 999 | ACL Mapped | Data dir needs `omega-permissions-heal.sh`. |
| **Postgres** | 999 | ACL Mapped | Data dir needs `omega-permissions-heal.sh`. |
| **Qdrant** | 1000 | `user: "1000:1000"` | Direct access. |

## 6. Critical Command Reference
- **Check Permissions**: `getfacl <file>`
- **Reset Directory**: `sudo rm -rf data/<dir> && mkdir data/<dir>` (Data Loss!)

**Archon Signature**: `Jem-4.6-Sovereign` 🔱
