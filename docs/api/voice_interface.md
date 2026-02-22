# Voice Interface API Reference

> **Generated**: 2026-02-21  
> **Source**: `app/XNAi_rag_app/ui/chainlit_app_voice.py`  
> **Version**: 0.1.0-alpha

---

## Overview

The Voice Interface is a Chainlit-based WebUI providing voice-to-voice conversation with the RAG system. It includes wake word detection ("Hey Nova"), speech-to-text (STT), text-to-speech (TTS), and real-time streaming.

> **Note**: This is a Chainlit application, not a REST API. It provides a web-based UI with WebSocket support for real-time audio streaming.

---

## Technology Stack

| Component | Implementation |
|-----------|---------------|
| UI Framework | Chainlit |
| STT (Speech-to-Text) | Faster Whisper |
| TTS (Text-to-Speech) | Piper ONNX |
| Wake Word | Silero VAD |
| Session Management | Redis |
| Vector Search | FAISS |

---

## Access

### URLs

| Service | URL | Description |
|---------|-----|-------------|
| Voice UI | `http://localhost:8001` | Chainlit voice interface |
| API Docs | `http://localhost:8000/docs` | REST API |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAINLIT_PORT` | `8001` | UI port |
| `RAG_API_URL` | `http://localhost:8000` | RAG API endpoint |
| `RAG_UI_USERNAME` | - | Auto-login username |
| `RAG_UI_PASSWORD` | - | Auto-login password |
| `XOE_VOICE_DEBUG` | `false` | Enable debug logging |
| `XOE_VOICE_DEBUG_DIR` | - | Debug output directory |

---

## Features

### Wake Word Detection

The interface listens for "Hey Nova" wake word:

```python
# Wake word detection via Silero VAD
wake_word_detector = WakeWordDetector()
```

### Voice-to-Voice Pipeline

```
Microphone → STT (Whisper) → RAG Query → LLM → TTS (Piper) → Speaker
```

### Session Persistence

Voice sessions are stored in Redis:

```python
session_manager = VoiceSessionManager(redis_client)
# Session data: conversation history, preferences, user context
```

### Rate Limiting

Voice input is rate-limited to prevent abuse:

```python
rate_limiter = VoiceRateLimiter(max_calls=10, period=60)
```

---

## Configuration

### Voice Config

```python
@dataclass
class VoiceConfig:
    stt_provider: STTProvider = STTProvider.WHISPER
    tts_provider: TTSProvider = PIPER
    language: str = "en"
    sample_rate: int = 16000
    buffer_size: int = 1024
    wake_word: str = "hey nova"
    vad_threshold: float = 0.5
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VOICE_STT_MODEL` | `base` | Whisper model size |
| `VOICE_TTS_MODEL` | `en_US-lessac-medium.onnx` | Piper model |
| `VOICE_WAKE_WORD` | `hey nova` | Wake phrase |
| `VOICE_VAD_THRESHOLD` | `0.5` | Voice activity threshold |

---

## WebSocket Events

The voice interface uses WebSocket for real-time audio streaming:

### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `audio_start` | - | Start audio stream |
| `audio_data` | base64 | Audio chunk |
| `audio_stop` | - | End audio stream |
| `transcription` | text | Manual text input |

### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `wake_word_detected` | - | Wake word heard |
| `transcription` | text | STT result |
| `response_chunk` | text | LLM response chunk |
| `tts_audio` | base64 | TTS audio chunk |
| `error` | message | Error occurred |

---

## API Integration

### Calling RAG from Voice

```python
from XNAi_rag_app.services.rag import RagService

async def voice_query(audio_input: bytes) -> str:
    # 1. Transcribe audio
    text = await stt.transcribe(audio_input)
    
    # 2. Query RAG
    response = await rag_service.query(text)
    
    # 3. Synthesize speech
    audio = await tts.synthesize(response)
    
    return audio
```

---

## Circuit Breaker Integration

The voice interface uses circuit breakers for resilience:

| Breaker | Purpose |
|---------|---------|
| `voice_processing_breaker` | STT/TTS processing |
| `rag_api_breaker` | RAG API calls |
| `redis_breaker` | Session storage |

### Error Handling

```python
try:
    audio = await voice_interface.process(audio_input)
except CircuitBreakerError as e:
    logger.warning(f"Voice circuit open: {e}")
    return {"error": "voice_unavailable", "suggestion": "Please try again shortly"}
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| E2E Latency | <300 ms |
| STT Latency | <500 ms |
| TTS Latency | <200 ms |
| Wake Word Accuracy | >95% |

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
    - CHAINLIT_NO_TELEMETRY=true
  volumes:
    - ./models:/models:ro
```

### Running

```bash
# Start voice UI
podman-compose up -d chainlit

# Access at http://localhost:8001
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Microphone not detected | Browser permissions | Allow microphone access |
| Wake word not responding | VAD threshold too high | Lower `VOICE_VAD_THRESHOLD` |
| TTS not working | Piper model missing | Check model files |
| No RAG responses | API unreachable | Check `RAG_API_URL` |

### Debug Mode

```bash
XOE_VOICE_DEBUG=true XOE_VOICE_DEBUG_DIR=/tmp/voice_logs \
  chainlit run chainlit_app_voice.py
```

---

## Related Documentation

- [Main API](main.md)
- [Voice Deployment Runbook](../03-how-to-guides/runbooks/voice-deployment.md)
