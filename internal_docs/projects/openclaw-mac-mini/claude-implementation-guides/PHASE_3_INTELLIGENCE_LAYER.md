# PHASE 3: Intelligence Layer (Local LLMs with Ollama)
## Hands-Free Local LLM Engine with Model Optimization

**Status**: Intelligence Layer (Days 3-5) | **Prerequisites**: Phases 1-2 complete | **Outputs**: Ollama daemon, 2+ optimized models, 25+ TPS benchmark | **Test Gate**: Model loading verified, TPS >25 on GPU, <10s voice latency

---

## Executive Summary

Phase 3 deploys **Ollama**, the local LLM inference engine. Ollama is optimized for:
- **macOS Apple Silicon**: Native Metal GPU acceleration (no CUDA needed)
- **Quantization**: GGUF format models load 4-10x faster than full precision
- **Voice-first**: CLI outputs are concise and VO-readable
- **Model diversity**: Llama 3.3, DeepSeek, Mistral, Phi, etc.

You'll install Ollama both natively (for Phase 1 testing) and in-container (for production OpenClaw).

---

## Part A: Understanding LLM Quantization

### Why Quantization Matters

A full 70B-parameter model in FP16 precision = ~140GB. Your Mac has 64GB. Quantization compresses models:

- **FP16**: 140GB (fits ~50B model)
- **Q8_0** (8-bit): 35GB (fits 70B, ~1% accuracy loss)
- **Q5_K_M** (5-bit): 24GB (fits 70B, ~2% accuracy loss; Apple Silicon optimized)
- **Q4_0** (4-bit): 17.5GB (fits 70B, ~3% accuracy loss)
- **Q4_K_M** (4-bit w/ importance matrix): 20GB (fits 70B, ~2% accuracy loss; **best for M-series**)

### Strategy: AWQ (Activation-aware Quantization)

**What it does**: Identifies which weights are "important" and preserves precision for those. Less important weights are aggressively quantized.

**Benefits**:
- 10-20% speed gain over basic Q4 quantization
- Minimal accuracy loss (comparable to Q5 but faster)
- Metal GPU-friendly on M-series

**How to use**: Convert HF models to GGUF with AWQ via llama.cpp:

```bash
./quantize model.gguf model-awq.gguf Q4_K_M_AWQ
```

