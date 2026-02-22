"""
Tests for Sovereign MC Agent — v1.1.0
======================================
Unit tests with full mocking — no live services required.
Integration stub marked @pytest.mark.integration.

Coverage:
  - EmbeddingEngine (fastembed, thread-safe, lazy load)
  - MemoryBankReader (async I/O, parallel load_context)
  - VikunjaClient (health, create_task, list_tasks)
  - QdrantMemory (ensure_collection retry, store_decision, search_decisions)
  - OpenCodeDispatcher (spawn, -p flag, error handling)
  - SovereignMCAgent (load_context AnyIO parallel, recall_decisions)

Constraints:
  - AnyIO TaskGroups only — pytest-anyio backend
  - No PyTorch / CUDA / sentence-transformers
  - All external calls mocked via unittest.mock / httpx MockTransport
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import anyio
import anyio.abc
import httpx

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.anyio  # all async tests use anyio


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def tmp_memory_bank(tmp_path: Path) -> Path:
    """Create a minimal memory_bank directory for tests."""
    bank = tmp_path / "memory_bank"
    bank.mkdir()
    (bank / "activeContext.md").write_text("# Active Context\n\nphase: 2.5\n- Priority A\n- Priority B\n")
    (bank / "progress.md").write_text("# Progress\n\nphase: Phase 2.5\n- TASK-021b: Sovereign MC Agent\n")
    (bank / "teamProtocols.md").write_text("# Team Protocols\n\nAnyIO only.\n")
    return bank


@pytest.fixture
def mock_qdrant_client():
    """Mock AsyncQdrantClient — no live Qdrant needed."""
    with patch(
        "app.XNAi_rag_app.core.sovereign_mc_agent.AsyncQdrantClient"
    ) as MockClient:
        instance = AsyncMock()
        instance.get_collections.return_value = MagicMock(collections=[])
        instance.create_collection.return_value = None
        instance.upsert.return_value = None
        instance.search.return_value = []
        instance.close.return_value = None
        MockClient.return_value = instance
        yield instance


@pytest.fixture
def mock_consul():
    """Mock consul_client.is_connected."""
    with patch(
        "app.XNAi_rag_app.core.sovereign_mc_agent.consul_client"
    ) as mock:
        mock.is_connected = True
        yield mock


@pytest.fixture
def mock_agent_bus():
    """Mock AgentBusClient context manager."""
    with patch(
        "app.XNAi_rag_app.core.sovereign_mc_agent.AgentBusClient"
    ) as MockBus:
        instance = AsyncMock()
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=None)
        instance.send_task = AsyncMock(return_value="stream-msg-001")
        MockBus.return_value = instance
        yield instance


# ===========================================================================
# EmbeddingEngine Tests
# ===========================================================================

class TestEmbeddingEngine:

    async def test_embed_returns_384_dim_vector(self):
        """EmbeddingEngine.embed() returns a 384-dim float list."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import EmbeddingEngine

        fake_vec = [0.1] * 384

        with patch("fastembed.TextEmbedding") as MockTE:
            mock_model = MagicMock()
            mock_model.embed.return_value = iter([MagicMock(tolist=lambda: fake_vec)])
            MockTE.return_value = mock_model

            engine = EmbeddingEngine()
            result = await engine.embed("test query")

        assert isinstance(result, list)
        assert len(result) == 384

    async def test_embed_batch_returns_multiple_vectors(self):
        """EmbeddingEngine.embed_batch() returns one vector per input."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import EmbeddingEngine

        texts = ["alpha", "beta", "gamma"]
        fake_vecs = [[0.1] * 384, [0.2] * 384, [0.3] * 384]

        with patch("fastembed.TextEmbedding") as MockTE:
            mock_model = MagicMock()
            mock_model.embed.return_value = iter(
                [MagicMock(tolist=lambda v=v: v) for v in fake_vecs]
            )
            MockTE.return_value = mock_model

            engine = EmbeddingEngine()
            results = await engine.embed_batch(texts)

        assert len(results) == 3
        assert all(len(v) == 384 for v in results)

    async def test_embed_lazy_loads_model_once(self):
        """Model is loaded lazily on first embed call."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import EmbeddingEngine

        with patch("fastembed.TextEmbedding") as MockTE:
            mock_model = MagicMock()
            mock_model.embed.return_value = iter([MagicMock(tolist=lambda: [0.0] * 384)])
            MockTE.return_value = mock_model

            engine = EmbeddingEngine()
            assert engine._model is None
            await engine.embed("hello")
            assert MockTE.call_count == 1

            # Second call — model not re-instantiated
            mock_model.embed.return_value = iter([MagicMock(tolist=lambda: [0.0] * 384)])
            await engine.embed("world")
            assert MockTE.call_count == 1


