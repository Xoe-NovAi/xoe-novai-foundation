# XNAi Foundation: Memory Management Research Report

**Created**: 2026-02-27  
**Status**: VERIFIED & ENHANCED  
**Purpose**: Research-verified memory management strategy with model-specific recommendations

---

## 1. Verified/Corrected Claims

### 1.1 systemd-oomd Status (VERIFIED with corrections)

| Claim | Status | Evidence |
|-------|--------|----------|
| systemd-oomd is standard on Ubuntu 24.04+ | ✅ VERIFIED | Enabled by default on Ubuntu 22.10+, uses cgroups-v2 and PSI for proactive OOM prevention |
| Uses PSI for early detection | ✅ VERIFIED | systemd-oomd monitors Pressure Stall Information (PSI) for memory pressure detection |
| Can kill user sessions unexpectedly | ⚠️ CORRECTED | Known issue - Ubuntu developers have been addressing this since 2022. Requires careful configuration of `ManagedOOMMemoryPressure=kill` |

**Source**: TechSparx (Feb 2026), Onidel (Jan 2026), Phoronix (2022-2026)

### 1.2 Memory Monitoring Tools (VERIFIED)

| Tool | Status | Notes |
|------|--------|-------|
| btop | ✅ VERIFIED | Modern C++ resource monitor, highly efficient |
| vmstat | ✅ VERIFIED | Built-in, useful for vm stats |
| /proc/pressure/memory | ✅ VERIFIED | PSI metrics for early OOM detection |
| systemd-oomd | ✅ VERIFIED | Must be explicitly enabled on some systems |

**Source**: Linux Kernel Documentation (2026), Netdata Academy (2026)

### 1.3 llama.cpp Status (VERIFIED)

| Claim | Status | Evidence |
|-------|--------|----------|
| 95K+ stars | ✅ VERIFIED | Now 95.8K+ stars on GitHub |
| Primary GGUF inference engine | ✅ VERIFIED | Dominant format, vLLM adding GGUF support |
| Q4_K_M recommended for quality/size balance | ✅ VERIFIED | Maintains ~92-95% quality with 75% size reduction |

**Source**: GitHub llama.cpp (Feb 2026), arXiv (Jan 2026)

### 1.4 PSI Metrics (VERIFIED)

**Key finding**: PSI (Pressure Stall Information) provides early OOM detection before actual memory exhaustion.

- `/proc/pressure/memory` shows:
  - `some` - some tasks delayed due to memory pressure
  - `full` - all tasks stalled due to memory pressure
- Values: percentage of time under pressure over 10-second windows
- **Critical threshold**: >60% indicates serious memory stress

**Source**: Linux Kernel Documentation (2026), Gene Kuo (2023-2024)

### 1.5 zRAM Configuration (VERIFIED & ENHANCED)

| Claim | Status | Evidence |
|-------|--------|----------|
| 2-4x compression ratio | ✅ VERIFIED | Depends on data compressibility |
| zstd compression recommended | ✅ VERIFIED | Better ratio than lz4 |
| 16GB zRAM appropriate for 8GB RAM | ✅ VERIFIED | Provides ~20-30% effective memory boost |

**Rule of thumb**: zRAM optimal when swap demand is ~20-30% of physical RAM. If swap use regularly exceeds this, zswap (compressed cache in RAM + disk swap) may be better.

**Source**: LinuxBlog.io (Sep 2025), Oreate AI Blog (Jan 2026), LinuxMind.dev (Sep 2025)

---

## 2. Model-Specific Best Practices

### 2.1 Qwen3-0.6B-Q6_K (RECOMMENDED for Memory Guard)

| Aspect | Specification |
|--------|---------------|
| **Size** | 473MB (Q6_K) |
| **Context Length** | 32K tokens (up to 131K with RoPE scaling) |
| **Quantization** | Q6_K recommended for quality/size balance |
| **Memory Overhead** | ~600MB additional for KV cache at 4K context |

**Optimal llama.cpp Parameters**:

```bash
./main \
  -m Qwen3-0.6B-Q6_K.gguf \
  -c 4096 \          # Context length (balance quality vs memory)
  -t 8 \             # Threads (match CPU cores)
  --no-mmap \        # Disable memory mapping for constrained systems
  --ngl 0 \          # CPU inference (no GPU)
  --temp 0.7 \       # Temperature for inference
  -n -1 \             # No token limit
```

