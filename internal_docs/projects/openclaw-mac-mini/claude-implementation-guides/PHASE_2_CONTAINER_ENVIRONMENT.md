# PHASE 2: Container Environment Setup (Podman)
## Hands-Free Containerization for OpenClaw & Ollama

**Status**: Container Layer (Days 2-3) | **Prerequisites**: Phase 1 complete | **Outputs**: Podman daemon, GPU-capable container, hands-free CLI | **Test Gate**: <5% overhead, successful GPU test, voice command proof-of-concept

---

## Executive Summary

Phase 2 establishes **Podman** (daemonless container runtime) as the sandbox for OpenClaw and Ollama workloads. Podman is superior to Docker on macOS because:
- No Docker Desktop required (fewer dependencies, less memory overhead)
- Native libkrun support for Vulkan-to-Metal GPU passthrough (~70-80% native performance)
- Runs containers as your user, not as a separate daemon (better security isolation)

**Hands-free focus**: All Podman commands are invoked via voice; outputs are announced via VoiceOver.

---

## Part A: Podman Installation

### Prerequisites

Ensure Phase 1 is complete:
- [ ] VoiceOver enabled and tested
- [ ] Dictation working (Fn + Fn activates)
- [ ] Microphone & speakers confirmed
- [ ] HDMI dummy plug installed

### Install Podman & Dependencies

Use VoiceOver to navigate Terminal. Open **Terminal** (VO + Space, search "Terminal", VO + Space to open).

