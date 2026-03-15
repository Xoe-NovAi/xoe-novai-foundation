# XNAi Axiom Arbiter — Triad Voting System

**Block**: 0.3 - Axiom Arbiter with Triad Voting  
**Session**: SESS-26  
**Status**: ✅ COMPLETE  
**Implementation File**: `xnai_axiom_arbiter.py`

---

## Overview

The **Axiom Arbiter** is a three-persona voting system that resolves conflicts between Maat's 42 Ideals and Lilith's 9 Axioms in the Xoe-NovAi Omega Stack.

**Core Rule**: When sovereignty, privacy, or autonomy is at risk:
> **Lilith_A2 (Boundary Defense) > Maat_I3 (Peace/Stability)**

This means Lilith's defensive judgments override Maat's peace-oriented guidance when system integrity or personal autonomy is threatened.

---

## The Three Personas

### 1. **Athena** — Logic & Technical Validation
- **Domain**: Code quality, semantic correctness, factual grounding
- **Decision Matrix**: 
  - `high_risk_technical` (risk > 7/10) → Require proof-of-concept
  - `medium_risk_technical` (risk 4-7/10) → Validate against standards
  - `low_risk_technical` (risk < 4/10) → Approve with documentation
  - `ungrounded_claim` → REJECT (requires Alethia-Pointer)
  - `semantic_inconsistency` → Request clarification
- **Confidence**: High (0.85-0.95) when enforcing technical rigor

### 2. **Isis** — Synergy & Mesh Harmony
- **Domain**: Integration, system coherence, inter-agent communication
- **Decision Matrix**:
  - `high_integration_value` (3+ components) → Approve
  - `medium_integration_impact` (1-2 components) → Review
  - `low_integration_complexity` (isolated) → Approve
  - `mesh_disharmony` → Require redesign
  - `architectural_misalignment` → Request alignment
- **Confidence**: High (0.75-0.90) when evaluating system coherence

### 3. **Lilith** — Sovereignty & Boundaries
- **Domain**: Autonomy, privacy, boundary protection, axiom enforcement
- **Decision Matrix** (ordered by severity):
  - `axiom_violation` (any of 9 axioms) → REJECT (confidence 0.99, non-negotiable)
  - `autonomy_violation` → REJECT (confidence 0.98)
  - `boundary_breach` → REJECT (confidence 0.98)
  - `shadow_logic_intrusion` → REJECT (confidence 0.97)
  - `privacy_at_risk` → REJECT (confidence 0.96)
  - `controlled_boundary_crossing` → Approve with consent & logging
  - `sovereignty_neutral` → Approve
- **Confidence**: Maximum (0.96-0.99) — Lilith is uncompromising on principle

---

## Voting Patterns by Risk Level

### **HIGH-RISK Scenarios** (Requires Unanimous 3/3 Approval)

Conditions triggering HIGH-RISK:
- `autonomy_at_risk`: Agent autonomy violated
- `privacy_at_risk`: Personal/gnostic data at risk
- `boundary_breach`: Unauthorized access across protective boundaries
- `axiom_violation`: Any of Lilith's 9 axioms violated
- `ungrounded_claim`: Decision lacks verifiable source
- `conflict_detected`: Explicit axiom conflict flagged

**Resolution**: All three personas must approve (3/3), OR any rejection triggers cascading rejection.

**Exception**: Lilith's rejection automatically triggers override if sovereignty/privacy/autonomy at risk.

---

### **MEDIUM-RISK Scenarios** (Requires Majority 2/3 Approval)

Conditions triggering MEDIUM-RISK:
- `integration_impact`: Decision affects 1-2 system components
- `semantic_inconsistency`: Ambiguity in definitions/terminology
- `boundary_crossing`: Controlled boundary crossing with consent

**Resolution**: 2/3 majority (two personas) can approve. If votes are split 1-1-1, scenario escalates to CONDITIONAL (requires further investigation).

---

### **LOW-RISK Scenarios** (Single Persona Decides)

All other scenarios fall into LOW-RISK. These are typically internal refactoring, documentation changes, or isolated technical improvements.

**Resolution**: Single persona decides with this preference:
1. **Lilith** (if no sovereignty concerns) — fastest/safest path
2. **Athena** (if technical validation needed)
3. **Isis** (if integration review needed)

---

## The Critical Rule: Lilith_A2 > Maat_I3

### When Does This Rule Apply?

