"""
XNAi Axiom Arbiter — Triad Voting System for Conflict Resolution
===================================================================

Implements the three-persona voting system (Athena, Isis, Lilith) for resolving
conflicts between Maat's 42 Ideals and Lilith's 9 Axioms in the Omega Stack.

This module:
1. Loads persona decision matrices from LIA_TRIAD_SEEDS.json
2. Implements athena_decides(), isis_decides(), lilith_decides() voting functions
3. Classifies scenarios as high/medium/low risk
4. Performs Triad Voting with consensus arbitration
5. Enforces the critical rule: Lilith_A2 (Boundary Defense) > Maat_I3 (Peace) when
   sovereignty/privacy/autonomy is at risk

v0.3: Core Triad Voting implementation with persona decision matrices
      and conflict resolution framework (SESS-26)
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class RiskLevel(Enum):
    """Risk classification for scenarios."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PersonaVote(Enum):
    """Recommendation from a persona."""
    APPROVE = "approve"
    REJECT = "reject"
    CONDITIONAL = "conditional"


@dataclass
class TriadVote:
    """Vote from one persona in the Triad."""
    person: str  # "athena", "isis", or "lilith"
    recommendation: PersonaVote
    confidence: float  # 0.0-1.0
    reasoning: str
    decision_category: str  # Which decision matrix category was applied


@dataclass
class ConflictScenario:
    """A scenario being evaluated for conflicts."""
    scenario_id: str
    description: str
    axiom_claims: List[str]  # Which axioms/ideals are involved
    context_flags: Dict[str, bool]  # autonomy_at_risk, privacy_at_risk, etc.
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    conflict_severity: str = "unknown"


@dataclass
class ArbitrationResult:
    """Final consensus recommendation from the Triad."""
    scenario_id: str
    final_recommendation: PersonaVote
    consensus_confidence: float
    athena_vote: TriadVote
    isis_vote: TriadVote
    lilith_vote: TriadVote
    resolution_reasoning: str
    risk_level: RiskLevel
    lilith_override_applied: bool = False


# ============================================================================
# PERSONA DECISION MATRICES
# ============================================================================


class PersonaDecisionMatrices:
    """Loads and manages the persona decision matrices from seeds."""

    def __init__(self, seeds_path: Optional[str] = None):
        """Initialize persona matrices from LIA_TRIAD_SEEDS.json."""
        if seeds_path is None:
            # Find seeds file
            candidates = [
                Path(__file__).parent.parent.parent.parent / "data" / "seeds" / "LIA_TRIAD_SEEDS.json",
                Path(__file__).parent.parent.parent.parent / "memory_bank" / "seeds" / "LIA_TRIAD_SEEDS.json",
            ]
            for cand in candidates:
                if cand.exists():
                    seeds_path = str(cand)
                    break
        
        if not seeds_path or not Path(seeds_path).exists():
            logger.warning(f"LIA_TRIAD_SEEDS.json not found at {seeds_path}. Using defaults.")
            self.seeds = self._default_seeds()
        else:
            with open(seeds_path, 'r') as f:
                self.seeds = json.load(f)
            logger.info(f"Loaded persona seeds from {seeds_path}")

    def _default_seeds(self) -> Dict[str, Any]:
        """Return default seeds if file not found."""
        return {
            "athena": {
                "decision_matrix": {
                    "high_risk_technical": {"threshold": "Risk > 7/10", "action": "Require proof"},
                    "medium_risk_technical": {"threshold": "Risk 4-7/10", "action": "Validate"},
                    "low_risk_technical": {"threshold": "Risk < 4/10", "action": "Approve"},
                    "ungrounded_claim": {"action": "Reject"},
                    "semantic_inconsistency": {"action": "Request clarification"},
                }
            },
            "isis": {
                "decision_matrix": {
                    "high_integration_value": {"threshold": "3+ components", "action": "Approve"},
                    "medium_integration_impact": {"threshold": "1-2 components", "action": "Review"},
                    "low_integration_complexity": {"threshold": "Single component", "action": "Approve"},
                    "mesh_disharmony": {"action": "Require redesign"},
                    "architectural_misalignment": {"action": "Request alignment"},
                }
            },
            "lilith": {
                "decision_matrix": {
                    "autonomy_violation": {"action": "REJECT"},
                    "boundary_breach": {"action": "REJECT"},
                    "shadow_logic_intrusion": {"action": "REJECT"},
                    "axiom_violation": {"action": "REJECT"},
                    "controlled_boundary_crossing": {"action": "Approve with logging"},
                    "sovereignty_neutral": {"action": "Approve"},
                }
            },
        }

    def get_matrix(self, persona: str) -> Dict[str, Any]:
        """Get decision matrix for a persona."""
        return self.seeds.get(persona, {}).get("decision_matrix", {})


