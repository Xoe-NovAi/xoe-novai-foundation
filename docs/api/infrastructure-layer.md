# Infrastructure Layer API Reference

> **Generated**: 2026-02-22  
> **Source**: `app/XNAi_rag_app/core/infrastructure/`  
> **Version**: 0.1.0

---

## Overview

The Infrastructure Layer provides reusable components for session management and knowledge retrieval. These components are used by all XNAi interfaces (Chainlit UI, voice interface, MC agent interfaces).

### Design Principles

1. **Graceful Degradation**: All services fall back gracefully when dependencies unavailable
2. **Feature Flags**: All components controllable via environment variables
3. **Torch-Free**: No PyTorch dependencies
4. **Async-First**: Uses AnyIO for structured concurrency

---

## Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `SessionManager` | Session persistence | `core/infrastructure/session_manager.py` |
| `KnowledgeClient` | Knowledge retrieval | `core/infrastructure/knowledge_client.py` |

---

## SessionManager

Unified session management with Redis persistence and in-memory fallback.

### Features

- Redis persistence with automatic fallback to in-memory
- Conversation history management with bounded storage
- Session TTL support
- Graceful degradation when Redis unavailable

### Configuration

```python
from XNAi_rag_app.core.infrastructure import SessionConfig

config = SessionConfig(
    session_ttl=3600,           # 1 hour
    max_conversation_turns=100, # Max history size
    redis_url="redis://localhost:6379",
    redis_host="redis",
    redis_port=6379,
    redis_password=None,
    connection_timeout=5,
)
```

### Usage

```python
from XNAi_rag_app.core.infrastructure import (
    SessionManager,
    SessionConfig,
    create_session_manager,
)

# Create session manager
config = SessionConfig(redis_url="redis://localhost:6379")
session = SessionManager(config)
await session.initialize()

# Store data
await session.set("user_id", "12345")
await session.set("preferences", {"theme": "dark"})

# Retrieve data
user_id = await session.get("user_id")

# Add conversation turns
await session.add_interaction("user", "Hello!")
await session.add_interaction("assistant", "Hi there!")

# Get conversation context for LLM
context = await session.get_conversation_context(max_turns=5)
# Returns: "user: Hello!\nassistant: Hi there!"

# Get session stats
stats = session.get_stats()
# Returns: session_id, message_count, etc.

# Clear session
await session.clear_session()

# Close connection
await session.close()
```

### Factory Function

```python
from XNAi_rag_app.core.infrastructure import create_session_manager

# Create and initialize in one step
session = await create_session_manager(
    session_id="user_123",
    redis_url="redis://localhost:6379"
)
```

### Redis Key Patterns

| Pattern | Purpose |
|---------|---------|
| `xnai:session:{id}:data` | Session data hash |
| `xnai:session:{id}:conversation` | Conversation history list |

### Feature Flag

```bash
FEATURE_REDIS_SESSIONS=true  # Enable Redis (default)
FEATURE_REDIS_SESSIONS=false # Force in-memory
```

---

## KnowledgeClient

Unified knowledge retrieval with multiple backend support.

### Features

- Qdrant (remote vector DB) with FAISS (local) fallback
- Multiple embedding strategies (fastembed, sentence-transformers)
- Graceful degradation when backends unavailable
- Caching layer for frequently accessed vectors

### Backend Priority

```
Qdrant (remote, persistent) → FAISS (local) → Keyword fallback
```

### Configuration

```python
from XNAi_rag_app.core.infrastructure import KnowledgeConfig

config = KnowledgeConfig(
    # Qdrant settings
    qdrant_url="http://localhost:6333",
    qdrant_api_key=None,
    qdrant_collection="xnai_knowledge",
    qdrant_vector_size=384,  # all-MiniLM-L6-v2
    
    # FAISS settings
    faiss_index_path=None,  # Auto-detect
    
    # Search settings
    default_top_k=5,
    score_threshold=0.7,
    
    # Embedding settings
    embedding_model="all-MiniLM-L6-v2",
    embedding_dimension=384,
    
    # Cache settings
    enable_cache=True,
    cache_ttl=3600,
)
```

### Usage

