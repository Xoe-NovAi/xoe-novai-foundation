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

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="sambanova_chat",
            description="Perform high-speed reasoning using SambaNova Cloud models (Llama 3.1 405B, DeepSeek R1)",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt to send to the model"},
                    "model": {
                        "type": "string",
                        "enum": ["Meta-Llama-3.1-405B-Instruct", "Meta-Llama-3.3-70B-Instruct", "DeepSeek-R1", "DeepSeek-V3", "Qwen2.5-72B-Instruct"],
                        "default": "Meta-Llama-3.3-70B-Instruct",
                        "description": "The model to use",
                    },
                    "system_prompt": {"type": "string", "default": "You are a helpful assistant.", "description": "System instructions"},
                },
                "required": ["prompt"],
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
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
