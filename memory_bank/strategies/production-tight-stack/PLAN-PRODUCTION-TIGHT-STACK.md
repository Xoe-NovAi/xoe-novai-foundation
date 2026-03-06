# XNAi Foundation: Production-Tight Stack Strategy
## Advanced Discovery-Based Plan with Documentation & Curation Foundation

**Created**: 2026-02-28  
**Status**: Ready for Deep Review  
**Overall Scope**: 6-8 week comprehensive stack optimization  
**Approach**: Documentation First → Knowledge Synthesis → Intelligent Curation → Production Excellence

---

## 🎯 STRATEGIC VISION

Transform XNAi Foundation from a functioning system into a **production-tight, self-maintaining knowledge platform** that:
- Operates with **zero manual intervention** via background inference
- **Crawls documentation** for all stack services with intelligent metadata extraction
- **Curates knowledge** locally using light quantized models running 24/7
- **Builds offline library** through online APIs with quality scoring
- **Manages documentation** with automated validation, linking, and freshness
- **Coordinates all systems** through Agent Bus & memory hierarchy

**Unique Selling Point**: Perfect documentation → Perfect curation → Perfect embeddings → Perfect inference

---

## 📊 CURRENT STATE ANALYSIS

### ✅ What's Already Working
1. **Documentation Systems**
   - 375 docs files across Diátaxis-compliant structure
   - 250 expert-knowledge files with domain organization
   - 210 memory_bank files with MemGPT-style tiering (Core → Recall → Archival)
   - MkDocs build ~5 seconds (optimized)
   - 16.4 MB total documentation

2. **Crawling Infrastructure**
   - crawl4ai (v0.7+) deployed with chromium headless
   - curation_worker.py (async Redis queue) ready
   - crawler_curation.py (metadata extraction) implemented
   - doc-curation-bridge.yaml (full pipeline config) existing
   - Content assessment pipeline designed (quality/relevance scoring)

3. **Knowledge Management**
   - Qdrant vector DB configured (xnai_knowledge collection)
   - FAISS local index available
   - Knowledge distillation pipeline (LangGraph StateGraph)
   - EKB audit framework exists (security ✅, infrastructure 🔄, models ⚠️)

4. **Agent Infrastructure**
   - NovAiBooK (research environment) fully implemented
   - Agent Bus (Redis Streams) coordinating 4 CLI agents
   - Vikunja integration for task management
   - Session manager + knowledge client core services

### 🔴 Critical Gaps (Must Fix First)
1. **Documentation Chaos**
   - ~50 duplicate files in handover directories (100KB waste)
   - Development logs bloating active docs (40+ stale files)
   - No unified search across docs+EKB+memory_bank
   - No semantic layer linking three systems
   - Stale content not automatically detected/flagged

2. **Curation Pipeline Incomplete**
   - crawler_curation.py exists but untested
   - Quality scorer dimensions defined but not implemented
   - No automated freshness tracking
   - No memory bank auto-archival
   - No integrated link validation

3. **Background Inference Not Scheduled**
   - Light models ready (Qwen3-0.6B-Q6_K, DistilBERT, BART)
   - No 24/7 scheduler for curation tasks
   - No automated research queue processing
   - No cache management strategy
   - No performance monitoring dashboard

4. **Knowledge Synthesis Missing**
   - No semantic index (YAML concept map)
   - No unified search API
   - No cross-system discovery mechanism
   - No automated document linking

---

## 🏗️ ARCHITECTURE: PRODUCTION-TIGHT KNOWLEDGE PLATFORM

### System Overview

