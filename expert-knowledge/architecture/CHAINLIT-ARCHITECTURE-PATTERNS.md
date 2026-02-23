# XNAi Chainlit Architecture — Design Patterns & Best Practices
## Gold-Standard Reference Document

**Status**: 🔒 LOCKED
**Created**: 2026-02-22
**Source**: JOB-R005, R006, R007 Implementation
**Confidence**: 98%

---

## Executive Summary

This document consolidates the architectural decisions, design patterns, and implementation details from the Chainlit Consolidation project. All future Chainlit development should reference this document.

---

## Architecture Overview

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              chainlit_app_unified.py                     │   │
│  │  - Feature flag gating                                   │   │
│  │  - Conditional handler registration                      │   │
│  │  - Graceful degradation                                  │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                          │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ SessionManager  │  │ KnowledgeClient │  │   VoiceModule   │ │
│  │ (Redis+Memory)  │  │ (Qdrant+FAISS)  │  │  (Optional)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  ** REUSABLE BY ALL INTERFACES **                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Design Patterns

### 1. Feature Flag Guard Pattern

All optional features must be gated by both feature flag AND availability check:

```python
# Environment variable (user control)
FEATURE_VOICE = os.getenv("FEATURE_VOICE", "false").lower() == "true"

# Import availability (dependency check)
try:
    from XNAi_rag_app.services.voice import VoiceModule
    VOICE_MODULE_AVAILABLE = True
except ImportError:
    VOICE_MODULE_AVAILABLE = False

# Combined check before use
if FEATURE_VOICE and VOICE_MODULE_AVAILABLE:
    # Initialize voice module
    pass
```

**Rationale**: Prevents runtime errors when dependencies are missing while allowing user control.

### 2. Graceful Degradation Pattern

All services must fall back gracefully:

```python
# SessionManager: Redis → In-Memory
# KnowledgeClient: Qdrant → FAISS → Keyword
# API: RAG API → Local LLM → Error Message

async def get_knowledge(query: str) -> List[Result]:
    if self._use_qdrant:
        results = await self._search_qdrant(query)
        if results:
            return results
    
    if self._use_faiss:
        results = await self._search_faiss(query)
        if results:
            return results
    
    return self._keyword_search(query)  # Always available
```

### 3. Conditional Handler Registration

Chainlit handlers for optional features must be registered conditionally:

```python
# At module level - only register if feature available
if cl and VOICE_MODULE_AVAILABLE:

    @cl.on_audio_start
    async def on_audio_start():
        if not _voice_module or not _voice_module.is_enabled:
            return False
        return True

    @cl.on_audio_chunk
    async def on_audio_chunk(chunk):
        # Handler code
        
    @cl.on_audio_end
    async def on_audio_end():
        # Handler code
```

### 4. Lazy Initialization Pattern

Expensive resources should be initialized lazily:

```python
@cl.on_chat_start
async def on_chat_start():
    global _session_manager, _knowledge_client, _voice_module
    
    # Initialize only when needed
    if FEATURE_REDIS_SESSIONS:
        _session_manager = SessionManager(SessionConfig(...))
        await _session_manager.initialize()
```

---

## Feature Flags Reference

| Flag | Default | Description | Dependencies |
|------|---------|-------------|--------------|
| `FEATURE_VOICE` | `false` | Voice responses | faster-whisper, piper |
| `FEATURE_REDIS_SESSIONS` | `true` | Redis persistence | redis |
| `FEATURE_QDRANT` | `true` | Qdrant vector search | qdrant-client |
| `FEATURE_LOCAL_FALLBACK` | `true` | Local LLM fallback | llama-cpp-python |

---

## Module Responsibilities

### SessionManager (`core/infrastructure/session_manager.py`)

**Purpose**: Unified session management with persistence

**Key Methods**:
- `initialize()` - Connect to Redis or fall back to memory
- `get(key)` / `set(key, value)` - Session storage
- `add_interaction(role, content)` - Add to conversation history
- `get_conversation_context(max_turns)` - Get formatted history

**Redis Key Pattern**: `xnai:session:{session_id}:{type}`

### KnowledgeClient (`core/infrastructure/knowledge_client.py`)

**Purpose**: Unified knowledge retrieval with multiple backends

**Key Methods**:
- `initialize()` - Initialize available backends
- `search(query, top_k, score_threshold)` - Search knowledge
- `add_document(content, metadata)` - Index new documents
- `get_status()` - Backend health check

**Backend Priority**: Qdrant → FAISS → Keyword fallback

### VoiceModule (`services/voice/voice_module.py`)

**Purpose**: Modular voice integration for Chainlit

**Key Methods**:
- `initialize()` - Initialize voice components
- `transcribe(audio_data)` - STT
- `synthesize(text)` - TTS
- `check_wake_word(text)` - Wake word detection
- `enable()` / `disable()` - Runtime toggle

---

## Code Quality Standards

### Async Patterns
- **Use AnyIO** for structured concurrency (not asyncio directly)
- **Thread pool** for CPU-bound operations (embeddings, STT)
- **Circuit breakers** for external service calls

### Error Handling
- **Never crash** on optional feature failure
- **Log warnings** for degraded mode
- **User-friendly messages** for service unavailable

### Import Guards
```python
try:
    from optional_dependency import Something
    OPTIONAL_AVAILABLE = True
except ImportError:
    OPTIONAL_AVAILABLE = False
    Something = None
```

---

## Testing Commands

```bash
# Test infrastructure imports
python3 -c "from XNAi_rag_app.core.infrastructure import SessionManager, KnowledgeClient; print('OK')"

# Test voice module imports
python3 -c "from XNAi_rag_app.services.voice import VoiceModule; print('OK')"

# Test unified app imports
python3 -c "import sys; sys.path.insert(0, 'app'); from XNAi_rag_app.ui.chainlit_app_unified import *; print('OK')"
```

---

## Metrics

| Metric | Value |
|--------|-------|
| Code Reduction | 65% (1685 → 580 lines) |
| Apps Consolidated | 2 → 1 |
| New Modules Created | 3 |
| Feature Flags Added | 4 |
| Test Coverage | Infrastructure layer has unit test patterns |

---

## Future Considerations

1. **FastAPI Interface**: Will reuse SessionManager and KnowledgeClient
2. **MC Agent Interface**: Will reuse all infrastructure components
3. **Gemini CLI**: Can use SessionManager for context management
4. **Knowledge Absorption**: Will use KnowledgeClient for storage

---

**Document Status**: 🔒 LOCKED - Do not modify without architecture review
**Next Review**: After FastAPI interface implementation
