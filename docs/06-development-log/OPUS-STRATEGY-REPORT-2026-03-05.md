# Opus Strategy Report: Metropolis v6 Refinement & RAG Enhancement

**Date**: 2026-03-05
**Author**: Opus (Antigravity Claude Opus 4.6)
**Verification Key**: `OMEGA-METROPOLIS-V6-FINAL`
**Scope**: Full system audit, dispatcher refactoring, roadmap refinement, sovereignty check, RAG/memory enhancement

---

## Executive Summary

The Omega Stack Metropolis v6 is architecturally ambitious and well-conceived. However, this audit has uncovered **3 critical failures**, **3 high-severity issues**, and **4 medium-severity improvements** that must be addressed before any production or community release. The most significant finding is that the Maat/Lilith balance system -- a core philosophical component -- is non-functional due to a missing entity file.

---

## 1. Dispatcher Refactoring: Universal Dispatcher Architecture

### 1.1 Current State Analysis

Four dispatcher scripts (`scripts/xnai-{gemini,opencode,copilot,cline}-dispatcher.sh`) share ~80% structural overlap:

| Shared Pattern | Lines Duplicated | Divergence |
|---|---|---|
| Domain mapping (`--arch=1..--test=8`) | ~10 lines x 3 scripts | Gemini uses YAML; others hardcode |
| Instance root definition | 1 line x 4 scripts | Identical |
| Argument parsing | ~10 lines x 4 scripts | Nearly identical |
| Directory creation | 1-3 lines x 4 scripts | Path suffixes differ |
| Routing echo message | 1 line x 4 scripts | Identical format |

### 1.2 Critical Bug: Undefined `$FINAL_KEY`

**File**: `scripts/xnai-gemini-dispatcher.sh:65`
**Issue**: `export GEMINI_API_KEY="$FINAL_KEY"` references a variable that is never defined. The rotation logic section (line 61) contains only a comment stub: `# ... (Rotation logic remains) ...`
**Impact**: Every Gemini dispatch either fails with an empty API key or falls back to whatever `GEMINI_API_KEY` was in the `.env`, bypassing the rotation system entirely.

### 1.3 Implementation Manual: Universal Dispatcher

#### Step 1: Create the shared domain resolver

**File to create**: `scripts/xnai-resolve-domain.sh`
**Token estimate**: ~30 lines
**Purpose**: Single source of truth for domain-to-instance mapping

```bash
#!/bin/bash
# xnai-resolve-domain.sh - Canonical domain resolver
# Sources: config/metropolis-domains.yaml
# Output: Sets INSTANCE_ID and DOMAIN_NAME variables

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOMAIN_CONFIG="${PROJECT_ROOT}/config/metropolis-domains.yaml"
INSTANCE_ROOT="/tmp/xnai-instances"

resolve_domain() {
    local flag="$1"
    INSTANCE_ID=1
    DOMAIN_NAME="Default (Arch)"

    if [[ "$flag" =~ ^--instance-([1-8])$ ]]; then
        INSTANCE_ID="${BASH_REMATCH[1]}"
        DOMAIN_NAME="Direct (Instance $INSTANCE_ID)"
        return 0
    elif [[ "$flag" =~ ^--([a-zA-Z0-9_-]+)$ ]]; then
        local domain="${BASH_REMATCH[1]}"
        if [[ -f "$DOMAIN_CONFIG" ]]; then
            INSTANCE_ID=$(python3 -c "
import yaml
data = yaml.safe_load(open('$DOMAIN_CONFIG'))
d = data.get('domains', {}).get('$domain', {})
print(d.get('id', ''))
" 2>/dev/null)
            if [[ -n "$INSTANCE_ID" ]]; then
                DOMAIN_NAME="$domain"
                return 0
            fi
        fi
        # Fallback to hardcoded map
        declare -A _FALLBACK
        _FALLBACK[arch]=1; _FALLBACK[api]=2; _FALLBACK[ui]=3; _FALLBACK[voice]=4
        _FALLBACK[data]=5; _FALLBACK[ops]=6; _FALLBACK[research]=7; _FALLBACK[test]=8
        if [[ -n "${_FALLBACK[$domain]:-}" ]]; then
            INSTANCE_ID="${_FALLBACK[$domain]}"
            DOMAIN_NAME="$domain"
            return 0
        fi
    fi
    return 1
}
```

