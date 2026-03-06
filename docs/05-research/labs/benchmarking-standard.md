# Build Performance Benchmarking & Monitoring Framework
**Version**: 1.0 | **Date**: January 27, 2026

---

## Part 1: Comprehensive Build Benchmarking Script

Create: `~/.local/bin/benchmark-xnai-builds.sh`

```bash
#!/bin/bash
set -euo pipefail

DOCKERFILE="${1:-.}/Podmanfile.api"
BUILD_CONTEXT="${2:-.}"
BENCHMARK_LOG="/tmp/xnai-build-benchmark-$(date +%Y%m%d-%H%M%S).json"
ITERATIONS=3

# Initialize JSON report
cat > "$BENCHMARK_LOG" <<'EOF'
{
  "timestamp": "$(date -Iseconds)",
  "dockerfile": "",
  "context": "",
  "iterations": 0,
  "cold_build": [],
  "warm_build": [],
  "metrics": {}
}
EOF

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

benchmark_build() {
    local test_name=$1
    local build_cmd=$2
    local iteration=$3
    
    log "[$test_name - Iteration $iteration/$ITERATIONS] Starting..."
    
    # Measure build time
    start_time=$(date +%s%N)
    
    if eval "$build_cmd" >/dev/null 2>&1; then
        end_time=$(date +%s%N)
        duration_ms=$(( (end_time - start_time) / 1000000 ))
        log "[$test_name - Iteration $iteration] Completed in ${duration_ms}ms"
        echo "$duration_ms"
    else
        log "[$test_name] Build failed"
        echo "0"
    fi
}

# Main benchmark loop
log "=== XNAI BUILD BENCHMARKING START ==="
log "Podmanfile: $DOCKERFILE"
log "Context: $BUILD_CONTEXT"
log "Iterations: $ITERATIONS"
log ""

# Clean slate
podman rmi -f xnai-bench:test 2>/dev/null || true

# Cold build tests (no cache)
log "PHASE 1: Cold Builds (no Podman layer cache)"
cold_times=()
for i in $(seq 1 $ITERATIONS); do
    podman rmi -f xnai-bench:test 2>/dev/null || true
    time_ms=$(benchmark_build "COLD" "podman build -t xnai-bench:test -f '$DOCKERFILE' '$BUILD_CONTEXT'" "$i")
    cold_times+=("$time_ms")
    sleep 2
done

log ""
log "PHASE 2: Warm Builds (with Podman layer cache)"
warm_times=()
for i in $(seq 1 $ITERATIONS); do
    time_ms=$(benchmark_build "WARM" "podman build -t xnai-bench:test -f '$DOCKERFILE' '$BUILD_CONTEXT'" "$i")
    warm_times+=("$time_ms")
    sleep 2
done

# Calculate statistics
cold_avg=$(echo "${cold_times[@]}" | awk '{sum=0; for(i=1;i<=NF;i++)sum+=$i; print int(sum/NF)}')
warm_avg=$(echo "${warm_times[@]}" | awk '{sum=0; for(i=1;i<=NF;i++)sum+=$i; print int(sum/NF)}')
improvement=$(echo "scale=2; (($cold_avg - $warm_avg) / $cold_avg) * 100" | bc)

# Generate report
log ""
log "=== BENCHMARK RESULTS ==="
log "Cold builds (ms): ${cold_times[*]}"
log "Cold avg:        ${cold_avg}ms"
log ""
log "Warm builds (ms): ${warm_times[*]}"
log "Warm avg:        ${warm_avg}ms"
log ""
log "Improvement:     ${improvement}% faster"
log ""

# Cleanup
podman rmi -f xnai-bench:test 2>/dev/null || true

log "Report saved to: $BENCHMARK_LOG"
log "=== BENCHMARK COMPLETE ==="
```

---

## Part 2: Grafana Dashboard JSON (Prometheus Metrics)

```json
{
  "dashboard": {
    "title": "APT-Cacher-NG Build Performance",
    "panels": [
      {
        "title": "Build Time (Cold vs Warm)",
        "targets": [
          {
            "expr": "build_time_seconds{job=\"xnai-builds\", type=\"cold\"}"
          },
          {
            "expr": "build_time_seconds{job=\"xnai-builds\", type=\"warm\"}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Cache Hit Ratio",
        "targets": [
          {
            "expr": "rate(apt_cache_hits_total[5m]) / rate(apt_cache_requests_total[5m])"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Cache Size Over Time",
        "targets": [
          {
            "expr": "apt_cache_size_bytes"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Service Health",
        "targets": [
          {
            "expr": "apt_cache_health"
          }
        ],
        "type": "stat",
        "thresholds": [0.5, 1]
      }
    ],
    "refresh": "30s",
    "time": {
      "from": "now-7d",
      "to": "now"
    }
  }
}
```

---

## Part 3: Prometheus Scrape Configuration

Add to `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'apt-cache-metrics'
    static_configs:
      - targets: ['127.0.0.1:9100']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'apt-cache-primary'
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'apt_cache_.*'
        action: keep

  - job_name: 'xnai-builds'
    static_configs:
      - targets: ['localhost:9000']
    scrape_interval: 60s
    scrape_timeout: 10s
```

---

## Part 4: Regression Detection Script

Create: `~/.local/bin/detect-build-regression.py`

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

BENCHMARK_DIR = Path("/tmp")
THRESHOLD_PERCENT = 10  # Alert if build slows >10%

def load_benchmarks():
    """Load recent benchmark reports"""
    reports = sorted(
        BENCHMARK_DIR.glob("xnai-build-benchmark-*.json"),
        reverse=True
    )
    return [json.load(open(r)) for r in reports[:5]]

def analyze_trend():
    """Detect performance regressions"""
    reports = load_benchmarks()
    if len(reports) < 2:
        print("Need at least 2 benchmark runs for trend analysis")
        return
    
    latest = reports[0]["metrics"]["warm_build_avg_ms"]
    previous = reports[1]["metrics"]["warm_build_avg_ms"]
    
    regression_pct = ((latest - previous) / previous) * 100
    
    if regression_pct > THRESHOLD_PERCENT:
        print(f"❌ REGRESSION DETECTED: {regression_pct:.1f}% slower")
        sys.exit(1)
    elif regression_pct < -THRESHOLD_PERCENT:
        print(f"✓ IMPROVEMENT: {-regression_pct:.1f}% faster")
        sys.exit(0)
    else:
        print(f"✓ STABLE: {regression_pct:+.1f}% (within ±{THRESHOLD_PERCENT}%)")
        sys.exit(0)

if __name__ == '__main__':
    analyze_trend()
```

---

## Part 5: Success Criteria Thresholds

| **Metric** | **Target** | **Warning** | **Critical** |
|---|---|---|---|
| Cold build time | <5 min | >6 min | >8 min |
| Warm build time | <45 sec | >60 sec | >120 sec |
| Cache hit ratio | >70% | >50% | <50% |
| Improvement ratio | >5× | >4× | <3× |
| Cache size | <30GB | <40GB | >50GB |
| Service uptime | 99.9% | 99% | <99% |

---

**Performance Monitoring by**: Xoe-NovAi DevOps
**Last Updated**: January 27, 2026