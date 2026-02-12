# PHASE 5: zRAM OPTIMIZATION & MEMORY PROFILING
## Design & Implementation Guide  
**Date**: February 12, 2026  
**Status**: Ready for Execution  
**Environment**: Terminal-only testing (no VS Code for accuracy)

---

## OBJECTIVE

Optimize zRAM and swap configuration for ML workload (Xoe-NovAi Stack) to:
1. Eliminate or significantly reduce OOM errors
2. Establish accurate memory usage baseline without IDE overhead
3. Identify sustainable concurrency limits
4. Document tuning strategy for production deployment

---

## PHASE 5 EXECUTION PHASES

### PHASE 5.A: PRE-OPTIMIZATION BASELINE (30 min)

**Goal**: Capture current memory behavior as baseline

**Steps**:
```bash
# 1. Close all applications including VS Code
# 2. Open clean terminal session
# 3. Check zRAM status
grep MemTotal /proc/meminfo
free -h
zramctl -b      # Check zRAM status if available
cat /proc/swaps # Check swap configuration

# 4. Record current kernel parameters
sysctl vm.swappiness vm.overcommit_memory vm.page-cluster

# 5. Start monitoring in separate terminal
btop -ncb > /tmp/baseline-before.log &

# 6. Bring up stack and measure
time docker-compose -f docker-compose.yml up -d
sleep 10
free -h > /tmp/memory-after-startup.txt
ps aux | grep -E "rag|chainlit|redis|caddy|mkdocs" > /tmp/processes-after-startup.txt

# 7. Check service health
curl -s http://127.0.0.1:8001/ | wc -l
curl -s http://127.0.0.1:8000/openapi.json | jq . | wc -l

# 8. Examine container resource usage
podman stats --no-stream xnai_rag_api > /tmp/rag-memory-baseline.txt
podman stats --no-stream xnai_chainlit_ui > /tmp/chainlit-memory-baseline.txt
```

**Capture** (save to repo):
- `/tmp/rag-memory-baseline.txt` → `phase-5-metrics/01-baseline-rag-memory.txt`
- `/tmp/chainlit-memory-baseline.txt` → `phase-5-metrics/01-baseline-chainlit-memory.txt`
- `/tmp/memory-after-startup.txt` → `phase-5-metrics/01-baseline-system-memory.txt`
- `/tmp/processes-after-startup.txt` → `phase-5-metrics/01-baseline-processes.txt`

**Expected Findings**:
- RAG API: ~5.5-5.8GB (94% of container limit)
- Chainlit UI: ~400-500MB
- Total system: ~7-7.5GB physical + maybe 1-2GB zRAM in use

---

### PHASE 5.B: KERNEL PARAMETER TUNING (15 min)

**Current Settings**: Default (likely swappiness=60)  
**Goal**: Optimize for ML workload behavior

**Proposed Tuning** (for testing):
```bash
# 1. Current settings for reference
sysctl -a | grep "vm\." | grep -E "swappiness|overcommit|page_cluster"

# 2. Test modifications (not permanent yet)
# Increase zRAM preference, but not too aggressive
sudo sysctl vm.swappiness=35      # Default 60 → 35 (more zRAM-friendly)
sudo sysctl vm.overcommit_memory=1  # Allow overcommit (common for containers)
sudo sysctl vm.page_cluster=3      # Batch page reads/writes

# 3. Verify changes
sysctl vm.swappiness vm.overcommit_memory vm.page_cluster

# 4. Document settings
echo "Tuned kernel parameters:" >> /tmp/phase5-tuning.log
sysctl vm.swappiness vm.overcommit_memory vm.page_cluster >> /tmp/phase5-tuning.log
```

**Monitoring During Tuning**:
- Watch `free -h` for swap-in activity
- Use `vmstat 1 10` to see page-in rate
- Monitor `/proc/swaps` for unusual swap usage

---

### PHASE 5.C: STRESS TEST WITH PROFILING (45 min)

**Goal**: Measure memory behavior under simulated load

**Test Scenario**: Concurrent requests to RAG API

