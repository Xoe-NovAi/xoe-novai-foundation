# Voice Control for Codex CLI (Kokoro + faster-whisper)

This project gives you voice-only control of `codex` CLI:

- STT: local [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper)
- TTS: local [`kokoro`](https://github.com/hexgrad/kokoro)
- Command execution: local `codex exec` and optional shell commands

## What it does

- Continuously listens with VAD (voice activity detection).
- Transcribes your speech to text locally.
- Requires wake word by default: `hey codex`.
- Routes commands to:
  - `codex exec` tasks
  - shell commands (`run shell ...`)
  - navigation/status controls
- Speaks results back with Kokoro.
- Requires spoken confirmation for risky tasks/commands.
- Supports interrupting a running task by voice.

## Requirements

- Python 3.10+
- Codex CLI installed and authenticated (`codex login`)
- System dependencies:

```bash
brew install ffmpeg portaudio espeak-ng
```

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
source .venv/bin/activate
python voice_codex_cli.py --cwd /Users/buck/Documents/GPT-voice-setup
```

## Smoke test (no audio dependencies)

Run this to verify wake-word and stop-task routing logic without installing
`faster-whisper`/`kokoro`:

```bash
python smoke_test_voice_codex_cli.py
```

Optional flags:

```bash
python voice_codex_cli.py \
  --cwd /path/to/repo \
  --whisper-model small.en \
  --whisper-device auto \
  --whisper-compute-type int8 \
  --kokoro-voice af_heart \
  --kokoro-lang-code a \
  --kokoro-speed 1.0 \
  --codex-sandbox workspace-write \
  --wake-word "hey codex"
```

## Voice command examples

- `hey codex fix failing tests`
- `hey codex add unit tests for parser`
- `hey codex run shell npm test`
- `hey codex stop running task`
- `hey codex task status`
- `hey codex go to folder src`
- `hey codex where am i`
- `hey codex read last output`
- `hey codex repeat`
- `hey codex exit`

Any unrecognized phrase is treated as a Codex task for fully voice-driven use.

To disable wake-word gating:

```bash
python voice_codex_cli.py --no-wake-word
```

## Safety model

If a command/task is high risk (for example includes `rm`, `git reset --hard`, `force push`, or `delete`), the assistant asks for a spoken one-time phrase like:

- `confirm 4821`

Say `cancel` to abort.

## Notes

- Voice processing is local (Kokoro + faster-whisper).
- Codex reasoning/execution still uses your Codex/OpenAI account through `codex` CLI.
- For best latency on CPU, try `--whisper-model base.en`.

## Cost estimate helper

Use the included script to estimate OpenAI API spend for an API-backed voice architecture:

```bash
python estimate_openai_voice_cost.py \
  --days 22 \
  --user-audio-minutes-per-day 30 \
  --assistant-audio-minutes-per-day 30 \
  --realtime-text-input-tokens-per-day 30000 \
  --realtime-text-output-tokens-per-day 18000 \
  --codex-input-tokens-per-day 150000 \
  --codex-output-tokens-per-day 45000
```
