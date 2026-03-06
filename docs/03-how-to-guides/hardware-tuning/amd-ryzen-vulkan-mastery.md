# AMD Ryzen & Vulkan Mastery Manual
**Status**: Elite Hardened
**Target Hardware**: AMD Ryzen 7 5700U (8C/16T, Vega 8 iGPU, Zen 2)
**Optimization Goal**: 35+ tok/s Inference & sub-150ms Voice Latency

## 1. Memory Orchestration (The 8GB Constraint)
On the Ryzen 5700U, the iGPU (Vega 8) shares the 8GB system RAM. Mismanagement of this shared pool is the primary cause of system instability.

### 1.1 The "70% Safety Buffer" (VRAM-RAM Tug-of-War)
- **The Rule**: Never allow the combined size of the Model Weights + KV Cache to exceed **70% of total available RAM** (System RAM + ZRAM).
- **Enforcement**: If peak memory exceeds 5.6GB (70% of 8GB), the kernel may kill the GPU driver to protect the OS. 
- **Remediation**: Use `Q4_K_S` or `Q5_K_M` quantization to stay within this envelope.

### 1.2 ZRAM Strategy
To maximize the 8GB pool, Xoe-NovAi leverages ZSTD-compressed ZRAM.
- **Swappiness**: Force `vm.swappiness=180`.
- **Page Cluster**: Set `vm.page-cluster=0` to reduce latency during ZRAM decompression.

---

## 2. Vulkan 1.4 Acceleration (Mesa 25.3+)
Xoe-NovAi utilizes the Vulkan compute backend for 25-55% performance gains over CPU-only inference.

### 2.1 Elite Build Flags
When building the RAG API, ensure these Vulkan-specific flags are enabled:
- **RADV GPL**: Enable `RADV_PERFTEST=gpl` to eliminate shader compilation stutter during the first interaction.
- **Scalar Block Layouts**: Reduces memory bandwidth overhead on integrated GPUs.
- **8-bit KV Cache**: Reduces VRAM footprint by 25% with negligible quality loss.

### 2.2 Startup Warmup Probe
Vulkan drivers require a "warmup" to stabilize shader caches. 
- **The SOP**: On startup, the system executes a **64x64 matrix multiplication probe**. This ensures that the first user query responds in <500ms rather than 10-15s.

---

## 3. Thermal & Power Orchestration (25W cTDP)
The Ryzen 5700U is a 25W sustained TDP chip. High thermal loads trigger clock-speed drops that impact audio quality.

### 3.1 Thermal-Aware Audio Quantum
- **The Risk**: Clock-speed drops during STT/TTS cause "robotic" audio jitter.
- **The Logic**: If CPU temperature exceeds **80°C**, the `PipeWire` quantum is automatically shifted to **256 samples** (conservative) to prevent buffer underruns.

### 3.2 CPU Core Masking
To prevent the LLM from starving the Voice UI of cycles:
- **Cores 0-5**: Dedicated to Matrix Multiplications (Inference).
- **Cores 6-7**: Reserved for UI, STT, and TTS orchestration.

---

## 4. Troubleshooting & Verification
- **Validate Vulkan**: Run `make doctor` or `vulkaninfo --summary`. Look for `AMD Radeon Graphics (RADV RENOIR)`.
- **Check AGESA**: Ensure host BIOS is updated to **AGESA 1.2.0.8+** for GPU stability.
- **Monitor Memory**: Use `watch -n 1 free -h` during inference to ensure usage stays under the 70% threshold.
