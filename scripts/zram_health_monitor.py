#!/usr/bin/env python3
"""
Omega Stack: ZRAM Health Monitor
================================

Monitors zRAM usage and PSI (Pressure Stall Information) to prevent
system-wide OOM during Heavy Lifting operations.
"""

import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zram_guard")

def get_zram_status():
    try:
        with open("/proc/swaps", "r") as f:
            lines = f.readlines()
            for line in lines:
                if "zram" in line:
                    parts = line.split()
                    used = int(parts[3])
                    total = int(parts[2])
                    return used, total
    except Exception as e:
        logger.error(f"Failed to read zram status: {e}")
    return 0, 0

def check_pressure():
    """Check IO/CPU Pressure Stall Information."""
    try:
        with open("/proc/pressure/memory", "r") as f:
            full = f.readline()
            # Parse 'some' or 'full' values
            return full.strip()
    except FileNotFoundError:
        return "PSI not supported"

if __name__ == "__main__":
    logger.info("ZRAM Guard Active.")
    while True:
        used, total = get_zram_status()
        if total > 0:
            percent = (used / total) * 100
            if percent > 80:
                logger.warning(f"CRITICAL: zRAM Usage at {percent:.1f}%! Danger of OOM.")
            else:
                logger.info(f"zRAM Usage: {percent:.1f}%")
        
        pressure = check_pressure()
        logger.debug(f"Memory Pressure: {pressure}")
        
        time.sleep(30)
