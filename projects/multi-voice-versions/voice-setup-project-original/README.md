# Voice Setup Project

Local voice integration for Claude Code, with a Codex-native path that uses built-in GPT dictation.

## New: Codex Native Voice

If your target is Codex (not Claude Code), start here:

- `/Users/buck/Documents/voice-setup-project/CODEX-VOICE-SETUP.md` - full setup and workflow
- `/Users/buck/Documents/voice-setup-project/scripts/start-codex-voice.sh` - launch Codex into a workspace
- `/Users/buck/Documents/voice-setup-project/scripts/install-start-codex-voice-app.sh` - build `/Applications/Start Codex Voice.app`
- `/Users/buck/Documents/voice-setup-project/scripts/speak-clipboard.sh` - optional macOS TTS helper

Note: this README below is the legacy Claude Code `voice-mode` stack.

## Goal

Get high-quality voice conversation working with Claude Code:
1. **Phase 1 (now):** Local voice using Kokoro (TTS) + Whisper (STT)
2. **Phase 2 (future):** OpenAI cloud voice when API key is available (higher quality)

## Architecture

```
User speech → Whisper STT (port 2022) → Claude Code → Kokoro TTS (port 8880) → Speaker
```

### Local Services

| Service | Role | Port | Tech | Status |
|---------|------|------|------|--------|
| Whisper | Speech-to-Text | 2022 | whisper.cpp + CoreML/Metal | ✅ Installed |
| Kokoro  | Text-to-Speech | 8880 | kokoro-fastapi + MPS GPU  | ✅ Installed |

### Cloud Services (future)

| Provider | Role | Notes |
|----------|------|-------|
| OpenAI   | STT + TTS | Requires `OPENAI_API_KEY`, much higher quality |

## Setup

### Install & Start Services

```bash
# Install (one-time)
uvx voice-mode service install whisper
uvx voice-mode service install kokoro

# Start services
uvx voice-mode service start whisper
uvx voice-mode service start kokoro

# Enable auto-start at login
uvx voice-mode service enable whisper
uvx voice-mode service enable kokoro

# Check status
uvx voice-mode service status
```

### Enable OpenAI (when subscribed)

1. Get API key from https://platform.openai.com/api-keys
2. Add to `~/.voicemode/voicemode.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```
3. Uncomment TTS/STT provider ordering to prefer cloud:
   ```
   VOICEMODE_TTS_BASE_URLS=https://api.openai.com/v1,http://127.0.0.1:8880/v1
   VOICEMODE_STT_BASE_URLS=https://api.openai.com/v1,http://127.0.0.1:2022/v1
   ```
   Or to keep local as default but have cloud as fallback, use the current ordering
   (local first, cloud second).

## Configuration Files

| File | Purpose |
|------|---------|
| `~/.voicemode/voicemode.env` | Main voicemode config |
| `~/.voicemode/services/whisper/` | Whisper service install |
| `~/.voicemode/services/kokoro/` | Kokoro service install |
| `~/.claude.json` | Claude Code MCP server config |

## Key Insights from xoe-novai-foundation Repo

Your existing project uses a more advanced stack:
- **Piper ONNX** for TTS (CPU-optimized, torch-free, <100ms latency)
- **Faster Whisper** (CTranslate2 backend, torch-free)
- **Silero VAD** (ONNX-based voice activity detection)
- 4-level degradation fallback system
- Redis session persistence
- Circuit breaker pattern

For Claude Code's voice-mode MCP, Kokoro + Whisper is the supported path.
Piper ONNX could be an alternative TTS if Kokoro quality is insufficient.

## Voice Quality Comparison

| Option | Quality | Latency | Offline | Cost |
|--------|---------|---------|---------|------|
| Kokoro (local) | ⭐⭐⭐⭐ | ~200ms | ✅ | Free |
| Whisper (local) | ⭐⭐⭐⭐ | <500ms | ✅ | Free |
| OpenAI TTS-1 | ⭐⭐⭐⭐ | ~50ms | ❌ | Pay-per-use |
| OpenAI TTS-1-HD | ⭐⭐⭐⭐⭐ | ~100ms | ❌ | Pay-per-use |
| OpenAI gpt-4o-mini-tts | ⭐⭐⭐⭐⭐ | ~100ms | ❌ | Pay-per-use |
| Piper ONNX | ⭐⭐⭐⭐ | <100ms | ✅ | Free |

## VAD Settings for Your Environment

Default `vad_aggressiveness=2` works for home office. Adjust if needed:
- `0-1`: Quiet room (catches soft speech)
- `2`: Normal home/office (default)
- `3`: Noisy environment

## Progress Log

### 2026-02-20
- Created project folder
- Installed Whisper STT (whisper.cpp with CoreML/Metal acceleration)
  - Model: ggml-base.bin (36.2 MB)
  - GPU: Metal enabled, CoreML active
  - Memory: ~262 MB
- Installed Kokoro TTS (kokoro-fastapi with MPS GPU)
  - 67 voice packs loaded
  - Memory: ~1.28 GB (model loaded on Apple Silicon GPU via MPS)
  - First startup takes ~4 minutes (model download + dependency install)
  - Subsequent startups are faster
- ✅ Enabled auto-start at login (LaunchAgents plist installed)
  - Whisper: ~/Library/LaunchAgents/com.voicemode.whisper.plist
  - Kokoro:  ~/Library/LaunchAgents/com.voicemode.kokoro.plist
- ✅ Tested voice conversation - TTS plays, STT listens
- TODO: Set up OpenAI API key path for future upgrade (Phase 2)
