# 🧠 Voice Assistant Best Practices (STT/TTS/VAD)

## Overview
Building a responsive, local-only voice assistant requires balancing latency, accuracy, and user experience. The v2.0.4 update for Xoe-NovAi implements several industry best practices.

## 1. Voice Activity Detection (VAD)
**Anti-Pattern**: Simple RMS (Root Mean Square) energy thresholds. These trigger on background noise like fans or typing.
**Best Practice**: Use neural VAD (like **Silero VAD**) via ONNX. It distinguishes human speech from noise with high precision.
- **XNAi Implementation**: `AudioStreamProcessor` uses Silero VAD ONNX with an RMS fallback.

## 2. Barge-in (Interruption)
**Concept**: Allow the user to stop the AI from speaking by simply talking.
**Mechanism**:
1. Monitor incoming audio even while TTS is playing.
2. If speech is detected for X consecutive frames (e.g., 200ms), trigger an interrupt signal.
3. The TTS generator must immediately stop yielding chunks, and the UI must clear its playback queue.
- **XNAi Implementation**: `VoiceInterface.interrupt()` sets a flag checked during Piper's `synthesize` loop.

## 3. Audio Containerization
**The Issue**: Modern browsers (`cl.Audio`) cannot play raw 16-bit PCM chunks directly.
**The Fix**: Wrap raw PCM data in a WAV container (RIFF header).
- **XNAi Implementation**: `synthesize_speech` uses the `wave` module to wrap Piper's raw bytes before sending to Chainlit.

## 4. Visual Feedback & State Management
**User Experience**: Voice users need to know if the system is "listening", "thinking" (processing RAG), or "speaking".
- **XNAi Implementation**: Integrated `cl.context.emitter.set_chat_state` at key pipeline transitions.

## 5. Latency (P95 Targets)
- **STT**: <300ms (achieved with `distil-large-v3-turbo` + CTranslate2).
- **TTS**: <100ms (achieved with Piper ONNX).
- **VAD**: <30ms per chunk.

## 6. Audio Standards
- **Sampling Rate**: 16kHz is the "Golden Mean" for STT/VAD (balance of quality vs. CPU usage).
- **Format**: Mono, 16-bit PCM.
