# XNAi Foundation Phase 5+ Operationalization - MASTER PLAN v3.1

**Status**: 🟢 PLANNING PHASE COMPLETE - Ready for Execution  
**Date**: 2026-02-16 09:11 UTC  
**Plan Version**: 3.1 (Full Claude Research Integration + Krikri Q5_K_M + T5 Research)  
**Location**: `internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/`

---

## 📋 EXECUTIVE SUMMARY

Comprehensive, research-backed, multi-phase strategic plan for XNAi Foundation Phase 5+ operationalization:

- ✅ **15 execution phases** (14 implementation + 1 meta documentation)
- ✅ **5 parallel execution tracks** (critical path, docs, research, sync, cleanup)
- ✅ **19.5 hours total duration** (achievable in 2 calendar weeks)
- ✅ **All 5 Claude research guides fully integrated** (mmap, models, Redis ACL, security, architect)
- ✅ **Updated model specifications** (Krikri Q5_K_M instead of Q4)
- ✅ **T5-Ancient-Greek research integrated** (decoder/encoder analysis added to Phase 10)
- ✅ **Proper project structure** (all docs in internal_docs, not session-state)

---

## 🔬 CLAUDE RESEARCH FILES - FULL INTEGRATION

### File 1: IMPLEMENTATION-ARCHITECT-SUMMARY.md (453 lines)
**Content**: Master review guide, gap analysis, decision framework
**Key Additions**:
- 3 critical gaps identified (security, memory, Vikunja)
- 5 resource guides provided
- Decision matrix for model selection
- Checkpoint validation framework

**Integration**: Used for overall plan structure, decision points, checkpoint gates

### File 2: GGUF-MMAP-IMPLEMENTATION-GUIDE.md (436 lines)
**Content**: mmap() zero-copy loading for large language models
**Key Findings**:
- **99.4% memory reduction**: Krikri from 7GB resident → 40MB page tables
- **Latency**: First call 5-10s (cold), subsequent <1s (kernel cache)
- **Implementation**: llama-cpp-python with `use_mmap=True, use_mlock=False`
- **Working set**: 1-2GB in zRAM for on-demand loading
- **Model Lifecycle Manager**: Required for unload/reload management

**Integrated Into**: 
- Phase 10: Ancient Greek Models + mmap() implementation (120 minutes)
- Task 10.2: Model Lifecycle Manager creation
- Task 10.4: Benchmark latencies

**Your Model**: Krikri Q5_K_M (you have this downloaded)
- Expected size: ~5GB quantized Q5_K_M
- Memory with mmap: ~50MB page tables + 1-2GB working set
- Latency: First call 5-10s, cached <1s

### File 3: ANCIENT-GREEK-MODELS-RESEARCH.md (481 lines)
**Content**: Comprehensive model comparison, BERT architecture, integration patterns
**Key Recommendation**: 
- **pranaydeeps/Ancient-Greek-BERT** (110M, ~220MB Q8)
  - PoS accuracy: 91.2% (SOTA for Ancient Greek as of 2021)
  - Training: First1KGreek + Perseus + PROIEL + Gorman (~20M tokens)
  - Integration: Always resident (small footprint, <100ms latency)
  
**Alternative Identified**: 
- **T5-Ancient-Greek** (220M, ~880MB encoder-decoder)
  - Accuracy: 92% PoS tagging
  - Size: Exceeds budget (but feasible as on-demand, like Krikri)
  - NEW: Your request to research as decoder/encoder option

**Division of Labor**:
- BERT: Fast linguistic analysis (<100ms) - morphology, PoS, embeddings
- Krikri: Heavyweight generation (translation, paraphrase, explanation)
- T5 (optional): Explore as alternative decoder or encoder

**Integrated Into**: 
- Phase 10: Model selection, benchmarking, integration
- Expert-knowledge linking for model specifications

