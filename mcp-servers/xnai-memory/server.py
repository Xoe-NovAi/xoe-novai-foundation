"""
XNAi Memory Bank MCP Server
===========================

MCP server exposing memory bank tools, resources, and prompts.
Implements MemGPT-style hierarchical memory architecture.

Usage:
    fastmcp run server.py
    # or
    python -m mcp_servers.xnai_memory.server
"""

from pathlib import Path
from typing import Optional, Dict, Any
import os
import anyio
from fastmcp import FastMCP

MEMORY_BANK_ROOT = Path(__file__).parent.parent.parent / "memory_bank"

mcp = FastMCP("XNAi Memory Bank")

# S2: Authorization
AUTHORIZED_AGENTS = {
    "antigravity": os.getenv("MCP_TOKEN_ANTIGRAVITY"),
    "gemini": os.getenv("MCP_TOKEN_GEMINI"),
    "sentinel": os.getenv("MCP_TOKEN_SENTINEL"),
    "generalist": os.getenv("MCP_TOKEN_GENERALIST"),
}

def _check_auth(agent_id: str, auth_token: str) -> bool:
    if not agent_id or agent_id not in AUTHORIZED_AGENTS:
        return False
    expected = AUTHORIZED_AGENTS[agent_id]
    if not expected: return True
    return auth_token == expected

@mcp.tool()
async def read_memory_file(path: str, agent_id: str, auth_token: str) -> str:
    """Read any file from the memory bank.

    Args:
        path: Relative path within memory_bank directory
        agent_id: Requesting agent ID
        auth_token: S2 authorization token
    """
    if not _check_auth(agent_id, auth_token):
        return "Error: Authentication failed"

    file_path = MEMORY_BANK_ROOT / path
    if not file_path.exists():
        return f"Error: File not found - {path}"

    if not str(file_path.resolve()).startswith(str(MEMORY_BANK_ROOT.resolve())):
        return "Error: Access denied - path outside memory bank"

    async with await anyio.open_file(file_path, mode="r", encoding="utf-8") as f:
        return await f.read()


@mcp.resource("memory://bank/core/activeContext.md")
async def get_active_context() -> str:
    """Get the active context for current session priorities."""
    return (MEMORY_BANK_ROOT / "activeContext.md").read_text(encoding="utf-8")


@mcp.resource("memory://bank/core/progress.md")
async def get_progress() -> str:
    """Get the current project progress status."""
    return (MEMORY_BANK_ROOT / "progress.md").read_text(encoding="utf-8")


@mcp.tool()
async def get_core_context(agent_id: str, auth_token: str) -> str:
    """Load and compile all core memory blocks.

    Args:
        agent_id: Requesting agent ID
        auth_token: S2 authorization token
    """
    if not _check_auth(agent_id, auth_token):
        return "Error: Authentication failed"

    core_blocks = [
        "projectbrief.md",
        "productContext.md",
        "systemPatterns.md",
        "techContext.md",
        "activeContext.md",
        "progress.md",
    ]

    compiled = []
    for block in core_blocks:
        path = MEMORY_BANK_ROOT / block
        if path.exists():
            async with await anyio.open_file(path, mode="r", encoding="utf-8") as f:
                content = await f.read()
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()
            compiled.append(f"## {block.replace('.md', '')}\n\n{content}")

    return "\n\n---\n\n".join(compiled)


@mcp.tool()
async def get_block_status(block_name: str, agent_id: str, auth_token: str) -> str:
    """Get utilization status for a memory block.

    Args:
        block_name: Name of the block (e.g., 'techContext', 'progress')
        agent_id: Requesting agent ID
        auth_token: S2 authorization token
    """
    if not _check_auth(agent_id, auth_token):
        return "Error: Authentication failed"

    from pathlib import Path
    import yaml

    blocks_yaml = MEMORY_BANK_ROOT / "BLOCKS.yaml"
    limits = {}

    if blocks_yaml.exists():
        with open(blocks_yaml) as f:
            config = yaml.safe_load(f)
            for block_id, block_config in config.get("blocks", {}).items():
                limits[block_config.get("label")] = block_config.get(
                    "chars_limit", 5000
                )

    block_file = MEMORY_BANK_ROOT / f"{block_name}.md"
    if not block_file.exists():
        block_file = MEMORY_BANK_ROOT / "progress" / f"{block_name}.md"

    if not block_file.exists():
        return f"Block '{block_name}' not found"

    async with await anyio.open_file(block_file, mode="r", encoding="utf-8") as f:
        content = await f.read()
    chars = len(content)
    limit = limits.get(block_name, 5000)
    utilization = chars / limit if limit > 0 else 0

    status = "🟢 Good"
    if utilization > 0.9:
        status = "🔴 Overflow"
    elif utilization > 0.7:
        status = "🟡 Warning"

    return f"""Block: {block_name}
Characters: {chars:,} / {limit:,}
Utilization: {utilization:.1%}
Status: {status}
Path: {block_file.relative_to(MEMORY_BANK_ROOT)}"""


