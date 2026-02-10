# Technical Context

## Hardware Specifications

### Host System
- **CPU**: AMD Ryzen 5700U (Zen 2, 8 Cores / 16 Threads)
- **Physical RAM**: 8 GB
- **Zram**: 12 GB (configured system-wide)
- **Total Available Memory**: ~20 GB (8GB physical + 12GB compressed swap)
- **Storage**: SSD (development environment)

### Memory Optimization
- **vm.swappiness**: 10 (prioritizes physical RAM, minimizes Zram thrashing)
- **Zram Algorithm**: lz4 (fast compression)
- **Optimization Goal**: Prioritize RAM for llama.cpp inference bursts

## Container Runtime

### Podman Configuration
- **Mode**: Rootless (user 1000, containers run as 1001:1001)
- **Version**: Latest available
- **Network**: xnai_network (bridge, external for Vikunja)
- **Storage**: Overlay with Z,U SELinux labels

### Resource Allocation Strategy
With 8GB physical + 12GB Zram:

| Service | Memory Limit | CPU Limit | Notes |
|---------|-------------|-----------|-------|
| RAG API | 4GB | 2.0 cores | Even cores (0,2,4,6,8,10,12,14) |
| Chainlit UI | 2GB | 1.0 cores | Odd cores (1,3,5,7,9,11,13,15) |
| PostgreSQL | 512MB shared_buffers | 0.5 cores | Tuned for <200MB footprint |
| Redis | 1GB maxmemory | 0.5 cores | LRU eviction, DB 5 for Vikunja (currently unused) |
| Vikunja | 512MB | 0.5 cores | All-in-one container, Redis integration disabled |
| Caddy | 128MB | 0.25 cores | Reverse proxy only |

**Total Reserved**: ~7.5GB (leaves headroom for inference spikes)

## Technology Stack

### Core Services
1. **Redis 7.4.1**: Cache, session storage, job queues
   - Allkeys-LRU eviction policy
   - DB isolation: 0-4 (Foundation), 5 (Vikunja)
   - Persistent Circuit Breaker state storage

2. **PostgreSQL 16**: Vikunja database
   - Alpine-based (minimal footprint)
   - shared_buffers: 512MB (optimized for Ryzen)

3. **Vikunja 0.24.1**: Task management
   - All-in-one image (API + Frontend)
   - Port 3456 internal only
   - Redis integration disabled (using database for caching/sessions)

4. **RAG API**: FastAPI backend
   - Qwen3-0.6B-Q6_K.gguf model
   - Hardware steering: Even cores only
   - Metrics via Caddy proxy at `/metrics`
   - **Persistent Circuit Breakers**: Redis-backed protection for models/API

5. **Chainlit UI**: Frontend
   - Voice-enabled interface
   - Hardware steering: Odd cores only
   - **Voice Degradation**: 4-level fallback system

6. **Caddy 2.8**: Reverse proxy
   - Single entry point (port 8000)
   - JSON access logs
   - Security headers (HSTS, CSP, etc.)

### Build Tools
- **BuildKit**: Enabled with inline cache
- **uv**: Python package manager (fast resolution)
- **Multi-stage builds**: Production-optimized images

## Security Configuration

### Container Hardening
- **User**: Non-root (1001:1001)
- **Capabilities**: DROP ALL, add only NET_BIND_SERVICE
- **Security Opt**: no-new-privileges
- **Read-only**: Where possible (tmpfs for writable dirs)
- **Secrets**: Environment variables (not Podman secrets - unreliable in rootless)
- **Volume Labels**: Standardized `:Z` labels (removed `:U` for SELinux compliance)

### Network Security
- **External Exposure**: Only Caddy on port 8000
- **Internal Communication**: xnai_network (bridge)
- **Service Discovery**: Container DNS names

### Data Protection
- **.env**: Gitignored, contains all secrets
- **No hardcoded passwords**: All via ${VAR} substitution
- **Redis**: Authenticated (${REDIS_PASSWORD})
- **PostgreSQL**: Authenticated (${VIKUNJA_DB_PASSWORD})

## Performance Optimizations

### Ryzen Zen 2 Tuning
```bash
OPENBLAS_CORETYPE=ZEN
OPENBLAS_NUM_THREADS=6
LLAMA_CPP_N_THREADS=6
LLAMA_CPP_USE_MLOCK=true
LLAMA_CPP_USE_MMAP=true
OMP_NUM_THREADS=1
```

