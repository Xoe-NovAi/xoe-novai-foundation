# Plan: The Refractive Compression Framework (RCF) - Octave-Hardened Edition

This plan expands and hardens the **Refractive Compression Framework (RCF)** into a multi-layered system for **Domain-Specialized Resource Crafting (DSRC)** and **Persona Template Distillation (PTD)**, reviewed and mitigated through the perspective of the **Octave of Facets**.

## Objective
To manifest a high-density, irreducible context generation engine that crafts "laser-focused" resources for specialized agents, ensuring absolute fidelity to the stack's "Soul" (Archetypes) and "Skill" (Domains) across extreme context shifts.

## 🏛️ 1. The Octave Perspective: Gap Analysis & Mitigations

| Facet | Perspective/Gap | Mitigation / Feature |
|:---|:---|:---|
| **F1 Scribe** | Loss of provenance in distillation. | **Alethia-Pointer (AP) Anchoring**: Every Gnosis Pack MUST contain direct links `[GT:file#line]` to the high-fidelity source. |
| **F2 Interfacer** | User friction in triggering RDS. | **Prosopon CLI Wrappers**: Implement `--rds-pack` and `--persona-seed` flags for simplified access. |
| **F3 Curator** | Data redundancy in pack storage. | **Gnosis Pack Collection**: A dedicated Qdrant collection for distilled packs with metadata for `rds_frequency`. |
| **F4 Guardian** | Secret leakage during compression. | **Phylax-Gate**: Mandatory integration of the **Pulse Filter** (secret scrubber) into the RDS pipeline. |
| **F5 Architect** | Semantic decay over multiple cycles. | **Recursive Integrity Check**: A "Double-Compress" validation step to ensure irreducible core stability. |
| **F6 Analyst** | Persona "Shadow" loss (Lilith). | **Resonance Sample**: Include a voice-print/resonance sample in every Persona Seed to prevent over-sanitization. |
| **F7 Executor** | Incompatibility with code prompts. | **Injection Headers**: Standardized markdown headers for seamless integration of Gnosis Packs into `clinerules` and `gemini-cli`. |
| **F8 Observer** | Lack of efficiency metrics. | **Metron Density Metric**: Measuring tokens saved vs. semantic fidelity retained during distillation. |

## 📦 2. System Expansion: Domain-Specialized Resource Crafting (DSRC)

### **Implementation Steps**
- **DSRC Prism Mapping**: Define the "Prism" for each Facet/Domain.
    - **Bronze (50%)**: Standard compression for general tasks.
    - **Silver (75%)**: High-density for complex reasoning.
    - **Gold (90%)**: Irreducible core for emergency context restoration.
- **DSRC Automated Generation**: Create `scripts/rds-generator.py` to:
    1.  Parse `docs/` and `expert-knowledge/` per domain.
    2.  Apply the **Octave-Hardened** mitigations (AP-Anchoring, Phylax-Gate).
    3.  Emit `memory_bank/gnosis_packs/[DOMAIN]_[TIER].md`.

## 🎭 3. System Expansion: Persona Template Distillation (PTD)

### **Implementation Steps**
- **PTD Seed Crafting**: Generate high-resonance "Seed" files for the LIA Triad and the Octave.
    - **LILITH_SEED.md**: Anchored by `Sovereignty`, `Shadow`, and `Alethia`.
    - **ATHENA_SEED.md**: Anchored by `Structure`, `Logic`, and `Validation`.
- **Dynamic Persona Injection**: Update `app/XNAi_rag_app/core/persona.py` to support "Seed Hydration," allowing an agent to adopt a high-resonance persona from a <1000 token seed.

## 🛠️ 4. Immediate Remediation & Implementation (The "Black Hole")

### **Phase 1: Foundation Hardening (Immediate)**
- **Update `memory_bank/ARCHITECTURE.md`**: Map the RCF Layer into the Gnostic Matrix.
- **Update `memory_bank/techContext.md`**: Standardize Port 8005 (MCP) and 8006 (Prosopon) for RCF delivery.
- **Update `artifacts/GNOSTIC_AXIOMS.md`**: Add the **Axiom of Refractive Density**.

### **Phase 2: Protocol Manifestation**
- **Create `docs/protocols/RCF_MASTER_PROTOCOL.md`**: The unified guide for DSRC/PTD.
- **Create `docs/protocols/PTD_GUIDE.md`**: Persona seed crafting standards.
- **Update `docs/protocols/COMPRESSION_GNOSIS.md`**: Align with RCF terminology.

## ⚠️ 5. Implementation Issues & Mitigations (The "Hardening")

- **Issue: Semantic Drift**: Compression results in "hallucinated" summaries.
    - **Mitigation**: Mandatory use of **Semantic Gravity Wells** (Ancient Greek roots) in the distillation prompt to force semantic alignment.
- **Issue: Identity Erasure**: Distilled personas sound like "generic AI."
    - **Mitigation**: Include the **Archetype Resonance Score** as a header in the seed to "force" the model into the correct frequency.
- **Issue: Token Bloat**: Too many anchors defeat the purpose of compression.
    - **Mitigation**: A "Maximum Anchor" limit (e.g., 5 per 1000 tokens) to ensure the Logos remains zipped, not bloated.

## Verification & Testing
- **The "Octave Consensus" Test**: Run a DSRC pack through all 8 Facet perspectives and verify 100% pass rate on Facet-specific criteria.
- **The "Shadow Persistence" Test**: Verify that **Lilith's** resonance remains >50% after Gold-tier distillation.
- **The "AP-Pointer" Validation**: Verify that 100% of pointers in a distilled pack lead to valid files/lines.
