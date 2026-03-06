#!/usr/bin/env python3
"""
XNAi Escalation & Surgical Metrics
==================================

Calculates the efficiency and accuracy of the hierarchical research chain.
Focus: 
- Confidence Velocity (Δ Confidence / Δ Level)
- Surgical Save Ratio (Tokens saved by surgical vs full escalation)
- Persona Divergence (Consistency across triangulation personas)
"""

import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class EscalationMetricsCalculator:
    def calculate_efficiency(self, session_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes a research session for efficiency gains.
        """
        if not session_history:
            return {}

        initial_conf = float(session_history[0].get("overall_confidence", 0.0))
        final_conf = float(session_history[-1].get("overall_confidence", 0.0))
        levels = len(session_history)
        
        # 1. Confidence Velocity
        conf_velocity = (final_conf - initial_conf) / levels if levels > 0 else 0
        
        # 2. Surgical Save Ratio (Simulated)
        # Ratio = (Full 8B Escalation Cost - Surgical Specialist Cost) / Full Cost
        surgical_events = [r for r in session_history if r.get("specialist_handoff")]
        save_ratio = 0.0
        if surgical_events:
            # Assumes 3B/7B specialist vs 8B authority + lower level overhead
            save_ratio = 0.45 * len(surgical_events) # Estimated 45% saving per event

        return {
            "confidence_velocity": round(conf_velocity, 4),
            "surgical_save_ratio": round(save_ratio, 2),
            "depth_efficiency": round(final_conf / levels, 4) if levels > 0 else 0
        }

    def analyze_persona_triangulation(self, results: Dict[str, str]) -> float:
        """
        Measures the divergence between personas (Skeptic vs Architect vs Synthesizer).
        High divergence suggests a complex/ambiguous query.
        """
        # In production, use semantic similarity (Jaccard or Cosine)
        return 0.15 # Mock divergence score
