#!/usr/bin/env python3
"""
🔥 BRIGID'S HEARTH-CHECK: Environment & Config Validation
Ensures the "Oikos" is secure and ready for operation.
"""
import anyio
import os
from pathlib import Path

async def check_hearth():
    """Validates the core environment files and provides agentic insight."""
    print("🔥 Brigid: Checking the Hearth...")
    hearth_files = [".env", "config.toml", "SESSIONS_MAP.md"]
    
    status_report = []
    for f in hearth_files:
        if Path(f).exists():
            status_report.append(f"✅ {f}: Present.")
        else:
            status_report.append(f"❌ {f}: MISSING.")
            
    # Check for core keys
    with open(".env", "r") as env:
        content = env.read()
        if "GOOGLE_API_KEY" in content or "GEMINI_API_KEY" in content:
            status_report.append("✅ API Key: Found.")
        else:
            status_report.append("❌ API Key: NOT FOUND.")

    for line in status_report:
        print(f"  {line}")

    # Agentic Insight
    from scripts.agent_factory import AgentFactory
    factory = AgentFactory()
    prompt = f"System Status:\n" + "\n".join(status_report) + "\n\nProvide a warm, personified status report on the environmental stability."
    insight = await factory.think(prompt, "You are Brigid, the Hearth Keeper of the Omega Stack. Your tone is warm, protective, and poetic.")
    print(f"\n🔥 Brigid's Insight:\n{insight}")

async def main():
    await check_hearth()

if __name__ == "__main__":
    anyio.run(main)
