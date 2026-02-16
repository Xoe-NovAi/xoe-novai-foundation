# RESEARCH-S3: Advanced zRAM Tiering & Optimization
**Version**: 1.0.0 | **Status**: PROPOSAL | **Topic**: Multi-Device zRAM & Ryzen/iGPU Tuning

## Executive Summary
This research explores the feasibility and benefits of implementing multiple zRAM devices with tiered priorities and different compression algorithms. This is particularly relevant for the Xoe-NovAi Foundation stack running on Ryzen hardware with integrated Graphics (iGPU), where memory contention between the CPU and GPU is a primary performance bottleneck.

---

## 🔬 Multi-Device zRAM Architecture

### 1. The Tiered Swap Concept
Linux allows multiple swap devices with different priorities (`swapon -p`). By creating multiple zRAM devices, we can optimize for both latency and capacity.

| Device | Algorithm | Priority | Target Usage |
|--------|-----------|----------|--------------|
| `/dev/zram0` | `lz4` | 100 | **High Frequency**: Small, fast pages, system buffers, interactive UI. |
| `/dev/zram1` | `zstd` | 50 | **Bulk Capacity**: Model weights, inactive background processes, large context chunks. |

### 2. Ryzen & iGPU Specific Optimization
The Ryzen iGPU (Radeon) shares system RAM via the UMA (Uniform Memory Access) buffer.
-   **The Contention**: When the iGPU claims RAM, the CPU has less physical headroom, forcing earlier swapping.
-   **The Solution**: Use a high-priority `lz4` zRAM device to minimize the "stutter" felt when the iGPU and CPU compete for bandwidth. The `lz4` algorithm has lower CPU overhead, leaving more cycles for iGPU drawing/inference.

---

## 🏗️ Experimental Project: "Project Multi-ZRAM"

### Goal
Implement a dual-device zRAM setup and measure the impact on RAG API latency under heavy load.

### Proposed Configuration
-   **ZRAM_FAST**: 1GiB, `lz4`, Priority 100.
-   **ZRAM_BULK**: 4GiB (or 50% of remaining), `zstd`, Priority 50.

### Implementation Script (PoC)
```bash
# Fast Tier
zramctl --find --size 1G --algorithm lz4
mkswap /dev/zram0
swapon -p 100 /dev/zram0

# Bulk Tier
zramctl --find --size 4G --algorithm zstd
mkswap /dev/zram1
swapon -p 50 /dev/zram1
```

---

## ⚖️ Best Practices & Pitfalls

### Pitfalls
-   **CPU Overhead**: Over-compressing with multiple `zstd` streams can starve the CPU during inference.
-   **Memory Overhead**: Each zRAM device has a small management overhead in the kernel.
-   **Context Drift**: If the fast tier is too small, the system constantly swaps between tiers, increasing latency.

### Best Practices
-   **Stream Alignment**: Set `max_comp_streams` to match the number of physical cores (not threads) to avoid cache thrashing.
-   **Swappiness Tuning**: Use `vm.swappiness = 180` to ensure the system utilizes the tiers before touching physical disk (if any).
-   **Page Cluster**: Use `vm.page-cluster = 0` to reduce I/O latency for single-page reads.

---

## 🚀 Future Roadmap: Dynamic Steering
Develop a "Sovereign Governor" that monitors iGPU usage and dynamically adjusts zRAM priorities or sizes to prevent system locks.

---

**Next Steps**: Implement the robust initialization script and verify the single-device baseline before moving to Multi-ZRAM.
