# Phase 5A — zRAM Deployment Record

Date: 2026-02-12
Status: Partially deployed (configuration & Tier‑4 artifacts created); host-level persistence pending privileged apply.

Summary
- zRAM configuration templates, systemd unit wrapper and health-check were added to the repo.
- `zstd` recommended; fallback to `lz4` when kernel lacks `zstd` support.
- `vm.swappiness` and `vm.page-cluster` tuning recommended and captured in `/etc/sysctl.d/99-xnai-zram-tuning.conf` (template in repo).
- Observability: `scripts/zram-health-check.sh` now writes Prometheus metrics to node_exporter textfile collector.

Files added/updated
- `internal_docs/01-strategic-planning/PHASE-5A-ZRAM-BEST-PRACTICES.md` (guidance + runbook)
- `scripts/zram-health-check.sh` (Prometheus metrics)
- `scripts/xnai-zram-init.sh` (auto-sizing wrapper)
- `TEMPLATE-xnai-zram.service` (updated to run wrapper)
- `TEMPLATE-sysctl-zram-tuning.conf`
- `internal_docs/01-strategic-planning/PHASE-5A-EXECUTION-CHECKLIST.md` (updated)
- `scripts/runtime_probe.py` (runtime probe: JSON + Prometheus textfile)
- `projects/foundation-observability/README.md` (project hub & roadmap)
- `tests/test_runtime_probe.py` (unit test for probe)

Operational notes
- Health-check metrics are written to `/var/lib/node_exporter/textfile_collector/xnai_zram.prom` when node_exporter is installed and writable.
- Prometheus scrape snippet and Grafana dashboard provided in `monitoring/` (import `monitoring/grafana/dashboards/xnai_zram_dashboard.json` and add `monitoring/prometheus/phase-5a-scrape.yml` to Prometheus `scrape_configs`).
- Persistence steps (requires sudo): copy sysctl template to `/etc/sysctl.d/`, install systemd unit, daemon-reload, enable/start service and optionally reboot for full persistence validation.

Rollback (quick)
1. `sudo systemctl stop --now xnai-zram.service`
2. `sudo swapoff /dev/zram0`
3. `sudo zramctl --reset /dev/zram0`
4. Restore `/etc/sysctl.d/` from backup or remove the `99-xnai-zram-tuning.conf` file

Acceptance for promotion to Phase 5B
- [ ] Integration tests show no OOMs under 5x load in staging
- [ ] Compression ratio ≥ 1.5 (target ≥ 2.0)
- [ ] Node_exporter confirms metrics available for 72h
- [ ] `runtime_probe.json` produced and ingested by RAG / Gemini (CI smoke test)
- [ ] `runtime_probe.prom` visible to Prometheus textfile collector and Grafana panels created
- [ ] Host-level persistence applied and validated
- [ ] zRAM configured to recommended defaults for 8-core/16GiB (8G, zstd level=3, streams=4)
- [ ] Sysctl tuning applied (`vm.swappiness=180`, `vm.page-cluster=0`, `vm.watermark_*` validated)
- [ ] Isolated-core policy validated (systemd `CPUAffinity=2-5` and container `--cpuset-cpus="2-5"` verified)
- [ ] Prometheus alert rules (Phase5A_*) deployed to staging Alertmanager routing and runbooks linked
- [ ] Copilot `ask_question` empirical test plan executed and results stored in `expert-knowledge/agent-tooling/`


Contacts
- Owner: The Architect
- Implementer: Cline
- Docs: memory_bank/PHASE-5A-DEPLOYED.md

