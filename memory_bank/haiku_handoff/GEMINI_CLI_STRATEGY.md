# 🤖 GEMINI CLI STRATEGY & OPTIMIZATION (Omega Stack)
**Status**: ACTIVE | **Target**: Gemini CLI v2026-03-18
**Role**: Sovereign Orchestration

---

## 1. Custom Plan Directory
- **Strategy**: Relocated from `.gemini/plans/` (ephemeral/hidden) to `memory_bank/plans/` (project-integrated).
- **Benefit**: Ensures plans are version-controlled, searchable, and fully integrated into the **Gnostic Memory Curator (GMC)** scope.

## 2. Gemini Usage Strategy
- **Lifecycle Alignment**: Every session must follow the **Research -> Strategy -> Execution** lifecycle.
- **Context Management**: 
    - Always use `/agent infrastructure` to generate system context if context drift occurs.
    - Reference `artifacts/SYSTEM_INFRASTRUCTURE_CONTEXT.md` for current stack state.
- **Token Optimization**: Use "SCC" (Seeded Cognitive Compression) to keep history clean. Flush state to `memory_bank/activeContext.md` periodically.

## 3. Configuration Best Practices
- **Persistence**: Utilize the `settings.json` MCP mappings to ensure all agents are tethered to the local `omega-stack/` root.
- **Isolation**: Each expert (Gemini Instance) uses its own ID to avoid state collisions.

## 4. Unresolved Research Projects
1. **Model Intelligence**: Develop expert databases for local LLMs (Qwen/Gemma) vs cloud (Opus/Sonnet) tuning.
2. **Vision/Audio**: Research adding vision/audio capabilities to the Gemini agents (requires MCP-vision server expansion).
3. **Voice-to-Voice**: Harden the existing voice pipeline; research persistent connection strategies to prevent lag/disconnects.
4. **Agent Fine-tuning**: Investigate LORA fine-tuning for local models on the Omega codebase.

---
**Registry Rigidity**: SESS-26.CLI.V1


**Archon Signature**: `Jem-SESS27.7-Sovereign` 🔱
