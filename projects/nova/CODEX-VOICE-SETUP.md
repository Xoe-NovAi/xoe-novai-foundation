# Codex Native Voice Setup

Status: working baseline as of 2026-02-20 on macOS with Codex Desktop.

This setup uses Codex's built-in dictation instead of the Claude `voice-mode` stack.

## What Changes From Claude Setup

- No Whisper service needed.
- No Kokoro service needed.
- No `~/.voicemode` config required.
- No MCP voice bridge required.
- Input voice is native in Codex Desktop ("hold to dictate").

## Native Controls (Codex)

Local app inspection shows Codex has native dictation UI and accelerator bindings:

- `Hold to dictate`
- `Transcribe and send` / `Stop dictation`
- Default dictation shortcut mapping: `Ctrl+M`

## Quick Start

1. Launch Codex in your target workspace:

```bash
/Users/buck/Documents/voice-setup-project/scripts/start-codex-voice.sh /Users/buck/Documents/voice-setup-project
```

2. In Codex, use native dictation:
- Press and hold `Ctrl+M`
- Speak your prompt
- Release to transcribe

3. Send the prompt from the composer (Enter/Cmd+Enter based on your send settings).

## Optional: One-Click Launcher App

Create `/Applications/Start Codex Voice.app`:

```bash
/Users/buck/Documents/voice-setup-project/scripts/install-start-codex-voice-app.sh /Users/buck/Documents/voice-setup-project
```

Then assign a global keyboard shortcut in macOS:
- System Settings -> Keyboard -> Keyboard Shortcuts -> Services
- Assign a shortcut for `Start Codex Voice`

## Optional: Spoken Playback

Codex native voice currently covers dictation (input). If you want spoken playback of responses:

```bash
/Users/buck/Documents/voice-setup-project/scripts/speak-clipboard.sh
```

This reads clipboard text with macOS `say`.

Example:

```bash
/Users/buck/Documents/voice-setup-project/scripts/speak-clipboard.sh "Build succeeded."
```

## Recommended Workflow

1. Speak prompts with `Ctrl+M` hold-to-dictate.
2. Keep responses in text for precision while coding.
3. Use `speak-clipboard.sh` only when you want audio playback.

## Known Limits

- This is not full duplex conversational voice (always-on listen/speak).
- Dictation requires Codex Desktop and microphone permission.
- If microphone access is denied, enable it in:
  System Settings -> Privacy & Security -> Microphone.

