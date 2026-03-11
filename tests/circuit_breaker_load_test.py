#!/usr/bin/env python3
"""
Load test circuit breakers under concurrent load
Phase 1, Day 2 - Circuit Breaker Implementation & Service Resilience
"""
import asyncio
import time
import sys
from unittest.mock import MagicMock, patch

# Mock chainlit in sys.modules before importing the dependent module
with patch.dict(sys.modules, {'chainlit': MagicMock()}):
    from XNAi_rag_app.ui.chainlit_app_unified import stream_from_api, check_api_health

async def generate_ai_response(query: str):
    """Wrapper to maintain compatibility with existing test structure"""
    try:
        async for event_type, content, metadata in stream_from_api(query):
            if event_type == "error":
                return f"Error: {metadata.get('error')}"
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"

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
    results = await asyncio.gather(*tasks)

    # Results summary
    duration = time.time() - start_time
    success_count = results.count("Success")
    success_rate = (success_count / 50) * 100

    print("\n📊 Load Test Results:")
    print(f"  ⏱️  Total Duration: {duration:.2f}s")
    print(f"  ✅ Successful Requests: {success_count}/50")
    print(f"  📈 Success Rate: {success_rate:.1f}%")

    # Verify final health
    is_healthy, health_msg = await check_api_health()
    print(f"🧪 API Health Post-Load: {'🟢 Healthy' if is_healthy else '🔴 Impacted'}")
    print(f"💬 Health Message: {health_msg}")

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
        print("  ⚠️  Moderate success rate - circuit breakers may have triggered")
    else:
        print("  🚨 Low success rate - system under heavy pressure")

    print("\n✅ Load test completed")

if __name__ == "__main__":
    asyncio.run(load_test_circuit_breakers())