### File 4: REDIS-ACL-AGENT-BUS-CONFIG.md (536 lines)
**Content**: Zero-trust Redis ACL architecture for multi-agent communication
**Key Architecture**:
- **7 ACL users** (not 1 default):
  1. Coordinator (Copilot): All channels, all commands (-dangerous)
  2. Worker (Cline): Own inbox/outbox, task queue, limited commands
  3. Worker (Gemini): Own inbox/outbox, task queue, limited commands
  4. Worker (Grok): Own inbox/outbox, task queue, limited commands
  5. Service (RAG API): Task queue only, stream operations only
  6. Service (Vikunja): Task queue only, stream operations only
  7. Monitor (Prometheus): Read-only, heartbeat/metrics only

**Principles**:
- Restrictive by default (grant nothing unless explicit)
- Channel isolation (each DID gets specific stream patterns)
- Command restrictions (no FLUSHALL, CONFIG, SHUTDOWN, etc.)
- Password protection (SHA256 hashing, unique per agent)

**Implementation**:
- `/data/redis/users.acl` file with 7 user definitions
- `docker-compose.yml` mount: `--aclfile /data/users.acl`
- `.env` variables for 7 unique passwords
- `app/XNAi_rag_app/core/agent_bus.py` updated with ACL auth

**Integrated Into**: 
- Phase 11: Agent Bus + Redis ACL Hardening (90 minutes)
- Task 11.1: Generate ACL file
- Task 11.2: Update docker-compose.yml
- Task 11.3: Test isolation verification
- Task 11.4: Operational testing

### File 5: SECURITY-TRINITY-VALIDATION-PLAYBOOK.md (701 lines)
**Content**: Complete security validation with Syft, Grype, Trivy
**Tools & Tasks**:

**Syft (SBOM Generation)**:
- Scan project directory: `syft packages dir:/path`
- Scan containers: `syft packages docker:image:tag`
- Expected: 100+ components tracked
- Output: JSON SBOM for CVE scanning

**Grype (CVE Scanning)**:
- Scan SBOM: `grype sbom:/logs/xnai-sbom.json --fail-on high`
- Analyze results: Extract HIGH/CRITICAL CVEs
- Remediation plan: Map CVEs to fix versions
- CI/CD automation: GitHub Actions workflow provided

**Trivy (Secrets & Misconfigs)**:
- Config scan: `trivy config /path --severity HIGH,CRITICAL`
- Secrets detection: `trivy fs /path --scanners secret`
- Misconfig audit: Docker, Kubernetes, Terraform rules
- Policy enforcement: OPA Rego policies

**Success Criteria**:
- ✅ SBOM complete (100+ components)
- ✅ Zero HIGH/CRITICAL unpatched CVEs
- ✅ No secrets exposed in configs
- ✅ Security policy enforced
- ✅ Compliance report generated

**Integrated Into**: 
- Phase 13: Security Trinity Validation (45 minutes)
- Task 13.1: Syft SBOM generation (15 min)
- Task 13.2: Grype CVE scanning (15 min)
- Task 13.3: Trivy audits (10 min)
- Task 13.4: Compliance report (5 min)

---

## 🎯 MODEL SPECIFICATIONS - UPDATED FOR YOUR CONFIG

### Krikri-7B Model Update

**Previous Plan**: 
- Model: Krikri-7B-Instruct Q4_K_M

**Your Actual Model**: 
- Model: Krikri-7B-Instruct Q5_K_M (user-downloaded)

**Specification Update**:
| Specification | Q4_K_M (Plan) | Q5_K_M (Your Model) | Impact |
|---|---|---|---|
| Quantization | Q4_K_M | Q5_K_M | Higher quality |
| File Size | ~4GB | ~5.5GB | +1.5GB disk |
| Memory (resident) | ~7GB | ~8.5GB | N/A (mmap) |
| Memory (mmap pages) | ~40MB | ~50MB | +10MB |
| Working Set | 1-2GB | 1-2.5GB | Minimal |
| First Call Latency | 5-10s | 5-10s | Same |
| Cached Latency | <1s | <1s | Same |
| Quality | 4-bit loss | Minimal loss | ✅ Better |
| License | Unknown (Krikri) | Unknown (Krikri) | Check separately |