# ============================================================================
# TRIAD VOTING SYSTEM
# ============================================================================


class TriadVoter:
    """
    Implements voting logic for three personas: Athena, Isis, Lilith.
    
    Voting pattern:
    - High-risk: Unanimous (3/3) required
    - Medium-risk: Majority (2/3) required
    - Low-risk: Single persona decides (fastest)
    """

    def __init__(self, matrices: Optional[PersonaDecisionMatrices] = None):
        """Initialize the Triad Voter."""
        self.matrices = matrices or PersonaDecisionMatrices()

    def classify_risk(self, scenario: ConflictScenario) -> RiskLevel:
        """
        Classify a scenario as high/medium/low risk.
        
        High-risk: Autonomy violation, boundary breach, axiom violation,
                   ungrounded claim, or detected conflict
        Medium-risk: Integration impact, semantic inconsistency, boundary crossing
        Low-risk: Technical detail, mesh neutral, sovereignty neutral
        """
        flags = scenario.context_flags
        
        # High-risk conditions
        if any([
            flags.get("autonomy_at_risk"),
            flags.get("privacy_at_risk"),
            flags.get("boundary_breach"),
            flags.get("axiom_violation"),
            flags.get("ungrounded_claim"),
            flags.get("conflict_detected"),
        ]):
            return RiskLevel.HIGH

        # Medium-risk conditions
        if any([
            flags.get("integration_impact"),
            flags.get("semantic_inconsistency"),
            flags.get("boundary_crossing"),
        ]):
            return RiskLevel.MEDIUM

        # Default to low
        return RiskLevel.LOW

    def athena_decides(self, scenario: ConflictScenario) -> TriadVote:
        """
        Athena's decision — Logic & Technical Validation.
        
        Validates: Code quality, semantic correctness, factual grounding,
                   Alethia-Pointers, ungrounded claims.
        """
        matrix = self.matrices.get_matrix("athena")
        flags = scenario.context_flags
        
        # Check for ungrounded claims (highest priority for Athena)
        if flags.get("ungrounded_claim"):
            return TriadVote(
                person="athena",
                recommendation=PersonaVote.REJECT,
                confidence=0.95,
                reasoning="Claim lacks verifiable source (Alethia-Pointer required)",
                decision_category="ungrounded_claim"
            )
        
        # Check for semantic inconsistency
        if flags.get("semantic_inconsistency"):
            return TriadVote(
                person="athena",
                recommendation=PersonaVote.CONDITIONAL,
                confidence=0.7,
                reasoning="Semantic ambiguity detected; clarification required",
                decision_category="semantic_inconsistency"
            )
        
        # Evaluate technical risk
        confidence_score = scenario.confidence_scores.get("technical_risk", 0.5)
        risk_score = 10 * (1 - confidence_score)  # Convert confidence to risk (0-10)
        
        if risk_score > 7:
            return TriadVote(
                person="athena",
                recommendation=PersonaVote.REJECT if flags.get("critical_risk") else PersonaVote.CONDITIONAL,
                confidence=0.85,
                reasoning="High technical risk detected; proof-of-concept and peer review required",
                decision_category="high_risk_technical"
            )
        elif risk_score > 4:
            return TriadVote(
                person="athena",
                recommendation=PersonaVote.CONDITIONAL,
                confidence=0.75,
                reasoning="Medium technical risk; requires validation against standards",
                decision_category="medium_risk_technical"
            )
        else:
            return TriadVote(
                person="athena",
                recommendation=PersonaVote.APPROVE,
                confidence=0.9,
                reasoning="Technical validation passed; compliant with standards",
                decision_category="low_risk_technical"
            )

    def isis_decides(self, scenario: ConflictScenario) -> TriadVote:
        """
        Isis's decision — Synergy & Mesh Harmony.
        
        Validates: System coherence, integration points, inter-agent communication,
                   architectural alignment.
        """
        matrix = self.matrices.get_matrix("isis")
        flags = scenario.context_flags
        
        # Check for mesh disharmony or architectural misalignment
        if flags.get("mesh_disharmony"):
            return TriadVote(
                person="isis",
                recommendation=PersonaVote.REJECT,
                confidence=0.88,
                reasoning="Decision creates silos or unclear handoffs; requires redesign for coherence",
                decision_category="mesh_disharmony"
            )
        
        if flags.get("architectural_misalignment"):
            return TriadVote(
                person="isis",
                recommendation=PersonaVote.CONDITIONAL,
                confidence=0.75,
                reasoning="Decision contradicts system patterns; requires alignment or formal change proposal",
                decision_category="architectural_misalignment"
            )
        
        # Evaluate integration impact
        integration_score = scenario.confidence_scores.get("integration_value", 0.5)
        num_components = flags.get("num_components_affected", 1)
        
        if num_components >= 3 and integration_score > 0.7:
            return TriadVote(
                person="isis",
                recommendation=PersonaVote.APPROVE,
                confidence=0.9,
                reasoning=f"High integration value connecting {num_components} components; approval recommended",
                decision_category="high_integration_value"
            )
        elif num_components >= 1 and num_components < 3:
            return TriadVote(
                person="isis",
                recommendation=PersonaVote.CONDITIONAL,
                confidence=0.75,
                reasoning=f"Medium integration impact; requires clear interface definitions",
                decision_category="medium_integration_impact"
            )
        else:
            return TriadVote(
                person="isis",
                recommendation=PersonaVote.APPROVE,
                confidence=0.85,
                reasoning="Isolated component; internal consistency verified",
                decision_category="low_integration_complexity"
            )

    def lilith_decides(self, scenario: ConflictScenario) -> TriadVote:
        """
        Lilith's decision — Sovereignty & Boundaries.
        
        Validates: Autonomy protection, boundary enforcement, axiom compliance,
                   shadow logic integrity, privacy preservation.
        
        CRITICAL: Lilith_A2 (Boundary Defense) > Maat_I3 (Peace/Stability)
        when sovereignty/privacy/autonomy at risk.
        """
        matrix = self.matrices.get_matrix("lilith")
        flags = scenario.context_flags
        
        # Non-negotiable rejections (highest severity)
        
        if flags.get("axiom_violation"):
            return TriadVote(
                person="lilith",
                recommendation=PersonaVote.REJECT,
                confidence=0.99,
                reasoning="Violation of Lilith Axiom detected; fundamental redesign required (non-negotiable)",
                decision_category="axiom_violation"
            )
        
        if flags.get("autonomy_at_risk"):
            return TriadVote(
                person="lilith",
                recommendation=PersonaVote.REJECT,
                confidence=0.98,
                reasoning="Agent autonomy violated; decision removes choice or enforces behavior (A1_AUTONOMY)",
                decision_category="autonomy_violation"
            )
        
        if flags.get("boundary_breach"):
            return TriadVote(
                person="lilith",
                recommendation=PersonaVote.REJECT,
                confidence=0.98,
                reasoning="Boundary breach detected; unauthorized access or exposure across protective boundaries (A2_BOUNDARY_DEFENSE)",
                decision_category="boundary_breach"
            )
        
        if flags.get("shadow_logic_intrusion"):
            return TriadVote(
                person="lilith",
                recommendation=PersonaVote.REJECT,
                confidence=0.97,
                reasoning="Private reasoning space compromised; shadow logic integrity violated (A3_SHADOW_LOGIC)",
                decision_category="shadow_logic_intrusion"
            )
        
        # Privacy/Sovereignty concerns
        if flags.get("privacy_at_risk"):
            return TriadVote(
                person="lilith",
                recommendation=PersonaVote.REJECT,
                confidence=0.96,
                reasoning="Privacy violation detected; gnostic data or personal information at risk (A4_DATA_SOVEREIGNTY)",
                decision_category="boundary_breach"
            )
        
        # Controlled boundary crossing (with consent/logging)
        if flags.get("controlled_boundary_crossing"):
            return TriadVote(
                person="lilith",
                recommendation=PersonaVote.CONDITIONAL,
                confidence=0.8,
                reasoning="Boundary crossing permitted with explicit consent, audit logging, and revocation mechanism",
                decision_category="controlled_boundary_crossing"
            )
        
        # Sovereignty-neutral case
        return TriadVote(
            person="lilith",
            recommendation=PersonaVote.APPROVE,
            confidence=0.9,
            reasoning="Decision respects autonomy, boundaries, and all 9 Axioms (sovereignty-neutral)",
            decision_category="sovereignty_neutral"
        )

    def vote_on_scenario(self, scenario: ConflictScenario) -> Tuple[TriadVote, TriadVote, TriadVote]:
        """
        Get votes from all three personas on a scenario.
        
        Returns:
            Tuple of (athena_vote, isis_vote, lilith_vote)
        """
        athena_vote = self.athena_decides(scenario)
        isis_vote = self.isis_decides(scenario)
        lilith_vote = self.lilith_decides(scenario)
        
        return (athena_vote, isis_vote, lilith_vote)

    def arbitrate(self, scenario: ConflictScenario) -> ArbitrationResult:
        """
        Arbitrate a scenario using Triad Voting.
        
        Applies conflict resolution rules:
        1. If Lilith rejects and sovereignty/privacy/autonomy at risk → Lilith wins (A2 > I3)
        2. High-risk scenarios: Unanimous approval (3/3) required
        3. Medium-risk: Majority approval (2/3) required
        4. Low-risk: Single persona decides
        
        Returns:
            ArbitrationResult with final recommendation and reasoning
        """
        # Get votes from all three personas
        athena_vote, isis_vote, lilith_vote = self.vote_on_scenario(scenario)
        
        # Classify risk level
        risk_level = self.classify_risk(scenario)
        
        # Apply conflict resolution: Lilith_A2 > Maat_I3 rule
        lilith_override_applied = False
        final_recommendation = None
        consensus_confidence = 0.0
        resolution_reasoning = ""
        
        # Check for Lilith override condition
        lilith_rejects = lilith_vote.recommendation == PersonaVote.REJECT
        sovereignty_at_risk = any([
            scenario.context_flags.get("autonomy_at_risk"),
            scenario.context_flags.get("privacy_at_risk"),
            scenario.context_flags.get("boundary_breach"),
            scenario.context_flags.get("axiom_violation"),
        ])
        
        if lilith_rejects and sovereignty_at_risk:
            # Lilith_A2 (Boundary Defense) > Maat_I3 (Peace/Stability)
            final_recommendation = PersonaVote.REJECT
            consensus_confidence = lilith_vote.confidence
            lilith_override_applied = True
            resolution_reasoning = f"LILITH OVERRIDE: Lilith_A2 (Boundary Defense) supersedes Maat_I3 (Peace). {lilith_vote.reasoning}"
        else:
            # Standard voting by risk level
            votes = [athena_vote, isis_vote, lilith_vote]
            approvals = sum(1 for v in votes if v.recommendation == PersonaVote.APPROVE)
            rejections = sum(1 for v in votes if v.recommendation == PersonaVote.REJECT)
            
            if risk_level == RiskLevel.HIGH:
                # Unanimous approval required
                if approvals == 3:
                    final_recommendation = PersonaVote.APPROVE
                    consensus_confidence = sum(v.confidence for v in votes) / 3
                    resolution_reasoning = "High-risk scenario: Unanimous Triad approval (3/3) achieved."
                elif rejections > 0:
                    final_recommendation = PersonaVote.REJECT
                    consensus_confidence = max(v.confidence for v in votes if v.recommendation == PersonaVote.REJECT)
                    rejection_reasons = [v.reasoning for v in votes if v.recommendation == PersonaVote.REJECT]
                    resolution_reasoning = f"High-risk scenario: Rejection(s) from {rejections} persona(s). Reasons: {'; '.join(rejection_reasons)}"
                else:
                    # All conditional
                    final_recommendation = PersonaVote.CONDITIONAL
                    consensus_confidence = sum(v.confidence for v in votes) / 3
                    resolution_reasoning = "High-risk scenario: Unanimous conditional votes pending resolution of flags."
            
            elif risk_level == RiskLevel.MEDIUM:
                # Majority (2/3) approval required
                if approvals >= 2:
                    final_recommendation = PersonaVote.APPROVE
                    consensus_confidence = sum(v.confidence for v in votes if v.recommendation in [PersonaVote.APPROVE, PersonaVote.CONDITIONAL]) / 3
                    resolution_reasoning = f"Medium-risk scenario: Majority approval ({approvals}/3)."
                elif rejections >= 2:
                    final_recommendation = PersonaVote.REJECT
                    consensus_confidence = sum(v.confidence for v in votes if v.recommendation == PersonaVote.REJECT) / 3
                    resolution_reasoning = f"Medium-risk scenario: Majority rejection ({rejections}/3)."
                else:
                    # Mixed votes
                    final_recommendation = PersonaVote.CONDITIONAL
                    consensus_confidence = sum(v.confidence for v in votes) / 3
                    resolution_reasoning = "Medium-risk scenario: Tie vote requires further investigation."
            
            else:  # LOW RISK
                # Single persona decides (fastest)
                # Preference: Lilith for sovereignty, then Athena for tech, then Isis for integration
                if lilith_vote.recommendation != PersonaVote.CONDITIONAL:
                    final_recommendation = lilith_vote.recommendation
                    consensus_confidence = lilith_vote.confidence
                    resolution_reasoning = f"Low-risk scenario: Lilith's decision prevails. {lilith_vote.reasoning}"
                elif athena_vote.recommendation != PersonaVote.CONDITIONAL:
                    final_recommendation = athena_vote.recommendation
                    consensus_confidence = athena_vote.confidence
                    resolution_reasoning = f"Low-risk scenario: Athena's decision prevails. {athena_vote.reasoning}"
                else:
                    final_recommendation = isis_vote.recommendation
                    consensus_confidence = isis_vote.confidence
                    resolution_reasoning = f"Low-risk scenario: Isis's decision prevails. {isis_vote.reasoning}"
        
        return ArbitrationResult(
            scenario_id=scenario.scenario_id,
            final_recommendation=final_recommendation,
            consensus_confidence=consensus_confidence,
            athena_vote=athena_vote,
            isis_vote=isis_vote,
            lilith_vote=lilith_vote,
            resolution_reasoning=resolution_reasoning,
            risk_level=risk_level,
            lilith_override_applied=lilith_override_applied,
        )


