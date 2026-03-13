# VictoriaMetrics Tuning & Memory Efficiency (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **VictoriaMetrics** is used as a high-performance, memory-efficient alternative to Prometheus for time-series metrics storage. It provides 3-4x better memory efficiency and 10x better disk compression, making it ideal for the Ryzen 5700U environment.

---

## 🚀 Performance Benchmarks (2026)

| Metric | Prometheus (v3.x) | VictoriaMetrics (v1.135+) |
| :--- | :--- | :--- |
| **RAM per Sample** | 1-3 bytes | 0.2-0.5 bytes (5x better) |
| **Disk Compression** | ~1.3 bytes/sample | ~0.4 - 0.6 bytes/sample |
| **Ingestion Rate** | Moderate | High (optimized for batch) |
| **Scalability** | Linear memory scaling | Sub-linear memory scaling |

---

## 🛠 Tuning for Single-Node Efficiency

VictoriaMetrics is largely "zero-config," but for the XNAi stack (single-node, resource-constrained), the following flags are used:

### 1. Global Resource Limits
- **`-memory.allowedPercent=80`**: (Default in XNAi `docker-compose.yml`) Limits RAM usage to 80% of container allotment. 
- **`-memory.allowedBytes=1G`**: Hard limit set via Docker `deploy.resources.limits`.

### 2. Query Protection (OOM Prevention)
- **`-search.maxMemoryPerQuery=256MB`**: Prevents a single complex Grafana query from crashing the service.
- **`-search.maxConcurrentRequests=4`**: Limits simultaneous query processing to reduce RAM spikes.

### 3. Storage & Ingestion
- **`-retentionPeriod=365d`**: 1-year retention is sustainable due to high compression.
- **`-storageDataPath=/victoria-metrics-data`**: Persistent volume location.
- **`-search.maxSeries=1000000`**: Maximum number of unique series allowed in memory.

---

## 📈 Operational Workflows

### 1. Health Checks
VictoriaMetrics provides a simple health endpoint used by Docker/Consul:
```bash
wget -q --spider http://localhost:8428/health
```

### 2. Data Backup
Since VM uses a custom storage format, backups should be handled at the volume level or via snapshots:
1. Stop the container (optional but safer).
2. Backup `./data/victoriametrics/`.
3. Restart container.

### 3. Monitoring VM with VM
VictoriaMetrics exports its own metrics at `/metrics`. These are scraped by the same instance or a sidecar `vmagent`.
- **UI Access**: [http://localhost:8428/vmui](http://localhost:8428/vmui) for ad-hoc querying.

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| High Latency | Memory pressure or slow disk | Check `victoriametrics_self_memory_usage_bytes` and I/O wait. |
| OOM Crash | Too many concurrent heavy queries | Reduce `-search.maxConcurrentRequests`. |
| Data Gaps | Ingestion rate too high for CPU | Check `victoriametrics_ingested_samples_total`. |

---

## 📚 References
- [VictoriaMetrics Docs](https://docs.victoriametrics.com/)
- [XNAi Docker Compose](docker-compose.yml)
