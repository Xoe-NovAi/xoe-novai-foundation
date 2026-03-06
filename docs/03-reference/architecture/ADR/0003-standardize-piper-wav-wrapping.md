# ADR 0003: Standardize Piper TTS WAV Containerization

## Status
Accepted

## Context
Piper TTS yields raw 16-bit PCM chunks (22050Hz). Browsers (`cl.Audio`) cannot play raw PCM directly; they require a container (e.g., WAV with RIFF headers). Previous implementations attempted manual header injection, which was fragile across different Piper versions. Additionally, Piper's `synthesize()` yields custom `AudioChunk` objects rather than bytes, causing `TypeErrors`.

## Decision
We standardized on the Python `wave` module for robust WAV wrapping and implemented explicit attribute extraction for Piper objects.
- **Extraction**: Uses `getattr(pcm_chunk, 'audio', pcm_chunk)` to safely handle both bytes and objects.
- **Wrapping**: Uses `wave.open` with a `BytesIO` buffer to generate industry-standard RIFF headers.

## Consequences
- **Positive**: Guaranteed audio playback across all modern browsers, removal of "ghost" TypeErrors, and robust handling of library-specific object wrappers.
- **Negative**: Adds a tiny CPU overhead for the wrapping step (negligible).
