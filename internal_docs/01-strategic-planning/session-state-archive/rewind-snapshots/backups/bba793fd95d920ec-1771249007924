# Claude.ai Implementation Architect Context Guide

**For**: Claude.ai providing research guidance to Copilot CLI  
**About**: XNAi Foundation stack development environment, architectural patterns, and performance optimization  
**Purpose**: Help Claude.ai understand the constraints, patterns, and goals for effective research and guidance  
**Date**: 2026-02-16  
**Version**: 1.0

---

## 1. PROJECT CONTEXT

### Mission
Build a **sovereign, visually appealing, resilient multi-agent RAG system** optimized for the **Ryzen 7 5700U** host (6 core, 12 thread, 6.6GB RAM). The system must operate **air-gap capable** with **zero external telemetry** while providing transparent, auditable AI operations.

### Core Philosophy: The 42 Laws of Ma'at
- **Truth** (Justified accuracy, verifiable claims)
- **Resilience** (Graceful degradation, fault tolerance)
- **Sovereignty** (Owner control, transparent operations)
- **Open Source** (Community driven, auditable code)

### Constraints That Shape Every Decision
1. **Memory**: <6GB total RAM (currently 6.6GB, 3.2GB fixed, 3.5GB available for models)
2. **CPU**: 6 physical cores (Ryzen 5700U), some reserved for system
3. **Disk**: Standard SSD (models stored locally, no remote API calls)
4. **Network**: Air-gap capable (no mandatory cloud dependencies)
5. **License**: Sovereign (no vendor lock-in, open source only)

---

## 2. STACK ARCHITECTURE

### 9 Core Services

| Service | Type | Language | Purpose | Status |
|---------|------|----------|---------|--------|
| **Consul** | Service Mesh | Go | Service discovery, health checks | ✅ Operational |
| **Redis** | Cache/Streams | C | Sessions, circuit breakers, agent channels | ✅ Operational |
| **PostgreSQL** | Database | C | Structured data, sessions | ✅ Operational |
| **Qdrant** | Vector DB | Rust | Semantic search, embeddings | ✅ Operational |
| **FAISS** | Vector Index | C++ | Local similarity search | ✅ Operational |
| **RAG API** | Microservice | Python | Document retrieval, inference | ✅ Operational |
| **Chainlit** | UI Framework | Python | Chat interface, session management | 🟡 Deployed (Phase 2) |
| **Vikunja** | Project Mgmt | Go | Task tracking, planning | ✅ Operational (Redis TBD) |
| **Curation Worker** | Async Task | Python | Knowledge processing, indexing | ✅ Operational |

### Service Mesh Pattern
```
Agent Request → Caddy Proxy → Consul DNS → Service Instance
                                      ↓
                            Redis ACL check (Ed25519)
                            ↓
                            Agent Bus Channel
                            ↓
                            Target Service
```

### Data Persistence Strategy
- **Sessions**: Redis (fast, in-memory)
- **Circuit Breakers**: Redis (state tracking)
- **Documents**: PostgreSQL + FAISS (searchable)
- **Embeddings**: Qdrant (vector similarity)
- **Agent Identity**: Local IAM database (Ed25519 keys)

### Identity & Security
- **Agent Handshake**: Ed25519 digital signatures
- **Channel Isolation**: Redis ACL patterns by DID (Distributed ID)
- **Encryption**: Symmetric (sessions), asymmetric (handshakes)
- **Trust Model**: Zero-trust (verify everything, grant nothing by default)

---

## 3. MODEL STRATEGY

### Current Implementation (Phase 5)
```
┌─────────────────────────────────────────────────────────┐
│ Ancient Greek Language Processing Pipeline              │
├─────────────────────────────────────────────────────────┤
│ Input: Greek text                                       │
│   ↓                                                      │
│ [BERT] Morphological Analysis (resident)               │
│   - POS tagging (91.2% accuracy)                       │
│   - Lemmatization                                       │
│   - ~100ms latency                                      │
│   ↓                                                      │
│ [Krikri-7B] Generation/Translation (on-demand mmap)    │
│   - Via mmap(): 50MB page tables, 1-2GB working set    │
│   - 5-10s first call, <1s cached                       │
│   - Flexible output generation                         │
│   ↓                                                      │
│ Output: Analyzed + Generated response                  │
└─────────────────────────────────────────────────────────┘
```