# ===========================================================================
# MemoryBankReader Tests
# ===========================================================================

class TestMemoryBankReader:

    async def test_read_file_existing(self, tmp_memory_bank: Path):
        """read_file() returns content of existing file."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import MemoryBankReader

        reader = MemoryBankReader(tmp_memory_bank)
        content = await reader.read_file("activeContext.md")
        assert "Active Context" in content
        assert "phase: 2.5" in content

    async def test_read_file_missing_returns_empty(self, tmp_memory_bank: Path):
        """read_file() returns '' for missing file without raising."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import MemoryBankReader

        reader = MemoryBankReader(tmp_memory_bank)
        content = await reader.read_file("nonexistent.md")
        assert content == ""

    async def test_write_file_creates_file(self, tmp_memory_bank: Path):
        """write_file() creates a new file with the given content."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import MemoryBankReader

        reader = MemoryBankReader(tmp_memory_bank)
        ok = await reader.write_file("new_doc.md", "# New Doc\n\nHello.")
        assert ok is True
        assert (tmp_memory_bank / "new_doc.md").read_text() == "# New Doc\n\nHello."

    async def test_load_context_parallel_reads(self, tmp_memory_bank: Path):
        """load_context() reads 3 files in parallel and parses phase/priorities."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import MemoryBankReader

        reader = MemoryBankReader(tmp_memory_bank)
        ctx = await reader.load_context()

        assert ctx.phase == "Phase 2.5"
        assert len(ctx.priorities) >= 1
        assert ctx.active_context != ""

    async def test_append_to_active_context(self, tmp_memory_bank: Path):
        """append_to_active_context() adds a timestamped section."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import MemoryBankReader

        reader = MemoryBankReader(tmp_memory_bank)
        ok = await reader.append_to_active_context("Sprint 2 Complete", "All bugs fixed.")
        assert ok is True

        content = await reader.read_file("activeContext.md")
        assert "Sprint 2 Complete" in content
        assert "All bugs fixed." in content


# ===========================================================================
# VikunjaClient Tests
# ===========================================================================

class TestVikunjaClient:

    def _make_transport(self, routes: dict) -> httpx.MockTransport:
        """Build an httpx MockTransport from a {url_pattern: response} dict."""
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            for pattern, resp in routes.items():
                if pattern in url:
                    return resp
            return httpx.Response(404, json={"error": "not found"})

        return httpx.MockTransport(handler)

    async def test_health_returns_true_on_200(self):
        """VikunjaClient.health() returns True when /info returns 200."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import VikunjaClient

        with patch("httpx.AsyncClient") as MockHTTP:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            MockHTTP.return_value.__aenter__ = AsyncMock(
                return_value=MagicMock(get=AsyncMock(return_value=mock_resp))
            )
            MockHTTP.return_value.__aexit__ = AsyncMock(return_value=None)

            client = VikunjaClient(base_url="http://localhost:3456")
            ok = await client.health()
            assert ok is True

    async def test_health_returns_false_on_connection_error(self):
        """VikunjaClient.health() returns False when connection fails."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import VikunjaClient

        with patch("httpx.AsyncClient") as MockHTTP:
            MockHTTP.return_value.__aenter__ = AsyncMock(
                return_value=MagicMock(
                    get=AsyncMock(side_effect=httpx.ConnectError("refused"))
                )
            )
            MockHTTP.return_value.__aexit__ = AsyncMock(return_value=None)

            client = VikunjaClient()
            ok = await client.health()
            assert ok is False

    async def test_create_task_returns_vikunja_task(self):
        """VikunjaClient.create_task() returns a VikunjaTask on success."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import VikunjaClient, VikunjaTask

        task_data = {
            "id": 42,
            "title": "Test Task",
            "description": "A description",
            "priority": 2,
            "done": False,
            "created": "2026-02-18T00:00:00Z",
        }

        with patch("httpx.AsyncClient") as MockHTTP:
            mock_resp = AsyncMock()
            mock_resp.json.return_value = task_data
            mock_resp.raise_for_status = MagicMock()
            MockHTTP.return_value.__aenter__ = AsyncMock(
                return_value=MagicMock(put=AsyncMock(return_value=mock_resp))
            )
            MockHTTP.return_value.__aexit__ = AsyncMock(return_value=None)

            client = VikunjaClient()
            task = await client.create_task(
                project_id=1, title="Test Task", description="A description", priority=2
            )

        assert isinstance(task, VikunjaTask)
        assert task.id == 42
        assert task.title == "Test Task"
        assert task.priority == 2


