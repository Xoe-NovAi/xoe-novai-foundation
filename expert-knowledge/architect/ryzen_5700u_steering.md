# Ryzen 5700U (Zen 2) Core Steering Standard

**Domain**: Architect / Hardware
**Date**: January 26, 2026
**Expert**: Gemini CLI (Sovereign Agent)

## Hardware Profile: AMD Ryzen 7 5700U
*   **Architecture**: Zen 2 (Lucienne).
*   **Cores/Threads**: 8 physical cores, 16 logical threads (SMT).
*   **Performance Bottleneck**: SMT resource contention and thermal throttling during long-running AI inference (LLM/STT).

## The Implementation: Physical-First Core Steering
To maximize L3 cache efficiency and minimize context-switch latency, high-compute AI workloads should be pinned to physical cores only.

1.  **Core Mapping**: 
    *   **Physical Cores (Even)**: `0, 2, 4, 6, 8, 10, 12, 14`
    *   **SMT Threads (Odd)**: `1, 3, 5, 7, 9, 11, 13, 15`
2.  **Configuration**: Use the `cpuset` directive in `docker-compose.yml`.
    ```yaml
    services:
      rag:
        cpuset: "0,2,4,6,8,10,12,14" # AI Inference
      ui:
        cpuset: "1,3,5,7,9,11,13,15" # Web Server / UI
    ```
3.  **Environment Variables**:
    *   `OPENBLAS_CORETYPE=ZEN`: Forces OpenBLAS to use Zen-optimized kernels.
    *   `OMP_NUM_THREADS=1`: Prevents OpenMP from creating too many sub-threads which leads to cache thrashing.

## Benefits
*   **Latency**: ~15-20% reduction in token-to-first-byte (TTFT).
*   **Stability**: Prevents "Robotic" audio in voice interfaces caused by scheduler jitter.
*   **Thermals**: More even heat distribution across the CCX (Core Complex).

## Verification
Use `top` or `htop` on the host. Press `1` to see individual core utilization. Compute tasks should only light up even-numbered cores.
