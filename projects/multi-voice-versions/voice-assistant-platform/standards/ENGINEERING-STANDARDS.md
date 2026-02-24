# Engineering Standards

**Project**: VoiceOS — Voice Assistant Platform
**Version**: 1.0
**Last Updated**: 2026-02-23

---

## Purpose

These standards define how all code in VoiceOS is written, reviewed, and maintained. They exist to ensure that:
- Every module works predictably and handles failure gracefully
- Any new contributor (or AI agent) can understand and extend the codebase
- Accessibility requirements are never an afterthought
- The system degrades gracefully when components are unavailable

All contributors — human and AI — MUST follow these standards when writing or modifying code in this project.

---

## 1. Language and Runtime

- **Python 3.11+** required for all modules
- Use `asyncio` for all I/O-bound operations (audio, HTTP, file)
- Use type hints everywhere (enforced by mypy)
- Use `dataclasses` or `pydantic` for data models
- No global mutable state outside of explicitly designated singletons

---

## 2. Module Structure

Every Python module MUST follow this structure:

```
src/
  module_name/
    __init__.py        # Public API exports only
    _core.py           # Implementation
    _types.py          # Types and dataclasses for this module
    _config.py         # Configuration (env var + YAML)
    _errors.py         # Custom exceptions
    tests/
      test_core.py
      test_config.py
```

---

## 3. Error Handling

### 3.1 Never Swallow Exceptions Silently

```python
# BAD
try:
    result = await stt_service.transcribe(audio)
except Exception:
    pass  # NEVER do this

# GOOD
try:
    result = await stt_service.transcribe(audio)
except STTConnectionError as e:
    logger.error("STT service unavailable", error=str(e))
    raise VoiceOSServiceError("Speech recognition failed") from e
```

### 3.2 Always Provide Voice-Friendly Error Messages

Every exception class that can surface to the user MUST include a `voice_message` attribute:

```python
@dataclass
class VoiceOSError(Exception):
    message: str
    voice_message: str  # What to say to the user
    recoverable: bool = True

# Example
raise VoiceOSError(
    message="STT service timeout after 5000ms",
    voice_message="Sorry, speech recognition timed out. Please try again.",
    recoverable=True
)
```

### 3.3 Circuit Breaker Required for All External Services

All calls to STT, TTS, LLM, or any network service MUST go through a circuit breaker:

```python
from src.reliability import CircuitBreaker

stt_breaker = CircuitBreaker(
    failure_threshold=3,
    success_threshold=2,
    timeout_sec=30
)

result = await stt_breaker.call(stt_service.transcribe, audio)
```

---

## 4. Async Protocol

### 4.1 All I/O is async

```python
# CORRECT
async def transcribe(self, audio: bytes) -> str: ...

# WRONG — blocks the event loop
def transcribe(self, audio: bytes) -> str:
    return requests.post(url, data=audio).json()["text"]
```

### 4.2 Use asyncio.timeout() for all network calls

```python
async with asyncio.timeout(5.0):
    response = await http_client.post(url, data=audio)
```

### 4.3 Audio callbacks must be synchronous (sounddevice constraint)

Audio recording callbacks from `sounddevice` are called from a C thread and must be synchronous. Use a thread-safe queue to bridge to async:

```python
audio_queue: asyncio.Queue[np.ndarray] = asyncio.Queue()

def audio_callback(indata, frames, time, status):
    # synchronous — put into queue for async consumption
    loop.call_soon_threadsafe(audio_queue.put_nowait, indata.copy())
```

---

## 5. Configuration

### 5.1 All configuration comes from one source

Config is loaded once at startup from:
1. `~/.voiceos/config.yaml` (user config)
2. Environment variables (override config file)
3. Default values in `_config.py` (fallback)

Never hardcode ports, URLs, model names, or timeouts in business logic.

### 5.2 Config schema

Every module's config MUST be a dataclass with defaults:

```python
@dataclass
class STTConfig:
    base_url: str = "http://127.0.0.1:2022"
    model: str = "whisper-base"
    language: str = "en"
    timeout_sec: float = 10.0
    vocabulary_bias: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "STTConfig":
        return cls(
            base_url=os.getenv("VOICEOS_STT_URL", cls.base_url),
            model=os.getenv("VOICEOS_STT_MODEL", cls.model),
        )
```

---

## 6. Logging

Use `structlog` for all logging. Never use `print()` in production code.

```python
import structlog
logger = structlog.get_logger(__name__)

# Correct
logger.info("transcription_complete", duration_ms=142, words=12)
logger.error("stt_failed", error=str(e), url=config.base_url)

# Wrong
print(f"Transcription done in {duration}ms")
```

Log levels:
- `DEBUG`: internal state, timing details
- `INFO`: normal events (session started, transcription complete)
- `WARNING`: degraded but operational (using fallback provider)
- `ERROR`: failure that affected user experience
- `CRITICAL`: system-level failure requiring restart

---

## 7. Accessibility Requirements (Non-Negotiable)

These are not optional. They apply to every feature.

### 7.1 Every user-facing event MUST be announceable

Any state change the user needs to know about MUST emit a `VoiceEvent` that can be read by VoiceOver or spoken by TTS:

```python
@dataclass
class VoiceEvent:
    event_type: str        # "session_started", "error", "response_ready"
    message: str           # What to say out loud
    priority: int          # 0=low, 1=normal, 2=high, 3=interrupt
    ssml: str | None = None  # Optional SSML for richer speech
```

### 7.2 No silent loading states

If a response takes >500ms, speak a progress message: "Working on it..."

### 7.3 All error messages must be in plain spoken English

No stack traces, error codes, or technical jargon in voice output.

### 7.4 All timeouts must have a spoken fallback

If a service times out, the system must speak a meaningful message before attempting recovery.

---

## 8. Testing

### 8.1 Every module must have unit tests

- Unit tests in `src/module_name/tests/`
- Integration tests in `tests/integration/`
- All tests run with `pytest`

### 8.2 Test coverage requirements

- Core business logic: 90%+
- Service integrations: mocked, 80%+
- Audio I/O: manual test procedures documented

### 8.3 Accessibility tests

Every new voice command or system event must have a test that verifies:
- It emits a `VoiceEvent`
- The `VoiceEvent.message` is non-empty and under 100 characters
- The event priority is appropriate

---

## 9. Documentation

### 9.1 Public API docstrings required

Every public function/method must have a docstring:
```python
async def transcribe(self, audio: bytes) -> str:
    """
    Convert audio bytes to text using configured STT service.

    Args:
        audio: Raw PCM audio data, 16kHz mono, int16

    Returns:
        Transcribed text string, or empty string if silent

    Raises:
        STTConnectionError: If service is unreachable
        STTTimeoutError: If transcription exceeds timeout
    """
```

### 9.2 ADRs for architectural decisions

Any decision that affects the overall architecture must be documented as an Architecture Decision Record (ADR) in `docs/adr/`. See `docs/adr/README.md` for the template.

---

## 10. Git and Versioning

- Branch naming: `feat/module-name`, `fix/issue-description`, `docs/topic`
- Commit messages: imperative present tense: "Add circuit breaker to STT client"
- No commits directly to `main` — PR required with at least one approval
- Semantic versioning: `MAJOR.MINOR.PATCH`

---

## 11. Security

- No API keys or secrets in code or config files
- All secrets loaded from environment variables or a secrets manager
- Audio data never logged or written to disk (only transcript)
- All external HTTP calls use TLS (no plain HTTP to cloud services)
