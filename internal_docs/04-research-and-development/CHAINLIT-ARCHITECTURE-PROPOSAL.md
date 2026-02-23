# Chainlit Architecture Proposal
## Unified Text + Voice Interface with Modular Components

**Date**: 2026-02-22  
**Author**: Cline (Claude Sonnet 4.6)  
**Status**: RESEARCH COMPLETE - Awaiting User Approval

---

## Executive Summary

After analyzing the current codebase and strategic roadmap, this proposal recommends:

1. **Single Chainlit App** with modular voice integration
2. **Shared Infrastructure Layer** for Redis/FAISS/Qdrant connectivity
3. **Feature Flag Architecture** for voice capabilities
4. **De-coupled Voice Services** for maintainability

---

## Current State Analysis

### File Inventory

| File | Lines | Purpose | Issues |
|------|-------|---------|--------|
| `ui/chainlit_app.py` | 721 | Text-only Chainlit UI | Missing Redis/FAISS/Qdrant |
| `ui/chainlit_app_voice.py` | 964 | Voice-enabled UI | Has Redis/FAISS, no Qdrant |
| `chainlit_app_voice.py` (root) | 9 | Shim | **BROKEN IMPORT** |
| `simple_chainlit_app.py` | 9 | Demo | Unused |
| `services/voice/voice_interface.py` | 1906 | Core voice service | Well-structured |
| `services/voice/voice_degradation.py` | 510 | Graceful degradation | Good patterns |
| `services/voice/voice_recovery.py` | 273 | Recovery logic | Good patterns |

### Architecture Gap

```
CURRENT:
┌─────────────────────────────────────────────────────────┐
│                   chainlit_app.py                       │
│  - Text chat only                                        │
│  - No Redis persistence                                  │
│  - No FAISS knowledge retrieval                          │
│  - No Qdrant vector search                               │
│  - No circuit breakers                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               chainlit_app_voice.py                     │
│  - Text + Voice chat                                     │
│  - Redis session manager                                 │
│  - FAISS client                                          │
│  - Circuit breakers                                      │
│  - Wake word detection                                   │
│  - Audio streaming                                       │
└─────────────────────────────────────────────────────────┘

GAP: 90% code duplication, text-only lacks infrastructure
```

---

## Proposed Architecture

### Design Principles

1. **Don't Repeat Yourself (DRY)**: Single Chainlit app with feature flags
2. **Infrastructure as a Service**: Shared services layer for all UI modes
3. **Modular Voice**: Voice as a plugin/module, not a separate app
4. **Graceful Degradation**: Works without voice, works without Redis, etc.
5. **Sovereignty First**: All services local/offline capable

### Proposed Structure

```
app/XNAi_rag_app/
├── ui/
│   └── chainlit_app.py          # UNIFIED app (~900 lines)
│       ├── SessionManager       # Redis + in-memory fallback
│       ├── KnowledgeClient      # FAISS + Qdrant abstraction
│       ├── ChatHandler          # Text chat logic
│       ├── VoiceModule          # Optional voice (feature flag)
│       └── CommandHandler       # Slash commands
│
├── core/
│   ├── infrastructure/
│   │   ├── session_manager.py   # Unified session management
│   │   ├── knowledge_client.py  # FAISS + Qdrant abstraction
│   │   └── circuit_breakers.py  # (existing)
│   └── services_init.py         # (existing, migrated)
│
└── services/
    └── voice/
        ├── __init__.py          # VoiceModule export
        ├── voice_interface.py   # (existing)
        ├── voice_degradation.py # (existing)
        ├── voice_recovery.py    # (existing)
        └── voice_module.py      # NEW: Chainlit integration adapter
```

### Core Components

#### 1. Infrastructure Layer (`core/infrastructure/`)

```python
# session_manager.py - Unified Session Management
class SessionManager:
    """
    Unified session management with graceful fallback.
    
    Priority: Redis → In-memory
    """
    def __init__(self, redis_url: Optional[str] = None):
        self._redis = None
        self._memory_fallback = {}
        self._use_redis = False
        
    async def initialize(self) -> bool:
        """Initialize Redis or fall back to memory."""
        if self._redis_url:
            try:
                await self._connect_redis()
                self._use_redis = True
            except Exception:
                logger.warning("Redis unavailable, using memory fallback")
        return True
    
    async def get(self, session_id: str, key: str) -> Optional[Any]:
        if self._use_redis:
            return await self._redis_get(session_id, key)
        return self._memory_fallback.get(f"{session_id}:{key}")
    
    async def set(self, session_id: str, key: str, value: Any) -> bool:
        if self._use_redis:
            return await self._redis_set(session_id, key, value)
        self._memory_fallback[f"{session_id}:{key}"] = value
        return True
```

