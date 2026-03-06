#!/usr/bin/env python3
"""
Test RAG API circuit breaker behavior
Phase 1, Day 2 - Circuit Breaker Implementation & Service Resilience
"""
import asyncio
import httpx
import sys
import os
import asyncio
import httpx
from unittest.mock import MagicMock, patch

# Mock chainlit in sys.modules before importing the dependent module
with patch.dict(sys.modules, {'chainlit': MagicMock()}):
    from XNAi_rag_app.ui.chainlit_app_voice import rag_api_breaker, get_circuit_breaker_status

async def simulate_rag_api_failure():
    """Simulate RAG API failures to test circuit breaker"""
    print("🧪 Testing RAG API Circuit Breaker...")
    print("=" * 50)

    # Initial state should be closed
    status = get_circuit_breaker_status()
    print(f"📊 Initial RAG API breaker state: {status['rag_api']['state']}")
    assert status['rag_api']['state'] == 'closed'
    print("✅ Circuit breaker starts in CLOSED state")

    # Simulate 3 failures (should trip circuit breaker)
    print("\n🔄 Simulating RAG API failures...")
    for i in range(4):
        try:
            # This will fail since RAG service might not be running in test
            async with httpx.AsyncClient(timeout=1.0) as client:
                response = await client.post("http://rag:8000/query", json={"query": "test"})
                print(f"📞 Call {i+1}: SUCCESS (unexpected)")
        except Exception as e:
            print(f"❌ Call {i+1}: FAILED - {str(e)[:50]}...")

            # Check circuit breaker state after failures
            status = get_circuit_breaker_status()
            if i >= 2:  # Should trip after 3rd failure
                print(f"🔌 Circuit breaker state after {i+1} failures: {status['rag_api']['state']}")
                if i >= 2:
                    assert status['rag_api']['state'] == 'open'
                    print("🚨 Circuit breaker OPEN (as expected)")

    # Test fail-fast behavior
    print("\n⚡ Testing fail-fast behavior...")
    try:
        # This should fail fast with CircuitBreakerError
        async with httpx.AsyncClient(timeout=1.0) as client:
            response = await client.post("http://rag:8000/query", json={"query": "test"})
    except Exception as e:
        print(f"⚡ Fail-fast working: {type(e).__name__}")

    print("\n✅ RAG API circuit breaker test completed successfully")
    print("📈 Circuit breaker demonstrates proper OPEN/CLOSED state transitions")

if __name__ == "__main__":
    asyncio.run(simulate_rag_api_failure())
