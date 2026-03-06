# VoiceOS

Voice-first AI platform for developers, built with accessibility in mind.
Runs on macOS with Apple Silicon.

## Features

- Voice conversation with Claude (cloud) or Ollama (local)
- Automatic failover between cloud and local AI
- Persistent memory across sessions (Xoe-NovAi memory bank pattern)
- macOS app navigation via Accessibility API
- Rate-limit auto-fallback with silent recovery
- Three modes: cloud only, local only, hybrid

## Quick Start

### Option 1: Claude CLI Voice Session (recommended)

Uses your existing Claude account. No API key needed.

    voice

Memory from previous sessions loads automatically.

### Option 2: Standalone App

    uv run voiceos start

First time setup for cloud mode:

    uv run voiceos set-key sk-ant-YOUR-KEY
    uv run voiceos use-cloud

## Requirements

- macOS with Apple Silicon
- Python 3.11+ (managed by uv)
- Ollama (for local AI)
- faster-whisper large-v3 (STT, port 2022)
- Kokoro (TTS, port 8880)

## Documentation

- docs/VOICE-USER-GUIDE.md: Complete user guide (screen-reader friendly)
- docs/ARCHITECTURE.md: System architecture and module design
- docs/PRODUCT-ROADMAP.md: Feature roadmap
- docs/IMPLEMENTATION-PLAN.md: Development plan

## Voice Commands

    "Switch to cloud" / "Switch to local" / "Switch to hybrid"
    "Open Terminal" / "Open Safari" / any app name
    "Remember that I prefer Python"
    "What do you remember?"
    "Status"
    "Repeat that"

## CLI Commands

    voiceos start            Start the voice loop
    voiceos status           Check service health
    voiceos config           Show configuration
    voiceos set-key KEY      Save Anthropic API key
    voiceos use-cloud        Switch to Claude mode
    voiceos use-local        Switch to local Ollama mode
    voiceos use-hybrid       Switch to hybrid mode
    voiceos memory           Show memory status
    voiceos check-permissions  Check macOS permissions

## Memory Management

    voice-memory             Show memory bank status
    voice-memory --context   Edit long-term facts
    voice-memory --history   Show session history
    voice-memory --search X  Search conversation archives
    voice-memory --clear     Clear last session context

## Architecture Credits

Memory bank system inspired by the Memory Bank Protocol from the
Xoe-NovAi Foundation Stack:
https://github.com/Xoe-NovAi/xoe-novai-foundation

## License

Private project.