**Setup**:
```bash
# 1. Create simple load test script
cat > /tmp/load-test.py << 'EOF'
import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://127.0.0.1:8000"
REQUESTS_PER_THREAD = 10
NUM_THREADS = 5

def make_request(i):
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"query": "What is machine learning?"},
            timeout=30
        )
        return {"status": response.status_code, "size": len(response.text)}
    except Exception as e:
        return {"error": str(e)}

def main():
    print(f"Starting load test: {NUM_THREADS} threads x {REQUESTS_PER_THREAD} requests")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for i in range(NUM_THREADS * REQUESTS_PER_THREAD):
            futures.append(executor.submit(make_request, i))
        
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    
    elapsed = time.time() - start_time
    print(f"Completed {len(results)} requests in {elapsed:.2f}s")
    print(f"Success: {sum(1 for r in results if 'status' in r)}")
    print(f"Errors: {sum(1 for r in results if 'error' in r)}")

if __name__ == "__main__":
    main()
EOF

# 2. Run concurrent monitoring + load test
(while true; do 
  echo "=== $(date) ===" >> /tmp/phase5-stress-test.log
  free -h >> /tmp/phase5-stress-test.log
  vmstat 1 1 | tail -1 >> /tmp/phase5-stress-test.log
  sleep 2
done) &
MONITOR_PID=$!

echo "Starting load test at $(date)"
python3 /tmp/load-test.py

# Save container stats during and after load
for container in xnai_rag_api xnai_chainlit_ui; do
  echo "=== $container ===" >> /tmp/phase5-container-stats.log
  podman stats --no-stream $container >> /tmp/phase5-container-stats.log
done

kill $MONITOR_PID

echo "Load test completed at $(date)"
```

**Data Collection**:
```bash
# During load: monitor memory in real-time
btop -ncb &   # Run in background

# After load: capture metrics
cat /proc/swaps >> /tmp/phase5-swaps.log
sysctl vm.swappiness >> /tmp/phase5-final-settings.log
```

**Save Outputs**:
- `phase-5-metrics/02-stress-test-monitoring.log`
- `phase-5-metrics/02-stress-test-container-stats.log`
- `phase-5-metrics/02-stress-test-btop.log`

---

### PHASE 5.D: ANALYSIS & RECOMMENDATIONS (20 min)

**Analyze Captured Data**:
```bash
# 1. Compare baseline vs. stressed
echo "=== BASELINE STATS ===" >> /tmp/phase5-analysis.txt
cat /tmp/memory-after-startup.txt >> /tmp/phase5-analysis.txt

echo "=== STRESSED STATS ===" >> /tmp/phase5-analysis.txt
tail -1 /tmp/phase5-stress-test.log >> /tmp/phase5-analysis.txt

# 2. Check for OOM incidents
dmesg | grep -i "out of memory" > /tmp/phase5-oom-check.txt
echo "OOM events: $(wc -l < /tmp/phase5-oom-check.txt)" >> /tmp/phase5-analysis.txt

# 3. Swap utilization impact
echo "=== SWAP ACTIVITY ===" >> /tmp/phase5-analysis.txt
grep "si\|so" /tmp/phase5-stress-test.log | head -10 >> /tmp/phase5-analysis.txt

# 4. Container resource peaks
echo "=== CONTAINER PEAKS ===" >> /tmp/phase5-analysis.txt
awk '{print $NF}' /tmp/phase5-container-stats.log | sort -h | tail -5 >> /tmp/phase5-analysis.txt
```

**Decision Criteria**:
```
OK to deploy if:
  ✅ No OOM events during stress test
  ✅ Swap-in rate < 50 MB/s (reasonable for zRAM)
  ✅ Response times stayed acceptable (<1s for simple queries)
  ✅ Chainlit UI stayed responsive (no lag)

Fix needed if:
  ❌ OOM events occurred → Increase zRAM or reduce container limit
  ❌ Swap-in rate > 200 MB/s → Reduce load or add memory
  ❌ Response times > 5s under load → Reduce context window or batch size
  ❌ Chainlit UI became unresponsive → Insufficient UI memory
```