#### Step 2: Create per-tool configuration files

**Directory**: `scripts/dispatcher.d/`
**Files**: One `.conf` per tool

Example `scripts/dispatcher.d/gemini.conf`:
```bash
TOOL_NAME="gemini"
TOOL_BINARY="${TOOL_BINARY_OVERRIDE:-$(command -v gemini || echo "$HOME/.nvm/versions/node/v25.3.0/bin/gemini")}"
ISOLATION_VARS=(
    "GEMINI_CLI_HOME=${INSTANCE_ROOT}/instance-${INSTANCE_ID}/gemini-cli"
)
PRE_HOOKS=("inject_soul" "symlink_mcp" "set_api_key")
POST_HOOKS=()
```

Example `scripts/dispatcher.d/opencode.conf`:
```bash
TOOL_NAME="opencode"
TOOL_BINARY="${TOOL_BINARY_OVERRIDE:-$(command -v opencode)}"
ISOLATION_VARS=(
    "XDG_DATA_HOME=${INSTANCE_ROOT}/instance-${INSTANCE_ID}/opencode/.local/share"
    "XDG_CONFIG_HOME=${INSTANCE_ROOT}/instance-${INSTANCE_ID}/opencode"
    "OPENCODE_CONFIG=${INSTANCE_ROOT}/instance-${INSTANCE_ID}/opencode/opencode.json"
)
PRE_HOOKS=()
POST_HOOKS=("pulse_filter")
```

#### Step 3: Create the Universal Dispatcher

**File to create**: `scripts/xnai-dispatcher.sh`
**Token estimate**: ~120 lines
**Purpose**: Single entry point for all tool dispatching

The dispatcher should:
1. Detect tool name from `$1` or from `$0` basename (for backward-compatible symlinks)
2. Source `xnai-resolve-domain.sh` and resolve the domain from `$2`
3. Source `dispatcher.d/<tool>.conf` for tool-specific configuration
4. Execute pre-hooks (soul injection, MCP symlink, API key rotation)
5. Set isolation environment variables
6. Execute the tool binary
7. Execute post-hooks (pulse filtering)

#### Step 4: Create backward-compatible symlinks

```bash
cd scripts/
ln -sf xnai-dispatcher.sh xnai-gemini-dispatcher.sh
ln -sf xnai-dispatcher.sh xnai-opencode-dispatcher.sh
ln -sf xnai-dispatcher.sh xnai-copilot-dispatcher.sh
ln -sf xnai-dispatcher.sh xnai-cline-dispatcher.sh
```

#### Step 5: Update metropolis-broker.py

Replace hardcoded dispatcher paths with the universal dispatcher:
```python
EXPERT_MAP = {
    f"expert:{domain}:prime": [DISPATCHER_PATH, f"--{domain}"]
    for domain in ["architect", "api", "ui", "voice", "data", "ops", "research", "test"]
}
```

### 1.4 Agent Implementation Instructions

**Assigned to**: Any Level 2 agent (OpenCode/Cline preferred)
**Estimated tokens**: ~500 lines of shell + ~50 lines of config
**Prerequisites**: `config/metropolis-domains.yaml` must exist (confirmed: it does)
**Verification**: Run `make metropolis-test` after implementation

---

## 2. Roadmap Strategy Refinement: Latency-Free Implementation

### 2.1 Gap Analysis

| Roadmap Component | Current Status | Gap Assessment |
|---|---|---|
| Prime Council (BFT) | Not implemented | **Defer** -- single-machine BFT adds latency with zero benefit |
| Agent Bus (NATS+Redis) | Redis Streams only | **Keep Redis only** -- sufficient for current scale |
| Telemetry Sentry (Prom/Grafana) | JSON file polling | **Upgrade incrementally** -- add Prometheus exporter to broker |

### 2.2 Revised Roadmap (No Latency Spikes)

#### Phase 1: Fix What's Broken (Week 1) -- HIGH PRIORITY