### Container Optimization
- **cpuset**: Hardware steering (even/odd core separation)
- **tmpfs**: In-memory cache directories
- **Shared memory**: /dev/shm for model loading
- **Zram**: Compressed swap for memory overcommit

## Secret Management

### Environment Variables (.env)
All secrets stored in `.env` (gitignored):
- REDIS_PASSWORD
- VIKUNJA_DB_PASSWORD
- VIKUNJA_JWT_SECRET
- API_KEY

### Pattern
```yaml
environment:
  - REDIS_PASSWORD=${REDIS_PASSWORD}
  - VIKUNJA_DB_PASSWORD=${VIKUNJA_DB_PASSWORD}
```

**Rationale**: Podman secrets unreliable in rootless mode. Environment variables are sovereign simple and work reliably.

## Deployment Architecture

### Single Entry Point
```
Internet → Caddy (8000) → Services
                ├── /api/v1* → RAG API (8000)
                ├── / → Chainlit UI (8001)
                ├── /vikunja/* → Vikunja (3456)
                └── /metrics → RAG API metrics
```

### Startup Order
1. **Infrastructure**: Redis, PostgreSQL
2. **Application**: RAG API, Vikunja
3. **Frontend**: Chainlit UI
4. **Proxy**: Caddy (depends on all)

### Health Checks
- All services have health checks with generous start_period
- Caddy health: http://127.0.0.1:2019/
- RAG health: http://localhost:8000/health
- Vikunja health: http://localhost:3456/api/v1/info

## Monitoring

### Metrics Collection
- **RAG API**: Prometheus endpoint (via Caddy proxy)
- **Caddy**: JSON access logs
- **Podman**: `podman stats` for resource monitoring

### Log Aggregation
- **Caddy**: ./logs/caddy/access.log
- **RAG**: Structured JSON via stdout/stderr
- **Container stdout/stderr**: Podman logs (OpenTelemetry Trace Context injected)

## Known Limitations

### Development Environment
- Single-node deployment (no Kubernetes)
- Local Zram (not distributed)
- Rootless Podman (some features limited)

### Resource Constraints
- 8GB physical RAM requires careful allocation
- llama.cpp bursts can spike memory
- Zram compression overhead for swap

### Current Issues
1. **Vikunja Redis Connection**: Vikunja fails to connect to Redis with "address redis: missing port in address" error. Redis integration disabled as workaround.
2. **Vikunja Container Health**: Vikunja container marked as "unhealthy" in Podman. Healthcheck command may be failing.
3. **Caddy Configuration**: Caddyfile has unformatted input warning. Functionally operational but syntax could be improved.
4. **IAM Database Persistence**: IAM database is currently in `/app/data` (tmpfs). Needs persistent volume migration.

## Version Control

### Git Strategy
- **.env**: Gitignored (secrets)
- **Configs**: Committed (structure, not values)
- **EKB**: Expert Knowledge Base for decisions

### Committed Files
- docker-compose.yml
- docker-compose.vikunja.yml
- Caddyfile
- Dockerfile.*
- config.toml
- .env.example (template, no real values)

## Troubleshooting

### Common Issues
1. **Port 8000 conflict**: Caddy must be sole external binding
2. **Secret mounting**: Use env vars, not Podman secrets
3. **Database auth**: Nuke data dir if password mismatch
4. **Dependency hangs**: Generous start_period, cascading depends_on

### Debug Commands
```bash
# Check resource usage
podman stats

# View logs
podman logs xnai_vikunja

# Test endpoints
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/vikunja/api/v1/info

# Verify Zram
cat /proc/sys/vm/swappiness  # Should be 10
zramctl
```

## Future Enhancements

### Potential Additions
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Loki**: Log aggregation
- **AlertManager**: Alerting

### Scaling Considerations
- Redis: Single instance sufficient for current load
- PostgreSQL: Could use connection pooling (PgBouncer)
- RAG API: Horizontal scaling with load balancer

## References

- Grok Stack Production Lockdown v1.0.0 (EKB)
- Claude Vikunja Implementation Guides
- Podman Rootless Documentation
- Caddy Reverse Proxy Best Practices
- Research Request: grok-mc-research-request.md (for resolving current issues)