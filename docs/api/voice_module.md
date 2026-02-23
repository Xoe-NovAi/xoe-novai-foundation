# Voice Module API Reference

> **Generated**: 2026-02-22
> **Source**: `app/XNAi_rag_app/services/voice/voice_module.py`
> **Version**: 0.1.0

---

## Overview

The Voice Module provides modular voice integration for Chainlit and other interfaces. It wraps the existing voice services with a clean, feature-flagged API.

### Key Features

- **Feature Flag Controlled**: Disabled by default (`FEATURE_VOICE=false`)
- **Graceful Degradation**: Falls back to text-only mode when unavailable
- **Wake Word Detection**: Optional "Hey Nova" detection
- **STT/TTS**: Speech-to-Text and Text-to-Speech support
- **Circuit Breaker Protection**: Resilient error handling

---

## Configuration

### VoiceModuleConfig

```python
from XNAi_rag_app.services.voice import VoiceModuleConfig

config = VoiceModuleConfig(
    enabled=False,              # Start disabled
    wake_word_enabled=True,     # Enable wake word detection
    offline_mode=True,          # Use offline providers only
    wake_word="hey nova",       # Wake phrase
    wake_word_sensitivity=0.5,  # Detection sensitivity (0-1)
    stt_provider="faster_whisper",
    tts_provider="piper",
    whisper_model="tiny",       # Whisper model size
    whisper_device="cpu",       # Device for inference
    sample_rate=16000,          # Audio sample rate
    rate_limit_requests=100,    # Rate limit per window
    rate_limit_window=60,       # Window in seconds
)
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FEATURE_VOICE` | `false` | Master feature flag |
| `VOICE_STT_MODEL` | `tiny` | Whisper model size |
| `VOICE_TTS_MODEL` | `en_US-lessac-medium.onnx` | Piper model |
| `VOICE_WAKE_WORD` | `hey nova` | Wake phrase |
| `VOICE_VAD_THRESHOLD` | `0.5` | Voice activity threshold |

---

## Usage

### Basic Initialization

```python
from XNAi_rag_app.services.voice import VoiceModule, VoiceModuleConfig

# Create with config
config = VoiceModuleConfig(enabled=True)
voice = VoiceModule(config)

# Initialize
success = await voice.initialize()

if success:
    print("Voice module ready")
else:
    print("Voice module unavailable")
```

### Factory Function

```python
from XNAi_rag_app.services.voice import create_voice_module

# Create and initialize in one step
voice = await create_voice_module(
    enabled=True,
    wake_word_enabled=True,
    offline_mode=True,
)
```

### Speech-to-Text

```python
# Transcribe audio
try:
    text, confidence = await voice.transcribe(audio_bytes)
    print(f"Transcription: {text} (confidence: {confidence:.2%})")
except VoiceNotEnabledError:
    print("Voice not enabled")
except VoiceNotInitializedError:
    print("Voice not initialized")
```

### Text-to-Speech

```python
# Synthesize speech
try:
    audio = await voice.synthesize("Hello, how can I help?")
    if audio:
        # Play or send audio
        await cl.Audio(name="Response", content=audio).send()
except VoiceNotEnabledError:
    print("Voice not enabled")
```

### Wake Word Detection

```python
# Check for wake word in transcription
detected, confidence = voice.check_wake_word(transcription)

if detected:
    print(f"Wake word detected! (confidence: {confidence:.2%})")
    # Process the command
else:
    print("Wake word not detected")
```

### Runtime Control

```python
# Enable/disable at runtime
voice.enable()   # Enable voice responses
voice.disable()  # Disable voice responses

# Check state
if voice.is_enabled:
    print("Voice is enabled")
if voice.is_initialized:
    print("Voice is initialized")
```

---

## Chainlit Integration

### Basic Integration

```python
import chainlit as cl
from XNAi_rag_app.services.voice import VoiceModule, VoiceModuleConfig

_voice_module: VoiceModule = None

@cl.on_chat_start
async def on_chat_start():
    global _voice_module
    
    # Check feature flag
    if os.getenv("FEATURE_VOICE", "false").lower() == "true":
        config = VoiceModuleConfig(enabled=False)  # Start disabled
        _voice_module = VoiceModule(config)
        success = await _voice_module.initialize()
        
        if success:
            # Add voice toggle to settings
            await cl.ChatSettings([
                cl.input_widget.Switch(
                    id="voice_enabled",
                    label="Voice Responses",
                    initial=False
                ),
            ]).send()

@cl.on_message
async def on_message(message: cl.Message):
    # ... process message ...
    
    # Check if voice is enabled
    voice_enabled = (
        cl.user_session.get("voice_enabled", False) and
        _voice_module and
        _voice_module.is_enabled
    )
    
    if voice_enabled:
        audio = await _voice_module.synthesize(response_text)
        if audio:
            await cl.Audio(name="Response", content=audio).send()
```

### Audio Stream Handling

```python
@cl.on_audio_start
async def on_audio_start():
    if not _voice_module or not _voice_module.is_enabled:
        return False  # Reject stream
    return True

@cl.on_audio_chunk
async def on_audio_chunk(chunk):
    # Buffer audio chunks
    buffer = cl.user_session.get("audio_buffer", [])
    buffer.append(chunk.data)
    cl.user_session.set("audio_buffer", buffer)

@cl.on_audio_end
async def on_audio_end():
    buffer = cl.user_session.get("audio_buffer", [])
    if buffer:
        audio_data = b"".join(buffer)
        text, confidence = await _voice_module.transcribe(audio_data)
        
        if text:
            detected, _ = _voice_module.check_wake_word(text)
            if detected:
                await on_message(cl.Message(content=text))
        
        cl.user_session.set("audio_buffer", [])
```

---

## Exception Handling

### Exceptions

```python
from XNAi_rag_app.services.voice import (
    VoiceNotEnabledError,
    VoiceNotInitializedError,
)

try:
    text, confidence = await voice.transcribe(audio)
except VoiceNotEnabledError:
    # Voice is disabled - fall back to text
    pass
except VoiceNotInitializedError:
    # Voice failed to initialize
    pass
```

---

## Status and Metrics

```python
# Get status
status = voice.get_status()
# Returns:
# {
#     "enabled": bool,
#     "initialized": bool,
#     "feature_flag": bool,
#     "voice_available": bool,
#     "wake_word_enabled": bool,
#     "stt_provider": str,
#     "tts_provider": str,
#     "metrics": {
#         "transcription_count": int,
#         "synthesis_count": int,
#         "wake_word_count": int,
#     }
# }
```

---

## Feature Flag

```bash
# Enable voice in environment
export FEATURE_VOICE=true

# Or in .env
FEATURE_VOICE=true
```

---

## Dependencies

| Package | Required | Purpose |
|---------|----------|---------|
| `faster-whisper` | For STT | Speech-to-Text |
| `piper-tts` | For TTS | Text-to-Speech |
| `anyio` | Yes | Async concurrency |

---

## Related Documentation

- [Voice Interface](voice_interface.md) - Chainlit voice interface
- [Infrastructure Layer](infrastructure-layer.md) - Session and knowledge clients
- [Architecture Patterns](../../expert-knowledge/architecture/CHAINLIT-ARCHITECTURE-PATTERNS.md)
