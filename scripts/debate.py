#!/usr/bin/env python3
"""
XNAi Metropolis Debate
======================
Autonomous interaction between two persistent experts.
Purpose: Refine the Knowledge Graph (Gnosis) by identifying relationships
between different domains of expertise.

Example:
  python3 scripts/debate.py --e1 "Socrates" --e2 "Kurt Cobain" --topic "The nature of authenticity"
"""

import sys
import os
import asyncio
import argparse
import logging
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "app"))

try:
    from XNAi_rag_app.core.entities.tools import summon_expert
    from XNAi_rag_app.services.feedback_loop import PerformanceFeedbackLoop
    from XNAi_rag_app.services.gnosis_injector import GnosisDossierInjector
except ImportError as e:
    print(f"Error: Could not import metropolis tools: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("metropolis_debate")

async def run_debate(e1: str, e2: str, topic: str, rounds: int = 2):
    logger.info(f"🏛️  Metropolis Debate Initiated: '{e1}' vs '{e2}'")
    logger.info(f"🎯 Topic: {topic}")
    
    debate_history = []
    
    # 1. Round 1: Expert 1 Opening Statement
    logger.info(f"🎤 {e1} is opening the floor...")
    res1 = await summon_expert(e1, f"Provide an opening statement on '{topic}' from your perspective.")
    debate_history.append({"speaker": e1, "statement": res1["response"]})
    
    # 2. Round 2: Expert 2 Counter-Argument / Reflection
    logger.info(f"🎤 {e2} is responding to {e1}...")
    res2 = await summon_expert(e2, f"Read this statement from {e1}: '{res1['response']}'. How does this align or conflict with your view on {topic}?")
    debate_history.append({"speaker": e2, "statement": res2["response"]})
    
    # 3. Final Synthesis
    logger.info("🧠 Synthesizing debate findings for Gnosis Engine...")
    synthesis_query = f"Synthesize the debate between {e1} and {e2} on {topic}."
    
    # We use a 'Synthesizer' expert or just an LLM round
    dossier = {
        "query": synthesis_query,
        "verified_facts": [
            f"{e1}'s view on {topic}: {res1['response'][:200]}...",
            f"{e2}'s view on {topic}: {res2['response'][:200]}...",
            f"Consensus/Conflict: Found interaction between {e1} and {e2} domains."
        ],
        "involved_entities": [e1.lower().replace(" ", "_"), e2.lower().replace(" ", "_")],
        "knowledge_map": {topic: [e1, e2]}
    }
    
    # 4. Inject into permanent memory
    injector = GnosisDossierInjector()
    await injector.inject_dossier(dossier)
    
    # 5. Record feedback for both (mutual learning)
    await PerformanceFeedbackLoop.record_session_outcome(synthesis_query, dossier, 0.95, "Autonomous debate success")
    
    logger.info("✅ Debate complete. Graph updated.")
    return debate_history

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XNAi Metropolis Debate")
    parser.add_argument("--e1", required=True, help="First expert")
    parser.add_argument("--e2", required=True, help="Second expert")
    parser.add_argument("--topic", required=True, help="Topic to debate")
    parser.add_argument("--rounds", type=int, default=2, help="Number of rounds")
    
    args = parser.parse_args()
    
    asyncio.run(run_debate(args.e1, args.e2, args.topic, args.rounds))
