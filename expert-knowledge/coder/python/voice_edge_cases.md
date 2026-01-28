# 🧠 Voice Assistant Edge-Case Hardening

## Overview
Moving from a prototype to a production voice assistant requires handling messy real-world audio data. The v2.0.5 update focuses on resilience against noise, hardware mismatches, and model hallucinations.

## 1. Whisper Hallucinations
**The Issue**: When Whisper STT receives silent or noisy audio, it often "hallucinates" common training set fillers like *"Thank you for watching"*, *"Please subscribe"*, or *"Subtitles by..."*.
**The Fix**: Implement a post-transcription filter.
- **XNAi Strategy**: Pattern-matching against a blacklist of known "filler" phrases combined with minimum character count thresholds.

## 2. Audio Normalization
**The Issue**: Users speak at different volumes and distances from the microphone. Low-gain audio leads to poor STT accuracy.
**The Fix**: Normalize audio levels before VAD or STT processing.
- **XNAi Strategy**: RMS-based normalization targeting -3dB peak in the `AudioStreamProcessor`.

## 3. Sampling Rate Mismatch
**The Issue**: Browsers often capture audio at 44.1kHz or 48kHz, but neural models (Whisper, Silero) require exactly 16kHz.
**The Fix**: Implement decimation or resampling.
- **XNAi Strategy**: While Chainlit handles some client-side resampling, the server-side should verify and decimate if necessary to prevent "robotic" pitch-shifted audio.

## 4. Acoustic Echo & Barge-in
**The Issue**: AI output from speakers being picked up by the microphone can trigger a "false barge-in", causing the AI to interrupt itself.
**The Fix**: 
1. **Software AEC**: Client-side echo cancellation via WebAudio API.
2. **Confidence Thresholding**: Increase the VAD/Barge-in threshold when AI output is active.
- **XNAi Strategy**: Increased interruption threshold to 300ms (consecutive frames) to ensure high-confidence speech before triggering an interrupt.

## 6. Piper TTS Object Mismatch
**The Issue**: The `piper-tts` library's `synthesize()` method yields `AudioChunk` objects (containing `.audio` bytes and metadata), not raw `bytes`. Passing the object directly to a buffer like `io.BytesIO().write()` results in a `TypeError: a bytes-like object is required`.
**The Fix**: Extract the `.audio` attribute from the yielded object.
- **XNAi Strategy**: Use `getattr(pcm_chunk, 'audio', pcm_chunk)` to ensure compatibility with both object-yielding and bytes-yielding TTS providers.
