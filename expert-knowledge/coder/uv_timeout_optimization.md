# EKB Gem: Build-time Dependency Timeouts (UV_HTTP_TIMEOUT)

## Issue
Docker/Podman builds hang indefinitely or fail during `uv pip install` when fetching large ML dependencies (e.g., `ctranslate2`, `llama-cpp-python`).

## Root Cause
Default HTTP timeouts in `uv` and `pip` may be too aggressive for large wheel downloads on restricted or high-latency networks. In BuildKit environments, this can lead to "silent hangs" where the layer processing appears to stop without providing an error message.

## Remediation
Inject `UV_HTTP_TIMEOUT` and `PIP_DEFAULT_TIMEOUT` environment variables into the build process or Dockerfile.

```dockerfile
# Global timeout for large ML wheels
ENV UV_HTTP_TIMEOUT=120 \
    PIP_DEFAULT_TIMEOUT=120
```

## Prevention
1. **Makefile Standards**: Include these variables in the `build` target.
2. **Pre-caching**: Use a local `wheelhouse/` to avoid network fetches during the core build phase.