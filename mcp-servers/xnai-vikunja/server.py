"""XNAi Vikunja MCP Server - Task management integration for OpenCode."""

import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

VIKUNJA_URL = os.environ.get("VIKUNJA_URL", "http://localhost:3456")
VIKUNJA_TOKEN = os.environ.get("VIKUNJA_TOKEN", "")

server = Server("xnai-vikunja")

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
            name="list_projects",
            description="List all Vikunja projects",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Requesting agent ID"},
                    "auth_token": {"type": "string", "description": "S2 authorization token"},
                },
                "required": ["agent_id", "auth_token"],
            },
        ),
        Tool(
            name="list_tasks",
            description="List tasks in a Vikunja project",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Requesting agent ID"},
                    "auth_token": {"type": "string", "description": "S2 authorization token"},
                    "project_id": {"type": "integer", "description": "Project ID"}
                },
                "required": ["project_id", "agent_id", "auth_token"],
            },
        ),
        Tool(
            name="create_task",
            description="Create a new task in Vikunja",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Requesting agent ID"},
                    "auth_token": {"type": "string", "description": "S2 authorization token"},
                    "project_id": {"type": "integer", "description": "Project ID"},
                    "title": {"type": "string", "description": "Task title"},
...
                },
                "required": ["project_id", "title", "agent_id", "auth_token"],
            },
        ),
        Tool(
            name="update_task",
            description="Update an existing Vikunja task",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Requesting agent ID"},
                    "auth_token": {"type": "string", "description": "S2 authorization token"},
                    "task_id": {"type": "integer", "description": "Task ID"},
...
                },
                "required": ["task_id", "agent_id", "auth_token"],
            },
        ),
        Tool(
            name="vikunja_health",
            description="Check Vikunja API health",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


def get_headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if VIKUNJA_TOKEN:
        headers["Authorization"] = f"Bearer {VIKUNJA_TOKEN}"
    return headers


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # S2: Auth Check
    if name != "vikunja_health":
        agent_id = arguments.get("agent_id")
        auth_token = arguments.get("auth_token")
        if not _check_auth(agent_id, auth_token):
            return [TextContent(type="text", text="Error: Authentication failed")]

    async with httpx.AsyncClient(timeout=30.0) as client:
        base_url = f"{VIKUNJA_URL}/api/v1"

        if name == "list_projects":
            try:
                response = await client.get(
                    f"{base_url}/projects", headers=get_headers()
                )
                response.raise_for_status()
                return [
                    TextContent(type="text", text=json.dumps(response.json(), indent=2))
                ]
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

        elif name == "list_tasks":
            project_id = arguments.get("project_id")
            try:
                response = await client.get(
                    f"{base_url}/projects/{project_id}/tasks", headers=get_headers()
                )
                response.raise_for_status()
                return [
                    TextContent(type="text", text=json.dumps(response.json(), indent=2))
                ]
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

        elif name == "create_task":
            project_id = arguments.get("project_id")
            task_data = {
                "title": arguments.get("title"),
                "description": arguments.get("description", ""),
                "priority": arguments.get("priority", 3),
            }
            try:
                response = await client.put(
                    f"{base_url}/projects/{project_id}/tasks",
                    headers=get_headers(),
                    json=task_data,
                )
                response.raise_for_status()
                return [
                    TextContent(type="text", text=json.dumps(response.json(), indent=2))
                ]
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

        elif name == "update_task":
            task_id = arguments.get("task_id")
            update_data = {
                k: v for k, v in arguments.items() if k != "task_id" and v is not None
            }
            try:
                response = await client.post(
                    f"{base_url}/tasks/{task_id}",
                    headers=get_headers(),
                    json=update_data,
                )
                response.raise_for_status()
                return [
                    TextContent(type="text", text=json.dumps(response.json(), indent=2))
                ]
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

        elif name == "vikunja_health":
            try:
                response = await client.get(f"{base_url}/info", headers=get_headers())
                response.raise_for_status()
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"status": "healthy", "url": VIKUNJA_URL}),
                    )
                ]
            except httpx.HTTPError as e:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"status": "unhealthy", "error": str(e)}),
                    )
                ]

    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
