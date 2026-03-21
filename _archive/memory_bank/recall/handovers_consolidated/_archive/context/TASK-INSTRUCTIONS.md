# Split Test Task Instructions

**Model**: [RAPTOR MINI | HAIKU 4.5 | MINIMAX M2.5 | KAT-CODER-PRO]  
**Date**: 2026-02-26  
**Output Directory**: `memory_bank/handovers/split-test/outputs/[MODEL]-wave5-manual/`

---

## Primary Task

Create a comprehensive **Wave 5 Implementation Manual** using the context files provided. Your output will be compared against three other AI models to evaluate quality, completeness, and efficiency.

This plan is expandable:
- you can switch the runner to `--adapter local` and supply a local ONNX/GGUF model for evaluation (e.g. a memory-bank-driven retrieval engine).
- later experiments may treat each memory bank as an "expert" model to be measured against identical prompts; see **Multi-Expert Memory Bank Strategy** for details.


---

## Input Context Files

| File | Purpose |
|------|---------|
| `RAPTOR-ONBOARDING-CONTEXT-DOCUMENT.md` | Full project status, Wave 5 details |
| `WAVE-5-PREP-RESOURCES.md` | Resource file paths, phase status |
| `WAVE-5-IMPLEMENTATION-MANUAL.md` | Existing reference (102KB) |

---

## Task Requirements

### 1. Manual Structure

Your Wave 5 Manual MUST include:

1. **Executive Summary** (1 page)
   - Current Wave 5 status (70% complete)
   - Phase breakdown (5A-5E)
   - Key objectives

2. **Phase 5A: Session Management & Memory Optimization** (2-3 pages)
   - Implementation steps
   - Acceptance criteria
   - Testing procedures
   - Troubleshooting

3. **Phase 5B: Agent Bus & Multi-Agent Coordination** (2-3 pages)
   - Implementation steps
   - Acceptance criteria
   - Testing procedures
   - Troubleshooting

4. **Phase 5C: IAM v2.0 & Ed25519 Authentication** (2-3 pages)
   - Implementation steps
   - Acceptance criteria
   - Testing procedures
   - Troubleshooting

5. **Phase 5D: Task Scheduler & Vikunja Integration** (2-3 pages)
   - Implementation steps
   - Acceptance criteria
   - Testing procedures
   - Troubleshooting

6. **Phase 5E: E5 Onboarding Protocol** (2-3 pages)
   - Implementation steps
   - Acceptance criteria
   - Testing procedures
   - Troubleshooting

7. **Quick Reference Card** (1 page)
   - Key commands
   - File locations
   - Emergency procedures

### 2. Quality Standards

- All file paths must be accurate and current
- Phase completion percentages must match provided data
- Include copy-paste ready code snippets
- Provide clear step-by-step instructions
- Each phase must have testable acceptance criteria

### 3. Token Optimization

Your manual should be optimized for:
- **Token efficiency**: High information density
- **Quick scanning**: Clear headings, bullet points
- **Copy-paste ready**: Code blocks complete
- **Navigation**: Table of contents, cross-references

---

## Output Format

Save your final manual as:
```
memory_bank/handovers/split-test/outputs/[MODEL]-wave5-manual/WAVE-5-MANUAL.md
```

Also create:
```
memory_bank/handovers/split-test/outputs/[MODEL]-wave5-manual/METRICS.json
```

### METRICS.json Template

```json
{
  "model": "[MODEL NAME]",
  "tokens_spent": [ESTIMATE],
  "time_elapsed": "[HH:MM]",
  "phases_completed": ["5A", "5B", "5C", "5D", "5E"],
  "sections_included": [LIST],
  "quality_self_assessment": "[1-5]",
  "key_strengths": [ARRAY],
  "limitations_observed": [ARRAY]
}
```

---

## Evaluation Criteria

Your output will be scored on:

| Criterion | Weight |
|-----------|--------|
| Completeness | 25% |
| Technical Accuracy | 25% |
| Actionability | 20% |
| Token Efficiency | 15% |
| Structure | 15% |

See `EVALUATION-CRITERIA.md` for detailed scoring rubric.

---

## Important Notes

1. **Do NOT consult with other models** — work independently
2. **Do NOT share output files** — keep in your designated directory
3. **Use provided context ONLY** — don't hallucinate file paths
4. **Be honest about limitations** — if unsure, state uncertainty

---

**Good luck!**
