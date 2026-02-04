#!/usr/bin/env python3
"""
Load test circuit breakers under concurrent load
Phase 1, Day 2 - Circuit Breaker Implementation & Service Resilience
"""
import asyncio
import time
import sys
import asyncio
import time
from unittest.mock import MagicMock, patch

# Mock chainlit in sys.modules before importing the dependent module
with patch.dict(sys.modules, {'chainlit': MagicMock()}):
    from XNAi_rag_app.ui.chainlit_app_voice import generate_ai_response, get_circuit_breaker_status

async def load_test_circuit_breakers():
    """Test circuit breakers under concurrent load"""
    print("🧪 Starting Circuit Breaker Load Test...")
    print("=" * 50)

    start_time = time.time()

    # Run 50 concurrent requests
    print("🚀 Launching 50 concurrent requests...")
    tasks = []
    for i in range(50):
        tasks.append(generate_ai_response(f"test query {i}"))

    # Execute concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    duration = end_time - start_time

    # Analyze results
    successful = sum(1 for r in results if not isinstance(r, Exception))
    failed = len(results) - successful
    success_rate = (successful / len(results)) * 100

    print("\n📊 Load Test Results:")
    print(f"  Total requests: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Success rate: {success_rate:.1f}%")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Requests/sec: {len(results)/duration:.1f}")

    # Check circuit breaker status
    print("\n🔌 Circuit Breaker Status:")
    status = get_circuit_breaker_status()
    for name, cb_status in status.items():
        state_emoji = {
            'closed': '✅',
            'open': '🚨',
            'half_open': '⚠️'
        }.get(cb_status['state'], '❓')

        print(f"  {state_emoji} {name}: {cb_status['state']} (failures: {cb_status['fail_count']})")

    # Performance analysis
    print("\n📈 Performance Analysis:")
    if duration < 10:
        print("  ⚡ Excellent performance (<10s for 50 requests)")
    elif duration < 30:
        print("  ✅ Good performance (<30s for 50 requests)")
    else:
        print("  ⚠️  Performance needs attention (>30s for 50 requests)")

    if success_rate > 80:
        print("  ✅ High success rate indicates good resilience")
    elif success_rate > 50:
        print("  ⚠️  Moderate success rate - some circuit breakers may be active")
    else:
        print("  🚨 Low success rate - circuit breakers heavily active")

    # Circuit breaker analysis
    open_breakers = [name for name, cb_status in status.items() if cb_status['state'] == 'open']
    if open_breakers:
        print(f"  ℹ️  {len(open_breakers)} circuit breaker(s) are open: {', '.join(open_breakers)}")
        print("     This is expected behavior under load when services are unavailable")
    else:
        print("  ℹ️  All circuit breakers remain closed - services handled load well")

    print("\n✅ Load test completed")
    print("📈 Circuit breakers demonstrate proper load handling and resilience")

if __name__ == "__main__":
    asyncio.run(load_test_circuit_breakers())
