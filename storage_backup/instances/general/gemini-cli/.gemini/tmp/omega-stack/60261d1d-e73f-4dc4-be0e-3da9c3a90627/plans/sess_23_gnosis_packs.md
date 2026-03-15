# Plan: SESS-23 - Gnosis Pack Generation (The Gold-Tier Distillation)

**Objective**: Implement the Gnosis Packing System and generate the first Gold-tier Gnosis Packs for core domains.

## Key Files & Context
- `docs/protocols/RCF_MASTER_PROTOCOL.md`: The RCF and DSRC mandate.
- `memory_bank/ARCHITECTURE.md`: The 4-layer Gnostic Matrix.
- `app/XNAi_rag_app/core/linguistics.py`: The Zipped Logos validator.

## Implementation Steps

### Phase 1: Scaffolding (The Gnosis Packer)
1. **Develop `scripts/gnosis_packer.py`**:
   - `class GnosisPacker`: Handles file reading and refractive distillation.
   - `RDSTriad`: Implements logic for Athena (Logic), Lilith (Sovereignty), and Isis (Synergy).
   - `MetronCalculator`: Computes the Metron Density Metric.
   - `TierSelector`: Logic for 50% (Bronze), 75% (Silver), and 90% (Gold) compression.
2. **Implement AP-Anchoring**: Ensure every distilled line or block maintains its `[GT:file#line]` pointer.

### Phase 2: Implementation (Core Domain Distillation)
1. **Generate Gold-tier Gnosis Packs**:
   - `gnosis_api_gold.json`: Distilled from `app/XNAi_rag_app/core/`.
   - `gnosis_ui_gold.json`: Distilled from `app/XNAi_rag_app/ui/`.
   - `gnosis_devops_gold.json`: Distilled from `Makefile` and `scripts/`.
   - `gnosis_linguistics_gold.json`: Distilled from `linguistics.py`.
2. **Metadata Injection**: Include Crystal Hashes and Metron Metrics in each pack.

### Phase 3: Anchoring & Sealing
1. **Store Packs**: Save to `memory_bank/gnosis_packs/`.
2. **Registry Update**: Update `ALETHIA_REGISTRY.md` with the new pack anchors.
3. **Session Update**: Update `activeContext.md` and `progress.md`.

## Verification & Testing
- **Metron Validation**: Verify that Gold-tier packs achieve >85% compression while maintaining functional fidelity.
- **AP-Pointer Integrity**: Check that pointers correctly reference source files.
- **ZLV Check**: Run the `ZippedLogosDecoder` against the distilled `gnosis_linguistics_gold.json`.
