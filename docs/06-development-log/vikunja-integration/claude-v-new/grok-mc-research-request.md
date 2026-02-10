## Research Request: Resolve Stack Pain Points and Blockers

### Current Stack Status
- **RAG API**: Running on port 8000 (accessible via Caddy at /api/v1)
- **Chainlit UI**: Running on port 8001 (accessible at /)
- **Vikunja**: Running on port 3456 (accessible via Caddy at /vikunja) - Redis integration disabled due to configuration issues
- **MkDocs**: Running on port 8008
- **Prometheus Metrics**: Running on port 8002
- **Caddy**: Running on port 8000 (reverse proxy)

### Identified Blockers and Issues

#### 1. Vikunja Redis Connection Failure
- **Issue**: Vikunja fails to connect to Redis with "address redis: missing port in address"
- **Root Cause**: Environment variables VIKUNJA_REDIS_PORT and VIKUNJA_REDIS_URL not being properly parsed by Vikunja container
- **Impact**: Redis integration disabled, using database for caching instead
- **Research Needed**: How Vikunja parses Redis configuration in Docker environment

#### 2. Caddy Configuration Issues
- **Issue**: Caddyfile validation errors: unrecognized directives, syntax issues
- **Root Cause**: Incorrect use of `header` as global option and `websocket` subdirective in reverse_proxy
- **Impact**: Caddy container was failing to start
- **Research Needed**: Caddyfile syntax best practices, reverse proxy configuration for WebSockets

#### 3. RAG API Log Directory Permissions
- **Issue**: Failed to setup file handler: [Errno 30] Read-only file system
- **Root Cause**: Container filesystem permissions
- **Impact**: Logs only available via console output
- **Research Needed**: Containerized Python application logging best practices

#### 4. Vikunja Container Health Status
- **Issue**: xnai_vikunja container marked as "unhealthy" in podman ps
- **Root Cause**: Healthcheck command failing or container not responding correctly
- **Impact**: Container status monitoring inaccurate
- **Research Needed**: Docker container healthcheck best practices for Vikunja

#### 5. AWQ Feature Status
- **Issue**: AWQ is enabled but flagged as "experimental, untested feature"
- **Root Cause**: Prometheus metrics showing AWQ-related metrics
- **Impact**: Potential stability issues
- **Research Needed**: How to disable AWQ feature completely

### Required Research Deliverables

1. **Vikunja Configuration Guide**: How to properly configure Redis connection in Vikunja container
2. **Caddyfile Best Practices**: Comprehensive guide for writing valid Caddyfile configurations with reverse proxy for WebSocket applications
3. **Container Logging Strategy**: How to handle logging in read-only container environments
4. **Vikunja Healthcheck Fix**: Proper healthcheck configuration for Vikunja container
5. **AWQ Feature Control**: How to disable AWQ entirely in the stack

### Scope of Research
- Current stack version: Sovereign Foundation v0.1.0-alpha
- Target containers: xnai_vikunja, xnai_rag_api, xnai_caddy
- Research should include:
  - Working configuration examples
  - Best practices for container deployment
  - Troubleshooting steps for common issues

### Timeline
- Research phase: 24 hours
- Implementation phase: 48 hours
- Testing phase: 24 hours
- Final delivery: 3 days