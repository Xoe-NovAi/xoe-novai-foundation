#!/usr/bin/env python3
"""
XNAi Foundation - Batch Synthesis Engine
========================================
Purpose: Consumer for high-reasoning synthesis tasks using Krikri-8b.
Consumed by: scripts/heavy_lift.sh
"""

import os
import json
import redis
import requests
import logging
import argparse
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
QUEUE_NAME = "xnai:jobs:heavy:pending"

def process_heavy_jobs(api_url: str):
    """Fetch and process heavy synthesis jobs."""
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
    
    logger.info(f"Connected to Redis. Waiting for jobs in {QUEUE_NAME}...")
    
    while True:
        # Fetch job (Blocking pop)
        job_data = r.blpop(QUEUE_NAME, timeout=10)
        if not job_data:
            logger.info("No heavy jobs remaining. Synthesis cycle complete.")
            break
        
        _, payload_json = job_data
        job = json.loads(payload_json)
        job_id = job.get("job_id", "unknown")
        prompt = job.get("prompt", "")
        
        logger.info(f"Processing Heavy Job: {job_id}")
        
        try:
            # Send to Krikri (llama-server)
            response = requests.post(
                f"{api_url}/completion",
                json={
                    "prompt": prompt,
                    "n_predict": 2048,
                    "temperature": 0.2
                },
                timeout=600  # Long timeout for 8B model synthesis
            )
            
            if response.status_code == 200:
                result = response.json().get("content")
                # Save result to file
                output_path = f"reports/synthesis_{job_id}.md"
                os.makedirs("reports", exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(f"# Synthesis Report: {job_id}
")
                    f.write(f"**Date**: {datetime.now().isoformat()}

")
                    f.write(result)
                
                logger.info(f"✓ Job {job_id} complete. Saved to {output_path}")
                # Notify Agent Bus or update task status (omitted for brevity)
            else:
                logger.error(f"✗ Krikri Server Error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"✗ Error processing job {job_id}: {e}")

def main():
    parser = argparse.ArgumentParser(description="XNAi Batch Synthesis Engine")
    parser.add_argument("--api-url", default="http://localhost:8085", help="Krikri Server URL")
    args = parser.parse_args()

    process_heavy_jobs(args.api_url)

if __name__ == "__main__":
    main()
