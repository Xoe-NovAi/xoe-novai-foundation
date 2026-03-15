"""
zRAM Monitor for Hellenic Ingestion (SESS-26)
SAFETY CRITICAL: Monitors zRAM memory tier and triggers backoff during high usage
Prevents zRAM overflow and OOM kills during document ingestion.

Algorithm:
  1. Query zramctl for zram0 usage (lz4 hot tier)
  2. Calculate usage percentage (TOTAL / DISKSIZE)
  3. IF usage > 90%:
     - Log warning with timestamp and percentage
     - Sleep 30 seconds (configurable)
     - Return False (back off from processing)
  4. ELSE:
     - Return True (safe to continue)
"""

import subprocess
import logging
import time
import re
from datetime import datetime, timezone
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_BACKOFF_DURATION_SECONDS = 30
ZRAM_USAGE_THRESHOLD_PERCENT = 90
ZRAM_DEVICE = "zram0"


def _parse_zramctl_output() -> Optional[Tuple[float, float, float]]:
    """
    Parse zramctl output and extract zram0 memory statistics.
    
    Returns:
        Tuple of (DISKSIZE_GB, TOTAL_GB, usage_percent) or None on error
        Example: (4.0, 0.48, 12.0)
    """
    try:
        result = subprocess.run(
            ["zramctl"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            logger.error(f"zramctl command failed: {result.stderr}")
            return None
        
        output = result.stdout
        for line in output.split('\n'):
            if "zram0" in line:
                # Parse the zram0 line
                # Format: /dev/zram0 lz4 4G 1.3G 460.2M 479.5M
                parts = line.split()
                if len(parts) >= 6:
                    # Extract DISKSIZE and TOTAL columns
                    disksize_str = parts[2]  # 4G
                    total_str = parts[5]     # 479.5M
                    
                    disksize_gb = _parse_size_to_gb(disksize_str)
                    total_gb = _parse_size_to_gb(total_str)
                    
                    if disksize_gb > 0:
                        usage_percent = (total_gb / disksize_gb) * 100
                        return (disksize_gb, total_gb, usage_percent)
        
        logger.warning("zram0 not found in zramctl output")
        return None
        
    except subprocess.TimeoutExpired:
        logger.error("zramctl command timed out")
        return None
    except Exception as e:
        logger.error(f"Error parsing zramctl output: {e}")
        return None


def _parse_size_to_gb(size_str: str) -> float:
    """
    Parse size string (e.g., '4G', '479.5M', '100K') to gigabytes.
    
    Args:
        size_str: Size string with unit (K, M, G, T)
    
    Returns:
        Size in gigabytes as float
    """
    size_str = size_str.strip().upper()
    
    units = {
        'K': 1e-6,      # kilobytes to GB
        'M': 1e-3,      # megabytes to GB
        'G': 1,         # gigabytes to GB
        'T': 1e3,       # terabytes to GB
    }
    
    # Extract numeric part and unit
    match = re.match(r'([0-9.]+)([KMGT])', size_str)
    if match:
        value, unit = float(match.group(1)), match.group(2)
        return value * units.get(unit, 0)
    
    return 0.0


def check_and_backoff(backoff_duration: int = DEFAULT_BACKOFF_DURATION_SECONDS) -> bool:
    """
    Check zRAM0 (lz4 hot tier) usage and trigger backoff if needed.
    
    SAFETY CRITICAL: Prevents zRAM overflow and OOM kills during ingestion.
    
    Algorithm:
      1. Query zramctl for zram0 usage
      2. Calculate usage percentage
      3. IF usage > 90%:
         - Log warning with timestamp and percentage
         - Sleep for backoff_duration seconds
         - Return False (caller should back off)
      4. ELSE:
         - Return True (safe to continue)
    
    Args:
        backoff_duration: How long to sleep if usage is high (default: 30 seconds)
    
    Returns:
        True if safe to continue processing, False if backoff was triggered
    """
    stats = _parse_zramctl_output()
    
    if stats is None:
        # If we can't check zRAM, assume it's safe to continue
        # (better to process than stall indefinitely)
        logger.warning("Could not check zRAM status; continuing anyway")
        return True
    
    disksize_gb, total_gb, usage_percent = stats
    
    if usage_percent > ZRAM_USAGE_THRESHOLD_PERCENT:
        # High usage detected - trigger backoff
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        remaining_gb = disksize_gb - total_gb
        
        log_message = (
            f"[{timestamp}] zRAM0 backoff triggered: {usage_percent:.1f}% > {ZRAM_USAGE_THRESHOLD_PERCENT}%, "
            f"pausing {backoff_duration}s (used: {total_gb:.2f}GB/{disksize_gb:.2f}GB, "
            f"remaining: {remaining_gb:.2f}GB)"
        )
        logger.warning(log_message)
        
        # Sleep to allow zRAM compression to catch up
        time.sleep(backoff_duration)
        
        return False
    
    # Safe to continue
    return True
