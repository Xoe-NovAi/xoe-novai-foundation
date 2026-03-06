# XNAi Foundation — Knowledge Absorption System Design

## Executive Summary

This document defines the architecture for an automated knowledge absorption system that transforms agent research into structured, searchable knowledge within the XNAi Foundation stack. The system prioritizes quality over quantity, ensuring only distilled, high-value knowledge enters the ecosystem.

## Design Philosophy

### Core Principles

1. **Quality Over Quantity**: Only high-value, distilled knowledge enters the system
2. **Local-First**: Zero external API calls for knowledge processing
3. **Torch-Free**: Uses ONNX, GGUF, fastembed for all AI operations
4. **Observable**: Every knowledge entry has provenance, quality score, and metadata
5. **Reversible**: Knowledge can be expired, updated, or removed

### Quality Gates

```
Raw Research → Extraction → Classification → Quality Scoring → Distillation → Storage
     │              │              │                │                │           │
     └──────────────┴──────────────┴────────────────┴────────────────┴───────────┘
                              REJECTION AT ANY STAGE
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE SOURCES                                    │
│   Agent Research • CLI Sessions • Web Content • Code Analysis • Decisions   │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                      STAGING LAYER (Library/_staging/)                       │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   raw/      │    │  extracted/ │    │  distilled/ │    │  rejected/  │  │
│  │  (incoming) │───▶│  (parsed)   │───▶│  (refined)  │───▶│  (archive)  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │                              │
│         └──────────────────┴──────────────────┘                              │
│                           │                                                  │
│                    7-day TTL                                                  │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────────┐
│                    DISTILLATION ENGINE (LangGraph)                          │
│                                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │  EXTRACT │──▶│CLASSIFY  │──▶│  SCORE   │──▶│DISTILL   │──▶│  STORE   │  │
│  │          │   │          │   │          │   │          │   │          │  │
│  │ - Parse  │   │ - Type   │   │ - Relev. │   │ - Summ.  │   │ - Qdrant │  │
│  │ - Clean  │   │ - Topic  │   │ - Novel  │   │ - Refine │   │ - Memory │  │
│  │ - Chunk  │   │ - Tags   │   │ - Action │   │ - Format │   │ - Index  │  │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘  │
│       │              │              │              │              │         │
│       └──────────────┴──────────────┴──────────────┴──────────────┘         │
│                              │                                               │
│                       QUALITY GATES                                          │
│                    (Reject if score < 0.6)                                   │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────────┐
│                      STORAGE LAYER                                           │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │    Qdrant       │  │  Memory Bank    │  │ Expert-Knowledge│             │
│  │                 │  │                 │  │                 │             │
│  │ xnai_knowledge  │  │ archival/       │  │ research/       │             │
│  │ (searchable)    │  │ (structured)    │  │ (canonical)     │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│           │                    │                    │                       │
│           └────────────────────┴────────────────────┘                       │
│                          │                                                   │
│                   Cross-References                                          │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────────────┐
│                    RETRIEVAL LAYER                                          │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  Semantic Search│  │  Agent Bus      │  │  Vikunja Tasks  │            │
│  │  (RAG API)      │  │  (Coordination) │  │  (Tracking)     │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Staging Layer

**Purpose**: Temporary storage for incoming research before processing.

**Location**: `library/_staging/`

**Structure**:
```
library/_staging/
├── raw/                    # Incoming research (7-day TTL)
│   ├── {source}_{date}_{id}.md
│   └── metadata.json
├── extracted/              # Parsed content (5-day TTL)
│   ├── {source}_{date}_{id}_extracted.json
│   └── chunks/
├── distilled/              # Refined knowledge (3-day TTL)
│   ├── {source}_{date}_{id}_distilled.md
│   └── quality_report.json
└── rejected/               # Rejected content (14-day TTL for audit)
    ├── {source}_{date}_{id}_rejected.md
    └── rejection_reason.json
