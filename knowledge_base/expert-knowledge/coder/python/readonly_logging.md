# EKB Gem: Read-Only Filesystem Logging (LOG_DIR)

## Issue
Service fails to start or logs errors like `[Errno 30] Read-only file system` when attempting to initialize file logging in a hardened container.

## Root Cause
Hardened containers (like the RAG API) often run with `read_only: true` for security. If the application attempts to create log files in a directory that isn't backed by a `tmpfs` or a writable volume, it will crash.

## Remediation
1. **Environment Support**: Update `logging_config.py` to respect a `LOG_DIR` environment variable.
2. **Container Orchestration**: Use `tmpfs` in `docker-compose.yml` to provide a writable log directory.

```python
# app/XNAi_rag_app/logging_config.py
log_dir = os.getenv("LOG_DIR", "./logs")
os.makedirs(log_dir, exist_ok=True)
```

```yaml
# docker-compose.yml
tmpfs:
  - /app/logs:size=100m,mode=1777
```

## Prevention
1. **Configuration Standard**: All Xoe-NovAi services must support externalizing log paths via environment variables.
2. **Infrastructure Audits**: Verify all `read_only` services have corresponding `tmpfs` mounts for `/tmp` and logs.
