"""
XNAi Agent Bus MCP Server — Redis Streams with Consumer Groups
================================================================
Multi-agent coordination via reliable Redis Streams delivery.

Changes vs v1.0.0:
  - FIX: All stream keys unified to `xnai:agent_bus` (was: tasks/results split)
  - FIX: Consumer groups (XGROUP CREATE + XREADGROUP + XACK + XAUTOCLAIM)
  - ADD: `ack_task` tool for explicit message acknowledgement
  - ADD: `recover_tasks` tool for XAUTOCLAIM stale message recovery

Stream: xnai:agent_bus
Group:  xnai-mcp-server
"""

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
STREAM_KEY = "xnai:agent_bus"
CONSUMER_GROUP = "xnai-mcp-server"
CONSUMER_NAME = f"mcp-{uuid.uuid4().hex[:8]}"
# Reclaim messages idle >30s (prevents permanent stalls)
AUTOCLAIM_IDLE_MS = 30_000

server = Server("xnai-agentbus")
redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client


async def ensure_consumer_group(r: redis.Redis) -> None:
    """
    Create the consumer group if it doesn't exist.
    Uses MKSTREAM so the stream is auto-created if missing.
    """
    try:
        await r.xgroup_create(
            name=STREAM_KEY,
            groupname=CONSUMER_GROUP,
            id="0",        # read all messages from beginning
            mkstream=True, # create stream if it doesn't exist
        )
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            pass  # Group already exists — normal on restart
        else:
            raise


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="publish_task",
            description=(
                "Publish a task to the XNAi Agent Bus (xnai:agent_bus) "
                "for multi-agent coordination via Redis Streams."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Agent role (architect, coder, security, documenter, researcher)",
                    },
                    "action": {"type": "string", "description": "Action to perform"},
                    "payload": {"type": "object", "description": "Task payload"},
                    "target_did": {
                        "type": "string",
                        "description": "Optional target agent DID (e.g. did:xnai:sovereign-mc-v1)",
                    },
                },
                "required": ["role", "action", "payload"],
            },
        ),
        Tool(
            name="read_tasks",
            description=(
                "Read pending tasks from the Agent Bus using consumer group delivery. "
                "Messages are delivered once and must be acknowledged with ack_task."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "default": 10,
                        "description": "Number of tasks to read (max 100)",
                    },
                    "block_ms": {
                        "type": "integer",
                        "default": 100,
                        "description": "Block up to N ms waiting for messages (0 = no block)",
                    },
                },
            },
        ),
        Tool(
            name="ack_task",
            description="Acknowledge a task message after processing (XACK).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Redis Streams message ID to acknowledge",
                    }
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="recover_tasks",
            description=(
                "Recover stale tasks (XAUTOCLAIM) that have been pending >30s "
                "and reassign them to this consumer for reprocessing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "default": 10,
                        "description": "Max number of stale messages to reclaim",
                    }
                },
            },
        ),
        Tool(
            name="bus_health",
            description="Check Agent Bus Redis connection health.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    r = await get_redis()
    await ensure_consumer_group(r)

    # -------------------------------------------------------------------------
    # publish_task
    # -------------------------------------------------------------------------
    if name == "publish_task":
        role = arguments.get("role", "coder")
        action = arguments.get("action", "")
        payload = arguments.get("payload", {})
        target_did = arguments.get("target_did", "")

        message = {
            "agent_id": f"opencode-{uuid.uuid4().hex[:8]}",
            "role": role,
            "action": action,
            "payload": json.dumps(payload),  # Streams store strings
            "target_did": target_did,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": str(uuid.uuid4()),
        }

        try:
            msg_id = await r.xadd(STREAM_KEY, message)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "published",
                            "stream": STREAM_KEY,
                            "message_id": msg_id,
                            "message": message,
                        },
                        indent=2,
                    ),
                )
            ]
        except redis.RedisError as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    # -------------------------------------------------------------------------
    # read_tasks (XREADGROUP — reliable consumer delivery)
    # -------------------------------------------------------------------------
    elif name == "read_tasks":
        count = min(int(arguments.get("count", 10)), 100)
        block_ms = int(arguments.get("block_ms", 100))

        try:
            results = await r.xreadgroup(
                groupname=CONSUMER_GROUP,
                consumername=CONSUMER_NAME,
                streams={STREAM_KEY: ">"},  # ">" = only undelivered messages
                count=count,
                block=block_ms if block_ms > 0 else None,
            )
            messages = []
            for _stream_name, entries in (results or []):
                for entry_id, data in entries:
                    # Deserialize payload JSON if present
                    if "payload" in data:
                        try:
                            data["payload"] = json.loads(data["payload"])
                        except (json.JSONDecodeError, TypeError):
                            pass
                    messages.append({"id": entry_id, "data": data})

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "count": len(messages),
                            "consumer": CONSUMER_NAME,
                            "group": CONSUMER_GROUP,
                            "stream": STREAM_KEY,
                            "tasks": messages,
                        },
                        indent=2,
                    ),
                )
            ]
        except redis.RedisError as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    # -------------------------------------------------------------------------
    # ack_task (XACK — mark message processed)
    # -------------------------------------------------------------------------
    elif name == "ack_task":
        message_id = arguments.get("message_id", "")
        if not message_id:
            return [TextContent(type="text", text=json.dumps({"error": "message_id required"}))]

        try:
            acked = await r.xack(STREAM_KEY, CONSUMER_GROUP, message_id)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "acknowledged" if acked else "not_found",
                            "message_id": message_id,
                            "acked_count": acked,
                        }
                    ),
                )
            ]
        except redis.RedisError as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    # -------------------------------------------------------------------------
    # recover_tasks (XAUTOCLAIM — reclaim stale PEL entries)
    # -------------------------------------------------------------------------
    elif name == "recover_tasks":
        count = min(int(arguments.get("count", 10)), 100)

        try:
            # XAUTOCLAIM: reclaim messages idle > AUTOCLAIM_IDLE_MS
            result = await r.xautoclaim(
                name=STREAM_KEY,
                groupname=CONSUMER_GROUP,
                consumername=CONSUMER_NAME,
                min_idle_time=AUTOCLAIM_IDLE_MS,
                start_id="0-0",
                count=count,
            )
            # result: (next_id, messages, deleted_ids)
            next_id, entries, deleted = result if len(result) == 3 else (result[0], result[1], [])
            messages = []
            for entry_id, data in entries:
                if "payload" in data:
                    try:
                        data["payload"] = json.loads(data["payload"])
                    except (json.JSONDecodeError, TypeError):
                        pass
                messages.append({"id": entry_id, "data": data})

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "recovered",
                            "count": len(messages),
                            "next_id": next_id,
                            "deleted_ids": deleted,
                            "tasks": messages,
                        },
                        indent=2,
                    ),
                )
            ]
        except redis.RedisError as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    # -------------------------------------------------------------------------
    # bus_health
    # -------------------------------------------------------------------------
    elif name == "bus_health":
        try:
            pong = await r.ping()
            # Get stream info if it exists
            stream_info: dict[str, Any] = {}
            try:
                info = await r.xinfo_stream(STREAM_KEY)
                stream_info = {
                    "length": info.get("length", 0),
                    "first_entry_id": str(info.get("first-entry", ["?"])[0]) if info.get("first-entry") else None,
                    "last_entry_id": str(info.get("last-entry", ["?"])[0]) if info.get("last-entry") else None,
                }
            except redis.RedisError:
                stream_info = {"note": "stream not yet created"}

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "healthy" if pong else "unhealthy",
                            "url": REDIS_URL,
                            "stream": STREAM_KEY,
                            "group": CONSUMER_GROUP,
                            "consumer": CONSUMER_NAME,
                            "stream_info": stream_info,
                        },
                        indent=2,
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

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
