# Stack Pain Points Remediation (v1.0.0)

## 1. Vikunja Redis Connectivity
- **Issue**: `dial tcp: address redis: missing port in address`
- **Fix**: Port must be embedded in `VIKUNJA_REDIS_HOST` (e.g., `redis:6379`).
- **Implementation**: Updated `docker-compose.yml` with `VIKUNJA_REDIS_HOST: "redis:6379"`.

## 2. Caddyfile Syntax
- **Issue**: Global headers and invalid `websocket` directives.
- **Fix**: Move headers to site blocks; remove `websocket` (Caddy auto-upgrades).
- **Implementation**: Created `Caddyfile.new` with site-block scoping and cleaned matchers.

## 3. Read-Only Filesystem Logging
- **Issue**: `[Errno 30] Read-only file system` when writing logs.
- **Fix**: Reconfigure Python logging to prioritize `stdout`/`stderr` and ensure log directories are created/checked for writability before handler attachment.
- **Implementation**: Patched `app/XNAi_rag_app/core/logging_config.py`.

## 4. Container Health Stability
- **Issue**: Containers marked "unhealthy" during slow bootstraps.
- **Fix**: Increase `start_period` to allow for migrations and service readiness.
- **Implementation**: Set `start_period: 90s` for Vikunja service.

## 5. Experimental Feature Leakage (AWQ)
- **Issue**: Metrics showing AWQ-related artifacts when unused.
- **Fix**: Explicitly disable AWQ flags in application config.
- **Implementation**: Added `awq_enabled = false` (conceptual) and sanitized `config.toml`.
