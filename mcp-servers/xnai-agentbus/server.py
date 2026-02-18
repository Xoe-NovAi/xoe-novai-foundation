"""XNAi Agent Bus MCP Server - Redis Streams integration for OpenCode."""

import json
import os
from typing import Any
from datetime import datetime, timezone
import uuid

import redis.asyncio as redis
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

server = Server("xnai-agentbus")
redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="publish_task",
            description="Publish a task to the Agent Bus for multi-agent coordination",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Agent role (architect, coder, security, documenter, researcher)",
                    },
                    "action": {"type": "string", "description": "Action to perform"},
                    "payload": {"type": "object", "description": "Task payload"},
                },
                "required": ["role", "action", "payload"],
            },
        ),
        Tool(
            name="read_results",
            description="Read results from the Agent Bus",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "default": 10,
                        "description": "Number of results to read",
                    }
                },
            },
        ),
        Tool(
            name="bus_health",
            description="Check Agent Bus Redis connection health",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    r = await get_redis()

    if name == "publish_task":
        role = arguments.get("role", "coder")
        action = arguments.get("action", "")
        payload = arguments.get("payload", {})

        message = {
            "agent_id": f"opencode-{uuid.uuid4().hex[:8]}",
            "role": role,
            "action": action,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": str(uuid.uuid4()),
        }

        try:
            await r.xadd("xnai:tasks", message)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "published",
                            "stream": "xnai:tasks",
                            "message": message,
                        },
                        indent=2,
                    ),
                )
            ]
        except redis.RedisError as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "read_results":
        count = arguments.get("count", 10)

        try:
            results = await r.xread({"xnai:results": "0"}, count=count)
            messages = []
            for stream_name, entries in results:
                for entry_id, data in entries:
                    messages.append({"id": entry_id, "data": data})

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"count": len(messages), "results": messages}, indent=2
                    ),
                )
            ]
        except redis.RedisError as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "bus_health":
        try:
            pong = await r.ping()
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"status": "healthy" if pong else "unhealthy", "url": REDIS_URL}
                    ),
                )
            ]
        except redis.RedisError as e:
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
