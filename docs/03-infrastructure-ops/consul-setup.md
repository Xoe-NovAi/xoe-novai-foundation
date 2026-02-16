# Consul Infrastructure Setup (Rootless Podman)

**Version:** 1.0
**Date:** 2026-02-15
**Status:** Operational

## Overview
The XNAi Foundation stack uses **Consul** for service discovery and health monitoring. This setup is optimized for **Rootless Podman** on a Ryzen 5700U host.

## Configuration Details

### 1. Image Selection
We use **`consul:1.15.4`**.
*   **Reason:** Newer versions (1.18+) and the `alpine` variants exhibited manifest/compatibility issues with the specific rootless Podman / BuildKit setup on this host. Version 1.15.4 is confirmed stable.

### 2. Rootless Permissions (Crucial)
In a rootless Podman environment, volume permissions can be tricky.
*   **Problem:** The `consul` container (running as `consul` user 100) often cannot write to the bind-mounted `data/consul` directory owned by the host user.
*   **Solution:** We configure the container to run as `root` *inside the container* (`user: root` in `docker-compose.yml`).
    *   In rootless Podman, `root` inside the container maps to the **unprivileged user** on the host.
    *   This allows the container to write to `data/consul` without permission errors.

### 3. Networking
*   **Port 8500:** HTTP API & UI (exposed to host).
*   **Port 8600:** DNS interface (exposed to host).
*   **Network:** `xnai_network` (bridge).

## Manual Setup / Troubleshooting

### Directory Initialization
If the `data/consul` directory permission issues persist, reset them:
```bash
# On the host
mkdir -p data/consul
chmod 777 data/consul
```

### Verification
1.  **UI:** Access `http://localhost:8500`
2.  **Logs:** `podman logs xnai_consul`