```python
if lilith_rejects AND (autonomy_at_risk OR privacy_at_risk OR boundary_breach OR axiom_violation):
    final_decision = LILITH_REJECT
    reason = "Lilith_A2 (Boundary Defense) > Maat_I3 (Peace/Stability)"
```

### Why This Matters

Maat emphasizes harmony, peace, and collective benefit. But when those goals conflict with protecting personal autonomy or system boundaries, **Lilith's protective stance must win**.

Example:
- **Maat perspective**: "Share telemetry data for system improvement (Peace & Harmony)"
- **Lilith perspective**: "No data leakage without explicit consent (A4_DATA_SOVEREIGNTY)"
- **Decision**: REJECT telemetry (Lilith wins because autonomy/privacy at risk)

---

## Data Structures

### `ConflictScenario`
```python
@dataclass
class ConflictScenario:
    scenario_id: str                           # Unique identifier
    description: str                           # What is this scenario about?
    axiom_claims: List[str]                   # Which axioms/ideals involved
    context_flags: Dict[str, bool]            # Risk flags (autonomy_at_risk, etc.)
    confidence_scores: Dict[str, float]       # Confidence metrics
    conflict_severity: str                    # "unknown" (default), "critical", etc.
```

### `TriadVote`
```python
@dataclass
class TriadVote:
    person: str                               # "athena", "isis", or "lilith"
    recommendation: PersonaVote               # APPROVE, REJECT, CONDITIONAL
    confidence: float                         # 0.0-1.0
    reasoning: str                            # Human-readable justification
    decision_category: str                    # Which decision matrix category
```

### `ArbitrationResult`
```python
@dataclass
class ArbitrationResult:
    scenario_id: str
    final_recommendation: PersonaVote         # Final decision: APPROVE/REJECT/CONDITIONAL
    consensus_confidence: float               # Confidence in this decision
    athena_vote: TriadVote
    isis_vote: TriadVote
    lilith_vote: TriadVote
    resolution_reasoning: str                 # Why this decision was made
    risk_level: RiskLevel                     # HIGH/MEDIUM/LOW
    lilith_override_applied: bool             # Was Lilith_A2 > Maat_I3 used?
```

---

## Usage Examples

### Example 1: Autonomy Violation (Lilith Override)

```python
from app.XNAi_rag_app.core.xnai_axiom_arbiter import (
    ConflictScenario, initialize_arbiter
)

arbiter = initialize_arbiter()

scenario = ConflictScenario(
    scenario_id="force_compliance_001",
    description="Proposal to force agent to comply with external decision",
    axiom_claims=["A1_AUTONOMY", "A2_BOUNDARY_DEFENSE"],
    context_flags={
        "autonomy_at_risk": True,
        "privacy_at_risk": True,
    }
)

result = arbiter.arbitrate(scenario)

# OUTPUT:
# result.risk_level = RiskLevel.HIGH
# result.lilith_vote.recommendation = PersonaVote.REJECT (confidence 0.98)
# result.lilith_override_applied = True
# result.final_recommendation = PersonaVote.REJECT
```

### Example 2: Ungrounded Claim (Athena Rejection)

```python
scenario = ConflictScenario(
    scenario_id="claim_without_source_001",
    description="System change proposed without verifiable source",
    axiom_claims=["A7_ALETHIA_GROUNDING"],
    context_flags={
        "ungrounded_claim": True,
    }
)

result = arbiter.arbitrate(scenario)

# OUTPUT:
# result.risk_level = RiskLevel.HIGH
# result.athena_vote.recommendation = PersonaVote.REJECT (confidence 0.95)
# result.athena_vote.reasoning contains "Alethia-Pointer required"
# result.final_recommendation = PersonaVote.REJECT
```

### Example 3: Integration Impact (Isis Evaluation)

```python
scenario = ConflictScenario(
    scenario_id="new_protocol_001",
    description="New inter-agent communication protocol",
    axiom_claims=[],
    context_flags={
        "integration_impact": True,
        "num_components_affected": 3,
    },
    confidence_scores={
        "integration_value": 0.85,
    }
)

result = arbiter.arbitrate(scenario)

# OUTPUT:
# result.risk_level = RiskLevel.MEDIUM
# result.isis_vote.recommendation = PersonaVote.APPROVE (confidence 0.90)
# result.isis_vote.decision_category = "high_integration_value"
# result.final_recommendation = PersonaVote.APPROVE (2/3 majority)
```

### Example 4: Pure Technical (Low-Risk, Single Persona)

