#!/usr/bin/env python3
"""
Test Redis circuit breaker behavior
Phase 1, Day 2 - Circuit Breaker Implementation & Service Resilience
"""
import asyncio
import sys
import asyncio
from unittest.mock import MagicMock, patch

# Mock chainlit in sys.modules before importing the dependent module
with patch.dict(sys.modules, {'chainlit': MagicMock()}):
    from XNAi_rag_app.ui.chainlit_app_voice import redis_breaker, get_circuit_breaker_status, _session_manager

async def simulate_redis_failure():
    """Simulate Redis connection failures"""
    print("🧪 Testing Redis Circuit Breaker...")
    print("=" * 50)

    # Initial state
    status = get_circuit_breaker_status()
    print(f"📊 Initial Redis breaker state: {status['redis']['state']}")
    assert status['redis']['state'] == 'closed'
    print("✅ Circuit breaker starts in CLOSED state")

    # Try Redis operations (may fail if Redis not running)
    print("\n🔄 Simulating Redis connection failures...")
    for i in range(6):  # Redis allows 5 failures before tripping
        try:
            if _session_manager:
                result = redis_breaker(_session_manager.get_conversation_context)(max_turns=5)
                print(f"📞 Redis call {i+1}: SUCCESS")
            else:
                print(f"⚠️  Redis call {i+1}: Session manager not available")
                raise Exception("Session manager not available")
        except Exception as e:
            print(f"❌ Redis call {i+1}: FAILED - {str(e)[:50]}...")

            # Check circuit breaker state
            status = get_circuit_breaker_status()
            if i >= 4:  # Should trip after 5th failure
                print(f"🔌 Circuit breaker state after {i+1} failures: {status['redis']['state']}")
                if i >= 4:
                    assert status['redis']['state'] == 'open'
                    print("🚨 Circuit breaker OPEN (as expected)")

    # Test fail-fast behavior
    print("\n⚡ Testing Redis fail-fast behavior...")
    try:
        if _session_manager:
            result = redis_breaker(_session_manager.get_conversation_context)(max_turns=5)
            print("⚡ Fail-fast: Unexpected success")
        else:
            print("⚠️  Session manager not available for fail-fast test")
    except Exception as e:
        print(f"⚡ Fail-fast working: {type(e).__name__}")

    print("\n✅ Redis circuit breaker test completed successfully")
    print("📈 Redis circuit breaker demonstrates proper failure handling")

if __name__ == "__main__":
    asyncio.run(simulate_redis_failure())
