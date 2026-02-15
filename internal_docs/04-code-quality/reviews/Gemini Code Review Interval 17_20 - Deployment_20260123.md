# Code Review Interval 17/20 - Deployment & Orchestration
**Date**: 2026-01-23
**Reviewer**: Gemini CLI
**Files Reviewed**: 5
**Total Files Reviewed**: 85

## Executive Summary
Interval 17 evaluates Deployment and Orchestration. **Research Refinement**: Recommended the use of `--userns=keep-id` for developer convenience and confirmed the necessity of the `:Z` flag for automated SELinux labeling in rootless Podman environments.

## Detailed File Analysis

### File 1: podman-compose.yml
#### Overview
- **Purpose**: Multi-service orchestration.
- **Research Refinement**: Updated security recommendations to include `userns_mode: "keep-id"` for the `rag` and `ui` services when running in development to simplify host directory write access.

### File 2: scripts/setup_volumes.sh
#### Overview
- **Purpose**: Volume initialization.
- **Research Refinement**: Integrated `podman unshare` as the primary ownership management tool, ensuring compliance with rootless user namespace constraints.

### File 3: scripts/generate_api_docs.py
*(No changes needed to existing analysis)*

### File 4: scripts/setup-prod-secrets.sh
*(No changes needed to existing analysis)*

### File 5: scripts/setup_permissions.sh
*(No changes needed to existing analysis)*

## Cross-File Insights
- **Deployment Best Practice**: Rootless Podman deployment should prioritize the `:Z` volume flag to ensure the internal UID mapping is automatically handled by the runtime where possible.
- **Developer Experience**: Using `keep-id` allows developers to modify library files on the host and have the changes reflected in the container without permission collisions.

## Priority Recommendations
- **High**: Standardize on `keep-id` for development environments.
- **Medium**: Enforce `:Z` flag on all volume mounts in `podman-compose.yml`.

INTERVAL_17_COMPLETE