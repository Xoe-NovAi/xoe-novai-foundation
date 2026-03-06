# Expert Knowledge: Podman/Docker Compose Mount Conflicts

## Issue: Duplicate Mount Destination
**Date**: 2026-01-26
**Category**: Infrastructure / Containers
**Symptom**: `Error: /path/to/dir: duplicate mount destination`

### Root Cause
This error occurs when a single destination path inside a container is targeted by multiple mount instructions in `docker-compose.yml`. 

Common scenarios include:
1.  **Mixing tmpfs and Volumes**: Attempting to mount a directory as both a `tmpfs` AND a `volume`.
2.  **Overlapping Volume Mounts**: Mounting different host paths to the same container path.

### Case Study: Xoe-NovAi Crawler Logs
In the Xoe-NovAi `docker-compose.yml`, the `crawler` service had the following conflict:
```yaml
    tmpfs:
      - /app/logs:size=100m,mode=0755
    volumes:
      - /tmp/crawler_logs:/app/logs
```
The container runtime cannot satisfy both requests for the same path (`/app/logs`).

### Remediation
Decide on a single mount strategy for the destination:
- Use **Volumes** if persistence or host-side log inspection is required.
- Use **tmpfs** if the data is transient and should reside in memory for performance or privacy.

### Prevention & Best Practices
- **Audit Mounts**: Regularly review `docker-compose.yml` for overlapping paths.
- **Service Isolation**: Ensure each service has a clearly defined and non-conflicting logging strategy.
- **Deployment Validation**: Use `podman-compose config` to validate the structure before deployment.
