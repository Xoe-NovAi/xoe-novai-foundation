# TASK 5A.1: COLLECT BASELINE METRICS
## Objective
Capture current system state and validate prerequisites before applying Phase 5A changes.

**Tier**: 3 (Task Module)  
**Duration**: 30 minutes  
**Prerequisites**: Sudo/root recommended, `zramctl` (optional), `systemctl`, `swapon`  

---

## OUTPUTS
- `/tmp/phase5a-baseline/baseline-<timestamp>.txt` (complete snapshot)
- Short summary of kernel params, container memory usage, and recent OOM events

---

## PREPARATION / SAFETY
- Run as root or with `sudo` where possible. If you cannot run as root, note which checks were skipped.
- Ensure at minimum `sysctl`, `swapon` are available. `zramctl` helpful but not required for baseline.

---

## STEPS

1. Create baseline dir
```bash
sudo mkdir -p /tmp/phase5a-baseline
sudo chown $(whoami) /tmp/phase5a-baseline
```

2. Capture basic system state
```bash
free -h > /tmp/phase5a-baseline/memory-start.txt
uname -a > /tmp/phase5a-baseline/uname.txt
cat /proc/meminfo > /tmp/phase5a-baseline/meminfo.txt
```

3. Record kernel tunables
```bash
sysctl vm.swappiness vm.page-cluster vm.vfs_cache_pressure vm.watermark_scale_factor > /tmp/phase5a-baseline/kernel-params.txt
```

4. zRAM & swap status (if zramctl present)
```bash
if command -v zramctl >/dev/null 2>&1; then
  zramctl > /tmp/phase5a-baseline/zram.txt
fi
swapon --show > /tmp/phase5a-baseline/swapon.txt
```

5. Container memory snapshot (podman/docker detection)
```bash
if command -v podman >/dev/null 2>&1; then
  podman stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}" > /tmp/phase5a-baseline/containers.txt
elif command -v docker >/dev/null 2>&1; then
  docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}" > /tmp/phase5a-baseline/containers.txt
else
  echo "No container runtime detected" > /tmp/phase5a-baseline/containers.txt
fi
```

6. Recent OOM events (robust fallback)
```bash
# Try dmesg first (may require sudo)
if sudo dmesg | grep -q "Out of memory" 2>/dev/null; then
  sudo dmesg | grep "Out of memory" | tail -n 20 > /tmp/phase5a-baseline/oom.txt
else
  # Fallback to journalctl -k which may require sudo
  sudo journalctl -k --no-pager | grep "Out of memory" | tail -n 20 > /tmp/phase5a-baseline/oom.txt || echo "No OOM events or access denied" > /tmp/phase5a-baseline/oom.txt
fi
```

7. Capture running processes by memory
```bash
ps aux --sort=-rss | head -15 > /tmp/phase5a-baseline/top-mem.txt
```

8. Summarize baseline (human-readable)
```bash
cat /tmp/phase5a-baseline/memory-start.txt
cat /tmp/phase5a-baseline/kernel-params.txt
cat /tmp/phase5a-baseline/zram.txt 2>/dev/null || true
```

---

## VALIDATION
- Baseline file exists: `ls -la /tmp/phase5a-baseline/`
- Kernel parameters recorded
- No unexpected OOM events in last 24 hours (if logs accessible)

---

## TROUBLESHOOTING
- If `dmesg` is inaccessible, run `sudo journalctl -k --no-pager` to inspect kernel logs.
- If container runtime not detected, ensure `podman` or `docker` installed.

---

## NEXT TASK
→ Task 5A.2: Apply Kernel Parameters
