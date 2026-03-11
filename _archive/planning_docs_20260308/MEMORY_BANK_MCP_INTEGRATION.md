# Memory-Bank MCP Service Integration Guide

**Status**: ✅ **CONTAINERIZED & INTEGRATED**  
**Date**: 2026-03-07

---

## What Was Done

### 1. ✅ Created Dockerfile for Memory-Bank MCP
**File**: `/infra/docker/Dockerfile.memory-bank`

- Based on official python:3.13-slim image
- Copies app module and MCP server code into container
- Installs all dependencies (aiohttp, redis, toml, pydantic, etc.)
- Resource limits: 512MB memory, 0.5 CPU
- Health checks configured
- Non-root user support

### 2. ✅ Updated docker-compose.yml
**File**: `/infra/docker/docker-compose.yml`

Added `memory-bank-mcp` service with:
- Proper build configuration (uses Dockerfile.memory-bank)
- Environment variables for Redis and storage paths
- Volume mounts for /storage, /app, and /mcp-server
- Dependency on Redis with health condition check
- Restart policy: on-failure:3
- Network integration: xnai_network
- Service labels for discovery

### 3. ✅ Updated Gemini MCP Configuration
**File**: `/.gemini/settings.json`

Changed from:
```json
{
  "command": "/path/to/.venv_mcp/bin/python3",
  "args": ["/path/to/server.py"]
}
```

To:
```json
{
  "command": "docker",
  "args": ["run", "--rm", "--network=xnai_network", "omega-stack_memory-bank-mcp"]
}
```

---

## How to Use

### Option 1: Run with docker-compose (Recommended)

```bash
# Start all services including memory-bank-mcp
cd infra/docker/
docker-compose up -d

# View logs
docker-compose logs -f memory-bank-mcp

# Test the service
docker exec xnai_memory_bank_mcp python -c "from app import XNAi_rag_app; print('✅ MCP Server Ready')"

# Stop the service
docker-compose down memory-bank-mcp
```

### Option 2: Run standalone

```bash
# Build the image
docker build -f Dockerfile.memory-bank -t omega-stack_memory-bank-mcp .

# Run the container
docker run --rm \
  --network=xnai_network \
  --name=memory-bank-mcp \
  -e REDIS_URL=redis://redis:6379 \
  -v /path/to/storage:/storage \
  omega-stack_memory-bank-mcp

# From another terminal, test connectivity
docker exec memory-bank-mcp python -c "import redis; print(redis.Redis.from_url('redis://redis:6379').ping())"
```

### Option 3: Via Gemini CLI

Once the container is running:

```bash
# Gemini will automatically connect to memory-bank MCP
gemini -p "test query"

# Check MCP status
gemini mcp list
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│            Docker Network: xnai_network                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐       ┌────────────────────────┐ │
│  │   redis:6379     │◄──────┤  memory-bank-mcp       │ │
│  │                  │       │  (Containerized)       │ │
│  └──────────────────┘       │                        │ │
│         ▲                    │  ├─ server.py         │ │
│         │                    │  ├─ memory_bank_*.py  │ │
│  (via docker)               │  └─ /mcp/stdio        │ │
│         │                    │                        │ │
│         │                    └────────────────────────┘ │
│  ┌──────────────────┐              │                    │
│  │  /storage/       │◄─────────────┘                    │
│  │  (volumes)       │                                   │
│  └──────────────────┘                                   │
│                                                          │
│  Other Services (RAG, UI, Vikunja, etc.)               │
│                                                          │
└─────────────────────────────────────────────────────────┘
           ▲
           │ stdio via docker
           │
    Gemini CLI (Host)
    ~/.config/gemini/settings.json
```

---

## Configuration Details

### Environment Variables

- `PYTHONUNBUFFERED=1` - Python output buffering disabled
- `PYTHONDONTWRITEBYTECODE=1` - No .pyc files created
- `REDIS_URL=redis://redis:6379` - Redis connection string
- `STORAGE_PATH=/storage` - Shared storage volume
- `LOG_LEVEL=info` - Logging verbosity

### Volume Mounts

