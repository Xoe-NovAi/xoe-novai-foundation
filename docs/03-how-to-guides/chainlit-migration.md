# Chainlit Migration Guide

> **Updated**: 2026-02-22
> **From**: Legacy dual-app setup (`chainlit_app.py` + `chainlit_app_voice.py`)
> **To**: Unified app (`chainlit_app_unified.py`)

---

## Overview

This guide helps you migrate from the legacy Chainlit setup to the new unified architecture.

### What Changed

| Before | After |
|--------|-------|
| 2 separate Chainlit apps | 1 unified app |
| 1,685 lines total | 580 lines (65% reduction) |
| Voice hardcoded | Voice optional (feature flag) |
| Duplicated infrastructure | Shared infrastructure layer |

---

## Quick Migration

### Step 1: Update Docker Compose

```yaml
# Before
chainlit:
  command: chainlit run ui/chainlit_app_voice.py --port 8001

# After
chainlit:
  command: chainlit run ui/chainlit_app_unified.py --port 8001
  environment:
    - FEATURE_VOICE=false  # Set to true to enable voice
```

### Step 2: Update Environment Variables

Add these to your `.env` or environment:

```bash
# Feature flags
FEATURE_VOICE=false           # Enable voice responses
FEATURE_REDIS_SESSIONS=true   # Redis session persistence
FEATURE_QDRANT=true           # Qdrant vector search
FEATURE_LOCAL_FALLBACK=true   # Local LLM fallback
```

### Step 3: Update Import Paths

```python
# Before
from XNAi_rag_app.ui.chainlit_app_voice import _session_manager

# After
from XNAi_rag_app.core.infrastructure import SessionManager, create_session_manager

# Create session manager
session = await create_session_manager()
```

---

## Feature Flag Migration

### Voice Features

| Old Behavior | New Behavior |
|-------------|--------------|
| Always on | `FEATURE_VOICE=false` by default |
| No toggle | `/voice on` and `/voice off` commands |
| Hardcoded config | `VoiceModuleConfig` class |

### Session Management

| Old Behavior | New Behavior |
|--------------|--------------|
| Redis only | Redis + in-memory fallback |
| Hardcoded keys | `xnai:session:{id}:{type}` pattern |
| No TTL | Configurable TTL (default 1 hour) |

### Knowledge Retrieval

| Old Behavior | New Behavior |
|--------------|--------------|
| FAISS only | Qdrant primary, FAISS fallback |
| No caching | Result caching with TTL |
| Direct import | `KnowledgeClient` abstraction |

---

## Command Changes

### New Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/stats` | Display session statistics |
| `/reset` | Clear conversation history |
| `/rag on/off` | Enable/disable RAG |
| `/status` | Check API connection |
| `/voice on/off` | Enable/disable voice responses |
| `/voice status` | Show voice module status |

### Removed Commands

| Old Command | Replacement |
|-------------|-------------|
| `/session clear` | `/reset` |

---

## Configuration Changes

### Session Config

```python
# Before (hardcoded)
redis_url = "redis://localhost:6379"

# After (configurable)
from XNAi_rag_app.core.infrastructure import SessionConfig

config = SessionConfig(
    session_ttl=3600,
    max_conversation_turns=100,
    redis_url="redis://localhost:6379",
)
```

### Knowledge Config

```python
# Before (hardcoded)
faiss_index = faiss.read_index("faiss_index/index.faiss")

# After (configurable)
from XNAi_rag_app.core.infrastructure import KnowledgeConfig

config = KnowledgeConfig(
    qdrant_url="http://localhost:6333",
    qdrant_collection="xnai_knowledge",
    default_top_k=5,
)
```

---

## Backup Files

Legacy files have been backed up:

```
chainlit_app_text_backup.py   # Old text-only app
chainlit_app_voice_backup.py  # Old voice app
```

These can be safely deleted after verifying the unified app works correctly.

---

## Troubleshooting

### Voice Not Working

1. Check feature flag: `FEATURE_VOICE=true`
2. Check voice module status: `/voice status`
3. Check logs for initialization errors

### Sessions Not Persisting

1. Check Redis connection: `redis-cli ping`
2. Check feature flag: `FEATURE_REDIS_SESSIONS=true`
3. Check logs for "in-memory fallback" warning

### Knowledge Search Failing

1. Check Qdrant connection: `curl http://localhost:6333/collections`
2. Check feature flag: `FEATURE_QDRANT=true`
3. Check logs for "FAISS fallback" warning

---

## Related Documentation

- [Voice Interface](../api/voice_interface.md)
- [Infrastructure Layer](../api/infrastructure-layer.md)
- [Voice Module](../api/voice_module.md)
