import anyio
import json
import logging
import os
import time
import yaml
import zstandard as zstd
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.config_loader import load_config
from app.XNAi_rag_app.core.metrics import metrics_collector

logger = logging.getLogger(__name__)

# Prometheus Metrics for the Librarian
LIBRARIAN_SUMMARIES = metrics_collector.create_counter("xnai_librarian_summaries_total", "Total session summaries generated")
LIBRARIAN_ARCHIVES = metrics_collector.create_counter("xnai_librarian_archives_total", "Total session archives created")
LIBRARIAN_ENTROPY = metrics_collector.create_gauge("xnai_librarian_state_entropy", "Measured state entropy score (0-1)", ["session_id"])
LIBRARIAN_COMPRESSION = metrics_collector.create_gauge("xnai_librarian_compression_ratio", "Raw context vs Summary ratio", ["session_id"])

class TheLibrarian(AgentBusClient):
    """
    Asynchronous State Worker for the Omega Stack.
    Responsible for session-bloat monitoring, recursive summarization, and zstd archival.
    """

    def __init__(self, agent_did: str = "worker:librarian:001"):
        super().__init__(agent_did)
        self.group_name = "librarian_group"
        self.config = load_config()
        self.archive_dir = Path(os.getenv("SESSION_ARCHIVE_DIR", "memory_bank/recall/conversations/archives"))
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.cctx = zstd.ZstdCompressor(level=10)

    async def start_listening(self):
        """Monitor Agent Bus for librarian-specific events with Metropolis resilience."""
        logger.info(f"📚 The Librarian ({self.agent_did}) online. Monitoring session state...")
        
        retry_delay = 2
        while True:
            try:
                tasks = await self.fetch_tasks(count=5)
                for task in tasks:
                    event_type = task["type"]
                    payload = task["payload"]

                    if event_type == "session_bloat":
                        await self._handle_bloat(payload)
                    elif event_type == "manual_checkpoint":
                        await self._handle_checkpoint(payload)

                    await self.acknowledge_task(task["id"])
                
                # Reset delay on success
                retry_delay = 2
                await anyio.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Librarian error: {e}")
                # Exponential backoff: 2, 4, 8, 16... max 60s
                retry_delay = min(retry_delay * 2, 60)
                await anyio.sleep(retry_delay)

    async def _handle_bloat(self, payload: Dict[str, Any]):
        """Trigger recursive summarization and archival for bloated sessions."""
        session_id = payload.get("session_id")
        token_count = payload.get("token_count", 0)
        
        logger.warning(f"⚠️ Session Bloat Detected: {session_id} ({token_count} tokens)")
        await self._create_state_summary(session_id)

    async def _handle_checkpoint(self, payload: Dict[str, Any]):
        """Manually triggered checkpoint."""
        session_id = payload.get("session_id")
        logger.info(f"📍 Manual Checkpoint Triggered: {session_id}")
        await self._create_state_summary(session_id)

    async def _create_state_summary(self, session_id: str):
        """
        1. Fetch raw history from Redis.
        2. Summarize via local LLM (RPC call or local load).
        3. Archive raw log to zstd.
        4. Update 'active_summary' in Redis.
        """
        try:
            # 1. Fetch History (Placeholder for actual Redis fetch)
            # history = await self.redis.lrange(f"xnai:session:{session_id}:history", 0, -1)
            history_raw = "Example raw session history content..." 
            
            # 2. Generate YAML Summary (Logic will integrate with RAG API /query)
            state_summary = {
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "COMPLETED",
                "completed_tasks": ["Phase 1: KV Cache Optimization"],
                "open_tasks": ["Phase 2: The Librarian Implementation"],
                "context_anchors": {
                    "active_model": "Qwen2.5-0.5B",
                    "n_ctx": 32768
                },
                "decisions": [
                    "Using q4_0 KV cache for RAM efficiency"
                ]
            }
            
            summary_yaml = yaml.dump(state_summary, sort_keys=False)
            
            # Metrics: Compression Ratio
            raw_len = len(history_raw)
            summary_len = len(summary_yaml)
            ratio = raw_len / summary_len if summary_len > 0 else 0
            LIBRARIAN_COMPRESSION.labels(session_id=session_id).set(ratio)
            
            # 3. Archive Raw Log
            archive_path = self.archive_dir / f"{session_id}_{int(time.time())}.log.zst"
            with open(archive_path, 'wb') as f:
                f.write(self.cctx.compress(history_raw.encode('utf-8')))
            
            # 4. Update Redis (Placeholder)
            # await self.redis.set(f"xnai:session:{session_id}:last_summary", summary_yaml)
            
            LIBRARIAN_SUMMARIES.inc()
            LIBRARIAN_ARCHIVES.inc()
            logger.info(f"✅ Librarian successfully processed session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to create summary for {session_id}: {e}")

if __name__ == "__main__":
    # Metropolis Standard: Use anyio.run for execution
    async def run_worker():
        async with TheLibrarian() as librarian:
            await librarian.start_listening()
            
    anyio.run(run_worker)
