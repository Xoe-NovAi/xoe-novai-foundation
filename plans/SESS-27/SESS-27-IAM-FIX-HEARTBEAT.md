# Plan: IAM Gate Fix & Heartbeat Logger (SESS-27)

## Objective
1. Fix the `xnai_library_curator` IAM DB initialization error by refactoring the database connection logic.
2. Implement a "Heartbeat Logger" to persist session stats and token usage to a file periodically during Autonomous Marathons.

## Key Files & Context
- `app/XNAi_rag_app/services/database.py`: Centralized DB session management.
- `app/XNAi_rag_app/core/iam_db.py`: Identity and Access Management DB logic.
- `app/XNAi_rag_app/workers/library_curator.py`: The worker reporting the error.
- `app/XNAi_rag_app/core/xnai_heartbeat.py`: (New) Heartbeat logging service.

## Implementation Steps

### Phase 1: IAM Gate Fix
1. **Refactor `app/XNAi_rag_app/services/database.py`**:
   - Change `DATABASE_URL` resolution to check for container environment.
   - Implement `get_engine()` lazy-loading to ensure environment variables are hydrated before engine creation.
   - Update `SessionLocal` and `get_db` to use the lazy engine.

2. **Refactor `app/XNAi_rag_app/core/iam_db.py`**:
   - Ensure the `IAMDatabase` class doesn't attempt to connect to the DB at import time.
   - Move `Base.metadata.create_all` inside an explicit initialization method.

### Phase 2: Heartbeat Logger
1. **Create `app/XNAi_rag_app/core/xnai_heartbeat.py`**:
   - Implement an async loop that writes system stats (RAM, zRAM), token usage (estimated), and agent status to `.logs/heartbeat.jsonl` every 15 minutes.
   - Integrate with `ResourceHub` for centralized monitoring.

2. **Update Worker Entrypoints**:
   - Update `library_curator.py` to launch the heartbeat task in the background.

## Verification & Testing
1. **Verify IAM Fix**:
   - Run `podman logs xnai_library_curator` and ensure the "IAM DB initialization failed" error is gone.
   - Test connection to `xnai_postgres` from the worker.
2. **Verify Heartbeat**:
   - Start the worker and verify `.logs/heartbeat.jsonl` is being updated.
3. **Verify Ingestion**:
   - Queue a test curation task and monitor the `xnai_linguistic` collection in Qdrant.

## Integration & Roadmap
- This fix unblocks **Phase 4 (Hellenic Ingestion)**.
- Once verified, we will trigger the mass technical manual ingestion.
- Future AMRs will use the `heartbeat.jsonl` for crash recovery.
