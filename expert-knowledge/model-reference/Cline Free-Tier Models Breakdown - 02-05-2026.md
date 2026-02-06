**Grok MC Vault Drop: Cline Free-Tier Models Breakdown – Sovereign Cline Arsenal Analysis**

Fresh 2026 snapshot ingested from Cline ecosystem (releases, blogs, OpenRouter integrations, community threads). Cline's free tier rotates frontier/open models via providers (Moonshot, Arcee, Kwaipilot, etc.) with generous daily limits or unlimited preview access. These are API-routed, not local — but zero-cost entry for agentic coding in VS Code/Cline IDE flow.

**Current Free-Tier Models (Feb 2026 Reality)**  
All accessible via Cline settings → Cline provider (or direct provider OAuth). No local inference needed; paywall only kicks in for heavy abuse beyond preview/free quotas.

1. **Kimi-k2.5** (Moonshot AI / Kimi-K2.5)  
   - **Identity**: 1T MoE (32B active), 256k–262k context, native multimodal (vision + agentic tool use). Open weights, frontier-class.  
   - **Strengths**: Beats Opus 4.5 / GPT-5.2 on many coding + reasoning benchmarks. Elite visual coding (UI specs → code), agent swarms (parallel agents), long-context mastery, thinking mode. Very strong instruction following and tool orchestration.  
   - **Weaknesses**: MoE routing can be inconsistent on edge cases; vision sometimes over-hallucinates without tight prompts. API latency higher than tiny models.  
   - **When to Use**: Complex agentic tasks, visual-to-code (screenshots → implementation), multi-step reasoning, long docs/codebases. Default for heavy lifting in free tier.  
   - **Strategy**: Lead model for autonomous Plan/Act in Cline. Chain with local RuvLTRA for structured routing if API quota bites.

2. **minimax-m2.1** (MiniMax)  
   - **Identity**: Lightweight SOTA (~10B class rumored), optimized for coding/agentic workflows, modern app dev. High usage in Kilo/Cline leaderboards.  
   - **Strengths**: Extremely fast + efficient for size. Strong real-world engineering (SWE-Bench style), agentic reliability, low hallucination on code tasks. Often tops speed/quality ratio in free tier.  
   - **Weaknesses**: Smaller context (~128k–200k), less raw reasoning depth than Kimi-k2.5 on frontier problems. Weaker multimodal/vision.  
   - **When to Use**: Everyday coding, quick refactors, terminal/CLI tasks, when latency matters (interactive sessions). High-volume mundane work.  
   - **Strategy**: Workhorse for 70–80% of Cline interactions. Escalate to Kimi only when depth or vision needed.

3. **kat-coder-pro** (Kwaipilot / KAT-Coder-Pro V1)  
   - **Identity**: Agentic coding specialist (Kwaipilot series). High SWE-Bench Verified (~73.4%), optimized tool-use, multi-turn, scalable RL-tuned.  
   - **Strengths**: Best-in-class real-world software engineering (bug fix, repo navigation, multi-file changes). Excellent generalization, instruction adherence.  
   - **Weaknesses**: Narrower focus (pure coding/agentic → weaker general chat/reasoning). Context likely 128k–200k. Less multimodal.  
   - **When to Use**: Deep repo surgery, bug hunting, complex refactors, agentic flows in large codebases.  
   - **Strategy**: Specialist summon for SWE-Bench-style problems. Pair with minimax for speed, Kimi for vision/long-context.

4. **trinity-large-preview** (Arcee AI / Trinity Large Preview)  
   - **Identity**: 400B sparse MoE (13B active), Apache 2.0, US-built. Trained for agent harnesses (Cline/OpenCode/Kilo). 128k–131k context. Free preview unlimited (limited time).  
   - **Strengths**: Frontier reasoning + deep code understanding. Excels in tool-driven workflows, long constraints, agent navigation. High-quality structured code reviews.  
   - **Weaknesses**: MoE inference can feel variable; preview may have post-training quirks. Larger active params → slightly higher latency than minimax.  
   - **When to Use**: Complex reasoning over code, code review at scale, agent orchestration, when you need "big model thinking" for free.  
   - **Strategy**: Premium free option for deep analysis/reviews. Use when Kimi quota dips or for US-sovereign preference.

5. **giga-potato** (Stealth / Kilo Code codename)  
   - **Identity**: Anonymous frontier reasoning model (suspected DeepSeek V4 / ByteDance Doubao variant). 256k context, ultra-long outputs, enterprise instruction following. Free stealth preview in Kilo (mirrored in Cline?).  
   - **Strengths**: Massive context mastery, high coherence on long interactions, strong synthesis/reasoning. Potentially SOTA on long-context coding/agents.  
   - **Weaknesses**: Opaque origin → trust variance. Preview stability unknown. May throttle or vanish post-stealth.  
   - **When to Use**: Ultra-long codebases/docs, extended agent sessions, when context starvation kills other models.  
   - **Strategy**: Exotic summon for 256k+ needs. Test aggressively during preview window.

**Overall Cline Free-Tier Strategy for XNAi**  
- **Default Stack**: minimax-m2.1 (speed) + Kimi-k2.5 (depth/vision) rotation.  
- **Escalation Ladder**: mundane → minimax → mid → kat-coder-pro → heavy → Kimi-k2.5 / trinity-large-preview.  
- **Giga-Potato Wildcard**: Long-context emergencies only.  
- **Hybrid Sovereign Play**: Use Cline free APIs for agentic speed → handoff complex verification to local Qwen2.5-Coder-7B + RuvLTRA routing.  
- **Quota Hygiene**: Spread load across models; monitor daily limits in Cline settings.

**EKB Save**  
`expert-knowledge/model-reference/cline-free-tier-models-v1.0.0.md` — full breakdown, usage matrix, escalation charter.

**Next Actions & Momentum Probes**  
1. In Cline → test rotation: 10 tasks split across minimax / Kimi / kat-coder-pro → log quality/latency delta vs local Qwen.  
2. Draft Cline-specific prompt pack enforcing Ma'at-structured output for free-tier consistency?  
3. Priority: lock minimax as daily driver, or stress-test trinity-large-preview during its free window?  
4. Any observed quota patterns or model quirks in your Cline env to feed back?

Vault synced. Free-tier leverage maximized. Your vector?