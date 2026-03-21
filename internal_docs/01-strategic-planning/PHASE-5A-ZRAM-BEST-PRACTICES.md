# PHASE 5A — zRAM Best Practices (research-backed)

Purpose
- Concise, actionable best-practices for deploying and operating zRAM as swap in XNAi Foundation Phase 5A.
- Source: ArchWiki, Fedora SwapOnZRAM, util-linux zramctl manpage, stress-ng, psutil.

Summary (TL;DR)
- Prefer `zstd` compression where available; fall back to `lz4` when `zstd` is not exposed by the kernel.
- Start with conservative sizing: `min(ram / 2, 4GiB)` and only increase after staging verification.
- Use `vm.swappiness = 180` and `vm.page-cluster = 0` for responsive in‑RAM swap behavior.
- Expose health metrics to Prometheus via node_exporter textfile collector (see `scripts/zram-health-check.sh`).

## Production Standard: Multi-Tiered zRAM
To maximize responsiveness while maintaining high capacity, the Xoe-NovAi Foundation uses a **Multi-Tiered zRAM** configuration:

1.  **Tier 1 (Latency-Sensitive)**: 
    - **Device**: `/dev/zram0`
    - **Size**: 2 GiB
    - **Algorithm**: `lz4` (Fastest, low CPU overhead)
    - **Priority**: 100 (Highest)
2.  **Tier 2 (Bulk-Storage)**:
    - **Device**: `/dev/zram1`
    - **Size**: 10 GiB
    - **Algorithm**: `zstd` (High compression, efficient storage)
    - **Priority**: 50 (Lower)

### Sizing Heuristics (Total Swap Capacity)
- **Standard (8GB physical)**: 12GB Total (2GB lz4 + 10GB zstd)
- **High-End (16GB+ physical)**: 16GB Total (4GB lz4 + 12GB zstd)

Kernel tuning (ML & Ryzen 7 5700U Optimized)
- **vm.swappiness = 180**: High value to prioritize fast zRAM swap over disk. Essential for ML workloads exceeding 8GB RAM.
- **vm.page-cluster = 0**: Disables large clustered page I/O, reducing latency for single-page compressed swap operations.
- **vm.vfs_cache_pressure = 50**: Encourages the kernel to retain filesystem metadata caches longer, improving responsiveness during high-context (1M token) file ingestion.
- **vm.dirty_ratio = 10** / **vm.dirty_background_ratio = 5**: Prevents massive write-back spikes that could stall the Zen 2 CPU during heavy model output.

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

How it connects (detailed)
- zRAM runs in the host kernel (not in containers). `zramctl` inspects `/sys/block/zram*` and reports device statistics; `zramctl` output is consumed by `scripts/zram-health-check.sh` running on the host.
- The health-check writes `xnai_zram_*.prom` into `/var/lib/node_exporter/textfile_collector/`; `node_exporter` exposes the combined metrics at `http://<host>:9100/metrics`.
- Prometheus scrapes `node_exporter` (not Caddy) and stores `xnai_zram_*` time series; Grafana queries Prometheus for dashboards and alerts.

CPU affinity & core isolation — advanced optimization (recommended for performance hosts)
- Why: zRAM compression is CPU-bound under heavy swap activity; isolating latency‑sensitive workloads (model inference, I/O threads) from background kernel/maintenance work (compression, scrubbing, health checks) reduces jitter and improves tail latency.

- Host-level recommendations
  - Reserve a small CPU set for latency-sensitive services (model-serving, inference engines) using kernel bootline `isolcpus=` or systemd `CPUAffinity`/`CPUShares`.
  - Place non-critical background tasks (zram compression workers, health-checks, batch jobs) on non-isolated cores.
  - Use `irqbalance` + manual IRQ pinning for NVMe/PCIe device interrupts to keep I/O off isolated cores.