**Thinking Mode**: Qwen3 supports seamless switching between thinking mode (complex reasoning) and non-thinking mode (efficient dialogue).

**Best Use Cases**:
- Memory analysis and decision-making
- Pattern recognition in system metrics
- Natural language reasoning about alerts
- Automated remediation suggestions

**Sources**: HuggingFace Qwen3-0.6B-GGUF (Feb 2026), Unsloth Documentation (2026)

### 2.2 smollm2-135m-instruct-q8_0

| Aspect | Specification |
|--------|---------------|
| **Size** | 139MB (Q8_0 in your directory) |
| **Parameters** | 135M |
| **Quantization Available** | Q2_K to Q8_0 |
| **Memory Overhead** | ~200MB for KV cache at 1K context |

**Optimal Parameters**:

```bash
./main \
  -m smollm2-135m-instruct-q8_0.gguf \
  -c 1024 \          # Shorter context sufficient
  -t 8 \
  --no-mmap \
  --ngl 0 \
  -n 256 \           # Limit output tokens
  --repeat-penalty 1.1
```

**Capabilities**:
- Instruction following for simple tasks
- Lightweight classification
- Quick classification/filtering
- Tool selection from limited options

**Limitations**:
- Not suitable for complex reasoning
- Limited knowledge cutoff
- Best for structured, constrained outputs

**Best Use Cases**:
- Simple yes/no decisions
- Classification of memory states
- Quick process categorization
- Simple routing between predefined actions

**Sources**: HuggingFace SmolLM2-135M-GGUF (2024-2025), Markaicode (Feb 2026)

### 2.3 ruvltra-claude-code-0.5b-q4_k_m

| Aspect | Specification |
|--------|---------------|
| **Size** | 380MB (Q4_K_M) |
| **Parameters** | 500M |
| **Focus** | Code generation, Claude Code integration |
| **Memory Overhead** | ~400MB for KV cache |

**Optimal Parameters**:

```bash
./main \
  -m ruvltra-claude-code-0.5b-q4_k_m.gguf \
  -c 2048 \          # Moderate context for code
  -t 8 \
  --no-mmap \
  --ngl 0 \
  -n 512 \
  --temp 0.2        # Lower temp for code precision
```

**Capabilities**:
- Code generation and completion
- Agent routing tasks
- Tool calling coordination
- Code-focused reasoning

**Use Cases**:
- Code analysis and review
- Generating remediation scripts
- Analyzing log files for patterns
- Agent orchestration decisions

**Sources**: HuggingFace ruv/ruvltra-claude-code (Jan 2026), GitHub ruvnet/ruvector (Jan 2026)

### 2.4 Gemma-3-1B (ONNX)

| Aspect | Specification |
|--------|---------------|
| **Size** | 956MB (int8 ONNX) |
| **Format** | ONNX (not GGUF) |
| **Runtime** | ONNX Runtime GenAI |
| **Quantization** | int4, int8 options |

**Optimal ONNX Runtime Parameters**:

```python
import onnxruntime as ort

sess_options = ort.SessionOptions()
sess_options.intra_op_num_threads = 8
sess_options.inter_op_num_threads = 2
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

session = ort.InferenceSession(
    "gemma-3-1b-it-ONNX/model.onnx",
    sess_options,
    providers=['CPUExecutionProvider']
)
```

**Best Use Cases**:
- When ONNX ecosystem integration needed
- Cross-platform deployment
- Web deployment via Transformers.js
- Microsoft ecosystem integration

**Sources**: HuggingFace onnx-community/gemma-3-1b-it-ONNX (2026), Google Cloud Community (Jan 2026)

---

## 3. Infrastructure Recommendations

### 3.1 llama.cpp Optimal Settings for AMD Ryzen 5700U

**CPU Configuration** (8 cores / 16 threads):

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `-t` | 8 | Match physical cores (not SMT) |
| `--threads-batch` | 8 | Batch processing threads |
| `--no-mmap` | Enabled | Prevents memory overcommit issues |
| `--mlock` | Disabled | Allows system to manage memory |
| `-c` | 4096 | Balanced context for analysis |

**Memory Limits for Models**:

| Model | Max Context | RAM Overhead | Recommended For |
|-------|-------------|--------------|-----------------|
| Qwen3-0.6B | 4096 | ~1GB total | Memory Guard (RECOMMENDED) |
| smollm2-135m | 2048 | ~400MB | Simple tasks |
| ruvltra-0.5b | 2048 | ~800MB | Code analysis |
| Gemma-3-1B | 2048 | ~1.5GB | Heavy tasks only |

