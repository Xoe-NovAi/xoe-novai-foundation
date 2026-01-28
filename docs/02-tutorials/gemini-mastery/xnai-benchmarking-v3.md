# Build Performance Benchmarking & Monitoring Framework (2026 Statistical Edition)
**Version**: 3.0 | **Date**: January 27, 2026

---

## Part 1: Comprehensive Build Benchmarking Script (with Real Cache Hit Parsing)

Create: `~/.local/bin/benchmark-xnai-builds.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# XOE-NOVAI BUILD BENCHMARKING SCRIPT (2026)
# Ma'at Principle: Truth (accurate measurement) + Order (reproducibility)
# ============================================================================

DOCKERFILE="${1:-.}/Dockerfile.api"
BUILD_CONTEXT="${2:-.}"
BENCHMARK_LOG="/tmp/xnai-build-benchmark-$(date +%Y%m%d-%H%M%S).json"
ITERATIONS=3
BUILD_TAG="xnai-benchmark:$(date +%s)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[✓]${NC} [$(date '+%H:%M:%S')] $*"
}

warn() {
    echo -e "${YELLOW}[⚠]${NC} [$(date '+%H:%M:%S')] $*"
}

error() {
    echo -e "${RED}[✗]${NC} [$(date '+%H:%M:%S')] $*"
}

# ============================================================================
# FUNCTION: Benchmark Single Build
# ============================================================================

benchmark_build() {
    local test_name=$1
    local build_cmd=$2
    local iteration=$3
    
    log "[$test_name - Iteration $iteration/$ITERATIONS] Starting..."
    
    start_time=$(date +%s%N)
    
    if eval "$build_cmd" >/dev/null 2>&1; then
        end_time=$(date +%s%N)
        duration_ms=$(( (end_time - start_time) / 1000000 ))
        log "[$test_name - Iteration $iteration] Completed in ${duration_ms}ms ($(echo "scale=2; $duration_ms / 1000" | bc)s)"
        echo "$duration_ms"
    else
        error "[$test_name - Iteration $iteration] Build failed"
        echo "0"
    fi
}

# ============================================================================
# FUNCTION: Parse Cache Hit Ratio from /acng-report.html
# ============================================================================

get_cache_hit_ratio() {
    local report_html
    report_html=$(curl -s http://127.0.0.1:3142/acng-report.html 2>/dev/null || echo "")
    
    if [[ -z "$report_html" ]]; then
        echo "0 0 0.00"  # hits total ratio
        return
    fi
    
    # Parse statistics from HTML report
    # Example patterns:
    #   "Hits: 1234"
    #   "Total Requests: 1290"
    #   Or from table: <td>Hit</td><td>1234</td>
    
    hits=$(echo "$report_html" | grep -oP '(?i)hit[^0-9]*\K\d+' | head -1 || echo 0)
    misses=$(echo "$report_html" | grep -oP '(?i)miss[^0-9]*\K\d+' | head -1 || echo 0)
    total=$((hits + misses))
    
    if [[ $total -gt 0 ]]; then
        ratio=$(echo "scale=4; ($hits / $total) * 100" | bc)
    else
        ratio="0.00"
    fi
    
    echo "$hits $total $ratio"
}

# ============================================================================
# FUNCTION: Calculate Statistics (Mean, Median, StdDev)
# ============================================================================

calc_stats() {
    local values=("$@")
    local count=${#values[@]}
    
    if [[ $count -eq 0 ]]; then
        echo "0 0 0"
        return
    fi
    
    # Calculate mean
    local sum=0
    for val in "${values[@]}"; do
        sum=$((sum + val))
    done
    local mean=$((sum / count))
    
    # Calculate median
    IFS=$'\n' sorted=($(sort -n <<<"${values[*]}"))
    unset IFS
    local median
    if (( count % 2 == 1 )); then
        median=${sorted[$((count / 2))]}
    else
        local mid1=${sorted[$((count / 2 - 1))]}
        local mid2=${sorted[$((count / 2))]}
        median=$(( (mid1 + mid2) / 2 ))
    fi
    
    # Calculate standard deviation
    local var_sum=0
    for val in "${values[@]}"; do
        diff=$((val - mean))
        var_sum=$((var_sum + diff * diff))
    done
    local variance=$((var_sum / count))
    local stddev=$(echo "scale=2; sqrt($variance)" | bc)
    
    echo "$mean $median $stddev"
}

# ============================================================================
# INITIALIZE
# ============================================================================

log "=== XOE-NOVAI BUILD BENCHMARKING START ==="
log "Dockerfile: $DOCKERFILE"
log "Context: $BUILD_CONTEXT"
log "Iterations: $ITERATIONS"
log "Timestamp: $(date -Iseconds)"
log ""

# Verify apt-cacher-ng is running
if ! curl -sf http://127.0.0.1:3142/acng-report.html >/dev/null 2>&1; then
    warn "apt-cacher-ng not accessible, starting service..."
    systemctl --user start apt-cacher-ng.container
    sleep 10
    
    if ! curl -sf http://127.0.0.1:3142/acng-report.html >/dev/null 2>&1; then
        error "Failed to start apt-cacher-ng, benchmarks may be inaccurate"
    fi
fi

# Get initial cache statistics
read -r hits_before total_before ratio_before <<< "$(get_cache_hit_ratio)"
log "Initial cache stats: $hits_before hits / $total_before total ($ratio_before% hit ratio)"
log ""

# Clean slate
podman rmi -f "$BUILD_TAG" 2>/dev/null || true

# ============================================================================
# PHASE 1: Cold Builds (no Docker layer cache, clearing apt cache)
# ============================================================================

log "PHASE 1: Cold Builds (no cache)"
cold_times=()

for i in $(seq 1 $ITERATIONS); do
    # Clear Docker layer cache
    podman rmi -f "$BUILD_TAG" 2>/dev/null || true
    
    # Clear apt-cacher-ng cache (first iteration only for true cold build)
    if [[ $i -eq 1 ]]; then
        log "Clearing apt-cacher-ng cache for baseline measurement..."
        cache_mountpoint=$(podman volume inspect apt-cache --format '{{.Mountpoint}}')
        podman unshare rm -rf "$cache_mountpoint"/* || warn "Failed to clear cache"
        systemctl --user restart apt-cacher-ng.container
        sleep 15
    fi
    
    time_ms=$(benchmark_build "COLD" "podman build --no-cache -t '$BUILD_TAG' -f '$DOCKERFILE' '$BUILD_CONTEXT'" "$i")
    cold_times+=("$time_ms")
    sleep 2
done

# ============================================================================
# PHASE 2: Warm Builds (with Docker layer cache + apt cache)
# ============================================================================

log ""
log "PHASE 2: Warm Builds (with cache)"
warm_times=()

for i in $(seq 1 $ITERATIONS); do
    time_ms=$(benchmark_build "WARM" "podman build -t '$BUILD_TAG' -f '$DOCKERFILE' '$BUILD_CONTEXT'" "$i")
    warm_times+=("$time_ms")
    sleep 2
done

# ============================================================================
# CALCULATE STATISTICS
# ============================================================================

log ""
log "Calculating statistics..."

# Cold build stats
read -r cold_mean cold_median cold_stddev <<< "$(calc_stats "${cold_times[@]}")"

# Warm build stats
read -r warm_mean warm_median warm_stddev <<< "$(calc_stats "${warm_times[@]}")"

# Performance improvement
if [[ $warm_mean -gt 0 ]]; then
    improvement=$(echo "scale=2; (($cold_mean - $warm_mean) / $cold_mean) * 100" | bc)
    speedup=$(echo "scale=2; $cold_mean / $warm_mean" | bc)
else
    improvement="N/A"
    speedup="N/A"
fi

# Get final cache statistics
read -r hits_after total_after ratio_after <<< "$(get_cache_hit_ratio)"
log "Final cache stats: $hits_after hits / $total_after total ($ratio_after% hit ratio)"

# Calculate cache requests during benchmark
cache_requests=$((total_after - total_before))
cache_hits=$((hits_after - hits_before))

if [[ $cache_requests -gt 0 ]]; then
    benchmark_hit_ratio=$(echo "scale=2; ($cache_hits / $cache_requests) * 100" | bc)
else
    benchmark_hit_ratio="0.00"
fi

# ============================================================================
# GENERATE JSON REPORT (for Prometheus export)
# ============================================================================

cat > "$BENCHMARK_LOG" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "dockerfile": "$DOCKERFILE",
  "context": "$BUILD_CONTEXT",
  "iterations": $ITERATIONS,
  "cold_build": {
    "times_ms": [$(IFS=,; echo "${cold_times[*]}")],
    "mean_ms": $cold_mean,
    "median_ms": $cold_median,
    "stddev_ms": $cold_stddev,
    "mean_sec": $(echo "scale=2; $cold_mean / 1000" | bc)
  },
  "warm_build": {
    "times_ms": [$(IFS=,; echo "${warm_times[*]}")],
    "mean_ms": $warm_mean,
    "median_ms": $warm_median,
    "stddev_ms": $warm_stddev,
    "mean_sec": $(echo "scale=2; $warm_mean / 1000" | bc)
  },
  "performance": {
    "improvement_percent": "$improvement",
    "speedup_factor": "$speedup"
  },
  "cache_stats": {
    "hits": $cache_hits,
    "requests": $cache_requests,
    "hit_ratio_percent": "$benchmark_hit_ratio"
  }
}
EOF

# ============================================================================
# EXPORT TO PROMETHEUS TEXTFILE FORMAT
# ============================================================================

metrics_dir="${HOME}/.local/var/lib/prometheus-textfile"
mkdir -p "$metrics_dir"

cat > "${metrics_dir}/xnai_build_benchmark.prom" <<EOF
# HELP xnai_build_cold_time_seconds Average cold build time in seconds
# TYPE xnai_build_cold_time_seconds gauge
xnai_build_cold_time_seconds $(echo "scale=3; $cold_mean / 1000" | bc)

# HELP xnai_build_warm_time_seconds Average warm build time in seconds
# TYPE xnai_build_warm_time_seconds gauge
xnai_build_warm_time_seconds $(echo "scale=3; $warm_mean / 1000" | bc)

# HELP xnai_build_speedup_factor Speedup factor (cold/warm)
# TYPE xnai_build_speedup_factor gauge
xnai_build_speedup_factor $speedup

# HELP xnai_cache_hit_ratio Cache hit ratio during benchmark
# TYPE xnai_cache_hit_ratio gauge
xnai_cache_hit_ratio $(echo "scale=4; $benchmark_hit_ratio / 100" | bc)

# HELP xnai_benchmark_timestamp Benchmark execution timestamp
# TYPE xnai_benchmark_timestamp gauge
xnai_benchmark_timestamp $(date +%s)
EOF

# ============================================================================
# DISPLAY RESULTS
# ============================================================================

log ""
log "=== BENCHMARK RESULTS ==="
log ""
log "Cold Build (no cache):"
log "  Times (ms):    ${cold_times[*]}"
log "  Mean:          ${cold_mean}ms ($(echo "scale=2; $cold_mean / 1000" | bc)s)"
log "  Median:        ${cold_median}ms"
log "  StdDev:        ${cold_stddev}ms"
log ""
log "Warm Build (with cache):"
log "  Times (ms):    ${warm_times[*]}"
log "  Mean:          ${warm_mean}ms ($(echo "scale=2; $warm_mean / 1000" | bc)s)"
log "  Median:        ${warm_median}ms"
log "  StdDev:        ${warm_stddev}ms"
log ""
log "Performance Improvement:"
log "  Time Saved:    ${improvement}%"
log "  Speedup:       ${speedup}x"
log ""
log "Cache Statistics (during benchmark):"
log "  Requests:      $cache_requests"
log "  Hits:          $cache_hits"
log "  Hit Ratio:     ${benchmark_hit_ratio}%"
log ""

# ============================================================================
# PASS/FAIL CRITERIA
# ============================================================================

pass_count=0
fail_count=0

# Test 1: Warm build <60 sec
if [[ $warm_mean -lt 60000 ]]; then
    log "✓ PASS: Warm build <60s"
    ((pass_count++))
else
    warn "✗ FAIL: Warm build ≥60s (target: <60s)"
    ((fail_count++))
fi

# Test 2: Cache hit ratio >70%
if (( $(echo "$benchmark_hit_ratio > 70" | bc -l) )); then
    log "✓ PASS: Cache hit ratio >70%"
    ((pass_count++))
else
    warn "✗ FAIL: Cache hit ratio ≤70% (target: >70%)"
    ((fail_count++))
fi

# Test 3: Speedup >3x
if [[ "$speedup" != "N/A" ]] && (( $(echo "$speedup > 3" | bc -l) )); then
    log "✓ PASS: Speedup >3x"
    ((pass_count++))
else
    warn "✗ FAIL: Speedup ≤3x (target: >3x)"
    ((fail_count++))
fi

log ""
log "Tests Passed: $pass_count/3"
log "Tests Failed: $fail_count/3"
log ""

# Cleanup
podman rmi -f "$BUILD_TAG" 2>/dev/null || true

log "JSON report: $BENCHMARK_LOG"
log "Prometheus metrics: ${metrics_dir}/xnai_build_benchmark.prom"
log "=== BENCHMARK COMPLETE ==="

# Exit with failure code if any tests failed
exit $fail_count
```

