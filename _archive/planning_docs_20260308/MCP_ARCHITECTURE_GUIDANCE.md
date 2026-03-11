# MCP Server Architecture - Critical Review

**Date**: 2026-03-07  
**Status**: ⚠️ **Architecture Issue Identified**

---

## Current State

### Memory-Bank MCP Server Location
```
/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/
├── .venv_mcp/                          ❌ ISOLATED HOST VENV
│   └── bin/python3
│       └── /lib/python3.13/site-packages/
├── mcp-servers/memory-bank-mcp/        ✅ Server code (good location)
│   ├── server.py
│   ├── memory_bank_store.py
│   ├── memory_bank_fallback.py
│   └── run_server.sh (wrapper hack)
└── infra/docker/
    ├── docker-compose.yml              ✅ 20+ containerized services
    └── Dockerfile*                     ✅ 8 service Dockerfiles
```

### Current (Wrong) Architecture
```
Gemini CLI (Host)
  ↓ spawn process
.venv_mcp/bin/python3 (Host Python)
  ↓ runs server.py
Memory-Bank MCP Server (Host venv)
  ↗ connects to Redis (Container)
  ↗ accesses /storage/ (Host volume)
```

**Problems:**
1. ❌ **Two Python Environments**: Main stack + isolated .venv_mcp
2. ❌ **Duplicate Dependencies**: aiohttp, redis, toml, pydantic installed in both
3. ❌ **Not Containerized**: Only MCP server not in docker-compose.yml
4. ❌ **Network Isolation**: Spawned host process, not container network
5. ❌ **Backup/Recovery**: Not part of docker-compose backup strategy
6. ❌ **Resource Management**: No limits, no health checks, no logging
7. ❌ **Scaling**: Can't have multiple MCP server instances

---

## Correct Architecture

### What You Should Have
```
docker-compose.yml (21 services)
├── redis                          ✅ Exists
├── postgres                        ✅ Exists
├── rag                             ✅ Exists
├── ui                              ✅ Exists
├── ... (17 other services)
└── memory-bank-mcp                 ❌ MISSING (should be here!)
    ├── Image: omega-stack_memory-bank-mcp
    ├── Dockerfile: infra/docker/Dockerfile.memory-bank
    ├── Network: xnai_network
    ├── Volumes: /storage/
    └── Depends: redis
```

### Network Diagram
```
┌─────────────────────────────────────────────────────────┐
│ Docker Network: xnai_network                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐     ┌──────────────┐                 │
│  │ Redis:6379   │◄────┤ memory-bank- │                 │
│  │              │     │ mcp:stdio    │                 │
│  └──────────────┘     └──────────────┘                 │
│         ▲              /mcp/server/                    │
│         │          ├─ server.py                        │
│         │          ├─ memory_bank_store.py             │
│         │          └─ memory_bank_fallback.py          │
│         │                                               │
│  ┌──────────────┐                                      │
│  │ Storage      │◄──────────────────────────────────┐  │
│  │ (/storage/)  │                                   │  │
│  └──────────────┘                                   │  │
│         ▲                                          mount │
│         │                                               │
│  Other Services (RAG, UI, etc.)                        │
│                                                        │
└─────────────────────────────────────────────────────────┘
         ▲
         │ stdio transport
         │
    Gemini CLI (Host)
```

---

## Implementation Plan

### Step 1: Create Dockerfile
**File**: `/infra/docker/Dockerfile.memory-bank`

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY app/ /app/app/
COPY mcp-servers/memory-bank-mcp/ /app/mcp-server/

# Create requirements file for MCP server
RUN echo "aiohttp>=3.13.3\n\
redis>=7.3.0\n\
toml>=0.10.2\n\
pydantic>=2.0\n\
httpx>=0.28.1\n\
mcp>=0.1.0\n\
anyio>=4.0\n\
pyyaml>=6.0\n\
sqlalchemy>=2.0" > /app/requirements-mcp.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements-mcp.txt

