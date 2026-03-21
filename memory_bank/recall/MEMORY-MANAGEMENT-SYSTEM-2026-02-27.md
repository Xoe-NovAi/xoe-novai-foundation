# XNAi Foundation Memory Management System
## Comprehensive Strategy Document

**Created**: 2026-02-27  
**Status**: IN PROGRESS  
**Branch**: `feature/memory-management-system`  

---

## Executive Summary

This document outlines a comprehensive memory management system for the XNAi Foundation, designed for a system with:
- **Physical RAM**: ~6.6GB usable (8GB stick + iGPU sharing)
- **zRAM Swap**: 16GB (zstd compression)
- **Total Effective Memory**: ~18GB

The memory crisis on 2026-02-27 demonstrated the need for proactive memory monitoring and automated remediation.

---

## System Specifications

### Current Hardware Profile

| Component | Specification | Notes |
|-----------|---------------|-------|
| Physical RAM | 6.6 GB | One 8GB stick + iGPU sharing |
| zRAM | 12 GB | zstd compression, 94%+ utilization under load |
| Total Memory | ~18 GB | Physical + zRAM combined |
| CPU | AMD Ryzen 5700U | 8 cores / 16 threads |
| Storage | 109GB NVMe | 87GB used (85%) |

### Memory Thresholds

| State | RAM Usage | Swap Usage | Action |
|-------|-----------|------------|--------|
| **GREEN** | < 60% | < 50% | Normal operation |
| **YELLOW** | 60-80% | 50-75% | Monitor closely |
| **ORANGE** | 80-90% | 75-90% | Alert + prepare remediation |
| **RED** | > 90% | > 90% | Auto-remediation triggered |
| **CRITICAL** | OOM imminent | Full | Emergency actions + escalate |

---

## Phase 1: Memory Monitoring Tools

### Recommended Tools Stack

| Tool | Purpose | Installation |
|------|---------|--------------|
| **btop** | Real-time process monitoring | `apt install btop` ✅ Installed |
| **vmstat** | Virtual memory statistics | Built-in |
| **free** | RAM/Swap summary | Built-in |
| **df** | Disk usage | Built-in |
| **systemd-oomd** | Automated OOM prevention | Built-in (enable) |
| **Prometheus + Node Exporter** | Historical metrics | Docker |
| **Grafana** | Visualization | Docker |

### Quick Monitoring Commands

```bash
# Real-time memory overview
btop

# Quick memory check
free -h

# Virtual memory statistics
vmstat 1

# Memory pressure
cat /proc/pressure/memory

# zRAM status
cat /sys/block/zram0/mm_stat

# Process memory sorted
ps aux --sort=-%mem | head -15

# Docker memory usage
docker stats --no-stream
```

---

## Phase 2: Memory Guard Agent (Local LLM)

### Concept

A lightweight background service that:
1. **Monitors** memory metrics continuously
2. **Analyzes** patterns and predicts issues
3. **Remediates** common problems automatically
4. **Escalates** to human when unable to resolve

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Memory Guard Agent                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Collector   │───▶│   Analyzer   │───▶│  Responder   │  │
│  │  (metrics)   │    │  (local LLM) │    │  (actions)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Decision Engine                          │   │
│  │   - Threshold checking                                │   │
│  │   - Pattern recognition                               │   │
│  │   - Action selection                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Notification System                     │   │
│  │   - Console logging                                   │   │
│  │   - Vikunja task creation                            │   │
│  │   - Agent Bus events                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Local LLM Models Available

Located in: `/home/arcana-novai/Documents/xnai-foundation/models/`

| Model | Size | Format | Use Case |
|-------|------|--------|----------|
| **Qwen3-0.6B-Q6_K.gguf** | 473MB | GGUF | **RECOMMENDED** - Memory Guard Agent |
| ruvltra-claude-code-0.5b-q4_k_m.gguf | 380MB | GGUF | Code-focused tasks |
| smollm2-135m-instruct-q8_0.gguf | 139MB | GGUF | Lightest, simple decisions |
| Gemma-3-1B_int8.onnx | 956MB | ONNX | General purpose |
| gemma-3-4b-it-UD-Q5_K_XL.gguf | 2.7GB | GGUF | Heavy tasks |
| functiongemma-270m-it-Q6_K.gguf | 270MB | GGUF | Function calling |

