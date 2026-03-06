---
title: TODOs — Phase-5A / Foundation Observability
---

Priority A
- Add `runtime_probe` to Prometheus textfile collector and include panels in Grafana (`monitoring/prometheus/`, `monitoring/grafana/`).
- Add systemd unit + timer to run `scripts/runtime_probe.py` every 60s (`scripts/systemd/`).
- Add CI smoke test that runs `scripts/runtime_probe.py --output-dir tmp` and validates JSON schema (`.github/workflows/smoke.yml`).

Priority B
- Extend `zram-health-check.sh` with additional metrics from `phase5a-best-practices.md` and add unit tests.
- Implement Gemini CLI commands to query `runtime_probe.json` and answer environment questions.

Priority C
- Add agent training docs + RAG ingestion of `FOUNDATION-OBSERVABILITY.md` and updated `memory_bank` entries.
- Add Alertmanager routing for Phase-5A alerts and link to runbooks.