```
┌──────────────────────────────────────────────────────────────┐
│           DOCUMENTATION EXCELLENCE FOUNDATION                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  docs/ (Diátaxis)  expert-knowledge/  memory_bank/           │
│  375 files         250 files          210 files              │
│  Tutorials/        Domain Research/   MemGPT Tiers/          │
│  How-tos/          Gold Standard      Core/Recall/Archive    │
│  Explanation/                                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                          ↓ 
┌──────────────────────────────────────────────────────────────┐
│          KNOWLEDGE SYNTHESIS & DISCOVERY LAYER               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  • Unified Search API (200ms response target)                │
│  • YAML Semantic Index (20+ concept maps)                    │
│  • Cross-system discovery (docs ↔ EKB ↔ memory_bank)        │
│  • Automated link validation + stale detection              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                          ↓ 
┌──────────────────────────────────────────────────────────────┐
│        CRAWLING & CURATION INTELLIGENCE PIPELINE             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  crawl4ai (discover)  →  Quality Assessment  →  Categorize  │
│     ↓                       ↓                      ↓          │
│  Metadata Extract    Quality Score (0-1)    Tag + Frontmatter│
│  Domain Classify     Relevance Score        Link Related     │
│  Citation Count      Duplication Check      Index Semantic   │
│     ↓                       ↓                      ↓          │
│  Redis Queue (async)  → Qdrant Vectorize → Memory Bank      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                          ↓ 
┌──────────────────────────────────────────────────────────────┐
│    BACKGROUND INFERENCE & 24/7 AUTOMATION WORKERS            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  • Qwen3-0.6B-Q6_K (473MB) - Reasoning & decisions          │
│  • DistilBERT (268MB) - Quality scoring & classification    │
│  • BART (1.4GB) - Summarization & entity extraction         │
│  • ONNX Runtime - Zero external API calls                   │
│                                                              │
│  Scheduled Tasks:                                            │
│  - 2 AM: Daily crawl + metadata extraction                  │
│  - 3 AM: Quality assessment + categorization                │
│  - 4 AM: Deduplication + semantic indexing                  │
│  - Hourly: Memory bank auto-archival                        │
│  - Weekly: Freshness detection + stale flagging             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                          ↓ 
┌──────────────────────────────────────────────────────────────┐
│         AGENT BUS COORDINATION & VIKUNJA INTEGRATION         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Event Types:                                                │
│  • content:discovered → Create Vikunja task + Agent bus     │
│  • content:assessed → Route to appropriate category         │
│  • content:published → Trigger search index update          │
│  • quality:low → Create improvement task                    │
│  • link:broken → Create validation task                     │
│  • memory:archive → Auto-move old sessions                  │
│                                                              │
│  Coordination: Redis Streams + OpenCode/Cline/Gemini CLIs  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Component | Technology | Status |
|-------|-----------|-----------|--------|
| **Crawling** | Web Discovery | crawl4ai v0.7+ | ✅ Ready |
| **Curation** | Metadata Extraction | crawler_curation.py | ✅ Ready |
| **Quality Assessment** | Scoring Engine | DistilBERT Q4 | ✅ Ready |
| **Reasoning** | Decisions/Analysis | Qwen3-0.6B-Q6_K | ✅ Ready |
| **Summarization** | Content Condensing | BART Q4 | ✅ Ready |
| **Vectorization** | Semantic Search | ONNX all-MiniLM-L6-v2 | ✅ Ready |
| **Vector Storage** | Index Management | Qdrant + FAISS | ✅ Ready |
| **Task Queue** | Async Processing | Redis Streams | ✅ Ready |
| **Coordination** | Multi-Agent | Agent Bus (Redis) | ✅ Ready |
| **Task Management** | Workflow Tracking | Vikunja API | ✅ Ready |
| **Documentation** | Source Control | MkDocs + Git | ✅ Ready |
| **Inference** | Local Models | llama.cpp + ONNX | ✅ Ready |

---

## 🗓️ DETAILED IMPLEMENTATION PHASES

### PHASE 0: Foundation Excellence (Weeks 1-2, ~25 hours)
**Goal**: Perfect documentation = perfect curation foundation

#### Phase 0A: Consolidation & Deduplication (Week 1, 10 hours)
**Tasks**:
1. **Handover Directory Merge** (2 hours)
   - Consolidate `memory_bank/handovers/` + `memory_bank/recall/handovers/` (50 duplicate files)
   - Create single canonical directory: `memory_bank/recall/handovers/`
   - Generate index: `handovers/INDEX.md` (searchable archive)
   - Delete redundant directory with git tracking
   - **Impact**: -100KB storage, clearer handover access

2. **Archive Development Logs** (2 hours)
   - Move docs/06-development-log/* (>30 days old) to docs/06-development-log/_archive/
   - Create archive index for historical lookup
   - Update MkDocs nav.yml (remove old files)
   - **Impact**: 30% reduction in active doc size, <5s MkDocs build

3. **Remove Duplicate Content** (3 hours)
   - Identify duplicates: Gemini CLI mastery docs, Vikunja docs, model research
   - Consolidate into single authoritative versions
   - Add cross-references in other locations
   - **Impact**: -50KB, improved discoverability

4. **Documentation Inventory Scan** (3 hours)
   - Create comprehensive file manifest (path, size, purpose, update date)
   - Identify orphaned files (not linked from anywhere)
   - Generate coverage report (domains covered)
   - **Output**: `docs/_meta/DOCUMENTATION-MANIFEST.yaml`

#### Phase 0B: Knowledge Synthesis Layer (Week 1-2, 15 hours)
**Tasks**:
1. **Build Semantic Index** (5 hours)
   - Create `docs/knowledge-synthesis/` directory structure
   - Design YAML concept map linking 20+ core concepts
   - Map relationships: docs ↔ EKB ↔ memory_bank
   - **Concepts**: Authentication, Curation, Models, Infrastructure, Memory, Agents, etc.
   - **Output**: `docs/knowledge-synthesis/SEMANTIC-INDEX.yaml` (searchable)

2. **Generate Human-Readable Index** (3 hours)
   - Create `docs/knowledge-synthesis/CONCEPTS.md`
   - One section per concept with links to all three systems
   - Visual relationship diagram (Mermaid)
   - Search-friendly markdown structure
   - **Output**: Cross-system navigation document

3. **Build Search API** (5 hours)
   - Create `app/XNAi_rag_app/api/docs_search.py`
   - Endpoint: `POST /api/v1/search` with filters
   - Parameters: query, type (docs/EKB/memory), domain, tags
   - Response: unified results ranked by relevance
   - Target: <200ms response time
   - **Implementation**: FastAPI + Qdrant + YAML index

4. **Validation Scripts** (2 hours)
   - Script: `scripts/validate_knowledge_synthesis.py`
   - Check: all links valid, all files indexed, all concepts covered
   - Output: validation report, broken links list
   - Integration: pre-commit hook + CI gate

#### Phase 0C: Automation & Maintenance (Week 2, 12 hours)
**Tasks**:
1. **Stale Content Detection** (3 hours)
   - Create `scripts/detect_stale_content.py`
   - Flag content >90 days unchanged
   - Generate weekly report: `reports/stale-content-{date}.md`
   - Add to docs frontmatter: `last_reviewed: 2026-XX-XX`
   - **Output**: Automated freshness monitoring

2. **Link Validation System** (3 hours)
   - Create `scripts/validate_links.py`
   - Pre-commit hook: `hooks/validate-markdown-links.sh`
   - GitHub Actions workflow: `.github/workflows/link-check.yml`
   - Check internal + external links
   - Report: `reports/link-validation-{date}.md`
   - **Output**: Zero broken links guarantee

3. **Memory Bank Auto-Archival** (3 hours)
   - Create `scripts/memory_bank_manager.py`
   - Scheduled task: Move core → recall → archival based on age
   - Policy: Core (<7 days activity), Recall (<30 days), Archive (>30 days)
   - Maintain token budget: core <25KB
   - **Output**: Self-maintaining memory tiers

4. **Documentation Maintenance Dashboard** (3 hours)
   - Create `docs/operations/DOCUMENTATION-STATUS.md`
   - Real-time status: build time, link health, coverage %, stale count
   - Metrics updated by CI/CD jobs
   - Action items: What to fix next
   - **Output**: Transparency + accountability

#### Phase 0D: Governance & Standards (Week 2-3, 8 hours)
**Tasks**:
1. **Governance Document** (3 hours)
   - Create `docs/_meta/GOVERNANCE.md`
   - Rules: contribution standards, review process, naming conventions
   - Quality gates: link validation, stale detection, coverage requirements
   - Roles: documentation maintainers, domain experts, reviewers
   - **Output**: Enforceable standards

2. **EKB Audit Framework** (3 hours)
   - Create `expert-knowledge/_meta/AUDIT-FRAMEWORK.yaml`
   - Define audit scope: 9 domains (Security, Infrastructure, Models, etc.)
   - Audit schedule: quarterly with detailed findings
   - Freshness tracking: last_reviewed date + next_review date
   - **Output**: Auditable knowledge quality

3. **Coverage Analyzer** (2 hours)
   - Create `scripts/analyze_coverage.py`
   - Target: >90% of code modules documented
   - Output: coverage report with gaps
   - Integrate with CI/CD: fail if <85%

### PHASE 1: Crawling Intelligence (Weeks 3-4, ~18 hours)
**Goal**: Production-ready crawling with metadata extraction

#### Phase 1A: Crawler Deployment & Testing (Week 3, 8 hours)
**Tasks**:
1. **Test crawler_curation.py** (2 hours)
   - Write unit tests (10+ test cases)
   - Mock crawl4ai responses
   - Validate metadata extraction
   - Test domain classification
   - **Success**: 100% pass rate

2. **Create Crawl Targets Manifest** (2 hours)
   - Document all stack services to crawl
   - Source: /app/XNAi_rag_app/services/, /mcp-servers/, /research-environment/
   - Output: `config/crawl-targets.yaml`
   - Include: service name, documentation URL, crawl frequency

3. **Deploy Crawl Scheduler** (2 hours)
   - Create `scripts/crawl_scheduler.py`
   - Cron jobs via systemd timer (not cron tab)
   - Daily crawl at 2 AM (off-peak)
   - Crawl rate: 2 URLs/second (respectful)
   - Timeout: 30s per URL
   - **Output**: Scheduled crawler service

4. **Setup Redis Queue Management** (2 hours)
   - Configure redis streams for crawl output
   - Channel: `crawl:discovered`
   - Priority queue: high/medium/low importance
   - Retention: 7 days
   - **Output**: Async queue infrastructure

#### Phase 1B: Metadata Pipeline (Week 3-4, 10 hours)
**Tasks**:
1. **Implement Quality Scorer** (4 hours)
   - Create `scripts/quality_scorer.py`
   - Dimension 1: Clarity (sentence length, jargon, readability)
   - Dimension 2: Completeness (sections, code examples, links)
   - Dimension 3: Accuracy (syntax valid, links work)
   - Dimension 4: Consistency (style compliance, terminology)
   - Dimension 5: Relevance (topic alignment, audience match)
   - Weights: 20% each
   - **Output**: Quality scores [0-1] for every document

2. **Implement Categorizer** (3 hours)
   - Create `scripts/auto_categorizer.py`
   - Use DistilBERT for content classification
   - Categories: Tutorial, How-to, Reference, Explanation, Strategic, Infrastructure, Research
   - Confidence threshold: >0.7
   - Fallback: manual review if uncertain
   - **Output**: Automatic categorization with confidence

3. **Deduplication Engine** (2 hours)
   - Use Qdrant semantic similarity
   - Threshold: >0.85 similarity = duplicate
   - Store in Qdrant collection: `xnai_curated`
   - Flag duplicates for review
   - **Output**: Duplicate detection + flagging

4. **Frontmatter Generator** (1 hour)
   - Extract/generate YAML frontmatter
   - Fields: title, category, status, tags, hardware_context, last_updated
   - Integrate with categorizer output
   - Add to document automatically

### PHASE 2: Background Inference Workers (Weeks 4-5, ~15 hours)
**Goal**: 24/7 autonomous curation system

#### Phase 2A: Light Model Infrastructure (Week 4, 7 hours)
**Tasks**:
1. **Setup Model Runners** (3 hours)
   - Qwen3-0.6B-Q6_K runner: reasoning engine
   - DistilBERT runner: quality/classification
   - BART runner: summarization
   - Each in separate Python process
   - Memory monitoring with btop
   - **Output**: 3 model services

2. **Implement Model Manager** (2 hours)
   - Create `scripts/model_manager.py`
   - Load models on startup (cold start)
   - Health check every 5 minutes
   - Auto-restart if crashed
   - Monitor memory + CPU
   - **Output**: Fault-tolerant model hosting

3. **Create Curation Worker** (2 hours)
   - Update `app/XNAi_rag_app/workers/curation_worker.py`
   - Poll Redis queue every 5 seconds
   - Process: assess quality → categorize → deduplicate → vectorize
   - Batch size: 5 documents per cycle
   - Retry failed items 3x
   - **Output**: Autonomous curation processor

#### Phase 2B: Scheduled Task Framework (Week 4-5, 8 hours)
**Tasks**:
1. **Create systemd Timer Infrastructure** (2 hours)
   - Daily crawl: 2 AM (0200 UTC)
   - Curation pass: 3 AM (0300 UTC)
   - Archive aging: 4 AM (0400 UTC)
   - Freshness check: Every Sunday 1 AM
   - Link validation: Every Tuesday 2 AM
   - **Output**: systemd timer units

2. **Implement Orchestrator** (3 hours)
   - Create `scripts/xnai_orchestrator.py`
   - Coordinate: crawl → assess → categorize → vectorize → store
   - Handle errors: retry, log, notify via Agent Bus
   - Monitor: memory, CPU, disk usage
   - Report: daily summary to `reports/daily-curation-{date}.md`

3. **Alert & Notification System** (2 hours)
   - Events: crawl_failed, quality_low, memory_critical
   - Channels: Agent Bus (Redis), Vikunja (create task), syslog
   - Escalation: retry 1x → manual review → alert user
   - **Output**: Operational visibility

4. **Monitoring Dashboard** (1 hour)
   - Create `docs/operations/CURATION-DASHBOARD.md`
   - Metrics: documents crawled, avg quality, categories discovered, duplicates found
   - Updated by orchestrator
   - Visible to team

### PHASE 3: Knowledge Storage & Retrieval (Weeks 5-6, ~12 hours)
**Goal**: Queryable knowledge with perfect recall

#### Phase 3A: Vector Store Optimization (Week 5, 5 hours)
**Tasks**:
1. **Configure Qdrant Collections** (2 hours)
   - Collection: `xnai_docs` (all documentation)
   - Collection: `xnai_curation` (curated content)
   - Collection: `xnai_research` (research findings)
   - Payload fields: source, category, quality_score, last_updated, domain
   - Vector model: all-MiniLM-L6-v2 (384 dims)
   - **Output**: Production Qdrant setup

2. **Implement Ingestion Pipeline** (2 hours)
   - Create `scripts/vectorize_and_store.py`
   - Batch: 50 documents at a time
   - Chunk strategy: 512 tokens per chunk, 128 token overlap
   - Vectorize using local ONNX model
   - Store with full metadata
   - **Output**: Automatic vectorization

3. **FAISS Local Index** (1 hour)
   - Maintain FAISS backup for offline search
   - Sync with Qdrant weekly
   - Fallback if Qdrant unavailable
   - **Output**: Offline search capability

#### Phase 3B: Memory Bank Tier Management (Week 5-6, 7 hours)
**Tasks**:
1. **Core Memory Manager** (2 hours)
   - File: `scripts/core_memory_manager.py`
   - Keep: projectbrief, activeContext, progress, architecture
   - Size limit: <25KB (enforced)
   - Auto-archive oldest items when exceeded
   - **Output**: Stable core context

2. **Recall Tier Auto-Migration** (2 hours)
   - File: `scripts/recall_tier_manager.py`
   - Policy: keep 90 days of conversations/decisions/handovers
   - Compress old items (summarization)
   - Move to archival after 90 days
   - Index for semantic search

3. **Archival Tier Organization** (2 hours)
   - Structure: research/, benchmarks/, strategies/, decisions/
   - Auto-index with Qdrant collection: `xnai_archival`
   - Permanent retention
   - Quarterly cleanup (remove duplicates)

4. **Memory Bank Health Report** (1 hour)
   - Create `reports/memory-bank-health-{date}.md`
   - Metrics: core size, recall retention, archival growth
   - Issues: bloated tiers, stale content, duplicates
   - Recommendations: action items
   - **Output**: Transparency + optimization

### PHASE 4: NovAiBooK Integration (Week 6, ~8 hours)
**Goal**: Research environment deep integration

#### Phase 4A: Notebook Documentation Crawling
**Tasks**:
1. **Create Jupyter Metadata Extractor** (2 hours)
   - Extract from .ipynb files in research-environment/notebooks/
   - Metadata: title, description, tags, cells (code + markdown)
   - Quality assessment: completeness (code examples, explanations)
   - Output: markdown for Qdrant indexing

2. **Integrate with Research Queue** (2 hours)
   - Hook: research task creation → auto-create documentation task
   - Pipeline: research_queue_worker.py → doc extraction → vectorization
   - Status tracking: via Vikunja

3. **Example Notebooks Documentation** (2 hours)
   - Document ancient_greek_text_analysis.ipynb workflow
   - Extract: process flow, model usage, data sources
   - Publish to docs/03-how-to-guides/research-ops/
   - Link from NovAiBooK docs

4. **Documentation Update** (2 hours)
   - Create `docs/03-how-to-guides/novaaibook/` directory
   - Docs: setup, workflow, integration, troubleshooting
   - Examples: common research patterns
   - API documentation: REST endpoints for notebook management

---

## 📊 SUCCESS METRICS

| Phase | Metric | Target | Status |
|-------|--------|--------|--------|
| **Phase 0** | Docs free of duplicates | 100% | 🔲 Pending |
| **Phase 0** | Broken links | 0 | 🔲 Pending |
| **Phase 0** | Knowledge synthesis index completeness | >90% | 🔲 Pending |
| **Phase 1** | Crawler test coverage | 100% | 🔲 Pending |
| **Phase 1** | Metadata extraction accuracy | >95% | 🔲 Pending |
| **Phase 2** | Worker uptime | >99.5% | 🔲 Pending |
| **Phase 2** | Daily crawl success rate | >95% | 🔲 Pending |
| **Phase 2** | Memory usage (avg) | <4GB | 🔲 Pending |
| **Phase 3** | Search API response time | <200ms | 🔲 Pending |
| **Phase 3** | Vector store recall@10 | >95% | 🔲 Pending |
| **Phase 4** | NovAiBooK integration | Full | 🔲 Pending |

---

## 🔧 TECHNICAL DECISIONS

### Why Documentation First?
Perfect documentation → clear curation targets → intelligent scoring → accurate embeddings → reliable inference

Reverse order: blindly curation → garbage in vectors → poor search → wasted inference

### Model Selection
- **Qwen3-0.6B-Q6_K**: Smallest capable reasoning model (473MB), perfect for memory-constrained systems
- **DistilBERT**: Lightweight classification (268MB), 40% smaller than BERT
- **BART**: Fast summarization (1.4GB), good quality/speed balance
- **All ONNX**: Zero external API calls, runs on CPU

### Memory Budget
- Core: <25KB (1000 tokens)
- Recall: <200KB (8000 tokens)
- Archive: unlimited
- Reasoning model: 473MB (Qwen3-Q6_K)
- Total inference footprint: <2GB with all three models + data

### Curation Quality Thresholds
- Publish if: quality_score ≥ 0.6 AND relevance_score ≥ 0.7
- Review if: 0.4-0.6 (manual)
- Reject if: <0.4 (too poor quality)

---

## 🚀 EXECUTION STRATEGY

### Key Success Factors
1. **Perfect Documentation Foundation** (Phase 0)
   - No curation works without clear targets
   - 30 hours upfront saves 6+ months debugging downstream

2. **Isolated Testing** (Each phase)
   - Unit tests before integration
   - Mock external dependencies
   - Verify each component independently

3. **Gradual Rollout**
   - Week 1: Foundation (local work)
   - Week 2-3: Synthesis + automation (local work)
   - Week 4-5: Crawling + inference (background jobs)
   - Week 6+: Production operation (24/7)

4. **Monitoring from Day 1**
   - Every component has health checks
   - Alerts for failures
   - Dashboard for status
   - Daily reports to memory_bank

### Resource Requirements
- **Disk**: ~50GB (documentation + models + vectors)
- **RAM**: 6-8GB peak (models loaded)
- **CPU**: 4 cores (2 for crawl, 2 for inference)
- **Network**: Crawl: 2-5 Mbps, Inference: none

### Team Coordination
- **Phase 0**: Solo documentation work (1 person, 25 hours)
- **Phase 1-2**: Crawling + inference (1-2 people, 30 hours)
- **Phase 3-4**: Integration + production (1 person, 20 hours)

---

## 📋 NEXT STEPS (IMMEDIATE)

Once plan approved:

1. **Day 1**: Create PHASE-0-FOUNDATION checklist in Vikunja
2. **Day 2-7**: Execute Phase 0A (consolidation) - 10 hours
3. **Week 2**: Execute Phase 0B (synthesis) + 0C (automation) - 27 hours
4. **Continuously**: Update memory_bank with progress, discoveries, blockers
5. **Weekly**: Report metrics to team

---

## 📚 APPENDIX: CURRENT SYSTEM STATE

### Documentation Structure (16.4 MB total)
```
docs/                    (11 MB, 375 files)
├── 01-start/           # Onboarding materials
├── 02-tutorials/       # Step-by-step learning
├── 03-how-to-guides/   # Practical solutions
├── 04-explanation/     # Conceptual content
├── 05-reference/       # API & spec docs
├── 06-development-log/ # Project history
└── microservices/      # Service documentation