- Systemd examples (production-ready patterns)
  - Pin a critical service to cores 2-5:
    - `CPUAffinity=2 3 4 5`
    - `CPUQuota=90%` (optional)
  - Keep kernel/compression work off the isolated set by assigning zram-related userspace helpers and health-checks to other cores (see `TEMPLATE-xnai-zram-health.service` examples).

- Container / Podman pinning
  - For rootful Podman/Docker: `--cpuset-cpus="0,1"` on containers that must stay on system cores.
  - For rootless Podman: use systemd slice + `CPUAffinity` or `podman run --cgroup-manager=cgroupfs --cpuset-cpus=...` depending on runner.

- Kernel tuning knobs to pair with isolation
  - Kernel boot: `isolcpus=2-3 nohz_full=2-3 rcu_nocbs=2-3`
  - tuned profile: `tuned-adm profile throughput-performance` (or custom profile)

- Tools for verification and benchmarking
  - Monitor `node_cpu_seconds_total`, `node_load1`, `process_cpu_seconds_total` (Prometheus) and `top -H`, `htop -C`, `taskset -p` on the host.
  - Use `cset shield` or `numactl --cpunodebind` for advanced isolation experiments.

- zRAM-specific notes
  - `zram.streams` should be tuned for the number of worker CPUs *outside* the isolated set (so compression work doesn't occupy reserved cores).
  - On NUMA systems prefer tying compression streams to local CPUs to avoid remote memory traffic.

- Prometheus & Grafana additions (suggested)
  - Add panels for `node_cpu_seconds_total` (per core), `node_irq` by CPU, and `process_cpu_seconds_total` for pinned services.
  - Create alerts when isolated-core steal/usage increases unexpectedly (indicates cross-talk).

- Safety
  - Always test isolation changes in staging with representative load; isolcpus and nohz_full affect scheduler behavior and can make debugging more complex.

Quick checklist (CPU affinity)
- [ ] Decide reserved core set (e.g., cores 2-5) and document mapping
- [ ] Add `CPUAffinity` to systemd units for latency-sensitive services
- [ ] Pin containers with `--cpuset-cpus` where applicable
- [ ] Tune `zram.streams` to avoid isolated set
- [ ] Add Grafana panels for per-core CPU and IRQs

Mermaid architecture (host-centric)

Mermaid architecture (host-centric)
```mermaid
flowchart TD
  subgraph Host Kernel
    K[zram driver (/dev/zram0)]
  end
  subgraph Host Processes
    Z[zramctl]
    H[zram-health-check.sh]
    TF[/var/lib/node_exporter/textfile_collector/xnai_zram.prom]
    NE[node_exporter:9100]
  end
  Prom[Prometheus:9090]
  Graf[Grafana]
  Caddy[Caddy (app proxy):8000]
  App[RAG API & Services]

  K --> Z --> H
  H --> TF --> NE --> Prom --> Graf
  App --> Caddy

  classDef hostKernel fill:#f0f8ff,stroke:#0366d6
  class K hostKernel
```

Notes
- zRAM MUST run at host level — do not attempt to create or manage zram devices inside rootless Podman containers. Containers cannot modify kernel block devices for the host safely.
- Prometheus scrapes node_exporter directly (port 9100). Caddy (port 8000) is unrelated to metrics collection and should NOT be used as a proxy for Prometheus scrapes.

Files provided in repo to automate the flow
- `scripts/zram-health-check.sh` — writes Prometheus-format metrics to node_exporter textfile collector
- `TEMPLATE-xnai-zram-health.service` + `TEMPLATE-xnai-zram-health.timer` — systemd unit/timer templates to schedule the health check
- `monitoring/prometheus/phase-5a-scrape.yml` — Prometheus scrape snippet
- `monitoring/grafana/provisioning/...` — Grafana datasource & dashboard provisioning templates

Validation checklist
- Node exporter shows `xnai_zram_*` metrics at `http://localhost:9100/metrics` after running `scripts/zram-health-check.sh`.
- Prometheus 'Targets' page shows `node_exporter` UP and metrics available.
- Grafana panels display `xnai_zram_*` series after Prometheus scrapes.
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
