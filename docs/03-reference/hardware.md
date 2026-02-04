# Hardware Mastery: Ryzen 5700U & Vulkan 1.4
**Status**: Elite Hardened
**Platform**: AMD Ryzen 7 5700U (Zen 2 Architecture)
**Last Updated**: January 27, 2026

## 🔱 The Vision: Adaptive Hardware Orchestration
While the current Foundation Stack is optimized for the AMD Ryzen 5700U (Zen 2) on Linux, our vision is to build a **Multi-OS, Multi-Hardware Ecosystem**.

1.  **OS Expansion**: We are expanding the Foundation Stack to support Windows (via WSL2/Native) and macOS (Apple Silicon).
2.  **Hardware Library**: We are building a comprehensive library of preset optimizations for different processors (Intel, AMD, ARM) and GPUs (NVIDIA, AMD, Intel Arc).
3.  **Dynamic Optimization Tool (Roadmap)**: Our goal is a tool that automatically detects your hardware and applies extreme, fine-grained tuning—mirroring the manual optimizations we've perfected for the 5700U.

---

## 1. Thermal & Power (25W cTDP)
The Ryzen 5700U is optimized for a sustained 25W cTDP. Xoe-NovAi leverages the `ryzenadj` pattern to ensure peak performance during inference without thermal throttling.

- **Governor**: Performance mode during active RAG queries.
- **EPP**: Set to `performance` for sub-200ms TTFT (Time to First Token).

## 2. Memory Orchestration (16GB+ Foundation)
While the stack is optimized for low RAM, a 16GB physical baseline ensures stability for the full 7-service Foundation.

- **ZRAM**: Recommended `vm.swappiness=180` for 8GB systems; standard swapping for 16GB+.
- **Watchdog**: The 400MB Soft-Stop rule prevents "Compression Death Loops" during intensive ingestion.

---

## 5. Hardware Verification SOP
To ensure your hardware is performing to Foundation standards:
1.  **Doctor Check**: `make doctor` (Verifies Vulkan extensions and CPU governor).
2.  **Mesa Audit**: `glxinfo | grep Mesa` (Should show v24.x or v25.x).
3.  **Core Pinning Test**: `scripts/verify_pinning.py` (Checks affinity for STT/TTS services).

## 3. Vulkan 1.4 Acceleration
Xoe-NovAi utilizes the Vega 8 iGPU through Mesa 25.3.

- **RADV GPL**: Graphics Pipeline Library enabled to eliminate first-query stutter.
- **Extensions**: Scalar Block Layouts and Push Descriptors reduce memory bandwidth bottlenecks.
- **VRAM Cap**: 70% combined safety buffer between System and iGPU memory.

## 4. CPU Thread Pinning
- **Cores 0-5**: Dedicated to LLM Generation (Matrix Multiplications).
- **Cores 6-7**: Dedicated to UI, STT (Whisper), and TTS (Piper).
- **Affinity**: `OMP_PROC_BIND=spread` for maximum cache utilization.