```

**TTL Policy**:
- Raw: 7 days (automatic cleanup)
- Extracted: 5 days
- Distilled: 3 days
- Rejected: 14 days (for audit and learning)

### 2. Distillation Engine (LangGraph)

**Purpose**: Multi-step workflow for transforming raw research into structured knowledge.

**Implementation**: `app/XNAi_rag_app/core/knowledge_distillation.py`

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class KnowledgeState(TypedDict):
    # Input
    source: str                    # Source identifier
    source_type: str               # "agent_research", "cli_session", "web_content"
    raw_content: str               # Original content
    
    # Processing
    extracted_content: str         # Cleaned content
    chunks: list[dict]             # Chunked content
    classification: dict           # Type, topic, tags
    quality_score: float           # 0.0 - 1.0
    rejection_reason: str          # If rejected
    
    # Distillation
    distilled_content: str         # Final refined content
    summary: str                   # Brief summary
    key_insights: list[str]        # Extracted insights
    action_items: list[str]        # Actionable items
    
    # Metadata
    provenance: dict               # Source tracking
    created_at: str
    processed_at: str
    
    # Storage targets
    storage_targets: Annotated[list[str], operator.add]
    qdrant_ids: Annotated[list[str], operator.add]
    memory_bank_refs: Annotated[list[str], operator.add]

# Node implementations
async def extract_content(state: KnowledgeState) -> dict:
    """Parse and clean raw content."""
    # Remove formatting artifacts
    # Extract structured sections
    # Identify code blocks, tables, lists
    return {"extracted_content": cleaned, "chunks": chunks}

async def classify_content(state: KnowledgeState) -> dict:
    """Classify content type and assign tags."""
    # Use local embedding model (fastembed)
    # Match against taxonomy
    # Assign: type, topic, tags, priority
    return {"classification": classification}

async def score_quality(state: KnowledgeState) -> dict:
    """Calculate quality score."""
    factors = {
        "relevance": 0.0,      # How relevant to XNAi Foundation
        "novelty": 0.0,        # New information vs duplicates
        "actionability": 0.0,  # Can it be acted upon?
        "completeness": 0.0,   # Is information complete?
        "accuracy": 0.0,       # Fact-check confidence
    }
    # Weighted scoring
    score = 0.3*relevance + 0.25*novelty + 0.2*actionability + 0.15*completeness + 0.1*accuracy
    return {"quality_score": score}

async def distill_content(state: KnowledgeState) -> dict:
    """Refine and summarize content."""
    # Extract key insights
    # Generate summary (local LLM)
    # Format for storage
    return {
        "distilled_content": refined,
        "summary": summary,
        "key_insights": insights,
        "action_items": actions
    }

async def store_knowledge(state: KnowledgeState) -> dict:
    """Store in appropriate targets."""
    targets = []
    qdrant_ids = []
    memory_refs = []
    
    # Store in Qdrant
    if state["quality_score"] >= 0.6:
        qdrant_id = await store_in_qdrant(state)
        qdrant_ids.append(qdrant_id)
        targets.append("qdrant")
    
    # Store in memory bank if high quality
    if state["quality_score"] >= 0.8:
        ref = await store_in_memory_bank(state)
        memory_refs.append(ref)
        targets.append("memory_bank")
    
    # Store in expert-knowledge if canonical
    if state["classification"]["type"] == "canonical":
        path = await store_in_expert_knowledge(state)
        targets.append("expert_knowledge")
    
    return {
        "storage_targets": targets,
        "qdrant_ids": qdrant_ids,
        "memory_bank_refs": memory_refs
    }

async def reject_content(state: KnowledgeState) -> dict:
    """Handle rejected content."""
    reason = f"Quality score {state['quality_score']:.2f} below threshold 0.6"
    await archive_rejected(state, reason)
    return {"rejection_reason": reason}

# Graph definition
def build_distillation_graph():
    graph = StateGraph(KnowledgeState)
    
    # Add nodes
    graph.add_node("extract", extract_content)
    graph.add_node("classify", classify_content)
    graph.add_node("score", score_quality)
    graph.add_node("distill", distill_content)
    graph.add_node("store", store_knowledge)
    graph.add_node("reject", reject_content)
    
    # Add edges
    graph.set_entry_point("extract")
    graph.add_edge("extract", "classify")
    graph.add_edge("classify", "score")
    
    # Conditional routing based on quality score
    graph.add_conditional_edges(
        "score",
        lambda state: "distill" if state["quality_score"] >= 0.6 else "reject",
        {"distill": "distill", "reject": "reject"}
    )
    
    graph.add_edge("distill", "store")
    graph.add_edge("store", END)
    graph.add_edge("reject", END)
    
    return graph.compile()
```

### 3. Quality Scoring System

**Purpose**: Ensure only high-quality knowledge enters the system.

**Scoring Factors**:

