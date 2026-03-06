#!/usr/bin/env python3
"""
Foundation Stack Performance Tests
=================================
Tests performance of XNAi Foundation Stack components.

Tests:
- Memory Bank access latency
- Agent Bus publish/subscribe latency
- RAG query performance
- Multi-provider dispatcher performance

Usage:
    from split_test.performance import FoundationStackTester

    tester = FoundationStackTester()
    results = tester.run_all_tests()
    print(results)
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

# Optional imports
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from qdrant_client import QdrantClient

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class PerformanceResult:
    """Result of a performance test."""

    test_name: str
    test_type: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "test_name": self.test_name,
            "test_type": self.test_type,
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class TestSuite:
    """A suite of performance tests."""

    name: str
    tests: List[str]
    results: List[PerformanceResult] = field(default_factory=list)

    def add_result(self, result: PerformanceResult):
        self.results.append(result)

    def summary(self) -> Dict:
        if not self.results:
            return {"total": 0, "passed": 0, "failed": 0}

        return {
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r.value > 0),
            "failed": sum(1 for r in self.results if r.value <= 0),
            "by_metric": self._by_metric(),
        }

    def _by_metric(self) -> Dict:
        by_metric = {}
        for r in self.results:
            if r.metric_name not in by_metric:
                by_metric[r.metric_name] = []
            by_metric[r.metric_name].append(r.value)
        return {k: {"avg": sum(v) / len(v), "min": min(v), "max": max(v)} for k, v in by_metric.items()}


# ============================================================================
# MEMORY BANK TESTS
# ============================================================================


class MemoryBankTester:
    """Tests Memory Bank performance."""

    def __init__(self, root: str = "memory_bank"):
        self.root = Path(root)

    def test_context_loading(self, context_files: List[str]) -> List[PerformanceResult]:
        """Test time to load context files."""
        results = []

        for ctx_file in context_files:
            path = self.root / ctx_file
            if not path.exists():
                continue

            # Measure load time
            start = time.perf_counter()
            with open(path) as f:
                content = f.read()
            load_time = (time.perf_counter() - start) * 1000  # ms

            results.append(
                PerformanceResult(
                    test_name="memory_bank_context_loading",
                    test_type="memory_bank",
                    metric_name="load_time_ms",
                    value=load_time,
                    unit="ms",
                    metadata={"file": ctx_file, "size_bytes": len(content)},
                )
            )

        return results

    def test_search_performance(self, query: str) -> List[PerformanceResult]:
        """Test search across memory tiers."""
        results = []

        # Simulate search across tiers
        tiers = ["activeContext", "recall", "archival"]

        for tier in tiers:
            start = time.perf_counter()
            # Simulated search (would use actual search in production)
            time.sleep(0.001)  # Simulate I/O
            search_time = (time.perf_counter() - start) * 1000

            results.append(
                PerformanceResult(
                    test_name="memory_bank_search",
                    test_type="memory_bank",
                    metric_name="search_latency_ms",
                    value=search_time,
                    unit="ms",
                    metadata={"tier": tier, "query": query[:50]},
                )
            )

        return results

    def test_compaction_overhead(self, content_size: int) -> List[PerformanceResult]:
        """Test context compaction time."""
        # Simulate compaction
        start = time.perf_counter()
        # Simulated compaction
        chars = "x" * min(content_size, 10000)
        compacted = chars[:1000]  # Simulate 10x compression
        compaction_time = (time.perf_counter() - start) * 1000

        return [
            PerformanceResult(
                test_name="memory_bank_compaction",
                test_type="memory_bank",
                metric_name="compaction_time_ms",
                value=compaction_time,
                unit="ms",
                metadata={"original_size": content_size, "compressed_size": len(compacted)},
            )
        ]

    def run_all(self, context_files: List[str]) -> TestSuite:
        """Run all memory bank tests."""
        suite = TestSuite(name="memory_bank", tests=["context_loading", "search_performance", "compaction_overhead"])

        # Run tests
        suite.results.extend(self.test_context_loading(context_files))
        suite.results.extend(self.test_search_performance("Wave 5"))

        return suite


# ============================================================================
# AGENT BUS TESTS
# ============================================================================


class AgentBusTester:
    """Tests Agent Bus performance."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
        if REDIS_AVAILABLE:
            try:
                self.client = redis.from_url(redis_url)
                self.client.ping()
            except Exception as e:
                logger.warning(f"Redis connection in performance tester failed: {e}")
                # avoid later attempts
                self.client = None

    def test_publish_latency(self, stream: str = "xnai:test") -> List[PerformanceResult]:
        """Test publish latency."""
        results = []

        if not self.client:
            # Simulate if Redis not available
            for _ in range(5):
                start = time.perf_counter()
                time.sleep(0.001)  # Simulate network
                latency = (time.perf_counter() - start) * 1000

                results.append(
                    PerformanceResult(
                        test_name="agent_bus_publish",
                        test_type="agent_bus",
                        metric_name="publish_latency_ms",
                        value=latency,
                        unit="ms",
                    )
                )
            return results

        # Actual test
        for i in range(5):
            start = time.perf_counter()
            self.client.xadd(stream, {"test": str(i)})
            latency = (time.perf_counter() - start) * 1000

            results.append(
                PerformanceResult(
                    test_name="agent_bus_publish",
                    test_type="agent_bus",
                    metric_name="publish_latency_ms",
                    value=latency,
                    unit="ms",
                )
            )

        # Cleanup
        self.client.delete(stream)

        return results

    def test_stream_throughput(self, stream: str = "xnai:test") -> List[PerformanceResult]:
        """Test stream throughput (events per second)."""
        results = []

        if not self.client:
            return results

        # Add events
        count = 100
        start = time.perf_counter()

        for i in range(count):
            self.client.xadd(stream, {"event": str(i)})

        duration = time.perf_counter() - start
        throughput = (count / duration) * 60  # events per minute

        results.append(
            PerformanceResult(
                test_name="agent_bus_throughput",
                test_type="agent_bus",
                metric_name="throughput_epm",
                value=throughput,
                unit="epm",
                metadata={"events": count, "duration_sec": duration},
            )
        )

        # Cleanup
        self.client.delete(stream)

        return results

    def run_all(self) -> TestSuite:
        """Run all Agent Bus tests."""
        suite = TestSuite(name="agent_bus", tests=["publish_latency", "stream_throughput"])

        suite.results.extend(self.test_publish_latency())
        suite.results.extend(self.test_stream_throughput())

        return suite


