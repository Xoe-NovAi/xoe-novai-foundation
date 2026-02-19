# fastembed — ONNX Embedding Guide for XNAi Foundation
**Documented**: 2026-02-18  
**Researcher**: Cline (Claude Opus 4.5)  
**Status**: ✅ Production-ready — replaces zero-vector placeholder

---

## What is fastembed?

`fastembed` is Qdrant's own Python embedding library built on **ONNX Runtime** — zero PyTorch, zero GPU, zero CUDA, zero sentence-transformers. It is the canonical embedding solution for XNAi Foundation's sovereign, offline-first stack.

- **GitHub**: `https://github.com/qdrant/fastembed`
- **PyPI**: `pip install fastembed>=0.4.0`
- **License**: Apache 2.0

---

## Why fastembed for XNAi Foundation?

| Requirement | fastembed | sentence-transformers |
|-------------|-----------|----------------------|
| Zero PyTorch | ✅ ONNX only | ❌ PyTorch required |
| Zero CUDA/Triton | ✅ CPU inference | ❌ GPU default |
| Offline/air-gap | ✅ Models cached locally | ⚠️ Downloads at runtime |
| Ryzen 7 5700U (6.6GB RAM) | ✅ Lightweight | ❌ Model + PyTorch too heavy |
| Zero telemetry | ✅ No beacon | ⚠️ HuggingFace calls |

---

## Installation

```bash
pip install "fastembed>=0.4.0"
```

Add to `requirements-api.in`:

```text
fastembed>=0.4.0
```

---

## Default Model — BAAI/bge-small-en-v1.5

The default model used in XNAi Foundation is `BAAI/bge-small-en-v1.5`:

| Property | Value |
|----------|-------|
| Vector dimension | **384** |
| Model size | ~33MB |
| Inference | CPU ONNX |
| Language | English |
| License | MIT |

This matches the Qdrant collection dimension `MC_VECTOR_DIM = 384`.

---

## Basic Usage (Synchronous)

```python
from fastembed import TextEmbedding

model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Single text
embeddings = list(model.embed(["Hello, world!"]))
vec = embeddings[0].tolist()   # list[float], len=384

# Batch
texts = ["text one", "text two", "text three"]
vecs = [v.tolist() for v in model.embed(texts)]
```

---

## Async-Safe Usage — AnyIO Pattern

fastembed's `TextEmbedding` is **synchronous**. To use it in an async context without blocking the event loop, run it in a thread pool via `anyio.to_thread.run_sync`:

```python
import anyio
from fastembed import TextEmbedding

model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

async def embed_async(text: str) -> list[float]:
    def _sync_embed():
        return list(model.embed([text]))[0].tolist()
    
    return await anyio.to_thread.run_sync(_sync_embed)
```

**Do NOT use** `asyncio.to_thread.run_in_executor` — this violates the AnyIO-only policy.

---

## EmbeddingEngine Class (XNAi Foundation Pattern)

The canonical implementation in `sovereign_mc_agent.py` v1.1.0:

```python
class EmbeddingEngine:
    """
    ONNX-based text embedder using fastembed.
    Thread-safe via anyio.Lock() — safe for concurrent AnyIO TaskGroups.
    Lazy-loads model on first use.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self._model_name = model_name
        self._model = None  # lazy init
        self._lock = anyio.Lock()

    def _load_model(self):
        if self._model is None:
            from fastembed import TextEmbedding
            self._model = TextEmbedding(model_name=self._model_name)
        return self._model

    async def embed(self, text: str) -> list[float]:
        async with self._lock:
            def _run() -> list[float]:
                model = self._load_model()
                return list(model.embed([text]))[0].tolist()
            return await anyio.to_thread.run_sync(_run)
```

Key design decisions:
- **`anyio.Lock()`** prevents concurrent model downloads (lazy init is not thread-safe)
- **Thread pool via `anyio.to_thread.run_sync`** — non-blocking event loop
- **Singleton** via `get_embedding_engine()` — one model load per process
- **Lazy init** — model not loaded until first embed call

---

## Integration with Qdrant

The `QdrantMemory` class in `sovereign_mc_agent.py` v1.1.0 uses EmbeddingEngine to produce real 384-dim vectors:

```python
# Store a decision with real embedding
await mem.store_decision(
    decision_id="decision-001",
    title="AnyIO TaskGroup chosen over asyncio.gather",
    content="AnyIO TaskGroups provide structured concurrency...",
    tags=["architecture", "concurrency"],
)

# Search with a natural language query
results = await mem.search_decisions(
    query="concurrent task execution policy",
    limit=5,
)
```

The embedding is computed automatically: `embed(f"{title}\n\n{content}")`.

---

## Supported Models (ONNX)

| Model | Dim | Size | Notes |
|-------|-----|------|-------|
| `BAAI/bge-small-en-v1.5` | 384 | 33MB | **XNAi default** |
| `BAAI/bge-base-en-v1.5` | 768 | 110MB | Larger, better recall |
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | 22MB | Tiny, good enough |
| `nomic-ai/nomic-embed-text-v1.5` | 768 | 137MB | Long context (8192 tokens) |

To change the model, update `MC_VECTOR_DIM` in `sovereign_mc_agent.py` to match.

---

## Graceful Degradation Pattern

Always wrap embedding calls with fallback to zero vectors — this ensures Qdrant upsert still works even if the model fails to load:

```python
try:
    vec = await embedder.embed(text)
except Exception as e:
    logger.warning(f"Embedding failed: {e} — using zero vector")
    vec = [0.0] * 384  # Store anyway, search won't match well
```

Zero vectors in Qdrant are valid but semantically meaningless. They will rank at the bottom of cosine similarity searches, which is acceptable for degraded-mode operation.

---

## Testing fastembed

When testing code that uses EmbeddingEngine, mock `fastembed.TextEmbedding`:

```python
from unittest.mock import patch, MagicMock, AsyncMock

async def test_embed():
    from sovereign_mc_agent import EmbeddingEngine
    
    fake_vec = [0.1] * 384
    
    with patch("fastembed.TextEmbedding") as MockTE:
        mock_model = MagicMock()
        mock_model.embed.return_value = iter([MagicMock(tolist=lambda: fake_vec)])
        MockTE.return_value = mock_model
        
        engine = EmbeddingEngine()
        result = await engine.embed("test text")
    
    assert len(result) == 384
```

---

## Model Caching (Offline/Air-Gap)

fastembed caches ONNX models locally at:

```
~/.cache/fastembed/models/BAAI/bge-small-en-v1.5/
```

Pre-download for air-gap environments:

```bash
python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"
```

After first download, no network access is required. This supports XNAi Foundation's offline-first requirement.

---

## DO NOT Use

| Package | Reason |
|---------|--------|
| `sentence-transformers` | Requires PyTorch |
| `torch` | PyTorch — banned |
| `transformers` (HuggingFace) | PyTorch dependency |
| `openai.embeddings` | External API — telemetry |
| `cohere.embed` | External API — telemetry |

---

*Documented during XNAi Foundation Sprint 2 — 2026-02-18*  
*See also: `SOVEREIGN-MC-AGENT-SPEC-v1.0.0.md`, `ANTIGRAVITY-AUTH-DISCOVERY-2026-02-18.md`*