| Factor | Weight | Description | Calculation |
|--------|--------|-------------|-------------|
| **Relevance** | 30% | How relevant to XNAi Foundation goals | Semantic similarity to core topics |
| **Novelty** | 25% | New information vs existing knowledge | Duplicate detection via Qdrant |
| **Actionability** | 20% | Can it be acted upon? | Presence of actionable items |
| **Completeness** | 15% | Is information complete? | Section coverage analysis |
| **Accuracy** | 10% | Fact-check confidence | Cross-reference validation |

**Quality Thresholds**:

| Score Range | Action | Storage Target |
|-------------|--------|----------------|
| 0.9 - 1.0 | **Gold Standard** | Qdrant + Memory Bank + Expert-Knowledge |
| 0.8 - 0.89 | **High Quality** | Qdrant + Memory Bank |
| 0.7 - 0.79 | **Good Quality** | Qdrant only |
| 0.6 - 0.69 | **Acceptable** | Qdrant only (with expiry) |
| < 0.6 | **Rejected** | Archive for audit |

### 4. Storage Integration

#### Qdrant Collection: `xnai_knowledge`

```python
COLLECTION_CONFIG = {
    "name": "xnai_knowledge",
    "vectors": {
        "size": 768,  # nomic-embed-text-v1.5
        "distance": "Cosine"
    },
    "payload_schema": {
        "source_type": "keyword",
        "topic": "keyword",
        "tags": "keyword[]",
        "quality_score": "float",
        "created_at": "integer",
        "expires_at": "integer",
        "provenance": "object"
    }
}
```

#### Memory Bank Integration

```python
async def store_in_memory_bank(state: KnowledgeState) -> str:
    """Store high-quality knowledge in memory bank."""
    # Determine target file
    if state["classification"]["topic"] == "architecture":
        target = "memory_bank/systemPatterns.md"
    elif state["classification"]["topic"] == "technical":
        target = "memory_bank/techContext.md"
    elif state["classification"]["topic"] == "strategic":
        target = "memory_bank/strategies/{topic}.md"
    else:
        target = "memory_bank/archival/research/{date}_{topic}.md"
    
    # Append distilled content
    await append_to_memory_block(target, state["distilled_content"])
    
    return target
```

#### Expert-Knowledge Integration

```python
async def store_in_expert_knowledge(state: KnowledgeState) -> str:
    """Store canonical knowledge in expert-knowledge directory."""
    # Determine target directory
    topic = state["classification"]["topic"]
    source = state["source_type"]
    
    target_dir = f"expert-knowledge/{topic}/"
    target_file = f"{source}_{date}_{id}.md"
    
    # Write canonical document
    path = Path(target_dir) / target_file
    await write_canonical_doc(path, state["distilled_content"])
    
    return str(path)
```

### 5. Agent Bus Integration

**Purpose**: Coordinate knowledge absorption across multiple agents.

**New Task Types**:

```python
KNOWLEDGE_TASK_TYPES = {
    "knowledge.ingest": "Ingest raw content into staging",
    "knowledge.extract": "Extract and clean content",
    "knowledge.classify": "Classify content type and tags",
    "knowledge.score": "Calculate quality score",
    "knowledge.distill": "Distill and summarize",
    "knowledge.store": "Store in appropriate targets",
    "knowledge.query": "Query knowledge base",
    "knowledge.expire": "Expire old knowledge",
    "knowledge.audit": "Audit knowledge quality"
}
```

**Task Routing**:

```python
async def route_knowledge_task(task_type: str, payload: dict):
    """Route knowledge tasks via agent bus."""
    if task_type.startswith("knowledge."):
        target_did = "knowledge-absorption-agent"
    else:
        target_did = "default-agent"
    
    await agent_bus.send_task(
        target_did=target_did,
        task_type=task_type,
        payload=payload
    )
```

### 6. Vikunja Workflow Integration

**Purpose**: Track knowledge absorption tasks and quality metrics.

**Project Setup**:

```yaml
project:
  name: "Knowledge Absorption"
  description: "Track research ingestion and quality metrics"
  
labels:
  - knowledge.ingest
  - knowledge.extract
  - knowledge.classify
  - knowledge.score
  - knowledge.distill
  - knowledge.store
  - knowledge.rejected
  - quality.gold
  - quality.high
  - quality.acceptable
```

**Task Template**:

