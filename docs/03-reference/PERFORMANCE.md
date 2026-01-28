# 📊 XNAi Performance Baselines

**Last Updated**: 2026-01-27
**Hardware**: AMD Ryzen 7 5700U (8C/16T, 25W cTDP)
**OS**: Linux (Podman 5.x)

## 1. Voice Interface (v2.0.5)
| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| **STT Latency (Whisper)** | 280ms - 450ms | <300ms | 🟡 Optimized |
| **TTS Synthesis (Piper)** | 80ms - 150ms | <100ms | 🟢 Best-in-Class |
| **VAD Accuracy (Silero)** | 98.2% | >95% | 🟢 Exceptional |
| **End-to-End Latency** | 1.2s - 1.8s | <1.0s | 🟡 Tuning Needed |

## 2. RAG & LLM Inference
| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| **TTFT (First Token)** | 420ms | <300ms | 🟡 Ryzen-specific |
| **Tokens per Second (TPS)**| 1.49 - 2.22 | >3.0 | 🔴 Hardware Limit |
| **KV Cache RAM (Int8)** | ~1.2GB | <2.0GB | 🟢 Ultra-Lean |
| **Context Window Load** | 1.8s | <1.0s | 🟡 Large Context |

## 3. Infrastructure & Build
| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| **Build Time (make build)**| 1m 42s | <2m | 🟢 BuildKit Opt |
| **Service Startup Time** | 12s | <15s | 🟢 Tini Init |
| **Redis Sync Latency** | 2ms | <5ms | 🟢 Local Sync |

## 4. Regression History
- **2026-01-27**: Established baselines for v2.0.5 release.
- **Note**: End-to-end latency is primarily blocked by the sequential nature of current transcription. Parallel LLM+TTS (Sentence Streaming) is the path to sub-1.0s results.