---

## TUNING OPTIONS & ROLLBACK

### Option 1: Aggressive zRAM (Conservative Swappiness)
```bash
# If OOMs occur frequently:
sudo sysctl vm.swappiness=10              # Very zRAM-friendly
sudo sysctl vm.overcommit_memory=1        # Aggressive overcommit
# Restart: podman-compose restart
```

### Option 2: Balanced (Recommended Default)
```bash
# Good balance between zRAM and performance:
sudo sysctl vm.swappiness=35
sudo sysctl vm.overcommit_memory=1
```

### Option 3: Conservative (Keep More in RAM)
```bash
# If performance degrades:
sudo sysctl vm.swappiness=60              # System default
sudo sysctl vm.overcommit_memory=2        # Conservative overcommit
```

### Rollback to Defaults
```bash
sudo sysctl vm.swappiness=60
sudo sysctl vm.overcommit_memory=0
sudo sysctl vm.page_cluster=3
```

---

## PERMANENT TUNING (After Validation)

**If Tuning Successful**:
```bash
# Make permanent in /etc/sysctl.conf
sudo bash -c 'cat >> /etc/sysctl.conf << EOF

# Phase 5 ML Stack Optimization
vm.swappiness=35
vm.overcommit_memory=1
vm.page_cluster=3
EOF'

# Verify
sudo sysctl -p
```

---

## METRICS TO COLLECT & REPORT

### Key Metrics
| Metric | Tool | Baseline | Target | Meaning |
|--------|------|----------|--------|---------|
| Physical RAM Used | `free` | 7-7.5GB | <7.5GB | System not running out of memory |
| zRAM Usage | `zramctl -b` | 1-2GB | <3GB | Swap compression ratio OK |
| Swap I/O Rate | `vmstat` | TBD | <50 MB/s | Not thrashing |
| OOM Events | `dmesg` | Unknown | 0 | No out-of-memory kills |
| Response Time (95th %ile) | Load test | TBD | <2s | Acceptable performance |
| Max Container Memory | `podman stats` | 5.8GB | <5.8GB | Respects limits |

### Report Template
```markdown
# Phase 5 Testing Results

## Configuration
- kernel vm.swappiness: [value]
- kernel vm.overcommit_memory: [value]
- Container limits: 4GB RAG, 2GB UI

## Baseline (Clean System)
- Physical RAM: [value]
- zRAM: [value]
- OOM Events: 0

## Post-Optimization
- Physical RAM: [value]
- zRAM: [value]
- OOM Events: [count]
- Peak swap-in rate: [value] MB/s

## Load Test Results
- Concurrent requests: [number]
- Success rate: [%]
- P95 response time: [time]
- P99 response time: [time]
- Max memory during load: [value]

## Recommendation
[Summary of findings and recommended production settings]
```

---

## TIMELINE

**Recommended Execution**:
1. **Phase 5.A Baseline**: 30 minutes (system idle, capture metrics)
2. **Phase 5.B Tuning**: 15 minutes (apply kernel parameters)
3. **Phase 5.C Stress Test**: 45 minutes (run load test, monitor)
4. **Phase 5.D Analysis**: 20 minutes (analyze results, decide)

**Total**: ~2 hours of focused testing

---

## SUCCESS CRITERIA

✅ **Phase 5 Complete When**:
1. Baseline metrics captured and documented
2. Kernel parameters tuned and tested
3. Stress test completed without OOM events
4. Production-ready configuration identified
5. Testing report generated

✅ **Production Readiness**:
- No OOM events during test scenarios
- Swap activity < 100 MB/s sustained
- Response times acceptable (< 2sec P95)
- Configuration documented for reproducibility

---

## NEXT STEPS AFTER PHASE 5

1. **Memory Bank Update**: Record findings and tuning strategy
2. **GitHub Push**: Commit metrics and analysis
3. **Phase 6 Preparation**: Begin Observable/Auth implementation
4. **Continuous Monitoring**: Set up alerts for memory pressure

---

**Phase 5 Ready**: ✅ Design document complete. Ready for terminal execution.
