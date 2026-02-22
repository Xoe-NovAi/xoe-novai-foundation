# Future Work & Enhancements

*Last updated: 2026-02-20 — based on research into current state of Claude Code voice ecosystem*

---

## Priority 1: Voice Permission Approvals — Known Limitation

**Status:** Confirmed architectural blocker as of 2026-02.

Claude Code uses the **Ink** terminal UI library, which explicitly distinguishes between physical keyboard input and programmatic stdin. Even if you convert voice to a keypress signal, Ink won't process it as a valid submission unless it comes from a physical TTY.

GitHub issue [#15553](https://github.com/anthropics/claude-code/issues/15553) (filed Dec 2025) tracks this exact problem. A proposed fix (`CLAUDE_ACCEPT_STDIN_SUBMIT=true` env var) does not yet exist.

**Current best workarounds:**

1. **Pre-approve voicemode MCP tools** (already done) — in `~/.claude/settings.json`:
   ```json
   "permissions": { "allow": ["mcp__voice-mode__converse", "mcp__voice-mode__service"] }
   ```

2. **Reduce prompts via trust level** — In `~/.claude/settings.json`:
   ```json
   { "defaultMode": "acceptEdits" }
   ```
   This bypasses file edit prompts while still requiring approval for bash commands.

3. **Two-stage model (recommended for safety):**
   - Voice → Claude generates plan/code → Review visually → Single keypress to approve

4. **Watch issue #15553** for when Anthropic ships stdin TTY support.

---

## Priority 2: OpenAI Cloud Voice (Phase 2 — when subscribed)

**When:** Once OpenAI subscription is active.

**Steps:**
1. Get API key: https://platform.openai.com/api-keys
2. Add to `~/.voicemode/voicemode.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```
   The system auto-detects it and adds cloud as fallback (local stays primary).

3. For cloud-first (best quality):
   ```
   VOICEMODE_TTS_BASE_URLS=https://api.openai.com/v1,http://127.0.0.1:8880/v1
   VOICEMODE_STT_BASE_URLS=https://api.openai.com/v1,http://127.0.0.1:2022/v1
   ```

**Quality options:**

| Model | Quality | Notes |
|-------|---------|-------|
| `tts-1` | ⭐⭐⭐⭐ | Fast |
| `tts-1-hd` | ⭐⭐⭐⭐⭐ | Better |
| `gpt-4o-mini-tts` | ⭐⭐⭐⭐⭐ | Supports emotional instructions |

```python
# Example with emotional instruction:
converse("I'm excited to help!", tts_instructions="Sound warm and enthusiastic")
```

---

## Priority 3: Better Whisper Model

**Current:** `base` model (36MB, fast, moderate accuracy)
**Upgrade:** `medium` model (~461MB, 25-30s/10min on M-series, excellent accuracy)
**Best:** `large-v3` (~1.5GB, 60s/10min, 10-20% fewer errors than medium)

Apple Silicon benchmarks (M-series):
- base: ~6s per 10 min audio
- medium: ~25-30s per 10 min audio
- large-v3: ~60s per 10 min audio

To upgrade, edit `~/.voicemode/voicemode.env`:
```bash
VOICEMODE_WHISPER_MODEL=medium  # Recommended upgrade
```
Then restart: `uvx voice-mode service restart whisper`

Note: Whisper will download the new model on first start (~461MB for medium).

---

## Priority 4: Kokoro CoreML (Apple Neural Engine Acceleration)

Research found a project [kokoro-coreml](https://github.com/mattmireles/kokoro-coreml) that converts Kokoro from PyTorch/MPS to CoreML, enabling Apple Neural Engine (ANE) acceleration.

ANE is significantly faster than MPS for inference workloads. This could reduce Kokoro's ~200ms TTS latency to ~50-100ms.

**Current Kokoro (MPS):** ~200ms first token, real-time factor 35x-100x
**CoreML/ANE potential:** ~50-100ms first token

To investigate: https://github.com/mattmireles/kokoro-coreml

---

## Priority 5: Kokoro Voice Mixing (Already Available)

Kokoro v0.3.0 (which is installed) supports voice mixing:
```python
# Mix voices: 67% bella + 33% sky
voice = "af_bella(2)+af_sky(1)"
```

Available voices: `af_sky`, `af_bella`, `af_heart`, `af_jessica`, `af_nova`, `af_sarah`, `af_river`, `af_alloy`, `af_aoede` (+ male equivalents)

To set a preferred voice in `~/.voicemode/voicemode.env`:
```bash
VOICEMODE_VOICES=af_sky,af_bella
VOICEMODE_KOKORO_DEFAULT_VOICE=af_sky
```

---

## Priority 6: Audio Device Optimization

### Current Setup (Working)
- **Input:** AirPods Pro mic (Bluetooth)
- **Output:** Mac mini Speakers (built-in)
- **Why:** Separating input/output eliminates Bluetooth HFP/A2DP mode-switching

### Better Option (If Issues Persist)
Use MacBook's built-in mic instead of AirPods mic:
- System Settings → Sound → Input → "MacBook Microphone"
- Completely eliminates Bluetooth for input (zero mode-switching)
- AirPods still handle output (A2DP quality, full stereo)
- Reduce chime timings back to defaults:
  ```bash
  VOICEMODE_CHIME_LEADING_SILENCE=0.2
  VOICEMODE_CHIME_TRAILING_SILENCE=0.3
  ```

Note: Mac mini speakers may not have a built-in mic. Check: System Settings → Sound → Input.

### Audio Switching Tool
The **Ears** app (https://retina.studio/ears) allows keyboard-shortcut audio device switching — useful for quickly toggling between headphone modes.

---

## Priority 7: Wake Word (Long-term)

True hands-free: say "Hey Claude" to start a session without touching the keyboard.

Options:
- **OpenWakeWord** — fully open source, runs locally, ~100MB
- **Porcupine** (picovoice.ai) — free tier, custom wake words
- **Whisper always-on** — high CPU cost, most accurate

This requires a lightweight always-on daemon. Pairs well with the "Start Voice" app already created.

---

## Priority 8: Piper ONNX Alternative TTS

From xoe-novai-foundation repo — Piper ONNX advantages:
- Torch-free (no PyTorch dependency)
- <100ms latency (vs Kokoro ~200ms)
- Much lower memory (~50MB vs Kokoro ~1.3GB)
- CPU-only (no GPU needed)

Trade-off: Voice quality lower than Kokoro's neural synthesis.

Good as low-memory fallback. Kokoro is recommended as primary.

---

## Notes from xoe-novai-foundation Architecture

Patterns worth borrowing if building a custom pipeline:
- **4-level degradation system** (STT → RAG → template → emergency fallback)
- **Circuit breaker pattern** for service failures (opens after 5 failures, 30s recovery)
- **Silero VAD** — better than Whisper's built-in VAD for real-time streaming
- **Bounded audio buffer** — 10s max, FIFO eviction, prevents memory leaks
- **Redis session persistence** — conversation history with 1-hour TTL