```python
# knowledge_client.py - FAISS + Qdrant Abstraction
class KnowledgeClient:
    """
    Unified knowledge retrieval with multiple backends.
    
    Priority: Qdrant (remote) → FAISS (local) → None
    """
    def __init__(self):
        self._qdrant = None
        self._faiss = None
        self._use_qdrant = False
        self._use_faiss = False
    
    async def initialize(self) -> bool:
        """Initialize available knowledge backends."""
        # Try Qdrant first
        try:
            await self._connect_qdrant()
            self._use_qdrant = True
        except Exception:
            pass
        
        # Fall back to FAISS
        if not self._use_qdrant:
            try:
                self._load_faiss()
                self._use_faiss = True
            except Exception:
                pass
        
        return self._use_qdrant or self._use_faiss
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if self._use_qdrant:
            return await self._qdrant_search(query, top_k)
        elif self._use_faiss:
            return self._faiss_search(query, top_k)
        return []
```

#### 2. Voice Module (`services/voice/voice_module.py`)

```python
# voice_module.py - Chainlit Voice Integration
class VoiceModule:
    """
    Modular voice integration for Chainlit.
    
    Provides:
    - Wake word detection
    - STT/TTS
    - Audio streaming
    - Circuit breaker protection
    
    Usage:
        voice = VoiceModule(config)
        await voice.initialize()
        
        # In Chainlit handler:
        if voice.is_enabled():
            await voice.handle_audio_chunk(chunk)
    """
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self._voice_interface: Optional[VoiceInterface] = None
        self._wake_word_detector: Optional[WakeWordDetector] = None
        self._enabled = False
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize voice components."""
        try:
            self._voice_interface = VoiceInterface(self.config)
            self._wake_word_detector = WakeWordDetector(
                wake_word=self.config.wake_word,
                sensitivity=self.config.wake_word_sensitivity
            )
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Voice module initialization failed: {e}")
            return False
    
    def enable(self):
        """Enable voice responses."""
        self._enabled = True
    
    def disable(self):
        """Disable voice responses."""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        return self._enabled and self._initialized
    
    async def transcribe(self, audio_data: bytes) -> Tuple[str, float]:
        """Transcribe audio to text."""
        if not self.is_enabled():
            raise VoiceNotEnabledError()
        return await self._voice_interface.transcribe_audio(audio_data)
    
    async def synthesize(self, text: str) -> Optional[bytes]:
        """Synthesize speech from text."""
        if not self.is_enabled():
            return None
        return await self._voice_interface.synthesize_speech(text)
    
    def check_wake_word(self, text: str) -> Tuple[bool, float]:
        """Check for wake word in text."""
        if not self._wake_word_detector:
            return True, 1.0
        return self._wake_word_detector.detect(text)
```

#### 3. Unified Chainlit App (`ui/chainlit_app.py`)