Make executable:
```bash
chmod +x ~/.local/bin/benchmark-xnai-builds.sh
```

---

## Part 2: Grafana Dashboard JSON (Production-Ready)

Save as: `grafana-dashboard-apt-cache.json`

```json
{
  "dashboard": {
    "title": "Xoe-NovAi APT-Cacher-NG Performance Dashboard",
    "tags": ["xnai", "apt-cache", "build-performance"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Build Time (Cold vs Warm)",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "xnai_build_cold_time_seconds",
            "legendFormat": "Cold Build"
          },
          {
            "expr": "xnai_build_warm_time_seconds",
            "legendFormat": "Warm Build"
          }
        ],
        "yaxes": [
          {
            "format": "s",
            "label": "Build Time"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": {
                "params": [60],
                "type": "gt"
              },
              "operator": {
                "type": "and"
              },
              "query": {
                "params": ["xnai_build_warm_time_seconds"]
              },
              "reducer": {
                "type": "avg"
              },
              "type": "query"
            }
          ],
          "name": "Warm Build >60s"
        }
      },
      {
        "id": 2,
        "title": "Cache Hit Ratio",
        "type": "stat",
        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "apt_cache_hit_ratio * 100"
          }
        ],
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": ["lastNotNull"]
          },
          "text": {
            "valueSize": 60
          }
        },
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 50, "color": "yellow"},
                {"value": 70, "color": "green"}
              ]
            },
            "unit": "percent"
          }
        }
      },
      {
        "id": 3,
        "title": "Cache Size Over Time",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "apt_cache_size_bytes / 1024 / 1024 / 1024",
            "legendFormat": "Cache Size (GB)"
          }
        ],
        "yaxes": [
          {
            "format": "decgbytes",
            "label": "Size"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": {
                "params": [50],
                "type": "gt"
              },
              "query": {
                "params": ["apt_cache_size_bytes / 1024 / 1024 / 1024"]
              },
              "type": "query"
            }
          ],
          "name": "Cache Size >50GB"
        }
      },
      {
        "id": 4,
        "title": "Service Health",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8},
        "targets": [
          {
            "expr": "apt_cache_health"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 1, "color": "green"}
              ]
            },
            "mappings": [
              {"type": "value", "value": "0", "text": "Down"},
              {"type": "value", "value": "1", "text": "Up"}
            ]
          }
        }
      },
      {
        "id": 5,
        "title": "Speedup Factor",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 12},
        "targets": [
          {
            "expr": "xnai_build_speedup_factor"
          }
        ],
        "options": {
          "textMode": "value_and_name"
        },
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 3, "color": "yellow"},
                {"value": 5, "color": "green"}
              ]
            },
            "unit": "none",
            "decimals": 2
          }
        }
      },
      {
        "id": 6,
        "title": "Vulnerabilities",
        "type": "stat",
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
        "targets": [
          {
            "expr": "apt_cache_vulnerabilities_critical",
            "legendFormat": "Critical"
          },
          {
            "expr": "apt_cache_vulnerabilities_high",
            "legendFormat": "High"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 1, "color": "yellow"},
                {"value": 5, "color": "red"}
              ]
            }
          }
        }
      }
    ],
    "refresh": "30s",
    "time": {
      "from": "now-7d",
      "to": "now"
    },
    "version": 1
  }
}
```

Import to Grafana:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d @grafana-dashboard-apt-cache.json \
  http://admin:admin@localhost:3000/api/dashboards/db
```

---

## Part 3: Success Criteria Thresholds (2026 Edition)

| **Metric** | **Target** | **Warning** | **Critical** | **Measurement** |
|---|---|---|---|---|
| Cold build time | <5 min (300s) | >6 min (360s) | >8 min (480s) | `xnai_build_cold_time_seconds` |
| Warm build time | <45 sec | >60 sec | >120 sec | `xnai_build_warm_time_seconds` |
| Cache hit ratio | >70% | >50% | <50% | `apt_cache_hit_ratio * 100` |
| Speedup factor | >5× | >4× | <3× | `xnai_build_speedup_factor` |
| Cache size | <30GB | <40GB | >50GB | `apt_cache_size_bytes / (1024^3)` |
| Service uptime | 99.9% | 99% | <99% | `avg_over_time(apt_cache_health[7d])` |
| Vulnerabilities (CRITICAL) | 0 | 0 | >0 | `apt_cache_vulnerabilities_critical` |

---

**Performance Monitoring by**: Xoe-NovAi DevOps  
**Last Updated**: January 27, 2026  
**Prepared by**: Xoe-NovAi Architecture Team