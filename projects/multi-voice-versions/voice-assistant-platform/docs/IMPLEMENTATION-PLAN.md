# Implementation Plan

**Project**: VoiceOS — Voice Assistant Platform
**Last Updated**: 2026-02-23
**Status**: Phase 0 → Phase 1 transition

---

## Current State (Phase 0 Baseline)

### What's Running
| Service | Status | Location |
|---------|--------|----------|
| Whisper STT | ✅ Running (port 2022) | LaunchAgent |
| Kokoro TTS | ✅ Running (port 8880) | LaunchAgent |
| Ollama | ✅ Running (port 11434) | Manual start |
| voicemode MCP | ✅ Integrated | Claude Code |
| Audio watcher | ✅ Running (daemon) | /tmp/audio_watcher.sh |

### What Exists in Codebase
- `research/llm-voice-systems-research.md` — LLM architecture research
- `docs/PRODUCT-ROADMAP.md` — Product vision and phases
- `docs/ARCHITECTURE.md` — System architecture
- `standards/ENGINEERING-STANDARDS.md` — Coding standards
- `standards/ACCESSIBILITY-STANDARDS.md` — Accessibility requirements

### Ollama Models Available
- `smolvlm2-2.2b-instruct` — 1.1GB (vision model)
- `starcoder2:3b` — 1.7GB (code model)

---

## Phase 1 Implementation Plan

### Sprint 1: Audio Foundation (Week 1)

**Goal**: Reliable audio capture and output with device stability.

#### Task 1.1 — AudioProcessor (`src/audio/audio_processor.py`)

```
Priority: CRITICAL — nothing else works without this
Estimated effort: 2 days
Dependencies: sounddevice, numpy, scipy or noisereduce

What to build:
  - MicCapture class: async audio stream from microphone
  - VADDetector class: detect speech start/end using energy threshold
  - AudioWatcher: monitor output device, restore if hijacked
  - AudioPlayer: play raw PCM audio bytes

Key design decisions:
  - sounddevice callbacks are synchronous (C thread)
  - Bridge to asyncio via asyncio.Queue
  - VAD threshold: tunable, default energy-based
  - 16kHz mono int16 format throughout (Whisper requirement)

Test plan:
  - test_capture_starts_and_stops.py
  - test_vad_detects_speech.py
  - test_audio_watcher_restores_device.py
```

#### Task 1.2 — STTManager (`src/stt/`)

```
Priority: CRITICAL
Estimated effort: 1 day
Dependencies: httpx (async HTTP), existing Whisper on :2022

What to build:
  - STTManager class with Whisper HTTP client
  - Circuit breaker wrapping all calls
  - Health check endpoint poller
  - Fallback to macOS SpeechRecognizer (AVFoundation via PyObjC)

Key design decisions:
  - POST audio/wav to http://127.0.0.1:2022/v1/audio/transcriptions
  - Include vocabulary bias for code terms (function, async, pytest, etc.)
  - Timeout: 10 seconds hard limit
  - Fallback triggers after 3 consecutive failures

Test plan:
  - test_transcribe_returns_text.py (integration, requires Whisper running)
  - test_fallback_triggers_on_timeout.py (mock Whisper)
  - test_circuit_breaker_opens_after_failures.py
```

#### Task 1.3 — TTSManager (`src/tts/`)

```
Priority: CRITICAL
Estimated effort: 1 day
Dependencies: httpx, Kokoro on :8880

What to build:
  - TTSManager class with Kokoro HTTP client
  - Priority queue for speaking events
  - Interrupt support (stop mid-sentence)
  - Fallback to macOS `say` subprocess

Key design decisions:
  - POST to http://127.0.0.1:8880/v1/audio/speech
  - Audio played via sounddevice (not subprocess)
  - Priority queue: 3=interrupt > 2=high > 1=normal > 0=low
  - Interruption: set stop flag, sounddevice.stop()

Test plan:
  - test_speak_plays_audio.py
  - test_interrupt_stops_playback.py
  - test_priority_queue_ordering.py
  - test_fallback_to_say.py
```

---

### Sprint 2: Service Layer (Week 1–2)

#### Task 2.1 — ServiceRegistry (`src/registry/`)

```
Priority: HIGH
Estimated effort: 1 day

What to build:
  - ServiceRegistry class: discover and track STT, TTS, LLM services
  - ServiceConfig dataclass: url, timeout, health_endpoint
  - HealthPoller: background task checking all services every 30s
  - Remote registration: add services by URL

Discovery priority:
  1. Environment variables (VOICEOS_STT_URL, etc.)
  2. ~/.voiceos/config.yaml
  3. Hardcoded local defaults

Remote discovery (Phase 2):
  - mDNS/DNS-SD via zeroconf Python package
  - Service advertisement: voiceos._tcp.local

Test plan:
  - test_discovers_from_env.py
  - test_health_poller_marks_unhealthy.py
  - test_remote_registration.py
```