```python
# chainlit_app.py - Unified Chainlit Interface
"""
Xoe-NovAi Chainlit Interface
=============================
Unified text + voice interface with modular components.

Features:
- Text chat with RAG integration
- Optional voice responses (feature flag)
- Redis session persistence (with fallback)
- FAISS + Qdrant knowledge retrieval
- Circuit breaker protection
"""

import chainlit as cl
from typing import Optional, Dict, Any

# Infrastructure
from ..core.infrastructure.session_manager import SessionManager
from ..core.infrastructure.knowledge_client import KnowledgeClient
from ..core.circuit_breakers import registry, initialize_circuit_breakers

# Voice Module (optional)
try:
    from ..services.voice.voice_module import VoiceModule
    from ..services.voice import VoiceConfig
    VOICE_AVAILABLE = True
except ImportError:
    VoiceModule = None
    VOICE_AVAILABLE = False

# Global instances
_session_manager: Optional[SessionManager] = None
_knowledge_client: Optional[KnowledgeClient] = None
_voice_module: Optional[VoiceModule] = None

# Feature flags
FEATURE_VOICE = os.getenv("FEATURE_VOICE", "false").lower() == "true"
FEATURE_REDIS_SESSIONS = os.getenv("FEATURE_REDIS_SESSIONS", "true").lower() == "true"
FEATURE_QDRANT = os.getenv("FEATURE_QDRANT", "true").lower() == "true"


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session with all available services."""
    
    # Initialize infrastructure
    global _session_manager, _knowledge_client, _voice_module
    
    # Session management
    _session_manager = SessionManager(
        redis_url=os.getenv("REDIS_URL") if FEATURE_REDIS_SESSIONS else None
    )
    await _session_manager.initialize()
    
    # Knowledge retrieval
    _knowledge_client = KnowledgeClient()
    await _knowledge_client.initialize()
    
    # Voice module (optional)
    if FEATURE_VOICE and VOICE_AVAILABLE:
        _voice_module = VoiceModule(VoiceConfig(
            wake_word_enabled=True,
            offline_mode=True
        ))
        await _voice_module.initialize()
    
    # Send welcome message with feature status
    await send_welcome_message()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    user_query = message.content.strip()
    
    # Handle commands
    if user_query.startswith("/"):
        await handle_command(user_query)
        return
    
    # Get conversation context
    context = await _session_manager.get_conversation_context(max_turns=5)
    
    # Get knowledge context
    knowledge = await _knowledge_client.search(user_query, top_k=3)
    
    # Generate response
    response = await generate_response(user_query, context, knowledge)
    
    # Stream response
    msg = cl.Message(content="")
    await msg.send()
    
    for word in response.split():
        await msg.stream_token(word + " ")
    await msg.update()
    
    # Voice response (if enabled)
    if _voice_module and _voice_module.is_enabled():
        audio = await _voice_module.synthesize(response)
        if audio:
            await cl.Audio(name="Nova", content=audio).send()
    
    # Save to session
    await _session_manager.add_interaction("user", user_query)
    await _session_manager.add_interaction("assistant", response)


# Voice handlers (conditional)
if VOICE_AVAILABLE:
    @cl.on_audio_start
    async def on_audio_start():
        if not _voice_module or not _voice_module.is_enabled():
            return False
        return True
    
    @cl.on_audio_chunk
    async def on_audio_chunk(chunk):
        if not _voice_module or not _voice_module.is_enabled():
            return
        
        transcription, confidence = await _voice_module.transcribe(chunk.data)
        
        # Check wake word
        detected, _ = _voice_module.check_wake_word(transcription)
        if detected:
            await on_message(cl.Message(content=transcription))
    
    @cl.on_audio_end
    async def on_audio_end():
        pass
```

---

## Migration Plan

### Phase 1: Infrastructure Layer (1 day)

1. Create `core/infrastructure/session_manager.py`
2. Create `core/infrastructure/knowledge_client.py`
3. Test with existing voice app

### Phase 2: Voice Module (1 day)

1. Create `services/voice/voice_module.py`
2. Refactor existing voice code to use module
3. Test voice functionality

### Phase 3: Unified Chainlit App (1 day)

1. Create new `ui/chainlit_app.py`
2. Migrate features from both apps
3. Add feature flags
4. Test all scenarios

### Phase 4: Cleanup (0.5 day)

1. Delete `ui/chainlit_app_voice.py`
2. Fix broken shim import
3. Delete `simple_chainlit_app.py`
4. Update documentation

---

## Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `FEATURE_VOICE` | `false` | Enable voice responses |
| `FEATURE_REDIS_SESSIONS` | `true` | Enable Redis session persistence |
| `FEATURE_QDRANT` | `true` | Enable Qdrant vector search |
| `FEATURE_LOCAL_FALLBACK` | `true` | Enable local LLM fallback |

---

## Benefits

| Current | Proposed |
|---------|----------|
| 2 Chainlit apps (1685 lines total) | 1 Chainlit app (~900 lines) |
| No Redis in text app | Unified session management |
| No FAISS/Qdrant in text app | Unified knowledge retrieval |
| Voice tightly coupled | Voice as module |
| 90% code duplication | DRY principle |
| Manual feature sync | Feature flags |

---

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Voice module complexity | Clear interface, well-documented |
| Feature flag proliferation | Document all flags, sensible defaults |
| Migration breakage | Incremental migration, thorough testing |
| Performance overhead | Lazy initialization, only load what's needed |

---

## Recommendation

**Proceed with unified architecture.**

The proposed design:
1. Eliminates 90% code duplication
2. Brings text app to parity with voice app
3. Makes voice a modular, optional feature
4. Follows DRY and separation of concerns principles
5. Aligns with strategic roadmap for Gemini CLI + FastAPI

**Estimated effort**: 3.5 days total

---

## Next Steps

1. **User Approval**: Confirm this architecture direction
2. **Create Infrastructure Layer**: Start with `session_manager.py`
3. **Create Voice Module**: Extract voice into modular component
4. **Migrate Chainlit**: Create unified app
5. **Cleanup**: Remove duplicates, fix imports