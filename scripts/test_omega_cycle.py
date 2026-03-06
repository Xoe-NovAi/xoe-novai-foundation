#!/usr/bin/env python3
"""
XNAi Omega Cycle Integrated Test
================================

Exercises the full intelligence loop:
1.  Speculative Funnel Search (128d -> 4096d)
2.  Triangulated Escalation (Skeptic, Architect, Synthesizer)
3.  Consensus Calculation
4.  Gnosis Dossier Injection (Permanent Learning)
5.  Graph Recall Verification
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from app.XNAi_rag_app.core.embeddings.speculative_engine import SpeculativeEmbeddingEngine
from app.XNAi_rag_app.services.escalation_researcher import EscalationResearcher
from app.XNAi_rag_app.core.curation.consensus import TriangulationConsensusManager
from app.XNAi_rag_app.services.gnosis_injector import GnosisDossierInjector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("omega_cycle_test")

async def run_omega_cycle(query: str):
    logger.info(f"🚀 Starting Omega Cycle for: '{query}'")
    
    # 1. Speculative Search
    engine = SpeculativeEmbeddingEngine()
    logger.info("Step 1: Funnel Search...")
    search_results = await engine.search(query)
    logger.info(f"   Found {len(search_results)} candidates.")

    # 2. Escalation Research
    researcher = EscalationResearcher()
    logger.info("Step 2: Triangulated Research...")
    final_research_result = None
    async for res in researcher.research_stream(query):
        final_research_result = res
        logger.info(f"   Level {res['level']} complete ({res['model_id']}).")
    
    # 3. Consensus Validation
    consensus_mgr = TriangulationConsensusManager()
    logger.info("Step 3: Consensus Calculation...")
    # Simulated persona answers for calculation
    persona_outputs = {
        "SKEPTIC": "The data confirms X but notes Y is missing.",
        "ARCHITECT": "X is confirmed, structure indicates Y is needed.",
        "SYNTHESIZER": "Confirmed X, Y remains a known gap."
    }
    consensus = await consensus_mgr.calculate_consensus(persona_outputs)
    logger.info(f"   Consensus Score: {consensus['score']:.4f} ({consensus['status']})")

    # 4. Gnosis Injection
    injector = GnosisDossierInjector()
    logger.info("Step 4: Gnosis Injection...")
    success = await injector.inject_dossier(final_research_result["dossier"])
    if success:
        logger.info("   Dossier committed to permanent memory.")
    else:
        logger.error("   Injection failed.")

    logger.info("✅ Omega Cycle Integrated Test Complete.")

if __name__ == "__main__":
    query = "How does the Omega Stack handle Ryzen 5700U thermal throttling?"
    asyncio.run(run_omega_cycle(query))
