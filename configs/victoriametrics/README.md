# VictoriaMetrics Configuration

## Overview

VictoriaMetrics replaces Prometheus for XNAi Foundation metrics storage, providing:
- 3-4x memory efficiency (512MB-1GB vs 2-4GB)
- 10x compression
- Air-gap compatible (single binary)
- 365-day retention

## Service Details

| Property | Value |
|----------|-------|
| Image | `victoriametrics/victoria-metrics:latest` |
| Port | 8428 |
| Retention | 365 days |
| Memory Limit | 1GB |
| Data Path | `/victoria-metrics-data` |

## Endpoints

| Endpoint | Purpose |
|----------|---------|
| `http://localhost:8428/health` | Health check |
| `http://localhost:8428/api/v1/write` | Write metrics |
| `http://localhost:8428/api/v1/query` | Query metrics (PromQL) |
| `http://localhost:8428/api/v1/query_range` | Range query |
| `http://localhost:8428/vmui` | Web UI |

## Usage

### Writing Metrics

```bash
# Write a metric
curl -X POST "http://localhost:8428/api/v1/write" \
  -d "xnai_memory_block_utilization{block=\"active_context\"} 0.45"
```

### Querying Metrics

```bash
# Query a metric
curl "http://localhost:8428/api/v1/query" \
  -d 'query=xnai_memory_block_utilization'
```

### Grafana Integration

1. Add VictoriaMetrics as a Prometheus datasource
2. URL: `http://victoriametrics:8428`
3. Use PromQL queries (95% compatible)

## Memory Bank Metrics

The following metrics are tracked:

| Metric | Type | Description |
|--------|------|-------------|
| `xnai_memory_block_utilization` | Gauge | Block size / limit |
| `xnai_memory_overflow_events_total` | Counter | Overflow event count |
| `xnai_memory_tools_invocations_total` | Counter | Tool usage count |
| `xnai_context_compile_tokens` | Histogram | Token count in compiled context |
| `xnai_session_continuity_score` | Gauge | Session continuity metric |

## Configuration Files

Currently using default configuration. To customize:

1. Create `scrape_configs.yaml` for vmagent
2. Add alerting rules in `alerts.yaml`
3. Reference from command line args

## Migration from Prometheus

If migrating existing Prometheus data:

```bash
# Use vmctl to migrate
vmctl prometheus --prom-snapshot=/path/to/prometheus/snapshot \
  --vm-addr=http://localhost:8428
```

## Resources

- [VictoriaMetrics Docs](https://docs.victoriametrics.com)
- [MetricsQL Guide](https://docs.victoriametrics.com/MetricsQL.html)
- [vmctl Migration Tool](https://docs.victoriametrics.com/vmctl.html)
