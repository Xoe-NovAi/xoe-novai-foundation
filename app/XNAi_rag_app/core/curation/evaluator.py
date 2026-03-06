#!/usr/bin/env python3
"""
XNAi Multidimensional Evaluator
===============================

Provides granular confidence scoring across multiple dimensions:
- Technical Accuracy
- Creative Quality
- Factuality
- Logical Consistency

Supports 'Surgical Escalation' by identifying the specific dimension 
requiring a specialist.
"""

import logging
from typing import List, Dict, Any, Literal
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceVector:
    technical: float = 0.0
    creative: float = 0.0
    factuality: float = 0.0
    logic: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "technical": self.technical,
            "creative": self.creative,
            "factuality": self.factuality,
            "logic": self.logic
        }
    
    def get_lowest_dimension(self) -> str:
        d = self.to_dict()
        return min(d, key=d.get)

@dataclass
class MultidimensionalEvaluation:
    vector: ConfidenceVector
    overall_score: float
    summary: str
    recommendation: str = None # Specialist recommendation

class CurationEvaluator:
    def __init__(self, model_func=None):
        self.model_func = model_func

    async def evaluate_multidimensional(self, query: str, content: str) -> MultidimensionalEvaluation:
        """
        Grade the content across multiple dimensions.
        """
        prompt = f"""
        TASK: Evaluate the following CONTENT based on the QUERY across 4 dimensions.
        
        QUERY: {query}
        CONTENT: {content[:2000]}
        
        DIMENSIONS:
        1. Technical: Correctness of code, paths, and technical specs.
        2. Creative: Quality of writing, tone, and engagement.
        3. Factuality: Grounding in data, avoidance of hallucinations.
        4. Logic: Structural soundess, step-by-step reasoning.
        
        Return in this format:
        TECHNICAL: [0.0-1.0]
        CREATIVE: [0.0-1.0]
        FACTUALITY: [0.0-1.0]
        LOGIC: [0.0-1.0]
        SUMMARY: [Brief text]
        """

        if not self.model_func:
            # Simulated vector for testing
            v = ConfidenceVector(technical=0.9, creative=0.4, factuality=0.9, logic=0.9)
            return MultidimensionalEvaluation(
                vector=v,
                overall_score=0.77,
                summary="Technical/Factuality high, but Creative writing is weak.",
                recommendation="creative_specialist"
            )

        try:
            response = await self.model_func(prompt)
            return self._parse_multidim(response)
        except Exception as e:
            logger.error(f"Multidim evaluation failed: {e}")
            return MultidimensionalEvaluation(ConfidenceVector(), 0.0, f"Error: {e}")

    def _parse_multidim(self, response: str) -> MultidimensionalEvaluation:
        lines = response.strip().split("\n")
        v = ConfidenceVector()
        summary = ""
        
        for line in lines:
            parts = line.split(":")
            if len(parts) < 2: continue
            key = parts[0].strip().upper()
            val = parts[1].strip()
            
            try:
                if key == "TECHNICAL": v.technical = float(val)
                elif key == "CREATIVE": v.creative = float(val)
                elif key == "FACTUALITY": v.factuality = float(val)
                elif key == "LOGIC": v.logic = float(val)
                elif key == "SUMMARY": summary = val
            except: pass
            
        overall = (v.technical + v.creative + v.factuality + v.logic) / 4
        return MultidimensionalEvaluation(vector=v, overall_score=overall, summary=summary)
