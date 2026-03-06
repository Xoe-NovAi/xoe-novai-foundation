# VoiceOS User Guide

This guide is written for screen reader users and anyone who prefers voice-first
interaction with their Mac. All instructions are text-based with no visual-only
elements. Keyboard shortcuts are listed where applicable.

Project: VoiceOS, Voice Assistant Platform for Developers
Hardware requirement: Mac with Apple Silicon, 16 GB RAM minimum (64 GB recommended)

---

## Quick Start

There are two ways to use VoiceOS:

### Option A: Claude CLI Voice Session (Recommended)

This uses Claude Code CLI with the MCP voice-mode server. No API key
configuration needed; it uses your existing Claude account via OAuth.

1. Open Terminal (Command+Space, type Terminal, press Enter).
2. Type: voice
3. Press Enter. The voice session begins. Speak naturally.
4. Say "stop listening" or press Control+C to end the session.

The "voice" command automatically loads your memory bank from previous sessions
so conversation continues where you left off.

Flags:
- voice --fresh: Start without loading previous session context.
- voice --show-context: Preview what context will be injected before starting.

### Option B: Standalone VoiceOS App

This runs the full VoiceOS Python pipeline with more control over routing.
Requires a one-time API key setup for cloud mode.

1. Open Terminal.
2. Type: voiceos start
3. Press Enter. VoiceOS announces readiness and begins listening.
4. Press Control+C to stop.

First-time setup for cloud mode:
  voiceos set-key sk-ant-api03-YOUR-KEY-HERE
  voiceos use-cloud

Get your API key at: https://console.anthropic.com/settings/keys

---

## Voice Commands

All commands are spoken naturally. No wake word is needed; VoiceOS is always
listening when active.

### General Conversation

Just speak. VoiceOS processes your speech and responds verbally.
Examples:
- "What time is it?"
- "Explain how Python decorators work."
- "Write a function that sorts a list of numbers."

### Navigation (macOS App Control)

- "Open Terminal" -- opens or switches to Terminal.
- "Open Safari" -- opens or switches to Safari.
- "Switch to Finder" -- brings Finder to front.
- "Focus Xcode" -- brings Xcode to front.

### Provider Switching

Switch between cloud AI (Claude) and local AI (Ollama) by voice:

- "Switch to cloud" or "Use Claude" -- uses Anthropic API for all queries.
- "Switch to local" or "Go offline" -- uses local Ollama only. Fully private.
- "Switch to hybrid" -- tries local first, cloud as backup.
- "What mode are you in?" or "Which AI?" -- announces current provider.

All mode changes are saved and persist across restarts.

### Memory Commands

VoiceOS remembers things about you across sessions:

- "Remember that I prefer Python over JavaScript." -- saves to long-term memory.
- "What do you remember?" -- lists saved facts about you.
- "Forget everything" -- clears all stored memory.

Memory is also extracted automatically every 10 conversation turns.

### Voice Control

- "Stop" or "Be quiet" -- interrupts the current response.
- "Repeat that" or "Say that again" -- replays the last response.
- "What can you do?" -- lists available commands.
- "Status" -- checks health of all services.

---

## Memory Bank

VoiceOS uses a persistent memory bank inspired by the Memory Bank Protocol from
the Xoe-NovAi Foundation Stack:
https://github.com/Xoe-NovAi/xoe-novai-foundation

Memory is stored at: ~/.voiceos/memory_bank/

### How It Works

Session Start: The "voice" command reads your memory bank and injects it as
context into the Claude session. This means Claude knows your name, preferences,
and what you discussed last time.

During Session: Each voice exchange (what Claude says and what you say back)
is archived to a daily log file in conversations/ as JSONL.

Session End: When the session stops, the memory bank is updated with a summary
of what was discussed and any facts you asked to be remembered.

### Memory Files

context.md: Long-term facts about you and your environment. Persistent across
all sessions. Edit manually with: voice-memory --context

activeContext.md: Summary of your last session. Auto-updated when a voice session
ends. Loaded automatically at next session start.

progress.md: Log of all sessions (date, turn count, duration).

