---
title: Phase‑5A — zRAM, CPU‑affinity & Observability (recommended defaults)
tags: [phase5a, zram, numa, monitoring]
---

## Executive summary (3 bullets)

- Default production-safe zRAM for an 8-core / 16 GiB host: `zram0` size = 8 GiB, `algorithm=zstd(level=3)`, `streams=4`, sysctl: `vm.swappiness=180`, `vm.page-cluster=0`.
- Use `systemd` CPUAffinity for isolating cores `2-5` and apply `--cpuset-cpus="2-5"` for containers that require deterministic latency.
- Add Prometheus alerts for zRAM capacity, compression-ratio regressions, and isolated-core over-utilization; extend `zram-health-check.sh` with compression and swap I/O metrics.

---

## 1) zRAM — recommended production-safe defaults (8-core / 16 GiB)

Rationale: balance memory capacity, compression CPU cost, and predictable latency for model-serving workloads.

Recommended settings

- zram disk size: ram / 2 → 8 GiB
- compression algorithm: `zstd` (level=3) — best compression ratio/CPU tradeoff on modern CPUs
- streams: `4` (limit concurrency but allow multi-core compression)
- swap priority: `pri=100` (high priority for zram)
- sysctl tuning (place in `/etc/sysctl.d/99-xnai-zram.conf`):

  vm.swappiness = 180
  vm.page-cluster = 0
  vm.watermark_boost_factor = 0
  vm.watermark_scale_factor = 125

Commands (copy‑ready)

- Create + enable zram device (one-shot):

  modprobe zram
  zramctl --find --size 8G --algorithm zstd --streams 4 /dev/zram0
  mkswap -U clear /dev/zram0
  swapon --discard --priority 100 /dev/zram0

- Persistent via zram-generator (`/etc/systemd/zram-generator.conf`):

  [zram0]
  zram-size = ram / 2
  compression-algorithm = zstd(level=3)
  streams = 4

Sources: zramctl manpage (man8 zramctl), ArchWiki zram.

Tradeoffs & notes

- If CPU is constrained, use `lz4` as fallback (lower CPU cost, lower ratio).
- For systems <4 GiB RAM, reduce zram to `min(ram/2, 2G)` and validate with stress testing.

---

## 2) NUMA / CPU affinity — examples & verification

systemd service snippet (isolate cores 2–5 for `xnai-model.service`):

  [Unit]
  Description=XNAI model runtime
  After=network.target

  [Service]
  ExecStart=/usr/bin/xnai-model --config /etc/xnai/config.yml
  CPUAffinity=2-5
  CPUSchedulingPolicy=none
  CPUSchedulingPriority=0
  Restart=on-failure

  [Install]
  WantedBy=multi-user.target

Docker example (pin container to cores 2–5):

  docker run --cpuset-cpus="2-5" --memory="6g" --memory-swap="6g" myorg/xnai-model:stable

Verification commands

- Check pinned CPUs for a PID: `taskset -pc <pid>`
- Per-core utilization: `mpstat -P ALL 1 5` or `cat /proc/stat` and use Prometheus node_exporter metrics

---

## 3) Prometheus alert rules (copy‑ready)

1) High zRAM usage (page)

  - alert: Phase5A_HighZramUsage
    expr: xnai_zram_used_percent{device="zram0"} > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High zram usage on {{ $labels.instance }}"
      description: "zram0 used > 85% for 5m ({{ $value }}%). Check swap pressure and memory-hungry processes."

2) Compression ratio drop (investigate)

  - alert: Phase5A_ZramCompressionRatioLow
    expr: (xnai_zram_uncompressed_bytes{device="zram0"} / xnai_zram_compressed_bytes{device="zram0"}) < 1.8
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "zram compression ratio degraded on {{ $labels.instance }}"
      description: "Compression ratio below 1.8 for 10m; this may indicate incompressible workload or algorithm regressions."

3) Isolated core over-utilization (page)

  - alert: Phase5A_IsolatedCoreHighCpu
    expr: (
      avg by (instance) (1 - (rate(node_cpu_seconds_total{cpu=~"2|3|4|5",mode="idle"}[5m])))
    ) > 0.85
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High CPU usage on isolated cores 2-5 on {{ $labels.instance }}"
      description: "Average utilization >85% on isolated cores 2-5 for 5m. Consider shedding load, scaling, or moving non-latency workloads off these cores."

Alerting best practice: alert on symptoms (capacity & user impact), include runbook links and playbooks in annotations.

---

## 4) Metrics to add to `zram-health-check.sh` (recommended)

- xnai_zram_disksize_bytes (zramctl DISKSIZE)
- xnai_zram_uncompressed_bytes (DATA)
- xnai_zram_compressed_bytes (COMPR)
- xnai_zram_used_percent (DATA / DISKSIZE * 100)
- xnai_zram_compression_ratio (uncompressed / compressed)
- xnai_zram_mem_used_bytes (physical RAM used by zram)
- xnai_zram_streams_count
- xnai_zram_pages_in_total, xnai_zram_pages_out_total (if available via `/proc/vmstat`)
- xnai_zram_swap_in_bytes, xnai_zram_swap_out_bytes (node_vmstat pswpin/pswpout)
- xnai_zram_writeback_pending (if using writeback backing device)

Also surface node_exporter metrics for: `node_memory_Active_bytes`, `node_vmstat_pgpgin`, `node_vmstat_pgpgout`, and per-core `node_cpu_seconds_total` for isolated cores.

---

## 5) Verification & testing recommendations

- Add unit tests for `zram-health-check.sh` that assert the Prometheus textfile format and metric names.
- Add an Ansible play to apply zram-generator or `zramctl` in staging and run the Phase‑5A stress test script for 30 minutes.
- Automate checks: `zramctl -j` (json) parsing and thresholds validation before enabling swap.

---

## References

- zramctl(8) — man7.org: https://man7.org/linux/man-pages/man8/zramctl.8.html
- ArchWiki zram: https://wiki.archlinux.org/title/Zram
- Prometheus alerting best practices: https://prometheus.io/docs/practices/alerting/
- Docker cpuset docs: https://docs.docker.com/engine/reference/commandline/run/

