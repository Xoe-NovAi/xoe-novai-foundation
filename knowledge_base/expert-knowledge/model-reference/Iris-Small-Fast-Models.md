**Grok MC Vault Ingest: Iris Messenger Model Candidate Profile – Sub-1B Tier**

Deep crawl complete across 2025–2026 sources (HF leaderboards, Reddit/LocalLLaMA threads, BentoML/SiliconFlow benchmarks, DataCamp/Dataiku roundups, arXiv evals). Filtered ruthlessly for **<1B params**, GGUF/local-first viability, Ryzen 5700U fit (CPU/iGPU Vulkan, 8GB RAM constraint), fast inference (<100–150 ms latency target for Chainlit UX), and routing/intent-following strength for Iris role (quick-footed Hermes proxy: classify query → route to heavy models → minimal hallucination overhead).

**Elite Shortlist (Sub-1B, Sovereign Fit, 2026 Reality)**  
Prioritized by real-world local inference quality + routing coherence over raw MMLU (which overrates toy models). All GGUF-ready via TheBloke/bartowski quant repos.

1. **Qwen3-0.6B / Qwen2.5-0.5B-Instruct** (Alibaba, ~0.5–0.6B)  
   - Sovereign Score: 10/10 (Apache 2.0, massive community quants)  
   - Inference: ~40–80 t/s CPU Ryzen, <2 GB RAM Q4_K_M  
   - Strengths: Punches far above weight — strong reasoning, multilingual, tool-calling basics, excellent instruction following for size. Competitive vs 3–7B in routing/intent classification.  
   - Iris Fit: Top contender. Clean structured output, low hallucination floor when prompted tightly. Qwen lineage dominates small-model leaderboards 2025–2026.  
   - Weakness: 32k context cap on instruct variant (fine for messenger).  
   - EKB Verdict: Primary recommendation for Chainlit front-line.

2. **Gemma-3-1B / Gemma-3-1B-it** (Google, 1B)  
   - Sovereign Score: 9/10 (permissive license, QAT quants available)  
   - Inference: ~30–60 t/s CPU/iGPU, ~2–2.5 GB Q4  
   - Strengths: Optimized for on-device, excellent multilingual + reasoning in 1B class. Structured prompts shine. 32k–128k context variants.  
   - Iris Fit: Very strong messenger — fast, coherent routing decisions. Often edges Qwen on creative/safe responses.  
   - Weakness: Slightly slower than Qwen on pure CPU bursts.

3. **Llama-3.2-1B-Instruct** (Meta, 1B)  
   - Sovereign Score: 9/10 (Llama Community License)  
   - Inference: ~35–70 t/s, ~2 GB Q4  
   - Strengths: Solid instruction following, good tool-use proxy behavior. Widely quantized.  
   - Iris Fit: Reliable default — clean handoff logic when prompted with XML/JSON.  
   - Weakness: Slightly behind Qwen/Gemma in raw small-model benchmarks 2026.

4. **SmolLM2-135M / SmolLM-360M / SmolLM2-1.7B** (Hugging Face, but focus 360M–1B tier)  
   - Sovereign Score: 10/10 (fully open)  
   - Inference: 135M–360M fly (~100+ t/s CPU), ultra-low RAM  
   - Strengths: Blazing speed, surprisingly coherent for sub-500M. Good for pure routing/switchboard.  
   - Iris Fit: Only if latency is god-tier priority (<50 ms). Quality drops vs 0.5–1B class.  
   - Weakness: Hallucination floor higher; not for nuanced intent.

**Dropped / Honorable Mentions (Why Not Primary)**  
- TinyLlama-1.1B: Solid 2024 baseline, but eclipsed by Qwen/Gemma 2025–2026 releases.  
- Phi-2/Phi-1.5 (~1.3B/0.5B): Strong reasoning but older training cutoff; no 2026 refresh momentum.  
- BitNet b1.58 variants: Experimental 1-bit efficiency kings, but inference ecosystem immature for Ryzen Vulkan.

**Recommendation Matrix – Iris Role (Chainlit Messenger)**

| Model                              | Latency (Ryzen est.) | Routing Coherence | RAM Footprint (Q4) | Multilingual | Overall Sovereign Fit | Rank           |
| ---------------------------------- | -------------------- | ----------------- | ------------------ | ------------ | --------------------- | -------------- |
| Qwen3-0.6B / Qwen2.5-0.5B-Instruct | ★★★★★ (fastest)      | ★★★★★             | ~1.8–2.2 GB        | ★★★★★        | ★★★★★                 | 1              |
| Gemma-3-1B-it                      | ★★★★☆                | ★★★★★             | ~2.2–2.5 GB        | ★★★★★        | ★★★★☆                 | 2              |
| Llama-3.2-1B-Instruct              | ★★★★☆                | ★★★★☆             | ~2 GB              | ★★★★☆        | ★★★★☆                 | 3              |
| SmolLM-360M                        | ★★★★★ (blazing)      | ★★★☆☆             | <1.5 GB            | ★★★☆☆        | ★★★★☆                 | 4 (speed pick) |

**Unsolicited Insight**  
Qwen small lineage is the 2026 sovereign king for <1B routing proxies — consistent leaderboard dominance + community love for structured output. Pair with our existing RuvLTRA-0.5B (Claude mimic) for hybrid mode: Iris = Qwen fast-path + RuvLTRA structured fallback.

**EKB Save**  
`expert-knowledge/models/iris-messenger-sub1b-candidates-v1.0.0.md` — full comparison table, GGUF pull commands, prompt templates for routing.

**Next Actions & Momentum Probes**  
1. Pull Qwen2.5-0.5B-Instruct-Q4_K_M.gguf (or Qwen3-0.6B if available) → benchmark tok/s + routing accuracy on 20 Chainlit-style queries.  
2. Draft Iris system prompt pack enforcing fast classify → route → minimal response?  
3. Want Ryzen-specific quant comparison (Q4 vs Q5 vs Q6) for these three?  
4. Priority: lock Qwen as Iris default, or run head-to-head vs Gemma-3-1B first?

Vault updated. Iris wings being forged. Your thrust vector?