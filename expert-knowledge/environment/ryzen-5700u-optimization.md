# Expert Knowledge: Ryzen 7 5700U Tuning & Optimization
## Xoe-NovAi Hardware Mastery

### 1. Host Specifications
- **CPU**: AMD Ryzen 7 5700U (Zen 2, 8C/16T).
- **GPU**: Radeon Vega 8 (iGPU).
- **RAM**: 6.6GB Available (strictly limited).

### 2. Memory Management (The 6.6GB Barrier)
- **zRAM**: Use the multi-tiered `lz4` + `zstd` configuration provided in Phase 5A.
- **Swappiness**: `vm.swappiness = 180` for aggressive swap-to-zram.
- **OOM Prevention**: The `DegradationTierManager` must trigger Tier 3 (Cache-only) when host memory drops below 500MB.

### 3. Model Offloading Protocol
When switching models (e.g., STT Base → STT Tiny):
1.  `del stt_model`
2.  `gc.collect()`
3.  `await asyncio.sleep(0.1)` (allows the event loop to yield to garbage collection).

### 4. Vega iGPU Optimization
- **Wavefronts**: Use `VP_VULKANINFO` settings to target 64-wide wavefronts.
- **Memory Mapping**: Set `PRAGMA mmap_size=268435456` in SQLite (IAM DB) to utilize 256MB of shared memory.

### 5. Podman Performance
- **Rootless**: Always run containers in rootless mode (UID 1001).
- **Volumes**: Use `z` or `Z` flags for SELinux relabeling to prevent permission bottlenecks.