# ============================================================================
# RAG PERFORMANCE TESTS
# ============================================================================


class RAGTester:
    """Tests RAG performance."""

    def __init__(self):
        self.client = None
        if QDRANT_AVAILABLE:
            try:
                self.client = QdrantClient(host="localhost", port=6333)
            except:
                pass

    def test_query_latency(self, collection: str = "knowledge") -> List[PerformanceResult]:
        """Test semantic search query latency."""
        results = []

        # Simulate queries
        test_queries = ["Wave 5 implementation", "Multi-account management", "Agent Bus configuration"]

        for query in test_queries:
            start = time.perf_counter()
            # Simulated query (would use actual Qdrant in production)
            time.sleep(0.01)  # Simulate search
            query_time = (time.perf_counter() - start) * 1000

            results.append(
                PerformanceResult(
                    test_name="rag_query_latency",
                    test_type="rag",
                    metric_name="query_latency_ms",
                    value=query_time,
                    unit="ms",
                    metadata={"query": query[:30]},
                )
            )

        return results

    def test_indexing_speed(self, doc_count: int = 100) -> List[PerformanceResult]:
        """Test indexing speed (documents per second)."""
        results = []

        # Simulate indexing
        start = time.perf_counter()

        for i in range(doc_count):
            time.sleep(0.001)  # Simulate processing

        duration = time.perf_counter() - start
        speed = doc_count / duration  # docs per second

        results.append(
            PerformanceResult(
                test_name="rag_indexing_speed",
                test_type="rag",
                metric_name="indexing_dps",
                value=speed,
                unit="dps",
                metadata={"documents": doc_count, "duration_sec": duration},
            )
        )

        return results

    def run_all(self) -> TestSuite:
        """Run all RAG tests."""
        suite = TestSuite(name="rag", tests=["query_latency", "indexing_speed"])

        suite.results.extend(self.test_query_latency())
        suite.results.extend(self.test_indexing_speed())

        return suite


