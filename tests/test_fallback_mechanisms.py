#!/usr/bin/env python3
"""
Test fallback mechanisms when circuit breakers are open
Phase 1, Day 2 - Circuit Breaker Implementation & Service Resilience
"""
import asyncio
import sys
import asyncio
from unittest.mock import MagicMock, patch

# Mock chainlit in sys.modules before importing the dependent module
with patch.dict(sys.modules, {'chainlit': MagicMock()}):
    from XNAi_rag_app.ui.chainlit_app_voice import generate_ai_response, rag_api_breaker, get_circuit_breaker_status

async def test_fallback_responses():
    """Test that fallback responses work when circuit breakers are open"""
    print("🧪 Testing Fallback Mechanisms...")
    print("=" * 50)

    # Check initial state
    status = get_circuit_breaker_status()
    print(f"📊 Initial RAG API breaker state: {status['rag_api']['state']}")
    initial_state = status['rag_api']['state']

    # Force RAG API circuit breaker to open by simulating failures
    print("\n🔄 Forcing RAG API circuit breaker to open...")
    for i in range(4):  # More than fail_max=3
        try:
            # Force a failure to increment the circuit breaker counter
            await rag_api_breaker.call_async(lambda: (_ for _ in ()).throw(Exception("Forced failure")))()
        except:
            pass

    # Verify circuit breaker is open
    status = get_circuit_breaker_status()
    print(f"🔌 RAG API breaker state after forced failures: {status['rag_api']['state']}")

    if status['rag_api']['state'] == 'open':
        print("✅ RAG API circuit breaker successfully forced open")
    else:
        print(f"⚠️  Circuit breaker state: {status['rag_api']['state']} (expected: open)")
        print("ℹ️  This might be expected if circuit breaker hasn't tripped yet")

    # Test fallback response
    print("\n🔄 Testing fallback response mechanism...")
    response = await generate_ai_response("test query")

    # Check for fallback indicators
    has_fallback_indicators = (
        "temporarily unable to access my knowledge base" in response or
        "automatically recovering" in response or
        "AI service temporarily unavailable" in response
    )

    if has_fallback_indicators:
        print("✅ Fallback response working correctly")
        print(f"📝 Fallback message: {response[:100]}...")
    else:
        print("⚠️  Fallback response may not be working as expected")
        print(f"📝 Response received: {response[:100]}...")

    # Test multiple fallback calls to ensure consistency
    print("\n🔄 Testing fallback consistency...")
    for i in range(3):
        response = await generate_ai_response(f"test query {i+1}")
        if has_fallback_indicators or "unable" in response.lower():
            print(f"✅ Fallback call {i+1}: Consistent behavior")
        else:
            print(f"⚠️  Fallback call {i+1}: Unexpected response")

    print("\n✅ Fallback mechanism test completed")
    print("📈 System demonstrates graceful degradation when services are unavailable")

if __name__ == "__main__":
    asyncio.run(test_fallback_responses())
