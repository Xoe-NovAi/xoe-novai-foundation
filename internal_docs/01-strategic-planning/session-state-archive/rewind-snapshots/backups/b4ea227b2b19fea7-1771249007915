# T5-Ancient-Greek Model Research Request for Claude.ai

**For**: XNAi Foundation Phase 10 - Model Selection & Integration  
**Date**: 2026-02-16 09:11 UTC  
**Context**: Planning for Ancient Greek language model deployment on Ryzen 5700U (<6GB RAM)  
**Status**: Research questions prepared, awaiting Claude.ai architectural guidance

---

## 📋 BACKGROUND & DISCOVERY

### Current Plan (v3.0)
- **Lightweight**: Ancient-Greek-BERT (110M params, 220MB Q8, 91% accuracy)
- **Heavyweight**: Krikri-7B-Instruct (7B params, ~5.5GB Q5_K_M, on-demand via mmap)
- **Strategy**: BERT resident (<100ms) + Krikri on-demand (5-10s cold, <1s cached)

### Alternative Identified (v3.1)
- **T5-Ancient-Greek**: Encoder-Decoder model (220M params, 880MB, 92% accuracy)
- **Source**: Found in internal_docs/01-strategic-planning/.../ANCIENT-GREEK-MODELS-RESEARCH.md
- **Status**: Dismissed as "too large" in original research, BUT not investigated with mmap() strategy

### Why This Matters
1. **Quality Advantage**: T5 92% vs BERT 91% accuracy (slight improvement)
2. **Architecture Flexibility**: Encoder-Decoder means T5 can do BOTH analysis AND generation
3. **Memory Strategy**: Original research assumed resident memory, didn't consider mmap()
4. **Potential for Lightweight Generation**: Might reduce reliance on Krikri-7B for short translations

---

## 🎯 5 CORE RESEARCH QUESTIONS