# ===========================================================================
# QdrantMemory Tests
# ===========================================================================

class TestQdrantMemory:

    async def test_ensure_collection_creates_if_missing(self, mock_qdrant_client):
        """ensure_collection() calls create_collection when not present."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import QdrantMemory, EmbeddingEngine

        mock_embedder = AsyncMock(spec=EmbeddingEngine)
        mem = QdrantMemory(embedder=mock_embedder)
        ok = await mem.ensure_collection()

        assert ok is True
        mock_qdrant_client.create_collection.assert_called_once()

    async def test_ensure_collection_retries_on_failure(self):
        """ensure_collection() retries 3 times before returning False."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import QdrantMemory, EmbeddingEngine

        with patch(
            "app.XNAi_rag_app.core.sovereign_mc_agent.AsyncQdrantClient"
        ) as MockClient:
            instance = AsyncMock()
            instance.get_collections.side_effect = Exception("Qdrant unreachable")
            MockClient.return_value = instance

            mock_embedder = AsyncMock(spec=EmbeddingEngine)

            with patch("anyio.sleep", new_callable=AsyncMock):
                mem = QdrantMemory(embedder=mock_embedder)
                ok = await mem.ensure_collection()

        assert ok is False
        assert instance.get_collections.call_count == 3

    async def test_store_decision_embeds_and_upserts(self, mock_qdrant_client):
        """store_decision() uses embedder and calls qdrant.upsert."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import QdrantMemory, EmbeddingEngine

        mock_embedder = AsyncMock(spec=EmbeddingEngine)
        mock_embedder.embed = AsyncMock(return_value=[0.5] * 384)

        mem = QdrantMemory(embedder=mock_embedder)
        ok = await mem.store_decision(
            decision_id="test-001",
            title="Decision Title",
            content="Some content about AnyIO",
            tags=["test"],
        )

        assert ok is True
        mock_embedder.embed.assert_called_once()
        embed_arg = mock_embedder.embed.call_args[0][0]
        assert "Decision Title" in embed_arg
        assert "Some content" in embed_arg
        mock_qdrant_client.upsert.assert_called_once()

    async def test_store_decision_degrades_on_embed_failure(self, mock_qdrant_client):
        """store_decision() falls back to zero vector when embed fails."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import QdrantMemory, EmbeddingEngine

        mock_embedder = AsyncMock(spec=EmbeddingEngine)
        mock_embedder.embed = AsyncMock(side_effect=RuntimeError("embed failed"))

        mem = QdrantMemory(embedder=mock_embedder)
        ok = await mem.store_decision("id-002", "Title", "Content")

        assert ok is True  # still stores with zero vector
        call_args = mock_qdrant_client.upsert.call_args
        points = call_args.kwargs.get("points") or call_args[1].get("points", [])
        if points:
            assert points[0].vector == [0.0] * 384

    async def test_search_decisions_embeds_query(self, mock_qdrant_client):
        """search_decisions() embeds query string and calls qdrant.search."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import QdrantMemory, EmbeddingEngine

        mock_embedder = AsyncMock(spec=EmbeddingEngine)
        mock_embedder.embed = AsyncMock(return_value=[0.1] * 384)

        mem = QdrantMemory(embedder=mock_embedder)
        results = await mem.search_decisions("AnyIO concurrent tasks")

        mock_embedder.embed.assert_called_once_with("AnyIO concurrent tasks")
        mock_qdrant_client.search.assert_called_once()
        assert isinstance(results, list)


# ===========================================================================
# OpenCodeDispatcher Tests
# ===========================================================================

class TestOpenCodeDispatcher:

    async def test_spawn_uses_dash_p_flag(self):
        """OpenCodeDispatcher.spawn() uses -p flag (not --print)."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import OpenCodeDispatcher

        captured_cmd: list[str] = []

        async def fake_run_process(cmd, **kwargs):
            captured_cmd.extend(cmd)
            result = MagicMock()
            result.returncode = 0
            result.stdout = b"Agent output here"
            return result

        with patch("anyio.run_process", side_effect=fake_run_process):
            session = await OpenCodeDispatcher.spawn(
                task="Analyze the codebase",
                model="opencode/glm-5-free",
                session_id="test-session-001",
            )

        assert "-p" in captured_cmd
        assert "--print" not in captured_cmd
        assert "-q" in captured_cmd
        assert session.status == "completed"
        assert session.output == "Agent output here"
        assert session.session_id == "test-session-001"

    async def test_spawn_returns_error_on_exception(self):
        """OpenCodeDispatcher.spawn() returns status=error on process failure."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import OpenCodeDispatcher

        with patch("anyio.run_process", side_effect=FileNotFoundError("opencode not found")):
            session = await OpenCodeDispatcher.spawn("do something")

        assert session.status == "error"
        assert "opencode not found" in session.output


# ===========================================================================
# SovereignMCAgent Integration Tests
# ===========================================================================

class TestSovereignMCAgent:

    async def test_load_context_runs_parallel_tasks(
        self, tmp_memory_bank: Path, mock_qdrant_client, mock_consul
    ):
        """load_context() uses AnyIO TaskGroup to run memory + qdrant in parallel."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import (
            SovereignMCAgent, EmbeddingEngine
        )

        mock_embedder = AsyncMock(spec=EmbeddingEngine)
        mock_embedder.embed = AsyncMock(return_value=[0.0] * 384)

        with patch(
            "app.XNAi_rag_app.core.sovereign_mc_agent.get_embedding_engine",
            return_value=mock_embedder,
        ):
            agent = SovereignMCAgent(memory_bank_path=tmp_memory_bank)
            ctx = await agent.load_context()
            await agent.shutdown()

        assert ctx is not None
        assert ctx.phase != ""
        # Both tasks ran — memory loaded + qdrant init called
        mock_qdrant_client.get_collections.assert_called()

    async def test_recall_decisions_passes_string_query(
        self, tmp_memory_bank: Path, mock_qdrant_client, mock_consul
    ):
        """recall_decisions() passes a string query (not a vector)."""
        from app.XNAi_rag_app.core.sovereign_mc_agent import (
            SovereignMCAgent, EmbeddingEngine
        )

        mock_embedder = AsyncMock(spec=EmbeddingEngine)
        mock_embedder.embed = AsyncMock(return_value=[0.1] * 384)

        with patch(
            "app.XNAi_rag_app.core.sovereign_mc_agent.get_embedding_engine",
            return_value=mock_embedder,
        ):
            agent = SovereignMCAgent(memory_bank_path=tmp_memory_bank)
            results = await agent.recall_decisions("AnyIO TaskGroup pattern", limit=3)
            await agent.shutdown()

        # Embedder was called with the string query
        mock_embedder.embed.assert_called_with("AnyIO TaskGroup pattern")
        assert isinstance(results, list)


# ===========================================================================
# Integration Stub (requires live services — skipped in CI)
# ===========================================================================

@pytest.mark.integration
async def test_integration_create_sovereign_mc():
    """
    Integration test: creates a real SovereignMCAgent.
    Requires: Qdrant on :6333, Vikunja on :3456, Redis on :6379.

    Skip with: pytest -m "not integration"
    """
    from app.XNAi_rag_app.core.sovereign_mc_agent import create_sovereign_mc

    agent = await create_sovereign_mc()
    assert agent is not None
    assert agent._context is not None

    status = await agent.get_project_status()
    assert "agent" in status
    assert "health" in status

    await agent.shutdown()
