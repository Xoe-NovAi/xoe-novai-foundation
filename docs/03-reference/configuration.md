# Configuration Reference

> **Last Updated**: 2026-02-21  
> **Config Source**: `config.toml` (23 sections)

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_PASSWORD` | Redis authentication (REQUIRED) | Generate with `openssl rand -base64 32` |

### Service URLs

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis hostname (container: `redis`) |
| `REDIS_PORT` | `6379` | Redis port |
| `QDRANT_URL` | `http://qdrant:6333` | Qdrant vector DB URL |
| `QDRANT_API_KEY` | - | Qdrant API key (optional) |
| `VIKUNJA_URL` | `http://localhost:3456` | Vikunja task API URL |
| `VIKUNJA_TOKEN` | - | Vikunja API token |
| `RAG_API_URL` | `http://localhost:8000` | RAG API URL |
| `CONSUL_HOST` | `consul` | Consul hostname |
| `CONSUL_PORT` | `8500` | Consul HTTP port |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |

### Performance Tuning (Ryzen 5700U)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENBLAS_NUM_THREADS` | `6` | BLAS parallelism |
| `OPENBLAS_CORETYPE` | `ZEN2` | AMD optimization |
| `N_THREADS` | `6` | General threading |
| `LLAMA_CPP_N_THREADS` | `6` | LLM inference threads |
| `OMP_NUM_THREADS` | `1` | Prevent oversubscription |

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL_PATH` | `/models/Qwen3-0.6B-Q6_K.gguf` | Model file path |
| `LLAMA_CPP_N_CTX` | `2048` | Context window size |
| `LLAMA_CPP_N_BATCH` | `512` | Batch size |
| `LLAMA_CPP_USE_MMAP` | `true` | Memory-map model |
| `LLAMA_CPP_USE_MLOCK` | `true` | Lock memory |
| `LLAMA_CPP_F16_KV` | `true` | Half-precision KV cache |

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `MFA_ENABLED` | `true` | Enable MFA |
| `IAM_DB_PATH` | `/app/data/iam.db` | IAM database |
| `JWT_PRIVATE_KEY_PATH` | `/app/data/jwt-private-key.pem` | JWT private key |
| `JWT_PUBLIC_KEY_PATH` | `/app/data/jwt-public-key.pem` | JWT public key |

### Observability

| Variable | Default | Description |
|----------|---------|-------------|
| `OBSERVABILITY_ENABLED` | `false` | Enable observability |
| `OBSERVABILITY_TRACING` | `true` | Distributed tracing |
| `OBSERVABILITY_METRICS` | `true` | Metrics collection |
| `OBSERVABILITY_LOGS` | `true` | Structured logging |
| `OBSERVABILITY_MEMORY_THRESHOLD` | `5000` | Memory alert threshold |
| `OBSERVABILITY_MAAT_COMPLIANCE` | `true` | Ma'at compliance |
| `OBSERVABILITY_PRIVACY_MODE` | `strict` | Privacy mode |

### Telemetry (Disabled by Default)

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAINLIT_NO_TELEMETRY` | `true` | Disable Chainlit telemetry |
| `CRAWL4AI_NO_TELEMETRY` | `true` | Disable Crawl4AI telemetry |
| `SCARF_NO_ANALYTICS` | `true` | Disable Scarf analytics |

### Voice Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAINLIT_PORT` | `8001` | Voice UI port |
| `RAG_UI_USERNAME` | - | Auto-login username |
| `RAG_UI_PASSWORD` | - | Auto-login password |
| `XOE_VOICE_DEBUG` | `false` | Debug logging |
| `VOICE_STT_MODEL` | `base` | Whisper model size |
| `VOICE_TTS_MODEL` | `en_US-lessac-medium.onnx` | Piper model |

### Crawl Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAWL_SANITIZE_SCRIPTS` | `true` | Remove script tags |
| `CRAWL_RATE_LIMIT_PER_MIN` | `30` | Rate limit |
| `CRAWL_CACHE_TTL` | `86400` | Cache TTL (seconds) |
| `LIBRARY_PATH` | `/library` | Library directory |
| `KNOWLEDGE_PATH` | `/knowledge` | Knowledge base |

### Container Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_UID` | `1001` | Non-root user ID |
| `APP_GID` | `1001` | Non-root group ID |
| `UID` | `1001` | Alias for APP_UID |
| `GID` | `1001` | Alias for APP_GID |
| `PYTHONUNBUFFERED` | `1` | Unbuffered output |
| `PYTHONPATH` | `/app` | Python path |
| `LOG_DIR` | `/app/logs` | Log directory |

---

## config.toml Reference

### [metadata] - Stack Identity

```toml
[metadata]
stack_version = "v0.1.0-alpha"
release_date = "2026-01-27"
codename = "Sovereign Foundation"
description = "CPU-optimized local AI RAG stack"
architecture = "streaming-first, zero-telemetry"
```

### [project] - Core Settings

```toml
[project]
name = "Xoe-NovAi"
phase = 1
telemetry_enabled = false
privacy_mode = "local-only"
data_sovereignty = true
```

### [models] - LLM & Embedding

```toml
[models]
llm_path = "/models/Qwen3-0.6B-Q6_K.gguf"
llm_size_gb = 3.0
llm_quantization = "Q6_K"
llm_context_window = 2048
embedding_path = "/embeddings/all-MiniLM-L12-v2.Q8_0.gguf"
embedding_dimensions = 384
```

### [performance] - Resource Limits

```toml
[performance]
memory_limit_bytes = 6442450944  # 6 GB
memory_warning_threshold_bytes = 5905580032  # 5.5 GB
latency_target_ms = 1000
cpu_threads = 12
```

### [rag] - RAG Configuration

```toml
[rag]
retrieval_enabled = true
top_k = 4
max_context_chars = 4000
hybrid_search = true
```

### [tier] - Tier Configuration

```toml
[tier.default]
max_tokens = 512
top_k = 4
context_chars = 4000
temperature = 0.7
```

### [circuit_breaker] - Resilience

```toml
[circuit_breaker]
failure_threshold = 5
recovery_timeout = 30
half_open_max_calls = 3
```

---

## Validation Rules

| Variable | Rule |
|----------|------|
| `REDIS_PASSWORD` | Must be set (fails if empty) |
| `APP_UID` / `APP_GID` | Valid UID/GID |
| `QDRANT_API_KEY` | Optional, empty OK |
| `MEMORY_LIMIT_GB` | Range 5-32GB |
| `MIN_CPU_THREADS` | Minimum 4 |
| `MAX_CPU_THREADS` | Maximum 8 |
| `MAX_LOGIN_ATTEMPTS` | 5 attempts |
| `LOCKOUT_DURATION_MINUTES` | 30 minutes |
| `MIN_PASSWORD_LENGTH` | 8 characters |

---

## Related Documentation

- [Secrets Management](secrets.md)
- [Main API](api/main.md)
- [Hardware Tuning](03-how-to-guides/hardware-tuning/)
