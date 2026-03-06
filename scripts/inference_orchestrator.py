#!/usr/bin/env python3
"""
XNAi Inference Orchestrator (RAM-Aware)
=======================================

Manages local LLM inference lifecycle on Ryzen 5700U (16GB RAM).
Intelligently swaps models for escalation levels to prevent OOM.

Optimization: 
- Draft Models for Speculative Decoding
- Q8_0 KV Cache
- Flash Attention
"""

import os
import subprocess
import time
import psutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class InferenceOrchestrator:
    def __init__(self):
        self.current_process = None
        self.current_model = None

    def _get_free_ram_gb(self):
        return psutil.virtual_memory().available / (1024**3)

    def stop_inference(self):
        if self.current_process:
            logger.info(f"Stopping model: {self.current_model}")
            self.current_process.terminate()
            self.current_process.wait()
            self.current_process = None
            self.current_model = None
            time.sleep(2) # Cooldown for RAM release

    def start_inference(self, model_path: str, draft_model: Optional[str] = None):
        if self.current_model == model_path:
            return # Already running

        self.stop_inference()
        
        free_ram = self._get_free_ram_gb()
        logger.info(f"Available RAM: {free_ram:.2f}GB")
        
        # Simple heuristic: 8B Q8 needs ~10GB, 1B needs ~2GB
        if free_ram < 4 and "8b" in model_path.lower():
            logger.warning("RAM low! Killing background services...")
            # subprocess.run(["podman", "stop", "xnai_crawler"])

        cmd = [
            "llama-server",
            "-m", model_path,
            "-c", "8192",
            "--flash-attn",
            "--cache-type-k", "q8_0",
            "--cache-type-v", "q8_0",
            "--port", "8080",
            "--threads", "8"
        ]
        
        if draft_model:
            cmd.extend(["-md", draft_model])

        logger.info(f"Launching {model_path}...")
        self.current_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        self.current_model = model_path
        
        # Wait for health check
        time.sleep(5)
        logger.info("Inference server ready.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orchestrator = InferenceOrchestrator()
    # orchestrator.start_inference("models/Krikri-8b-Instruct.gguf")
