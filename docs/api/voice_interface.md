# Voice Interface API Reference

> **Generated**: 2026-02-22  
> **Source**: `app/XNAi_rag_app/ui/chainlit_app_unified.py`  
> **Version**: 0.2.0

---

## Overview

The Voice Interface is a Chainlit-based WebUI providing unified text and voice conversation with the RAG system. It includes optional wake word detection ("Hey Nova"), speech-to-text (STT), text-to-speech (TTS), and real-time streaming.

> **Note**: This is a unified Chainlit application that combines text and voice interfaces. Voice is optional and disabled by default via feature flag.

---

## Feature Flags

The unified interface uses feature flags for optional components:

| Flag | Default | Description |
|------|---------|-------------|
| `FEATURE_VOICE` | `false` | Enable voice responses (STT/TTS) |
| `FEATURE_REDIS_SESSIONS` | `true` | Enable Redis session persistence |
| `FEATURE_QDRANT` | `true` | Enable Qdrant vector search |
| `FEATURE_LOCAL_FALLBACK` | `true` | Enable local LLM fallback |

### Enabling Voice

```bash
# Enable voice in environment
export FEATURE_VOICE=true

# Run with voice enabled
chainlit run chainlit_app_unified.py --headless
```

---

## Technology Stack

| Component | Implementation |
|-----------|---------------|
| UI Framework | Chainlit |
| Session Manager | Redis + In-Memory Fallback |
| Knowledge Retrieval | Qdrant + FAISS Fallback |
| STT (Speech-to-Text) | Faster Whisper (optional) |
| TTS (Text-to-Speech) | Piper ONNX (optional) |
| Wake Word | Silero VAD (optional) |

---

## Architecture

### Infrastructure Layer

The unified app uses a shared infrastructure layer:

```
app/XNAi_rag_app/core/infrastructure/
├── session_manager.py    # Redis + in-memory fallback
└── knowledge_client.py   # Qdrant + FAISS abstraction

app/XNAi_rag_app/services/voice/
└── voice_module.py       # Chainlit voice integration adapter
```

### Graceful Degradation

All services fall back gracefully:

| Service | Primary | Fallback | Last Resort |
|---------|---------|----------|-------------|
| Sessions | Redis | In-Memory | - |
| Knowledge | Qdrant | FAISS | Keyword Search |
| Voice | STT/TTS | Text Only | - |
| API | RAG API | Local LLM | Error Message |

---

## Access

### URLs

| Service | URL | Description |
|---------|-----|-------------|
| Unified UI | `http://localhost:8001` | Chainlit text+voice interface |
| API Docs | `http://localhost:8000/docs` | REST API |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAINLIT_PORT` | `8001` | UI port |
| `RAG_API_URL` | `http://localhost:8000` | RAG API endpoint |
| `RAG_UI_USERNAME` | - | Auto-login username |
| `RAG_UI_PASSWORD` | - | Auto-login password |
| `FEATURE_VOICE` | `false` | Enable voice features |
| `FEATURE_REDIS_SESSIONS` | `true` | Enable Redis sessions |
| `FEATURE_QDRANT` | `true` | Enable Qdrant |

---

## Features

### Text Chat (Default)

The primary interface is text-based:

```
User Input → RAG Query → LLM Response → Text Display
```

### Voice Chat (Optional)

When `FEATURE_VOICE=true`:

```
Microphone → STT (Whisper) → RAG Query → LLM → TTS (Piper) → Speaker
```

### Wake Word Detection

The interface listens for "Hey Nova" wake word (when voice enabled):

```python
# Wake word detection via VoiceModule
from XNAi_rag_app.services.voice import VoiceModule

voice = VoiceModule(VoiceModuleConfig(wake_word_enabled=True))
detected, confidence = voice.check_wake_word(text)
```

### Session Persistence

Sessions use the infrastructure layer:

```python
from XNAi_rag_app.core.infrastructure import SessionManager

# Create session manager
session = SessionManager(SessionConfig(redis_url="redis://localhost:6379"))
await session.initialize()

# Store data
await session.set("user_id", "12345")

# Get conversation context
context = await session.get_conversation_context(max_turns=5)
```

### Knowledge Retrieval

Knowledge uses the infrastructure layer:

```python
from XNAi_rag_app.core.infrastructure import KnowledgeClient

# Create knowledge client
knowledge = KnowledgeClient(KnowledgeConfig(qdrant_url="http://localhost:6333"))
await knowledge.initialize()

# Search knowledge
results = await knowledge.search("What is XNAi?", top_k=5)
```

---

## Configuration

### Voice Module Config