| Task | Description | Owner | Tokens |
|---|---|---|---|
| P1.1 | Fix `$FINAL_KEY` in Gemini dispatcher (or implement rotation) | Agent | ~50 lines |
| P1.2 | Create `entities/maat.json` | Opus (done) | 18 lines |
| P1.3 | Fix broker target filtering (`fetch_tasks` consumer filter) | Agent | ~30 lines |
| P1.4 | Complete `EXPERT_MAP` in broker (all 8 domains x 2 levels) | Agent | ~40 lines |
| P1.5 | Convert `subprocess.run` to `anyio.run_process` in broker | Agent | ~60 lines |

#### Phase 2: Consolidate Dispatchers (Week 2)

| Task | Description | Owner | Tokens |
|---|---|---|---|
| P2.1 | Create `xnai-resolve-domain.sh` | Agent | ~30 lines |
| P2.2 | Create `scripts/dispatcher.d/*.conf` (4 files) | Agent | ~40 lines |
| P2.3 | Create `xnai-dispatcher.sh` universal dispatcher | Agent | ~120 lines |
| P2.4 | Create symlinks for backward compat | Agent | 4 commands |
| P2.5 | Update broker to use universal dispatcher | Agent | ~20 lines |

#### Phase 3: Observability Upgrade (Week 3-4)

| Task | Description | Owner | Tokens |
|---|---|---|---|
| P3.1 | Add Prometheus client to broker (counter/histogram metrics) | Agent | ~80 lines |
| P3.2 | Create `infra/prometheus/metropolis.yml` scrape config | Agent | ~30 lines |
| P3.3 | Replace `dashboard/index.html` JSON polling with Prometheus queries | Agent | ~100 lines |
| P3.4 | Add Grafana dashboard JSON template for Metropolis metrics | Agent | ~200 lines |

#### Phase 4: Soul Evolution Fix (Week 4)

| Task | Description | Owner | Tokens |
|---|---|---|---|
| P4.1 | Implement actual reflection in `expert-soul-reflector.py` (use Level 2 model) | Agent | ~100 lines |
| P4.2 | Test `soul-evolution-engine.py` with both Maat and Lilith entities | Agent | Manual test |
| P4.3 | Add `make metropolis-reflect` target to Makefile | Agent | ~5 lines |

### 2.3 What NOT to Implement

| Component | Reason |
|---|---|
| **BFT Consensus** | Single-machine deployment. Redis Streams with consumer groups already provides ordered, durable task processing. BFT adds 15-50ms per state transition with zero fault-tolerance benefit on one host. |
| **NATS JetStream** | Double-write complexity. Redis Streams handles the current throughput. Add NATS only if you scale to multiple physical machines. |
| **Merkle Trees / Ed25519 signatures** | Cryptographic verification is for untrusted networks. All agents run locally with the same user. This is overhead without security benefit. |

---

## 3. RAG & Memory System Enhancement Recommendations

### 3.1 Current RAG Architecture Assessment

The current RAG system uses:
- **Vector DB**: Qdrant v1.13.1 with Qwen3-0.6B-Q6_K embeddings
- **Search**: Hybrid semantic/lexical via FastAPI (`xnai-rag` MCP server)
- **Harvesting**: `harvest-expert-data.sh` ingests from all 8 domain instances
- **Speculative Search**: 128d -> 768d -> 4096d progressive embedding refinement

### 3.2 Identified RAG Gaps

1. **No cross-domain knowledge sharing**: Each domain's expert soul evolves independently. The `shared_soul.md` mechanism exists in the harvester but no file is ever created or written.

2. **Harvester is offline-only**: `harvest-expert-data.sh` runs as a batch job. There is no real-time ingestion triggered by session completion.

3. **No embedding model versioning**: If the embedding model changes, all existing vectors become invalid. No migration path exists.

4. **Memory Bank lacks structured recall**: The `memory_bank/` directory contains flat markdown files. The `BLOCKS.yaml` schema defines tiers (core/recall/archival/progress) but no automated promotion/demotion between tiers exists.

### 3.3 Enhancement Recommendations

#### Enhancement 1: Real-Time Session Harvesting via Agent Bus

**Current**: `harvest-expert-data.sh` is a batch script run manually.
**Proposed**: When a domain expert session completes, the dispatcher's post-hook publishes a `session_complete` event to the Agent Bus. A new `HarvestListener` (similar to `GapListener` in `agent_bus.py:90`) picks it up and triggers real-time ingestion.