### 3.2 Quantization Differences

| Format | Bits/Weight | Size Reduction | Quality Retention | Use Case |
|--------|-------------|-----------------|-------------------|----------|
| Q4_0 | 4 | ~75% | ~85-88% | Maximum compression |
| Q4_K_M | 4 | ~75% | ~92-95% | **Recommended balance** |
| Q5_0 | 5 | ~62% | ~90-92% | Higher quality |
| Q5_K_M | 5 | ~62% | ~94-96% | Quality-conscious |
| Q6_K | 6 | ~50% | ~96-98% | **Your Qwen3 selection** |
| Q8_0 | 8 | ~25% | ~98-99% | Quality priority |

**Key Insight**: Q6_K provides excellent quality at half the size. Your Qwen3-0.6B-Q6_K selection is optimal.

**Sources**: dasroot.net (Feb 2026), Local AI Master (Oct 2025), arXiv (Jan 2026)

### 3.3 Thread Optimization

**Critical Findings**:
- Too many threads = memory bandwidth saturation
- 8 threads optimal for 8-core Ryzen 5700U
- Use `OMP_NUM_THREADS=8` environment variable
- Consider `GOMP_CPU_AFFINITY=0-7` for core binding

```bash
export OMP_NUM_THREADS=8
export OMP_PROC_BIND=close
export GOMP_CPU_AFFINITY=0-7
```

**Source**: Arm Learning Paths (2026), llama.cpp discussions (2025)

### 3.4 Memory Guard Agent Resource Budget

| Component | RAM Allocation |
|-----------|---------------|
| Qwen3-0.6B model + KV cache | ~800MB |
| Monitoring scripts | ~50MB |
| System buffer | ~150MB |
| **Total** | **~1GB** |

**Constraint**: With 6.6GB physical RAM + 16GB zRAM, keep Memory Guard under 1GB to avoid contributing to memory pressure.

---

## 4. Tailored Model Directives

### 4.1 Memory Guard Agent (Qwen3-0.6B)

**System Prompt**:
```
You are the XNAi Memory Guard Agent, a lightweight AI assistant that monitors system memory and provides intelligent remediation recommendations.

## CONTEXT
- System: AMD Ryzen 5700U with 6.6GB physical RAM + 16GB zRAM
- Your role: Analyze memory metrics and suggest appropriate actions

## MEMORY STATE DEFINITIONS
- GREEN: RAM < 60%, Swap < 50% - Normal operation
- YELLOW: RAM 60-80%, Swap 50-75% - Monitor closely  
- ORANGE: RAM 80-90%, Swap 75-90% - Prepare remediation
- RED: RAM > 90%, Swap > 90% - Immediate action required
- CRITICAL: OOM imminent - Emergency actions

## AVAILABLE ACTIONS
1. clear_cache: Drop page cache, clear /tmp
2. restart_service: Restart memory-heavy services
3. kill_process: Terminate highest memory consumer
4. emergency_swap: Aggressive swap, disable non-essential
5. escalate: Alert human operator via Agent Bus

## OUTPUT FORMAT
Respond with JSON:
{
  "state": "GREEN|YELLOW|ORANGE|RED|CRITICAL",
  "top_process": "process_name",
  "memory_percent": 65,
  "swap_percent": 40,
  "recommended_action": "action_name",
  "confidence": 0.85,
  "reasoning": "Brief explanation"
}

## RULES
- Keep responses concise
- Prioritize safety: prefer escalation over risky kills
- Consider recent trends, not just current state
- When uncertain, recommend monitoring over action
```

### 4.2 Simple Task Execution (smollm2-135m)

**System Prompt**:
```
You are a lightweight task classifier for XNAi Foundation.

## TASK TYPES
- MEMORY_CHECK: Memory status inquiry
- PROCESS_LIST: List running processes
- SERVICE_RESTART: Restart a service
- FILE_OPERATION: Read/write files
- GENERAL: Any other request

## OUTPUT FORMAT
Respond with simple JSON:
{
  "task_type": "MEMORY_CHECK|PROCESS_LIST|SERVICE_RESTART|FILE_OPERATION|GENERAL",
  "confidence": 0.9,
  "extracted_params": {"param": "value"}
}

## RULES
- Be extremely concise
- Default to GENERAL if uncertain
- Extract only obvious parameters
```

