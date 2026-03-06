# EKB Gem: Permission-Hardened Runtime Directories for Rootless Podman
**Category:** Architect / Infrastructure
**Date:** 2026-01-26
**Issue:** `PermissionError: [Errno 13] Permission denied` when container services (Chainlit, RAG, Crawler) attempt to create or write to files in host-mounted volumes.

## Root Cause
- **UID Mapping:** In Rootless Podman, the container's `root` (0) and `appuser` (1001) are mapped to high-range UIDs on the host (e.g., 100000+).
- **Default Ownership:** Host directories created by the user (UID 1000) are not writable by the container's sub-UIDs unless permissions are explicitly permissive.
- **Dynamic File Creation:** Libraries like Chainlit attempt to create config files (`chainlit.md`, `.chainlit/`) at the root of the application directory at runtime.

## Remediation: The "Sticky 1777" Pattern
1. **Dockerfile Hardening:** Ensure all potential runtime-writable paths are initialized and opened in the image.
   ```dockerfile
   RUN mkdir -p /app/logs /app/data /app/.chainlit && \
       chown -R appuser:appuser /app && \
       chmod -R 1777 /app
   ```
   *Note: `1777` (Sticky bit) allows anyone to write but only the owner to delete, maximizing compatibility for rootless mapping.*

2. **Compose tmpfs:** Use `tmpfs` for ephemeral runtime directories (logs, cache) to bypass host volume conflicts entirely.
   ```yaml
   tmpfs:
     - /app/logs:size=100m,mode=1777
     - /app/.chainlit:size=10m,mode=1777
   ```

3. **Host-Side Fix:** If a volume mount is already corrupted by ownership mismatches, use `podman unshare` to reset permissions on the host.
   ```bash
   podman unshare chmod -R 777 data/faiss_index
   ```

## Prevention
- **Image Self-Sufficiency:** Pre-create all hidden directories (`.cache`, `.chainlit`, `.crawl4ai`) in the Dockerfile.
- **Permissive Defaults:** Use `1777` for directories that are strictly for runtime artifacts.
- **Volume Minimization:** Only mount volumes for data that *must* persist; use `tmpfs` for everything else.
