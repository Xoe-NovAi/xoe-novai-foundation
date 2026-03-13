# EKB Gem: Podman Rootless Volume Permissions

## Issue
Containers (e.g., `xnai_crawler`, `xnai_rag_api`) fail with `PermissionError` when writing to host-mounted volumes, despite the container user being `appuser` (UID 1001).

## Root Cause
In rootless Podman, host UIDs are mapped to a range within the container. If a host directory is created by the host user (e.g., UID 1000) and mounted into a container running as `appuser` (mapped to a different UID on the host, often in the 100,000+ range), the container user lacks write permissions. `chown` within the Dockerfile only affects the image layer, not the runtime mount.

## Remediation
Use the "Sticky Bit + World Writable" pattern (`chmod 1777`) for runtime-writable directories that are intended to be mapped to host volumes. This allows any mapped container user to write while preventing unauthorized deletion.

```dockerfile
# Hardening pattern for rootless mounts
RUN mkdir -p /app/logs /app/data && \
    chmod -R 1777 /app/logs /app/data
```

Additionally, ensure host-side directories (like `/tmp/crawl4ai`) are initialized with appropriate permissions before `make up`.

## Prevention
1. **Dockerfile Standard**: All `mkdir` for volume targets must be followed by `chmod 1777`.
2. **Infrastructure Scripts**: Use `scripts/infra/init_volumes.sh` to pre-create host directories with `777` permissions to avoid manual intervention.

