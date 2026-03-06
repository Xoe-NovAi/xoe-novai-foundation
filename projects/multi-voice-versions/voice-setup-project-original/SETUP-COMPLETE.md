# Voice Setup - Complete Configuration Reference

**Status:** ✅ Working as of 2026-02-20
**User:** Mark (MARK's Best AirPods Pro as mic, Mac mini Speakers as audio output)

---

## What's Running

| Service | Role | Port | Status | Auto-Start |
|---------|------|------|--------|------------|
| **Whisper STT** | Speech-to-Text | 2022 | ✅ Running | ✅ Login |
| **Kokoro TTS** | Text-to-Speech | 8880 | ✅ Running | ✅ Login |

### Hardware Config (Important)
- **Microphone input:** AirPods Pro (Bluetooth)
- **Audio output:** Mac mini Speakers (wired/built-in)
- This split avoids Bluetooth HFP/A2DP mode-switching latency

---

## How to Start a Voice Conversation

### Option 1: From any Claude Code session (easiest)
In the Claude Code terminal, type:
```
start voice conversation
```
Claude will immediately start speaking and listening.

### Option 2: New session via keyboard shortcut
1. Press your assigned keyboard shortcut (see below)
2. A Terminal window opens and launches Claude Code automatically
3. Claude starts in voice mode immediately

### Option 3: From terminal manually
```bash
claude "start voice conversation"
```

---

## Keyboard Shortcut Setup

An app called **"Start Voice"** was created in `/Applications/Start Voice.app`.

To assign a global keyboard shortcut:
1. Open **System Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Click **Services** in the left panel
3. Scroll to **General** section → find **"Start Voice"**
4. Click "Add Shortcut" and press your desired key combo
   - Suggested: `Control + Option + V`

---

## Volume Control

Volume can be set by Claude during a voice session. Just say:
> "Set the volume to 70 percent"

Or manually:
```bash
osascript -e 'set volume output volume 75'  # 0-100
```

---

## Services Management

```bash
# Check status of all services
uvx voice-mode service status

# Start services manually
uvx voice-mode service start whisper
uvx voice-mode service start kokoro

# Stop services
uvx voice-mode service stop whisper
uvx voice-mode service stop kokoro

# Restart (e.g., if something's stuck)
uvx voice-mode service restart whisper
uvx voice-mode service restart kokoro

# View logs
uvx voice-mode service logs whisper
uvx voice-mode service logs kokoro
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `~/.voicemode/voicemode.env` | Main config — providers, timing, VAD, STT prompt |
| `~/.voicemode/keep-speakers-output.sh` | Audio guardian — keeps Mac mini Speakers as output |
| `~/.claude.json` | Claude Code MCP server definitions |
| `~/.claude/settings.json` | Claude Code permissions + hooks config |
| `~/Library/LaunchAgents/com.voicemode.whisper.plist` | Auto-start plist (Whisper) |
| `~/Library/LaunchAgents/com.voicemode.kokoro.plist` | Auto-start plist (Kokoro) |
| `~/Library/LaunchAgents/com.voicemode.keep-speakers.plist` | Auto-start plist (audio guardian) |
| `/Applications/Start Voice.app` | One-click voice launcher |
| `~/Library/Services/StartVoice.workflow` | Quick Action for keyboard shortcut |

---

## Key Config Settings (`~/.voicemode/voicemode.env`)

```bash
# Bluetooth timing buffer (AirPods Pro)
VOICEMODE_CHIME_LEADING_SILENCE=1.0
VOICEMODE_CHIME_TRAILING_SILENCE=1.5

# Vocabulary biasing — helps Whisper recognize technical/project terms
VOICEMODE_STT_PROMPT=Claude Code, Anthropic, GitHub, Python, JavaScript, TypeScript, npm, API, JSON, YAML, terminal, bash, zsh, Kokoro, Whisper, voicemode, MCP, macOS
```

---

## Adding OpenAI API Key (Phase 2 — when subscribed)

When you have an OpenAI API key, add it to `~/.voicemode/voicemode.env`:
```bash
OPENAI_API_KEY=sk-...your-key-here...
```

Optionally prefer OpenAI over local:
```bash
# Cloud-first (OpenAI primary, local fallback)
VOICEMODE_TTS_BASE_URLS=https://api.openai.com/v1,http://127.0.0.1:8880/v1
VOICEMODE_STT_BASE_URLS=https://api.openai.com/v1,http://127.0.0.1:2022/v1
```

Or keep local-first (current default, cloud as fallback):
```bash
# Just having OPENAI_API_KEY set adds cloud as automatic fallback
```

OpenAI voice quality options:
| Model | Quality | Speed |
|-------|---------|-------|
| `tts-1` | ⭐⭐⭐⭐ | Fast |
| `tts-1-hd` | ⭐⭐⭐⭐⭐ | Medium |
| `gpt-4o-mini-tts` | ⭐⭐⭐⭐⭐ | Medium + emotions |

---

## Known Limitations & Workarounds

### Permission Prompts Require Keyboard
Claude Code permission prompts (e.g., "Allow writing to file? [y/n]")
currently require pressing **Enter** or **y** on the keyboard.

**Workaround options:**
1. Use a permissive trust level in Claude Code settings to reduce prompt frequency
2. *(Future)* A voice-to-keypress script could automate this — see `FUTURE-WORK.md`

### Bluetooth Audio Notes
- **Audio guardian** (`keep-speakers-output.sh`) runs at login and auto-corrects output to Mac mini Speakers every 5 seconds
- macOS tends to grab AirPods as default output when they connect — the guardian prevents this
- AirPods mic works fine as input-only (no mode-switching lag)
- If recording errors appear, wait ~5 seconds for the guardian to correct the output, or run manually:
  ```bash
  /opt/homebrew/bin/SwitchAudioSource -s "Mac mini Speakers"
  ```
- Mac mini has NO built-in microphone — AirPods Pro is the only mic option

### Kokoro First-Start Delay
Kokoro takes ~4 minutes to start on first boot after install (model download + deps).
Subsequent starts are faster (~30-60 seconds for model loading).
Both services auto-start at login, so this only matters after a fresh install.

---

## Troubleshooting

### "Could not record audio"
- Check if AirPods are also set as audio output → switch output to Mac mini Speakers
- Check mic permissions: System Settings → Privacy & Security → Microphone

### "STT service connection failed / timed out"
```bash
uvx voice-mode service restart whisper
```

### "TTS service connection failed"
```bash
uvx voice-mode service restart kokoro
# Note: Kokoro takes 30-60s to restart
```

### "Both services not available" (after reboot)
Services should auto-start. If they don't:
```bash
uvx voice-mode service start whisper && uvx voice-mode service start kokoro
```
Or re-enable auto-start:
```bash
uvx voice-mode service enable whisper
uvx voice-mode service enable kokoro
```

---

## Voice Tips

- **Speak naturally** — Whisper handles conversational speech well
- **Pause after Claude finishes** — wait for the chime before speaking
- **Short responses** — Claude replies faster with shorter TTS (less Bluetooth risk)
- **Volume:** Say "set volume to X percent" or use keyboard volume keys
- **End session:** Say "stop" or "goodbye" or just close the terminal

---

## System Architecture

```
You speak
    ↓
AirPods Pro mic (Bluetooth input only)
    ↓
Whisper STT (port 2022, CoreML + Metal GPU)
    ↓
Claude Code (processes request)
    ↓
Kokoro TTS (port 8880, Apple Silicon MPS GPU, 67 voices)
    ↓
Mac mini Speakers (wired output)
    ↓
You hear

[Background: keep-speakers-output.sh polls every 5s to maintain Mac mini Speakers as output]
```

---

## Session Summary (2026-02-20)

Everything accomplished in the initial voice setup session:

1. ✅ Installed Whisper STT (whisper.cpp v1.8.3, CoreML + Metal, base model)
2. ✅ Installed Kokoro TTS (kokoro-fastapi v0.2.4, 67 voice packs, Apple Silicon MPS)
3. ✅ Both services auto-start at login (LaunchAgents)
4. ✅ Tested full voice conversation — working
5. ✅ Diagnosed and fixed Bluetooth AirPods mode-switching issue
6. ✅ Created audio guardian (`keep-speakers-output.sh`) — auto-corrects output device
7. ✅ Created "Start Voice" app in /Applications + Quick Action for keyboard shortcut
8. ✅ Pre-approved voicemode MCP permissions in Claude Code settings
9. ✅ Added STT vocabulary biasing for technical terms
10. ✅ Project folder fully documented (this file + FUTURE-WORK.md + README.md)
