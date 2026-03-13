# Expert Knowledge: Multi-Agent Resource Limits
## Phase 5 Discovery - Ryzen 7 5700U

### 1. Memory Audit (2026-02-15)
- **Total RAM**: 6.6GB (6902MB)
- **Base OS + Background**: ~1.5GB
- **Core Containers (Idle)**: ~250MB
- **Available Headroom**: ~4.8GB

### 2. Service-Specific Quotas (Proposed)
| Service | Hard Limit | Soft Limit | Notes |
|---------|------------|------------|-------|
| `rag_api` | 4.5GB | 3.5GB | Triggers T3 degradation at soft limit |
| `chainlit_ui` | 1GB | 500MB | |
| `consul`/`redis` | 256MB | 128MB | |
| `mkdocs`/`crawler` | 256MB | 128MB | |
| **Agent CLI** | 500MB | 256MB | Gemini/Cline/Copilot overhead |

### 3. OOM Strategy
- **zRAM Priority**: Ensure agents are swapped to zRAM (lz4) before the RAG model is touched.
- **Degradation**: If `MemAvailable` < 500MB, all non-essential agents must pause their task groups.
