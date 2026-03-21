import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_a2a():
    # Configure the server parameters
    server_params = StdioServerParameters(
        command="podman",
        args=[
            "run", "-i", "--rm", "--network=host", "--pull=never",
            "--env-file", "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/.env",
            "-v", "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/storage:/storage:Z",
            "-v", "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/app:/app/app:ro",
            "xnai_memory_bank_mcp", "python", "server.py"
        ]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Register a test agent
            reg_result = await session.call_tool("register_agent", {
                "agent_id": "general",
                "capabilities": ["core", "strategy"],
                "memory_limit_gb": 1.0
            })
            print(f"Registration: {reg_result.content[0].text}")

            # 2. Add some 'Technical' memory to the general
            update_result = await session.call_tool("update_context", {
                "agent_id": "general",
                "context_type": "technical",
                "context_data": {
                    "summary": "Swap initialized with 16GB total capacity.",
                    "lessons_learned": ["Always cap parallel build jobs to 2."]
                }
            })
            print(f"Update: {update_result.content[0].text}")

            # 3. Test A2A Query from 'facet_1'
            # First register facet_1
            await session.call_tool("register_agent", {
                "agent_id": "facet_1",
                "capabilities": ["code"],
                "memory_limit_gb": 0.5
            })

            a2a_result = await session.call_tool("query_agent_memory", {
                "target_agent_id": "general",
                "query": "Swap",
                "requesting_agent_id": "facet_1"
            })
            print(f"A2A Result: {a2a_result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(test_a2a())