conversations/: Daily archive files in JSONL format. One file per day. Searchable.

### Managing Memory

From the command line:

voice-memory: Show memory bank status (archive count, last session info).
voice-memory --context: Open long-term facts in your text editor.
voice-memory --clear: Clear last-session context (keeps long-term facts).
voice-memory --history: Show recent session log.
voice-memory --search TERM: Search conversation archives for a word or phrase.

---

## Configuration

### Viewing Current Configuration

  voiceos config

This shows all active settings: LLM mode, API key status (masked), STT and TTS
URLs, Ollama models, and audio output device.

### Switching Modes

  voiceos use-cloud: Switch to Claude (cloud) mode. Saves setting.
  voiceos use-local: Switch to Ollama (local) mode. Saves setting.
  voiceos use-hybrid: Switch to hybrid mode. Saves setting.

These can also be done by voice during a session.

### Configuration File

Settings are stored at: ~/.voiceos/config

This is a simple key=value file (one per line). It stores:
- ANTHROPIC_API_KEY: Your Claude API key (chmod 0600, owner-only readable).
- VOICEOS_LLM_MODE: Current mode (claude_only, ollama_only, hybrid).

Environment variables override the config file.

---

## Services

VoiceOS depends on local services that run in the background:

### Speech-to-Text: faster-whisper large-v3
- Port: 2022
- Model: 2.9 GB, already cached locally
- LaunchAgent: com.voiceos.whisper-large-v3
- Starts automatically at login

### Text-to-Speech: Kokoro
- Port: 8880
- Uses Apple Silicon GPU (MPS) for fast synthesis
- LaunchAgent: com.voicemode.kokoro
- Starts automatically at login

### LLM: Ollama
- Port: 11434
- Default model: qwen2.5:32b (20 GB, fits in 64 GB unified memory)
- Code model: qwen2.5-coder:7b
- Fast model: phi4-mini

### Checking Service Health

  voiceos status

This checks all services and reports healthy or unhealthy for each.

---

## Failsafe Behavior

VoiceOS is designed to never go silent:

1. Cloud rate limit (HTTP 429): Automatically falls back to local Ollama.
   Announces the switch via voice. Automatically switches back to Claude when
   the rate limit window resets (parses reset headers from Anthropic API).

2. No API key: Falls back to local Ollama automatically. The "voiceos set-key"
   command saves your key persistently.

3. Ollama not running: Voice error message. No crash.

4. STT/TTS service down: Circuit breaker opens after 3 failures. Retries after
   60 seconds. Emergency fallback to macOS "say" command for TTS.

---

## macOS Permissions

VoiceOS needs two permissions:

1. Microphone: Required for voice input.
   System Settings, Privacy and Security, Microphone.

2. Accessibility: Required for app navigation commands.
   System Settings, Privacy and Security, Accessibility.

Check permissions:
  voiceos check-permissions

If permissions are missing, the command will offer to open the relevant
System Settings pane.

---

## Troubleshooting

Problem: "voice" command not found.
Solution: Close and reopen Terminal, or run: export PATH="$HOME/bin:$PATH"

Problem: No sound output.
Solution: Check that "Mac mini Speakers" is the output device. VoiceOS
  includes an audio watcher that prevents AirPods from hijacking output.

Problem: Claude says API key is not set.
Solution: Run: voiceos set-key sk-ant-YOUR-KEY
  Or use the "voice" command which uses Claude Code OAuth (no key needed).

Problem: Slow responses from local AI.
Solution: The qwen2.5:32b model needs 90 seconds timeout. If still slow,
  try: voiceos use-cloud to switch to Claude.

Problem: Memory not loading.
Solution: Run: voice-memory to check status. Ensure ~/.voiceos/memory_bank/
  exists and has context.md and activeContext.md files.

---

## Architecture Credits

Memory bank system inspired by the Memory Bank Protocol from:
Xoe-NovAi Foundation Stack
https://github.com/Xoe-NovAi/xoe-novai-foundation

Key patterns: external brain for AI session continuity, dual-tier memory
(session state plus long-term facts), event-based JSONL logging, resilience-first
I/O with atomic writes and graceful degradation.
