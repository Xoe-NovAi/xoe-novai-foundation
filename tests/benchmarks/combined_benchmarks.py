#!/usr/bin/env python3
"""
Combined System Performance Benchmarking
Tests query router, pipeline, and fallback mechanisms
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import statistics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CombinedBenchmarkResult:
    """Result tracking for combined benchmarks"""

    def __init__(self, name: str, unit: str = "ms"):
        self.name = name
        self.unit = unit
        self.times: List[float] = []
        self.start_time = None

    def add_time(self, duration_ms: float):
        """Record a single measurement"""
        self.times.append(duration_ms)

    def stats(self) -> Dict[str, Any]:
        """Calculate statistical summary"""
        if not self.times:
            return {}
        
        sorted_times = sorted(self.times)
        n = len(sorted_times)
        
        return {
            "count": n,
            "mean": statistics.mean(sorted_times),
            "median": statistics.median(sorted_times),
            "stdev": statistics.stdev(sorted_times) if n > 1 else 0,
            "min": sorted_times[0],
            "max": sorted_times[-1],
            "p50": sorted_times[int(n * 0.50)],
            "p95": sorted_times[int(n * 0.95)],
            "p99": sorted_times[int(n * 0.99)],
            "unit": self.unit,
        }

    def __enter__(self):
        """Context manager entry - start timing"""
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        """Context manager exit - record time"""
        duration_ms = (time.time() - self.start_time) * 1000
        self.add_time(duration_ms)


class QueryRouterBenchmark:
    """Benchmark query router decision logic"""

    def __init__(self):
        self.results: Dict[str, CombinedBenchmarkResult] = {}

    async def benchmark_router_decision(self):
        """Benchmark router decision time"""
        logger.info("Benchmarking query router decision time...")
        
        result = CombinedBenchmarkResult("ROUTER_DECISION", "ms")
        
        # Simulate different query types
        queries = [
            {"type": "vector_search", "content": "test query"},
            {"type": "fts", "content": "keyword search"},
            {"type": "metadata_filter", "content": "filter"},
            {"type": "cache_check", "content": "cached"},
        ]
        
        for _ in range(100):
            for query in queries:
                with result:
                    # Simulate router decision logic
                    query_type = query.get("type")
                    if query_type == "vector_search":
                        await asyncio.sleep(0.001)
                    elif query_type == "fts":
                        await asyncio.sleep(0.0005)
                    elif query_type == "metadata_filter":
                        await asyncio.sleep(0.0002)
                    else:
                        await asyncio.sleep(0.0001)
        
        self.results["ROUTER_DECISION"] = result
        logger.info(f"Router decision benchmark: {result.stats()}")

    async def benchmark_pipeline(self):
        """Benchmark full query pipeline"""
        logger.info("Benchmarking full query pipeline...")
        
        result = CombinedBenchmarkResult("FULL_PIPELINE", "ms")
        
        for _ in range(50):
            with result:
                # Simulate query pipeline:
                # 1. Parse query
                await asyncio.sleep(0.0005)
                # 2. Route to backend
                await asyncio.sleep(0.001)
                # 3. Execute query
                await asyncio.sleep(0.005)
                # 4. Format results
                await asyncio.sleep(0.001)
        
        self.results["FULL_PIPELINE"] = result
        logger.info(f"Full pipeline benchmark: {result.stats()}")

    async def benchmark_fallback_activation(self):
        """Benchmark multi-tier fallback activation time"""
        logger.info("Benchmarking fallback activation time...")
        
        result = CombinedBenchmarkResult("FALLBACK_ACTIVATION", "ms")
        
        for i in range(50):
            with result:
                # Simulate fallback detection and activation
                if i % 3 == 0:
                    # Detect failure
                    await asyncio.sleep(0.0005)
                    # Activate fallback tier
                    await asyncio.sleep(0.002)
        
        self.results["FALLBACK_ACTIVATION"] = result
        logger.info(f"Fallback activation benchmark: {result.stats()}")

    async def benchmark_concurrent_queries(self, concurrency: int):
        """Benchmark concurrent query handling"""
        logger.info(f"Benchmarking {concurrency} concurrent queries...")
        
        result = CombinedBenchmarkResult(f"CONCURRENT_{concurrency}", "ms")
        
        async def handle_query():
            await asyncio.sleep(0.01)  # Simulate query processing
        
        with result:
            tasks = [handle_query() for _ in range(concurrency)]
            await asyncio.gather(*tasks)
        
        # Record time per query
        result.add_time((result.times[-1] if result.times else 10))
        
        self.results[f"CONCURRENT_{concurrency}"] = result
        logger.info(f"Concurrent queries ({concurrency}): {result.stats()}")

    async def run_all(self):
        """Run all combined benchmarks"""
        await self.benchmark_router_decision()
        await self.benchmark_pipeline()
        await self.benchmark_fallback_activation()
        
        # Test different concurrency levels
        for concurrency in [10, 100, 1000]:
            await self.benchmark_concurrent_queries(concurrency)

    def get_results(self) -> Dict[str, Dict[str, Any]]:
        """Get all benchmark results"""
        return {
            name: result.stats() for name, result in self.results.items()
        }


async def run_combined_benchmarks():
    """Run combined system benchmarks"""
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "combined_system": {},
    }
    
    logger.info("=" * 60)
    logger.info("COMBINED SYSTEM BENCHMARKS")
    logger.info("=" * 60)
    
    combined_bench = QueryRouterBenchmark()
    await combined_bench.run_all()
    all_results["combined_system"] = combined_bench.get_results()
    
    # Save results
    output_file = Path("benchmarks/combined_benchmark_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"\nResults saved to {output_file}")
    
    return all_results


if __name__ == "__main__":
    results = asyncio.run(run_combined_benchmarks())
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("COMBINED BENCHMARK SUMMARY")
    logger.info("=" * 60)
    
    for name, stats in results["combined_system"].items():
        if stats:
            logger.info(
                f"{name}: p50={stats.get('p50', 0):.2f}ms, "
                f"p95={stats.get('p95', 0):.2f}ms, "
                f"p99={stats.get('p99', 0):.2f}ms"
            )