**Recommended for Memory Guard**: **Qwen3-0.6B-Q6_K.gguf** (473MB)
- Smallest full model, Q6_K quantization maintains quality
- Efficient CPU inference via llama.cpp
- Can run with <1GB RAM overhead

---

### Research: 2026 Best Practices

Key findings from 2026 research:

1. **systemd-oomd** - Now standard on Ubuntu 24.04+ for proactive OOM prevention
2. **llama.cpp** - 95K+ stars, continues as primary GGUF inference engine
3. **Ollama** - Popular for easy local LLM deployment
4. **Local AI Privacy** - Growing importance for sovereign AI systems
5. **PSI (Pressure Stall Information)** - Key metric for early OOM detection

Sources (2026):
- SitePoint: "Guide to Local LLMs in 2026" (Feb 2026)
- systemd-oomd documentation (2026)
- Ubuntu 24.04 memory management guides (Feb 2026)

### Remediation Actions

| Action | Trigger | Description |
|--------|---------|-------------|
| **Clear Cache** | RAM > 80% | Drop caches, clear temp files |
| **Restart Service** | RAM > 85% | Restart memory-heavy services |
| **Kill Process** | RAM > 90% | Terminate highest memory process |
| **Emergency Swap** | Critical | Aggressive swap, disable non-essential |
| **Escalate** | All fails | Alert human, create Vikunja task |

### Escalation Triggers

1. Memory > 95% for > 30 seconds
2. Swap > 95% for > 60 seconds
3. OOM killer activated
4. Remediation failed 3+ times
5. Unknown process consuming memory

---

## Phase 3: systemd-oomd Configuration

### Enable systemd-oomd

> **CORRECTION (2026-02-27)**: Use `ignore` for user.slice to prevent unwanted session kills.

```bash
# Check if available
systemctl status systemd-oomd

# Enable
sudo systemctl enable --now systemd-oomd

# IMPORTANT: Disable for user.slice to prevent session kills
# This prevents AI assistants from being killed unexpectedly
sudo systemctl set-property user-.slice ManagedOOMMemoryPressure=ignore

# Keep system slice protected
sudo systemctl set-property system.slice ManagedOOMMemoryPressure=kill
sudo systemctl set-property system.slice ManagedOOMSwap=kill
```

### Configuration for zRAM

```bash
# Enable swap monitoring for system slice
sudo systemctl set-property system.slice ManagedOOMSwap=kill
```

> **Note**: The original `kill` setting for user.slice was causing sessions to be terminated. The corrected `ignore` setting prevents this while keeping system services protected.

---

## Phase 4: Automated Scripts

### Memory Monitor Script

Create `scripts/xnai-memory-guard.sh`:

```bash
#!/bin/bash
# XNAi Memory Guard - Background Memory Monitor
# Version: 1.0.0

# Configuration
RAM_THRESHOLD=80
SWAP_THRESHOLD=80
CHECK_INTERVAL=30
LOG_FILE="/var/log/xnai-memory-guard.log"

# Thresholds
GREEN="60"
YELLOW="80"
ORANGE="90"

get_ram_usage() {
    free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}'
}

get_swap_usage() {
    free | grep Swap | awk '{printf "%.0f", $3/$2 * 100}'
}

get_zram_stats() {
    if [ -f /sys/block/zram0/mm_stat ]; then
        cat /sys/block/zram0/mm_stat
    fi
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

remediate() {
    local usage=$1
    local type=$2
    
    log "REMEDIATION: $type at ${usage}%"
    
    # Clear page cache
    sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null
    
    # Clear temp files
    rm -rf /tmp/xnai-* 2>/dev/null
    
    # Notify via Agent Bus (if available)
    # redis-cli xadd xnai:alerts * type="memory_remediation" usage="$usage" action="$type"
}

# Main loop
while true; do
    RAM=$(get_ram_usage)
    SWAP=$(get_swap_usage)
    
    if [ "$RAM" -gt "$ORANGE" ] || [ "$SWAP" -gt "$ORANGE" ]; then
        log "ALERT: RAM=${RAM}% SWAP=${SWAP}%"
        remediate "$RAM" "high_memory"
    elif [ "$RAM" -gt "$YELLOW" ] || [ "$SWAP" -gt "$YELLOW" ]; then
        log "WARNING: RAM=${RAM}% SWAP=${SWAP}%"
    fi
    
    sleep "$CHECK_INTERVAL"
done
```

