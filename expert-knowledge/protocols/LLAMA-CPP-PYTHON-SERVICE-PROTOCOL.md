# llama-cpp-python Service Protocol

**Version**: 1.0.0 | **Date**: 2026-02-18 | **Status**: ACTIVE  
**Author**: Claude Sonnet 4.6 (Cline) | Sprint 3  
**Applies To**: XNAi Foundation local inference stack

---

## Overview

`llama-cpp-python` is the XNAi Foundation's **primary local inference engine**. It runs any GGUF model and exposes an OpenAI-compatible REST API at `http://localhost:8080/v1`. This replaces Ollama for local model serving.

**Why llama-cpp-python over Ollama?**
- Direct GGUF model control (no model library lock-in)
- Vulkan GPU acceleration (`--n_gpu_layers -1`) — critical for Ryzen RDNA2 iGPU
- OpenAI-compatible API — works with any client expecting `/v1/chat/completions`
- Zero telemetry — fully sovereign
- Lighter weight than Ollama daemon

---

## Installation

```bash
# Install with Vulkan support (for Ryzen 5700U RDNA2 iGPU)
pip install llama-cpp-python[server] --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/vulkan

# Or standard CPU install
pip install llama-cpp-python[server]

# Verify installation
python -m llama_cpp.server --help
```

---

## Starting the Server

### Minimal (CPU-only)

```bash
python -m llama_cpp.server \
  --model /path/to/your-model.gguf \
  --port 8080
```

### Recommended (Vulkan GPU + XNAi settings)

```bash
python -m llama_cpp.server \
  --model /path/to/your-model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --n_ctx 32768 \
  --n_gpu_layers -1 \
  --chat_format chatml \
  --verbose False
```

### Configuration Options Reference

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | required | Path to GGUF file |
| `--host` | `localhost` | Bind address; use `0.0.0.0` for LAN access |
| `--port` | `8080` | HTTP port |
| `--n_ctx` | `512` | Context window size (tokens) |
| `--n_gpu_layers` | `0` | GPU layers; `-1` = all layers on GPU |
| `--n_threads` | auto | CPU threads for inference |
| `--chat_format` | `llama-2` | Chat template: `chatml`, `mistral-instruct`, etc. |
| `--verbose` | `True` | Suppress with `False` for clean output |
| `--seed` | `-1` | Random seed; set for reproducibility |

### Ryzen 5700U Optimization (Vulkan iGPU)

```bash
# Set Vulkan to use AMD iGPU (RADV_RENOIR)
export VULKAN_SDK=/usr
export AMD_VULKAN_ICD=RADV

python -m llama_cpp.server \
  --model /home/arcana-novai/Documents/xnai-foundation/models/your-model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --n_ctx 32768 \
  --n_gpu_layers -1 \
  --n_threads 8 \
  --chat_format chatml \
  --verbose False
```

---

## API Endpoints

The server exposes the full OpenAI-compatible API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat completion (main endpoint) |
| `/v1/completions` | POST | Text completion |
| `/v1/embeddings` | POST | Text embeddings |
| `/health` | GET | Health check (returns `{"status": "ok"}`) |
| `/docs` | GET | Swagger UI (interactive API docs) |

### Quick Test

```bash
# Health check
curl http://localhost:8080/health

# Test chat completion
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'

# List models
curl http://localhost:8080/v1/models
```

---

## Integration with OpenCode

The `llama-cpp` provider is configured in `.opencode/opencode.json`:

```json
{
  "provider": {
    "llama-cpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama-cpp-python (local sovereign)",
      "options": {
        "baseURL": "http://localhost:8080/v1"
      },
      "models": {
        "local": {
          "name": "Local GGUF Model",
          "limit": { "context": 32768, "output": 4096 }
        }
      }
    }
  }
}
```

**Usage in OpenCode:**
```bash
# Start llama-cpp-python server first (Terminal 1)
python -m llama_cpp.server --model /path/to/model.gguf --port 8080 --n_gpu_layers -1

# Use in OpenCode (Terminal 2)
opencode -m llama-cpp/local -p "your task"
```

---

## Integration with XNAi Foundation RAG API

The RAG API (`app/XNAi_rag_app/main.py`) can be configured to use llama-cpp-python for inference. Set in `.env`:

```bash
# .env — LLM backend configuration
LLM_BASE_URL=http://localhost:8080/v1
LLM_API_KEY=not-needed       # llama-cpp-python doesn't require auth
LLM_MODEL=local              # model name returned by /v1/models
LLM_MAX_TOKENS=4096
LLM_CONTEXT_WINDOW=32768
```

---

## Caddy Integration (Optional)

The existing `Caddyfile` does NOT proxy llama-cpp-python — it serves the Docker stack on `:8000`. This is intentional: llama-cpp-python runs as a **local process**, not a container.

To add Caddy proxying (if desired for unified routing):

```caddyfile
# Add to Caddyfile within the :8000 block
@llama {
  path /llama/*
}
handle @llama {
  uri strip_prefix /llama
  reverse_proxy localhost:8080
}
```

Then access via `http://localhost:8000/llama/v1/chat/completions`.

**Current decision**: Direct access at `http://localhost:8080/v1` is simpler and recommended. No Caddyfile changes needed.

---

## Running as a Systemd Service (Optional)

For persistent operation across reboots:

```ini
# /etc/systemd/system/xnai-llama.service
[Unit]
Description=XNAi llama-cpp-python inference server
After=network.target

[Service]
Type=simple
User=arcana-novai
Environment=VULKAN_SDK=/usr
Environment=AMD_VULKAN_ICD=RADV
ExecStart=/home/arcana-novai/.local/bin/python -m llama_cpp.server \
  --model /home/arcana-novai/Documents/xnai-foundation/models/your-model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --n_ctx 32768 \
  --n_gpu_layers -1 \
  --verbose False
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable xnai-llama.service
sudo systemctl start xnai-llama.service
sudo systemctl status xnai-llama.service
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Connection refused :8080` | Server not running | Start server before using in OpenCode |
| `Vulkan: No devices found` | AMD GPU not detected | Check `vulkaninfo` output; use CPU mode (`--n_gpu_layers 0`) |
| `Context length exceeded` | `n_ctx` too small | Increase `--n_ctx 65536` |
| `GGUF file not found` | Wrong path | Use absolute path to `.gguf` file |
| Out of memory | Too many GPU layers | Reduce `--n_gpu_layers` (e.g., 20) |
| Slow inference | All CPU | Add `--n_gpu_layers -1` for Vulkan offload |
| Model name mismatch | OpenCode expects `local` | Server returns filename as model ID; OpenCode's `@ai-sdk/openai-compatible` sends `local` — both work |

---

## Sovereign Stack Compatibility

| Property | Status |
|----------|--------|
| Zero telemetry | ✅ No external calls |
| Air-gap capable | ✅ Fully offline |
| No PyTorch/CUDA | ✅ Pure GGUF + Vulkan/CPU |
| Non-root operation | ✅ Runs as user process |
| UID 1001 compliant | ✅ (run as user, not container) |

---

*Protocol v1.0.0 — Claude Sonnet 4.6 (Cline) — 2026-02-18*
