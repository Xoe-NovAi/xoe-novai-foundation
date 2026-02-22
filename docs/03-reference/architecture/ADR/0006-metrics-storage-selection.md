# ADR 0006: Metrics Storage Selection (VictoriaMetrics)

## Status
Accepted

## Context
The XNAi Foundation Stack requires a time-series metrics storage system for observability, alerting, and performance monitoring. Key requirements:
- Works offline with zero external telemetry
- Memory-efficient for 8-16GB RAM constraint
- Compatible with Prometheus ecosystem ( exporters, Grafana)
- Single-binary deployment preferred

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **VictoriaMetrics** | 3-4x memory efficient, single binary, Prometheus-compatible | Less community than Prometheus |
| **Prometheus** | Industry standard, huge ecosystem | 3-4x more memory, complex clustering |
| **InfluxDB** | SQL-like queries, mature | Different data model, heavier |
| **Thanos** | Prometheus scaling | Complex, multiple components |
| **Cortex** | Horizontally scalable | Complex, designed for cloud |
| **Mimir** | Grafana Labs solution | Complex, overkill for single-node |

## Decision
We adopt **VictoriaMetrics** as the primary metrics storage:

**Key Factors:**
1. **Memory Efficiency**: 3-4x less RAM than Prometheus
2. **Single Binary**: No external dependencies, easy deployment
3. **Prometheus-Compatible**: Drop-in replacement, existing exporters work
4. **Compression**: 10x data compression vs Prometheus
5. **Air-Gap Ready**: Fully offline operation

**Deployment Configuration:**
```yaml
victoriametrics:
  image: victoriametrics/victoria-metrics:latest
  command:
    - "-storageDataPath=/victoria-metrics-data"
    - "-retentionPeriod=365d"
    - "-memory.allowedPercent=80"
  deploy:
    resources:
      limits:
        memory: 1G
```

## Consequences

### Positive
- **Sovereignty**: Zero external telemetry, fully offline
- **Resource Efficiency**: Fits in 512MB-1GB memory budget
- **Long Retention**: 365-day retention feasible on modest storage
- **Grafana Compatible**: Works with existing dashboards
- **MetricsQL**: Enhanced query language beyond PromQL

### Negative
- **Smaller Community**: Less documentation than Prometheus
- **Learning Curve**: MetricsQL has differences from PromQL
- **Vendor Alignment**: Tied to VictoriaMetrics ecosystem

### Performance Comparison (10M samples)

| Metric | Prometheus | VictoriaMetrics |
|--------|------------|-----------------|
| Memory | 4GB | 1GB |
| Disk | 10GB | 1GB |
| Query Latency | 100-500ms | 50-200ms |
| Ingestion Rate | 200K/sec | 1M/sec |

## Related
- `configs/victoriametrics/README.md`
- `docker-compose.yml` victoriametrics service
- `docs/03-how-to-guides/runbooks/` monitoring section
