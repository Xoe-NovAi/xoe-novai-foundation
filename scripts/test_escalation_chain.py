#!/usr/bin/env python3
"""
Xoe-NovAi Escalation Researcher Lab
===================================

Validates the 4-level escalation research chain.
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from app.XNAi_rag_app.services.escalation_researcher import EscalationResearcher
except ImportError as e:
    print(f"❌ Error: Could not import EscalationResearcher: {e}")
    sys.exit(1)

async def main():
    print("🚀 Launching Escalation Researcher Lab...")
    
    # Initialize the researcher
    # No redis for this simple test
    researcher = EscalationResearcher()
    
    query = "What are the core mandates of the Xoe-NovAi Foundation?"
    
    print(f"🔍 Research Query: '{query}'")
    print("-" * 50)
    
    start_time = time.time()
    
    # Use research_stream to see intermediate levels
    async for result in researcher.research_stream(query):
        level = result["level"]
        confidence = result["confidence"]
        vector = result.get("confidence_vector", {})
        latency = result["latency_ms"]
        
        print(f"\n[Level {level}] {result['model_id']}")
        print(f"   Overall Confidence: {confidence:.2%}")
        if vector:
            print(f"   Confidence Vector: {vector}")
        
        if "specialist_handoff" in result:
            spec = result["specialist_handoff"]
            print(f"   🎯 SURGICAL HANDOFF IDENTIFIED: {spec['role']} (Model: {spec['model']})")

        print(f"   Latency: {latency:.2f}ms")
        
        if level < 4 and confidence < 0.9:
            print(f"   ⚠️ Confidence below threshold. Escalating...")
        else:
            print(f"   ✅ Confidence achieved or Authority reached.")

    end_time = time.time()
    print("-" * 50)
    print(f"✅ Research chain complete in {(end_time - start_time)*1000:.2f}ms total")

if __name__ == "__main__":
    asyncio.run(main())
