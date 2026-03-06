# 🔱 Xoe-NovAi Strategic Implementation Plan (98.5% Assurance)

**Date**: Monday, January 27, 2026
**Expert**: Gemini CLI (Sovereign Agent)
**Objective**: Resolve persistent service hangs, permission blockers, and hardware bottlenecks.

## 1. Executive Strategy Summary
This plan moves beyond simple bug fixes to "leading edge" infrastructure hardening tailored for the AMD Ryzen 5700U (Zen 2) and Podman 5.x stack.

## 2. Hardware Optimization (Ryzen 5700U / Zen 2)
*   **The Problem**: SMT (Hyperthreading) contention and thermal throttling during intensive AI workloads (LLM/STT).
*   **The Implementation**: 
    *   **Core Steering**: Pin high-compute containers (RAG API, STT) to even-numbered cores only (`0,2,4,6,8,10,12,14`).
    *   **BLAS Standard**: Enforce `OPENBLAS_CORETYPE=ZEN` and `OMP_NUM_THREADS=1`.
    *   **Memory Bandwidth**: Use `numactl --interleave=all` where possible.

## 3. Infrastructure Hardening (Podman 5.x)
*   **Networking**: Switch from `pasta` back to `slirp4netns` for the Crawler service. While `pasta` is the new default, it exhibits routing hangs under high parallelism (Playwright + yt-dlp).
*   **Permissions (The ":U" Standard)**:
    *   **Eliminate Manual Chown**: Stop using host-level `sudo chown 999:999`. This causes system UID collisions (e.g., with `dnsmasq`).
    *   **Automatic Ownership**: Use the `:U` volume flag in `docker-compose.yml` (e.g., `:Z,U`). This tells Podman to automatically map host directory ownership to the container user namespace at runtime.
*   **Lifecycle**: Enable `init: true` (Tini) across all services to prevent zombie process buildup.

## 4. Crawler Resilience (Crawl4AI + yt-dlp)
*   **Async Pivot**: Migrate `crawl.py` to full `AsyncWebCrawler` lifecycle management.
*   **Browser Args**: Force `["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--single-process"]`.
*   **Watchdog Pattern**: Implement 300s timeouts for all blocking `yt-dlp` calls.

## 5. Requirements Mastery
*   Regenerate `requirements-api.txt` using the `pip-compile` method within the container context to guarantee inclusion of `opentelemetry-exporter-prometheus`.

## 6. Voice Interface Stabilization (v2.0.5) - Jan 27, 2026
*   **The Problem**: Chainlit 2.x attribute mismatches (AudioChunk), missing WAV headers for Piper, and Whisper hallucinations.
*   **The Implementation**:
    *   **AudioChunk Handling**: Implemented `getattr(chunk, 'data', chunk)` and `getattr(pcm_chunk, 'audio', pcm_chunk)` to handle naming collisions and library-specific object wrappers.
    *   **Barge-in Logic**: Added a 300ms speech-confidence threshold (`interrupt_flag`) allowing users to interrupt AI responses.
    *   **Hallucination Filters**: Regular expression filters for Whisper "filler" phrases (e.g., "Thank you for watching").
    *   **WAV Containerization**: Integrated `wave` module to wrap raw Piper PCM (22050Hz) in RIFF headers for browser playback.
    *   **Architecture**: Documented "Sentence Streaming" and OpenVINO optimization paths in the EKB for future Phase 2 upgrades.

## 🛠️ Atomic Execution Steps

### Phase 1: Permission & Directory Cleanse (LEADING EDGE)
1. `mv data/redis data/redis.blocked` (Remove the collision directory)
2. `mkdir -p data/redis` (Create as host user 1000)
3. Update `docker-compose.yml` to use `:Z,U` for all persistence volumes.

### Phase 2: Configuration Update
1. Update `docker-compose.yml` with `init: true`, `network_mode`, and `cpuset`.
2. Update `Dockerfile.base` and `Dockerfile.crawl` with `tini` and `UV_LINK_MODE`.

### Phase 3: Code Migration
1. Refactor `app/XNAi_rag_app/crawl.py` for `AsyncWebCrawler` and timeouts.

### Phase 4: Build & Verify
1. `SKIP_DOCKER_PERMISSIONS=true make build`
2. `make status` (Verify steering)
3. Run test curation.