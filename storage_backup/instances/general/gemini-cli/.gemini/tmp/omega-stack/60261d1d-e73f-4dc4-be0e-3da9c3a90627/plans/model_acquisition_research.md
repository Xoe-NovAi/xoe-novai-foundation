# Plan: Model Acquisition Research (Facet 3)

**Objective**: Research acquisition and integration paths for `Ancient-Greek-BERT` and `Krikri-8B-Instruct`.

## Key Files & Context
- `memory_bank/techContext.md`: References the target models and hardware (Ryzen 5700U).
- `app/GEMINI.md`: Directs usage of `facet-research` (Facet 3).
- **Ancient-Greek-BERT**: `pranaydeeps/Ancient-Greek-BERT` (768-dim, BERT-base).
- **Krikri-8B-Instruct**: `Q5_K_M` GGUF optimized for 8 physical cores and Flash Attention.

## Implementation Steps
1. **Research & Documentation**: 
   - Identify specific download URLs and checksums for the models.
   - Define exact preprocessing requirements for `Ancient-Greek-BERT` in `linguistics.py`.
   - Formulate `llama-cli` or `ollama` configuration flags for `Krikri-8B-Instruct` on Ryzen 5700U.
2. **Makefile Integration**:
   - Update `Makefile` with `download-ancient-greek-bert` and `download-krikri` targets.
   - Add an `optimize-ryzen` target to apply system-level tweaks (NUMA, power profiles).
3. **Execution & Validation**:
   - Use `facet-3` (Researcher) to perform deep analysis.
   - If interrupted, restart with updated context and findings.

## Verification & Testing
- Run `make download-models` (after update) to verify accessibility.
- Execute a test script in `linguistics.py` that utilizes the BERT embeddings.
- Perform a local benchmark of Krikri using `llama-cli` to verify token/sec targets.
