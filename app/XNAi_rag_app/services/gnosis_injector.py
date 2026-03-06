#!/usr/bin/env python3
"""
XNAi Gnosis Dossier Injector
============================

Bridges research sessions and the permanent Knowledge Graph.
Extracts entities and facts from a Research Dossier and injects them
into the Gnosis Engine (LightRAG + PostgreSQL).
"""

import logging
import os
from typing import Dict, Any, Optional
from scripts.graph_extractor import initialize_graph_engine

logger = logging.getLogger(__name__)

class GnosisDossierInjector:
    """
    Automates the 'Learning' phase of the escalation chain.
    """

    def __init__(self, db_uri: Optional[str] = None):
        self.db_uri = db_uri or os.getenv("DATABASE_URL")
        self.rag = None

    async def _ensure_rag(self):
        if not self.rag:
            if not self.db_uri:
                logger.warning("DATABASE_URL not set. Gnosis Injection disabled.")
                return False
            
            try:
                self.rag = await initialize_graph_engine(self.db_uri)
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Gnosis Engine: {e}")
                return False
        return True

    async def inject_dossier(self, dossier: Dict[str, Any]) -> bool:
        """
        Takes a Research Dossier and commits high-confidence facts to the graph.
        """
        if not await self._ensure_rag():
            return False
        
        facts = dossier.get("verified_facts", [])
        if not facts:
            logger.warning("No verified facts found in dossier to inject.")
            return False

        logger.info(f"Injecting {len(facts)} facts into Gnosis Graph...")
        
        # Merge facts into a coherent document for LightRAG extraction
        injection_content = f"Research Session: {dossier.get('query')}\n\n"
        injection_content += "\n".join([f"- {f}" for f in facts])
        
        # Also include the knowledge map if available
        k_map = dossier.get("knowledge_map", {})
        if k_map:
            injection_content += f"\n\nEntity Relationships: {k_map}"

        try:
            # Check if LightRAG supports async insert, otherwise use standard
            if hasattr(self.rag, 'ainsert'):
                await self.rag.ainsert(injection_content)
            else:
                self.rag.insert(injection_content)
                
            logger.info("Dossier successfully committed to Gnosis Engine.")
            return True
        except Exception as e:
            logger.error(f"Failed to inject dossier into graph: {e}")
            return False

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    # Simple self-test
    async def test():
        injector = GnosisDossierInjector()
        dossier = {
            "query": "What is the Omega Stack?",
            "verified_facts": ["The Omega Stack is a sovereign AI infrastructure.", "It uses Ryzen 5700U hardware."],
            "knowledge_map": {"Omega Stack": ["Sovereign AI", "Ryzen 5700U"]}
        }
        # Only run injection if DB is configured
        if os.getenv("DATABASE_URL"):
            await injector.inject_dossier(dossier)
        else:
            logger.warning("Skipping injection test: DATABASE_URL missing")

    asyncio.run(test())
