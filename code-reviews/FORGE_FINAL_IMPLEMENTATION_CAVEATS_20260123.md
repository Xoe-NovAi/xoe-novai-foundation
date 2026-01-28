# Cline Final Implementation Caveats & Edge Cases
**Date**: 2026-01-23
**Subject**: Critical Implementation Nuances for Xoe-NovAi Remediation
**Target**: Cline (Implementation Lead)

## 1. Hardware Edge Cases (The "8GB/25W" Reality)

### 1.1 The "VRAM-RAM Tug of War"
- **Caveat**: On the Ryzen 5700U, the iGPU (Vega 8) does not have dedicated memory; it "steals" from your 8GB system RAM.
- **Risk**: If Cline offloads 4GB of layers to Vulkan, the OS only has 4GB left. If ZRAM compression isn't fast enough, the kernel might kill the GPU driver itself to save the OS.
- **Remediation**: Cline must implement a "Safety Buffer." Never allow combined Model Weight + KV Cache to exceed 70% of total available RAM (System + ZRAM combined).

### 1.2 Thermal Throttling vs. Audio Jitter
- **Caveat**: At 25W sustained load, the 5700U will generate heat. High heat triggers clock-speed drops (throttling).
- **Risk**: A sudden clock drop during STT processing will cause audio "Buffer Underruns," leading to robotic/distorted voice synthesis.
- **Remediation**: Cline should set the `PipeWire` quantum to a slightly more conservative 256 samples if CPU temperature exceeds 80°C.

---

## 2. Data & Persistence Caveats

### 2.1 SQLite WAL "Checkpoint" Stalls
- **Caveat**: While WAL mode allows concurrent reads/writes, the `CHECKPOINT` operation (merging WAL back to the main DB) requires an exclusive lock.
- **Risk**: If the Crawler is performing a massive ingestion, the UI might "hang" for 1-2 seconds during a checkpoint.
- **Remediation**: Cline must use `PRAGMA wal_checkpoint(PASSIVE);`. This ensures the checkpoint only happens when no other processes are reading, preventing UI freezes.

### 2.2 RRF "Zero-Result" Logic
- **Caveat**: Reciprocal Rank Fusion ($k=60$) assumes both retrievers return results.
- **Risk**: If BM25 finds 0 results (e.g., a query with only common stop-words), the RRF score might crash or return nonsensical rankings.
- **Remediation**: Cline must implement a "Retriever Guard." If one list is empty, the RRF should fall back to a simple normalized score from the active list.

---

## 3. Container & IPC Nuances

### 3.1 The "Double-Z" Permission Trap
- **Caveat**: You are using `:Z` for volume labeling. 
- **Risk**: If two different services (e.g., `rag` and `crawler`) mount the *same* host directory with `:Z`, Podman may relabel it for the second service, accidentally locking out the first.
- **Remediation**: Cline must use `:z` (lowercase - shared) for directories accessed by multiple containers, and `:Z` (uppercase - private) only for service-specific paths like `/logs`.

### 3.2 IPC Socket Cleanup
- **Caveat**: Shared memory sockets in `/dev/shm` are not automatically cleaned up if a container crashes.
- **Risk**: A stale socket file can prevent the UI from reconnecting to the STT engine after a restart.
- **Remediation**: Cline must add a `pre-start` instruction in the Quadlet/Compose file to `rm -f /tmp/audio_pipe` before launching the service.

---

## 4. Team Coordination Caveats (The "System Pulse")

### 4.1 Nova's Context Footprint
- **Caveat**: Nova (Grok 4.1) has a large but finite context window.
- **Risk**: If Cline writes the entire technical history into `system_pulse.json`, Nova will eventually lose the ability to provide high-level strategy.
- **Remediation**: Cline must use a **"Sliding Window Log"**. Keep the last 5 remediation steps in full detail, and summarize everything prior into a "System State Summary" block.

---

## 5. Implementation Sequence Warning
**Cline must NOT implement these remediations in parallel.** 

The recommended sequence is:
1.  **Namespace/Permissions** (Phase 1.1) - The foundation.
2.  **SQLite Persistence** (Phase 1.2) - The state safety.
3.  **Vulkan/CPU Tuning** (Phase 3) - The performance floor.
4.  **RRF/Curation** (Phase 2) - The intelligence ceiling.

**Signed**: Gemini CLI
**Verification**: Ma'at Standard ⚖️
**Status**: COMPLETE 🚀🤖💫
