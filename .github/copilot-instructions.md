# Repository Copilot Instructions — XNAi Foundation

## Purpose

Provide GitHub Copilot CLI and agents with repository-level guidance so they use project conventions, honor zero-telemetry, and follow model/runtime constraints.

---

## Core Rules

### 1. Zero-Telemetry Mandate
- **NO external API calls** for model inference without explicit user approval
- **NO data transmission** to external servers
- All inference must be local (ONNX, GGUF, CTranslate2)
- If an external API is needed, **ask user first**

### 2. Torch-Free Policy
- **NO PyTorch/Torch/Triton/CUDA** imports
- Use only:
  - ONNX Runtime
  - GGUF (llama-cpp-python with Vulkan)
  - CTranslate2
  - NumPy for numerical operations
- Sentence-transformers requires PyTorch → **AVOID**

### 3. Resource Constraints
- Target: **<6GB RAM**, **<500ms latency**
- Use memory mapping for large files
- Prefer streaming over loading entire files
- Always check memory usage before operations

### 4. Ethical Guardrails
- Follow Ma'at's 42 Ideals
- No harmful, biased, or unethical code
- Respect user privacy and sovereignty
- Document security implications

---

## Architecture

### Infrastructure Layer
```
app/XNAi_rag_app/core/infrastructure/
├── session_manager.py    # Redis + in-memory fallback
└── knowledge_client.py   # Qdrant + FAISS abstraction
```

**Always use these components** for:
- Session persistence: `SessionManager`
- Knowledge retrieval: `KnowledgeClient`

### Voice Module
```
app/XNAi_rag_app/services/voice/
└── voice_module.py       # Chainlit integration adapter
```

**Voice is optional** - controlled by `FEATURE_VOICE` flag

### Knowledge Distillation
```
app/XNAi_rag_app/core/distillation/
├── state.py              # KnowledgeState TypedDict
├── knowledge_distillation.py  # LangGraph StateGraph
├── nodes/                # Pipeline nodes
└── quality/              # Quality scoring
```

---

## Feature Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `FEATURE_VOICE` | `false` | Enable voice responses |
| `FEATURE_REDIS_SESSIONS` | `true` | Redis session persistence |
| `FEATURE_QDRANT` | `true` | Qdrant vector search |
| `FEATURE_LOCAL_FALLBACK` | `true` | Local LLM fallback |

**Always check feature flags** before using optional components.

---

## Coding Standards

### Async Patterns
- Use **AnyIO** for structured concurrency (not asyncio directly)
- Use thread pools for CPU-bound operations
- Never block the event loop

### Error Handling
- **Graceful degradation** - always fall back gracefully
- Log warnings for degraded mode
- Provide user-friendly error messages
- Use circuit breakers for external services

### Import Pattern
```python
# Always use try/except for optional imports
try:
    from optional_package import Something
    OPTIONAL_AVAILABLE = True
except ImportError:
    OPTIONAL_AVAILABLE = False
    Something = None
```

### Type Hints
```python
# Always add type hints
from typing import Optional, Dict, Any, List

async def process(
    data: str,
    options: Optional[Dict[str, Any]] = None,
) -> List[str]:
    ...
```

---

## Memory Bank Protocol

### When to Read
- Start of each session
- Before making architectural decisions
- When context is needed

### When to Update
- After completing significant work
- When strategy changes
- Before context window fills

### Key Files
- `memory_bank/activeContext.md` - Current state
- `memory_bank/progress.md` - Phase status
- `memory_bank/strategies/` - Task queues

---

## Allowed Directories

```
/app                    # Main application code
/memory_bank            # Context persistence
/docs                   # Documentation
/scripts                # Automation scripts
/internal_docs          # Internal documentation
/.github                # GitHub configuration
/expert-knowledge       # Gold-standard docs
```

---

## Testing

### Run Tests
```bash
# Unit tests
pytest tests/

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_session_manager.py
```

### Test Pattern
```python
import pytest

@pytest.mark.asyncio
async def test_feature():
    # Arrange
    config = Config()
    
    # Act
    result = await process(config)
    
    # Assert
    assert result is not None
```

---

## Linting

### Ruff Commands
```bash
# Check code
ruff check .

# Fix issues
ruff check --fix .

# Format code
ruff format .

# Check formatting
ruff format --check .
```

### Type Checking
```bash
mypy app/ --ignore-missing-imports
```

---

## Quick Reference

### Infrastructure Usage
```python
from XNAi_rag_app.core.infrastructure import (
    SessionManager,
    KnowledgeClient,
    create_session_manager,
    create_knowledge_client,
)

# Create session
session = await create_session_manager()

# Create knowledge client
knowledge = await create_knowledge_client()
```

### Voice Module Usage
```python
from XNAi_rag_app.services.voice import (
    VoiceModule,
    VoiceModuleConfig,
)

if os.getenv("FEATURE_VOICE") == "true":
    voice = VoiceModule(VoiceModuleConfig())
    await voice.initialize()
```

---

## Related Documentation

- `memory_bank/activeContext.md` - Current state
- `docs/api/infrastructure-layer.md` - Infrastructure API
- `docs/api/voice_module.md` - Voice module API
- `.gemini/GEMINI.md` - Gemini CLI context
- `.opencode/RULES.md` - OpenCode rules

---

**Last Updated**: 2026-02-22
