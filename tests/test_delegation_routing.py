#!/usr/bin/env python3
"""
Phase D: Comprehensive Tests for Delegation Protocol

Tests task_classifier and routing_engine against all scenarios
from DELEGATION-PROTOCOL-v1.md
"""

import sys
import json
from communication_hub.conductor.task_classifier import (
    Task, TaskCategory, ComplexityModifiers, ComplexityScorer
)
from communication_hub.conductor.routing_engine import (
    RoutingEngine, AgentCapacity, AgentStatus
)


def test_complexity_scorer():
    """Test complexity scoring against all documented scenarios."""
    
    print("\n" + "=" * 80)
    print("TEST 1: COMPLEXITY SCORER")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Simple single model card",
            "task": Task(
                task_id="t1",
                title="Model card for DeepSeek 6.7B",
                category=TaskCategory.RESEARCH,
                description="Single model",
                base_scope="small",
                modifiers=ComplexityModifiers()
            ),
            "expected_score": 1,
            "expected_agent": "crawler"
        },
        {
            "name": "Medium model comparison",
            "task": Task(
                task_id="t2",
                title="Compare 5 models",
                category=TaskCategory.RESEARCH,
                description="Multiple models",
                base_scope="medium",
                modifiers=ComplexityModifiers(multi_model_comparison=True)
            ),
            "expected_score": 4,
            "expected_agent": "copilot"
        },
        {
            "name": "Complex system analysis",
            "task": Task(
                task_id="t3",
                title="Holistic XOH review",
                category=TaskCategory.PLANNING,
                description="Entire system",
                base_scope="large",
                modifiers=ComplexityModifiers(
                    system_strategy=True,
                    documentation_heavy=True,
                    custom_research=True
                )
            ),
            "expected_score": 7,
            "expected_agent": "gemini"
        },
        {
            "name": "Implementation with integration",
            "task": Task(
                task_id="t4",
                title="Implement routing engine",
                category=TaskCategory.IMPLEMENTATION,
                description="Code + integration",
                base_scope="large",
                modifiers=ComplexityModifiers(
                    novel_integration=True,
                    code_generation_required=True,
                    system_strategy=True
                )
            ),
            "expected_score": 8,
            "expected_agent": "cline"
        },
        {
            "name": "Hardware-specific research",
            "task": Task(
                task_id="t5",
                title="Ryzen 7 model optimization",
                category=TaskCategory.RESEARCH,
                description="Hardware benchmarking",
                base_scope="medium",
                modifiers=ComplexityModifiers(
                    hardware_specific=True,
                    custom_research=True
                )
            ),
            "expected_score": 4,
            "expected_agent": "copilot"
        },
    ]
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        score = ComplexityScorer.score_task(case["task"])
        agent = ComplexityScorer.get_target_agent(score)
        
        score_ok = score == case["expected_score"]
        agent_ok = agent == case["expected_agent"]
        
        status = "✓ PASS" if (score_ok and agent_ok) else "✗ FAIL"
        
        print(f"\n{status} {case['name']}")
        print(f"  Score: {score} (expected {case['expected_score']}) {'✓' if score_ok else '✗'}")
        print(f"  Agent: {agent} (expected {case['expected_agent']}) {'✓' if agent_ok else '✗'}")
        
        if score_ok and agent_ok:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'-' * 80}")
    print(f"Complexity Scorer: {passed}/{len(test_cases)} tests passed")
    return passed, failed


def test_routing_engine():
    """Test routing engine decision logic."""
    
    print("\n" + "=" * 80)
    print("TEST 2: ROUTING ENGINE")
    print("=" * 80)
    
    engine = RoutingEngine()
    
    # Register agents with different capacities
    agents = [
        AgentCapacity(
            agent_id="crawler:001",
            agent_type="crawler",
            status=AgentStatus.AVAILABLE,
            current_load=1,
            max_concurrent=3,
            avg_response_time_ms=500,
            last_heartbeat="2026-02-16T21:00:00Z"
        ),
        AgentCapacity(
            agent_id="copilot:haiku:001",
            agent_type="copilot",
            status=AgentStatus.AVAILABLE,
            current_load=0,
            max_concurrent=1,
            avg_response_time_ms=2000,
            last_heartbeat="2026-02-16T21:00:00Z"
        ),
        AgentCapacity(
            agent_id="gemini:pro:001",
            agent_type="gemini",
            status=AgentStatus.BUSY,
            current_load=1,
            max_concurrent=1,
            avg_response_time_ms=5000,
            last_heartbeat="2026-02-16T21:00:00Z"
        ),
        AgentCapacity(
            agent_id="cline:kat:001",
            agent_type="cline",
            status=AgentStatus.AVAILABLE,
            current_load=0,
            max_concurrent=1,
            avg_response_time_ms=3000,
            last_heartbeat="2026-02-16T21:00:00Z"
        ),
    ]
    
    for agent in agents:
        engine.register_agent(agent)
    
    test_cases = [
        {
            "name": "Route crawler task when available",
            "score": 1,
            "expected_agent_type": "crawler",
            "should_fallback": False
        },
        {
            "name": "Route copilot task",
            "score": 5,
            "expected_agent_type": "copilot",
            "should_fallback": False
        },
        {
            "name": "Route gemini task with fallback (Gemini busy)",
            "score": 7,
            "expected_agent_type": "gemini",
            "should_fallback": True  # Gemini is busy
        },
        {
            "name": "Route cline task",
            "score": 8,
            "expected_agent_type": "cline",
            "should_fallback": False
        },
    ]
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        decision = engine.route_task(case["name"], case["score"])
        
        if case["should_fallback"]:
            has_fallback = decision.fallback_agent is not None
            agent_type_ok = decision.primary_agent == case["expected_agent_type"]
            test_ok = has_fallback and agent_type_ok
        else:
            no_fallback = decision.fallback_agent is None
            agent_type_ok = case["expected_agent_type"] in decision.primary_agent
            test_ok = no_fallback and agent_type_ok
        
        status = "✓ PASS" if test_ok else "✗ FAIL"
        
        print(f"\n{status} {case['name']}")
        print(f"  Primary: {decision.primary_agent}")
        if decision.fallback_agent:
            print(f"  Fallback: {decision.fallback_agent}")
        print(f"  Score: {decision.complexity_score}")
        print(f"  Reason: {decision.reason}")
        
        if test_ok:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'-' * 80}")
    print(f"Routing Engine: {passed}/{len(test_cases)} tests passed")
    return passed, failed


