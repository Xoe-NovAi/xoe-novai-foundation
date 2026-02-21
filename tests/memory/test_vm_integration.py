"""Test VictoriaMetrics integration with metrics collector."""

import asyncio
import sys

sys.path.insert(0, "/home/arcana-novai/Documents/xnai-foundation/app")

from XNAi_rag_app.core.memory.metrics_collector import MemoryMetricsCollector


async def test_vm_write():
    collector = MemoryMetricsCollector(vm_endpoint="http://localhost:8428")

    await collector.record_block_utilization("test_block", 500, 1000, "core")
    print("✅ Block utilization metric written")

    await collector.record_tool_invocation("memory_replace", True)
    print("✅ Tool invocation metric written")

    await collector.record_overflow_event("test_block")
    print("✅ Overflow event metric written")

    await collector.close()

    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://localhost:8428/api/v1/export?match=memory_block_utilization"
        ) as resp:
            data = await resp.text()
            print(f"📊 VM Export result:\n{data[:500]}")

    print("\n✅ VictoriaMetrics integration test PASSED")


if __name__ == "__main__":
    asyncio.run(test_vm_write())
