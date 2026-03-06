#!/usr/bin/env python3
"""
Test script for holographic memory system
=========================================

Validates the core functionality of the holographic memory implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from holographic_memory import HolographicMemory
from domains import classify_content_domain


async def test_basic_functionality():
    """Test basic holographic memory operations."""
    print("🧪 Testing Holographic Memory Basic Functionality")
    print("=" * 50)

    # Initialize memory system
    memory = HolographicMemory()
    print("✅ Holographic memory initialized")

    # Test content storage
    test_content = {
        "title": "API Design Patterns",
        "description": "Best practices for REST API design including versioning, authentication, and error handling",
        "tags": ["api", "rest", "design", "backend"],
        "importance": "high"
    }

    fragment_id = await memory.store_fragment(test_content, "technical_architecture")
    print(f"✅ Content stored with fragment ID: {fragment_id}")

    # Test recall
    query = "API design patterns"
    results = await memory.holographic_recall(query, top_k=3)
    print(f"✅ Recall operation completed, found {len(results)} results")

    if results:
        print(f"   - Best match domain: {results[0]['primary_domain']}")
        print(f"   - Activation level: {results[0]['activation']:.2f}")
        print(f"   - Access count: {results[0]['access_count']}")

    # Test associative connections
    if results:
        connections = await memory.find_associative_connections(fragment_id, max_connections=2)
        print(f"✅ Found {len(connections)} associative connections")

    # Test statistics
    stats = memory.get_statistics()
    print(f"✅ Memory statistics: {stats['total_fragments']} fragments stored")
    print(f"   - Recall operations: {stats['recall_operations']}")
    print(f"   - Average similarity: {stats['average_similarity']:.2f}")

    return True


async def test_domain_classification():
    """Test content domain classification."""
    print("\n🧪 Testing Domain Classification")
    print("=" * 50)

    test_cases = [
        ("How to implement user authentication in a web API", "security_practices"),
        ("Database optimization techniques for large datasets", "performance_optimizations"),
        ("Writing comprehensive unit tests for Python functions", "testing_strategies"),
        ("Creating user-friendly API documentation", "documentation_patterns"),
        ("Deploying containerized applications to production", "deployment_processes")
    ]

    correct = 0
    total = len(test_cases)

    for content, expected_domain in test_cases:
        predicted_domain = classify_content_domain(content)
        status = "✅" if predicted_domain == expected_domain else "❌"
        print(f"{status} '{content[:50]}...' → {predicted_domain} (expected: {expected_domain})")

        if predicted_domain == expected_domain:
            correct += 1

    accuracy = correct / total * 100
    print(f"Classification accuracy: {accuracy:.1f}%")
    return accuracy >= 80  # Accept 80% accuracy for basic classification


async def test_temporal_decay():
    """Test temporal decay functionality."""
    print("\n🧪 Testing Temporal Decay")
    print("=" * 50)

    memory = HolographicMemory(decay_rate=0.9)  # Aggressive decay for testing

    # Store multiple fragments
    fragments = []
    for i in range(3):
        content = {
            "title": f"Test Pattern {i}",
            "description": f"Testing temporal decay with pattern {i}",
            "category": "testing"
        }
        fragment_id = await memory.store_fragment(content, "testing_strategies")
        fragments.append(fragment_id)

    # Check initial activation
    stats_before = memory.get_statistics()
    print(f"✅ Initial fragments stored: {stats_before['total_fragments']}")

    # Manually trigger decay (normally happens hourly)
    await memory._apply_temporal_decay()
    print("✅ Temporal decay applied")

    # Check activation after decay
    stats_after = memory.get_statistics()
    print(f"✅ Fragments after decay: {stats_after['total_fragments']}")

    # Verify decay occurred
    return stats_after['temporal_decay_applied'] > 0


async def test_associative_recall():
    """Test associative memory connections."""
    print("\n🧪 Testing Associative Recall")
    print("=" * 50)

    memory = HolographicMemory()

    # Store related content
    related_content = [
        {
            "title": "REST API Authentication",
            "description": "Implementing JWT tokens for API security",
            "tags": ["api", "security", "jwt"]
        },
        {
            "title": "API Rate Limiting",
            "description": "Implementing rate limiting for API endpoints",
            "tags": ["api", "security", "rate-limiting"]
        },
        {
            "title": "OAuth2 Implementation",
            "description": "Setting up OAuth2 authentication flow",
            "tags": ["api", "security", "oauth"]
        }
    ]

    fragment_ids = []
    for content in related_content:
        fragment_id = await memory.store_fragment(content, "security_practices")
        fragment_ids.append(fragment_id)

    # Test associative connections from first fragment
    connections = await memory.find_associative_connections(fragment_ids[0], max_connections=5)
    print(f"✅ Found {len(connections)} associative connections")

    if connections:
        print(f"   - Strongest connection strength: {connections[0]['connection_strength']:.2f}")
        if connections[0]['shared_domains']:
            print(f"   - Shared domains: {connections[0]['shared_domains']}")

    return len(connections) > 0


async def run_all_tests():
    """Run all holographic memory tests."""
    print("🚀 Starting Holographic Memory System Tests")
    print("=" * 60)

    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Domain Classification", test_domain_classification),
        ("Temporal Decay", test_temporal_decay),
        ("Associative Recall", test_associative_recall)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Running: {test_name}")
            result = await test_func()
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"📊 Result: {status}")
            results.append(result)
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("📈 TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)
    success_rate = passed / total * 100

    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 OVERALL: SUCCESS - Holographic Memory System Ready!")
        return True
    else:
        print("⚠️  OVERALL: ISSUES DETECTED - Review test failures")
        return False


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())

    # Exit with appropriate code
    sys.exit(0 if success else 1)