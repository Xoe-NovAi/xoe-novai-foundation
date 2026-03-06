# xnai-voice-core

This is the standalone, plug-and-play voice module extracted from the XNAi Foundation Stack. 
It unifies the Mac Mini `VoiceOS` environment with the Ryzen server-side `app/` features to create a robust, resilient offline voice layer.

## Features
- **Torch-free Inference**: Uses CTranslate2 (Faster Whisper) and Piper ONNX for maximum CPU efficiency without heavy torch dependencies.
- **Dynamic Resilience**: JSON-backed persistent Circuit Breakers instantly cut failing audio connections to avert UI freezing.
- **Bounded Context**: Prevents audio array out-of-memory crashes by capping maximum durations.