(We'll use pre-quantized models for speed; manual quantization is optional in Phase 6.)

### Optional: SparseML + DeepSparse (Advanced Compression)

**What it does**: Prunes 50-70% of weights, then quantizes remainder. Can achieve 60-80% size reduction.

**Tradeoff**: Pruned models may lose knowledge on niche topics; recovery via prompting (chain-of-thought).

**For now**: Defer to Phase 6 (advanced scaling). Start with Q4_K_M.

---

## Part B: Ollama Installation

### Install Ollama Natively (Primary)

**Important**: Ollama runs natively on macOS, not in containers, for best GPU performance.

Download and install from Homebrew:

```bash
brew install ollama
```

VoiceOver will announce installation progress. Wait for completion.

**Verify installation**:

```bash
ollama --version
```

Expected output: `ollama version [version number]`

### Enable Metal GPU Acceleration

Ollama must be explicitly configured to use Metal. Edit/create `~/.ollama/modelfile` or configure via environment:

```bash
# Set Metal environment variables
export OLLAMA_GPU_LAYERS=99  # Offload all layers to GPU
export OLLAMA_NUM_GPU=1       # Use 1 GPU (M-series Macs have 1)
export OLLAMA_METAL=1         # Enable Metal acceleration

# Optional: increase context length for long documents
export OLLAMA_NUM_CTX=8192    # 8K context (increase for longer tasks)

# Save to shell config so it persists
echo 'export OLLAMA_GPU_LAYERS=99' >> ~/.zshrc
echo 'export OLLAMA_NUM_GPU=1' >> ~/.zshrc
echo 'export OLLAMA_METAL=1' >> ~/.zshrc

source ~/.zshrc
```

### Start Ollama Daemon

```bash
# Start in foreground to verify Metal activation
OLLAMA_METAL=1 OLLAMA_GPU_LAYERS=99 ollama serve
```

**Watch for this line** (VoiceOver will read it):
```
metal: initialized device 'Apple M3 Pro GPU' with 18 cores
```

If you see `metal: initialized`, GPU acceleration is active. 

**Stop the daemon** (Ctrl + C) and start it as a background service:

```bash
brew services start ollama
```

---

## Part C: Model Selection & Download

### Recommended Model Stack

**For your use case** (OpenClaw agent with hands-free operation):

| Model | Size | VRAM | Speed | Quality | Quantization |
|-------|------|------|-------|---------|--------------|
| **Llama 3.3 70B** (Primary) | 35GB | 36GB | 25-30 TPS | Excellent reasoning | Q4_K_M |
| **DeepSeek-V3 67B** (Backup) | 32GB | 33GB | 22-28 TPS | Excellent coding | Q4 |
| **Mistral 7B** (Fast fallback) | 4GB | 4GB | 40+ TPS | Good for quick tasks | Q4_K_M |

**Why these**:
- **Llama 3.3 70B**: Best reasoning, best for agent tasks (planning, tool use)
- **DeepSeek-V3**: Exceptional coding, math; good fallback
- **Mistral 7B**: Fast for time-sensitive tasks (voice response latency critical)

### Download Models

```bash
# Download Llama 3.3 70B Q4_K_M
ollama pull llama3.3:70b-instruct-q4_k_m

# Download DeepSeek V3 Q4
ollama pull deepseek-coder:33b-instruct-q4

# Download Mistral 7B (fast)
ollama pull mistral:7b-instruct-q4_k_m
```

**Each download will take 10-30 minutes** depending on internet speed. VoiceOver announces progress.

**Verify downloads**:

```bash
ollama list
```

Expected output:
```
llama3.3:70b-instruct-q4_k_m    35GB
deepseek-coder:33b-instruct-q4  16GB
mistral:7b-instruct-q4_k_m      4GB
```

---

## Part D: Ollama Configuration for Hands-Free Operation

### Configure API Endpoint

Ollama by default listens on `http://127.0.0.1:11434`. Configure OpenClaw to use this endpoint.

Create `~/.ollama/config.json`:

```json
{
  "models_dir": "~/.ollama/models",
  "keep_alive": "5m",
  "gpu_layers": 99,
  "num_gpu": 1,
  "metal": true,
  
  "api": {
    "host": "127.0.0.1",
    "port": 11434
  },
  
  "tts": {
    "enabled": true,
    "provider": "voiceover",
    "voice": "Samantha",
    "rate": 0.5
  }
}
```

### Optimize Context Window for Voice Interaction

Voice interaction requires quick responses. Long context (16K+) slows inference. Balance context with latency:

Create `~/.ollama/modelfile.llama`:

```dockerfile
FROM llama3.3:70b-instruct-q4_k_m

# Reduce context to 4K for faster voice response
PARAMETER num_ctx 4096
PARAMETER num_batch 512
PARAMETER num_parallel 1

# Temperature for deterministic agent responses
PARAMETER temperature 0.3

# System prompt for agent mode
SYSTEM "You are an autonomous agent that plans and executes tasks. Be concise. Your outputs will be read aloud via text-to-speech, so keep responses short (under 50 words per response). Format lists as: 'item one, item two, item three' (not bullet points). When requesting approval, use: 'APPROVAL_REQUESTED: [action description]'."
```

Build custom model:

```bash
ollama create llama3.3:agent -f ~/.ollama/modelfile.llama
```

---

## Part E: Hands-Free Ollama CLI

### Voice Command Aliases for Model Interaction

Edit `~/.zshrc`:

```bash
# Ollama voice commands

alias ollama-status='ollama list | say'

alias ollama-test='
  echo "Testing Llama 3.3..."
  say "Testing Llama 3.3 agent model."
  
  # Quick inference test
  echo "Q: What is 2 + 2?" | \
  ollama run llama3.3:agent | \
  head -1 | \
  say
  
  say "Test complete."
'

alias ollama-bench='
  echo "Benchmarking models..."
  say "Running benchmark. This will take 2-3 minutes."
  
  for model in llama3.3:agent mistral:7b-instruct-q4_k_m; do
    echo "Testing $model..."
    time ollama run $model "In one sentence, summarize the benefits of quantized language models."
  done
  
  say "Benchmark complete."
'

alias ollama-health='
  status=$(curl -s http://127.0.0.1:11434/api/tags | jq '.models | length' || echo "unknown")
  say "Ollama has $status models loaded."
'

# Test model latency for voice responses
alias ollama-latency='
  echo "Measuring latency..."
  start=$(date +%s%N)
  
  response=$(echo "Fast test" | ollama run mistral:7b-instruct-q4_k_m)
  
  end=$(date +%s%N)
  latency_ms=$(( ($end - $start) / 1000000 ))
  
  say "Response latency: $latency_ms milliseconds"
'
```

Reload shell:

```bash
source ~/.zshrc
```

### Test Commands

```bash
ollama-status
```

VoiceOver will read all available models.

```bash
ollama-test
```

Will run a quick test and announce the result.

---

## Part F: Benchmark & Performance Tuning

### Comprehensive Benchmark Script

Create `~/.openclaw/benchmark-ollama.sh`:

```bash
#!/bin/bash
# Benchmark Ollama models for voice response time

log_file="~/.openclaw/benchmark-results.log"
echo "=== Ollama Model Benchmark ===" > "$log_file"
echo "Date: $(date)" >> "$log_file"

# Test prompts (short for voice response)
prompts=(
  "Summarize quantum computing in one sentence."
  "What is the capital of France?"
  "Explain machine learning simply."
  "What are the top 3 uses of AI in 2026?"
)

test_models=(
  "llama3.3:agent"
  "mistral:7b-instruct-q4_k_m"
)

for model in "${test_models[@]}"; do
  echo "" >> "$log_file"
  echo "=== Testing: $model ===" >> "$log_file"
  
  say "Testing model: $model"
  
  for prompt in "${prompts[@]}"; do
    echo "Prompt: $prompt" >> "$log_file"
    
    # Measure time
    start=$(date +%s%N)
    
    response=$(echo "$prompt" | ollama run "$model" --timeout 30s 2>/dev/null)
    status=$?
    
    end=$(date +%s%N)
    latency_ms=$(( ($end - $start) / 1000000 ))
    
    if [ $status -eq 0 ]; then
      echo "Latency: ${latency_ms}ms" >> "$log_file"
      echo "Response: ${response:0:100}..." >> "$log_file"
      
      # Voice feedback
      if (( latency_ms < 3000 )); then
        feedback="Good: ${latency_ms}ms"
      elif (( latency_ms < 8000 )); then
        feedback="Acceptable: ${latency_ms}ms"
      else
        feedback="Slow: ${latency_ms}ms. Consider switching models or reducing batch size."
      fi
      
      say "$feedback"
    else
      echo "ERROR: Model failed or timed out" >> "$log_file"
      say "Model failed. Check logs."
    fi
    
    echo "" >> "$log_file"
  done
done

echo "" >> "$log_file"
echo "Benchmark complete." >> "$log_file"
say "Benchmark complete. Results in $log_file"

# Print summary
echo ""
echo "=== SUMMARY ==="
grep "Latency:" "$log_file" | awk '{sum+=$2; count++} END {print "Average latency: " sum/count "ms"}'
```

Run benchmark:

```bash
chmod +x ~/.openclaw/benchmark-ollama.sh
~/.openclaw/benchmark-ollama.sh
```

**Success Criteria**:
- Mistral 7B: <2 seconds (ideal for voice response)
- Llama 3.3 70B: 5-10 seconds (acceptable for complex reasoning)
- All models: No crashes, clean shutdown

---

## Part G: Knowledge Gaps & Solutions

### Gap 1: Model Knowledge Loss in Quantization

**Question**: Does Q4_K_M quantization "forget" knowledge?

**Answer**: Minimal. Tests show <2% perplexity increase vs. FP16. Knowledge is preserved in most weights; only edge-case reasoning degrades slightly.

**Recovery strategy** (if accuracy drops): Use chain-of-thought prompting:
```
Bad: "Who invented the transistor?"
Good: "Think step-by-step. The transistor was invented in what year, by whom, and where?"
```

### Gap 2: Context Window Trade-off

**Question**: Why reduce context to 4K if the Mac can handle 8K+?

**Answer**: Voice latency. Longer context = longer inference time.
- 4K context: 5-8 second response time (acceptable for voice)
- 8K context: 10-15 second response time (user perception: too slow)

**Recommendation**: Start with 4K for voice. Increase to 8K for batch/offline tasks (Phase 6).

### Gap 3: GPU Memory Pressure & Swapping

**Question**: What happens if Ollama tries to load a model larger than VRAM?

**Answer**: macOS automatically swaps to disk. Performance drops to 1-3 TPS. Detection:
```bash
vm_stat | grep "Pages swapped"
```

If Pages swapped increases, close other apps or reduce model size.

---

## Part H: Model Optimization (AWQ Conversion)

### Optional: Convert Model to AWQ Format

If you want maximum speed (10-20% gain), convert model to AWQ. Requires:
- `llama.cpp` (GGML inference engine)
- Source model in GGUF format

**Installation**:
```bash
brew install llama-cpp
```

**Convert Llama 3.3 to AWQ**:
```bash
# Download base model (if not already in Ollama)
cd ~/.ollama/models/blobs

# Quantize to AWQ (takes 30-60 minutes)
llama-quantize \
  --type f16 \
  llama-3.3-70b-instruct.gguf \
  llama-3.3-70b-instruct-awq.gguf
```

**Create Ollama modelfile for AWQ**:
```dockerfile
FROM llama-3.3-70b-instruct-awq.gguf
PARAMETER temperature 0.3
```

```bash
ollama create llama3.3:awq -f modelfile-awq
```

**Expected gain**: 10-20% faster (30-35 TPS vs. 25-30 TPS).

---

## Part I: Testing & Validation Gate

### Pre-Phase-4 Checklist

Before moving to OpenClaw integration:

1. **Ollama Installation**:
   - [ ] `ollama --version` returns version
   - [ ] `ollama serve` shows "Metal: initialized device"
   - [ ] `ollama list` shows ≥2 models

2. **Model Loading**:
   - [ ] `ollama run llama3.3:agent "hello"` completes in <10 seconds
   - [ ] Model generates coherent 1-sentence response
   - [ ] No OOM (out of memory) errors

3. **Performance**:
   - [ ] Llama 3.3: 25+ TPS measured by benchmark script
   - [ ] Mistral 7B: 40+ TPS
   - [ ] Voice latency (Mistral): <2 seconds for simple queries

4. **Hands-Free**:
   - [ ] `ollama-status` via voice alias reads model list
   - [ ] `ollama-bench` runs and announces results
   - [ ] VoiceOver announces all model outputs

### Voice Latency Stress Test

Create `~/.openclaw/latency-test.sh`:

```bash
#!/bin/bash
# Simulate real voice latency under load

say "Starting latency test. Listen for response times."

for i in {1..5}; do
  query="Quick question $i: Write a 1-sentence definition of machine learning."
  
  start=$(date +%s%N)
  response=$(echo "$query" | ollama run mistral:7b-instruct-q4_k_m 2>/dev/null)
  end=$(date +%s%N)
  
  latency_ms=$(( ($end - $start) / 1000000 ))
  
  echo "Query $i latency: ${latency_ms}ms"
  say "Response time: $latency_ms milliseconds"
  
  sleep 1
done

say "Latency test complete."
```

**Success**: Average latency <2 seconds.

---

## Part J: Extension Points

### `ollama` Configuration Schema

```json
{
  "ollama": {
    "models": [
      {
        "name": "llama3.3:agent",
        "size_gb": 35,
        "quantization": "Q4_K_M",
        "context_length": 4096,
        "optimization": "none",
        "primary_use": "complex_reasoning"
      },
      {
        "name": "mistral:7b-instruct-q4_k_m",
        "size_gb": 4,
        "quantization": "Q4_K_M",
        "context_length": 4096,
        "optimization": "none",
        "primary_use": "voice_response_speed"
      }
    ],
    "gpu_settings": {
      "gpu_layers": 99,
      "num_gpu": 1,
      "metal_enabled": true
    },
    "inference_defaults": {
      "temperature": 0.3,
      "top_p": 0.9,
      "timeout_seconds": 30
    }
  }
}
```

---

## Troubleshooting Matrix

| **Issue** | **Symptom** | **Fix** |
|-----------|-----------|--------|
| Metal GPU not detected | `ollama serve` shows only CPU | Ensure `OLLAMA_METAL=1` set; restart ollama; check `pmset -g` for power settings |
| Model loads but runs on CPU | Inference is 2-3 TPS | Check `ollama list` VRAM column; increase `OLLAMA_GPU_LAYERS` to 99 |
| Model crashes with OOM | "killed by kernel" or "Segmentation fault" | Reduce batch size or model size; close other apps; check `vm_stat` |
| Voice response slow (>5s) | Latency stress test fails | Switch to Mistral 7B; reduce context window; increase `num_parallel` |
| Ollama service crashes after 30 minutes | Daemon dies under load | Check logs: `tail -f ~/.ollama/logs/server.log`; likely thermal throttle or memory leak |

---

## Summary & Handoff to Phase 4

**What you've built**:
- ✓ Ollama installed with Metal GPU acceleration enabled
- ✓ 3 optimized models downloaded and benchmarked
- ✓ Voice commands for model interaction
- ✓ Performance validated: 25+ TPS, <5s voice latency
- ✓ Hands-free operation tested end-to-end

**Next**: Phase 4 integrates OpenClaw (the agent orchestrator) with Ollama. OpenClaw will use Ollama as its LLM backbone, routing all requests through the local engine.

**Estimated time**: 3-5 hours (including model downloads and benchmarking).

**Critical note**: GPU acceleration is essential. If Metal doesn't work, CPU-only mode is functional but slow. Troubleshoot GPU before proceeding to Phase 4.