#### Task 2.2 — LLMRouter (`src/llm/`)

```
Priority: HIGH
Estimated effort: 2 days

What to build:
  - LLMRouter class with three modes
  - OllamaProvider: HTTP client for Ollama API
  - AnthropicProvider: uses anthropic Python SDK
  - CircuitBreaker per provider
  - RequestContext: carries latency budget, request type, user prefs

Three modes:
  class LLMMode(Enum):
      OLLAMA_ONLY = "ollama_only"
      HYBRID = "hybrid"          # Ollama first, Claude fallback
      CLAUDE_ONLY = "claude_only"

Routing logic:
  - code tasks → best available (Opus > Haiku > StarCoder2)
  - fast queries → fastest available (Ollama first)
  - offline mode → Ollama only

Ollama models priority:
  - Code: starcoder2:3b (available) → pull qwen2.5-coder:7b when ready
  - General: smolvlm2-2.2b-instruct (available) → pull llama3.2:3b when ready

Test plan:
  - test_routes_to_ollama_in_ollama_only_mode.py
  - test_falls_back_to_claude_when_ollama_fails.py
  - test_circuit_breaker_stops_routing_to_failed_provider.py
```

---

### Sprint 3: Accessibility Foundation (Week 2–3)

#### Task 3.1 — VoiceEventBus (`src/events/`)

```
Priority: HIGH (required before accessibility)
Estimated effort: 0.5 days

What to build:
  - VoiceEvent dataclass: type, message, priority, ssml
  - VoiceEventBus: asyncio pub/sub
  - TTSManager subscribes to bus
  - VoiceOverBridge subscribes to bus

VoiceEvent schema:
  @dataclass
  class VoiceEvent:
      event_type: str
      message: str
      priority: int = 1  # 0–3
      ssml: str | None = None
      interrupt_current: bool = False
```

#### Task 3.2 — AccessibilityOrchestrator (`src/accessibility/`)

```
Priority: HIGH (core differentiator for blind users)
Estimated effort: 3 days
Dependencies: pyobjc-framework-Accessibility, pyobjc-framework-ApplicationServices

What to build:
  - AccessibilityOrchestrator: main controller
  - AppNavigator: open/focus/navigate macOS apps
  - ElementReader: read AXUIElement labels, roles, values
  - Announcer: post to VoiceOver via NSAccessibilityPostNotification
  - PermissionChecker: verify + guide accessibility permissions at startup

macOS permissions required:
  - Accessibility: kAXTrustedCheckOptionPrompt
  - Checked at startup, guided voice setup if missing

Priority features for blind user:
  1. announce(): speak a message via VoiceOver or TTS
  2. focus_app(): open and focus an application by name
  3. read_focused_element(): describe what's currently focused
  4. list_app_elements(): enumerate interactive elements in focused window
  5. click_element(): activate an element by label

Test plan (manual — requires display):
  - test_announces_via_voiceover.py (integration)
  - test_focus_terminal.py (integration)
  - test_permission_checker.py (unit)
```

#### Task 3.3 — IntentClassifier (`src/intent/`)

```
Priority: MEDIUM (can use simple routing initially)
Estimated effort: 1 day

Phase 1 approach: keyword-based classification
Phase 2 upgrade: small local classifier model

Intent taxonomy v1:
  - nav.*: "open", "go to", "switch to", "focus", "close"
  - code.*: "write", "debug", "explain", "run", "test"
  - system.*: "volume", "brightness", "wifi", "bluetooth"
  - voice.*: "stop", "repeat", "louder", "slower"
  - query.*: everything else → LLM

Classification method:
  - Regex patterns for high-confidence intents (nav, system, voice)
  - LLM classification for ambiguous inputs (using fast local model)
```

---

### Sprint 4: Integration and CLI (Week 3–4)

#### Task 4.1 — VoiceOrchestrator (`src/orchestrator.py`)

```
Priority: HIGH
Estimated effort: 1 day

The main loop:
  1. AudioProcessor.start_capture() → audio stream
  2. VAD detects speech
  3. STTManager.transcribe(audio) → text
  4. IntentClassifier.classify(text) → intent
  5. Route to handler
  6. Handler produces response text + VoiceEvent
  7. TTSManager speaks response

All steps async. Circuit breakers on all service calls.
VoiceEventBus used for all speech output.
```

#### Task 4.2 — CLI (`src/cli.py`)

```
Priority: MEDIUM
Estimated effort: 0.5 days

Commands:
  voiceos start                   Start the voice loop
  voiceos start --mode ollama     Start in Ollama-only mode
  voiceos status                  Check all service health
  voiceos check-permissions       Verify macOS permissions
  voiceos config                  Show current config
  voiceos logs                    Tail the log file

Built with: click or argparse
```

#### Task 4.3 — Configuration (`src/config.py`)