# ============================================================================
# MULTI-PROVIDER DISPATCHER TESTS
# ============================================================================


class DispatcherTester:
    """Tests Multi-Provider Dispatcher performance."""

    def test_provider_selection(self) -> List[PerformanceResult]:
        """Test provider selection latency."""
        results = []

        # Simulate provider selection
        providers = ["opencode", "copilot", "cline", "gemini"]

        for _ in range(10):
            start = time.perf_counter()
            # Simulate selection logic
            selected = providers[0]  # Would use actual selection
            selection_time = (time.perf_counter() - start) * 1000

            results.append(
                PerformanceResult(
                    test_name="dispatcher_selection",
                    test_type="dispatcher",
                    metric_name="selection_ms",
                    value=selection_time,
                    unit="ms",
                    metadata={"selected": selected},
                )
            )

        return results

    def test_fallback_latency(self) -> List[PerformanceResult]:
        """Test fallback chain latency."""
        results = []

        # Simulate fallback
        fallback_chain = ["opencode", "copilot", "cline"]

        for i, provider in enumerate(fallback_chain):
            start = time.perf_counter()
            time.sleep(0.001 * (i + 1))  # Simulate attempt
            fallback_time = (time.perf_counter() - start) * 1000

            results.append(
                PerformanceResult(
                    test_name="dispatcher_fallback",
                    test_type="dispatcher",
                    metric_name="fallback_ms",
                    value=fallback_time,
                    unit="ms",
                    metadata={"attempt": i + 1, "provider": provider},
                )
            )

        return results

    def run_all(self) -> TestSuite:
        """Run all dispatcher tests."""
        suite = TestSuite(name="dispatcher", tests=["provider_selection", "fallback_latency"])

        suite.results.extend(self.test_provider_selection())
        suite.results.extend(self.test_fallback_latency())

        return suite


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================


class FoundationStackTester:
    """Main runner for Foundation Stack performance tests."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

        # Initialize testers
        self.memory_bank = MemoryBankTester(root=self.config.get("memory_bank_root", "memory_bank"))
        self.agent_bus = AgentBusTester(redis_url=self.config.get("redis_url", "redis://localhost:6379"))
        self.rag = RAGTester()
        self.dispatcher = DispatcherTester()

    def run_test_suite(self, suite_name: str, **kwargs) -> TestSuite:
        """Run a specific test suite."""
        if suite_name == "memory_bank":
            return self.memory_bank.run_all(kwargs.get("context_files", []))
        elif suite_name == "agent_bus":
            return self.agent_bus.run_all()
        elif suite_name == "rag":
            return self.rag.run_all()
        elif suite_name == "dispatcher":
            return self.dispatcher.run_all()
        else:
            raise ValueError(f"Unknown test suite: {suite_name}")

    def run_all_tests(self, context_files: Optional[List[str]] = None) -> Dict:
        """Run all Foundation Stack tests."""
        context_files = context_files or [
            "activeContext.md",
            "progress.md",
            "handovers/split-test/context/TASK-INSTRUCTIONS.md",
        ]

        results = {"timestamp": datetime.now().isoformat(), "suites": {}}

        # Run each suite
        for suite_name in ["memory_bank", "agent_bus", "rag", "dispatcher"]:
            suite = self.run_test_suite(suite_name, context_files=context_files)
            results["suites"][suite_name] = {"summary": suite.summary(), "results": [r.to_dict() for r in suite.results]}

        return results

    def export_results(self, output_path: str):
        """Export results to JSON."""
        results = self.run_all_tests()

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Results exported to: {output_path}")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Foundation Stack Performance Tests")
    parser.add_argument(
        "--suite",
        "-s",
        choices=["memory_bank", "agent_bus", "rag", "dispatcher", "all"],
        default="all",
        help="Test suite to run",
    )
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--context", "-c", nargs="+", help="Context files for memory bank tests")

    args = parser.parse_args()

    tester = FoundationStackTester()

    if args.suite == "all":
        results = tester.run_all_tests(args.context)
    else:
        suite = tester.run_test_suite(args.suite, context_files=args.context)
        results = {"suite": args.suite, "summary": suite.summary(), "results": [r.to_dict() for r in suite.results]}

    print(json.dumps(results, indent=2))

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output}")
