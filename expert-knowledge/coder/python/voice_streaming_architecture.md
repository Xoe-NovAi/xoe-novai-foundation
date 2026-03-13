# 🎙️ Voice Streaming & Performance Architecture

## 1. Zero-Latency Synthesis (Sentence Streaming)
To minimize "Time to First Audio" (TTFA), the system uses a pipeline that segments LLM output into sentences before synthesis.

### Pipeline Flow
1. **LLM Stream**: Tokens arrive asynchronously from the inference engine.
2. **Sentence Segmenter**: A buffer accumulates tokens until a boundary (`.`, `!`, `?`) is detected.
3. **Parallel TTS**: As soon as a sentence is complete, it is dispatched to the TTS engine (Piper) while the LLM continues generating the next sentence.
4. **Audio Queue**: Audio chunks are queued in the UI for seamless playback.

### Implementation Pattern (Async)
```python
async def voice_pipeline(llm_stream):
    buffer = ""
    async for token in llm_stream:
        buffer += token
        if any(p in token for p in ".!?"):
            sentence = buffer.strip()
            audio_bytes = await tts.synthesize(sentence)
            await ui.play_audio(audio_bytes)
            buffer = ""
```

## 2. Ryzen 5700U Optimizations
The Ryzen 5700U (Zen 2, 8C/16T) performs best when leveraging SIMD instructions and optimized inference runtimes.

### OpenVINO Integration
- **Benchmark**: OpenVINO provides ~40% faster inference for Whisper on AMD CPUs compared to standard ONNX.
- **Requirement**: Use `ov_type=int8` or `ov_type=fp16` models from the OpenVINO Model Zoo.
- **XNAi Strategy**: Prepare a fallback to `faster-whisper` (current) if OpenVINO libraries are missing in the target environment.

## 3. Real-Time STT (Buffer-and-Overlap)
Since Whisper is not a true "streaming" model (it requires a full audio context), we simulate real-time transcription.

### Strategy
1. **Rolling Window**: Capture 1-2 second chunks of audio.
2. **Contextual Overlap**: Append the last 0.5s of the previous window to the current window to maintain word continuity.
3. **Greedy Decoding**: Use `beam_size=1` for partial windows to maximize speed, and `beam_size=5` only for final voice segments.

## 4. Perceived Latency vs. Actual Latency
- **UI Signaling**: Provide "Thinking..." or "Listening..." visual cues immediately to reduce user frustration.
- **Audio Pre-warming**: Initialize TTS engines with a silent "warm-up" synthesis on startup to avoid first-run cold starts.
