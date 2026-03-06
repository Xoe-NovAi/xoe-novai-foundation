# Chainlit Voice Interface Patterns (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **Chainlit** (v1.3+) serves as the primary conversational frontend. It is specifically optimized for "Voice-First" AI interactions, utilizing a low-latency, local-only audio processing stack based on `faster-whisper` and `Piper` (ONNX).

---

## 🎙 Optimized Audio Stack (2026)

To achieve the "Gold Standard" of <1s conversational latency on the Ryzen 5700U, the following stack is employed:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **STT** (Speech-to-Text) | `faster-whisper` | 4x faster than standard Whisper (CTranslate2) |
| **TTS** (Text-to-Speech) | `Piper` (ONNX) | Human-like speech generation in <100ms |
| **Inference Engine** | `ONNX Runtime` | Hardware-accelerated execution |
| **VAD** | `Silero VAD` | Voice Activity Detection for hands-free flow |

---

## 🛠 Voice Patterns & Implementation

The XNAi stack uses three primary Chainlit decorators to manage the audio lifecycle:

### 1. `@cl.on_audio_chunk` (Streaming)
Processes raw audio bytes in real-time as the user speaks.
- **Buffer Strategy**: Append chunks to `cl.user_session["audio_buffer"]`.
- **Optimization**: Use 16kHz mono sampling across the entire pipeline.

### 2. `@cl.on_audio_end` (Transcription)
Triggered by VAD or manual stop, initiating the final STT and LLM processing.
- **Workflow**: Buffer → `faster-whisper` (int8/float16) → LLM → TTS.

### 3. `cl.Audio` (Synthesis)
Sends synthesized speech back to the user with `autoplay=True`.
- **Streaming TTS**: Split LLM output into sentences and synthesize in parallel to hide latency.

---

## 📈 Operational Workflows

### 1. "Hands-Free" Mode
By combining VAD with `cl.on_audio_end`, the system automatically processes speech when the user pauses, enabling a continuous voice-to-voice experience.

### 2. "Barge-in" Support
If the user starts speaking while the AI is playing audio, the VAD triggers a "stop" command to the audio player, allowing the user to interrupt naturally.

### 3. Browser Compatibility
- **Chrome/Edge**: Best performance, fully supports `AudioContext` autoplay.
- **Firefox/Safari**: Requires an initial user gesture (e.g., clicking a "Start" button) to enable audio output.

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| High Audio Latency | Sampling rate mismatch | Ensure 16kHz mono throughout the pipeline. |
| Audio Popping | Buffer underrun during TTS | Increase sentence-buffer size or use streaming synthesis. |
| No Audio Output | Browser autoplay policy | Add a "Start Conversation" button to trigger `AudioContext`. |

---

## 📚 References
- [Chainlit Documentation](https://docs.chainlit.io/)
- [Faster-Whisper Project](https://github.com/SYSTRAN/faster-whisper)
- [Piper TTS Project](https://github.com/rhasspy/piper)