```python
async def create_knowledge_task(state: KnowledgeState) -> VikunjaTask:
    """Create Vikunja task for knowledge tracking."""
    return await vikunja.create_task(
        project_id=KNOWLEDGE_PROJECT_ID,
        title=f"[{state['source_type']}] {state['classification']['topic']}",
        description=f"""
## Source
- Type: {state['source_type']}
- ID: {state['source']}
- Quality Score: {state['quality_score']:.2f}

## Summary
{state['summary']}

## Key Insights
{chr(10).join(f"- {i}" for i in state['key_insights'])}

## Storage
- Targets: {', '.join(state['storage_targets'])}
- Qdrant IDs: {', '.join(state['qdrant_ids'])}
""",
        priority=map_quality_to_priority(state['quality_score']),
        labels=generate_labels(state)
    )
```

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)

1. **Create Staging Directory**
   - `library/_staging/` with subdirectories
   - TTL cleanup script

2. **Implement KnowledgeState TypedDict**
   - Define state schema
   - Add validation

3. **Create Qdrant Collection**
   - `xnai_knowledge` collection
   - Payload schema

### Phase 2: Distillation Engine (Week 2)

1. **Implement LangGraph Workflow**
   - Extract node
   - Classify node
   - Score node
   - Distill node
   - Store node

2. **Quality Scoring System**
   - Relevance calculation
   - Novelty detection
   - Actionability extraction

3. **Rejection Handling**
   - Archive rejected content
   - Generate rejection reports

### Phase 3: Integration (Week 3)

1. **Agent Bus Integration**
   - New task types
   - Task routing

2. **Vikunja Integration**
   - Project setup
   - Task templates

3. **Memory Bank Integration**
   - Append functions
   - Overflow handling

### Phase 4: Testing & Validation (Week 4)

1. **Unit Tests**
   - Each node in isolation
   - Quality scoring accuracy

2. **Integration Tests**
   - End-to-end workflow
   - Cross-system integration

3. **Performance Testing**
   - Throughput benchmarks
   - Memory usage profiling

## Quality Metrics

### System Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Acceptance Rate** | 40-60% | Accepted / Total ingested |
| **Average Quality Score** | > 0.7 | Mean of accepted content |
| **Duplicate Detection** | > 90% | Correctly identified duplicates |
| **Storage Efficiency** | < 100MB/month | Incremental storage growth |

### Content Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Relevance Score** | > 0.8 | Average for accepted content |
| **Novelty Score** | > 0.6 | Average for accepted content |
| **Actionability Score** | > 0.5 | Average for accepted content |
| **Expiry Rate** | < 10% | Expired / Total stored |

## Security Considerations

### Data Protection

```python
class KnowledgeSecurity:
    """Security measures for knowledge absorption."""
    
    async def sanitize_content(self, content: str) -> str:
        """Remove sensitive information."""
        # Remove API keys
        # Remove credentials
        # Remove PII
        return sanitized
    
    async def validate_provenance(self, source: str) -> bool:
        """Validate source is trusted."""
        trusted_sources = [
            "agent_research",
            "cli_session",
            "approved_api"
        ]
        return source in trusted_sources
```

### Access Control

```python
class KnowledgeAccess:
    """Access control for knowledge base."""
    
    async def check_access(self, agent_did: str, action: str) -> bool:
        """Check if agent has permission for action."""
        permissions = {
            "knowledge.ingest": ["mc-overseer", "researcher"],
            "knowledge.store": ["mc-overseer"],
            "knowledge.expire": ["mc-overseer", "architect"],
            "knowledge.audit": ["mc-overseer", "security"]
        }
        return agent_did in permissions.get(action, [])
```

## Maintenance

### Automated Cleanup

```python
async def cleanup_expired_knowledge():
    """Remove expired knowledge from all storage targets."""
    # Clean staging directory
    await cleanup_staging()
    
    # Expire Qdrant entries
    await expire_qdrant_entries()
    
    # Archive old memory bank entries
    await archive_memory_bank()
```

### Quality Audits

```python
async def audit_knowledge_quality():
    """Periodic audit of stored knowledge."""
    # Sample random entries
    # Re-calculate quality scores
    # Identify drift or degradation
    # Generate audit report
```

---

**Status**: DESIGN COMPLETE - Ready for implementation
**Owner**: MC-Overseer Agent
**Dependencies**: LangGraph, Qdrant, Agent Bus, Vikunja, fastembed
**Timeline**: 4 weeks for complete implementation