---

## Phase 5: Integration Points

### Agent Bus Events

Publish memory events to Agent Bus:

```
xnai:memory_alerts
├── state: green|yellow|orange|red|critical
├── ram_usage: 65
├── swap_usage: 40
├── top_process: opencode
├── action_taken: none|clear_cache|restart_service|kill_process|escalate
└── timestamp: 2026-02-27T10:30:00
```

### Vikunja Integration

Create tasks for:
- Memory investigation
- Process analysis
- Service restart approval
- Escalation acknowledgment

### Prometheus Metrics

```yaml
# xnai_memory_exporter.yml
metrics:
  - name: xnai_ram_usage_percent
    type: gauge
    help: RAM usage percentage
    
  - name: xnai_swap_usage_percent  
    type: gauge
    help: Swap usage percentage
    
  - name: xnai_zram_compression_ratio
    type: gauge
    help: zRAM compression ratio
    
  - name: xnai_memory_state
    type: gauge
    help: Memory state (0=green, 1=yellow, 2=orange, 3=red, 4=critical)
```

---

## Phase 6: Implementation Checklist

### Immediate (This Session)

- [ ] Create `feature/memory-management-system` branch
- [ ] Set up systemd-oomd
- [ ] Configure memory thresholds
- [ ] Test monitoring scripts
- [ ] Update memory bank

### Short-Term (This Week)

- [ ] Download Qwen2.5-0.5B model
- [ ] Create Memory Guard service
- [ ] Integrate with Agent Bus
- [ ] Integrate with Vikunja
- [ ] Create Grafana dashboard

### Medium-Term (This Month)

- [ ] Add ML-based anomaly detection
- [ ] Implement predictive alerts
- [ ] Create self-healing workflows
- [ ] Document runbooks
- [ ] Test failure scenarios

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Memory Guard uses too much RAM | Run with strict memory limits, use smallest model |
| False positives | Require consecutive alerts before action |
| Service becomes unresponsive | Manual override always available |
| Model inference too slow | Use rule-based fallback for critical decisions |

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `scripts/xnai-memory-guard.sh` | Create |
| `scripts/xnai-memory-monitor.py` | Create |
| `configs/xnai-memory-guard.yaml` | Create |
| `docker-compose.yml` | Add memory-exporter service |
| `memory_bank/MEMORY-MANAGEMENT-SYSTEM.md` | Create |
| `.env` | Add memory thresholds |

---

## Research Notes

### Key Sources (2026)

1. **systemd-oomd**: Uses cgroups-v2 and PSI for proactive OOM prevention
2. **llama.cpp**: 95K+ stars, primary GGUF inference engine
3. **Qwen3-0.6B**: Available locally, efficient CPU inference
4. **btop**: Modern resource monitor (C++, efficient)
5. **Ollama**: Popular for easy local LLM deployment (2026)

### 2026 Best Practices

1. Enable systemd-oomd for proactive OOM prevention
2. Use PSI metrics for early detection
3. Implement graduated response (green → yellow → orange → red)
4. Run local LLM with strict memory limits
5. Always have human escalation path
6. Test failure scenarios regularly

### References

- SitePoint: "Guide to Local LLMs in 2026" (Feb 2026)
- "The Complete Stack for Local Autonomous Agents" (Feb 2026)
- Ubuntu 24.04 systemd-oomd documentation (2026)
- OneUptime: "How to Fix OOM Killer Memory Issues" (Jan 2026)

---

## Next Steps

1. ✅ Document created
2. ⏳ Create Git branch
3. ⏳ Implement monitoring scripts
4. ⏳ Download local model
5. ⏳ Create Memory Guard service
6. ⏳ Integrate with Foundation Stack

---

**Last Updated**: 2026-02-27  
**Next Review**: After Phase 1 complete  
**Owner**: XNAi Foundation Memory Team