@mcp.tool()
async def search_memory_bank(query: str, agent_id: str, auth_token: str) -> str:
    """Search for text within the memory bank.

    Args:
        query: Search term to find
        agent_id: Requesting agent ID
        auth_token: S2 authorization token
    """
    if not _check_auth(agent_id, auth_token):
        return "Error: Authentication failed"

    import re
    from pathlib import Path

    results = []
    pattern = re.compile(query, re.IGNORECASE)

    for md_file in MEMORY_BANK_ROOT.rglob("*.md"):
        try:
            async with await anyio.open_file(md_file, mode="r", encoding="utf-8") as f:
                content = await f.read()
            matches = list(pattern.finditer(content))

            if matches:
                rel_path = md_file.relative_to(MEMORY_BANK_ROOT)
                match = matches[0]
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].replace("\n", " ")

                results.append(
                    f"- {rel_path} ({len(matches)} match{'es' if len(matches) > 1 else ''})"
                )
                results.append(f"  ...{context}...")
        except Exception:
            continue

    if not results:
        return f"No matches found for '{query}'"

    return "\n".join(results[:20])


@mcp.tool()
async def list_memory_files(agent_id: str, auth_token: str, tier: str = "all") -> str:
    """List files in the memory bank.

    Args:
        agent_id: Requesting agent ID
        auth_token: S2 authorization token
        tier: Filter by tier - 'core', 'recall', 'archival', or 'all'
    """
    if not _check_auth(agent_id, auth_token):
        return "Error: Authentication failed"

    from pathlib import Path

    tiers = {
        "core": [".md"],
        "recall": ["recall"],
        "archival": ["archival"],
        "progress": ["progress"],
    }

    output = []

    if tier in ("all", "core"):
        core_files = []
        for md_file in MEMORY_BANK_ROOT.glob("*.md"):
            async with await anyio.open_file(md_file, mode="r", encoding="utf-8") as f:
                chars = len(await f.read())
            core_files.append(f"  - {md_file.name} ({chars:,} chars)")
        output.append(
            f"Core Memory ({len(core_files)} files):\n" + "\n".join(sorted(core_files))
        )

    if tier in ("all", "recall"):
        recall_dir = MEMORY_BANK_ROOT / "recall"
        if recall_dir.exists():
            recall_files = list(recall_dir.rglob("*.md"))
            output.append(f"\nRecall Tier ({len(recall_files)} files)")

    if tier in ("all", "archival"):
        archival_dir = MEMORY_BANK_ROOT / "archival"
        if archival_dir.exists():
            archival_files = list(archival_dir.rglob("*.md"))
            output.append(f"\nArchival Tier ({len(archival_files)} files)")

    if tier in ("all", "progress"):
        progress_dir = MEMORY_BANK_ROOT / "progress"
        if progress_dir.exists():
            progress_files = list(progress_dir.rglob("*.md"))
            output.append(f"\nProgress Files ({len(progress_files)} files)")

    return "\n".join(output)


@mcp.prompt()
async def load_context_prompt() -> str:
    """Prompt template for loading memory context."""
    return """Load the XNAi memory bank context:

1. First, use the `get_core_context` tool to load all core blocks
2. Review the current priorities from activeContext
3. Check progress status using `get_block_status` for any relevant blocks

Provide a summary of the current project state and immediate priorities."""


@mcp.prompt()
async def search_and_summarize(query: str) -> str:
    """Prompt template for searching memory and summarizing findings.

    Args:
        query: Topic to search for
    """
    return f"""Search the memory bank for information about: {query}

1. Use the `search_memory_bank` tool with query "{query}"
2. For any relevant files found, read them using the memory://bank/ resource
3. Summarize the findings in a clear, organized format
4. Note any gaps or areas that need more documentation"""


if __name__ == "__main__":
    mcp.run()
