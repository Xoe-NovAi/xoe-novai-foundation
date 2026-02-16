---
last_updated: 2026-02-14
status: active
persona_focus: Grok
agent_impact: high
related_phases: All
---

# Model Capability Matrix (Feb 2026)

This matrix defines the strengths and weaknesses of the current Xoe-NovAi model lineup to optimize for the Ground Truth Foundation.

| Model | Token Window | Primary Strength | Weakness | Assigned Role |
| :--- | :--- | :--- | :--- | :--- |
| **Gemini 3 Flash** | 1,000,000 | "Thinking" speed, 1M context, multimodal, truth-synthesis. | Occasional over-verbosity. | **Ground Truth Orchestrator** |
| **Kimi K2.5** | 256,000 | SWE-bench leader, visual coding, deep terminal reasoning. | Debugging consistency. | **Advanced Engineer (Cline)** |
| **Claude Haiku 4.5** | 200,000 | Speed, "Near-frontier" code quality, tactical efficiency. | Output token limit (64k). | **Tactical Support (Copilot)** |

## 📊 Strategic Evaluation
- **Gemini 3 Flash** (Scribe) is the **Ultimate Scribe**. Released in Dec 2025, it integrates reasoning capabilities into a high-speed package. With 1M tokens and 3x faster response than 2.5 Pro, it is the primary tool for cross-repo auditing and SDD (Spec-Driven Development) orchestration.
- **Kimi K2.5** (Cline) is the heavy lifter. Its 73.8% SWE-bench score and TerminalBench leadership make it the ideal candidate for **complex implementations** that require driving the terminal and deep file-system navigation.
- **Claude Haiku 4.5** (Copilot) is the **Swift Sword**. Its speed and 200k context make it perfect for rapid snippets, documentation fixes, and secondary verification.
