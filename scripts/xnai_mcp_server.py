from fastmcp import FastMCP
import os
import json
import subprocess
from pathlib import Path

# Initialize Xoe-NovAi Command Center
mcp = FastMCP(
    "Xoe-NovAi Command Center",
    description="Centralized MCP server for Sovereign AI Agent Orchestration"
)

# Paths
INBOX = Path("internal_docs/communication_hub/inbox")
OUTBOX = Path("internal_docs/communication_hub/outbox")

@mcp.tool()
def send_agent_message(target: str, task_description: str, priority: str = "medium") -> str:
    """
    Sends a task assignment to another agent via the Agent Bus.
    Args:
        target: The agent name (cline, gemini, copilot)
        task_description: The detailed task prompt
        priority: high, medium, or low
    """
    msg_id = f"mcp-{int(os.times()[4])}"
    msg = {
        "message_id": msg_id,
        "sender": "mcp-server",
        "target": target,
        "type": "task_assignment",
        "content": {"description": task_description},
        "priority": priority
    }
    
    file_path = INBOX / f"{target}_{msg_id}.json"
    with open(file_path, "w") as f:
        json.dump(msg, f, indent=2)
    
    return f"Message sent to {target} inbox: {file_path}"

@mcp.tool()
def get_system_load() -> dict:
    """Returns the current CPU and Memory usage of the Ryzen host."""
    import psutil
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "zram_info": subprocess.getoutput("zramctl --noheadings")
    }

@mcp.tool()
def read_agent_outbox(agent_name: str) -> list:
    """Reads all completed task reports from a specific agent's outbox."""
    files = OUTBOX.glob(f"{agent_name}_response_*.json")
    results = []
    for f in files:
        with open(f, "r") as content:
            results.append(json.load(content))
    return results

if __name__ == "__main__":
    mcp.run()