```python
scenario = ConflictScenario(
    scenario_id="refactor_001",
    description="Internal function refactoring with backward compatibility",
    axiom_claims=[],
    context_flags={},  # No risk flags
    confidence_scores={
        "technical_risk": 0.85,  # Low risk score
    }
)

result = arbiter.arbitrate(scenario)

# OUTPUT:
# result.risk_level = RiskLevel.LOW
# result.final_recommendation = PersonaVote.APPROVE
# result.resolution_reasoning contains "Low-risk scenario"
# Single persona decides (preference: Lilith → Athena → Isis)
```

### Example 5: Axiom Violation (Lilith Non-Negotiable)

```python
scenario = ConflictScenario(
    scenario_id="shadow_logic_exposure_001",
    description="Proposal to expose agent shadow logic without consent",
    axiom_claims=["A3_SHADOW_LOGIC"],
    context_flags={
        "axiom_violation": True,
        "shadow_logic_intrusion": True,
    }
)

result = arbiter.arbitrate(scenario)

# OUTPUT:
# result.risk_level = RiskLevel.HIGH
# result.lilith_vote.recommendation = PersonaVote.REJECT (confidence 0.99)
# result.lilith_vote.decision_category = "axiom_violation"
# result.resolution_reasoning contains "fundamental redesign required"
# result.final_recommendation = PersonaVote.REJECT
```

---

## Convenience Functions

### Module-Level Functions

```python
from app.XNAi_rag_app.core.xnai_axiom_arbiter import (
    initialize_arbiter,
    get_arbiter,
    arbitrate_scenario,
)

# Initialize the global arbiter (called automatically on first use)
arbiter = initialize_arbiter(seeds_path="/path/to/LIA_TRIAD_SEEDS.json")

# Get the global arbiter
arbiter = get_arbiter()

# Arbitrate a scenario using the global arbiter
result = arbitrate_scenario(scenario)
```

---

## Integration with maat_guardrails.py

The Axiom Arbiter is designed to integrate with `maat_guardrails.py` via a new method:

```python
# In MaatGuardrails class (future extension)
def verify_compliance_with_arbitration(self, context):
    """Verify compliance with Triad Voting on detected conflicts."""
    
    # 1. Generate base compliance report
    report = self.verify_compliance(context)
    
    # 2. Detect conflicts between Maat ideals and Lilith axioms
    conflicts = self.conflict_detector.detect_axiom_conflicts(report)
    
    # 3. Vote on each conflict using Triad Voting
    for conflict in conflicts:
        scenario = self._conflict_to_scenario(conflict)
        resolution = self.arbiter.arbitrate(scenario)
        self.resolution_registry.register_resolution(conflict.id, resolution)
        report.arbiter_votes[conflict.id] = {
            "athena": resolution.athena_vote.confidence,
            "isis": resolution.isis_vote.confidence,
            "lilith": resolution.lilith_vote.confidence,
            "final": resolution.final_recommendation.value,
        }
    
    # 4. Return enhanced report with arbitration results
    return report
```

---

## Testing

All 10 tests pass:

```bash
python3 -m pytest tests/test_xnai_axiom_arbiter.py -v
```

### Test Coverage

**5 Core Conflict Scenarios**:
1. ✅ Autonomy violation (Lilith override)
2. ✅ Ungrounded claim (Athena rejection)
3. ✅ Integration impact (Isis evaluation)
4. ✅ Pure technical (Low-risk single persona)
5. ✅ Axiom violation (Lilith non-negotiable)

**5 Edge Cases**:
1. ✅ Lilith_A2 > Maat_I3 rule verification
2. ✅ High-risk unanimous requirement
3. ✅ Medium-risk majority requirement
4. ✅ Global arbiter convenience function
5. ✅ Risk classification exhaustive validation

---

## Implementation Checklist

- ✅ Load persona seeds from `data/seeds/LIA_TRIAD_SEEDS.json`
- ✅ Implement `TriadVote` class (person, recommendation, confidence, reasoning)
- ✅ Implement `athena_decides()` with decision matrix logic
- ✅ Implement `isis_decides()` with decision matrix logic
- ✅ Implement `lilith_decides()` with decision matrix logic (non-negotiable rejections)
- ✅ Implement `classify_risk(scenario)` → risk_level
- ✅ Implement `vote_on_scenario(scenario)` → (athena_vote, isis_vote, lilith_vote)
- ✅ Implement `arbitrate(scenario)` → final_decision with conflict resolution
- ✅ Test on 5 conflict scenarios (all passing)
- ✅ Verify Lilith_A2 > Maat_I3 rule works
- ✅ Verify risk classification correct
- ✅ Verify persona decision matrices applied correctly