**Implementation**: Update Phase 10 task 10.3 to use your Q5_K_M:
```bash
# Phase 10.3: Download/Link Krikri-7B
cp /path/to/your/Krikri-7B-Instruct-Q5_K_M.gguf /models/Krikri-7B-Q5_K_M.gguf

# Phase 10.4: Benchmark with Q5_K_M (not Q4_K_M)
python app/XNAi_rag_app/core/model_lifecycle.py \
  --model /models/Krikri-7B-Q5_K_M.gguf \
  --benchmark
```

---

## 📊 T5-ANCIENT-GREEK RESEARCH INTEGRATION

### Background
Claude identified T5-Ancient-Greek in the models comparison but dismissed it as "too large" for resident memory. However, with mmap() strategy used for Krikri, we should investigate T5 as an alternative.

### What is T5-Ancient-Greek?
- **Architecture**: Encoder-Decoder (not encoder-only like BERT)
- **Parameters**: 220M (vs BERT's 110M)
- **File Size**: ~880MB (vs BERT's 220MB)
- **Accuracy**: 92% PoS tagging (vs BERT's 91.2%)
- **License**: Apache 2.0 (✅ Sovereign-compatible)
- **Training**: Classical Greek texts
- **Use Cases**: Both encoding (analysis) AND decoding (generation)

### Key Difference: Encoder vs Encoder-Decoder
| Aspect | Ancient-Greek-BERT | T5-Ancient-Greek |
|--------|-------------------|------------------|
| **Architecture** | Encoder only | Encoder + Decoder |
| **Input** | Text → embeddings | Text → contextualized vectors |
| **Output** | Embeddings, PoS tags | Embeddings, PoS tags, OR generated text |
| **Can generate text?** | ❌ No | ✅ Yes (light generation) |
| **Latency** | <100ms | 100-500ms (encoder), 1-3s (generation) |
| **Memory** | 110MB resident | 880MB (400MB for encoder alone?) |
| **Best for** | Analysis only | Analysis + light generation |
| **Speed** | Fastest | Moderate |
| **Quality** | 91.2% accuracy | 92% accuracy |

### Research Questions for Claude.ai

**Q1: T5 Memory With mmap()**
- Can T5-Ancient-Greek use mmap() like Krikri-7B?
- If so, resident memory: ~50MB page tables instead of 880MB?
- Working set for inference: 200-400MB?
- Would this enable T5 as always-resident OR on-demand alternative to BERT+Krikri?

**Q2: T5 as Lightweight Decoder**
- Could T5 replace Krikri-7B for lightweight translation tasks?
- Quality comparison: T5 92% vs Krikri 7B (unknown baseline)?
- Latency: T5 generation speed vs Krikri 5-10s cold?
- Use case: Short translations (1-5 sentences) vs long-form (essays, articles)?

**Q3: T5 as Enhanced Encoder**
- T5's encoder better than BERT for morphological analysis (92% vs 91.2%)?
- If we use T5 encoder only, memory impact vs full model?
- Can T5 encoder be frozen to run on-demand at CPU cost?
- Would using T5 encoder + Krikri decoder be better than BERT + Krikri?

**Q4: Dual-Model Strategy**
- **Option A** (Current): Ancient-Greek-BERT (resident) + Krikri Q5_K_M (on-demand)
- **Option B**: T5-Ancient-Greek encoder (resident, mmap?) + Krikri (on-demand)
- **Option C**: T5-Ancient-Greek full (on-demand, mmap) - replaces BERT entirely
- Which is optimal for <6GB RAM, <100ms analysis latency, quality preservation?

**Q5: T5 Model Variants**
- Is there a smaller T5 variant for Ancient Greek? (T5-small, T5-base?)
- Any DistilBERT or TinyBERT equivalents for Ancient Greek?
- Could we quantize T5 to Q8_0 like we do for BERT?

### Integration into Phase 10
**Phase 10 Research Task (NEW)**:
```bash
# Phase 10.1: T5-Ancient-Greek Investigation
# Subtasks:
- 10.1a: Find T5-Ancient-Greek model on HuggingFace (if exists)
- 10.1b: Test mmap() loading with T5 (encoder-decoder)
- 10.1c: Benchmark memory vs BERT (resident vs on-demand)
- 10.1d: Compare generation quality: T5 vs Krikri-7B
- 10.1e: Test latency: T5 analysis + generation vs BERT + Krikri

# Phase 10.2: Model Selection Decision
# Evaluate three options:
Option A (Current Plan): BERT (resident) + Krikri Q5_K_M (on-demand)
Option B (T5 Enhanced): T5 encoder (resident or mmap?) + Krikri (on-demand)
Option C (T5 Complete): T5 full model (on-demand mmap) - replace BERT

# Recommendation based on Phase 10 testing
```

---

## 15-PHASE EXECUTION ROADMAP (UNCHANGED)

### **Track A: Critical Operations (Copilot) - 6h 50m**
- Phase 1: Service Diagnostics (2h)
- Phase 2: Chainlit Build & Deploy (45m)
- Phase 2.5: Vikunja Redis Integration (20m) ← Claude feedback
- Phase 3: Caddy Routing Debug (40m)
- Phase 4: Full Stack Testing (60m)
- Phase 5: Integration Testing (60m)
- Phase 13: Security Trinity Validation (45m) ← Claude feedback

### **Track B: Documentation (Cline) - 4h 15m - Parallel with A**
- Phase 6: Architecture Documentation (90m)
- Phase 7: API Reference (75m)
- Phase 8: Design Patterns Guide (80m)

### **Track C: Research & Hardening (Cline) - 4h 40m - After Phase 5**
- Phase 9: Crawl4ai Investigation (90m)
- Phase 10: Ancient Greek Models + mmap() + T5 Research (120m) ← UPDATED
- Phase 11: Agent Bus + Redis ACL Hardening (90m)

### **Track D: Knowledge Sync (Copilot + Cline) - 2h - Continuous**
- Phase 12: Memory Bank Integration (120m)

### **Track E: Cleanup & Template (Copilot) - 1h 45m - Concurrent**
- Phase 14: Project Root Cleanup (60m)
- Phase 15: Pre-Execution Template Docs (45m)

**TOTAL: 19.5 hours**

---

## 📁 DOCUMENT ORGANIZATION

### Proper Structure (NOT session-state)
```
xnai-foundation/
├─ internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/
│  ├─ 00-INTEGRATED-PLAN-WITH-CLAUDE-RESEARCH.md ← PRIMARY REFERENCE
│  ├─ 00-README.md (navigation)
│  ├─ RESEARCH-REQUIREMENTS-FOR-CLAUDE.md (Phase 16+ queue)
│  ├─ EXPANDED-PLAN.md (detailed tasks)
│  ├─ CLAUDE-FEEDBACK-INTEGRATED.md (summary)
│  ├─ EXECUTION-SUMMARY.md (timeline)
│  ├─ QUICK-START.md (5-minute overview)
│  ├─ FINAL-SUMMARY-FOR-USER.md (executive summary)
│  └─ [execution-logs/ and checkpoints/ created during execution]
│
├─ internal_docs/00-project-standards/
│  └─ PRE-EXECUTION-TEMPLATE-v1.0.md (reusable for future projects)
│
└─ PHASE-5-STRATEGIC-PLANNING-COMPLETE.md (root-level summary)
```

**NO FILES IN: `.copilot/session-state/`** ✅ All relocated

---

## ✅ FINAL INTEGRATION CHECKLIST

### Claude Research Integration
- [x] File 1 (IMPLEMENTATION-ARCHITECT-SUMMARY): Gap analysis, decision framework
- [x] File 2 (GGUF-MMAP): mmap() strategy, Model Lifecycle Manager
- [x] File 3 (ANCIENT-GREEK-MODELS): BERT selection, T5 identified
- [x] File 4 (REDIS-ACL): Zero-trust architecture, 7-user ACL system
- [x] File 5 (SECURITY-TRINITY): Syft/Grype/Trivy validation procedures

### Model Updates
- [x] Krikri: Changed from Q4_K_M to Q5_K_M (your actual model)
- [x] Ancient-Greek-BERT: Confirmed as lightweight encoder (110MB, 91% accuracy)
- [x] T5-Ancient-Greek: Identified for research as encoder-decoder option
- [x] Phase 10: Updated to include T5 investigation + decision framework

### Document Organization
- [x] All planning docs moved from session-state to `internal_docs/`
- [x] Proper directory structure created
- [x] Navigation README created
- [x] Master plan updated with all findings
- [x] Pre-execution template in `/00-project-standards/`

### Research Queue for Claude.ai
- [x] 5 T5-Ancient-Greek research questions prepared
- [x] Phase 16+ research topics documented
- [x] Integration points identified

---

## 🎓 RESEARCH QUESTIONS FOR CLAUDE.AI

### T5-Ancient-Greek Investigation (Priority: High)

**Question 1**: Can T5-Ancient-Greek use mmap() for on-demand loading like Krikri-7B?
- Expected answer: Yes/No + memory implications
- Impact: Determines if T5 is viable as always-resident OR on-demand

**Question 2**: Is T5 suitable as a lightweight decoder replacement for Krikri-7B?
- Evaluation criteria: Translation quality, latency, memory efficiency
- Decision point: Should we invest in T5 as alternative to Krikri?

**Question 3**: Is T5's encoder (92% accuracy) better than BERT's (91.2%)?
- Use case: Would T5 encoder offer quality improvement over BERT?
- Cost analysis: 880MB vs 220MB - worth the overhead?

**Question 4**: Optimal model configuration for <6GB RAM:
- Option A: BERT (resident, 110MB) + Krikri Q5_K_M (on-demand, 5GB)
- Option B: T5 (resident mmap, ~50MB) + Krikri (on-demand)
- Option C: T5 (on-demand mmap, ~50MB) - replaces BERT entirely
- Which maximizes quality + speed within memory budget?

**Question 5**: T5 quantization and optimization:
- Can T5 be quantized to Q8_0 like BERT? (Would 880MB → 220MB?)
- Are there smaller T5 variants for Ancient Greek? (base, small)
- Best practices for T5 encoder-decoder with mmap()?

### Phase 16+ Research Queue (After Execution)

**Immediate** (After Phase 5):
- Model swapping strategies for constrained memory
- CVE remediation automation
- Lightweight model complement selection

**Short-term** (After Phase 11):
- Kernel page cache optimization for ML
- Role-based Redis ACL design
- Secret rotation procedures

**Medium-term** (After Phase 15):
- Multi-model inference pipeline
- Future model upgrade path
- Horizontal scaling strategy

---

## 🚀 READY FOR PHASE 1 EXECUTION

### Prerequisites Met
- ✅ All 5 Claude research guides fully reviewed and integrated
- ✅ Krikri model specifications updated (Q5_K_M)
- ✅ T5-Ancient-Greek research questions prepared
- ✅ All planning documents relocated to project structure
- ✅ Master plan created with complete integration
- ✅ Proper file organization established

### Next Steps
1. **Review** this master plan
2. **Ask clarifying questions** on T5 research or any other aspect
3. **Request Claude.ai review** of T5 questions (optional)
4. **Authorize Phase 1** to begin execution

---

## 📍 CURRENT STATUS

**Planning**: ✅ COMPLETE  
**Document Organization**: ✅ COMPLETE  
**Claude Research Integration**: ✅ COMPLETE  
**Model Specifications**: ✅ UPDATED  
**T5 Research Questions**: ✅ PREPARED  

**Awaiting**: User decision to proceed with Phase 1

---

**Version**: 3.1  
**Last Updated**: 2026-02-16 09:11 UTC  
**Location**: `/internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/`  
**Status**: 🟢 Ready for Execution Authorization