expert-knowledge/        (2.2 MB, 250 files)
├── security/           # OWASP audits, IAM schemas
├── infrastructure/     # Podman, Vikunja, Redis, etc.
├── coder/              # Implementation patterns
├── model-reference/    # Model evaluations & specs
├── origins/            # Project history
├── patterns/           # Error handling, async, etc.
└── _meta/              # Audit framework, governance

memory_bank/            (3.2 MB, 210 files)
├── CORE/              # Always loaded (5 files, ~25KB)
├── strategies/        # Playbooks & plans (15 files)
├── PHASES/            # Phase completion (7 files)
├── recall/            # Searchable history (50 files, 90-day retention)
├── archival/          # Long-term storage (100+ files)
└── handovers/         # Agent transitions (50 files, ⚠️ DUPLICATED)
```

### Curation Infrastructure (Ready)
- **crawl4ai**: v0.7+ deployed, async capable
- **Quality Scorer**: Dimensions designed (5 x 0.2 weight each)
- **Categorizer**: 7 categories mapped
- **Redis Queue**: Streams configured
- **Qdrant**: Collections defined
- **FAISS**: Local index available

### Background Models (Ready)
- **Qwen3-0.6B-Q6_K**: Reasoning (473MB)
- **DistilBERT**: Classification (268MB)
- **BART**: Summarization (1.4GB)
- **all-MiniLM-L6-v2**: Vectorization (91MB)
- **ONNX Runtime**: All models run locally

### Agent Infrastructure (Ready)
- **Agent Bus**: Redis Streams coordinating 4 CLIs
- **Vikunja**: Task management API
- **NovAiBooK**: Research environment (fully implemented)
- **Knowledge Client**: Qdrant access layer
- **Session Manager**: State persistence

---

**Document Version**: 1.0 (Deep Discovery Complete)  
**Last Updated**: 2026-02-28  
**Next Review**: After user approval  
**Approval Status**: 🔲 PENDING USER REVIEW
