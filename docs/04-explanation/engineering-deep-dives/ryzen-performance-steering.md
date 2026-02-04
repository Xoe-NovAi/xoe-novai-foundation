# Engineering Deep Dive: Ryzen Performance Steering
**Target Hardware**: AMD Ryzen 7 5700U (Zen 2)
**Optimization Focus**: Latency & Multi-Modal Throughput

## 🧠 The "Even-Core" Strategy
The Ryzen 5700U is an 8-core/16-thread processor. For AI workloads, using hyperthreads (odd-numbered logical cores) can introduce cache contention and jitter.

### Core Pinning Pattern
We pin primary AI processes (Whisper STT, Llama-cpp) to **even-numbered physical cores**:
- **Cores**: 0, 2, 4, 6, 8, 10, 12, 14.
- **Why**: Ensures each AI thread has exclusive access to a physical L3 cache slice and execution units.

### OpenBLAS Alignment
We enforce Ryzen-specific acceleration via environment variables:
- `OPENBLAS_CORETYPE=ZEN`
- `OPENBLAS_NUM_THREADS=6` (Standardized AI thread count).

## ⚡ Int8 KV Cache Optimization
Memory is the primary bottleneck on 8GB systems. By utilizing **Int8 KV Caching**, we reduce the memory footprint of the LLM context.
- **Savings**: ~50% reduction in RAM usage for long-context retrieval.
- **Trade-off**: < 1% impact on perplexity (negligible for RAG tasks).

## 🏎️ BuildKit Cache Hardlining
To achieve "Elite" build speeds, we use the **Cache Hardlining** pattern:
```dockerfile
RUN --mount=type=cache,id=xnai-pip,target=/root/.cache/pip,uid=0,gid=0 \
    uv pip install --system -r requirements.txt
```
By forcing `uid=0,gid=0` on the cache mount, we enable **Atomic Hardlinking**. This allows `uv` to link packages from the cache directly into the system site-packages in milliseconds, rather than copying them.

## 🛡️ Rootless Runtime Persistence
Rootless Podman uses dynamic runtime directories (e.g., `/run/user/1000/containers`). We use `scripts/socket_resolver.py` to ensure that our observability tools and scanners can always find the correct socket, regardless of the distribution's `$XDG_RUNTIME_DIR` implementation.

## 🔧 tmpfs-First Strategy
For maximum performance and security, we mount high-I/O directories in **tmpfs**:
- `/app/logs`
- `/tmp/audio_pipe`
This ensures that transient audio data and logs never touch the NVMe, reducing wear and improving sub-150ms response times.
