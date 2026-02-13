# PHASE 5A — zRAM Best Practices (research-backed)

Purpose
- Concise, actionable best-practices for deploying and operating zRAM as swap in XNAi Foundation Phase 5A.
- Source: ArchWiki, Fedora SwapOnZRAM, util-linux zramctl manpage, stress-ng, psutil.

Summary (TL;DR)
- Prefer `zstd` compression where available; fall back to `lz4` when `zstd` is not exposed by the kernel.
- Start with conservative sizing: `min(ram / 2, 4GiB)` and only increase after staging verification.
- Use `vm.swappiness = 180` and `vm.page-cluster = 0` for responsive in‑RAM swap behavior.
- Expose health metrics to Prometheus via node_exporter textfile collector (see `scripts/zram-health-check.sh`).

Sizing heuristics (recommended)
- RAM ≤ 4 GiB  -> zram-size = min(ram/2, 1 GiB)
- 4 GiB < RAM ≤ 16 GiB -> zram-size = min(ram/2, 4 GiB)
- 16 GiB < RAM ≤ 64 GiB -> zram-size = min(ram/4, 8 GiB)
- RAM > 64 GiB -> zram-size = min(ram/8, 16 GiB)

Kernel tuning (explanatory rationale)
- vm.swappiness = 180 — encourages earlier pageout to zram (ArchWiki/Fedora recommended for in-memory swap).
- vm.page-cluster = 0 — avoids large clustered page I/O (improves responsiveness for compressed swap).
- vm.watermark_boost_factor = 0 and vm.watermark_scale_factor tuned conservatively — avoid aggressive reclaim.

Compression algorithm
- Preferred: `zstd(level=3)` — best compression ratio/CPU trade-off on modern CPUs.
- Fallback: `lz4` — low CPU overhead, lower compression.
- Streams: set `streams` ≈ number of available CPUs (use `nproc --ignore=1` for small VMs).

Implementation options
- Preferred (distro-native): `zram-generator` (systemd generator) — early-boot, upstream, used by Fedora/Arch.
- Alternative: `xnai-zram.service` wrapper — acceptable when generator is not available.
- Important: zram swap does NOT support hibernation — document this limitation.

Observability (Prometheus)
- Health-check writes to node_exporter textfile collector directory (`/var/lib/node_exporter/textfile_collector/`).
- Recommended metric names (gauge):
  - `xnai_zram_compression_ratio` (float)
  - `xnai_zram_used_bytes` (gauge)
  - `xnai_zram_uncompressed_bytes_total` (gauge)
  - `xnai_zram_streams` (gauge)
  - `xnai_zram_algorithm{alg="zstd"}` (label)
- Ensure `node_exporter` can read the file (ownership/permissions).

Prometheus & Grafana quick integration
- Prometheus: add `monitoring/prometheus/phase-5a-scrape.yml` to your `prometheus.yml` under `scrape_configs:` and reload Prometheus. The snippet assumes `node_exporter` on `localhost:9100` — update targets to match your environment.
- Node exporter: ensure it is started with `--collector.textfile.directory=/var/lib/node_exporter/textfile_collector` so `xnai_zram.prom` is picked up.
- Grafana: import `monitoring/grafana/dashboards/xnai_zram_dashboard.json` (UID `xnai-zram-health`) into Grafana; point the dashboard at your Prometheus datasource.

Suggested alert thresholds (examples)
- Compression ratio < 1.2 → WARNING
- xnai_zram_used_bytes / total_physical_ram > 0.92 → CRITICAL

Files included in repo
- `monitoring/prometheus/phase-5a-scrape.yml` — Prometheus scrape snippet
- `monitoring/grafana/dashboards/xnai_zram_dashboard.json` — Grafana dashboard (importable)
- `scripts/zram-health-check.sh` — writes metrics to node_exporter textfile collector

Validation checklist
- Prometheus is scraping node_exporter and `xnai_zram_*` metrics appear in Prometheus (use `metrics` / Prometheus UI)
- Grafana dashboard imported and panels show data for the last 5–15 minutes
- Alerts (if configured) fire in staging when thresholds exceeded


Stress-testing guidance
- Use `stress-ng` with staged ramp and `--backoff`.
- Avoid `--pathological` and other options that can hang the host.
- Set safety thresholds: abort staged tests when CPU >85% or MEM >92% on production nodes.
- Validate compression ratio and peak memory under representative 5x load before promotion.

CI & testing recommendations
- Unit tests for `validate-phase-5a.py` and `zram-health-check.sh` (mock `/proc` and `zramctl`).
- Integration job: `phase-5a-stress-test.py --staging` on privileged ephemeral VM (manual gate required).
- Add `phase5a-rollback.sh` to scripts for automated safe rollback.

Operational runbook (quick)
- Activate:
  - Copy `TEMPLATE-sysctl-zram-tuning.conf` → `/etc/sysctl.d/99-xnai-zram-tuning.conf`
  - Copy `TEMPLATE-xnai-zram.service` → `/etc/systemd/system/`
  - sudo systemctl daemon-reload && sudo systemctl enable --now xnai-zram.service
  - sudo sysctl -p /etc/sysctl.d/99-xnai-zram-tuning.conf
- Verify:
  - `zramctl` shows `/dev/zram0` with algorithm `zstd` (or `lz4` fallback)
  - `swapon --show` includes `/dev/zram0`
  - `python3 scripts/validate-phase-5a.py` → all checks pass
- Rollback:
  - `sudo systemctl stop --now xnai-zram.service`
  - `sudo rm /etc/sysctl.d/99-xnai-zram-tuning.conf` (or restore backup)
  - `sudo swapoff /dev/zram0 && sudo zramctl --reset /dev/zram0`

References
- ArchWiki — zram: https://wiki.archlinux.org/title/Zram
- Fedora — SwapOnZRAM: https://fedoraproject.org/wiki/Changes/SwapOnZRAM
- zramctl manpage: https://man7.org/linux/man-pages/man8/zramctl.8.html
- stress-ng manpage: https://manpages.debian.org/stretch/stress-ng/stress-ng.1.en.html
- psutil (monitoring): https://psutil.readthedocs.io/en/latest/

Document version: 2026-02-12 — Research-backed, Tier‑4 template-ready
