# Production Deployment Guide

This guide covers production deployment of Xoe-NovAi RAG stack using Podman/Docker.

## Quick Start

```bash
# Clone repository
git clone https://github.com/arcana-novai/xnai-foundation.git
cd xnai-foundation

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start production stack
podman-compose -f docker-compose.production.yml up -d
```

## Prerequisites

### System Requirements
- **CPU**: 4+ cores (AMD Ryzen 5700U or better)
- **RAM**: 6GB minimum, 8GB recommended
- **Storage**: 10GB+ for data volumes
- **OS**: Linux (Fedora/Ubuntu recommended) or macOS

### Software Requirements
- **Podman**: 4.0+ (or Docker 24.0+)
- **podman-compose**: 1.0+ (or docker-compose v2)
- **Git**: 2.30+

## Architecture Overview

```
                    ┌─────────────┐
                    │   Caddy     │ :80/:443
                    │ (Reverse    │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
┌───┴───┐            ┌─────┴─────┐          ┌─────┴─────┐
│ Redis │            │  RAG API  │          │  Consul   │
│ :6379 │            │   :8000   │          │   :8500   │
└───────┘            └─────┬─────┘          └───────────┘
                           │
                    ┌──────┴──────┐
                    │   Qdrant    │
                    │   :6333     │
                    └─────────────┘
```

## Container Configuration

### Building Images

```bash
# Build production image
podman build -f containers/Containerfile.production -t xnai-rag:production .

# Build with specific version
podman build --build-arg BUILDVERSION=0.2.0 -f containers/Containerfile.production -t xnai-rag:0.2.0 .
```

### Running Services

```bash
# Start all services
podman-compose -f docker-compose.production.yml up -d

# Check service status
podman-compose -f docker-compose.production.yml ps

# View logs
podman-compose -f docker-compose.production.yml logs -f rag-api
```

## Health Endpoints

| Service | Endpoint | Description |
|---------|----------|-------------|
| RAG API | `/health` | Overall system health |
| RAG API | `/metrics` | Prometheus metrics |
| Qdrant | `:6333/health` | Vector DB health |
| Redis | `redis-cli ping` | Cache health |
| Consul | `/v1/status/leader` | Service discovery |

## Environment Variables

### Required Variables

```bash
# .env file
REDIS_PASSWORD=your-secure-password
LOG_LEVEL=INFO
ENVIRONMENT=production
VERSION=0.2.0
```

### Optional Variables

```bash
# Performance tuning
WORKERS=4
MAX_REQUESTS=1000
TIMEOUT=60

# Resource limits
MEMORY_LIMIT=2G
CPU_LIMIT=2
```

## Security Considerations

### Non-Root Containers
All containers run as non-root user (`xnai:1000`).

### Network Isolation
Services communicate via isolated bridge network.

### Secrets Management
- Use `.env` file for secrets (not committed to git)
- Consider HashiCorp Vault for enterprise deployments

### TLS/SSL
Caddy automatically manages HTTPS certificates via Let's Encrypt.

## Monitoring

### Prometheus Metrics
```bash
# Scrape endpoint
curl http://localhost:8000/metrics
```

### Log Aggregation
Logs are written to `/app/logs` and can be forwarded to:
- Loki
- Elasticsearch
- CloudWatch Logs

## Scaling

### Horizontal Scaling

```bash
# Scale RAG API to 3 instances
podman-compose -f docker-compose.production.yml up -d --scale rag-api=3
```

### Load Balancing
Caddy automatically load balances between API instances.

## Backup & Recovery

### Volume Backup

```bash
# Backup Qdrant data
podman run --rm -v xnai-foundation_qdrant-data:/data -v $(pwd):/backup alpine tar czf /backup/qdrant-backup.tar.gz -C /data .

# Backup Redis data
podman run --rm -v xnai-foundation_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .
```

### Recovery

```bash
# Restore Qdrant data
podman run --rm -v xnai-foundation_qdrant-data:/data -v $(pwd):/backup alpine tar xzf /backup/qdrant-backup.tar.gz -C /data
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   podman unshare chown -R 1000:1000 ./data
   ```

2. **Memory Issues**
   ```bash
   # Check memory usage
   podman stats
   ```

3. **Network Issues**
   ```bash
   # Inspect network
   podman network inspect xnai-network
   ```

### Log Analysis

```bash
# View recent errors
podman-compose logs rag-api 2>&1 | grep -i error

# Follow logs in real-time
podman-compose logs -f --tail=100 rag-api
```

## Maintenance

### Updates

```bash
# Pull latest images
podman-compose -f docker-compose.production.yml pull

# Recreate containers
podman-compose -f docker-compose.production.yml up -d --force-recreate
```

### Cleanup

```bash
# Remove unused images
podman image prune -f

# Remove unused volumes (CAUTION)
podman volume prune -f
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/arcana-novai/xnai-foundation/issues
- Documentation: https://arcana-novai.github.io/xnai-foundation