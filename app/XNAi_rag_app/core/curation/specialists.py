#!/usr/bin/env python3
"""
XNAi Surgical Specialist Registry
==================================

Maps confidence dimensions to specialized models and personas.
Ensures the most appropriate intelligence is applied to gaps.
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class SpecialistRole(Enum):
    TECHNICAL = "technical_expert"
    CREATIVE = "creative_writer"
    FACTUAL = "fact_checker"
    LOGICIAN = "logical_analyst"
    PHILOSOPHER = "philosophical_critic"

class SurgicalRoutingEngine:
    """
    Decides the 'Surgical Handoff' based on Confidence Vectors.
    """

    # Specialist Model Map
    SPECIALIST_MODELS = {
        SpecialistRole.TECHNICAL: "storage/models/deepseek-coder-7b.gguf",
        SpecialistRole.CREATIVE: "storage/models/qwen-7b-creative.gguf",
        SpecialistRole.FACTUAL: "storage/models/llama-3-8b-instruct.gguf",
        SpecialistRole.LOGICIAN: "storage/models/mistral-7b-instruct.gguf",
        SpecialistRole.PHILOSOPHER: "storage/models/philosophy-7b.gguf"
    }

    # Specialist Persona Instructions
    SPECIALIST_PERSONAS = {
        SpecialistRole.TECHNICAL: "Focus exclusively on code accuracy, paths, and technical protocols.",
        SpecialistRole.CREATIVE: "Rewrite the content for maximum engagement, clarity, and narrative flow.",
        SpecialistRole.FACTUAL: "Verify every claim against the provided dossier and flag hallucinations.",
        SpecialistRole.LOGICIAN: "Audit the reasoning chain for logical fallacies and structural gaps.",
        SpecialistRole.PHILOSOPHER: "Analyze the underlying principles and ethical implications of the content."
    }

    def get_specialist(self, dimension: str) -> Dict[str, Any]:
        """
        Returns the appropriate model and persona for a low-confidence dimension.
        """
        dim_map = {
            "technical": SpecialistRole.TECHNICAL,
            "creative": SpecialistRole.CREATIVE,
            "factuality": SpecialistRole.FACTUAL,
            "logic": SpecialistRole.LOGICIAN
        }
        
        role = dim_map.get(dimension.lower(), SpecialistRole.FACTUAL)
        
        return {
            "role": role.value,
            "model": self.SPECIALIST_MODELS.get(role),
            "persona": self.SPECIALIST_PERSONAS.get(role)
        }

    def suggest_rotation(self, turn_count: int) -> str:
        """
        Suggests a persona rotation for multi-turn triangulation within the same model.
        Example for ~150M model: Philosophy -> Technical -> Creative.
        """
        rotation = [SpecialistRole.PHILOSOPHER, SpecialistRole.TECHNICAL, SpecialistRole.CREATIVE]
        return rotation[turn_count % len(rotation)].value
