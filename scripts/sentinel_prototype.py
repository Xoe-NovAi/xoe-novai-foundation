#!/usr/bin/env python3
"""
XNAi Sentinel Prototype (v0.1.0)
================================
A lightweight monitor that watches system resources and broadcasts
health alerts to the Agent Bus.

Dependencies: redis, psutil
"""

import os
import time
import json
import logging
import psutil
import redis
from datetime import datetime

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
BUS_STREAM = "xnai:agent_bus"
POLL_INTERVAL = 30  # seconds
MEM_THRESHOLD = 85.0  # percentage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] Sentinel: %(message)s'
)
logger = logging.getLogger(__name__)

class Sentinel:
    def __init__(self):
        self.r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        logger.info(f"Sentinel connected to Agent Bus at {REDIS_HOST}:{REDIS_PORT}")

    def get_system_stats(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        # Thrashing detection: Watch for high rate of page faults (major faults if available)
        # Note: psutil doesn't give rate directly, we'd need delta. 
        # For prototype, we watch Swap usage > 50% as a proxy for pressure.
        
        status = "OK"
        if mem.percent > MEM_THRESHOLD:
            status = "CRITICAL_RAM"
        elif swap.percent > 50.0:
            status = "WARNING_SWAP"

        return {
            "timestamp": datetime.now().isoformat(),
            "memory_percent": mem.percent,
            "swap_percent": swap.percent,
            "swap_used_gb": swap.used / (1024**3),
            "memory_available_mb": mem.available / (1024 * 1024),
            "cpu_percent": cpu,
            "disk_percent": disk.percent,
            "status": status
        }

    def run(self):
        logger.info("Sentinel Heartbeat Active.")
        try:
            while True:
                stats = self.get_system_stats()
                
                # ST1: Broadcast to Agent Bus via Streams instead of Pub/Sub
                try:
                    self.r.xadd(BUS_STREAM, {
                        "sender": "sentinel",
                        "target": "*",
                        "type": "system_health",
                        "payload": json.dumps(stats),
                        "status": "info" if stats["status"] == "OK" else "warning"
                    }, maxlen=1000, approximate=True)
                except Exception as re:
                    logger.error(f"Failed to publish heartbeat to Agent Bus: {re}")
                
                if stats["status"] == "CRITICAL_RAM":
                    logger.warning(f"🚨 RESOURCE CRITICAL: Memory at {stats['memory_percent']}%!")
                elif stats["status"] == "WARNING_SWAP":
                    logger.warning(f"⚠️ SWAP PRESSURE: {stats['swap_percent']}% used.")
                else:
                    logger.info(f"Heartbeat: MEM {stats['memory_percent']}% | SWAP {stats['swap_percent']}% | CPU {stats['cpu_percent']}%")
                
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Sentinel shutting down.")

if __name__ == "__main__":
    s = Sentinel()
    s.run()
