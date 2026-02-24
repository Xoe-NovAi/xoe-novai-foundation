# System Architecture

**Project**: VoiceOS — Voice Assistant Platform
**Version**: 1.0
**Last Updated**: 2026-02-23

---

## Overview

VoiceOS is a modular, async-first voice processing pipeline. Each layer is independently replaceable. All modules communicate through defined interfaces. No module has a hard dependency on another module's implementation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER LAYER                                  │
│            (Voice In) ◄──────────────────► (Voice Out)              │
└─────────────┬────────────────────────────────────┬──────────────────┘
              │ audio                               │ speech
┌─────────────▼────────────────────────────────────▼──────────────────┐
│                        AUDIO I/O LAYER                               │
│  AudioProcessor                              TTSManager              │
│  - Mic capture (sounddevice)                 - Kokoro (local)        │
│  - Noise reduction                           - OpenAI TTS (cloud)   │
│  - VAD / silence detection                   - macOS say (fallback) │
│  - Audio routing watcher                     - SSML rendering       │
└─────────────┬────────────────────────────────────▲──────────────────┘
              │ raw audio bytes                     │ text to speak
┌─────────────▼─────────────────────┐  ┌───────────┴──────────────────┐
│          STT LAYER                │  │       VOICE EVENT BUS        │
│  STTManager                       │  │  - VoiceEvent dispatch       │
│  - Whisper local (port 2022)      │  │  - Priority queue            │
│  - OpenAI Whisper (cloud)         │  │  - VoiceOver bridge          │
│  - Auto fallback                  │  │  - Interrupt handling        │
└─────────────┬─────────────────────┘  └──────────────────────────────┘
              │ transcribed text
┌─────────────▼────────────────────────────────────────────────────────┐
│                       INTENT LAYER                                    │
│  IntentClassifier                                                     │
│  - Command type detection (code, nav, query, system, accessibility)  │
│  - Context-aware: considers conversation history                     │
│  - Routes to correct handler                                         │
└──────┬─────────┬──────────────┬──────────────┬──────────────┬────────┘
       │         │              │              │              │
  ┌────▼──┐  ┌───▼───┐  ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
  │ CODE  │  │ QUERY │  │ SYSTEM NAV  │ │ ACCESS. │ │ LLMROUTER   │
  │Handler│  │Handler│  │   Handler   │ │ Handler │ │(all complex)│
  └────┬──┘  └───┬───┘  └──────┬──────┘ └────┬────┘ └──────┬──────┘
       │         │              │              │              │
┌──────▼─────────▼──────────────▼──────────────▼──────────────▼──────┐
│                         LLM LAYER                                    │
│  LLMRouter                                                           │
│  - Ollama (local): Llama, Qwen, StarCoder (port 11434)              │
│  - Claude (cloud): Haiku (fast), Opus (quality)                     │
│  - Mode: Ollama-only | Ollama+Claude | Claude-only                  │
│  - Circuit breaker per provider                                      │
│  - Cost + latency tracking                                           │
└─────────────┬────────────────────────────────────────────────────────┘
              │ response text
┌─────────────▼────────────────────────────────────────────────────────┐
│                   RESPONSE FORMATTER                                  │
│  - Strips markdown (not speakable)                                   │
│  - Truncates to voice-appropriate length                             │
│  - Adds SSML for prosody (pauses, emphasis)                         │
│  - Emits VoiceEvent for announcement                                 │
└─────────────┬────────────────────────────────────────────────────────┘
              │ formatted speech text
   (feeds back to Voice Event Bus → TTS)
```

---

## Module Descriptions

### AudioProcessor (`src/audio/`)

Responsible for all audio capture and output device management.

**Key responsibilities:**
- Capture raw audio from microphone (16kHz, mono, int16)
- Perform voice activity detection (VAD) to detect speech start/end
- Apply noise reduction (spectral subtraction or RNNoise)
- Monitor and restore audio output device (anti-AirPods-hijack watcher)
- Provide stream interface for continuous capture

**Key interfaces:**
```python
class AudioProcessor:
    async def start_capture(self) -> AsyncIterator[AudioChunk]
    async def play(self, audio: bytes) -> None
    def set_output_device(self, device_name: str) -> None
    def get_current_output_device(self) -> str
```

---

### STTManager (`src/stt/`)

Converts audio bytes to text using configured STT backends.

**Backends (in priority order):**
1. Local Whisper (port 2022) — default, private, fast
2. OpenAI Whisper API — cloud fallback, higher accuracy
3. macOS Speech Recognition — emergency fallback, no dependencies

**Key interfaces:**
```python
class STTManager:
    async def transcribe(self, audio: bytes) -> TranscriptResult
    async def health_check(self) -> ServiceHealth
```

---

### TTSManager (`src/tts/`)

Converts text to speech using configured TTS backends.

**Backends (in priority order):**
1. Kokoro (port 8880, MPS) — local, natural voice
2. OpenAI TTS / gpt-4o-mini-tts — cloud, highest quality
3. macOS `say` — emergency fallback, always available

**Key interfaces:**
```python
class TTSManager:
    async def speak(self, text: str, priority: int = 1) -> None
    async def speak_ssml(self, ssml: str, priority: int = 1) -> None
    def interrupt(self) -> None
