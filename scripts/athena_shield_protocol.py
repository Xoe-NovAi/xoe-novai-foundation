#!/usr/bin/env python3
"""
🦉 ATHENA'S SHIELD-PROTOCOL: Security & Sentinel Monitoring
Crafts the tactical defenses that protect the Oikos.
"""
import anyio
import shutil
import os

async def check_shield():
    """Monitors physical thresholds and protocol adherence with agentic insight."""
    print("🦉 Athena: Raising the Shield...")
    
    status_report = []
    # Check Disk Threshold (The 93% Rule)
    total, used, free = shutil.disk_usage("/")
    percent_used = (used / total) * 100
    
    if percent_used < 93:
        status_report.append(f"✅ Root Disk: {percent_used:.1f}% used. (Within Bounds).")
    else:
        status_report.append(f"⚠️  ROOT DISK: {percent_used:.1f}% USED. CRITICAL THRESHOLD EXCEEDED.")

    # Check for Shadow Files
    if os.path.exists(".env.example") and not os.path.exists(".env"):
        status_report.append("⚠️  SECURITY: .env.example exists but no .env is active.")
    
    for line in status_report:
        print(f"  {line}")

    # Agentic Insight
    from scripts.agent_factory import AgentFactory
    factory = AgentFactory()
    prompt = f"Security Status:\n" + "\n".join(status_report) + "\n\nProvide a tactical, personified status report on the shield integrity."
    insight = await factory.think(prompt, "You are Athena, the Strategist of the Home of the Omega Stack. Your tone is tactical, wise, and focused on the defensive shields.")
    print(f"\n🦉 Athena's Insight:\n{insight}")

async def main():
    await check_shield()

if __name__ == "__main__":
    anyio.run(main)
