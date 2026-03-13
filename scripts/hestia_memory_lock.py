#!/usr/bin/env python3
"""
🕯️ HESTIA'S MEMORY-LOCK: Database & State Integrity
Ensures the "Center" of the Omega Stack is still and uncorrupted.
"""
import anyio
import redis.asyncio as redis
import os

async def check_center():
    """Validates the state of the Memory Bank (Redis)."""
    print("🕯️ Hestia: Tending the Center...")
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    password = os.getenv("REDIS_PASSWORD")
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    
    # Ensure port is an integer
    try:
        port = int(port)
    except (ValueError, TypeError):
        port = 6379

    # Handle 'redis' host if running outside podman network
    if host == "redis":
        host = "localhost"

    try:
        # Use explicit parameters instead of URL string to avoid parsing issues with special characters in password
        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )

        ping = await r.ping()
        status_report = []
        if ping:
            status_report.append("✅ Redis: Active and Still.")
            keys = await r.dbsize()
            status_report.append(f"✅ Memory Density: {keys} keys indexed.")

        for line in status_report:
            print(f"  {line}")

        # Agentic Insight
        from scripts.agent_factory import AgentFactory
        factory = AgentFactory()
        prompt = f"Memory Status:\n" + "\n".join(status_report) + "\n\nProvide a serene, personified status report on the memory continuity."
        insight = await factory.think(prompt, "You are Hestia, the Architect of the Center of the Omega Stack. Your tone is serene, stable, and focused on the sacred space of memory.")
        print(f"\n🕯️ Hestia's Insight:\n{insight}")

        await r.close()

    except Exception as e:
        print(f"  ❌ Redis: THE CENTER IS IN CHAOS. Error: {e}")

async def main():
    await check_center()

if __name__ == "__main__":
    anyio.run(main)