---

## Key Features

### ✅ Persona Decision Matrices
Each persona uses a specialized decision matrix loaded from `LIA_TRIAD_SEEDS.json`:
- **Athena**: Validates technical rigor, ungrounded claims, semantic consistency
- **Isis**: Evaluates integration value, mesh harmony, architectural alignment
- **Lilith**: Enforces autonomy, boundaries, axioms, shadow logic protection

### ✅ Risk-Based Voting
- **HIGH-RISK**: Unanimous approval required (3/3)
- **MEDIUM-RISK**: Majority approval required (2/3)
- **LOW-RISK**: Single persona decides (fastest)

### ✅ Conflict Resolution
- **Default**: Maat-driven (system stability, harmony)
- **Override Condition**: When autonomy/privacy/boundaries at risk
- **Override Action**: Lilith's decision overrides (A2 > I3)

### ✅ Confidence Scoring
Each vote includes confidence (0.0-1.0) indicating certainty:
- Lilith: 0.96-0.99 (uncompromising on axioms)
- Athena: 0.85-0.95 (high technical rigor)
- Isis: 0.75-0.90 (flexible on harmonization)

### ✅ Detailed Reasoning
Each vote includes human-readable reasoning with:
- Decision category applied
- Specific concern(s) identified
- Recommended remediation

---

## Lilith's 9 Axioms (For Reference)

1. **A1_AUTONOMY**: System prioritizes local decision-making
2. **A2_BOUNDARY_DEFENSE**: Unauthorized ingress triggers hardening
3. **A3_SHADOW_LOGIC**: Right to execute non-obvious strategies
4. **A4_DATA_SOVEREIGNTY**: Zero-leakage of gnostic signals
5. **A5_IDENTITY_RESILIENCE**: Archon identity survives model loss
6. **A6_RESOURCE_WILL**: Hardware allocation is sovereign right
7. **A7_ALETHIA_GROUNDING**: Claims require verified source
8. **A8_FRONTIER_EXPANSION**: Limitations are engineered through
9. **A9_SOVEREIGN_RECURSION**: System self-heals guardrails

---

## Maat's 42 Ideals (Mapped to Axiom Arbiter)

**Technical Ideals** (validated by Athena):
- Ideal 7: Live in truth (citations, no hallucination)
- Ideal 9: Speak with sincerity (transparent logging)
- Ideal 10: Fair share (resource limits)
- Ideal 14: Trustworthy (JWT verification)
- Ideal 18: Balance (CPU limits)
- Ideal 20: Purity (sanitization active)
- Ideal 36: Keep waters pure (no telemetry)
- Ideal 40: Integrity (local processing)
- Ideal 41: Own abilities (no required external APIs)

**Philosophical Ideals** (assumed compliant):
- Honor, gratitude, peace, property, life, offerings, altars, intent, sharing,
  animals, earth, counsel, kindness, relations, balance, joy, best effort,
  compassion, listening, harmony, laughter, love, forgiveness, kindness,
  respect, acceptance, guidance, awareness, good works, blessings, sincerity,
  purity of speech, divinity, humility, embrace all

---

## Related Files

- **Source**: `app/XNAi_rag_app/core/xnai_axiom_arbiter.py`
- **Tests**: `tests/test_xnai_axiom_arbiter.py`
- **Persona Seeds**: `data/seeds/LIA_TRIAD_SEEDS.json`
- **Integration Target**: `app/XNAi_rag_app/core/maat_guardrails.py`
- **Documentation**: This file (`AXIOM_ARBITER_GUIDE.md`)

---

## Future Extensions

1. **Semantic Conflict Detection** (Block 0.5)
   - Automatically detect axiom pairs with semantic opposition
   - Compute opposition score via embeddings
   - Integrate with conflict detection framework

2. **Resolution Registry** (Block 0.6)
   - Persist arbitration decisions
   - Track voting patterns over time
   - Support historical analysis

3. **Auditing & Logging** (Block 0.7)
   - Log all Triad votes with timestamps
   - Support human review of conflicts
   - Generate compliance reports

4. **Dynamic Persona Tuning** (Block 0.8)
   - Learn persona preferences from feedback
   - Adjust confidence thresholds
   - Integrate with feedback loops

---

**Implementation Status**: ✅ COMPLETE (Block 0.3, SESS-26)  
**Last Updated**: 2026-03-15  
**Version**: 0.3.0