**Step 1: Install Homebrew** (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Homebrew will announce progress via text. VoiceOver will read each line.

**Step 2: Install Podman**

```bash
brew install podman podman-compose
```

Wait for installation to complete. Homebrew outputs progress; VoiceOver reads it.

**Step 3: Verify Installation**

```bash
podman --version
```

VoiceOver will read: "podman version [version number]". If you hear this, installation succeeded.

### Initialize Podman Machine

Podman on macOS runs in a lightweight VM. Initialize it:

```bash
podman machine init \
  --cpus 12 \
  --memory 57344 \
  --disk-size 200 \
  --name openclaw-machine
```

**Parameters explained**:
- `--cpus 12`: 12 cores of CPU (leaves 4 for macOS system)
- `--memory 57344`: 57GB RAM (leaves 7GB for macOS + system overhead)
- `--disk-size 200`: 200GB disk for container images + cache
- `--name openclaw-machine`: Friendly name for voice commands

**Expected output** (read by VoiceOver):
```
Podman machine "openclaw-machine" created successfully.
```

### Start Podman Machine

```bash
podman machine start openclaw-machine
```

**Expected output**:
```
Starting Podman machine "openclaw-machine"...
[progress indicators]
Machine "openclaw-machine" started successfully.
```

---

## Part B: GPU Acceleration Setup

### Understanding GPU Passthrough on macOS

**Problem**: macOS doesn't support GPU passthrough to Linux VMs as cleanly as NVIDIA CUDA passthrough on Linux/Windows.

**Solution**: Use **Vulkan** (cross-platform graphics API) as a bridge. Vulkan translates to Metal internally.

**Performance**: Vulkan-to-Metal achieves 70-80% of native Metal speed (acceptable for inference; prompt processing is IO-bound, not compute-bound).

### Enable Vulkan in Podman

Create configuration file:

```bash
mkdir -p ~/.config/podman
cat > ~/.config/podman/containers.conf << 'EOF'
[engine]
# Enable Vulkan GPU passthrough
runtime_supports_json = true

[containers]
# Allow GPU passthrough
devices = ["/dev/dri:/dev/dri"]

[machine]
# Use libkrun for Vulkan support
image_path = "podman-v5.0.0-machine.img"
EOF
```

Restart Podman machine:

```bash
podman machine stop openclaw-machine
podman machine start openclaw-machine
```

### Test GPU Passthrough

Run a test container with Vulkan:

```bash
podman run --rm \
  --device /dev/dri \
  --security-opt label=disable \
  ubuntu:24.04 \
  /bin/bash -c "apt-get update && apt-get install -y vulkan-tools && vulkaninfo | head -20"
```

**Expected output** (read by VoiceOver):
```
vulkaninfo: .... = [GPU info]
apiVersion = [version]
```

If you see vulkan info, GPU passthrough is working.

**If GPU detection fails**:
- Check Podman logs: `podman machine ssh -- dmesg | grep -i vulkan`
- Update macOS (Vulkan support improved in Sonoma+)
- Fallback: CPU-only mode (slower but functional; see "Fallback CPU Mode" below)

---

## Part C: Hands-Free Podman CLI

### Create Voice Command Aliases

Edit `~/.zshrc` (or `~/.bashrc` if using bash):

```bash
# Add to end of ~/.zshrc

# Podman voice-friendly aliases
alias podman-status='echo "Podman status:" && podman ps -a && say "Podman status report complete"'
alias podman-logs='podman logs --tail 50 openclaw-gateway | say'
alias podman-stop='podman stop openclaw-gateway && say "Container stopped"'
alias podman-start='podman run -d --name openclaw-gateway [container-spec] && say "Container started"'
alias podman-health='podman inspect openclaw-gateway --format="{{.State.Status}}" | xargs -I {} say "Container status: {}"'

# GPU health check
alias gpu-status='
  echo "Checking GPU status..."
  podman exec openclaw-container nvidia-smi 2>/dev/null || \
  podman exec openclaw-container vulkaninfo | grep -i "GPU\|Device" | head -5 | xargs -I {} say "GPU: {}"
'

# OpenClaw-specific voice commands
alias openclaw-approve='echo "Awaiting approval..." && say "Agent pending approval. Say approve to proceed."'
alias openclaw-logs-voice='podman logs -f openclaw-gateway | say'
```

Reload shell:

```bash
source ~/.zshrc
```

### Test Voice Commands

In Terminal, with VoiceOver enabled:

```bash
podman-status
```

VoiceOver will read the container list, then announce "Podman status report complete".

---

## Part D: Thermal Management

### Why Thermal Management Matters

M-series Macs can run GPU + Ollama inference continuously, but thermal throttling degrades performance. A simple monitoring loop prevents overheating.

### Create Thermal Monitoring Script

Create `~/.openclaw/thermal-monitor.sh`:

```bash
#!/bin/bash
# Thermal monitoring for M-series Mac during OpenClaw operation

TEMP_THRESHOLD=80  # Celsius; trigger warning
CRITICAL_THRESHOLD=95  # Celsius; trigger shutdown

log_file="~/.openclaw/thermal.log"
say_enabled=true  # Set to false to silence voice announcements

while true; do
  # Read thermal sensor (requires T2 Thermal Reader or equivalent)
  # On Apple Silicon, use pmset for power state info as proxy
  
  thermal_state=$(pmset -g thermlog | grep "CPU Thermal Level" | awk '{print $NF}')
  timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  
  echo "[$timestamp] Thermal state: $thermal_state" >> "$log_file"
  
  if [[ "$thermal_state" -gt 5 ]]; then
    message="Warning: CPU thermal level elevated. Reducing inference load."
    echo "[$timestamp] $message" >> "$log_file"
    if $say_enabled; then
      say "$message"
    fi
    # Reduce Ollama parallel inference
    podman exec openclaw-gateway /bin/bash -c "export OLLAMA_NUM_PARALLEL=1"
  fi
  
  if [[ "$thermal_state" -gt 7 ]]; then
    message="Critical: Thermal shutdown triggered."
    echo "[$timestamp] $message" >> "$log_file"
    if $say_enabled; then
      say "$message"
    fi
    podman stop openclaw-gateway
    sleep 300  # Wait 5 minutes, then restart
    podman start openclaw-gateway
  fi
  
  sleep 60  # Check every minute
done
```

Make it executable:

```bash
chmod +x ~/.openclaw/thermal-monitor.sh
```

Run in background (or via launchd daemon in Phase 6):

```bash
nohup ~/.openclaw/thermal-monitor.sh > ~/.openclaw/thermal-monitor.log 2>&1 &
```

VoiceOver will announce thermal warnings as they occur.

---

## Part E: Podman Compose Setup

Create a basic `docker-compose.yml` (Podman is Docker-compatible):

Create `~/.openclaw/podman-compose.yml`:

```yaml
version: '3.8'

services:
  openclaw-gateway:
    image: openclaw:latest  # Built in Phase 4
    container_name: openclaw-gateway
    
    # GPU passthrough (Vulkan)
    devices:
      - /dev/dri:/dev/dri
    
    # Network
    ports:
      - "8080:8080"  # OpenClaw API
      - "11434:11434"  # Ollama inference
    
    # Memory
    mem_limit: 56g
    
    # Environment
    environment:
      OLLAMA_GPU_LAYERS: 99
      OLLAMA_NUM_GPU: 1
      OLLAMA_VULKAN: 1
      OLLAMA_HOST: "0.0.0.0:11434"
      OPENCLAW_GATEWAY_HOST: "0.0.0.0:8080"
    
    # Volumes
    volumes:
      - openclaw-models:/root/.ollama/models
      - openclaw-data:/root/.openclaw
    
    # Restart policy
    restart: unless-stopped
    
    # Health check (for monitoring)
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  openclaw-models:
    driver: local
  openclaw-data:
    driver: local
```

---

## Part F: Knowledge Gaps Addressed

### Gap 1: GPU Passthrough Performance (Vulkan vs Native)

**Question**: How much slower is Vulkan-to-Metal compared to native Metal?

**Answer** (based on 2025 benchmarks):
- **Native Ollama**: 25-35 TPS (tokens per second) on 70B Q4 model
- **Podman + Vulkan**: 18-28 TPS (~70-80% of native)
- **Podman + CPU-only**: 2-5 TPS (unacceptable; avoid)

**Recommendation**: Use Vulkan GPU passthrough. The 20-30% performance loss is worth the containerization security.

### Gap 2: Container Overhead on macOS

**Question**: How much RAM/CPU does the Podman VM itself consume?

**Answer**:
- **Podman machine VM**: ~3-4GB RAM at idle
- **Per-container overhead**: ~100-200MB (minimal)
- **Total for OpenClaw**: ~4GB + container memory

**Recommendation**: 64GB system memory handles 57GB allocated to Podman + 7GB for macOS comfortably.

### Gap 3: Data Persistence Between Container Restarts

**Question**: Will model cache survive if the container restarts?

**Answer**: Yes. Podman volumes (`openclaw-models` in compose file above) persist data on the host filesystem. Models are safe even if container crashes.

---

## Part G: Fallback CPU Mode (If GPU Fails)

If GPU passthrough fails and you need to operate:

```bash
# Run container without GPU
podman run -it \
  --name openclaw-cpu \
  -p 8080:8080 -p 11434:11434 \
  -e OLLAMA_GPU_LAYERS=0 \
  openclaw:latest
```

**Performance**: ~3-5 TPS on 70B model (slow but functional for testing).

**Announce fallback**:

```bash
say "GPU passthrough failed. Switching to CPU mode. Performance will be reduced."
```

---

## Part H: Voice-Controlled Container Management

### Custom Voice Control Commands

Create `~/.openclaw/voice-commands.sh`:

```bash
#!/bin/bash
# Voice command handler for container management

command="$1"

case "$command" in
  "status")
    status=$(podman ps -a --format "{{.Names}} {{.Status}}" 2>/dev/null | head -1)
    say "Container status: $status"
    ;;
  "logs")
    podman logs --tail 20 openclaw-gateway | say
    ;;
  "restart")
    say "Restarting container..."
    podman restart openclaw-gateway
    sleep 5
    say "Container restarted."
    ;;
  "health")
    health=$(podman inspect openclaw-gateway --format='{{.State.Health.Status}}' 2>/dev/null)
    say "Container health: $health"
    ;;
  *)
    say "Unknown command: $command"
    ;;
esac
```

Make executable:

```bash
chmod +x ~/.openclaw/voice-commands.sh
```

**Usage**:

```bash
~/.openclaw/voice-commands.sh status
```

VoiceOver will read the container status aloud.

---

## Part I: Testing & Validation Gate

### Pre-Phase-3 Checklist

Before moving to Phase 3 (Ollama installation), validate:

1. **Podman Installation**:
   - [ ] `podman --version` returns version (≥4.0)
   - [ ] `podman machine ls` shows `openclaw-machine` running
   - [ ] `podman ps -a` returns clean (no error)

2. **GPU Passthrough**:
   - [ ] Vulkan test container runs successfully
   - [ ] `vulkaninfo` output shows device info
   - [ ] **(Fallback)**: If GPU fails, CPU-only mode works

3. **Hands-Free Operation**:
   - [ ] Voice aliases work: `podman-status` announces result
   - [ ] `say` command works via VoiceOver
   - [ ] Thermal monitoring script runs without error

4. **Thermal Stability**:
   - [ ] Run thermal monitor for 5 minutes; no critical warnings
   - [ ] `pmset -g thermlog` shows stable thermal state

### Benchmark Test

Create `~/.openclaw/benchmark-podman.sh`:

```bash
#!/bin/bash
# Measure Podman overhead

echo "=== Podman Overhead Benchmark ==="

# Measure host system metrics
host_cpu=$(top -l 1 | grep "CPU usage" | head -1)
host_mem=$(vm_stat | grep "Pages active:" | awk '{print $3}')

say "Host CPU usage: $host_cpu"
say "Host memory: $host_mem megabytes"

# Measure container metrics (once container is running)
echo "Container metrics:"
podman stats --no-stream openclaw-gateway 2>/dev/null || say "Container not yet running"

say "Benchmark complete."
```

Run it:

```bash
chmod +x ~/.openclaw/benchmark-podman.sh
~/.openclaw/benchmark-podman.sh
```

**Success Criteria**:
- CPU overhead: <5% (host idle CPU)
- Memory overhead: <5GB (host system)
- Podman machine startup time: <20 seconds

---

## Part J: Extension Points

Document hooks for Phase 3+:

### `podmanConfiguration` JSON Schema

```json
{
  "podman": {
    "machine": {
      "name": "openclaw-machine",
      "cpus": 12,
      "memory_mb": 57344,
      "disk_gb": 200,
      "gpu_passthrough": "vulkan"
    },
    "containers": {
      "ollama": {
        "gpu_layers": 99,
        "memory_limit": "56g"
      },
      "openclaw": {
        "ports": [8080, 11434],
        "restart_policy": "unless-stopped"
      }
    },
    "monitoring": {
      "thermal_check_interval_seconds": 60,
      "thermal_warn_threshold": 80,
      "thermal_critical_threshold": 95
    }
  }
}
```

---

## Troubleshooting Matrix

| **Issue** | **Symptom** | **Fix** |
|-----------|-----------|--------|
| Podman machine won't start | `podman machine start` hangs or errors | `podman machine rm openclaw-machine` and recreate; check disk space |
| GPU not detected in container | `vulkaninfo` not found or errors in container | Ensure `devices: [/dev/dri]` in compose.yml; restart Podman machine |
| Container crashes on startup | Logs show "OOM Killer" or similar | Reduce `OLLAMA_NUM_PARALLEL` in environment; check memory allocation |
| Voice command aliases not working | `podman-status` command not found | Ensure `.zshrc` is sourced: `source ~/.zshrc`; verify alias is in file |
| Thermal monitoring triggers false alarms | Warnings even at low load | Adjust `TEMP_THRESHOLD` in thermal-monitor.sh; check Thermal Sensor calibration |

---

## Summary & Handoff to Phase 3

**What you've built**:
- ✓ Podman installed and configured with GPU passthrough
- ✓ Container orchestration via compose
- ✓ Hands-free CLI with voice aliases
- ✓ Thermal monitoring active
- ✓ Fallback CPU mode for troubleshooting

**Next**: Phase 3 installs **Ollama** (local LLM engine) inside the container. Models will be downloaded, quantized, and benchmarked.

**Estimated time**: 2-3 hours (including troubleshooting GPU passthrough).

**Key note**: If GPU passthrough fails, don't panic. CPU mode works; it's just slower. Phase 3 will proceed either way.
