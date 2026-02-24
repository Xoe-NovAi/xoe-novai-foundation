# Voice Assistant Platform — Product Roadmap

**Product Name**: VoiceOS
**Vision**: The first fully voice-controlled AI development environment, built from the ground up for blind and sighted users alike.
**Last Updated**: 2026-02-23
**Owner**: Mark / Buck

---

## Mission

Enable any human — regardless of sight — to build, navigate, and operate software using only their voice. VoiceOS is not an accessibility add-on. It is a first-class voice-native platform where voice is the primary input and all visual interfaces are optional.

---

## Guiding Principles

1. **Voice First, Always** — Every feature must work without a screen. Visual UI is a bonus layer.
2. **Reliability Over Novelty** — A feature that works 99% of the time beats a flashy one that works 80%.
3. **Progressive Disclosure** — Simple commands for simple tasks; depth is available on request.
4. **Open & Composable** — Built on open standards (MCP, OpenAI API spec, WebAudio API). No lock-in.
5. **Transparency** — System always tells the user what it is doing and why. No silent failures.
6. **Privacy by Default** — Local-first processing. Cloud is opt-in.

---

## User Personas

### Primary: Alex (Blind Developer)
- Congenitally blind, uses VoiceOver daily
- Writes Python and shell scripts
- Needs: full system navigation by voice, spoken code feedback, zero-visual-dependency
- Success metric: full development session without touching keyboard or screen

### Secondary: Jordan (Sighted Developer with RSI)
- Has repetitive strain injury, cannot type for long periods
- Needs: voice command for common IDE actions, dictation with code awareness
- Success metric: 80% of coding session completed voice-only

### Tertiary: Sam (Power User)
- Fully sighted, wants voice as a productivity multiplier
- Needs: fast commands, low latency, smart context
- Success metric: faster task completion than keyboard-only

---

## Product Phases

### Phase 0 — Foundation (Current / Feb 2026)
**Status**: In Progress
**Goal**: Working local voice pipeline, documented architecture, research complete

- [x] Whisper STT running locally (port 2022, CoreML + Metal)
- [x] Kokoro TTS running locally (port 8880, MPS)
- [x] voicemode MCP integrated with Claude Code
- [x] LLM architecture research complete
- [ ] Standards and protocols defined
- [ ] Codebase scaffolded with clean module boundaries
- [ ] AudioProcessor module
- [ ] ServiceRegistry with remote discovery

---

### Phase 1 — Core Voice Loop (March 2026)
**Theme**: "It works reliably every time"
**Target User**: Alex (blind developer)

#### Milestones
- [ ] **M1.1** — AudioProcessor: reliable mic capture, noise reduction, silence detection
- [ ] **M1.2** — ServiceRegistry: health-aware discovery for STT, TTS, LLM services
- [ ] **M1.3** — LLMRouter: Ollama-only, Ollama+Claude, Claude-only modes
- [ ] **M1.4** — VoiceOverBridge: integration with macOS VoiceOver (announce responses)
- [ ] **M1.5** — ConversationManager: multi-turn context with sliding window
- [ ] **M1.6** — WakeWord: "Hey VoiceOS" trigger (OpenWakeWord)
- [ ] **M1.7** — CLI launcher: `voiceos start` command

#### Success Criteria
- 10-minute voice-only session without keyboard intervention
- Response latency p95 < 2 seconds end-to-end (STT + LLM + TTS)
- Zero crashes during normal use
- VoiceOver reads all responses correctly

---

### Phase 2 — macOS Integration (April–May 2026)
**Theme**: "Control anything on the Mac by voice"
**Target User**: Alex + Jordan

#### Milestones
- [ ] **M2.1** — AccessibilityController: AXUIElement-based app navigation
- [ ] **M2.2** — AppCatalog: voice shortcuts for common apps (Xcode, Terminal, Safari, VS Code)
- [ ] **M2.3** — ClaudeCodeBridge: voice-driven Claude Code sessions (approve, reject, guide)
- [ ] **M2.4** — CodexBridge: voice-driven Codex sessions (Ctrl+M dictation integration)
- [ ] **M2.5** — ScreenReader: on-demand screen content reading (OCR + accessibility tree)
- [ ] **M2.6** — SystemCommands: volume, brightness, Bluetooth, wifi by voice
- [ ] **M2.7** — NotificationVoice: VoiceOver-style announcement of system notifications

