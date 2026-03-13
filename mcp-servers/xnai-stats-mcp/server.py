import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

from pathlib import Path

mcp = FastMCP("OmegaStats")
# Resolve path relative to project root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
METRICS_PATH = PROJECT_ROOT / "artifacts" / "omega_instance_metrics.json"

@mcp.tool()
def get_usage_metrics():
    """Returns real-time usage metrics for all 8 expert domain instances."""
    if not METRICS_PATH.exists():
        return "Metrics data not available. Run 'make metropolis-stats' first."
    
    with open(METRICS_PATH, 'r') as f:
        return json.load(f)

@mcp.tool()
def get_system_stats():
    """🔱 Archon Mandate: Direct monitoring of zRAM drives and Vulkan iGPU utilization."""
    stats = {
        "zram": {"available": False},
        "vulkan_gpu": {"available": False},
        "timestamp": datetime.now().isoformat()
    }
    
    # zRAM Stats
    zram_path = Path("/sys/block/zram0/mm_stat")
    if zram_path.exists():
        try:
            with open(zram_path, "r") as f:
                mm_stat = f.read().split()
                # 0: orig_data_size, 1: compr_data_size, 2: mem_used_total
                stats["zram"] = {
                    "available": True,
                    "orig_data_mb": round(int(mm_stat[0]) / 1024 / 1024, 2),
                    "compressed_data_mb": round(int(mm_stat[1]) / 1024 / 1024, 2),
                    "mem_used_total_mb": round(int(mm_stat[2]) / 1024 / 1024, 2),
                    "ratio": round(int(mm_stat[0]) / int(mm_stat[1]), 2) if int(mm_stat[1]) > 0 else 1.0
                }
        except Exception as e:
            stats["zram"]["error"] = str(e)

    # Vulkan iGPU Stats (AMD Ryzen 5700U)
    gpu_path = Path("/sys/class/drm/card1/device/gpu_busy_percent")
    if gpu_path.exists():
        try:
            with open(gpu_path, "r") as f:
                stats["vulkan_gpu"] = {
                    "available": True,
                    "utilization_percent": int(f.read().strip())
                }
        except Exception as e:
            stats["vulkan_gpu"]["error"] = str(e)
            
    return stats

@mcp.tool()
def check_quota_status(instance_id: int):
    """Check if a specific domain expert instance is approaching its quota limit."""
    if not METRICS_PATH.exists():
        return "Metrics data not available."
    
    with open(METRICS_PATH, 'r') as f:
        data = json.load(f)
        inst = data.get("instances", {}).get(f"instance-{instance_id}")
        if not inst:
            return f"Instance {instance_id} not found."
        
        g = inst["gemini"]
        return f"Domain: {inst['name']} | Requests: {g['total_requests']} | Tokens: {g['total_tokens']} | Status: {g['quota_status']}"

if __name__ == "__main__":
    mcp.run()
