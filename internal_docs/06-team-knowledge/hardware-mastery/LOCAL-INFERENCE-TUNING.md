---
last_updated: 2026-02-14
status: draft
persona_focus: Grok
agent_impact: high
related_phases: Phase-5
---

# Local Inference & Hardware Mastery: Ryzen 7 5700U (Zen 2 / Vega)

To achieve sovereignty, the Xoe-NovAi Foundation optimizes all local AI tools for the Human Director's specific hardware: **AMD Ryzen 7 5700U (Zen 2 Architecture / Vega iGPU)**.

## ⚙️ The Local Pipeline (CPU + iGPU)
Our strategy maximizes the Lucienne-based SOC:
1.  **CPU (Zen 2)**: Orchestrates the OS, filesystem, and CLI tools. Optimized for 8 cores / 16 threads.
2.  **iGPU (Vega)**: Handles token generation and multimodal processing via Vulkan.

## 🛠️ Optimization Patterns (The Vega Correction)
### 1. Vulkan Native Execution
Compile all local inference backends (e.g., `llama.cpp`) with the Vulkan backend. 
- **Important**: The Ryzen 7 5700U uses the **Vega 8 (GCN 5.1)** iGPU, not RDNA. 
- **Wavefront Size**: Vega uses **64-wide wavefronts**. Current RDNA-optimized code (32-wide) should be adjusted for Vega to maximize CU occupancy.
- **Mesa Support**: Ensure Mesa 25.3+ is used for stable Vulkan 1.3/1.4 support on GCN5 hardware.

### 2. Model Quantization (GGUF Primary)
Prioritize **GGUF** formats. 
- **Vega Limitations**: Vega lacks the hardware-accelerated matrix multiplication (WMMA) found in newer RDNA3 chips. Expect lower tokens-per-second than RDNA-based systems, but still 2-3x faster than pure CPU.
- **AWQ**: ⚠️ **DISABLED / UNTESTED**. AWQ is optimized for Tensor cores (NVIDIA) or newer AMD architectures. It is considered unstable on Vega.

### 3. zRAM & Kernel Tuning
Since the system operates with 8GB physical RAM and 12GB zRAM, aggressive swapping to compressed RAM is required to prevent OOM during large context (1M token) processing.
- **vm.swappiness = 180**: High value to prioritize fast zRAM swap over disk.
- **vm.page-cluster = 0**: Minimizes latency for compressed swap operations.
- **Compression**: `zstd` algorithm for the best balance of ratio and CPU usage.

## 🚀 Performance Benchmarks
- **Target Latency**: <300ms for voice-to-text (Piper/Whisper).
- **Target Throughput**: >15 tokens/sec for local 7B GGUF models on Vega.
