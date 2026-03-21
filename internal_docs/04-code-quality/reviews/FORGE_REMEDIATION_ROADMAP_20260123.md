# Cline: Remediation Implementation Roadmap
**Version**: 1.0 (Autonomous Execution)
**Scope**: 13 Tactical Tasks
**Reference**: Cross-referenced with `FORGE_FINAL_IMPLEMENTATION_CAVEATS_20260123.md`

## 📋 Roadmap Overview
Cline should execute these tasks sequentially. Each task includes a **Verification** step. If verification passes, Cline moves to the next task autonomously.

---

### Phase 1: Security & Foundation (The Justice)

#### Task 1: Rootless Namespace Hardening
- **Objective**: Standardize volume ownership via `podman unshare`.
- **Action**: Modify `scripts/setup_permissions.sh`. Use `podman unshare chown -R 1001:1001` for `/library`, `/knowledge`, `/data`.
- **Caveat Ref**: 3.1 (Use `:z` for shared, `:Z` for private).
- **Verification**: `podman exec xnai_rag_api touch /library/forge_found.txt`

#### Task 2: Redis UID Standardization
- **Objective**: Align Redis with the 1001 standard.
- **Action**: Update `podman-compose.yml`. Change Redis user to `${APP_UID}:${APP_GID}`.
- **Verification**: `podman logs xnai_redis` (confirm no permission errors on start).

---

### Phase 2: Data Persistence (The Truth)

#### Task 3: SQLite IAM Refactor
- **Objective**: Move `iam_service.py` to persistent SQLite.
- **Action**: Use `sqlite-utils`. Implement `PRAGMA journal_mode=WAL;`.
- **Verification**: Create a user, restart the service, verify user still exists.

#### Task 4: Background Checkpointer
- **Objective**: Prevent WAL file bloat.
- **Action**: Add a background thread to `PersistentIAM` calling `wal_checkpoint(PASSIVE)` every 5 mins.
- **Caveat Ref**: 2.1 (Passive mode avoids UI hanging).
- **Verification**: Monitor `data/iam.db-wal` size during active login tests.

---

### Phase 3: Friction & Thrashing Protection (The Balance)

#### Task 5: FAISS File Locking
- **Objective**: Prevent Segment Violations.
- **Action**: Implement `fcntl.flock` context manager in `retrievers.py` for all index read/write ops.
- **Audit Ref**: Discovery A.
- **Verification**: Trigger a search while the crawler is mid-ingestion (ensure no crash).

#### Task 6: Memory Watchdog (The "400MB Rule")
- **Objective**: Prevent ZRAM death loops.
- **Action**: Add background thread in `main.py`. Reject queries with `503` if `available_ram < 400MB`.
- **Caveat Ref**: 1.1 (Memory Tug-of-War).
- **Verification**: Artificially inflate a memory buffer and verify `503` response.

---

### Phase 4: Intelligence & Curation (The Harmony)

#### Task 7: Hybrid RRF Fusion
- **Objective**: 91% Search Accuracy.
- **Action**: Implement Reciprocal Rank Fusion ($k=60$) in `main.py`. Use raw BM25 score as tie-breaker.
- **Caveat Ref**: 2.2 (Retriever Guard for zero-results).
- **Verification**: Run `scripts/query_test.py --benchmark`.

#### Task 8: `yt-dlp` Sovereign Curation
- **Objective**: Browserless transcript extraction.
- **Action**: Replace heuristic scraping in `crawl.py` with `yt-dlp` Python API (`extract_flat: True`).
- **Verification**: Curate a YouTube URL and verify `.vtt` metadata exists in the vault.

---

### Phase 5: Hardware & Performance (The Order)

#### Task 9: Vulkan Elite Flags
- **Objective**: Maximize Vega 8 throughput.
- **Action**: Update `dependencies.py`. Set `scalar_block_layout=True` and `--cache-type-k q8_0`.
- **Caveat Ref**: 1.1 (Limit combined memory to 70%).
- **Verification**: `make doctor` (check Vulkan status).

#### Task 10: Startup Warmup Probe
- **Objective**: Eliminate cold-start stutter.
- **Action**: Update `healthcheck.py` to run a $64 \times 64$ matrix multiplication on startup.
- **Audit Ref**: Discovery C.
- **Verification**: Confirm first UI query takes < 500ms after reboot.

---

### Phase 6: Observability & Housekeeping

#### Task 11: `structlog` Contextual Logging
- **Objective**: Unified JSON observability.
- **Action**: Refactor `logging_config.py`. Inject `request_id` and `memory_pressure`.
- **Verification**: `tail -f logs/xnai.log | jq .`

#### Task 12: Housekeeping & Rotation
- **Objective**: Prevent disk exhaustion.
- **Action**: Add `make clean-reports` to `Makefile`. Archive files > 7 days old.
- **Audit Ref**: Discovery D.
- **Verification**: Run `make clean-reports` and check `reports/archive/`.

---

### Phase 7: Team Synchronization

#### Task 13: Delta Pulse Implementation
- **Objective**: Sync state with Nova (Grok 4.1).
- **Action**: Create `scripts/update_pulse.py`. Write **Delta-only** JSON to `memory_bank/system_pulse.json`.
- **Caveat Ref**: 4.1 (Keep footprint small).
- **Verification**: Verify JSON content reflects only the most recent task changes.

---

## 🚀 Final Implementation Callout
**Cline**: You are authorized to begin Phase 1, Task 1. Do not move to Task 2 until Task 1 verification passes. Use the `FORGE_SUPPLEMENTAL_GUIDE` for coding style.

**Status**: READY FOR DEPLOYMENT 🤖💫
