# VoiceOS -- Project Instructions for Claude

## What This Is

VoiceOS is a voice-first AI platform for developers, with a focus on
accessibility for blind users. It runs on a Mac mini Pro with 64 GB RAM.

## Two Execution Modes

1. **Standalone Python app** (`voiceos start`): Full asyncio voice pipeline.
   Needs an Anthropic API key (`sk-ant-...`) stored in `~/.voiceos/config`.
   Run with: `uv run voiceos start`

2. **Claude CLI voice session** (`voice`): Wrapper script at `~/bin/voice` that
   reads the memory bank from `~/.voiceos/memory_bank/` and launches
   `claude` with MCP `voice-mode`. Uses OAuth (no API key needed).

## Key Directories

- `src/` -- Main Python source (orchestrator, llm router, stt, tts, memory, audio, accessibility)
- `src/llm/llm_router.py` -- LLM routing: Anthropic (cloud) + Ollama (local), rate-limit auto-fallback
- `src/memory/memory_manager.py` -- Persistent memory for standalone app (`~/.voiceos/memory/`)
- `src/config.py` -- Persistent config at `~/.voiceos/config`
- `docs/` -- Architecture, roadmap, user guide
- `tests/` -- Test suite
- `~/.voiceos/memory_bank/` -- Memory bank for Claude CLI voice sessions

## Architecture Credit

Memory bank system inspired by the Xoe-NovAi Foundation Stack:
https://github.com/Xoe-NovAi/xoe-novai-foundation

## Services (always running via LaunchAgents)

- STT: faster-whisper large-v3 on port 2022 (server: `~/.voicemode/services/whisper-large-v3/server.py`)
- TTS: Kokoro on port 8880
- LLM: Ollama on port 11434 (qwen2.5:32b default, qwen2.5-coder:7b for code, phi4-mini for fast)

## Code Style

- Python 3.11+, asyncio throughout
- Type hints on all function signatures
- structlog for logging (not stdlib logging)
- Click for CLI
- uv for package management (pyproject.toml, uv.lock)
- No emojis in code or docs

## Key Design Decisions

- Default LLM mode: `claude_only` (Anthropic API)
- Rate limit (HTTP 429): auto-fallback to local Ollama, auto-recovery from headers
- Circuit breaker: 3 failures opens, 60s timeout, 2 successes closes
- Memory: two-tier (session.json for continuity, long_term.json for facts)
- STT: 20s timeout (large-v3 model needs more than base)
- TTS: Kokoro first, macOS `say` fallback
- Audio: watcher prevents AirPods from hijacking output to "Mac mini Speakers"

## Building for Blind Users

This app targets VoiceOver users. All output must be spoken, not visual.
No emojis in TTS output. Keep responses brief (2 sentences max unless asked).
Documentation uses plain text headings (no visual-only formatting).
