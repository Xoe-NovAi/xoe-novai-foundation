# ADR 0002: Use Silero VAD for Robust Speech Detection

## Status
Accepted

## Context
Initial voice implementations used a primitive RMS-based energy threshold for Voice Activity Detection (VAD). This approach failed in real-world environments with ambient noise (fans, keyboard typing), leading to "infinite listening" loops or accidental interruptions of the AI.

## Decision
We integrated Silero VAD (ONNX) as the primary speech detection engine.
- **Runtime**: ONNX Runtime (CPU-optimized).
- **Fallback**: Remains RMS-based if the ONNX model is missing or fails to load.
- **Threshold**: Set to 300ms of consecutive speech frames to trigger "Barge-in" interruption.

## Consequences
- **Positive**: Significantly higher noise resilience, reduced false triggers, and more natural "Barge-in" UX.
- **Negative**: Adds a small dependency (ONNX Runtime) and model asset (~2MB silero_vad.onnx).
