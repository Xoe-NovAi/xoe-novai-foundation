# The Resilience Manifesto: Mastering Ma'at Logic
**Status**: Elite Hardened
**Goal**: 99.9% Availability & Zero-Crash Continuity

## 1. Concurrency Resilience (AnyIO)
Xoe-NovAi uses **Structured Concurrency** to prevent resource leaks and background "ghost" processes.

- **Rule**: All concurrent tasks (STT, RAG, TTS) must be scoped within a `TaskGroup`.
- **ExceptionGroup**: We use `except*` to handle multiple failures simultaneously. If the TTS engine fails, the system logs the specific error but ensures the RAG session is safely persistent.

---

## 2. The 400MB Soft-Stop Rule
To prevent "Compression Death Loops" on 8GB systems, Xoe-NovAi implements a memory-aware rejection middleware.

### 2.1 Middleware Logic
- **Threshold**: 400MB of available RAM.
- **Action**: If memory < 400MB, the RAG API rejects all new **POST** requests to `/query` and `/stream`.
- **Response**: Returns a `503 Service Unavailable` with the following body:
```json
{
  "error_code": "RESOURCE_EXHAUSTED",
  "message": "System under critical memory pressure",
  "recovery_suggestion": "Please wait a few moments for ZRAM to clear"
}
```

---

## 3. Triple-Layer Circuit Breakers
Every critical external or high-latency service is protected by a circuit breaker to prevent cascading failures.

### 3.1 STT Circuit Breaker (Speech-to-Text)
- **Failure Threshold**: 5 consecutive failures.
- **Timeout**: 60 seconds.
- **Fallback**: Automatic switch to **Text-Only Mode** if the voice engine is non-responsive.

### 3.2 TTS Circuit Breaker (Text-to-Speech)
- **Failure Threshold**: 3 consecutive failures.
- **Timeout**: 30 seconds.
- **Fallback**: Returns the LLM response as text and disables the audio stream to save RAM.

### 3.3 RAG API Circuit Breaker
- **Failure Threshold**: 5 consecutive failures.
- **Timeout**: 60 seconds.
- **Fallback**: Triggers **Keyword-Search Only** mode (BM25), bypassing the embedding engine and FAISS dense search.

---

## 4. Graceful Voice Degradation
Xoe-NovAi follows a 4-level fallback hierarchy for its voice interface:

1.  **Full Mode**: Faster-Whisper (Turbo) + Piper ONNX (Full Prosody).
2.  **Performance Mode**: Precision shift (FP32 -> FP16) for KV caches.
3.  **Static Mode**: Serves pre-recorded "Standard Response" audio from the vault if TTS is under heavy load.
4.  **Emergency Mode**: Text-only output with `pyttsx3` host-level audio fallback.

---

## 5. Verification SOP
- **Simulate Pressure**: Artificially inflate a memory buffer and verify the `503` response.
- **Trigger Breakers**: Point the STT service to an invalid socket and confirm the "Text-Only" UI fallback.
- **Health Check**: Run `make status` to view current circuit states.
