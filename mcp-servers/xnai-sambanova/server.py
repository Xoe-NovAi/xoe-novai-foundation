"""XNAi SambaNova MCP Server - High-speed model integration for Omega CLI."""

import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_API_URL = "https://api.sambanova.ai/v1"

server = Server("xnai-sambanova")

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

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="sambanova_chat",
            description="Perform high-speed reasoning using SambaNova Cloud models",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Requesting agent ID"},
                    "auth_token": {"type": "string", "description": "S2 authorization token"},
                    "prompt": {"type": "string", "description": "The prompt to send to the model"},
                    "model": {
...
                },
                "required": ["prompt", "agent_id", "auth_token"],
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    agent_id = arguments.get("agent_id")
    auth_token = arguments.get("auth_token")
    if not _check_auth(agent_id, auth_token):
        return [TextContent(type="text", text="Error: Authentication failed")]

    if not SAMBANOVA_API_KEY:
        # Try rotation if single key missing
        SAMBA_KEY_1 = os.environ.get("SAMBANOVA_API_KEY_1")
        if SAMBA_KEY_1:
            api_key = SAMBA_KEY_1
        else:
            return [TextContent(type="text", text="Error: SAMBANOVA_API_KEY not set.")]
    else:
        api_key = SAMBANOVA_API_KEY

    async with httpx.AsyncClient(timeout=60.0) as client:
        if name == "sambanova_chat":
            prompt = arguments.get("prompt", "")
            model = arguments.get("model", "Meta-Llama-3.3-70B-Instruct")
            system_prompt = arguments.get("system_prompt", "You are a helpful assistant.")

            try:
                response = await client.post(
                    f"{SAMBANOVA_API_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                return [TextContent(type="text", text=content)]
            except Exception as e:
                return [TextContent(type="text", text=f"SambaNova API Error: {str(e)}")]

    return [TextContent(type="text", text="Unknown tool")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
