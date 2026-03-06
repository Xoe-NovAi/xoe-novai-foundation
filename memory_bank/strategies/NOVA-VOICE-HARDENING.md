# Nova Voice Module Hardening & Modularity

**Date:** 2026-02-25
**Author:** Copilot strategy agent

This note outlines areas for Claude Opus 4.6 to focus on when reviewing and enhancing the Nova voice module, and offers guidance on keeping all voice/stack services modular and portable.

## 1. Hardening the Voice Module

1. **Resiliency and graceful degradation**
   - Ensure every external dependency (STT, TTS, wake-word) is wrapped with circuit breakers and can fall back to alternate providers or no-op behavior.
   - Add configurable timeouts on audio processing pipelines to prevent hung tasks. Log and surface alerts when breakers open.

2. **Security and sandboxing**
   - Run model inference (Whisper, Piper) in a sandboxed subprocess or container to isolate crashes and resource exhaustion.
   - Audit audio input for injection/overflow attacks; validate sample rates and channel counts.
   - Implement strict permission controls for microphone access (especially on macOS) and encrypt cached audio data at rest.

3. **Performance and resource management**
   - Add adaptive sampling and batching mechanisms; allow low‑latency vs high‑accuracy modes.
   - Profile CPU/GPU usage and introduce dynamic model selection based on system load (e.g. tiny vs medium Whisper).
   - Monitor memory usage of FAISS/embeddings and prune sessions periodically.

4. **Testing & observability**
   - Expand unit tests for each component (wake word, STT/TTS, rate limiter) and add integration tests simulating real audio streams.
   - Expose Prometheus metrics: `voice_requests_total`, `voice_breaker_state`, `speech_latency_seconds`, etc.
   - Add end‑to‑end scenario tests using audio recordings (automated in CI).

5. **Configuration & feature flags**
   - Centralize all voice settings in `VoiceModuleConfig` with environment overrides and support structured dynamic reload (e.g. via Consul KV).
   - Leverage the existing feature‑flag system for rapid enable/disable or A/B of new algorithms.

6. **Documentation & developer ergonomics**
   - Maintain a voice module handbook that describes the component interfaces, extension points, and recommended providers.
   - Document how to plug in a new STT/TTS provider or wake‑word engine using the `VoiceInterface` abstractions.

## 2. Modularity & Portability of Stack Services

1. **Clear interface/ABI boundaries**
   - Define abstract base classes (`VoiceInterface`, `STTProvider`, `TTSProvider`, `WakeWordDetector`, etc.) in a minimal core package (`xnai-voice-core`).
   - Keep OS‑specific implementations in separate modules (`voice_linux.py`, `voice_macos.py`) that are dynamically selected at runtime.

2. **Plugin architecture**
   - Use entry points (setuptools) or a registry pattern so new providers can be installed independently (e.g. `pip install xnai-voice-piper-gcp`).
   - Allow configuration to refer to plugins by name rather than hard‑coding classes.

3. **Decouple from Chainlit**
   - The voice module should not import Chainlit; instead, expose a clean async API that any web/UI framework can call. This makes it easier to reuse in Nova or other projects.

4. **Separate packages & docs**
   - Publish the voice module as its own Python package with minimal dependencies. Document install/usage separately from the main repo.
   - Include example wrappers for a CLI, a FastAPI service, and a generic event bus.

5. **Containerization and OS abstraction**
   - Provide Dockerfiles for Linux and macOS (where possible via `osxcross` or virtualization) so voice services can run in isolation.
   - Use a hardware abstraction layer for audio I/O so that Nova‑specific CoreAudio code can be swapped with ALSA/Pulse/PortAudio.

6. **Shareable utilities**
   - Extract commonly useful components (e.g. `AudioGuardian`, BT router, memory bank) into standalone repositories or libraries with their own versioning. These became community‑friendly tools as noted in the Nova project distinction document.

## 3. Directives for Opus 4.6

- Review the current `voice_module.py` and `voice_interface.py` along with Nova‑specific Mac components. Identify any hidden OS assumptions or tight coupling.
- Propose refactorings to isolate Mac‑only code behind interfaces so the core module remains portable.
- Suggest a minimal set of metrics and tests required to certify voice module production readiness.
- Generate a draft design for a plugin registry and example provider implementation.

> Opus should treat the voice subsystem as a candidate for extraction into a reusable, language‑agnostic microservice. The goal is to allow other systems (Nova, future mobile clients, etc.) to import or call it with minimal friction.

**End of note.**