#### Success Criteria
- Open any Mac application and navigate its UI entirely by voice
- Write and run code in Terminal without touching keyboard
- All system settings controllable by voice command

---

### Phase 3 — Intelligence Layer (June–August 2026)
**Theme**: "It understands what you mean, not just what you say"
**Target User**: All personas

#### Milestones
- [ ] **M3.1** — IntentClassifier: route voice commands to correct handler (code, nav, query, system)
- [ ] **M3.2** — ContextMemory: persistent cross-session memory (what I was working on, my preferences)
- [ ] **M3.3** — CodeAwareSTT: vocabulary biasing for code symbols, function names, file paths
- [ ] **M3.4** — SmartSummarizer: condense long code/output into voice-friendly summaries
- [ ] **M3.5** — ErrorDiagnoser: explain compiler/runtime errors in plain spoken language
- [ ] **M3.6** — ProactiveAssistant: "I notice you've said 'undefined' 3 times — want me to debug?"

#### Success Criteria
- 90%+ command intent accuracy on dev workload
- Context carries correctly across session restarts
- Long file contents summarized to under 30 spoken words

---

### Phase 4 — Multi-User & Remote (Q4 2026)
**Theme**: "Use it anywhere, share it with anyone"

#### Milestones
- [ ] **M4.1** — SpeakerIdentification: personalized experience per voice
- [ ] **M4.2** — RemoteServices: SSH into a Mac and control it by voice from another device
- [ ] **M4.3** — TeamSharing: multiple users, shared context, different permission levels
- [ ] **M4.4** — CloudSync: session history, preferences synced across devices
- [ ] **M4.5** — MobileCompanion: iOS app as microphone + speaker relay

---

### Phase 5 — Platform & Ecosystem (2027)
**Theme**: "Build on VoiceOS"

#### Milestones
- [ ] **M5.1** — VoiceOS SDK: third-party developers can register voice commands
- [ ] **M5.2** — Plugin Marketplace: community voice command packs
- [ ] **M5.3** — Fine-tuned Models: custom STT vocabulary, domain-specific LLM fine-tunes
- [ ] **M5.4** — Enterprise Edition: SSO, audit logs, on-premises deployment
- [ ] **M5.5** — Open Source Core: VoiceOS core released as open source

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| STT (local) | Whisper.cpp (CoreML + Metal) | Fast, private, offline |
| STT (cloud) | OpenAI Whisper API | Higher accuracy, cloud fallback |
| TTS (local) | Kokoro FastAPI (MPS) | Natural voice, offline |
| TTS (cloud) | OpenAI TTS / gpt-4o-mini-tts | Highest quality, emotional |
| LLM (local) | Ollama (Llama, Qwen, StarCoder) | Privacy, offline, fast |
| LLM (cloud) | Anthropic Claude (Haiku/Opus) | Best quality, tool use |
| Voice MCP | voice-mode (mbailey) | Claude Code integration |
| Accessibility | PyObjC (AXUIElement + SpeechRecognition) | Native macOS integration |
| Audio I/O | sounddevice + AVFoundation | Cross-platform + native |
| Orchestration | asyncio + Python 3.11+ | Async-first design |
| Config | YAML + env var overrides | 12-factor app |
| Monitoring | Prometheus + structlog | Production observability |

---

## Release Cadence

- **Nightly**: Automated tests + lint
- **Weekly**: Internal demo session
- **Monthly**: Phase milestone review
- **Quarterly**: User research session with Alex persona

---

## Key Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Bluetooth audio hijacking (AirPods) | High | Audio watcher daemon; fixed to Mac mini speakers |
| STT accuracy on code terms | High | Vocabulary biasing in Whisper |
| Ink/TTY stdin issue in Claude Code | Medium | Pre-approve MCP tools; workaround documented |
| Network dependency for cloud LLM | Medium | Local Ollama fallback always available |
| macOS accessibility permissions | Medium | Setup guide + automated permission check |
| Latency spikes (>2s) | Medium | Circuit breaker + local fast path |
| Privacy (cloud STT/LLM) | Low | Local-first default; explicit opt-in for cloud |
