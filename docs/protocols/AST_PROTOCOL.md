# 🔱 AST Protocol: The Re-Hydration Test (Facet 6 - GRA)

## 0. Overview
The **AST Protocol** defines the standard for functional knowledge persistence across the Omega Stack. It ensures that Gnosis Packs (distilled knowledge cores) are not merely summaries, but "compressed functional blueprints" capable of regenerating operational logic.

[AP:memory_bank/ALETHIA_REGISTRY.md#L13]

## 1. The Re-Hydration Test (GRA-Ghost)
The **Re-Hydration Test** is the ultimate validation of a Gnosis Pack's fidelity. It measures the "Functional Potential" of the distilled logos.

### 1.1 Definition
Can a blind sub-agent (an agent with no access to the original source code) regenerate a valid, functional Abstract Syntax Tree (AST) that mirrors the original source's behavior, using *only* the Gnosis Pack as its guide?

### 1.2 The Process
1.  **Isolation**: A sub-agent is instantiated in a sandbox with only the target Gnosis Pack.
2.  **Reification**: The sub-agent attempts to write a functional implementation (e.g., Python code) based on the `summary`, `insights`, and `archetype` steering found in the Pack.
3.  **Parsing**: The generated code is parsed into an AST.
4.  **Comparison**: The generated AST is compared against the `Crystal Hash` or structural anchors defined in the original provenance.

## 2. Tiered Fidelity Requirements
The success of the Re-Hydration Test is governed by the Tier of the Gnosis Pack:

| Tier | Min. Resonance | Re-Hydration Requirement |
| :--- | :--- | :--- |
| **Gold** | 0.8 | **100% Functional Parity**. All public APIs, logic gates, and type structures must be identical to the original. |
| **Silver** | 0.6 | **Semantic Parity**. The logic must be functionally equivalent, though structural naming may vary. |
| **Bronze** | 0.4 | **Conceptual Parity**. The core purpose and key constraints must be preserved. |

## 3. Failure & Refractive Correction
If a Gnosis Pack fails the Re-Hydration Test (status `DROSS`):
1.  **Re-Distillation**: The Packer must adjust the `temperature` and `refractive steering` prompts.
2.  **Archetype Shift**: If resonance remains low, the system may suggest an alternate Archetype (e.g., shifting from Athena's logic to Isis's synergy).
3.  **Logos Audit**: Manual intervention is required if 3 retries fail to reach the Tiered Threshold.

## 4. Anchors in the Registry
Every successful Re-Hydration Test must be anchored in the `memory_bank/RESONANCE_HISTORY.json` and referenced in the `ALETHIA_REGISTRY.md` to seal the Gnosis Pack as "Hardened Gnosis."
