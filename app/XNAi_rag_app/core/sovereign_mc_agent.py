"""
Sovereign Mission Control Agent
================================
The XNAi Foundation Stack directing itself.

This agent is the architectural north star: a locally-running orchestration
layer that uses the Foundation Stack as its own intelligence layer.

Architecture:
  - Qdrant: Semantic memory (past decisions, project knowledge)
  - Vikunja: Task tracking and project management (REST API)
  - Redis Streams: Agent Bus routing (AgentBusClient)
  - Consul: Service health awareness
  - memory_bank/: Strategic context (read/write)
  - Ed25519 IAM: Zero-trust agent authentication

Constraints:
  - AnyIO TaskGroups ONLY (never asyncio.gather)
  - No PyTorch / CUDA / Triton / sentence-transformers
  - fastembed (ONNX) for embeddings — zero PyTorch
  - Zero external telemetry
  - UID 1001 for all file operations

Version: 1.1.0
Phase: 2.5 — Sovereign MC Agent
TASK: TASK-021b
Implemented: 2026-02-18
Sprint 2 Fixes: 2026-02-18
  - FIX: asyncio.run → anyio.run (AnyIO policy)
  - FIX: EmbeddingEngine added (fastembed ONNX, no PyTorch)
  - FIX: store_decision/search_decisions now embed text via EmbeddingEngine
  - FIX: MemoryBankReader I/O is non-blocking (anyio.to_thread.run_sync)
  - FIX: OpenCodeDispatcher uses -p/-q flags (not --print)
  - FIX: QdrantMemory.ensure_collection() has 3-retry backoff
  - FIX: subprocess import removed
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import anyio
import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.consul_client import consul_client

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

MEMORY_BANK_PATH = Path(os.getenv("MEMORY_BANK_PATH", "memory_bank"))
VIKUNJA_URL = os.getenv("VIKUNJA_URL", "http://localhost:3456")
VIKUNJA_TOKEN = os.getenv("VIKUNJA_TOKEN", "")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
MC_DID = os.getenv("SOVEREIGN_MC_DID", "did:xnai:sovereign-mc-v1")
MC_COLLECTION = "sovereign_mc_decisions"
MC_VECTOR_DIM = 384  # BAAI/bge-small-en-v1.5 via fastembed


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ProjectContext:
    """Loaded context from memory bank + Qdrant."""
    active_context: str = ""
    progress: str = ""
    team_protocols: str = ""
    phase: str = "unknown"
    priorities: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    loaded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class VikunjaTask:
    """Vikunja task record."""
    id: int
    title: str
    description: str
    priority: int
    done: bool
    project_id: int
    created: str


@dataclass
class AgentBusMessage:
    """Task routed via Agent Bus."""
    task_id: str
    target_did: str
    task_type: str
    payload: dict[str, Any]
    sent_at: str


@dataclass
class SystemHealth:
    """Overall system health snapshot."""
    consul: bool = False
    redis: bool = False
    qdrant: bool = False
    vikunja: bool = False
    overall: bool = False
    checked_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class OpenCodeSession:
    """Running OpenCode agent session."""
    session_id: str
    model: str
    task: str
    process: Optional[Any] = None
    status: str = "running"
    output: str = ""


# ============================================================================
# Embedding Engine (ONNX — no PyTorch)
# ============================================================================

class EmbeddingEngine:
    """
    ONNX-based text embedder using fastembed.
    Model: BAAI/bge-small-en-v1.5 → 384-dim vectors.
    Zero PyTorch, zero GPU, zero telemetry.

    The underlying fastembed.TextEmbedding is synchronous; we run it
    in a thread pool via anyio.to_thread.run_sync to avoid blocking
    the event loop.

    Usage:
        engine = EmbeddingEngine()
        vec = await engine.embed("text to embed")
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self._model_name = model_name
        self._model: Any = None  # lazy init on first use
        self._lock = anyio.Lock()

    def _load_model(self) -> Any:
        """Sync: load fastembed model (runs in thread pool)."""
        if self._model is None:
            from fastembed import TextEmbedding  # type: ignore
            self._model = TextEmbedding(model_name=self._model_name)
            logger.info(f"EmbeddingEngine loaded: {self._model_name}")
        return self._model

    async def embed(self, text: str) -> list[float]:
        """
        Async-safe embed: runs sync fastembed in thread pool.
        Returns a 384-dim float list.
        """
        async with self._lock:
            def _run() -> list[float]:
                model = self._load_model()
                result = list(model.embed([text]))
                return result[0].tolist()

            return await anyio.to_thread.run_sync(_run)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts — returns list of 384-dim vectors."""
        async with self._lock:
            def _run() -> list[list[float]]:
                model = self._load_model()
                result = list(model.embed(texts))
                return [v.tolist() for v in result]

            return await anyio.to_thread.run_sync(_run)


# Singleton embedding engine shared across the process
_embedding_engine: Optional[EmbeddingEngine] = None


def get_embedding_engine() -> EmbeddingEngine:
    """Return the process-level EmbeddingEngine singleton."""
    global _embedding_engine
    if _embedding_engine is None:
        _embedding_engine = EmbeddingEngine()
    return _embedding_engine


# ============================================================================
# Memory Bank Reader
# ============================================================================

class MemoryBankReader:
    """
    Reads and writes strategic context from memory_bank/*.md files.
    All I/O is non-blocking via anyio.to_thread.run_sync.
    """

    def __init__(self, bank_path: Path = MEMORY_BANK_PATH):
        self.bank_path = bank_path

    async def read_file(self, filename: str) -> str:
        """
        Async-safe read of a memory bank file.
        Returns empty string if file is missing.
        """
        filepath = self.bank_path / filename

        def _read() -> str:
            try:
                if filepath.exists():
                    return filepath.read_text(encoding="utf-8")
                logger.warning(f"Memory bank file not found: {filepath}")
                return ""
            except OSError as e:
                logger.error(f"Failed to read {filepath}: {e}")
                return ""

        return await anyio.to_thread.run_sync(_read)

    async def write_file(self, filename: str, content: str) -> bool:
        """Async-safe write to a memory bank file."""
        filepath = self.bank_path / filename

        def _write() -> bool:
            try:
                self.bank_path.mkdir(parents=True, exist_ok=True)
                filepath.write_text(content, encoding="utf-8")
                logger.info(f"Memory bank updated: {filepath}")
                return True
            except OSError as e:
                logger.error(f"Failed to write {filepath}: {e}")
                return False

        return await anyio.to_thread.run_sync(_write)

    async def load_context(self) -> ProjectContext:
        """Load the full project context from memory bank files in parallel."""
        active_holder: dict[str, str] = {}
        progress_holder: dict[str, str] = {}
        protocols_holder: dict[str, str] = {}

        async def _load_active():
            active_holder["v"] = await self.read_file("activeContext.md")

        async def _load_progress():
            progress_holder["v"] = await self.read_file("progress.md")

        async def _load_protocols():
            protocols_holder["v"] = await self.read_file("teamProtocols.md")

        async with anyio.create_task_group() as tg:
            tg.start_soon(_load_active)
            tg.start_soon(_load_progress)
            tg.start_soon(_load_protocols)

        active = active_holder.get("v", "")
        progress = progress_holder.get("v", "")
        protocols = protocols_holder.get("v", "")

        # Parse phase from progress.md
        phase = "unknown"
        priorities: list[str] = []
        blockers: list[str] = []

        for line in progress.splitlines():
            if "phase:" in line.lower():
                phase = line.split(":")[-1].strip()
            if line.strip().startswith("- ") and "Next milestone" not in line:
                priorities.append(line.strip("- ").strip())

        return ProjectContext(
            active_context=active,
            progress=progress,
            team_protocols=protocols,
            phase=phase,
            priorities=priorities[:5],
            blockers=blockers,
        )

    async def append_to_active_context(self, section_title: str, content: str) -> bool:
        """Append a timestamped section to activeContext.md."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        addition = f"\n\n## {section_title} — {timestamp}\n\n{content}\n"
        existing = await self.read_file("activeContext.md")
        return await self.write_file("activeContext.md", existing + addition)


# ============================================================================
# Vikunja Client
# ============================================================================

class VikunjaClient:
    """
    Async Vikunja REST API client.
    Handles task creation, updates, and project listing.
    API: http://localhost:3456/api/v1
    """

    def __init__(
        self,
        base_url: str = VIKUNJA_URL,
        token: str = VIKUNJA_TOKEN,
    ):
        self.base_url = f"{base_url.rstrip('/')}/api/v1"
        self.headers = {
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        }

    async def health(self) -> bool:
        """Check Vikunja API availability."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self.base_url}/info", headers=self.headers
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Vikunja health check failed: {e}")
            return False

    async def list_projects(self) -> list[dict]:
        """List all Vikunja projects."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/projects", headers=self.headers
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []

    async def create_task(
        self,
        project_id: int,
        title: str,
        description: str = "",
        priority: int = 3,
    ) -> Optional[VikunjaTask]:
        """
        Create a task in Vikunja.
        Priority: 1=critical, 2=high, 3=medium, 4=low, 5=someday
        """
        task_data = {
            "title": title,
            "description": description,
            "priority": priority,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.put(
                    f"{self.base_url}/projects/{project_id}/tasks",
                    headers=self.headers,
                    json=task_data,
                )
                resp.raise_for_status()
                data = resp.json()
                return VikunjaTask(
                    id=data["id"],
                    title=data["title"],
                    description=data.get("description", ""),
                    priority=data.get("priority", priority),
                    done=data.get("done", False),
                    project_id=project_id,
                    created=data.get("created", ""),
                )
        except Exception as e:
            logger.error(f"Failed to create Vikunja task '{title}': {e}")
            return None

    async def update_task(
        self,
        task_id: int,
        done: Optional[bool] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Update an existing Vikunja task."""
        update_data: dict[str, Any] = {}
        if done is not None:
            update_data["done"] = done
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description

        if not update_data:
            return True

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self.headers,
                    json=update_data,
                )
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return False

    async def list_tasks(self, project_id: int) -> list[dict]:
        """List tasks in a project."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/projects/{project_id}/tasks",
                    headers=self.headers,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"Failed to list tasks for project {project_id}: {e}")
            return []


# ============================================================================
# Qdrant Semantic Memory
# ============================================================================

class QdrantMemory:
    """
    Semantic memory layer using AsyncQdrantClient.
    Stores past decisions, architectural choices, and research findings
    for retrieval by future sessions.

    Embedding is handled by EmbeddingEngine (fastembed ONNX) — no PyTorch.
    """

    def __init__(
        self,
        url: str = QDRANT_URL,
        api_key: str = QDRANT_API_KEY,
        collection: str = MC_COLLECTION,
        embedder: Optional[EmbeddingEngine] = None,
    ):
        kwargs: dict[str, Any] = {"url": url, "timeout": 10.0}
        if api_key:
            kwargs["api_key"] = api_key
        self.client = AsyncQdrantClient(**kwargs)
        self.collection = collection
        self.embedder = embedder or get_embedding_engine()

    async def ensure_collection(self) -> bool:
        """
        Create collection if it doesn't exist.
        Retries up to 3 times with 2s backoff; logs degraded mode on failure.
        """
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                collections = await self.client.get_collections()
                names = [c.name for c in collections.collections]
                if self.collection not in names:
                    await self.client.create_collection(
                        collection_name=self.collection,
                        vectors_config=VectorParams(
                            size=MC_VECTOR_DIM, distance=Distance.COSINE
                        ),
                    )
                    logger.info(f"Created Qdrant collection: {self.collection}")
                return True
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(
                        f"Qdrant collection setup attempt {attempt}/{max_retries} "
                        f"failed: {e} — retrying in 2s"
                    )
                    await anyio.sleep(2.0)
                else:
                    logger.warning(
                        f"Qdrant collection setup failed after {max_retries} attempts: {e} "
                        f"— running in degraded mode (no semantic memory)"
                    )
        return False

    async def store_decision(
        self,
        decision_id: str,
        title: str,
        content: str,
        tags: Optional[list[str]] = None,
    ) -> bool:
        """
        Store a decision or research finding in semantic memory.
        Embeds `title + content` via EmbeddingEngine (fastembed ONNX).
        Silently degrades if Qdrant is unavailable.
        """
        tags = tags or []
        embed_text = f"{title}\n\n{content}"

        try:
            vec = await self.embedder.embed(embed_text)
        except Exception as e:
            logger.warning(f"Embedding failed for '{title}': {e} — using zero vector")
            vec = [0.0] * MC_VECTOR_DIM

        try:
            point = PointStruct(
                id=abs(hash(decision_id)) % (2**31),  # uint32-safe
                vector=vec,
                payload={
                    "decision_id": decision_id,
                    "title": title,
                    "content": content,
                    "tags": tags,
                    "stored_at": datetime.now(timezone.utc).isoformat(),
                    "agent": "sovereign-mc-v1",
                },
            )
            await self.client.upsert(
                collection_name=self.collection,
                points=[point],
            )
            logger.info(f"Stored decision in Qdrant: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to store decision in Qdrant: {e}")
            return False

    async def search_decisions(
        self,
        query: str,
        limit: int = 5,
        filter_tags: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Search past decisions by semantic similarity.
        Accepts a query string; embeds it via EmbeddingEngine.
        """
        try:
            query_vec = await self.embedder.embed(query)
        except Exception as e:
            logger.error(f"Failed to embed search query: {e}")
            return []

        try:
            results = await self.client.search(
                collection_name=self.collection,
                query_vector=query_vec,
                limit=limit,
            )
            return [
                {
                    "score": r.score,
                    "title": r.payload.get("title"),
                    "content": r.payload.get("content"),
                    "tags": r.payload.get("tags", []),
                    "stored_at": r.payload.get("stored_at"),
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []

    async def close(self):
        """Close the Qdrant client."""
        try:
            await self.client.close()
        except Exception:
            pass


# ============================================================================
# OpenCode Dispatcher
# ============================================================================

class OpenCodeDispatcher:
    """
    Spawn and manage OpenCode CLI agent sessions.
    Uses anyio subprocess for AnyIO compatibility.

    CLI flags:
      -p / --prompt  : non-interactive prompt mode (charmbracelet/crush ≥0.1)
      -q             : suppress spinner / quiet output
    """

    @staticmethod
    async def spawn(
        task: str,
        model: str = "opencode/glm-5-free",
        session_id: Optional[str] = None,
        working_dir: Optional[str] = None,
    ) -> OpenCodeSession:
        """
        Spawn an OpenCode agent session for a task.
        Returns session metadata with stdout captured as output.
        """
        import uuid

        sid = session_id or f"mc-{uuid.uuid4().hex[:8]}"
        cwd = working_dir or str(Path.cwd())

        cmd = [
            "opencode",
            "--model", model,
            "--session", sid,
            "-q",        # quiet: suppress spinner
            "-p", task,  # non-interactive prompt mode (NOT --print)
        ]

        logger.info(f"Spawning OpenCode [{model}] session={sid}: {task[:60]}...")

        try:
            result = await anyio.run_process(
                cmd,
                cwd=cwd,
                check=False,
            )
            output = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
            status = "completed" if result.returncode == 0 else "failed"
            return OpenCodeSession(
                session_id=sid,
                model=model,
                task=task,
                status=status,
                output=output,
            )
        except Exception as e:
            logger.error(f"OpenCode spawn failed: {e}")
            return OpenCodeSession(
                session_id=sid,
                model=model,
                task=task,
                status="error",
                output=str(e),
            )


# ============================================================================
# Sovereign MC Agent (Core)
# ============================================================================

class SovereignMCAgent:
    """
    The XNAi Foundation Stack's self-directing Mission Control Agent.

    This agent orchestrates the entire XNAi Foundation using its own
    infrastructure as the intelligence layer. It is sovereign — all
    operations are local, zero external telemetry.

    Usage:
        agent = SovereignMCAgent()
        context = await agent.load_context()
        status = await agent.get_project_status()
        task = await agent.create_vikunja_task("Title", "Desc", priority=1)
        await agent.delegate_to_opencode("research X", "opencode/glm-5-free")

    AnyIO note: All concurrent operations use TaskGroups, never asyncio.gather.
    """

    def __init__(
        self,
        agent_did: str = MC_DID,
        memory_bank_path: Path = MEMORY_BANK_PATH,
        vikunja_url: str = VIKUNJA_URL,
        qdrant_url: str = QDRANT_URL,
    ):
        self.did = agent_did
        self.memory = MemoryBankReader(memory_bank_path)
        self.vikunja = VikunjaClient(base_url=vikunja_url)
        self.qdrant = QdrantMemory(url=qdrant_url)
        self.dispatcher = OpenCodeDispatcher()
        self._context: Optional[ProjectContext] = None
        logger.info(f"SovereignMCAgent initialized: {self.did}")

    # -------------------------------------------------------------------------
    # Context Loading
    # -------------------------------------------------------------------------

    async def load_context(self) -> ProjectContext:
        """
        Load full project context in parallel:
          - memory_bank/*.md files (async I/O via thread pool)
          - Qdrant collection setup (async, non-blocking, with retry)

        Uses AnyIO TaskGroup for parallel execution.
        """
        context_holder: dict[str, Any] = {}
        qdrant_ready: dict[str, bool] = {}

        async def _load_memory():
            context_holder["ctx"] = await self.memory.load_context()

        async def _init_qdrant():
            qdrant_ready["ok"] = await self.qdrant.ensure_collection()

        async with anyio.create_task_group() as tg:
            tg.start_soon(_load_memory)
            tg.start_soon(_init_qdrant)

        self._context = context_holder.get("ctx", ProjectContext())
        if qdrant_ready.get("ok"):
            logger.info("Qdrant semantic memory: ready")
        else:
            logger.warning("Qdrant semantic memory: unavailable (degraded mode)")

        logger.info(
            f"Context loaded: phase={self._context.phase}, "
            f"priorities={len(self._context.priorities)}"
        )
        return self._context

    # -------------------------------------------------------------------------
    # Project Status
    # -------------------------------------------------------------------------

    async def get_project_status(
        self, vikunja_project_id: int = 1
    ) -> dict[str, Any]:
        """
        Get comprehensive project status in parallel:
          - Vikunja task list
          - System health
          - Current context summary

        Uses AnyIO TaskGroup for parallel execution.
        """
        health_holder: dict[str, SystemHealth] = {}
        tasks_holder: dict[str, list] = {}
        projects_holder: dict[str, list] = {}

        async def _get_health():
            health_holder["h"] = await self.get_service_health()

        async def _get_tasks():
            tasks_holder["t"] = await self.vikunja.list_tasks(vikunja_project_id)

        async def _get_projects():
            projects_holder["p"] = await self.vikunja.list_projects()

        async with anyio.create_task_group() as tg:
            tg.start_soon(_get_health)
            tg.start_soon(_get_tasks)
            tg.start_soon(_get_projects)

        health = health_holder.get("h", SystemHealth())
        tasks = tasks_holder.get("t", [])
        projects = projects_holder.get("p", [])

        open_tasks = [t for t in tasks if not t.get("done", False)]
        done_tasks = [t for t in tasks if t.get("done", False)]

        return {
            "agent": self.did,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": self._context.phase if self._context else "unknown",
            "health": {
                "overall": health.overall,
                "consul": health.consul,
                "redis": health.redis,
                "qdrant": health.qdrant,
                "vikunja": health.vikunja,
            },
            "vikunja": {
                "projects": len(projects),
                "open_tasks": len(open_tasks),
                "completed_tasks": len(done_tasks),
                "tasks": open_tasks[:10],
            },
            "priorities": self._context.priorities if self._context else [],
            "blockers": self._context.blockers if self._context else [],
        }

    # -------------------------------------------------------------------------
    # Task Management
    # -------------------------------------------------------------------------

    async def create_vikunja_task(
        self,
        title: str,
        description: str = "",
        priority: int = 3,
        project_id: int = 1,
        store_in_qdrant: bool = True,
    ) -> Optional[VikunjaTask]:
        """
        Create a task in Vikunja and optionally record it in Qdrant memory.
        priority: 1=critical, 2=high, 3=medium, 4=low, 5=someday
        """
        task = await self.vikunja.create_task(
            project_id=project_id,
            title=title,
            description=description,
            priority=priority,
        )

        if task and store_in_qdrant:
            await self.qdrant.store_decision(
                decision_id=f"task-{task.id}",
                title=f"Task Created: {title}",
                content=description,
                tags=["vikunja-task", f"priority-{priority}"],
            )

        if task:
            logger.info(f"Created Vikunja task #{task.id}: {title}")
        return task

    async def complete_vikunja_task(self, task_id: int) -> bool:
        """Mark a Vikunja task as done."""
        return await self.vikunja.update_task(task_id=task_id, done=True)

    # -------------------------------------------------------------------------
    # Agent Delegation
    # -------------------------------------------------------------------------

    async def delegate_to_opencode(
        self,
        task: str,
        model: str = "opencode/glm-5-free",
        session_id: Optional[str] = None,
    ) -> OpenCodeSession:
        """
        Delegate a task to an OpenCode CLI agent.
        Returns the completed session with output.
        """
        session = await self.dispatcher.spawn(
            task=task,
            model=model,
            session_id=session_id,
        )

        await self.qdrant.store_decision(
            decision_id=f"delegation-{session.session_id}",
            title=f"Delegated to OpenCode [{model}]",
            content=task,
            tags=["delegation", "opencode", model.replace("/", "-")],
        )

        logger.info(
            f"OpenCode session {session.session_id} "
            f"status={session.status} output_len={len(session.output)}"
        )
        return session

    async def route_via_agent_bus(
        self,
        target_did: str,
        task_type: str,
        payload: dict[str, Any],
    ) -> Optional[str]:
        """
        Route a task to another agent via the Agent Bus (Redis Streams).
        Returns the task_id on success, None on failure.
        """
        try:
            async with AgentBusClient(self.did) as bus:
                task_id = await bus.send_task(
                    target_did=target_did,
                    task_type=task_type,
                    payload=payload,
                )
                logger.info(
                    f"Routed task via Agent Bus: {task_id} → {target_did}"
                )
                return task_id.decode() if isinstance(task_id, bytes) else task_id
        except Exception as e:
            logger.error(f"Agent Bus routing failed: {e}")
            return None

    # -------------------------------------------------------------------------
    # Memory & Knowledge
    # -------------------------------------------------------------------------

    async def update_memory(
        self,
        section_title: str,
        content: str,
        store_in_qdrant: bool = True,
    ) -> bool:
        """
        Update the memory bank with a new section.
        Optionally stores in Qdrant for semantic retrieval.
        """
        success = await self.memory.append_to_active_context(section_title, content)

        if success and store_in_qdrant:
            await self.qdrant.store_decision(
                decision_id=f"mem-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                title=section_title,
                content=content,
                tags=["memory-bank-update"],
            )

        return success

    async def recall_decisions(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict]:
        """
        Recall past decisions from Qdrant semantic memory.
        query: natural language query string (embedded internally).
        """
        return await self.qdrant.search_decisions(query=query, limit=limit)

    # -------------------------------------------------------------------------
    # Health Monitoring
    # -------------------------------------------------------------------------

    async def get_service_health(self) -> SystemHealth:
        """
        Check health of all Foundation Stack services in parallel.
        Uses AnyIO TaskGroup for concurrent checks.
        """
        health = SystemHealth()
        results: dict[str, bool] = {}

        async def _check_consul():
            results["consul"] = consul_client.is_connected

        async def _check_redis():
            try:
                from redis.asyncio import Redis
                r = Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    password=os.getenv("REDIS_PASSWORD"),
                    socket_connect_timeout=2.0,
                )
                await r.ping()
                await r.aclose()
                results["redis"] = True
            except Exception:
                results["redis"] = False

        async def _check_qdrant():
            try:
                ok = await self.qdrant.ensure_collection()
                results["qdrant"] = ok
            except Exception:
                results["qdrant"] = False

        async def _check_vikunja():
            results["vikunja"] = await self.vikunja.health()

        async with anyio.create_task_group() as tg:
            tg.start_soon(_check_consul)
            tg.start_soon(_check_redis)
            tg.start_soon(_check_qdrant)
            tg.start_soon(_check_vikunja)

        health.consul = results.get("consul", False)
        health.redis = results.get("redis", False)
        health.qdrant = results.get("qdrant", False)
        health.vikunja = results.get("vikunja", False)
        health.overall = all([health.consul, health.redis, health.qdrant])
        health.details = results

        status_icon = "✅" if health.overall else "⚠️"
        logger.info(
            f"{status_icon} Health: consul={health.consul} redis={health.redis} "
            f"qdrant={health.qdrant} vikunja={health.vikunja}"
        )
        return health

    # -------------------------------------------------------------------------
    # MC Oversight Output
    # -------------------------------------------------------------------------

    async def generate_status_report(
        self, vikunja_project_id: int = 1
    ) -> str:
        """
        Generate a markdown status report for mc-oversight/.
        Captures current project state for the next agent session.
        """
        status = await self.get_project_status(vikunja_project_id)
        ctx = self._context or ProjectContext()

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        health_icon = "✅" if status["health"]["overall"] else "⚠️"

        lines = [
            "# XNAi Foundation — Initiative Status Dashboard",
            f"**Generated**: {timestamp}  ",
            f"**Agent**: {self.did}  ",
            f"**Phase**: {status['phase']}  ",
            "",
            f"## System Health {health_icon}",
            "",
            "| Service | Status |",
            "|---------|--------|",
            f"| Consul  | {'✅ Healthy' if status['health']['consul'] else '❌ Down'} |",
            f"| Redis   | {'✅ Healthy' if status['health']['redis'] else '❌ Down'} |",
            f"| Qdrant  | {'✅ Healthy' if status['health']['qdrant'] else '❌ Down'} |",
            f"| Vikunja | {'✅ Healthy' if status['health']['vikunja'] else '❌ Down'} |",
            "",
            "## Vikunja Project Status",
            "",
            f"- **Projects**: {status['vikunja']['projects']}",
            f"- **Open Tasks**: {status['vikunja']['open_tasks']}",
            f"- **Completed**: {status['vikunja']['completed_tasks']}",
            "",
        ]

        if ctx.priorities:
            lines += ["## Current Priorities", ""]
            for i, p in enumerate(ctx.priorities, 1):
                lines.append(f"{i}. {p}")
            lines.append("")

        open_tasks = status["vikunja"].get("tasks", [])
        if open_tasks:
            lines += ["## Open Tasks (Top 10)", ""]
            for t in open_tasks[:10]:
                priority = t.get("priority", 3)
                done = "✅" if t.get("done") else "⬜"
                lines.append(
                    f"- {done} **{t.get('title', 'Unknown')}** (priority={priority})"
                )
            lines.append("")

        return "\n".join(lines)

    async def write_status_report(
        self,
        output_path: str = "mc-oversight/initiative-status-dashboard.md",
        vikunja_project_id: int = 1,
    ) -> bool:
        """Generate and write the status dashboard to mc-oversight/."""
        report = await self.generate_status_report(vikunja_project_id)

        def _write():
            try:
                path = Path(output_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(report, encoding="utf-8")
                logger.info(f"Status report written: {output_path}")
                return True
            except OSError as e:
                logger.error(f"Failed to write status report: {e}")
                return False

        return await anyio.to_thread.run_sync(_write)

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def shutdown(self):
        """Graceful shutdown — close async clients."""
        await self.qdrant.close()
        logger.info("SovereignMCAgent shutdown complete")


# ============================================================================
# Convenience Factory
# ============================================================================

async def create_sovereign_mc() -> SovereignMCAgent:
    """
    Factory function: create and initialize a SovereignMCAgent.
    Loads context and ensures Qdrant collection exists.

    Usage:
        agent = await create_sovereign_mc()
        status = await agent.get_project_status()
    """
    agent = SovereignMCAgent()
    await agent.load_context()
    return agent


# ============================================================================
# CLI Entry Point (for testing)
# ============================================================================

if __name__ == "__main__":
    async def demo():
        print("🏛️ Sovereign MC Agent — Demo Mode (v1.1.0)")
        agent = await create_sovereign_mc()

        print("\n📊 Project Status:")
        status = await agent.get_project_status()
        print(json.dumps(status, indent=2, default=str))

        print("\n💾 Generating Status Report...")
        await agent.write_status_report()
        print("Report written to mc-oversight/initiative-status-dashboard.md")

        print("\n🔍 Testing semantic recall...")
        results = await agent.recall_decisions("AnyIO TaskGroup concurrent operations")
        print(f"Recalled {len(results)} past decisions")

        await agent.shutdown()

    # AnyIO-compliant entry point (NOT asyncio.run)
    anyio.run(demo)