```python
from XNAi_rag_app.services.voice import VoiceModuleConfig

config = VoiceModuleConfig(
    enabled=False,           # Start disabled
    wake_word_enabled=True,  # Enable wake word
    offline_mode=True,       # Use offline providers
    stt_provider="faster_whisper",
    tts_provider="piper",
    whisper_model="tiny",
)
```

### Session Config

```python
from XNAi_rag_app.core.infrastructure import SessionConfig

config = SessionConfig(
    session_ttl=3600,         # 1 hour
    max_conversation_turns=100,
    redis_host="redis",
    redis_port=6379,
)
```

### Knowledge Config

```python
from XNAi_rag_app.core.infrastructure import KnowledgeConfig

config = KnowledgeConfig(
    qdrant_url="http://localhost:6333",
    qdrant_collection="xnai_knowledge",
    default_top_k=5,
    score_threshold=0.7,
)
```

---

## Commands

The unified app supports slash commands:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/stats` | Display session statistics |
| `/reset` | Clear conversation history |
| `/rag on/off` | Enable/disable RAG |
| `/status` | Check API connection |
| `/voice on/off` | Enable/disable voice responses |
| `/voice status` | Show voice module status |

---

## API Integration

### Using Infrastructure Layer

```python
from XNAi_rag_app.core.infrastructure import (
    SessionManager,
    KnowledgeClient,
    create_session_manager,
    create_knowledge_client,
)

async def setup():
    # Create session manager
    session = await create_session_manager(
        session_id="user_123",
        redis_url="redis://localhost:6379"
    )
    
    # Create knowledge client
    knowledge = await create_knowledge_client(
        qdrant_url="http://localhost:6333"
    )
    
    return session, knowledge
```

### Voice Processing

```python
from XNAi_rag_app.services.voice import VoiceModule, VoiceModuleConfig

async def process_voice(audio_bytes: bytes) -> str:
    # Initialize voice module
    config = VoiceModuleConfig(enabled=True)
    voice = VoiceModule(config)
    await voice.initialize()
    
    # Transcribe
    text, confidence = await voice.transcribe(audio_bytes)
    
    # Synthesize response
    audio = await voice.synthesize(text)
    
    return audio
```

---

## Circuit Breaker Integration

The interface uses circuit breakers for resilience:

| Breaker | Purpose |
|---------|---------|
| `rag_api_breaker` | RAG API calls |
| `voice_stt_breaker` | STT processing |
| `voice_tts_breaker` | TTS processing |
| `redis_breaker` | Session storage |

### Error Handling

```python
try:
    response = await api_client.query(text)
except CircuitBreakerError as e:
    logger.warning(f"Circuit open: {e}")
    # Graceful degradation
    response = await local_llm.fallback(text)
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| E2E Latency | <300 ms |
| STT Latency | <500 ms |
| TTS Latency | <200 ms |
| Memory Usage | <6GB RAM |

---

## Deployment

### Docker

```yaml
chainlit:
  build:
    context: .
    dockerfile: Dockerfile.chainlit
  ports:
    - "8001:8001"
  environment:
    - RAG_API_URL=http://rag:8000
    - FEATURE_VOICE=false
    - FEATURE_REDIS_SESSIONS=true
    - FEATURE_QDRANT=true
    - CHAINLIT_NO_TELEMETRY=true
  volumes:
    - ./models:/models:ro
```

### Running

```bash
# Text-only mode (default)
chainlit run chainlit_app_unified.py --headless

# With voice enabled
FEATURE_VOICE=true chainlit run chainlit_app_unified.py --headless

# With Docker/Podman
podman-compose up -d chainlit
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Voice not working | Feature flag off | Set `FEATURE_VOICE=true` |
| Sessions not persisting | Redis unavailable | Check Redis connection |
| No knowledge results | Qdrant unavailable | Check Qdrant connection |
| Microphone not detected | Browser permissions | Allow microphone access |

### Debug Mode

```bash
# Enable debug logging
XOE_VOICE_DEBUG=true \
FEATURE_VOICE=true \
chainlit run chainlit_app_unified.py --headless
```

---

## Related Documentation

- [Infrastructure Layer](infrastructure-layer.md)
- [Voice Module](voice_module.md)
- [Main API](main.md)
- [Voice Deployment Runbook](../03-how-to-guides/runbooks/voice-deployment.md)

---

## Migration from Legacy Apps

If you were using the old separate apps:

| Old App | New App | Notes |
|---------|---------|-------|
| `chainlit_app.py` | `chainlit_app_unified.py` | Text-only mode (default) |
| `chainlit_app_voice.py` | `chainlit_app_unified.py` | Enable `FEATURE_VOICE=true` |

The unified app provides all functionality with better code reuse and simpler deployment.