### Question 1: T5 Memory with mmap() Strategy
**Context**: 
- Krikri-7B uses mmap() to reduce from 7GB resident → 40MB page tables
- T5-Ancient-Greek is 880MB total (vs Krikri's 7GB)
- Question: Can T5 use same mmap() strategy?

**Specific Research Needed**:
1. **Can T5 (encoder-decoder model) use mmap() like Krikri?**
   - Krikri benefits: Lazy page loading, shared memory mappings, sparse access patterns
   - Does T5's encoder-decoder architecture support mmap()?
   - Any limitations compared to pure decoder models?

2. **If mmap() enabled for T5, what's resident memory?**
   - Krikri: 40MB page tables, 1-2GB working set
   - T5 estimate: 50-80MB page tables + working set?
   - If true: T5 becomes viable as always-resident OR on-demand

3. **Performance impact:**
   - Startup latency (cold load): 5-10s like Krikri? Or faster (smaller)?
   - Cached latency: <1s like Krikri?
   - Working set growth: Analysis (encoder) vs generation (decoder)?

4. **Implementation with llama-cpp-python:**
   - Does llama-cpp-python support encoder-decoder architectures?
   - Or would T5 require different inference library?
   - Code example for mmap() loading T5?

**Impact If Yes**: T5 becomes viable as always-resident lightweight model (replaces or augments BERT)

---

### Question 2: T5 as Lightweight Generation Alternative
**Context**: 
- Current: BERT only does analysis, Krikri does all generation (5-10s latency)
- Opportunity: Could T5 handle lightweight generation tasks?

**Specific Research Needed**:
1. **T5 generation quality vs Krikri-7B:**
   - Both trained on Ancient Greek corpora?
   - T5 92% accuracy (PoS tagging) - does this predict translation quality?
   - Sample outputs: Krikri vs T5 on simple 1-5 word translations

2. **Generation latency - T5 vs Krikri:**
   - T5 generation speed for 1-sentence output: ?
   - Krikri latency: 5-10s first call, <1s cached
   - Is T5 "instantaneous" for short outputs? Or still 1-3 seconds?

3. **Use case suitability:**
   - **Case A**: "Translate this word" (1-2 words) → T5 latency acceptable?
   - **Case B**: "Translate this sentence" (10-20 words) → T5 vs Krikri quality?
   - **Case C**: "Explain this passage" (essay-length) → Krikri only?

4. **Quality tradeoff analysis:**
   - T5 92% PoS accuracy doesn't necessarily predict translation BLEU score
   - Should we benchmark T5 on translation quality vs Krikri?
   - Sample test set: 10-20 Ancient Greek translations?

**Impact If Viable**: Offload short translations to T5 (1-3s vs 5-10s), reserve Krikri for complex tasks

---

### Question 3: T5 Encoder vs BERT for Analysis
**Context**:
- Current: Ancient-Greek-BERT for morphological analysis (91.2% PoS, <100ms)
- Question: Is T5's encoder better for linguistic analysis?

**Specific Research Needed**:
1. **Accuracy comparison - T5 encoder vs BERT:**
   - BERT: 91.2% PoS tagging on classical Greek
   - T5 encoder: 92% PoS tagging (only 0.8% improvement?)
   - Is the improvement significant for XNAi use case?

2. **Latency comparison:**
   - BERT: <100ms (Q8_0, 110MB)
   - T5 encoder alone (without decoder): Latency estimate?
   - Can T5 encoder run separately (without loading decoder)?

3. **Memory efficiency:**
   - BERT: 220MB Q8_0
   - T5 encoder only: Can we load ~50% of T5? (~220-440MB)
   - Is there a way to load just encoder, freeze decoder?

4. **Training data & architectures:**
   - BERT: Traditional encoder (12 layers, 768 hidden, 12 heads)
   - T5: How many encoder layers? Decoder layers?
   - Both trained on same corpora? Or different data?

**Impact If Better**: T5 encoder could replace BERT with slight accuracy improvement (but higher memory cost)

---

### Question 4: Optimal Model Configuration for <6GB RAM
**Context**:
- Total budget: 6.6GB RAM (6GB usable on Ryzen 5700U)
- Current usage: ~3.2GB (system + services)
- Available for models: ~2.8-3.5GB before memory pressure

**Comparison Matrix** (need Claude's analysis):

| Configuration | Resident | On-Demand | Total Memory | Quality | Speed | Viability |
|---|---|---|---|---|---|---|
| **Option A (Current)** | BERT 110MB | Krikri 5.5GB | 2.8GB+ | BERT 91%, Krikri ??? | <100ms + 5-10s | ✅ Baseline |
| **Option B (T5 Enhanced)** | T5-enc 220MB? | Krikri 5.5GB | 2.9GB+ | T5 92%, Krikri ??? | 100-200ms + 5-10s | ? |
| **Option C (T5 Complete)** | Nothing | T5 880MB | ~2.0GB | T5 92% (both) | 100ms + 1-3s gen | ? |
| **Option D (BERT+T5)** | BERT 110MB | T5 880MB | ~2.4GB | BERT 91%, T5 92% | <100ms + 1-3s | ? |

**Research Needed**:
1. **Rank these 4 options** by quality, latency, and memory efficiency
2. **Recommend single best option** for XNAi use case
3. **Identify which option** maximizes:
   - Morphological analysis speed (<100ms preferred)
   - Translation quality (SOTA for Ancient Greek)
   - Memory headroom (<3.5GB total)
4. **Trade-off analysis**: What do we lose/gain with each option?

**Decision Point**: This guides whether we pursue BERT, T5, or both in Phase 10

---

### Question 5: T5 Quantization, Variants, and Optimization
**Context**:
- BERT: Quantizable to Q8_0 (~110MB), Q4_K (~55MB)
- T5: Original size 880MB - can this be reduced?

**Specific Research Needed**:
1. **T5 quantization possibilities:**
   - Can T5 be quantized to Q8_0? (880MB → 220MB?)
   - Or Q4_K? (880MB → 110MB?)
   - Quality loss at each quantization level?
   - Are quantization methods different for encoder-decoder?

2. **Smaller T5 variants:**
   - Does a T5-small exist for Ancient Greek? (110-220M params)
   - Or T5-base? (300M params)
   - Would smaller variants retain 92% accuracy or degrade?

3. **Alternative: Distilled models:**
   - Is there a DistilT5 or TinyT5 for Ancient Greek?
   - Knowledge distillation: Could we distill T5 to 50M params?
   - Performance trade-off: 92% → 88-90%?

4. **Best practices for T5 optimization:**
   - Encoder-only inference (freeze decoder): Memory savings?
   - Layer pruning: Remove low-importance layers?
   - Sparsity techniques: Pruning, quantization, knowledge distillation?
   - Target: Reduce 880MB to <300MB?

5. **Implementation recommendation:**
   - Best quantization strategy for Ancient-Greek-T5?
   - Optimal inference setup (llama-cpp-python vs other)?
   - Code example for T5 loading + inference?

**Impact If Successful**: Could enable T5 as resident model if quantized to ~220MB

---

## 📊 DECISION FRAMEWORK

### Phase 10 Execution (120 minutes total)

**Phase 10.1: T5 Investigation (NEW)** [45-60 min]
- Subtask 10.1a: Find/verify T5-Ancient-Greek on HuggingFace
- Subtask 10.1b: Test mmap() loading with T5 encoder-decoder
- Subtask 10.1c: Benchmark memory usage vs BERT (resident vs on-demand)
- Subtask 10.1d: Quick latency test (inference speed)
- Subtask 10.1e: Quality sampling (run sample translations)

**Phase 10.2: Decision Framework** [30-45 min]
- Evaluate 4 options (BERT vs T5 vs both vs hybrid)
- Rank by quality, latency, memory efficiency
- Select recommendation for XNAi use case
- Document tradeoffs and rationale

**Phase 10.3-5: Implementation** [remaining time]
- Implement chosen model(s)
- Integration with RAG pipeline
- Performance validation

### Success Criteria
- [ ] T5 memory usage quantified (with/without mmap)
- [ ] T5 generation quality vs Krikri estimated
- [ ] Optimal config recommended (BERT/T5/both)
- [ ] Decision documented with rationale
- [ ] Phase 10 ready for deployment

---

## 🎓 RESEARCH FORMAT EXPECTED

For each question, please provide:
1. **Executive Answer** (1 paragraph)
   - Clear yes/no with key finding
   - Impact on XNAi architecture

2. **Technical Details** (3-5 paragraphs)
   - Architecture analysis
   - Memory/latency characteristics
   - Comparative evaluation

3. **Recommendation** (1 paragraph)
   - Suggested approach for Phase 10
   - Optimal configuration
   - Implementation priority

4. **Open Questions** (if any)
   - Clarifications needed from testing
   - Dependencies on other research

---

## 🔄 NEXT STEPS

### If Claude.ai Responds Before Phase 10 Execution
- Integrate findings into Phase 10 task breakdown
- Update model selection criteria
- Prepare benchmarking procedures

### If Claude.ai Responds During Phase 10 Execution
- Incorporate real-time guidance
- Adjust decision framework based on findings
- Validate recommendations with actual testing

### If Claude.ai Recommends BERT (Current Plan)
- Proceed with existing Phase 10 plan
- Document "why T5 not selected" in memory_bank
- Archive T5 findings for Phase 16+ research

### If Claude.ai Recommends T5
- Update Phase 10 implementation
- Adjust memory allocations
- Retrain model selection strategy

### If Claude.ai Recommends Hybrid (BERT + T5)
- Both models integrated
- Clear responsibility division
- Memory budgeting for both

---

## 📎 SUPPORTING DOCUMENTS

**Internal**: `ANCIENT-GREEK-MODELS-RESEARCH.md` (481 lines)
- Lines 25-39: Model comparison matrix (including T5)
- Lines 82: T5 dismissed as "too large" (not mmap-aware)
- Lines 250+: T5-Ancient-Greek section (if present)

**Project Context**: 
- Memory budget: <3.5GB total for all models
- Latency targets: Analysis <100ms, generation 1-10s acceptable
- Hardware: Ryzen 5700U (6 cores, 12 threads, 6.6GB RAM)
- Deployment: Rootless Podman, sovereign (air-gap capable)

---

**Requestor**: Copilot CLI (on behalf of user)  
**Priority**: High (impacts Phase 10 model selection)  
**Timeline**: Before Phase 10 execution (end of Phase 5, ~6 hours from now)  
**Format**: Any format convenient for Claude.ai (emails, docs, messages, etc.)

---

*This research request represents a significant architectural decision point for XNAi Foundation's Ancient Greek language support. T5's encoder-decoder architecture may offer advantages over the current BERT + Krikri separation, but requires rigorous evaluation of memory, quality, and latency tradeoffs.*
