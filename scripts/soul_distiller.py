#!/usr/bin/env python3
"""
🔱 SOUL DISTILLER: The Gnostic Evolution Engine
Distills 20-turn cycles into the agent's Soul system to record learning.
"""
import anyio
import yaml
import time
from pathlib import Path
from datetime import datetime

SOUL_PATH = Path("/app/memory_bank/mission_control/SOUL_PATHS.yaml")
CHRONICLE_DIR = Path("/app/memory_bank/mission_control/chronicles")

async def distill_cycle(session_id: str, turn_count: int, context_summary: str):
    """
    Distills the current cycle into the Soul Path.
    1. Extracts 'Gnosis' from context.
    2. Updates SOUL_PATHS.yaml.
    3. Records the evolution in the Chronicles.
    """
    print(f"🔱 Soul Distiller: Distilling cycle {turn_count//20} for [{session_id}]...")
    
    # Load existing Soul Path
    soul_data = {}
    if SOUL_PATH.exists():
        with open(SOUL_PATH, "r") as f:
            soul_data = yaml.safe_load(f) or {}

    # Update Evolution Record
    timestamp = datetime.now().isoformat()
    evolution_entry = {
        "timestamp": timestamp,
        "session_id": session_id,
        "turn_cycle": turn_count // 20,
        "gnosis_distilled": context_summary,
        "archetype_alignment": 0.95 # Placeholder for resonance engine
    }
    
    if session_id not in soul_data:
        soul_data[session_id] = {"evolution_history": []}
    
    soul_data[session_id]["evolution_history"].append(evolution_entry)
    
    # Write back to Soul Path
    with open(SOUL_PATH, "w") as f:
        yaml.dump(soul_data, f)
        
    print(f"✅ Gnosis Distilled into {SOUL_PATH}")
    
    # Generate Chronicle Record
    chronicle_path = CHRONICLE_DIR / f"EVOLUTION_{session_id}_{turn_count}.md"
    CHRONICLE_DIR.mkdir(parents=True, exist_ok=True)
    with open(chronicle_path, "w") as f:
        f.write(f"# 🔱 Soul Evolution Record: {session_id}\n")
        f.write(f"**Turn Cycle**: {turn_count // 20}\n")
        f.write(f"**Distilled Gnosis**: {context_summary}\n")
    
    return True

async def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: soul_distiller.py <session_id> <turn_count> <summary>")
        return
    
    await distill_cycle(sys.argv[1], int(sys.argv[2]), sys.argv[3])

if __name__ == "__main__":
    anyio.run(main)
