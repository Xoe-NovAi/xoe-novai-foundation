# Expert Knowledge: Build Recovery & Disk Management in Resource-Constrained Environments

## Issue: Stalled Builds & "No Space Left on Device"
**Date**: 2026-01-26
**Category**: Infrastructure / Build Engineering
**Symptom**: Builds hanging without progress, or explicitly failing with `os error 28: No space left on device`.

### Root Causes
1.  **Disk Exhaustion**: High disk utilization (90%+) leaving insufficient room for temporary container layers and package archives.
2.  **Orphaned Processes**: Interrupted builds (e.g., due to timeout or manual cancellation) leaving `buildah`, `podman`, or `apt-get` processes running in the background, locking resources and consuming I/O.
3.  **Build Context Size**: Large files in the build context being copied to the daemon.

### Remediation & Recovery Workflow

#### 1. Resource Cleanup (The 8GB Reclaim)
When disk is near capacity, execute the following to reclaim space safely:
```bash
# 1. Prune unused Podman images
podman image prune -f

# 2. Vacuum system logs (highly effective for long-running systems)
sudo journalctl --vacuum-size=500M

# 3. Clear user-level caches
rm -rf ~/.cache/*

# 4. Clear rotated system logs
sudo rm -f /var/log/syslog.* /var/log/kern.log.* /var/log/messages.*
```

#### 2. Process Stabilization
Ensure no competing build processes are active:
```bash
# Identify and kill orphaned build/package processes
pkill -9 -f "podman|buildah|apt-get|uv|pip"
```

#### 3. Standardized Build Procedure
Use background execution with robust logging for long-running builds to avoid terminal timeout issues:
```bash
nohup bash -c "SKIP_DOCKER_PERMISSIONS=true make build" > build_full.log 2>&1 &
```

### Prevention & Best Practices
- **Monitoring**: Always check `df -h .` before initiating a large build stack.
- **Cache Mounts**: Leverage BuildKit cache mounts (`--mount=type=cache`) to reuse package archives across builds, reducing both download time and temporary disk usage.
- **Image Indexing**: Standardize on a consistent naming convention (e.g., `xnai-` prefix) to simplify management and avoid confusion during multi-service deployments.
