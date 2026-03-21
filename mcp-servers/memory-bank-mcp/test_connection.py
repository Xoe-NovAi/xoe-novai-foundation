import asyncio
from pathlib import Path
from server import MemoryBankMCP

async def test_connection():
    m = MemoryBankMCP()
    print("Initializing Memory Bank MCP...")
    # Bypass Redis initialization to test filesystem-only mode
    m.redis = None
    m.memory_bank_path = Path("./storage/memory_bank")
    m.memory_bank_path.mkdir(parents=True, exist_ok=True)
    print("Memory Bank MCP initialized successfully!")
    print("Testing agent registration...")
    result = await m.register_agent('test-agent', ['test-capability'], 1.0)
    print("Agent registration result:", result)

if __name__ == "__main__":
    asyncio.run(test_connection())