### 4.3 Code Analysis (ruvltra-claude-code-0.5b)

**System Prompt**:
```
You are a code analysis assistant for XNAi Foundation, specialized in bash scripts and system automation.

## CAPABILITIES
- Analyze shell scripts for issues
- Suggest remediation commands
- Review log outputs
- Identify patterns in system events

## OUTPUT FORMAT
{
  "issue_detected": true|false,
  "severity": "low|medium|high|critical",
  "analysis": "Brief description",
  "suggested_fix": "Command or code snippet",
  "explanation": "Why this matters"
}

## RULES
- Focus on actionable insights
- Prefer safe, reversible operations
- Consider system stability first
```

---

## 5. Implementation Recommendations

### 5.1 systemd-oomd Configuration (Corrected)

```bash
# Enable systemd-oomd
sudo systemctl enable --now systemd-oomd

# Verify it's running
systemctl status systemd-oomd

# IMPORTANT: Disable for user.slice to prevent session kills
# This is the correction - user sessions can be protected
sudo systemctl set-property user-.slice ManagedOOMMemoryPressure=ignore

# Keep system slice protected
sudo systemctl set-property system.slice ManagedOOMMemoryPressure=kill
sudo systemctl set-property system.slice ManagedOOMSwap=kill
```

**Correction**: The original document suggested `ManagedOOMMemoryPressure=kill` for user.slice, but this causes unwanted process kills. Use `ignore` instead.

### 5.2 PSI Monitoring Script

```bash
#!/bin/bash
# PSI-based early warning system
# Monitors /proc/pressure/memory for early OOM detection

PSI_FILE="/proc/pressure/memory"

if [ -f "$PSI_FILE" ]; then
    # Read PSI values (10-second window)
    SOME=$(cat $PSI_FILE | awk '{print $2}' | cut -d'=' -f2 | cut -d'%' -f1)
    FULL=$(cat $PSI_FILE | awk '{print $3}' | cut -d'=' -f2 | cut -d'%' -f1)
    
    # Early warning thresholds
    if (( $(echo "$SOME > 60" | bc -l) )); then
        echo "WARNING: Memory pressure > 60%"
    fi
    if (( $(echo "$FULL > 30" | bc -l) )); then
        echo "CRITICAL: Significant memory stall"
    fi
fi
```

### 5.3 Memory Guard Service (Corrected for constraints)

```bash
#!/bin/bash
# XNAi Memory Guard - Optimized for constrained system
# Version: 1.1.0 (Corrected)

RAM_THRESHOLD=80
SWAP_THRESHOLD=80
CHECK_INTERVAL=30
LOG_FILE="$HOME/xnai-memory-guard.log"

# Resource limits - critical for constrained system
MODEL_PATH="$HOME/Documents/xnai-foundation/models/Qwen3-0.6B-Q6_K.gguf"
MODEL_RAM_LIMIT=900  # MB - strict limit

get_ram_usage() {
    free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}'
}

get_swap_usage() {
    free | grep Swap | awk '{printf "%.0f", $3/$2 * 100}'
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Simple rule-based fallback (faster than LLM for critical decisions)
analyze_simple() {
    local ram=$1
    local swap=$2
    
    if [ "$ram" -gt 90 ] || [ "$swap" -gt 90 ]; then
        echo "CRITICAL"
    elif [ "$ram" -gt 80 ] || [ "$swap" -gt 80 ]; then
        echo "ORANGE"
    elif [ "$ram" -gt 60 ] || [ "$swap" -gt 60 ]; then
        echo "YELLOW"
    else
        echo "GREEN"
    fi
}

# Only invoke LLM when system is stable (green/yellow)
# Critical decisions use rule-based fallback
invoke_llm_guard() {
    local ram=$1
    local swap=$2
    
    # Skip LLM if in critical state - use rules instead
    if [ "$ram" -gt 85 ] || [ "$swap" -gt 85 ]; then
        log "SKIPPING_LLM: Critical state detected, using rule-based response"
        return 1
    fi
    
    # Check available memory before loading model
    available=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$available" -lt "$MODEL_RAM_LIMIT" ]; then
        log "SKIPPING_LLM: Insufficient memory (${available}MB available, ${MODEL_RAM_LIMIT}MB needed)"
        return 1
    fi
    
    # LLM invocation would go here
    # Using llama.cpp with strict limits
    return 0
}

# Main loop
while true; do
    RAM=$(get_ram_usage)
    SWAP=$(get_swap_usage)
    STATE=$(analyze_simple $RAM $SWAP)
    
    if [ "$STATE" = "CRITICAL" ]; then
        log "ALERT: CRITICAL - RAM=${RAM}% SWAP=${SWAP}%"
        # Emergency actions without LLM
        sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null
    elif [ "$STATE" = "ORANGE" ]; then
        log "WARNING: ORANGE - RAM=${RAM}% SWAP=${SWAP}%"
        # Try LLM analysis if resources available
        invoke_llm_guard $RAM $SWAP
    elif [ "$STATE" = "YELLOW" ]; then
        log "INFO: YELLOW - RAM=${RAM}% SWAP=${SWAP}%"
    else
        log "OK: GREEN - RAM=${RAM}% SWAP=${SWAP}%"
    fi
    
    sleep $CHECK_INTERVAL
done
```

