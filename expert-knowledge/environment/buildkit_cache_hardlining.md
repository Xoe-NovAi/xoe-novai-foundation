# BuildKit Cache Mount Hardlining in Rootless Podman

**Domain**: Environment / Infrastructure
**Date**: January 25, 2026
**Expert**: Gemini CLI & The Vizier

## The Problem: Hardlink Fallback Errors
During `uv pip install` operations within rootless Podman containers, the following error frequently appears:
`DEBUG Failed to hardlink ... attempting to copy files as a fallback`

This happens because `uv` (running as root in the container) attempts to hardlink files from the BuildKit cache mount to the system-wide `site-packages` directory. If the cache mount is owned by a different UID (e.g., `1001`), the hardlink fails, leading to slow copy operations and potential permission friction.

## The Solution: The `uid=0` Standard
In rootless Podman, the container's `root` (UID 0) is actually the host user. To ensure maximum build velocity and hardlink compatibility:

1.  **Standardize Cache Mounts**: Always use `uid=0,gid=0` for mounts used during `apt` or `uv pip --system` installs.
2.  **Syntax**:
    ```dockerfile
    RUN --mount=type=cache,id=xnai-uv-cache,target=/root/.cache/uv,uid=0,gid=0 \
        uv pip install --system -r requirements.txt
    ```
3.  **Rationale**: This aligns the owner of the cache files with the owner of the installation process (root within the container), allowing the filesystem to perform atomic hardlinks.

## Performance Impact
- **Build Speed**: 2x - 5x faster cache re-use.
- **Disk Usage**: Significant reduction due to hardlinking instead of copying large wheelhouse artifacts.

