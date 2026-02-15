# NUMA-aware pinning & zRAM (advanced)

Purpose
- Provide NUMA-aware CPU/memory pinning examples and tuned profile advice for Phase-5A hosts.

When to use
- Large multi-socket servers where memory locality impacts compression and swap performance.

Key principles
- Keep zRAM compression streams local to the NUMA node where the bulk of compressed memory resides.
- Reserve inference/model-serving CPUs on a local NUMA node when low latency is required.
- Avoid cross-node memory traffic for compression workers to reduce latency and memory bandwidth contention.

Practical examples
- Identify nodes & CPUs:
  - lscpu -e | grep "NUMA" # or `numactl --hardware`
- Bind service to node 0 CPUs:
  - systemd: `CPUAffinity=0-7` for node0 (adjust ranges)
  - podman: `--cpuset-cpus=0-7 --cpuset-mems=0`

zRAM tuning (NUMA)
- Set `zram.streams` to worker count on the same NUMA node.
- Use `numactl --interleave=0` only for workloads that need balanced memory.

Tuned profile example (tuned)
- Create `/etc/tuned/phase5a-performance-numa/profile.conf` with custom settings to control IRQ affinity and scheduler parameters.

Verification
- Use `numastat`, `perf`, and Prometheus `node_memory_*` + `node_cpu_seconds_total` split by core to verify locality.

Caveats
- NUMA pinning increases operational complexity; test thoroughly in staging.