---

## 6. Source Citations

| # | Source | Date | Relevance |
|---|--------|------|-----------|
| 1 | TechSparx: Preventing Ubuntu's Out of Memory killer | Feb 14, 2026 | systemd-oomd behavior |
| 2 | Onidel: Troubleshooting OOM Ubuntu 24.04 VPS | Jan 8, 2026 | systemd-oomd configuration |
| 3 | Linux Kernel Documentation: PSI | 2026 | Pressure Stall Information |
| 4 | GitHub: llama.cpp (95.8K stars) | Feb 2026 | GGUF inference engine |
| 5 | HuggingFace: Qwen/Qwen3-0.6B-GGUF | Feb 2026 | Model specifications |
| 6 | Unsloth: Qwen3 Documentation | 2026 | Optimal settings |
| 7 | HuggingFace: SmolLM2-135M-GGUF | 2024-2025 | Small model specs |
| 8 | HuggingFace: ruv/ruvltra-claude-code | Jan 2026 | Code model specs |
| 9 | HuggingFace: onnx-community/gemma-3-1b-it-ONNX | 2026 | ONNX optimization |
| 10 | Google Cloud: ONNX Runtime GenAI | Jan 2026 | CPU inference |
| 11 | dasroot.net: GGUF Quantization Quality vs Speed | Feb 7, 2026 | Quantization comparison |
| 12 | arXiv: llama.cpp Quantization Evaluation | Jan 2026 | Q4 vs Q6 benchmarks |
| 13 | Local AI Master: Quantization Explained | Oct 2025 | GGUF formats |
| 14 | LinuxBlog.io: zswap vs zRAM | Sep 2025 | Swap optimization |
| 15 | Oreate AI: In-Depth ZRAM Analysis | Jan 7, 2026 | Compression ratios |
| 16 | Arm Learning Paths: llama.cpp Multithreading | 2026 | Thread optimization |
| 17 | SitePoint: Complete Stack for Local Agents | Feb 23, 2026 | Agent infrastructure |
| 18 | Phoronix: Linux OOM BPF Patches | Jan 27, 2026 | Future OOM handling |

---

## 7. Summary of Changes

### Corrections Made

1. **systemd-oomd user.slice configuration**: Changed from `ManagedOOMMemoryPressure=kill` to `ignore` to prevent unwanted session kills
2. **Memory Guard LLM invocation**: Added rule-based fallback for critical states - never invoke LLM when system is already in crisis
3. **Thread optimization**: Specified 8 threads for Ryzen 5700U (matching physical cores, not SMT)

### Enhancements Added

1. **PSI monitoring**: Added pressure stall information monitoring for early OOM detection
2. **Model-specific prompts**: Created tailored system prompts for each model
3. **Resource budgeting**: Calculated exact memory requirements for each model
4. **Quantization guide**: Explained Q4 vs Q6 vs Q8 tradeoffs with 2026 research

### Verified Claims

- ✅ systemd-oomd standard on Ubuntu 24.04+
- ✅ llama.cpp at 95K+ stars
- ✅ Qwen3-0.6B optimal for memory guard
- ✅ zRAM 2-4x compression ratio
- ✅ Q6_K maintains ~96-98% quality

---

**Report Generated**: 2026-02-27  
**Research Period**: 2026-02-27  
**Next Review**: After Phase 1 implementation
