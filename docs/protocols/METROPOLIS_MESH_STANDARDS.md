# 🏙️ Metropolis Mesh Standards & Strategic Protocols

**Version**: 1.0.0-HARDENED
**Status**: ACTIVE
**Authority**: Gemini General / Omega Stack PM

## 🛡️ Core Mandates

### 1. Networking & Port Mapping
- **Caddy First**: All external traffic MUST flow through the Caddy gateway (Port 8000).
- **Service Isolation**: Direct port exposure in `docker-compose.yml` is FORBIDDEN for internal mesh services. Use the internal network aliases.
- **Port Conflict Guard**: Ensure unique `METRICS_PORT` for every service sharing the same base image (e.g., RAG API vs. Llama Server).
- **Redis Protocol**: Use `rediss://` (TLS) for all connections. In the internal mesh, set `ssl_cert_reqs='none'` to bypass hostname verification while maintaining encryption.

### 2. Identity & Permissions
- **UID/GID 1000**: All services must operate as UID 1000 (appuser) to maintain host compatibility and avoid permission drift.
- **Ownership Recovery**: If a rootless container shifts permissions, use the "Alpine Reclaim" pattern:
  `podman run --rm -v ./path:/mnt:z alpine chown -R 1000:1000 /mnt`

### 3. Resource Management (Ryzen 5700U / 6.6GB RAM)
- **Log Capping**: Every service MUST have log limits: `max-size: "10m"`, `max-file: "3"`.
- **Memory Guard**: LLM services MUST disable `mlock` (`LLAMA_CPP_USE_MLOCK=false`) to avoid rootless ulimit crashes.
- **Tiered Startup**: Core infrastructure (Redis, Postgres, Consul) MUST be healthy before launching LLMs or RAG services.

### 4. Build Optimization & Persistence
- **Wheel Caching**: Use BuildKit cache mounts (`--mount=type=cache,target=/root/.cache/uv`) for all Python builds.
- **HF Authentication**: Use `HF_TOKEN` for all HuggingFace downloads to enable caching and avoid rate limits.
- **Persistent Cache**: Map `/home/appuser/.cache/huggingface` to a named volume (`xnai_huggingface_cache`) to prevent redundant downloads.

### 5. OpenTelemetry & Observability
- **OTLP Endpoint**: Default OTLP collector is `http://localhost:4317` (Jaeger).
- **Metric Standardization**: Use Prometheus format; all endpoints should expose `/metrics`.

## 📜 Procedures

### Adding a New Model
1. Download via authenticated HF curl.
2. Verify SHA256 against source.
3. Place in `./infra/docker/models/` or appropriate partition.
4. Register in `models/registry.json`.
5. Update `docker-compose.yml` with the new path.

### Handling "Container Already in Use"
1. `podman pod rm -f -a`
2. `podman system prune -f`
3. Verify `ss -tulpn` for hung ports.