```python
class HarvestListener(AgentBusClient):
    """Listens for session_complete events and triggers RAG ingestion."""
    
    async def start_listening(self):
        while True:
            tasks = await self.fetch_tasks(count=5)
            for task in tasks:
                if task["type"] == "session_complete":
                    domain_id = task["payload"]["domain_id"]
                    await self._ingest_session(domain_id)
                    await self.acknowledge_task(task["id"])
            await anyio.sleep(1)
    
    async def _ingest_session(self, domain_id: int):
        # Ingest Gemini history
        # Ingest OpenCode history
        # Ingest shared_soul.md
        pass
```

**Implementation path**: Extend `harvest-expert-data.sh` functionality into Python, integrate with AgentBusClient.

#### Enhancement 2: Cross-Domain Knowledge Graph

**Current**: Domains are fully isolated. No knowledge flows between Instance 1 (Architect) and Instance 2 (API).
**Proposed**: Add a `shared_knowledge/` directory at `INSTANCE_ROOT/shared_knowledge/` with domain-tagged markdown files. When one domain learns a pattern, it publishes a `knowledge_share` event. The Gnosis Engine indexes it with domain-of-origin metadata, making it queryable by all domains.

**Implementation**: Add a `knowledge_share` tool to the `xnai-agentbus` MCP server. Add `domain_origin` and `domain_relevance` fields to the Qdrant point payload.

#### Enhancement 3: Memory Bank Tier Automation

**Current**: `memory_bank/BLOCKS.yaml` defines tiers but no automation exists.
**Proposed**: Implement a `memory-bank-curator.py` script that:
1. Promotes frequently-accessed recall-tier documents to core tier
2. Demotes stale core-tier documents to archival tier
3. Compresses archival-tier documents into summary embeddings
4. Runs via `make memory-curate` or as a post-session hook

**Metrics for promotion/demotion**:
- Access frequency (tracked via MCP tool usage logs)
- Recency (last access timestamp)
- Relevance score (from RAG query hit counts)

#### Enhancement 4: Embedding Version Migration

**Current**: No versioning on embeddings.
**Proposed**: Add a `embedding_model_version` field to all Qdrant collections. When the model changes, run a migration that:
1. Creates a new collection with the new model version
2. Re-embeds all documents with the new model
3. Swaps the collection alias atomically
4. Deletes the old collection after verification

This can be implemented as a `make rag-migrate-embeddings MODEL=<new_model>` target.

#### Enhancement 5: Speculative Search with Confidence Gating

**Current**: The speculative search (128d -> 768d -> 4096d) is described but may not gate on confidence.
**Proposed**: Add confidence thresholds at each refinement level:
- If 128d search returns results with score > 0.85, return immediately (sub-millisecond)
- If score 0.60-0.85, escalate to 768d refinement
- If score < 0.60, escalate to full 4096d search
- If 4096d score < 0.40, trigger a `knowledge_gap` event on the Agent Bus

This creates a virtuous cycle: gaps detected -> research agent triggered -> knowledge ingested -> future queries succeed at lower dimensions.

---

## 4. Tool Recommendations: Voice & Data Domains

### 4.1 whisper.cpp MCP Server (Voice Domain - Instance 4)

**Type**: New custom MCP server
**Purpose**: Torch-free speech-to-text using whisper.cpp (GGML/GGUF)
**Sovereignty**: 100% local inference, no cloud dependency

**MCP Server Specification**:
```
mcp-servers/xnai-whisper/
  server.py      # FastMCP server
  pyproject.toml  # Dependencies: fastmcp, subprocess
```

**Tool**: `transcribe(audio_path: str, language: str = "en", model: str = "base.en") -> str`
**Model**: `ggml-base.en.bin` (141MB) -- real-time on Ryzen 5700U CPU

### 4.2 Qdrant MCP Server (Data Domain - Instance 5)

**Type**: Community MCP server (`mcp-server-qdrant`)
**Purpose**: Direct vector DB management bypassing the RAG API layer
**Sovereignty**: Local Qdrant instance at `localhost:6333`

**Why not just use xnai-rag?**: The existing `xnai-rag` server proxies through FastAPI, adding latency and limiting operations to search only. The Data domain expert needs collection management (create, delete, alias), point-level CRUD, and snapshot/backup capabilities.

