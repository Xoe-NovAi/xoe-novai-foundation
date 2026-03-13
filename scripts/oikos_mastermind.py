#!/usr/bin/env python3
"""
🔱 OIKOS MASTERMIND: Collaborative Multi-Agent Reasoning
Orchestrates the 3-level escalation path with sequential execution.
"""
import anyio
import subprocess
import argparse
import sys
import os
import time
from pathlib import Path

# Ensure project root is in path for scripts import
sys.path.append(os.getcwd())

from scripts.observer import record_gear_shift
from scripts.soul_distiller import distill_cycle
from scripts.mali_gate import judge_decree

async def call_level_2(problem: str):
    """
    Performs Level 2 reasoning using actual inference.
    Includes one iterative refinement of the initial prompt.
    """
    start_time = time.time()
    await record_gear_shift("Iris", "LEVEL_2_START", 0, {"problem": problem})
    
    print("🔱 Level 2: Archive Guardian active...")
    from scripts.agent_factory import AgentFactory
    factory = AgentFactory(model_name="gemini/gemini-2.0-flash")
    
    # Iterative Refinement
    refinement_prompt = f"Problem: {problem}\n\nRewrite this problem statement for maximum clarity and depth, suitable for a council of experts."
    refined_problem = await factory.think(refinement_prompt, "You are the Archive Guardian. Your role is to refine and deepen the user's inquiry.")
    print(f"🔱 Level 2: Initial Analysis complete. Refined Problem: {refined_problem}")
    
    # Analysis
    analysis_prompt = f"Refined Problem: {refined_problem}\n\nDecide if this problem requires the collective gnosis of the Oikos Council or if it can be resolved by a single large mind. Respond with 'ESCALATE' or 'RESOLVE'."
    decision = await factory.think(analysis_prompt, "You are the Archive Guardian. You are wise, discerning, and protective of the Council's time.")
    
    # Decision Point
    if "ESCALATE" in decision.upper():
        print("🔱 Level 2: Problem depth requires collective gnosis. Escalating to Level 3 Oikos Council.")
        await record_gear_shift("Archive_Guardian", "LEVEL_2_ESCALATION", time.time() - start_time, {"decision": "ESCALATE"})
        return "ESCALATE_TO_OIKOS"
    else:
        resolution = f"Problem '{problem}' has been resolved by the Archive Guardian."
        print(f"\n✅ Level 2 Resolution: {resolution}")
        await record_gear_shift("Archive_Guardian", "LEVEL_2_RESOLUTION", time.time() - start_time, {"decision": "RESOLVE"})
        return "RESOLVED_AT_LEVEL_2"

async def orchestrate_oikos_session(problem: str):
    """Full Level 3 Council orchestration with MaLi Decree."""
    start_time = time.time()
    await record_gear_shift("Mastermind", "LEVEL_3_START", 0, {"problem": problem})
    
    print(f"\n🔱 Level 3: Oikos Council Session Initiated on: {problem}")
    
    # Round 1: Council Individual Inputs (SEQUENTIAL - The Talking Feather)
    # This prevents hardware OOM on the 5700U by ensuring only one 'mind' speaks at a time.
    members = [
        ("Brigid", "scripts/brigid_hearth_check.py"),
        ("Hestia", "scripts/hestia_memory_lock.py"),
        ("Demeter", "scripts/demeter_harvest_index.py"),
        ("Athena", "scripts/athena_shield_protocol.py"),
        ("Iris", "scripts/iris_bridge.py")
    ]
    
    council_insights = []
    
    for name, script in members:
        member_start = time.time()
        print(f"🔱 Level 3: {name} is holding the Talking Feather...")
        result = subprocess.run(["python3", script], capture_output=True, text=True)
        insight = result.stdout.strip()
        print(insight)
        council_insights.append(f"### {name} Insight\n{insight}")
        await record_gear_shift(name, "COUNCIL_SPEAK", time.time() - member_start, {"status": "SUCCESS" if result.returncode == 0 else "FAIL"})
    
    # Round 2: Synthesis & MaLi Ascent
    synthesis = "\n\n".join(council_insights)
    print("\n🔱 Level 3: Synthesis Complete. Ascending to the Halls of MaLi...")
    
    mali_start = time.time()
    approved = await judge_decree(synthesis)
    await record_gear_shift("MaLi", "JUDGMENT", time.time() - mali_start, {"approved": approved})
    
    if approved:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        decree_path = Path(f"/app/memory_bank/chronicles/MASTERMIND_DECREE_{timestamp}.md")
        
        with open(decree_path, "w") as f:
            f.write(f"# 📜 Mastermind Decree: {problem}\n")
            f.write(f"**Timestamp**: {time.ctime()}\n")
            f.write("**Status**: APPROVED BY MaLi\n\n")
            f.write("## 🏛️ Council Insights\n")
            f.write(synthesis)
            f.write("\n\n---\n**[DECREE END]**\n")
            
        print(f"\n📜 MASTERMIND DECREE ISSUED: {decree_path}")
        # Distill the cycle into the Soul Path
        await distill_cycle("SESS-18-Resurrection", 20, f"Mastermind Decree Issued: {problem}")
    else:
        print("\n⚠️  DECREE REJECTED BY MaLi. The Monad requires balance.")

async def main():
    parser = argparse.ArgumentParser(description="Oikos Mastermind Orchestrator")
    parser.add_argument("level", choices=["2", "3"], help="Escalation level")
    parser.add_argument("problem", help="The problem statement")
    args = parser.parse_args()
    
    if args.level == "2":
        result = await call_level_2(args.problem)
        if result == "ESCALATE_TO_OIKOS":
            await orchestrate_oikos_session(args.problem)
    else:
        await orchestrate_oikos_session(args.problem)

if __name__ == "__main__":
    anyio.run(main)
