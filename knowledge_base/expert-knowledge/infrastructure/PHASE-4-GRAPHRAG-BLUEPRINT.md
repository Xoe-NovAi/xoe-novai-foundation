# PHASE 4 BLUEPRINT: Hybrid Knowledge GraphRAG Integration

**Status**: 🟢 DRAFT | **Architect**: Gemini CLI (Unified)
**Priority**: CRITICAL
**Target Hardware**: Ryzen 5700U (8GB RAM / 16GB Swap)

---

## 1. Overview
The XNAi Foundation will transition from a flat vector retrieval system to a **Hybrid Knowledge Layer**. This integrates **Qdrant** (semantic search) with **LightRAG** (structural/multi-hop reasoning) using **PostgreSQL** as the graph backend to stay within memory limits.

---

## 2. Technical Stack
- **Graph Engine**: `LightRAG` (v1.0+) with `Postgres` storage backend.
- **Extraction Model**: `Krikri-8b-Instruct` or `Gemma-3-4b` (Local).
- **Orchestration**: `Agent Bus` triggers graph indexing after successful deep crawls.
- **Backend Database**: Existing `xnai_postgres` (schema: `product_knowledge`).

---

## 3. Implementation Workflow

### Step 1: Ingestion & Extraction (Asynchronous)
1. `offline_library_manager` saves a deep-crawled manual to `library/sorted`.
2. A `research_task` is published to the Agent Bus.
3. The **Heavy Lifting Scheduler** triggers:
    - Stops non-essential services.
    - Loads the 8B extraction model.
    - Extracts Entities (Services, Specs, Products) and Relations (Competes with, Requires).
    - Writes triplets to `product_knowledge.relations`.

### Step 2: Hybrid Retrieval
1. **Query Classifier**: A small local model (Qwen-3-0.6B) determines if the query is Relational or Fact-based.
2. **Parallel Retrieval**:
    - **Vector Path**: Qdrant returns top 5 semantic chunks.
    - **Graph Path**: LightRAG performs multi-hop traversal in Postgres to find related entities.
3. **Synthesis**: Results are fused using **Reciprocal Rank Fusion (RRF)** before being sent to the synthesis model.

---

## 4. Product Database Integration
The system will maintain a "Competitive Intelligence" table in Postgres:
- **Automatic Sync**: Any product found in technical manuals is auto-added to `product_knowledge.products`.
- **Zotero Link**: Scholarly metadata from Zotero is used to timestamp and cite product specs.

---

## 5. Security & Sovereignty
- **Forward-Auth**: Caddy middleware will verify that only authorized agents can mutate the Graph.
- **No External Leak**: All entity extraction happens on the Ryzen host.

---

## 6. Next Actions for Opus 4.6
1. **Implement `scripts/graph_extractor.py`**: A wrapper for LightRAG that talks to the `xnai_postgres` backend.
2. **Update `Caddyfile`**: Add Forward-Auth logic for internal agent security.
3. **Create `make curate-product`**: A specialized target for deep-crawling product homepages and auto-populating the schema.