### Models in Use

**BERT (Resident, Always Loaded)**
- Model: `pranaydeeps/Ancient-Greek-BERT`
- Size: 110M parameters, ~220MB Q8 quantized
- Accuracy: 91.2% PoS tagging
- Latency: <100ms
- Purpose: Fast morphological analysis
- Why Resident: Small, fast, always needed

**Krikri-7B (On-Demand via mmap)**
- Model: `krikri-7b-instruct-Q5_K_M` (user's download)
- Size: 7B parameters, ~5.5GB file (Q5_K_M quantization)
- Latency: 5-10s first call (cold), <1s cached
- Memory with mmap: 50MB page tables + 1-2GB working set (kernel cached)
- Purpose: Generation, translation, complex reasoning
- Why mmap: 99.4% memory reduction vs resident loading

**T5-Ancient-Greek (Under Investigation)**
- Model: 220M encoder-decoder
- Size: 880MB
- Accuracy: 92% PoS tagging (vs BERT's 91.2%)
- Trade-off: Better accuracy but larger footprint
- Status: 5 research questions submitted to Claude.ai
- Decision Point: Phase 10 (awaiting Claude.ai guidance)

### Memory Budget Allocation (6.6GB Hardware)
```
┌─────────────────────────────────────────┐
│ 6.6GB Total Hardware                    │
├─────────────────────────────────────────┤
│ System: 400MB                           │
│ Services: 2.8GB (fixed, optimized)      │
│ Models: <900MB                          │
│  ├─ BERT resident: 220MB                │
│  ├─ mmap() page tables: 50MB            │
│  ├─ Working set (zRAM): 1-2GB          │
│  └─ Headroom: 1.9-2.4GB ✅              │
└─────────────────────────────────────────┘
```

**Memory Optimization Techniques**:
1. **mmap()**: Load Krikri-7B without resident memory (50MB vs 7GB)
2. **zRAM**: Compress working set (kernel page cache)
3. **Model Quantization**: Q5_K_M (5-bit) vs full precision
4. **Lazy Loading**: Load models on-demand, unload when idle
5. **Process Recycling**: Restart inference workers periodically

---

## 4. PERFORMANCE TARGETS

### Latency Goals
| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| PoS Tagging (BERT) | <100ms | ~80-100ms | ✅ Met |
| Simple Translation | <1s | 1-3s (cached) | 🟡 Acceptable |
| Complex Generation | 5-10s | 5-10s (cold) | ✅ Met |
| API Response | <500ms | ~200-400ms | ✅ Met |

### Throughput Goals
| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| Req/sec (API) | 10 | ~5-8 | CPU bound |
| Concurrent Users | 5 | ~3-5 | RAM bound |
| Daily Requests | 10K | ~5K | Memory IO |
| Model Cache Hit | 80% | 60-70% | Improving |

### Resource Utilization
- **CPU**: 60-70% during inference (6 cores, 2-3 active)
- **Memory**: 60-70% peak (4.5-4.7GB out of 6.6GB)
- **Disk**: Read-heavy (model loading), write-moderate (logging)
- **Network**: Minimal (air-gap capable)

---

## 5. ARCHITECTURAL PATTERNS

### Resilience Pattern: Circuit Breaker
When a service fails:
1. **Detect**: Monitor error rate, latency spikes
2. **Open**: Stop requests to failing service (fast-fail)
3. **Half-Open**: Periodically test recovery
4. **Close**: Resume normal traffic
- **Storage**: Redis (shared, fast recovery)
- **Timeout**: 30-60 seconds

### Concurrency Pattern: Task Groups (AnyIO)
```python
async with anyio.create_task_group() as tg:
    tg.start_soon(worker1)  # Concurrent
    tg.start_soon(worker2)  # Concurrent
    # All complete before exiting scope
```
**Never use**: `asyncio.gather()`, `create_task()` (unstructured)

### Agent Communication: Agent Bus
```
Agent A → Redis Stream (ACL validated) → Agent B
          ↑
      Ed25519 signature verification
      Channel isolation (DID-based patterns)
      Message encryption (optional)
```

**ACL Model**: Restrictive by default
- Coordinator: All channels
- Workers: Only assigned task channels
- Services: Only health/status channels
- Monitor: Read-only on all channels

---

## 6. DEPLOYMENT MODEL

### Container Strategy: Rootless Podman
- **No root access**: Security isolation
- **User namespaces**: UID/GID mapping
- **Network isolation**: Only Caddy → internal services
- **Read-only FS**: Immutable configs, writable volumes only for data

### Caddy Proxy Configuration
```
xnai-rag-api:8000  → /api/*
vikunja:3456       → /tasks/*
chainlit:8001      → /chat/*
mkdocs:8080        → /docs/*
```
**Key Features**:
- URI prefix stripping (internal routing)
- Health checks (circuit breaker integration)
- Automatic HTTPS (self-signed in air-gap)
- Rate limiting (per-user, per-endpoint)

### Orchestration: Docker Compose
- **Single-host deployment** (Ryzen 5700U)
- **Shared networks** (consul, default)
- **Volume mounts**: Data persistence, model caching
- **Environment variables**: Configuration without rebuilds

---

## 7. RESEARCH PRIORITIES FOR CLAUDE.AI

### Active Research Questions (Phase 10)
These 5 questions guide model selection and will shape system performance:

1. **T5 mmap() Viability**
   - Can T5 (encoder-decoder) use mmap() like Krikri-7B?
   - Working set implications
   - Implementation with llama-cpp-python

2. **T5 as Generation Engine**
   - Quality vs Krikri-7B (92% vs ??? BLEU)
   - Latency for short translations (1-3s?)
   - Suitable use cases

3. **T5 Encoder vs BERT**
   - Accuracy advantage (0.8% improvement significant?)
   - Memory trade-off (880MB vs 220MB)
   - When to use each

4. **Optimal Configuration**
   - BERT + Krikri (current)
   - T5 only (simpler)
   - BERT + T5 (hybrid)
   - Decision framework for Phase 10

5. **T5 Optimization**
   - Quantization to <300MB
   - Smaller T5 variants
   - Distillation possibilities

**Expected Output**: Decision framework + implementation guide

---

## 8. DOCUMENTATION STANDARDS

### Diátaxis Structure (For All Docs)
```
Tutorial    → Learning-oriented (how to get started)
How-To      → Goal-oriented (how to accomplish X)
Reference   → Information-oriented (API, config)
Explanation → Understanding-oriented (why it works this way)
```

### Metadata (YAML Frontmatter)
```yaml
---
title: Component Name
status: Draft/Review/Complete
persona_focus: Developers/Operators/Architects
last_updated: 2026-02-16
ma_at_alignment: Truth/Resilience/Sovereignty
---
```

### Knowledge Organization
- Linked to **42 Laws of Ma'at** where applicable
- Versioned for reproducibility
- Examples with expected output
- Error handling explained

---

## 9. INTEGRATION POINTS FOR CLAUDE.AI

### How Claude Guidance Flows Into Copilot Execution

```
Claude.ai Research
      ↓
Copilot Integrates
      ↓
Phase 10-11 Implementation
      ↓
Tested & Validated
      ↓
Memory Bank Documentation
      ↓
Agent & Stack Improvements
```

### What Copilot Does With Claude's Research
1. **Extract Decision Framework**: Turns recommendations into task choices
2. **Create Implementation Tasks**: Breaks research into executable steps
3. **Define Success Criteria**: Benchmarks and validation procedures
4. **Document Trade-offs**: Captures why certain options were chosen
5. **Integrate into Knowledge**: Updates memory bank and internal docs

### Feedback Loop
- Copilot executes Claude's recommendations
- Validates assumptions with real data
- Reports back findings to memory_bank
- Prepares Phase 16+ optimization research queue

---

## 10. PERFORMANCE OPTIMIZATION OPPORTUNITIES

### Identified in Current Phase
1. **Model Selection** (Phase 10): T5 vs BERT trade-offs
2. **Memory Pressure** (Phase 10): Swapping, prioritization
3. **Inference Latency** (Phase 10): Caching, batching
4. **Security Hardening** (Phase 11/13): ACL, encryption
5. **Knowledge Integration** (Phase 12): Memory bank synchronization

### For Future Phases (16+)
1. **Horizontal Scaling**: Multi-instance deployment
2. **Model Ensemble**: Multiple models for redundancy
3. **Specialized Models**: Domain-specific Ancient Greek
4. **Continuous Learning**: Model fine-tuning on domain data
5. **Zero-Copy Inference**: Further memory optimization

---

## 11. TESTING & VALIDATION STRATEGY

### Performance Benchmarks
- **BERT Latency**: Run 100 samples, measure <100ms?
- **Krikri Throughput**: How many concurrent requests?
- **Memory Stability**: Run 24hr test, any leaks?
- **Redis ACL**: Can unauthorized agents access channels?
- **SBOM/CVE Scanning**: Syft/Grype/Trivy green?

### Integration Testing
- **Stack Health**: All 9 services start, respond to health checks?
- **Service Mesh**: Consul registration, DNS resolution?
- **API Gateway**: Caddy routes to correct backends?
- **Agent Bus**: Message delivery, ACL enforcement?
- **Data Persistence**: Redis ↔ PostgreSQL sync?

### Regression Testing
- **Breaking Changes**: Previous functionality still works?
- **Performance Regression**: Latency stayed same or improved?
- **Security Regression**: No new CVEs, ACL gaps?
- **Knowledge Regression**: Memory bank consistency?

---

## 12. COMMUNICATION PROTOCOL

### For Copilot → Claude.ai
1. **Research Questions**: Specific, measurable, actionable
2. **Constraints**: Hardware, time, budget, license limitations
3. **Context**: Why this research matters (business impact)
4. **Deliverable Format**: What Copilot needs to integrate answer

### For Claude.ai → Copilot
1. **Executive Summary**: 1-para answer with key finding
2. **Technical Details**: Architecture, trade-offs, evidence
3. **Recommendation**: Best path forward for constraints
4. **Implementation Guide**: How to execute recommendation
5. **Remaining Questions**: What still needs testing

### Expected Timeline
- **Research Submission**: Async, anytime
- **Claude.ai Response**: 2-24 hours
- **Copilot Integration**: Before relevant phase execution
- **Validation**: During Phase execution with real data

---

## 13. SUCCESS METRICS

### For Claude.ai Guidance
- ✅ Recommendations reduce Phase execution time by 20%+
- ✅ Architectural guidance prevents blocking issues
- ✅ Research questions answered with actionable insights
- ✅ Knowledge integrated into production system
- ✅ Future optimization opportunities identified

### For XNAi Stack
- ✅ All 9 services operational with <500ms latency
- ✅ Models performing at target accuracy (91%+ PoS)
- ✅ Memory usage <6GB peak, scalable architecture
- ✅ Zero security vulnerabilities (no HIGH/CRITICAL CVEs)
- ✅ Air-gap capability maintained (no external dependencies)

---

## 14. GLOSSARY & REFERENCE

### Key Terms
- **AIR-GAP**: No internet connectivity, all data/models local
- **GGUF**: GPU-friendly format for quantized model weights
- **mmap()**: Memory-mapped file IO, zero-copy loading
- **zRAM**: Compressed RAM drive, reduces physical memory pressure
- **Agent Bus**: Redis streams for inter-agent communication
- **Circuit Breaker**: Fault tolerance pattern for service failures
- **DID**: Distributed Identity, used for agent identification
- **ACL**: Access Control List, fine-grained permissions
- **Diátaxis**: Documentation structure (tutorial, how-to, reference, explanation)
- **Ma'at**: Egyptian concept of truth, balance, cosmic order → XNAi's 42 Laws

### Technical Repos & Standards
- **Consul**: Service mesh & discovery (HashiCorp)
- **Redis**: In-memory cache & streams (Redis Labs)
- **FastAPI**: Python async web framework (Starlette)
- **LangChain**: LLM framework (Harrison Chase)
- **Qdrant**: Vector database (Qdrant)
- **llama-cpp-python**: GGUF inference library

---

**This guide enables Claude.ai to understand the XNAi Foundation stack comprehensively and provide deeply informed architectural and optimization guidance. Use this context when answering research questions to ensure recommendations account for the hardware constraints, performance targets, and sovereignty requirements.**

---

*Version 1.0 • Generated 2026-02-16*  
*For: Claude.ai Implementation Architect*  
*By: Copilot CLI on behalf of XNAi Foundation Team*
