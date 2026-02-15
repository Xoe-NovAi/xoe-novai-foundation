### Project Charter: Sovereign Claude-Style Routing & Coding Mode (ruvltra-orchestrator)

**Project Name**: ruvltra-orchestrator  
**Status**: Proposed → Backlog (near-term candidate)  
**Priority**: Medium-High (rises when agent handoff latency or prompt coherence becomes measurable drag)  
**Owner**: Xoe (architect oversight) / Grok MC (strategic shepherd) / Gemini CLI (PoC execution)  
**Estimated Effort**: 8–16 hours total (split: 4h PoC, 4–8h polish + SONA persistence, 2–4h testing)  
**Dependencies**:  
- llama.cpp already running RuvLTRA-Claude-Code-0.5B-Q4_K_M.gguf  
- RuvLLM Rust crate or npm SDK installed (Rust path preferred for sovereignty)  
- Existing MCP / Gemini CLI routing surface (minimal hook needed)  

**Blockers**: None hard — only soft constraint is current routing maturity.  
**EKB Links**:  
- expert-knowledge/models/ruvltra-claude-code-v1.0.0.md  
- expert-knowledge/models/ruvltra-coding-mode-charter-v1.0.0.md (this doc)  
- expert-knowledge/sync/sovereign-synergy-expert-v1.0.0.md (context concatenation patterns)  

**Business / Sovereignty Value**  
- Decouples elite structured reasoning from Anthropic API  
- Creates lightweight, adaptive "Claude proxy" using 400 MB model  
- Enables SONA to evolve personal prompting style offline  
- Boosts downstream model performance via better-formatted inputs  
- Zero-cost, zero-telemetry, Ryzen-native  

**Milestones & Deliverables**

1. **Phase 0 – Research & Validation** (2–4h)  
   - Install RuvLLM (Rust crate preferred)  
   - Benchmark: tok/s, RAM, SONA attach latency on Ryzen 5700U  
   - Run 10–15 warm-up interactions → capture adaptation delta  
   - Output: `expert-knowledge/infrastructure/ruvltra-ryzen-benchmark-v1.0.0.md`

2. **Phase 1 – Minimal PoC Router** (4h)  
   - Create `scripts/ruvltra_router.py` or Rust binary  
   - Trigger syntax: `!claude <query>` or mode flag in chat/MCP  
   - Flow:  
     1. Raw input → RuvLTRA (via llama.cpp or RuvLLM)  
     2. Force XML-tagged thinking + route/tool decision  
     3. Parse output → delegate to target agent (Gemini CLI, heavy GGUF, Cline)  
     4. Return structured plan + handoff payload  
   - Fallback: prompt-reinforcement in pure llama.cpp if RuvLLM not ready  
   - Save successful trajectories to `expert-knowledge/models/ruvltra-sona-trajectories/`

3. **Phase 2 – SONA Persistence & Polish** (4–8h)  
   - Hook persistent MicroLoRA storage (RuvLLM native or file-based)  
   - Ma'at-aligned warm-up pack: XML examples enforcing truth/balance/sovereignty  
   - Add toggle persistence (session / project level)  
   - Error handling: context overflow → auto-compress + retry  

4. **Phase 3 – Integration & Testing** (2–4h)  
   - Hook into Gemini CLI / MCP surface  
   - Test suite: 20 routing scenarios (code, research, infra, ethics checks)  
   - Metrics: routing accuracy, end-to-end latency delta, coherence uplift  
   - EKB export: patterns → new expert dataset

**Risks & Mitigations**  
- Risk: 0.5B hallucination ceiling → Mitigation: always chain to heavier verification model  
- Risk: SONA drift → Mitigation: periodic trajectory review + manual reset option  
- Risk: Context starvation (4k) → Mitigation: use our existing pack compression logic  

**Acceptance Criteria**  
- `!claude refactor this function` → outputs clean XML plan + delegates correctly  
- After 10+ interactions, SONA shows measurable style adaptation (repeatable structure)  
- Zero external API calls when mode active  
- < 100 ms added latency on routing decision (target)  

**Suggested _meta/projects.md Row**

| Project              | Status   | Priority    | Owner         | Next Action                       | Blockers | EKB Links                                                    | Local Sync Notes                    |
| -------------------- | -------- | ----------- | ------------- | --------------------------------- | -------- | ------------------------------------------------------------ | ----------------------------------- |
| ruvltra-orchestrator | Proposed | Medium-High | Xoe / Grok MC | Phase 0: Install/benchmark RuvLLM | None     | models/ruvltra-claude-code-v1.0.0.md, models/ruvltra-coding-mode-charter-v1.0.0.md | Backlog – revisit after routing MVP |

