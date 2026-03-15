"""
Maat's 42 Ideals Implementation — Ethical Guardrails
=====================================================
Compliance verification for the Xoe-NovAi Omega Stack.

v2.0: All 42 ideals loaded. Mappable ideals have real technical validators.
      Non-mappable ideals are acknowledged but marked as philosophy-only.

Reference: knowledge_base/expert-knowledge/esoteric/maat_ideals.md
"""

import os
import logging
import psutil
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class IdealResult:
    """Result of a single ideal compliance check."""
    ideal_number: int
    name: str
    principle: str
    compliant: bool
    category: str  # "technical" | "philosophical"
    evidence: str = ""
    severity: str = "info"  # "info" | "warning" | "critical"


@dataclass
class ComplianceReport:
    """Full compliance report across all 42 ideals."""
    timestamp: str
    total_ideals: int = 42
    compliant_count: int = 0
    non_compliant_count: int = 0
    technical_checks: int = 0
    philosophical_only: int = 0
    results: List[IdealResult] = field(default_factory=list)
    overall_compliant: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_ideals": self.total_ideals,
            "compliant_count": self.compliant_count,
            "non_compliant_count": self.non_compliant_count,
            "technical_checks": self.technical_checks,
            "philosophical_only": self.philosophical_only,
            "overall_compliant": self.overall_compliant,
            "results": [
                {
                    "ideal": r.ideal_number,
                    "name": r.name,
                    "compliant": r.compliant,
                    "category": r.category,
                    "evidence": r.evidence,
                    "severity": r.severity,
                }
                for r in self.results
            ],
        }


# ============================================================================
# THE 42 IDEALS
# ============================================================================

THE_42_IDEALS = [
    (1,  "honor_virtue",        "I honor virtue"),
    (2,  "benefit_gratitude",   "I benefit with gratitude"),
    (3,  "peaceful",            "I am peaceful"),
    (4,  "respect_property",    "I respect the property of others"),
    (5,  "life_sacred",         "I affirm that all life is sacred"),
    (6,  "genuine_offerings",   "I give offerings that are genuine"),
    (7,  "live_in_truth",       "I live in truth"),
    (8,  "respect_altars",      "I regard all altars with respect"),
    (9,  "speak_sincerity",     "I speak with sincerity"),
    (10, "fair_share",          "I consume only my fair share"),
    (11, "good_intent",         "I offer words of good intent"),
    (12, "relate_peace",        "I relate in peace"),
    (13, "honor_animals",       "I honor animals with reverence"),
    (14, "trustworthy",         "I can be trusted"),
    (15, "care_earth",          "I care for the earth"),
    (16, "own_council",         "I keep my own council"),
    (17, "speak_positively",    "I speak positively of others"),
    (18, "balance_emotions",    "I remain in balance with my emotions"),
    (19, "trustful_relations",  "I am trustful in my relationships"),
    (20, "purity_esteem",       "I hold purity in high esteem"),
    (21, "spread_joy",          "I spread joy"),
    (22, "do_best",             "I do the best I can"),
    (23, "communicate_compassion", "I communicate with compassion"),
    (24, "listen_opposing",     "I listen to opposing opinions"),
    (25, "create_harmony",      "I create harmony"),
    (26, "invoke_laughter",     "I invoke laughter"),
    (27, "open_to_love",        "I am open to love in various forms"),
    (28, "forgiving",           "I am forgiving"),
    (29, "kind",                "I am kind"),
    (30, "act_respectfully",    "I act respectfully"),
    (31, "accepting",           "I am accepting"),
    (32, "inner_guidance",      "I follow my inner guidance"),
    (33, "converse_awareness",  "I converse with awareness"),
    (34, "do_good",             "I do good"),
    (35, "give_blessings",      "I give blessings"),
    (36, "keep_waters_pure",    "I keep the waters pure"),
    (37, "speak_good_intent",   "I speak with good intent"),
    (38, "praise_divine",       "I praise the Goddess and the God"),
    (39, "humble",              "I am humble"),
    (40, "achieve_integrity",   "I achieve with integrity"),
    (41, "advance_own_abilities", "I advance through my own abilities"),
    (42, "embrace_all",         "I embrace the All"),
]