```

---

### ServiceRegistry (`src/registry/`)

Discovers and tracks health of all services (STT, TTS, LLM, Accessibility).

**Discovery methods:**
1. Environment variables (`VOICEOS_STT_URL`, etc.)
2. Config file (`~/.voiceos/config.yaml`)
3. mDNS/DNS-SD (local network auto-discovery)
4. Hardcoded defaults

**Key interfaces:**
```python
class ServiceRegistry:
    async def get_service(self, name: str) -> ServiceConfig
    async def health_check_all(self) -> dict[str, ServiceHealth]
    def register_remote(self, name: str, url: str) -> None
```

---

### LLMRouter (`src/llm/`)

Routes requests to the appropriate LLM provider based on context, mode, and availability.

**Modes:**
- `ollama_only` — never calls cloud, works offline
- `hybrid` — local first, cloud fallback
- `claude_only` — always uses Anthropic API

**Routing logic:**
1. Classify request type (code, query, system, accessibility)
2. Check latency budget for request type
3. Check circuit breaker status for each provider
4. Route to fastest healthy provider within latency budget

**Key interfaces:**
```python
class LLMRouter:
    async def complete(self, messages: list[Message], context: RequestContext) -> LLMResponse
    async def stream(self, messages: list[Message], context: RequestContext) -> AsyncIterator[str]
    def set_mode(self, mode: LLMMode) -> None
```

---

### IntentClassifier (`src/intent/`)

Determines what the user wants to do from transcribed text.

**Intent categories:**
| Category | Examples | Handler |
|----------|---------|---------|
| `code.write` | "Write a function to..." | LLMRouter → Code mode |
| `code.debug` | "Why is this failing?" | LLMRouter → Debug mode |
| `code.read` | "What does this file do?" | LLMRouter → Explain mode |
| `nav.app` | "Open Terminal" | AccessibilityController |
| `nav.web` | "Search for..." | BrowserController |
| `system.control` | "Turn up volume" | SystemController |
| `system.query` | "What time is it?" | LLMRouter → Fast mode |
| `voice.control` | "Stop talking" / "Repeat that" | TTSManager direct |
| `session.control` | "Start new session" / "What did I say?" | ConversationManager |

---

### AccessibilityOrchestrator (`src/accessibility/`)

Integrates with macOS VoiceOver and Accessibility API.

**Capabilities:**
- Navigate any macOS app using AXUIElement
- Post announcements to VoiceOver queue
- Read screen content (accessibility tree + OCR fallback)
- Trigger keyboard shortcuts programmatically
- Monitor and respond to system notifications

**Key interfaces:**
```python
class AccessibilityOrchestrator:
    async def focus_app(self, app_name: str) -> None
    async def read_focused_element(self) -> str
    async def click_element(self, label: str) -> None
    async def type_text(self, text: str) -> None
    async def announce(self, message: str, priority: int = 1) -> None
    async def get_screen_summary(self) -> str
```

---

### ConversationManager (`src/conversation/`)

Manages multi-turn conversation context across sessions.

**Features:**
- Sliding window context (last N turns)
- Automatic summarization when context fills
- Session persistence to disk (encrypted)
- "What did I say?" and "Where were we?" commands

---

### VoiceEventBus (`src/events/`)

Central pub/sub bus for all voice events.

**Event flow:**
1. Any module emits a `VoiceEvent`
2. Bus applies priority ordering
3. TTSManager subscribes and speaks events in order
4. VoiceOverBridge also subscribes for VoiceOver integration

---

## Data Flow: Complete Voice Turn

```
1. Microphone captures audio
   AudioProcessor → detects VAD start/end

2. Audio sent to STT
   STTManager.transcribe(audio) → "Open Terminal"

3. Intent classified
   IntentClassifier.classify("Open Terminal") → Intent(nav.app, app="Terminal")

4. Handler invoked
   AccessibilityOrchestrator.focus_app("Terminal")

5. VoiceEvent emitted
   VoiceEvent(message="Opening Terminal", priority=1)

6. Event spoken
   TTSManager.speak("Opening Terminal")
```

---

## Deployment Topology

```
Mac mini (Primary)
├── Whisper STT       :2022  (LaunchAgent, auto-start)
├── Kokoro TTS        :8880  (LaunchAgent, auto-start)
├── Ollama LLM        :11434 (LaunchAgent or manual)
├── VoiceOS Core      (CLI process or LaunchAgent)
└── Audio Watcher     (background daemon)

Cloud (Optional / Fallback)
├── Anthropic API     (Claude Haiku / Opus)
└── OpenAI API        (Whisper / TTS — when subscribed)
```

---

## Future: Remote Node Support

```
Remote Machine (e.g., laptop)
├── VoiceOS Core      (mic + speaker on remote)
└── ServiceProxy      (tunnels to Mac mini services)

Mac mini (Server)
├── All services running as above
└── Accepts remote connections (authenticated)
```