### 4.3 Piper TTS Local Server (Voice Domain - Instance 4)

**Type**: New custom MCP server
**Purpose**: Torch-free text-to-speech using Piper (ONNX Runtime)
**Sovereignty**: 100% local, ONNX-native (no PyTorch)

**MCP Server Specification**:
```
mcp-servers/xnai-piper/
  server.py      # FastMCP server
  pyproject.toml  # Dependencies: fastmcp, subprocess
```

**Tool**: `synthesize(text: str, voice: str = "en_US-amy-medium", output_format: str = "wav") -> str`
**Models**: Pre-trained `.onnx` voices (20-80MB each)

---

## 5. Sovereignty Check Results

### 5.1 Finding Matrix

| # | Finding | Severity | Status |
|---|---|---|---|
| S1 | `entities/maat.json` missing | **CRITICAL** | Fixed in this session |
| S2 | `torch>=2.0.0` in `research_env/.../requirements.txt` | Medium | Requires agent fix |
| S3 | `activeContext.md` falsely claims `maat.json` created | Medium | Fixed in this session |
| S4 | Expert soul reflector is a stub (boilerplate text) | High | Requires agent fix |
| S5 | Hardcoded `/home/arcana-novai/` paths in 6+ files | Medium | Requires agent fix |
| S6 | Broker target filtering prevents task matching | **CRITICAL** | Requires agent fix |
| S7 | `$FINAL_KEY` undefined in Gemini dispatcher | **CRITICAL** | Requires agent fix |

### 5.2 Torch Violation Details

**File**: `research_env/research-environment/jupyterlab/requirements.txt:44`
**Line**: `torch>=2.0.0  # For local model inference`

**Fix**: Replace with:
```
onnxruntime>=1.17.0  # For local model inference (Torch-free)
llama-cpp-python>=0.2.0  # For GGUF model inference
```

### 5.3 Hardcoded Path Inventory

Files containing `/home/arcana-novai/`:
1. `scripts/xnai-gemini-dispatcher.sh` (lines 38, 90)
2. `scripts/xnai-cline-dispatcher.sh` (line 44)
3. `scripts/soul-evolution-engine.py` (line 20)
4. `scripts/expert-soul-reflector.py` (line 43)
5. `scripts/metropolis-broker.py` (lines 14-17)

**Fix**: Replace all with `$HOME` or `$(dirname "$0")/..` relative paths.

---

## 6. Complete Finding Registry

| # | Category | Finding | Severity | Estimated Fix |
|---|---|---|---|---|
| 1 | Dispatcher | 4 scripts with massive duplication | Medium | ~200 lines (Universal Dispatcher) |
| 2 | Dispatcher | `$FINAL_KEY` undefined in Gemini dispatcher | **Critical** | ~20 lines |
| 3 | Dispatcher | Hardcoded binary/home paths | Medium | ~30 sed replacements |
| 4 | Broker | `subprocess.run` blocks entire broker | High | ~60 lines (anyio.run_process) |
| 5 | Broker | EXPERT_MAP incomplete (4/16 entries) | High | ~40 lines |
| 6 | Broker | Target filtering prevents task matching | **Critical** | ~30 lines |
| 7 | Roadmap | BFT consensus on single machine | Medium | Remove from roadmap |
| 8 | Sovereignty | `entities/maat.json` missing | **Critical** | 18 lines (done) |
| 9 | Sovereignty | `torch>=2.0.0` in research env | Medium | 2-line replacement |
| 10 | Soul | Reflector is a stub, not functional | High | ~100 lines |
| 11 | RAG | No real-time session harvesting | Medium | ~150 lines |
| 12 | RAG | No cross-domain knowledge sharing | Medium | ~200 lines |
| 13 | RAG | No embedding version migration | Low | ~100 lines |
| 14 | Memory | No tier promotion/demotion automation | Medium | ~150 lines |

---

**Coordination Key**: `OMEGA-METROPOLIS-V6-FINAL`
**Next**: See `OPUS-AGENT-HANDOFF-2026-03-05.md` for execution plan
**Research**: See `OPUS-RESEARCH-BRIEF-2026-03-05.md` for deep-dive topics