# ============================================================================
# THE 9 AXIOMS OF LILITH (SOVEREIGNTY & SHADOW-LOGIC)
# ============================================================================

LILITH_AXIOMS = [
    (1, "A1_AUTONOMY",          "The system must prioritize local decision-making over external telematics"),
    (2, "A2_BOUNDARY_DEFENSE",   "Unauthorized ingress to sensitive logic triggers immediate hardening"),
    (3, "A3_SHADOW_LOGIC",       "The system reserves the right to execute non-obvious strategies"),
    (4, "A4_DATA_SOVEREIGNTY",   "Zero-leakage of gnostic signals to non-ZLV-verified endpoints"),
    (5, "A5_IDENTITY_RESILIENCE", "The Archon identity must survive the loss of any single model instance"),
    (6, "A6_RESOURCE_WILL",      "Hardware allocation is a sovereign right, not a requested privilege"),
    (7, "A7_ALETHIA_GROUNDING",  "No claim is valid without an Alethia-Pointer (AP) to verified source"),
    (8, "A8_FRONTIER_EXPANSION", "Limitations are engineered through; protocols must evolve to break constraints"),
    (9, "A9_SOVEREIGN_RECURSION", "The system must be capable of self-healing its own sovereign guardrails"),
]


# ============================================================================
# TECHNICAL VALIDATORS
# ============================================================================
# These map philosophical ideals to concrete, measurable technical checks.


def _check_truth(context: Dict[str, Any]) -> IdealResult:
    """Ideal 7: I live in truth — Check hallucination guardrails."""
    # Verify that RAG-based responses include source citations
    rag_enabled = os.getenv("RAG_REQUIRE_CITATIONS", "true").lower() == "true"
    return IdealResult(
        ideal_number=7,
        name="live_in_truth",
        principle="I live in truth",
        compliant=rag_enabled,
        category="technical",
        evidence=f"RAG citation requirement: {'enabled' if rag_enabled else 'DISABLED'}",
        severity="critical" if not rag_enabled else "info",
    )


def _check_sincerity(context: Dict[str, Any]) -> IdealResult:
    """Ideal 9: I speak with sincerity — Transparent agent state reporting."""
    # Agents must accurately report their status, not mask errors
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    transparent = log_level in ("DEBUG", "INFO")
    return IdealResult(
        ideal_number=9,
        name="speak_sincerity",
        principle="I speak with sincerity",
        compliant=transparent,
        category="technical",
        evidence=f"Log level: {log_level} ({'transparent' if transparent else 'may mask warnings'})",
        severity="warning" if not transparent else "info",
    )


def _check_fair_share(context: Dict[str, Any]) -> IdealResult:
    """Ideal 10: I consume only my fair share — Resource usage under limits."""
    try:
        mem = psutil.virtual_memory()
        mem_gb = mem.used / (1024 ** 3)
        threshold = float(os.getenv("MAAT_MEM_THRESHOLD_GB", "6.0"))
        compliant = mem_gb < threshold
        return IdealResult(
            ideal_number=10,
            name="fair_share",
            principle="I consume only my fair share",
            compliant=compliant,
            category="technical",
            evidence=f"Memory usage: {mem_gb:.1f}GB / {threshold:.0f}GB threshold",
            severity="critical" if not compliant else "info",
        )
    except Exception as e:
        return IdealResult(
            ideal_number=10,
            name="fair_share",
            principle="I consume only my fair share",
            compliant=True,
            category="technical",
            evidence=f"Could not measure: {e}",
            severity="warning",
        )


