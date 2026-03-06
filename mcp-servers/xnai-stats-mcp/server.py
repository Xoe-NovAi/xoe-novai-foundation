import json
import os
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
