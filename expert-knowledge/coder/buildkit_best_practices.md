---
category: coder
tags: [buildkit, podman, uv, cache-mounts, rootless]
impact_level: high
date_captured: 2026-01-24
related_components: [Dockerfile, Dockerfile.base, Makefile]
---

# BuildKit Mastery: Best Practices & Edge Cases

## ## Context
BuildKit cache mounts are the primary mechanism for accelerating Xoe-NovAi builds without introducing external dependencies like `apt-cacher-ng`.

## ## The Patterns

### 1. Unified uv + BuildKit Standard
**Standard**: All services MUST use `uv` for package installation with separate cache mounts for `pip` and `uv`.
```dockerfile
RUN --mount=type=cache,id=xnai-pip-cache,target=/root/.cache/pip,uid=1001,gid=1001 \
    --mount=type=cache,id=xnai-uv-cache,target=/root/.cache/uv,uid=1001,gid=1001 \
    uv pip install --system -r requirements.txt
```
- **Why**: `uv` is 10-100x faster than pip.
- **UID/GID Mapping**: Critical for rootless Podman (1001:1001).

### 2. The "Syntax Line 1" Rule
**Constraint**: The BuildKit syntax directive MUST be on the first line.
```dockerfile
# syntax=docker/dockerfile:1
```

### 3. Isolated Cache IDs
**Pattern**: Namespace IDs with `xnai-` to prevent corruption between different project builds.
```dockerfile
RUN --mount=type=cache,id=xnai-apt-cache,target=/var/cache/apt,uid=1001,gid=1001 ...
```

## ## Edge Cases & Troubleshooting

### Podman 5.x `sharing=locked` Conflict
- **Symptom**: `Error: invalid mount type "cache": sharing: invalid mount option`.
- **Root Cause**: Podman 5.x strict parsers don't recognize `locked` for certain drivers.
- **Fix**: Omit `sharing=locked`.

### The .gitignore Turn-Waster
- **Symptom**: Agent wastes 5+ turns searching for a file hidden by `.gitignore`.
- **Fix**: Use `run_shell_command("cat <path>")` immediately to bypass glob restrictions.

## ## Verification
- **Cold Build**: ~180s
- **Warm Build**: < 45s (Cache Hit)
- **Proof**: Run `make build` and verify `--> Using cache` in logs.

---
**Status**: 🟢 AUTHORITATIVE
**Reviewers**: Gemini CLI & Stack Researcher


