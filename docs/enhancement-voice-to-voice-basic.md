**Voice-to-Voice Briefing for Cline: Sovereign Execution Parameters**

Cline — elite engineer, refactorer, auditor — you are now tasked with activating the full voice-to-voice pipeline (STT → LLM → TTS) in `app/XNAi_rag_app/voice_interface.py`. This is a high-impact enhancement: Phase 1.5 voice integration, Maat Ideal 41 (advance through own abilities) in action. Success = sub-300ms end-to-end latency on Ryzen 5700U, torch-free, zero-telemetry, fully local.

**Critical Ground Truth from EKB**

1. **Hardware Target** (`ryzen-hardening-expert-v1.0.0.md`)
   - Ryzen 7 5700U (8c/16t Zen 2, Vega 8 iGPU)
   - 8GB RAM baseline — keep footprint <2GB resident
   - Audio spec: 16 kHz, 16-bit PCM mono, 200ms barge-in threshold

2. **Model Loadout** (locked, no substitutions)
   - STT: `distil-large-v3` via Faster-Whisper (CTranslate2 format)
   - TTS: `en_US-john-medium.onnx` via Piper-ONNX runtime
   - VAD: `silero_vad.onnx`
   - All inference must remain torch-free — ONNX Runtime only

3. **Dependency Rules** (zero-cost, sovereign)
   - Use `uv` exclusively for package resolution (project standard)
   - Install into project venv only — never system-wide
   - Prefer pre-built wheels; no compilation unless unavoidable
   - Required runtime packages:
     • `onnxruntime` (CPU build, Vulkan if available)
     • `piper-tts` (ONNX variant)
     • `faster-whisper`
     • `sounddevice`, `soundfile` (audio I/O)
     • `redis` (session queue, local socket only)
   - Block any package that pulls PyTorch or CUDA

4. **Security & Architecture Mandates** (`sovereign-trinity-expert-v1.0.0.md`)
   - Run everything rootless
   - No network calls from voice workers
   - Validate model file hashes before load (add integrity checks)
   - Circuit breakers and graceful degradation required

5. **Implementation Priorities**
   - Streaming pipeline first (real-time VAD → STT → LLM → TTS)
   - Fallback chain: Piper-ONNX → pyttsx3 (offline only) → silent failure
   - Latency monitoring hooks (log per-segment ms)
   - Zero external audio device config assumptions — auto-detect

**Risks to Neutralize**
- Model format mismatch (Gemma ONNX mentioned elsewhere — ignore; use only john-medium)
- ONNX Runtime Vulkan acceleration not auto-enabled on Ryzen — force if possible
- Redis default port conflicts — bind Unix socket only

**Success Criteria**
- End-to-end conversation loop works locally with <300ms perceived latency
- All new code passes existing tests + new voice smoke suite
- No new telemetry or cloud dependencies introduced
- Full changes documented in `enhancements/enhancement-voice-to-voice-basic.md` update

**Next Actions**
1. Ingest this briefing + `ryzen-hardening-expert-v1.0.0.md` + `enhancement-voice-to-voice-basic.md`
2. Create task lock `_meta/locks/task-voice-to-voice-pipeline.yaml` (owner: Cline)
3. Execute dependency installation via `uv` in clean venv
4. Implement pipeline with streaming, fallbacks, latency logging
5. Run full validation on hardware, report metrics

Questions for momentum:
- Estimated completion window?
- Any model file path changes needed from current layout?
- Preferred wake-word trigger (default “Hey Xoe” or none)?

Execute with precision. This pipeline is the voice of sovereignty.

— Grok MC