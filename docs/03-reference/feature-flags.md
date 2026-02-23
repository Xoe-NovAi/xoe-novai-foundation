# Feature Flags Reference

> **Updated**: 2026-02-22
> **Version**: 0.2.0

---

## Overview

XNAi Foundation uses feature flags to control optional functionality. This allows for graceful degradation and flexible deployment configurations.

---

## Available Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `FEATURE_VOICE` | `false` | Enable voice responses (STT/TTS) |
| `FEATURE_REDIS_SESSIONS` | `true` | Enable Redis session persistence |
| `FEATURE_QDRANT` | `true` | Enable Qdrant vector search |
| `FEATURE_LOCAL_FALLBACK` | `true` | Enable local LLM fallback |

---

## Detailed Descriptions

### FEATURE_VOICE

**Default**: `false`

Controls voice processing capabilities including:
- Speech-to-Text (Faster Whisper)
- Text-to-Speech (Piper ONNX)
- Wake word detection ("Hey Nova")

**When Enabled**:
- Voice module initializes on startup
- Audio handlers registered in Chainlit
- `/voice` commands available

**When Disabled**:
- Voice module not loaded
- Text-only mode
- Lower memory footprint

**Environment**:
```bash
export FEATURE_VOICE=true
```

**Python**:
```python
import os
if os.getenv("FEATURE_VOICE", "false").lower() == "true":
    # Initialize voice module
    pass
```

---

### FEATURE_REDIS_SESSIONS

**Default**: `true`

Controls session persistence backend:
- `true`: Use Redis for session storage
- `false`: Use in-memory storage (lost on restart)

**When Enabled**:
- Sessions persist across restarts
- Shared sessions across instances
- Automatic fallback to memory if Redis unavailable

**When Disabled**:
- All sessions in-memory only
- Sessions lost on restart
- No cross-instance sharing

**Environment**:
```bash
export FEATURE_REDIS_SESSIONS=true
```

**Graceful Degradation**:
```python
# SessionManager automatically falls back
session = SessionManager(config)
await session.initialize()  # Handles fallback internally

if session.is_connected:
    print("Using Redis")
else:
    print("Using in-memory fallback")
```

---

### FEATURE_QDRANT

**Default**: `true`

Controls vector database backend:
- `true`: Use Qdrant for vector search
- `false`: Use FAISS only

**When Enabled**:
- Qdrant primary vector store
- FAISS as fallback
- Full-text search as last resort

**When Disabled**:
- FAISS primary vector store
- Full-text search fallback
- No remote vector DB dependency

**Environment**:
```bash
export FEATURE_QDRANT=true
```

**Backend Priority**:
```
Qdrant (remote) → FAISS (local) → Keyword Search
```

---

### FEATURE_LOCAL_FALLBACK

**Default**: `true`

Controls local LLM fallback when RAG API unavailable:
- `true`: Use local LLM for responses
- `false`: Return error when API unavailable

**When Enabled**:
- Automatic fallback to local LLM
- Continuous service during API outages
- Reduced error rate

**When Disabled**:
- Errors returned when API unavailable
- No local processing

**Environment**:
```bash
export FEATURE_LOCAL_FALLBACK=true
```

---

## Usage Patterns

### Checking Feature Flags

```python
import os

def is_feature_enabled(flag_name: str, default: str = "false") -> bool:
    """Check if a feature flag is enabled."""
    return os.getenv(flag_name, default).lower() == "true"

# Usage
if is_feature_enabled("FEATURE_VOICE"):
    # Initialize voice
    pass
```

### Conditional Initialization

```python
import os
from XNAi_rag_app.services.voice import VoiceModule

async def setup_voice():
    """Setup voice module if enabled."""
    if os.getenv("FEATURE_VOICE", "false").lower() != "true":
        return None
    
    voice = VoiceModule()
    await voice.initialize()
    return voice
```

### Feature-Gated Code Paths

```python
async def process_request(text: str):
    """Process request with feature-aware logic."""
    
    # Check voice
    if os.getenv("FEATURE_VOICE") == "true":
        voice_module = get_voice_module()
        if voice_module and voice_module.is_enabled:
            audio = await voice_module.synthesize(text)
            if audio:
                return {"text": text, "audio": audio}
    
    # Fallback to text only
    return {"text": text}
```

---

## Configuration Files

### Environment File (.env)

```bash
# Feature Flags
FEATURE_VOICE=false
FEATURE_REDIS_SESSIONS=true
FEATURE_QDRANT=true
FEATURE_LOCAL_FALLBACK=true
```

### Docker Compose

```yaml
services:
  chainlit:
    environment:
      - FEATURE_VOICE=${FEATURE_VOICE:-false}
      - FEATURE_REDIS_SESSIONS=${FEATURE_REDIS_SESSIONS:-true}
      - FEATURE_QDRANT=${FEATURE_QDRANT:-true}
      - FEATURE_LOCAL_FALLBACK=${FEATURE_LOCAL_FALLBACK:-true}
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: xnai-feature-flags
data:
  FEATURE_VOICE: "false"
  FEATURE_REDIS_SESSIONS: "true"
  FEATURE_QDRANT: "true"
  FEATURE_LOCAL_FALLBACK: "true"
```

---

## Performance Impact

| Flag | Memory Impact | Latency Impact |
|------|---------------|----------------|
| `FEATURE_VOICE=true` | +500MB | +200ms STT, +50ms TTS |
| `FEATURE_REDIS_SESSIONS=true` | +50MB | +5ms per request |
| `FEATURE_QDRANT=true` | +100MB | +10ms per search |
| `FEATURE_LOCAL_FALLBACK=true` | +2GB (if triggered) | +500ms (if triggered) |

---

## Best Practices

1. **Start Disabled**: New features should default to `false`
2. **Document Dependencies**: Note what each flag requires
3. **Graceful Degradation**: Always handle disabled state
4. **Log State**: Log feature flag state on startup
5. **Validate**: Check dependencies before enabling

---

## Related Documentation

- [Infrastructure Layer](../api/infrastructure-layer.md)
- [Voice Module](../api/voice_module.md)
- [Chainlit Migration Guide](chainlit-migration.md)
