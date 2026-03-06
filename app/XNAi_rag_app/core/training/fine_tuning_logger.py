#!/usr/bin/env python3
"""
XNAi Fine-Tuning Logger
=======================

Captures high-quality "Gold Standard" interactions for future model fine-tuning.
Focuses on the 'Dual-Stack' identity (Expert Persona + Model Engine).

Output Format: JSONL (Alpaca/ShareGPT compatible)
Target: storage/data/training/gold_standard.jsonl
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FineTuningLogger:
    """
    Logs successful interactions to build a sovereign fine-tuning dataset.
    """

    def __init__(self, base_dir: str = "storage/data/training"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.dataset_path = self.base_dir / "gold_standard.jsonl"

    async def log_interaction(
        self, 
        query: str, 
        response: str, 
        expert_id: str, 
        model_id: str, 
        rating: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a high-quality interaction (Rating > 0.85) for fine-tuning.
        """
        if rating < 0.85:
            return # Only keep the best for training

        entry = {
            "timestamp": time.time(),
            "expert_id": expert_id,
            "model_id": model_id,
            "rating": rating,
            "instruction": f"Act as {expert_id}. Use your domain expertise to answer.",
            "input": query,
            "output": response,
            "system_prompt": f"You are {expert_id}, running on the {model_id} engine.",
            "metadata": metadata or {}
        }

        try:
            with open(self.dataset_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "
")
            
            logger.info(f"💾 Logged fine-tuning example: {expert_id} on {model_id}")
            
        except Exception as e:
            logger.error(f"Failed to log fine-tuning data: {e}")

# Global instance
ft_logger = FineTuningLogger()