# Run the server
WORKDIR /app/mcp-server
CMD ["python", "server.py"]
```

### Step 2: Update docker-compose.yml
Add to `/infra/docker/docker-compose.yml`:

```yaml
  memory-bank-mcp:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.memory-bank
    container_name: xnai_memory_bank_mcp
    environment:
      - PYTHONUNBUFFERED=1
      - REDIS_URL=redis://redis:6379
      - STORAGE_PATH=/storage
      - LOG_LEVEL=info
    volumes:
      - ./storage:/storage
      - ./app:/app/app:ro
      - ./mcp-servers/memory-bank-mcp:/app/mcp-server:ro
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - xnai_network
    restart: on-failure:3
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      - "com.xnai.component=memory-bank-mcp"
      - "com.xnai.requires=redis"
```

### Step 3: Update Gemini MCP Config
**File**: `/root/.config/gemini/settings.json` OR `.gemini/settings.json`

```json
{
  "mcpServers": {
    "memory-bank": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "--network=xnai_network",
        "--name=memory-bank-mcp-gemini",
        "omega-stack_memory-bank-mcp"
      ]
    }
  }
}
```

Or (better) use `docker exec` if container already running:

```json
{
  "mcpServers": {
    "memory-bank": {
      "command": "docker",
      "args": [
        "exec",
        "xnai_memory_bank_mcp",
        "python",
        "server.py"
      ]
    }
  }
}
```

### Step 4: Clean Up Host venv
```bash
# Once docker service is verified working:
rm -rf .venv_mcp
rm mcp-servers/memory-bank-mcp/run_server.sh

# Update scripts to not reference .venv_mcp
```

---

## Why This Matters

### Development
- ✅ Same environment as production
- ✅ Easy to test changes (rebuild container)
- ✅ Dependencies tracked in Dockerfile
- ✅ Reproducible builds

### Operations
- ✅ Managed by docker-compose
- ✅ Automatic restart on failure
- ✅ Resource limits and isolation
- ✅ Proper logging and monitoring
- ✅ Health checks built-in

### Architecture
- ✅ All services in one compose file
- ✅ Proper networking isolation
- ✅ Shared volumes for data
- ✅ Single configuration source
- ✅ Compatible with backup/restore

---

## Other MCP Servers

Your stack has 7 MCP servers defined in `/mcp-servers/`:

1. **memory-bank-mcp** ← We're fixing this
2. **xnai-agentbus** - Should be containerized
3. **xnai-memory** - Should be containerized
4. **xnai-rag** - Might already be (check RAG service)
5. **xnai-sambanova** - Should be containerized
6. **xnai-stats-mcp** - Should be containerized
7. **xnai-vikunja** - Might be (Vikunja is containerized)

**Recommendation**: Audit all 7 and containerize any that aren't already.

---

## Decision Point

### Option A: Quick Fix (Keep venv for now)
- ❌ Leave memory-bank in .venv_mcp
- ❌ Accept technical debt
- ✅ Focus on getting Gemini API key working
- ⏰ Time: 5 minutes
- 💾 Files: 0

### Option B: Do It Right (Containerize)
- ✅ Create Dockerfile.memory-bank
- ✅ Update docker-compose.yml
- ✅ Update Gemini config
- ✅ Proper architecture
- ⏰ Time: 30 minutes
- 💾 Files: 3-4

### Option C: Audit First (Then Decide)
- ✅ Check status of all 7 MCP servers
- ✅ See which are already containerized
- ✅ Plan comprehensive MCP modernization
- ⏰ Time: 20 minutes
- 💾 Files: 0

---

## Recommendation

**Do Option B + Document Option C Plan**

This is the right time to containerize memory-bank because:
1. You're already aware of the architectural issue
2. Docker stack is already running (redis, postgres, etc.)
3. Won't be harder later, only more technical debt
4. Sets precedent for other MCP servers

Once memory-bank is containerized, you'll have a template for the other 6.

---

## Next Steps

Tell me which option you want and I'll implement it.

Questions for you:
1. Should we containerize memory-bank now?
2. What Gemini API key issue - should we fix that first?
3. Should we audit all 7 MCP servers for current state?