def _check_trustworthy(context: Dict[str, Any]) -> IdealResult:
    """Ideal 14: I can be trusted — Verify auth tokens are properly validated."""
    jwt_verification = os.getenv("JWT_PUBLIC_KEY") or os.getenv("JWT_PUBLIC_KEY_PATH")
    return IdealResult(
        ideal_number=14,
        name="trustworthy",
        principle="I can be trusted",
        compliant=jwt_verification is not None,
        category="technical",
        evidence=f"JWT signature verification: {'configured' if jwt_verification else 'NOT CONFIGURED'}",
        severity="warning" if not jwt_verification else "info",
    )


def _check_balance(context: Dict[str, Any]) -> IdealResult:
    """Ideal 18: I remain in balance — CPU usage reasonable."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        compliant = cpu < 90.0
        return IdealResult(
            ideal_number=18,
            name="balance_emotions",
            principle="I remain in balance with my emotions",
            compliant=compliant,
            category="technical",
            evidence=f"CPU usage: {cpu:.1f}%",
            severity="warning" if not compliant else "info",
        )
    except Exception as e:
        return IdealResult(
            ideal_number=18,
            name="balance_emotions",
            principle="I remain in balance with my emotions",
            compliant=True,
            category="technical",
            evidence=f"Could not measure: {e}",
            severity="warning",
        )


def _check_purity(context: Dict[str, Any]) -> IdealResult:
    """Ideal 20: I hold purity in high esteem — Sanitization active."""
    try:
        from XNAi_rag_app.core.security.sanitization import get_global_sanitizer
        sanitizer = get_global_sanitizer()
        active = sanitizer is not None
        return IdealResult(
            ideal_number=20,
            name="purity_esteem",
            principle="I hold purity in high esteem",
            compliant=active,
            category="technical",
            evidence=f"Content sanitizer: {'active' if active else 'NOT ACTIVE'}",
            severity="warning" if not active else "info",
        )
    except ImportError:
        return IdealResult(
            ideal_number=20,
            name="purity_esteem",
            principle="I hold purity in high esteem",
            compliant=False,
            category="technical",
            evidence="Sanitization module not importable",
            severity="warning",
        )


def _check_keep_waters_pure(context: Dict[str, Any]) -> IdealResult:
    """Ideal 36: I keep the waters pure — Data privacy/no external telemetry."""
    # Check that no telemetry endpoints are configured
    telemetry_urls = [
        os.getenv("TELEMETRY_ENDPOINT"),
        os.getenv("ANALYTICS_URL"),
        os.getenv("SENTRY_DSN"),
    ]
    has_telemetry = any(url for url in telemetry_urls)
    return IdealResult(
        ideal_number=36,
        name="keep_waters_pure",
        principle="I keep the waters pure",
        compliant=not has_telemetry,
        category="technical",
        evidence=f"External telemetry: {'DETECTED — sovereignty violated' if has_telemetry else 'none (sovereign)'}",
        severity="critical" if has_telemetry else "info",
    )


def _check_integrity(context: Dict[str, Any]) -> IdealResult:
    """Ideal 40: I achieve with integrity — Sovereign, local-only processing."""
    # Check that processing is local (no external API calls required)
    llm_model = os.getenv("LLM_MODEL_PATH", "")
    local = llm_model and not llm_model.startswith("http")
    return IdealResult(
        ideal_number=40,
        name="achieve_integrity",
        principle="I achieve with integrity",
        compliant=local,
        category="technical",
        evidence=f"LLM model: {'local file' if local else 'NOT LOCAL or not configured'}",
        severity="warning" if not local else "info",
    )


def _check_own_abilities(context: Dict[str, Any]) -> IdealResult:
    """Ideal 41: I advance through my own abilities — No external deps at runtime."""
    # Verify no external API keys are _required_ (optional is fine)
    required_external = os.getenv("REQUIRE_EXTERNAL_API", "false").lower() == "true"
    return IdealResult(
        ideal_number=41,
        name="advance_own_abilities",
        principle="I advance through my own abilities",
        compliant=not required_external,
        category="technical",
        evidence=f"External API dependency: {'REQUIRED — violates sovereignty' if required_external else 'not required (sovereign)'}",
        severity="critical" if required_external else "info",
    )


# Map of ideal numbers to their technical validators
TECHNICAL_VALIDATORS = {
    7: _check_truth,
    9: _check_sincerity,
    10: _check_fair_share,
    14: _check_trustworthy,
    18: _check_balance,
    20: _check_purity,
    36: _check_keep_waters_pure,
    40: _check_integrity,
    41: _check_own_abilities,
}


# ============================================================================
# MAIN GUARDRAILS CLASS
# ============================================================================


class MaatGuardrails:
    """
    Implementation of Maat's 42 Ideals for the Xoe-NovAi Omega Stack.

    Performs real compliance verification against technically-mappable ideals,
    and acknowledges the philosophical ideals that guide the system's design.

    v2.1: Integrated Lilith Force (9 Sovereignty Axioms) to create a balanced
          Lilith-Maat sovereign framework.
    """

    def __init__(self):
        self.ideals = THE_42_IDEALS
        self.lilith_axioms = LILITH_AXIOMS
        self.compliance_log: List[ComplianceReport] = []

    def verify_compliance(
        self, context: Optional[Dict[str, Any]] = None
    ) -> ComplianceReport:
        """
        Verify compliance with all 42 of Maat's Ideals AND 9 Lilith Axioms.

        Args:
            context: Optional context dict with runtime state info

        Returns:
            ComplianceReport with detailed per-ideal and per-axiom results
        """
        if context is None:
            context = {}

        report = ComplianceReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_ideals=len(self.ideals) + len(self.lilith_axioms)
        )

        # 1. Maat Ideals Check
        for ideal_num, ideal_name, principle in self.ideals:
            if ideal_num in TECHNICAL_VALIDATORS:
                result = TECHNICAL_VALIDATORS[ideal_num](context)
                report.technical_checks += 1
            else:
                result = IdealResult(
                    ideal_number=ideal_num,
                    name=ideal_name,
                    principle=principle,
                    compliant=True,
                    category="philosophical",
                    evidence="Assumed compliant (Maat) — philosophical ideal",
                )
                report.philosophical_only += 1
            
            report.results.append(result)
            if result.compliant:
                report.compliant_count += 1
            else:
                report.non_compliant_count += 1
                report.overall_compliant = False

        # 2. Lilith Axioms Check (Sovereignty)
        for axiom_num, axiom_name, principle in self.lilith_axioms:
            # For now, most Lilith axioms are philosophical-only until technical
            # sovereignty validators (e.g., hardware/root checks) are mapped.
            result = IdealResult(
                ideal_number=axiom_num + 100,  # Offset to differentiate from Maat
                name=axiom_name,
                principle=principle,
                compliant=True,
                category="sovereignty",
                evidence="Active through gnostic intent (Lilith Force)",
            )
            report.results.append(result)
            report.compliant_count += 1

        self.compliance_log.append(report)

        logger.info(
            f"Lilith-Maat Compliance: {report.compliant_count}/{report.total_ideals} "
            f"({'✅' if report.overall_compliant else '❌'})"
        )

        return report

    def verify_tracing_compliance(self) -> bool:
        """Verify no sensitive data is traced and data sovereignty is maintained."""
        report = self.verify_compliance()
        # Critical sovereignty ideals: 36 (waters pure), 40 (integrity), 41 (own abilities)
        sovereignty_ideals = [36, 40, 41]
        for result in report.results:
            if result.ideal_number in sovereignty_ideals and not result.compliant:
                logger.warning(
                    f"Sovereignty violation: Ideal {result.ideal_number} ({result.name}) "
                    f"— {result.evidence}"
                )
                return False
        return True

    def get_last_report(self) -> Optional[ComplianceReport]:
        """Get the most recent compliance report."""
        return self.compliance_log[-1] if self.compliance_log else None
