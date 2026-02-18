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


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_projects",
            description="List all Vikunja projects",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_tasks",
            description="List tasks in a Vikunja project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "Project ID"}
                },
                "required": ["project_id"],
            },
        ),
        Tool(
            name="create_task",
            description="Create a new task in Vikunja",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "Project ID"},
                    "title": {"type": "string", "description": "Task title"},
                    "description": {
                        "type": "string",
                        "description": "Task description",
                    },
                    "priority": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "description": "Priority (1=critical, 5=someday)",
                    },
                },
                "required": ["project_id", "title"],
            },
        ),
        Tool(
            name="update_task",
            description="Update an existing Vikunja task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID"},
                    "title": {"type": "string", "description": "New title"},
                    "description": {"type": "string", "description": "New description"},
                    "done": {"type": "boolean", "description": "Mark as done"},
                },
                "required": ["task_id"],
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
