#!/usr/bin/env python3
import os
import time
import subprocess
import logging
from prometheus_client import start_http_server, Gauge

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Prometheus Metrics
ZRAM_CAPACITY = Gauge('xnai_zram_capacity_bytes', 'Total capacity of zram device')
ZRAM_USED = Gauge('xnai_zram_used_bytes', 'Memory used by zram (compressed size)')
ZRAM_ORIG_DATA = Gauge('xnai_zram_orig_data_bytes', 'Original size of data stored in zram')
ZRAM_COMP_RATIO = Gauge('xnai_zram_compression_ratio', 'Compression ratio (orig/compressed)')

def get_zram_stats():
    """Parse /sys/block/zram0/mm_stat for detailed metrics."""
    try:
        if not os.path.exists("/sys/block/zram0/mm_stat"):
            return None
        
        with open("/sys/block/zram0/mm_stat", "r") as f:
            stats = f.read().split()
            # mm_stat columns: 
            # 0: orig_data_size, 1: compr_data_size, 2: mem_used_total, 3: mem_limit...
            return {
                "orig": int(stats[0]),
                "comp": int(stats[1]),
                "total": int(stats[2])
            }
    except Exception as e:
        logger.error(f"Error reading zram stats: {e}")
        return None

def update_metrics():
    """Update prometheus gauges."""
    stats = get_zram_stats()
    if stats:
        ZRAM_ORIG_DATA.set(stats["orig"])
        ZRAM_USED.set(stats["total"])
        ratio = stats["orig"] / stats["total"] if stats["total"] > 0 else 1.0
        ZRAM_COMP_RATIO.set(ratio)
        
        # Get capacity via zramctl or sysfs
        try:
            with open("/sys/block/zram0/disksize", "r") as f:
                ZRAM_CAPACITY.set(int(f.read().strip()))
        except:
            pass

if __name__ == "__main__":
    # Start metrics server on port 9101 (dedicated for infra)
    start_http_server(9101)
    logger.info("🚀 Swap Monitor Exporter started on port 9101")
    
    while True:
        update_metrics()
        time.sleep(15)
