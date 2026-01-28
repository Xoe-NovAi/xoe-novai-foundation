# Rootless Podman :U Volume Flag Standard

**Domain**: Environment / Infrastructure
**Date**: January 26, 2026
**Expert**: Gemini CLI (Sovereign Agent)

## The Problem: Host-Level UID Collisions
In rootless Podman environments, manual `chown` commands on the host (e.g., `sudo chown 999:999 data/redis`) are brittle and dangerous. They often collide with host system users (e.g., `dnsmasq`) and fail when the container tries to write to the volume due to namespace mapping mismatches.

## The Solution: The `:U` Flag
Podman 3.1+ and 5.x introduce the `:U` volume flag, which provides "Automatic Ownership Mapping."

1.  **Usage**: Add `:U` to the volume mount string in `docker-compose.yml` or `podman run`.
    ```yaml
    volumes:
      - ./data/redis:/data:Z,U
    ```
2.  **Mechanism**: At runtime, Podman recursively `chown`s the host directory to match the UID/GID of the user running *inside* the container namespace.
3.  **Benefits**: 
    *   **Zero-sudo**: No manual host permissions management required.
    *   **Portability**: Works across different Linux distributions regardless of host UID ranges.
    *   **Safety**: Avoids collisions with host system users.

## Best Practices
*   **Combine with `:Z`**: Always use `:Z,U` if SELinux is enabled (standard on Fedora/RHEL/CentOS).
*   **Host Ownership**: Create the directory as the host user (UID 1000) first. Podman will handle the rest.
*   **Avoid Manual Chown**: Remove all hardcoded `chown` commands from Makefiles or setup scripts.

## Rationale
This aligns with Xoe-NovAi's "Sovereign Infrastructure" goal by reducing reliance on host-level root privileges and ensuring atomic, reproducible environment setup.