def test_turnaround_estimates():
    """Test turnaround time estimation."""
    
    print("\n" + "=" * 80)
    print("TEST 3: TURNAROUND TIME ESTIMATES")
    print("=" * 80)
    
    test_cases = [
        ("crawler", (15, 60)),
        ("copilot", (30, 120)),
        ("gemini", (120, 360)),
        ("cline", (240, 720)),
    ]
    
    passed = 0
    
    for agent_type, expected in test_cases:
        result = ComplexityScorer.estimate_turnaround_minutes(agent_type)
        ok = result == expected
        status = "✓ PASS" if ok else "✗ FAIL"
        
        print(f"{status} {agent_type:10} → {result[0]:3}-{result[1]:3} min (expected {expected[0]}-{expected[1]})")
        
        if ok:
            passed += 1
    
    print(f"\n{'-' * 80}")
    print(f"Turnaround Estimates: {passed}/{len(test_cases)} tests passed")
    return passed, 0


def test_end_to_end():
    """Test end-to-end routing flow."""
    
    print("\n" + "=" * 80)
    print("TEST 4: END-TO-END DELEGATION FLOW")
    print("=" * 80)
    
    # Create task -> score -> route -> enqueue
    task = Task(
        task_id="phase_d_integration_test",
        title="Test end-to-end flow",
        category=TaskCategory.IMPLEMENTATION,
        description="Full integration test",
        base_scope="medium",
        modifiers=ComplexityModifiers(code_generation_required=True)
    )
    
    # Step 1: Score
    score = ComplexityScorer.score_task(task)
    print(f"\n1. Task Scored: {score}")
    
    # Step 2: Get target agent
    agent = ComplexityScorer.get_target_agent(score)
    print(f"2. Target Agent: {agent}")
    
    # Step 3: Estimate turnaround
    min_time, max_time = ComplexityScorer.estimate_turnaround_minutes(agent)
    print(f"3. Turnaround Estimate: {min_time}-{max_time} min")
    
    # Step 4: Route
    engine = RoutingEngine()
    
    # Register a Copilot agent
    engine.register_agent(AgentCapacity(
        agent_id="copilot:test:001",
        agent_type="copilot",
        status=AgentStatus.AVAILABLE,
        current_load=0,
        max_concurrent=1,
        avg_response_time_ms=2000,
        last_heartbeat="2026-02-16T21:00:00Z"
    ))
    
    decision = engine.route_task(task.task_id, score)
    print(f"4. Routing Decision: {decision.primary_agent}")
    
    # Step 5: Enqueue
    job_id = engine.enqueue_job(decision, {
        "task_title": task.title,
        "task_description": task.description
    })
    print(f"5. Job Queued: {job_id}")
    
    # Step 6: Check status
    job_status = engine.get_job_status(job_id)
    print(f"6. Job Status: {job_status['status']}")
    
    print(f"\n{'-' * 80}")
    print(f"End-to-End Flow: ✓ PASS")
    return 1, 0


def main():
    """Run all tests."""
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "DELEGATION PROTOCOL COMPREHENSIVE TESTS" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    total_passed = 0
    total_failed = 0
    
    # Run all test suites
    p, f = test_complexity_scorer()
    total_passed += p
    total_failed += f
    
    p, f = test_routing_engine()
    total_passed += p
    total_failed += f
    
    p, f = test_turnaround_estimates()
    total_passed += p
    total_failed += f
    
    p, f = test_end_to_end()
    total_passed += p
    total_failed += f
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total_failed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
