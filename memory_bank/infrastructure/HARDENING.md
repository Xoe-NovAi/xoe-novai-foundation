# XNAi System Hardening & Permission Strategy

## 🛡️ The "Never Again" Permission Fix
Permission issues in rootless Podman were rooted in UID/GID mapping offsets. We have implemented a definitive architectural fix.

### 1. Host-Container Identity Alignment
- **Mechanism**: `userns_mode: "keep-id"` in `docker-compose.yml`.
- **Effect**: Maps the container user (UID 1001) directly to the host user (`arcana-novai`, UID 1000) for all bind-mounted volumes.
- **Benefit**: host and container now see the same numeric IDs, ending "Permission Denied" errors during RAG ingestion and expert creation.

### 2. Mandatory Pre-Flight Hardening
- **Tool**: `system-harden.sh`
- **Actions**:
    - Aligns host directory ownership via `podman unshare`.
    - Enforces `775` permissions.
    - Sets the **Sticky Bit** (`chmod g+s`) on all data directories to ensure future files inherit the correct group.

### 3. Service Resilience
- **Cache Volumes**: Added dedicated `data/cache` mapping to prevent "Read-only file system" errors in LLM/Whisper model downloads.
- **AnyIO Locks**: Upgraded from `asyncio.Lock` to `anyio.Lock` for structured concurrency compliance.

---
**Status**: ✅ **PERMANENTLY REMEDIATED** (2026-03-01)
