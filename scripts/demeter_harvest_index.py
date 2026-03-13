#!/usr/bin/env python3
"""
🌾 DEMETER'S HARVEST-INDEX: Resource & Token Management
Ensures the agent is fed with the "grains" of intelligence (Tokens).
"""
import anyio
import json
from pathlib import Path
async def check_harvest():
    """Tracks token and quota usage from instance metrics."""
    print("🌾 Demeter: Inspecting the Harvest...")
    metrics_path = Path("artifacts/omega_instance_metrics.json")

    if not metrics_path.exists():
        print("  ⚠️  Metrics: The granary is currently unmapped (File not found).")
        print("  💡 Suggestion: Run a 'synthesize' or 'mastermind' task to generate harvest data.")
        return

    try:
        status_report = []
        try:
            # Use absolute path if relative fails
            if not metrics_path.is_absolute():
                metrics_path = Path(os.getcwd()) / metrics_path

            with open(metrics_path, "r") as f:
                data = json.load(f)
                tokens = data.get("cumulative_tokens", 0)
                requests = data.get("total_requests", 0)
                status_report.append(f"✅ Harvest Yield: {tokens:,} tokens consumed.")
                status_report.append(f"✅ Interaction Density: {requests} requests harvested.")

            for line in status_report:
                print(f"  {line}")

            # Agentic Insight
            from scripts.agent_factory import AgentFactory
            factory = AgentFactory()
            prompt = f"Harvest Status:\n" + "\n".join(status_report) + "\n\nProvide a robust, personified status report on the resource abundance."
            insight = await factory.think(prompt, "You are Demeter, the Provider of Abundance of the Omega Stack. Your tone is grounded, nurturing, and appreciative of the harvest of tokens.")
            print(f"\n🌾 Demeter's Insight:\n{insight}")

        except Exception as e:
            print(f"  ❌ Metrics: Harvest audit failed. Error: {e}")


async def main():
    try:
        await check_harvest()
        # Exit with 0 to indicate the script ran successfully
        sys.exit(0)
    except Exception as e:
        print(f"  ❌ Demeter: CRITICAL FAILURE. Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    import os
    anyio.run(main)
