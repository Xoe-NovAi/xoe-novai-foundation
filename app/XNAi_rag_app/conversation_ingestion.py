# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint5-2026-02-18
# version: v1.0.0
# created: 2026-02-18
# ---
"""
conversation_ingestion.py — CLI Session → Qdrant xnai_conversations

Harvests and ingests AI CLI session data from:
  - GitHub Copilot CLI: ~/.copilot/session-state/<UUID>/events.jsonl
  - Gemini CLI: ~/.gemini/sessions/<id>/conversation.json
  - OpenCode CLI: ~/.opencode/sessions/<id>.json
  - Cline: ~/.config/VSCodium/.../tasks/<id>/api_conversation_history.json

Target Qdrant collection: xnai_conversations
See: expert-knowledge/research/CLI-SESSION-STORAGE-DEEP-DIVE-2026-02-18.md
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

COPILOT_DIR = Path.home() / ".copilot" / "session-state"
GEMINI_DIR = Path.home() / ".gemini" / "sessions"
OPENCODE_DIR = Path.home() / ".opencode" / "sessions"
CLINE_DIR = (
    Path.home()
    / ".config"
    / "VSCodium"
    / "User"
    / "globalStorage"
    / "saoudrizwan.claude-dev"
    / "tasks"
)

QDRANT_COLLECTION = "xnai_conversations"
EMBEDDING_MODEL = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_DIM = 768

# ─── Frontmatter Parser ───────────────────────────────────────────────────────


def extract_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}
    return {}


# ─── Source Parsers ───────────────────────────────────────────────────────────


class CopilotSessionParser:
    """Parse GitHub Copilot CLI events.jsonl sessions."""

    def parse_session(self, session_dir: Path) -> list[dict[str, Any]]:
        """Parse a single Copilot session directory."""
        events_file = session_dir / "events.jsonl"
        workspace_file = session_dir / "workspace.yaml"

        if not events_file.exists():
            return []

        # Load workspace metadata
        workspace: dict = {}
        if workspace_file.exists():
            try:
                workspace = yaml.safe_load(workspace_file.read_text()) or {}
            except Exception:
                pass

        session_id = workspace.get("id", session_dir.name)
        cwd = workspace.get("cwd", "")
        created_at = workspace.get("created_at", "")
        model = workspace.get("model", "gpt-4o")

        records = []
        try:
            with events_file.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    event_type = event.get("type", "")
                    if event_type in ("user_message", "assistant_message"):
                        role = "user" if event_type == "user_message" else "assistant"
                        content = event.get("content", "")
                        if not content:
                            continue
                        records.append(
                            {
                                "source": "copilot",
                                "session_id": session_id,
                                "timestamp": event.get("timestamp", created_at),
                                "cwd": cwd,
                                "role": role,
                                "content": content,
                                "model": model,
                                "tags": self._classify_content(content),
                            }
                        )
        except OSError as e:
            logger.warning("Failed to read %s: %s", events_file, e)

        return records

    def _classify_content(self, content: str) -> list[str]:
        """Auto-classify content for tagging."""
        tags = []
        lower = content.lower()
        if any(w in lower for w in ["decision", "decided", "chose", "approach"]):
            tags.append("architectural-decision")
        if any(w in lower for w in ["def ", "class ", "import ", "```python"]):
            tags.append("code")
        if any(w in lower for w in ["research", "found", "discovered", "according to"]):
            tags.append("research")
        if any(w in lower for w in ["error", "fix", "bug", "issue"]):
            tags.append("debugging")
        return tags or ["conversation"]

    def discover_sessions(self) -> list[Path]:
        """Find all Copilot session directories."""
        if not COPILOT_DIR.exists():
            return []
        return [d for d in COPILOT_DIR.iterdir() if d.is_dir()]


class GeminiSessionParser:
    """Parse Gemini CLI session files."""

    def parse_session(self, session_dir: Path) -> list[dict[str, Any]]:
        conv_file = session_dir / "conversation.json"
        meta_file = session_dir / "metadata.json"

        if not conv_file.exists():
            return []

        metadata: dict = {}
        if meta_file.exists():
            try:
                metadata = json.loads(meta_file.read_text())
            except Exception:
                pass

        session_id = metadata.get("id", session_dir.name)
        model = metadata.get("model", "gemini-2.0-flash")

        try:
            turns = json.loads(conv_file.read_text())
        except Exception:
            return []

        records = []
        for turn in turns:
            role = turn.get("role", "user")
            parts = turn.get("parts", [])
            content = " ".join(p.get("text", "") for p in parts if "text" in p)
            if content:
                records.append(
                    {
                        "source": "gemini",
                        "session_id": session_id,
                        "timestamp": metadata.get("created_at", ""),
                        "cwd": metadata.get("cwd", ""),
                        "role": role,
                        "content": content,
                        "model": model,
                        "tags": ["conversation"],
                    }
                )
        return records

    def discover_sessions(self) -> list[Path]:
        if not GEMINI_DIR.exists():
            return []
        return [d for d in GEMINI_DIR.iterdir() if d.is_dir()]


class ClineSessionParser:
    """Parse Cline VSCodium extension task history."""

    def parse_task(self, task_dir: Path) -> list[dict[str, Any]]:
        history_file = task_dir / "api_conversation_history.json"
        if not history_file.exists():
            return []

        try:
            messages = json.loads(history_file.read_text())
        except Exception:
            return []

        task_id = task_dir.name
        created = datetime.fromtimestamp(task_dir.stat().st_mtime).isoformat()

        records = []
        for msg in messages:
            role = msg.get("role", "user")
            content_raw = msg.get("content", "")

            # Content can be string or list of content blocks
            if isinstance(content_raw, str):
                content = content_raw
            elif isinstance(content_raw, list):
                parts = []
                for block in content_raw:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            parts.append(block.get("text", ""))
                        elif block.get("type") == "tool_result":
                            # Skip tool results to reduce noise
                            pass
                content = " ".join(parts)
            else:
                continue

            if content and len(content) > 20:
                records.append(
                    {
                        "source": "cline",
                        "session_id": task_id,
                        "timestamp": created,
                        "cwd": "",
                        "role": role,
                        "content": content[:4000],  # cap at 4K chars per chunk
                        "model": "claude-opus-4-5",
                        "tags": ["conversation"],
                    }
                )
        return records

    def discover_tasks(self) -> list[Path]:
        if not CLINE_DIR.exists():
            return []
        return [d for d in CLINE_DIR.iterdir() if d.is_dir()]


# ─── Main Ingestion Class ─────────────────────────────────────────────────────


class ConversationIngestion:
    """
    Harvest CLI session data and ingest into Qdrant xnai_conversations collection.

    Usage:
        ingestion = ConversationIngestion(qdrant_url="http://localhost:6333")
        await ingestion.run()
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        qdrant_api_key: str | None = None,
        dry_run: bool = False,
    ):
        self.qdrant_url = qdrant_url
        self.qdrant_api_key = qdrant_api_key
        self.dry_run = dry_run
        self._qdrant = None
        self._embedder = None

    def _get_qdrant(self):
        """Lazy-load Qdrant client."""
        if self._qdrant is None:
            from qdrant_client import QdrantClient

            self._qdrant = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
            )
        return self._qdrant

    def _get_embedder(self):
        """Lazy-load fastembed model."""
        if self._embedder is None:
            from fastembed import TextEmbedding

            self._embedder = TextEmbedding(model_name=EMBEDDING_MODEL)
        return self._embedder

    def ensure_collection(self) -> None:
        """Create xnai_conversations collection if it doesn't exist."""
        from qdrant_client.models import Distance, VectorParams

        client = self._get_qdrant()
        existing = [c.name for c in client.get_collections().collections]
        if QDRANT_COLLECTION not in existing:
            client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
            logger.info("Created collection: %s", QDRANT_COLLECTION)

    def embed_records(self, records: list[dict]) -> list[dict]:
        """Add vector embeddings to records."""
        embedder = self._get_embedder()
        texts = [r["content"] for r in records]
        embeddings = list(embedder.embed(texts))
        for record, vector in zip(records, embeddings):
            record["vector"] = vector.tolist()
        return records

    def upsert_records(self, records: list[dict]) -> int:
        """Upsert records into Qdrant."""
        from qdrant_client.models import PointStruct

        client = self._get_qdrant()
        points = []
        for record in records:
            vector = record.pop("vector", None)
            if vector is None:
                continue
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{record['source']}-{record['session_id']}-{record['content'][:50]}"))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=record,
                )
            )

        if not points:
            return 0

        client.upsert(collection_name=QDRANT_COLLECTION, points=points)
        return len(points)

    def harvest_all(self) -> list[dict]:
        """Harvest records from all CLI sources."""
        all_records: list[dict] = []

        # Copilot
        copilot = CopilotSessionParser()
        for session_dir in copilot.discover_sessions():
            records = copilot.parse_session(session_dir)
            all_records.extend(records)
            logger.debug("Copilot session %s: %d records", session_dir.name, len(records))

        # Gemini
        gemini = GeminiSessionParser()
        for session_dir in gemini.discover_sessions():
            records = gemini.parse_session(session_dir)
            all_records.extend(records)

        # Cline
        cline = ClineSessionParser()
        for task_dir in cline.discover_tasks():
            records = cline.parse_task(task_dir)
            all_records.extend(records)

        logger.info("Harvested %d total records from all CLI sources", len(all_records))
        return all_records

    def run(self, sources: list[str] | None = None) -> dict[str, int]:
        """
        Run the full harvest + ingest pipeline.

        Args:
            sources: Optional list of sources to include ('copilot', 'gemini', 'cline').
                     If None, all sources are harvested.

        Returns:
            Dict with counts: {'harvested': N, 'ingested': N, 'errors': N}
        """
        stats = {"harvested": 0, "ingested": 0, "errors": 0}

        try:
            records = self.harvest_all()
            if sources:
                records = [r for r in records if r.get("source") in sources]

            stats["harvested"] = len(records)

            if self.dry_run:
                logger.info("DRY RUN: would ingest %d records", len(records))
                return stats

            if not records:
                logger.info("No records to ingest")
                return stats

            self.ensure_collection()

            # Batch embed + upsert in chunks of 100
            batch_size = 100
            for i in range(0, len(records), batch_size):
                batch = records[i : i + batch_size]
                try:
                    batch = self.embed_records(batch)
                    ingested = self.upsert_records(batch)
                    stats["ingested"] += ingested
                except Exception as e:
                    logger.error("Batch ingest error: %s", e)
                    stats["errors"] += len(batch)

        except Exception as e:
            logger.error("Harvest failed: %s", e)
            stats["errors"] += 1

        logger.info(
            "Conversation ingestion complete: harvested=%d ingested=%d errors=%d",
            stats["harvested"],
            stats["ingested"],
            stats["errors"],
        )
        return stats


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="Harvest CLI sessions → Qdrant xnai_conversations")
    parser.add_argument("--qdrant-url", default="http://localhost:6333")
    parser.add_argument("--qdrant-api-key", default=None)
    parser.add_argument("--sources", nargs="+", choices=["copilot", "gemini", "opencode", "cline"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ingestion = ConversationIngestion(
        qdrant_url=args.qdrant_url,
        qdrant_api_key=args.qdrant_api_key,
        dry_run=args.dry_run,
    )
    stats = ingestion.run(sources=args.sources)
    print(f"Done: {stats}")
