# XNAi Product & Service Intelligence Framework (v1.0.0)

**Date**: February 28, 2026
**Status**: 🟢 ACTIVE | **Strategy**: Sovereign Multi-Agent Research
**Tags**: [Competitive-Intelligence, Product-Research, Multi-Agent, Postgres, GraphRAG]

---

## 1. Executive Summary
The XNAi Foundation maintains a **Sovereign Product Database** to track technical specifications, pricing models, and competitive benchmarks of industry services (LLMs, Databases, Infrastructure). This framework uses an autonomous, multi-agent pipeline to ingest, verify, and relationalize product information into a **Hybrid Knowledge Layer**.

---

## 2. Architecture: Modular Multi-Agent CI

To ensure accuracy and prevent LLM hallucinations, product research is split across three specialized agent roles:

| Agent Role | Responsibility | Tools |
| :--- | :--- | :--- |
| **Retriever** | Deep-crawls documentation, release notes, and pricing pages. | Crawl4AI, Serper, GitHub API |
| **Critic** | Cross-references extracted specs against secondary sources (e.g., Reddit, X, Benchmarks). | KnowledgeClient, Qdrant |
| **Strategist** | Performs SWOT analysis and maps relations (e.g., "Product A competes with Product B"). | LightRAG, Postgres |

---

## 3. Knowledge Storage Strategy

### 3.1 Structured Spec Storage (SQL)
- **Schema**: `product_knowledge` (PostgreSQL).
- **Function**: Holds deterministic data (RAM limits, token pricing, version numbers).
- **Benefit**: Enables precise SQL queries (e.g., "List all local LLMs with >128k context and <10GB RAM usage").

### 3.2 Relational Knowledge (Graph)
- **Backend**: LightRAG + Postgres.
- **Function**: Maps ecosystem dependencies (e.g., "Open WebUI requires Ollama or llama-cpp-python").
- **Win**: Enables multi-hop discovery of stack compatibility.

### 3.3 Semantic Knowledge (Vector)
- **Backend**: Qdrant.
- **Function**: Stores qualitative descriptions and user reviews for similarity-based discovery.

---

## 4. Resource-Scheduled "Heavy Lifting"

Given the Ryzen 5700U's 8GB RAM constraint, the high-reasoning extraction (Graph building) is performed in **Scheduled Sessions**:
1. **Trigger**: Agent Bus detects 10+ new product documents.
2. **Action**: `heavy_lift.sh` stops non-essential services (RAG API, Crawler).
3. **Execution**: A quantized 8B model (Krikri-8b) processes the backlog into the Postgres graph.
4. **Resumption**: Normal services restart.

---

## 5. Continuous Monitoring Workflow

1. **Detection**: Monitoring agents track `robots.txt` or `sitemap.xml` changes on target product domains.
2. **Ingestion**: `offline_library_manager --deep` downloads the new documentation.
3. **Synthesis**: The `ProductResearchAgent` updates the structured database and generates a Markdown report in `reports/products/`.
4. **Verification**: Citation-based verification via **Better BibTeX** links every spec to a specific page/timestamp.

---

## 6. Directory Structure
- `data/product_knowledge/`: Raw JSON extraction results.
- `library/products/`: Downloaded technical manuals and whitepapers.
- `reports/products/`: Human-readable Markdown comparison reports.
- `migrations/versions/005_product_knowledge_schema.sql`: Database structure.
