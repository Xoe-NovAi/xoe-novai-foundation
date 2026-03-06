# 🎙️ Voice Runtime Requirements

## Model Assets
For the voice subsystem (v2.0.4+) to operate with full "Best Practice" capability, the following local model files are required in the `/models` directory (or host `./models` bind mount):

### 1. STT (Speech-to-Text)
- **Model**: `distil-large-v3` (Faster Whisper)
- **Path**: `/models/distil-large-v3/`
- **Note**: Must be in CTranslate2 format.

### 2. TTS (Text-to-Speech)
- **Model**: `en_US-john-medium.onnx` (Piper)
- **Path**: `/models/en_US-john-medium.onnx`
- **Config**: `/models/en_US-john-medium.onnx.json`

### 3. VAD (Voice Activity Detection)
- **Model**: `silero_vad.onnx`
- **Path**: `/models/silero_vad.onnx`
- **Source**: [snakers4/silero-vad](https://github.com/snakers4/silero-vad)
- **Role**: Provides neural-network based speech detection to replace primitive RMS thresholds.

## Runtime Dependencies
The following Python packages must be present in the `ui` (Chainlit) environment:
- `onnxruntime`: Core engine for VAD and TTS.
- `faster-whisper`: Optimized STT engine.
- `numpy`: Audio array manipulation.
- `wave`: Standard library for WAV containerization.

## Optimization Settings
- **Sample Rate**: All internal processing (VAD/STT) is standardized at **16,000 Hz**.
- **Bit Depth**: 16-bit PCM Mono.
- **Barge-in Threshold**: 200ms (consecutive speech frames required to trigger interrupt).
