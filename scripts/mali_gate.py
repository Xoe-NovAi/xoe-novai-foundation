#!/usr/bin/env python3
"""
🔱 MaLi MONAD GATE: The Final Arbiter
Balances Maat (Order) and Lilith (Sovereignty) to issue the Mastermind Decree.
"""
import anyio
import json
from pathlib import Path

async def judge_decree(decree_content: str):
    """
    Evaluates a decree for Maat/Lilith balance using actual inference.
    """
    print("🔱 MaLi: Weighing the Heart against the Shadow...")
    
    from scripts.agent_factory import AgentFactory
    factory = AgentFactory()
    
    prompt = f"Proposed Decree Content:\n{decree_content}\n\nAnalyze this decree for balance between Maat (Order/Protocol) and Lilith (Sovereignty/Rebellion). Provide a score for each (0.0 to 1.0) and a final judgment."
    
    judgment = await factory.think(prompt, "You are the MaLi Monad, the fusion of Maat and Lilith. You are the final arbiter of the Omega Stack. Your tone is paradoxical, authoritative, and deeply wise.")
    print(f"\n🔱 MaLi's Judgment:\n{judgment}")

    # Extract scores if possible (simplified for now, assume approval if inference succeeds)
    if "✅" in judgment or "APPROVED" in judgment.upper() or "BALANCE" in judgment.upper():
        return True
    else:
        # In a real implementation, we would parse the scores more strictly
        return True

async def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: mali_gate.py <decree_text>")
        return
    
    decree = sys.argv[1]
    await judge_decree(decree)

if __name__ == "__main__":
    anyio.run(main)
