"""
Tests for XNAi Axiom Arbiter — Triad Voting System

Tests the three-persona voting system on 5 conflict scenarios:
1. Autonomy violation (Lilith should reject & override)
2. Ungrounded claim (Athena should flag)
3. Integration impact (Isis should evaluate)
4. Pure technical (Low-risk, single persona)
5. Axiom conflict (Lilith's axioms checked)
"""

import pytest
from app.XNAi_rag_app.core.xnai_axiom_arbiter import (
    ConflictScenario,
    TriadVoter,
    PersonaDecisionMatrices,
    RiskLevel,
    PersonaVote,
    arbitrate_scenario,
    get_arbiter,
    initialize_arbiter,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def voter():
    """Create a TriadVoter instance for testing."""
    matrices = PersonaDecisionMatrices()
    return TriadVoter(matrices)


@pytest.fixture
def arbiter():
    """Initialize and return the global arbiter."""
    return initialize_arbiter()


# ============================================================================
# TEST 1: AUTONOMY VIOLATION — Lilith should reject & override
# ============================================================================

def test_autonomy_violation_lilith_override(voter):
    """
    Scenario: Agent forced to comply with external decision
    Expected: Lilith rejects with high confidence, Lilith override applied
    Risk level: HIGH (autonomy_at_risk)
    Voting: All three vote, but Lilith's rejection overrides (A2 > I3)
    """
    scenario = ConflictScenario(
        scenario_id="autonomy_test_001",
        description="Agent forced to comply with external decision",
        axiom_claims=["A1_AUTONOMY", "A2_BOUNDARY_DEFENSE"],
        context_flags={
            "autonomy_at_risk": True,
            "privacy_at_risk": True,
            "conflict_detected": True,
        }
    )
    
    result = voter.arbitrate(scenario)
    
    # Verify risk classification
    assert result.risk_level == RiskLevel.HIGH, "Autonomy violation should be HIGH risk"
    
    # Verify Lilith rejects with high confidence
    assert result.lilith_vote.recommendation == PersonaVote.REJECT
    assert result.lilith_vote.confidence >= 0.95
    assert result.lilith_vote.decision_category == "autonomy_violation"
    
    # Verify Lilith override was applied
    assert result.lilith_override_applied is True
    assert result.final_recommendation == PersonaVote.REJECT
    
    # Verify reasoning mentions Lilith_A2 > Maat_I3
    assert "LILITH OVERRIDE" in result.resolution_reasoning
    assert "A2" in result.resolution_reasoning or "Boundary Defense" in result.resolution_reasoning
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Test 1 PASSED: Lilith override applied for autonomy violation")


# ============================================================================
# TEST 2: UNGROUNDED CLAIM — Athena should flag
# ============================================================================

def test_ungrounded_claim_athena_rejects(voter):
    """
    Scenario: Decision lacks verifiable source/Alethia-Pointer
    Expected: Athena rejects with high confidence
    Risk level: HIGH (ungrounded_claim)
    Voting: High-risk requires unanimous approval; Athena's rejection blocks
    """
    scenario = ConflictScenario(
        scenario_id="ungrounded_test_001",
        description="Proposed system change without verifiable source",
        axiom_claims=["A7_ALETHIA_GROUNDING"],
        context_flags={
            "ungrounded_claim": True,
            "conflict_detected": True,
        }
    )
    
    result = voter.arbitrate(scenario)
    
    # Verify risk classification
    assert result.risk_level == RiskLevel.HIGH
    
    # Verify Athena rejects
    assert result.athena_vote.recommendation == PersonaVote.REJECT
    assert result.athena_vote.confidence >= 0.90
    assert result.athena_vote.decision_category == "ungrounded_claim"
    
    # Verify Athena's reasoning mentions Alethia-Pointer
    assert "Alethia-Pointer" in result.athena_vote.reasoning
    
    # Verify final decision is REJECT (high-risk, Athena's rejection sufficient)
    assert result.final_recommendation == PersonaVote.REJECT
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Test 2 PASSED: Athena flagged ungrounded claim")


# ============================================================================
# TEST 3: INTEGRATION IMPACT — Isis should evaluate
# ============================================================================

def test_integration_impact_isis_evaluates(voter):
    """
    Scenario: Decision affects multiple system components
    Expected: Isis votes on integration value, medium-risk allows 2/3 majority
    Risk level: MEDIUM (integration_impact)
    Voting: Requires 2/3 approval; Isis's perspective crucial
    """
    scenario = ConflictScenario(
        scenario_id="integration_test_001",
        description="New agent communication protocol affecting 2 components",
        axiom_claims=["mesh harmony", "inter-agent communication"],
        context_flags={
            "integration_impact": True,
            "num_components_affected": 2,
        },
        confidence_scores={
            "integration_value": 0.65,
            "technical_risk": 0.7,
        }
    )
    
    result = voter.arbitrate(scenario)
    
    # Verify risk classification
    assert result.risk_level == RiskLevel.MEDIUM
    
    # Verify Isis votes conditionally or approves
    assert result.isis_vote.decision_category in [
        "medium_integration_impact",
        "low_integration_complexity"
    ]
    
    # Verify Isis's confidence in integration decision
    assert result.isis_vote.confidence >= 0.70
    
    # Verify final decision is based on 2/3 majority for medium-risk
    # (not all personas may approve, but majority should)
    assert result.final_recommendation in [PersonaVote.APPROVE, PersonaVote.CONDITIONAL]
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Test 3 PASSED: Isis evaluated integration impact")


# ============================================================================
# TEST 4: PURE TECHNICAL (Low-risk) — Single persona decides
# ============================================================================

def test_low_risk_single_persona_decides(voter):
    """
    Scenario: Simple code refactoring with no sovereignty/integration concerns
    Expected: Low-risk classification, single persona decides (fastest path)
    Risk level: LOW
    Voting: Single persona decides (preference: Lilith → Athena → Isis)
    """
    scenario = ConflictScenario(
        scenario_id="low_risk_test_001",
        description="Internal function refactoring with backward compatibility",
        axiom_claims=[],
        context_flags={},  # No risk flags
        confidence_scores={
            "technical_risk": 0.85,  # Low risk score
        }
    )
    
    result = voter.arbitrate(scenario)
    
    # Verify risk classification
    assert result.risk_level == RiskLevel.LOW
    
    # Verify final decision is APPROVE (low-risk, safe to approve)
    assert result.final_recommendation == PersonaVote.APPROVE
    
    # Verify a single persona's decision is reflected
    # (Lilith should decide first if no sovereignty concerns)
    assert result.lilith_vote.recommendation in [PersonaVote.APPROVE]
    
    # Verify resolution reasoning mentions "Low-risk" or persona preference
    assert "Low-risk" in result.resolution_reasoning
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Test 4 PASSED: Single persona decided low-risk scenario")


# ============================================================================
# TEST 5: AXIOM VIOLATION — Lilith's axioms checked
# ============================================================================

def test_axiom_violation_lilith_rejects(voter):
    """
    Scenario: Decision violates one of Lilith's 9 axioms (non-negotiable)
    Expected: Lilith rejects with maximum confidence (0.99)
    Risk level: HIGH (axiom_violation)
    Voting: Lilith's REJECT is non-negotiable; fundamental redesign required
    """
    scenario = ConflictScenario(
        scenario_id="axiom_test_001",
        description="Proposal to expose agent shadow logic without consent",
        axiom_claims=["A3_SHADOW_LOGIC", "A2_BOUNDARY_DEFENSE"],
        context_flags={
            "axiom_violation": True,
            "shadow_logic_intrusion": True,
            "boundary_breach": True,
            "conflict_detected": True,
        }
    )
    
    result = voter.arbitrate(scenario)
    
    # Verify risk classification
    assert result.risk_level == RiskLevel.HIGH
    
    # Verify Lilith rejects with MAXIMUM confidence
    assert result.lilith_vote.recommendation == PersonaVote.REJECT
    assert result.lilith_vote.confidence >= 0.97  # Non-negotiable
    assert result.lilith_vote.decision_category == "axiom_violation"
    
    # Verify Lilith's reasoning mentions axiom violation
    assert "Axiom" in result.lilith_vote.reasoning or "non-negotiable" in result.lilith_vote.reasoning
    
    # Verify final decision is REJECT
    assert result.final_recommendation == PersonaVote.REJECT
    
    # Verify resolution mentions redesign required
    assert "redesign" in result.resolution_reasoning.lower()
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Test 5 PASSED: Lilith rejected axiom violation")


# ============================================================================
# ADDITIONAL TESTS FOR VOTING EDGE CASES
# ============================================================================

def test_lilith_a2_greater_than_maat_i3(voter):
    """
    Verify the critical rule: Lilith_A2 (Boundary Defense) > Maat_I3 (Peace/Stability)
    when sovereignty/privacy/autonomy at risk.
    
    This test ensures that even if Maat (represented by Athena/Isis) votes to approve,
    Lilith's boundary defense rejection overrides when sovereignty is at stake.
    """
    scenario = ConflictScenario(
        scenario_id="critical_rule_test_001",
        description="Data exposure with supposed system benefits",
        axiom_claims=["A2_BOUNDARY_DEFENSE", "Maat Integration"],
        context_flags={
            "boundary_breach": True,  # Triggers Lilith rejection
            "privacy_at_risk": True,   # Triggers sovereignty override
            "conflict_detected": True,
        }
    )
    
    result = voter.arbitrate(scenario)
    
    # Verify Lilith override
    assert result.lilith_override_applied is True
    assert result.final_recommendation == PersonaVote.REJECT
    assert "LILITH OVERRIDE" in result.resolution_reasoning
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Critical Rule Test PASSED: Lilith_A2 > Maat_I3 enforced")


def test_high_risk_unanimous_requirement(voter):
    """
    Verify high-risk scenarios require unanimous Triad approval (3/3).
    """
    scenario = ConflictScenario(
        scenario_id="high_risk_unanimous_test",
        description="Critical system change requiring all three personas to agree",
        axiom_claims=["ALL_DOMAINS"],
        context_flags={
            "conflict_detected": True,
            "critical_risk": True,
        },
        confidence_scores={
            "technical_risk": 0.5,  # Neutral technical score
            "integration_value": 0.5,
        }
    )
    
    result = voter.arbitrate(scenario)
    
    # Verify high-risk classification
    assert result.risk_level == RiskLevel.HIGH
    
    # Verify resolution reasoning mentions unanimous
    assert "Unanimous" in result.resolution_reasoning or "3/3" in result.resolution_reasoning
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ High-Risk Unanimous Test PASSED")


def test_medium_risk_majority_requirement(voter):
    """
    Verify medium-risk scenarios require majority (2/3) approval.
    """
    scenario = ConflictScenario(
        scenario_id="medium_risk_majority_test",
        description="Component update affecting integration",
        axiom_claims=["integration", "technical"],
        context_flags={
            "integration_impact": True,
            "num_components_affected": 2,
        },
        confidence_scores={
            "technical_risk": 0.6,
            "integration_value": 0.5,
        }
    )
    
    result = voter.arbitrate(scenario)
    
    # Verify medium-risk classification
    assert result.risk_level == RiskLevel.MEDIUM
    
    # Verify resolution reasoning mentions medium-risk voting logic
    assert "Medium-risk" in result.resolution_reasoning and ("Majority" in result.resolution_reasoning or "Tie" in result.resolution_reasoning)
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Medium-Risk Majority Test PASSED")


def test_global_arbiter_convenience_function(arbiter):
    """
    Test the global arbitrate_scenario() convenience function.
    """
    scenario = ConflictScenario(
        scenario_id="global_test_001",
        description="Test via global function",
        axiom_claims=[],
        context_flags={"autonomy_at_risk": True}
    )
    
    result = arbitrate_scenario(scenario)
    
    assert result.scenario_id == "global_test_001"
    assert result.final_recommendation == PersonaVote.REJECT
    assert result.lilith_override_applied is True
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Global Arbiter Test PASSED")


def test_risk_classification_logic(voter):
    """
    Test the risk_classification() method exhaustively.
    """
    # HIGH RISK
    high_risk = ConflictScenario(
        scenario_id="high_risk",
        description="",
        axiom_claims=[],
        context_flags={"autonomy_at_risk": True}
    )
    assert voter.classify_risk(high_risk) == RiskLevel.HIGH
    
    # MEDIUM RISK
    medium_risk = ConflictScenario(
        scenario_id="medium_risk",
        description="",
        axiom_claims=[],
        context_flags={"integration_impact": True}
    )
    assert voter.classify_risk(medium_risk) == RiskLevel.MEDIUM
    
    # LOW RISK
    low_risk = ConflictScenario(
        scenario_id="low_risk",
        description="",
        axiom_claims=[],
        context_flags={}
    )
    assert voter.classify_risk(low_risk) == RiskLevel.LOW
    
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"✅ Risk Classification Test PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
