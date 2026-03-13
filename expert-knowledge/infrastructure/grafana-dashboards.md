# Grafana Observability & Dashboards (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **Grafana** (v11.4.0) serves as the centralized observability and visualization platform. It correlates metrics from VictoriaMetrics, logs from Caddy/RAG API, and provides real-time health dashboards for the entire stack.

---

## 🚀 Unified Observability Stack (2026)

The XNAi stack follows the "VictoriaMetrics-First" approach for high-efficiency observability:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Source** | VictoriaMetrics | Long-term, high-compression metrics storage |
| **Query Language** | MetricsQL | Backwards compatible with PromQL, optimized for VM |
| **Alerting** | Grafana Managed Alerts | Unified alerting across metrics and logs |
| **Provisioning** | Dashboards-as-Code | Ensures consistency via automated YAML/JSON imports |

---

## 🛠 Dashboard Design & Best Practices

The XNAi Foundation uses two primary monitoring methodologies:

### 1. RED Method (Services)
Applied to the RAG API, Chainlit UI, and Vikunja:
- **Rate**: Requests per second (e.g., `sum(rate(xnai_http_requests_total[5m]))`)
- **Errors**: Failed requests (HTTP 5xx/4xx)
- **Duration**: Latency percentiles (P50, P95, P99)

### 2. USE Method (Infrastructure)
Applied to the Ryzen 5700U host and container resources:
- **Utilization**: % of CPU/RAM busy
- **Saturation**: IO wait, network queueing
- **Errors**: Hardware/OS errors, OOM kills

---

## 📈 Operational Workflows

### 1. Provisioned Dashboards
Dashboards are stored as JSON files in `monitoring/dashboards/` and automatically provisioned on startup.
- **Foundation Health**: High-level overview of all stack services.
- **RAG Performance**: Detailed metrics for LLM latency, token usage, and cache hit rates.
- **Infrastrucutre Ops**: Node-level metrics (CPU, RAM, Disk I/O).

### 2. Data Links & Correlations
From a spike in LLM latency, users can click to jump directly to the relevant logs in Loki or trace IDs in Tempo (if enabled).

### 3. Alerting & Notifications
Alerts are configured to trigger when:
- RAG API P95 latency > 2s for 5 minutes.
- Service availability < 99%.
- Memory usage > 90% for 10 minutes.

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Dashboard Flickering | Rapid refresh or slow data source | Increase refresh interval to 30s+ or optimize VM queries. |
| Missing Metrics | Scrape failure or label mismatch | Check `victoriametrics_scrape_targets` and service discovery. |
| Dashboard Sprawl | Too many manual dashboards | Move to provisioned dashboards and use library panels. |

---

## 📚 References
- [Grafana Documentation](https://grafana.com/docs/)
- [VictoriaMetrics MetricsQL](https://docs.victoriametrics.com/metricsql/)
- [XNAi Monitoring Strategy](memory_bank/strategies/production-tight-stack/PLAN-PRODUCTION-TIGHT-STACK.md)
