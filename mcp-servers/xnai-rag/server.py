"""XNAi RAG MCP Server - Semantic search integration for OpenCode."""

import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

RAG_API_URL = os.environ.get("RAG_API_URL", "http://localhost:8000")

server = Server("xnai-rag")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="semantic_search",
            description="Search the XNAi Foundation knowledge base using hybrid semantic/lexical search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "mode": {
                        "type": "string",
                        "enum": ["semantic", "lexical", "hybrid"],
                        "default": "hybrid",
                        "description": "Search mode",
                    },
                    "top_k": {
                        "type": "integer",
                        "default": 10,
                        "description": "Number of results to return",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="rag_health",
            description="Check RAG API health status",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        if name == "semantic_search":
            query = arguments.get("query", "")
            mode = arguments.get("mode", "hybrid")
            top_k = arguments.get("top_k", 10)

            try:
                response = await client.post(
                    f"{RAG_API_URL}/search",
                    json={"query": query, "mode": mode, "top_k": top_k},
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for r in data.get("results", []):
                    results.append(
                        {
                            "source": r.get("source", "unknown"),
                            "score": r.get("score", 0),
                            "content": r.get("content", "")[:500],
                        }
                    )

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "query": query,
                                "mode": mode,
                                "total": data.get("total", 0),
                                "latency_ms": data.get("latency_ms", 0),
                                "results": results,
                            },
                            indent=2,
                        ),
                    )
                ]
            except httpx.HTTPError as e:
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

        elif name == "rag_health":
            try:
                response = await client.get(f"{RAG_API_URL}/health")
                response.raise_for_status()
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"status": "healthy", "url": RAG_API_URL}),
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