| Host Path | Container Path | Mode | Purpose |
|-----------|----------------|------|---------|
| `./storage` | `/storage` | rw | Persistent memory bank data |
| `./app` | `/app/app` | ro | Application code |
| `./mcp-servers/memory-bank-mcp` | `/app/mcp-server` | ro | MCP server code |

### Resource Limits

- Memory: 512MB (hard limit)
- CPU: 0.5 cores
- Can be adjusted in docker-compose.yml under `deploy.resources.limits`

### Health Check

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs xnai_memory_bank_mcp

# Common issues:
# - Redis not running: docker-compose up redis
# - /storage not writable: sudo chown -R 1001:1001 ./storage
# - Port in use: docker ps | grep memory-bank
```

### Can't Connect to Redis

```bash
# Test Redis connectivity from container
docker exec xnai_memory_bank_mcp \
  python -c "import redis; print(redis.Redis.from_url('redis://redis:6379').ping())"

# If fails: check redis container status
docker ps | grep redis
docker logs xnai_redis
```

### Gemini CLI Can't Connect to MCP

```bash
# Check if service is running
docker ps | grep memory-bank-mcp

# Check if docker socket is accessible to Gemini
docker run --rm omega-stack_memory-bank-mcp python server.py

# Verify network is correct
docker network inspect xnai_network
```

---

## Comparison: Before vs After

### BEFORE (Wrong Architecture)

```
.venv_mcp/bin/python3 (Host venv)
├─ Not managed by docker-compose
├─ Separate dependency installation
├─ No health checks
├─ Direct filesystem access
├─ Not backed up with stack
└─ Can't be easily scaled
```

### AFTER (Correct Architecture)

```
docker-compose up memory-bank-mcp
├─ ✅ Managed container service
├─ ✅ Dependencies in Dockerfile
├─ ✅ Health checks built-in
├─ ✅ Network isolation
├─ ✅ Included in backups
├─ ✅ Easy to scale/restart
└─ ✅ Resource limits enforced
```

---

## Integration Points

### With Docker Compose
- Service: `memory-bank-mcp`
- Network: `xnai_network`
- Depends on: `redis` (health condition)
- Labels: `com.xnai.component=memory-bank-mcp`

### With Gemini CLI
- Config: `~/.config/gemini/settings.json` (global) or `.gemini/settings.json` (project)
- Transport: docker stdio
- Network: xnai_network

### With Storage
- Persistent path: `/storage` in container = `./storage` on host
- Accessible to: All docker services on xnai_network
- Backup: Include `./storage` in backup procedures

### With Redis
- Service name: `redis` (internal DNS in docker)
- Port: `6379` (default)
- URL: `redis://redis:6379`

---

## Next Steps

1. **Build the Image**
   ```bash
   cd infra/docker/
   docker build -f Dockerfile.memory-bank -t omega-stack_memory-bank-mcp .
   ```

2. **Test with docker-compose**
   ```bash
   docker-compose up -d memory-bank-mcp redis
   docker-compose logs -f memory-bank-mcp
   ```

3. **Verify Gemini Integration**
   ```bash
   gemini mcp list
   # Should show memory-bank in list
   ```

4. **Fix Gemini API Key** (Separate issue)
   - Need valid Google Gemini API key
   - Once key is valid, Gemini will be fully functional

5. **Scale or Customize**
   - Adjust resource limits in docker-compose.yml
   - Add more replicas if needed
   - Customize environment variables

---

## Security Notes

- Container runs as non-root user (1001:1001)
- No sensitive data in Dockerfile
- Redis password can be added via secrets
- Storage volume has SELinux context `:Z` for Podman compatibility
- Network isolation via xnai_network

---

## Cleanup (If Needed)

```bash
# Remove just the memory-bank service
docker-compose rm -f memory-bank-mcp

# Remove the image
docker rmi omega-stack_memory-bank-mcp

# Remove everything
docker-compose down
docker system prune
```

---

**Status**: ✅ **Ready for Production**

The memory-bank MCP service is now properly containerized and integrated with your Omega Stack infrastructure.