```
Priority: HIGH
Estimated effort: 0.5 days

Config file location: ~/.voiceos/config.yaml
Default config created on first run.

Schema:
  llm:
    mode: hybrid  # ollama_only | hybrid | claude_only
    ollama_url: http://localhost:11434
    anthropic_api_key: ${ANTHROPIC_API_KEY}

  stt:
    url: http://localhost:2022
    model: whisper-base
    vocabulary_bias:
      - async
      - pytest
      - Claude
      - Anthropic

  tts:
    url: http://localhost:8880
    voice: af_sky
    speed: 1.0
    fallback: say

  audio:
    input_device: null  # null = system default
    output_device: "Mac mini Speakers"
    sample_rate: 16000
    vad_silence_duration: 2.5

  accessibility:
    voiceover_integration: true
    announcement_priority: 1
```

---

### Sprint 5: Wake Word + Polish (Week 4)

#### Task 5.1 — WakeWord (`src/wakeword/`)

```
Priority: MEDIUM
Estimated effort: 2 days
Dependencies: openwakeword (Python package)

Wake word: "Hey VoiceOS"
Alternative: "Computer" (easier to say)

Implementation:
  - openwakeword runs continuously in background thread
  - Detection triggers STT capture start
  - Low CPU (~2%) when idle

Custom model option:
  - Record 150 samples of wake phrase
  - Train custom openWakeWord model
  - Better accuracy than generic model
```

---

## File Structure After Phase 1

```
voice-assistant-platform/
├── docs/
│   ├── PRODUCT-ROADMAP.md
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION-PLAN.md
│   └── adr/
│       └── 001-python-asyncio.md
├── standards/
│   ├── ENGINEERING-STANDARDS.md
│   └── ACCESSIBILITY-STANDARDS.md
├── research/
│   └── llm-voice-systems-research.md
├── src/
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── audio_processor.py
│   │   └── tests/
│   ├── stt/
│   │   ├── __init__.py
│   │   ├── stt_manager.py
│   │   └── tests/
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── tts_manager.py
│   │   └── tests/
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── llm_router.py
│   │   ├── providers/
│   │   │   ├── ollama.py
│   │   │   └── anthropic.py
│   │   └── tests/
│   ├── registry/
│   │   ├── __init__.py
│   │   ├── service_registry.py
│   │   └── tests/
│   ├── intent/
│   │   ├── __init__.py
│   │   ├── intent_classifier.py
│   │   └── tests/
│   ├── accessibility/
│   │   ├── __init__.py
│   │   ├── accessibility_orchestrator.py
│   │   ├── app_navigator.py
│   │   ├── element_reader.py
│   │   ├── voiceover_bridge.py
│   │   └── tests/
│   ├── events/
│   │   ├── __init__.py
│   │   └── voice_event_bus.py
│   ├── conversation/
│   │   ├── __init__.py
│   │   └── conversation_manager.py
│   ├── config.py
│   ├── cli.py
│   └── orchestrator.py
├── tests/
│   └── integration/
├── deployment/
│   ├── launchagent-voiceos.plist
│   └── setup.sh
└── pyproject.toml
```

---

## Dependencies (`pyproject.toml`)

```toml
[project]
name = "voiceos"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Audio
    "sounddevice>=0.4.6",
    "numpy>=1.26",
    "scipy>=1.11",

    # HTTP clients
    "httpx>=0.27",
    "anthropic>=0.34",

    # Config
    "pyyaml>=6.0",
    "pydantic>=2.0",

    # Logging
    "structlog>=24.0",

    # CLI
    "click>=8.1",

    # macOS accessibility
    "pyobjc-framework-Accessibility>=10.0",
    "pyobjc-framework-ApplicationServices>=10.0",
    "pyobjc-framework-AVFoundation>=10.0",

    # Wake word (Phase 1 Sprint 5)
    "openwakeword>=0.6",
]

[project.scripts]
voiceos = "src.cli:main"
```

---

## Known Risks

| Risk | Phase | Mitigation |
|------|-------|-----------|
| PyObjC compatibility with macOS 15 | Phase 1 | Test early; fallback to subprocess osascript |
| Whisper timeout on long audio | Phase 1 | 10s hard limit; VAD ensures audio is short |
| Kokoro voice quality for code terms | Phase 1 | Custom pronunciation dict; SSML markup |
| OpenWakeWord false positive rate | Phase 1 | Tune threshold; custom model improves it |
| Ollama model quality for code | Phase 1 | Use StarCoder2 for code; pull better model |
| asyncio + sounddevice threading | Phase 1 | Use call_soon_threadsafe; well-documented pattern |

---

## Definition of Done (Phase 1)

A Phase 1 milestone is complete when:
1. All unit tests pass (`pytest src/`)
2. Integration test: 10-minute voice session completes without crash
3. Eyes-closed test: all milestone features usable without screen
4. VoiceOver compatibility test: responses read correctly
5. Documentation updated in `docs/`
6. No hardcoded secrets, URLs, or timeouts in business logic
