---
version: 1.0.0
tags: [ryzen, hardening, infrastructure, zen2, optimization, podman, voice]
date: 2026-01-29
ma_at_mappings: [7: Truth in evolution, 41: Advance through own abilities]
expert_dataset_name: Ryzen Hardening Expert
expertise_focus: Zen 2 hardware tuning, rootless Podman hardening, and sovereign AI infrastructure patterns.
community_contrib_ready: true
---

# Ryzen Hardening Expert (v1.0.0)

## Overview
This dataset focuses on hardware-level tuning and infrastructure hardening for the AMD Ryzen Zen 2 architecture, specifically the 5700U APU. It provides elite patterns for maximizing AI inference performance on mid-grade, sovereign hardware.

## System Specifications (Ground Baseline)
- **CPU**: AMD Ryzen 7 5700U (8 cores, 16 threads, Zen 2).
- **RAM**: 8GB DDR4-3200 (Pinned baseline).
- **GPU**: Radeon Vega 8 iGPU (Vulkan 1.2 support).
- **OS**: Linux (Optimized for Podman rootless).

## Hardware Optimization Patterns

### 1. OpenBLAS Steering
- **Requirement**: `OPENBLAS_CORETYPE=ZEN`
- **Rationale**: Forces the OpenBLAS library to use Zen-optimized kernels, bypassing generic x86_64 fallbacks. Essential for `numpy` and `scipy` performance in RAG services.

### 2. CPU Governor Control
- **Pattern**: Performance Mode.
- **Command**: `echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
- **Impact**: Eliminates frequency scaling latency during bursty AI inference tasks.

### 3. Memory Management (Huge Pages)
- **Pattern**: Static Huge Page allocation.
- **Command**: `echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages`
- **Win**: Reduces TLB misses for large model weights in memory.

## 🛠️ Podman & Container Hardening

### 1. Rootless Permission Pattern (:U Flag)
- **Problem**: Host-level UID collisions and manual `chown` brittleness.
- **The Pattern**: Use the `:U` volume flag for "Automatic Ownership Mapping."
- **Syntax**: `- ./data/redis:/data:Z,U`
- **Win**: Zero-sudo portability and safe UID namespace mapping across distributions.

### 2. BuildKit Cache Hardlining
- **Problem**: Hardlink fallback errors during `uv pip` installs in rootless mode.
- **The Pattern**: Standardize cache mounts to `uid=0,gid=0`.
- **Syntax**: `RUN --mount=type=cache,id=xnai-...,target=...,uid=0,gid=0`
- **Win**: 2x - 5x faster cache re-use through atomic filesystem hardlinks.

## 🎙️ Voice Runtime & Assets

### 1. Model Requirements
- **STT**: `distil-large-v3` (Faster Whisper) in CTranslate2 format.
- **TTS**: `en_US-john-medium.onnx` (Piper).
- **VAD**: `silero_vad.onnx` (Neural voice activity detection).

### 2. Standardized Audio Specs
- **Sample Rate**: 16,000 Hz.
- **Bit Depth**: 16-bit PCM Mono.
- **Barge-in Threshold**: 200ms consecutive speech frames.

## Ma'at Alignment
- **Ideal 7 (Truth)**: Accurate hardware profiles ensure deterministic performance.
- **Ideal 41 (Abilities)**: Advancing through own abilities by mastering local hardware.