```python
from XNAi_rag_app.core.infrastructure import (
    KnowledgeClient,
    KnowledgeConfig,
    SearchResult,
    create_knowledge_client,
)

# Create knowledge client
config = KnowledgeConfig(qdrant_url="http://localhost:6333")
knowledge = KnowledgeClient(config)
await knowledge.initialize()

# Search for relevant documents
results = await knowledge.search(
    query="What is XNAi Foundation?",
    top_k=5,
    score_threshold=0.7,
)

for result in results:
    print(f"Score: {result.score:.2f}")
    print(f"Content: {result.content[:100]}...")
    print(f"Source: {result.source}")

# Add document to knowledge base
success = await knowledge.add_document(
    content="XNAi Foundation is a sovereign AI system...",
    metadata={"source": "docs", "type": "explanation"},
    doc_id="doc_001",
)

# Get client status
status = await knowledge.get_status()
# Returns: qdrant_available, faiss_available, embeddings_available

# Clear cache
knowledge.clear_cache()

# Close connections
await knowledge.close()
```

### Factory Function

```python
from XNAi_rag_app.core.infrastructure import create_knowledge_client

# Create and initialize in one step
knowledge = await create_knowledge_client(
    qdrant_url="http://localhost:6333"
)
```

### SearchResult

```python
@dataclass
class SearchResult:
    id: str              # Document ID
    content: str         # Document content
    score: float         # Relevance score (0-1)
    source: str          # Backend source (qdrant/faiss/keyword)
    metadata: dict       # Additional metadata
```

### Feature Flag

```bash
FEATURE_QDRANT=true  # Enable Qdrant (default)
FEATURE_QDRANT=false # Force FAISS only
```

---

## Integration Examples

### Chainlit Integration

```python
import chainlit as cl
from XNAi_rag_app.core.infrastructure import (
    SessionManager,
    KnowledgeClient,
)

session_manager: SessionManager = None
knowledge_client: KnowledgeClient = None

@cl.on_chat_start
async def on_chat_start():
    global session_manager, knowledge_client
    
    # Initialize infrastructure
    session_manager = SessionManager()
    await session_manager.initialize()
    
    knowledge_client = KnowledgeClient()
    await knowledge_client.initialize()
    
    cl.user_session.set("session_manager", session_manager)
    cl.user_session.set("knowledge_client", knowledge_client)

@cl.on_message
async def on_message(message: cl.Message):
    session = cl.user_session.get("session_manager")
    knowledge = cl.user_session.get("knowledge_client")
    
    # Get context
    context = await session.get_conversation_context()
    
    # Search knowledge
    results = await knowledge.search(message.content)
    
    # Process and respond...
    
    # Save interaction
    await session.add_interaction("user", message.content)
    await session.add_interaction("assistant", response)
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from XNAi_rag_app.core.infrastructure import (
    SessionManager,
    KnowledgeClient,
    create_session_manager,
    create_knowledge_client,
)

app = FastAPI()

# Global instances
_session_manager: SessionManager = None
_knowledge_client: KnowledgeClient = None

@app.on_event("startup")
async def startup():
    global _session_manager, _knowledge_client
    _session_manager = await create_session_manager()
    _knowledge_client = await create_knowledge_client()

@app.on_event("shutdown")
async def shutdown():
    await _session_manager.close()
    await _knowledge_client.close()

@app.get("/search")
async def search(q: str):
    results = await _knowledge_client.search(q)
    return {"results": [r.to_dict() for r in results]}
```

---

## Error Handling

### Graceful Degradation

All components fall back gracefully:

```python
# SessionManager: Redis → In-Memory
session = SessionManager(config)
await session.initialize()
# If Redis unavailable, automatically uses in-memory

# KnowledgeClient: Qdrant → FAISS → Keyword
knowledge = KnowledgeClient(config)
await knowledge.initialize()
# Falls back through backends as needed
```

### Checking Availability

```python
# Check session manager
if session_manager.is_connected:
    print("Using Redis")
else:
    print("Using in-memory fallback")

# Check knowledge client
status = await knowledge_client.get_status()
if status["qdrant"]["available"]:
    print("Qdrant available")
elif status["faiss"]["available"]:
    print("FAISS available")
else:
    print("Keyword search only")
```

---

## Testing

### Unit Tests

```python
import pytest
from XNAi_rag_app.core.infrastructure import SessionManager, SessionConfig

@pytest.mark.asyncio
async def test_session_manager():
    config = SessionConfig(redis_url=None)  # Force in-memory
    session = SessionManager(config)
    await session.initialize()
    
    await session.set("key", "value")
    result = await session.get("key")
    
    assert result == "value"
    
    await session.close()
```

### Import Test

```bash
python3 -c "from XNAi_rag_app.core.infrastructure import SessionManager, KnowledgeClient; print('OK')"
```

---

## Related Documentation

- [Voice Interface](voice_interface.md)
- [Voice Module](voice_module.md)
- [Architecture Patterns](../../expert-knowledge/architecture/CHAINLIT-ARCHITECTURE-PATTERNS.md)