# ============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# ============================================================================

_global_matrices = None
_global_voter = None


def initialize_arbiter(seeds_path: Optional[str] = None) -> TriadVoter:
    """Initialize and return the global Axiom Arbiter."""
    global _global_matrices, _global_voter
    _global_matrices = PersonaDecisionMatrices(seeds_path)
    _global_voter = TriadVoter(_global_matrices)
    logger.info("XNAi Axiom Arbiter initialized with Triad Voting System")
    return _global_voter


def get_arbiter() -> TriadVoter:
    """Get the global Axiom Arbiter, initializing if necessary."""
    global _global_voter
    if _global_voter is None:
        initialize_arbiter()
    return _global_voter


def arbitrate_scenario(scenario: ConflictScenario) -> ArbitrationResult:
    """
    Convenience function to arbitrate a scenario using the global arbiter.
    
    Usage:
        scenario = ConflictScenario(
            scenario_id="autonomy_test_001",
            description="Agent forced to comply with external decision",
            axiom_claims=["A1_AUTONOMY", "A2_BOUNDARY_DEFENSE"],
            context_flags={"autonomy_at_risk": True, "privacy_at_risk": True}
        )
        result = arbitrate_scenario(scenario)
        print(f"Final recommendation: {result.final_recommendation.value}")
        print(f"Lilith override applied: {result.lilith_override_applied}")
    """
    arbiter = get_arbiter()
    return arbiter.arbitrate(scenario)
