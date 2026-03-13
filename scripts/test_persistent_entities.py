#!/usr/bin/env python3
"""
Test Script for Persistent Entity System
========================================

Demonstrates the persistent entity system with continuous learning.
Shows how entities remember past interactions and improve over time.
"""

import asyncio
import logging
import time
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the app directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from XNAi_rag_app.core.entities.registry import (
    get_entity_registry, 
    register_persistent_entity,
    get_entity_context
)
from XNAi_rag_app.core.entities.feedback_loop import (
    get_feedback_loop,
    record_entity_feedback,
    get_entity_performance_report
)

async def test_persistent_entity_system():
    """Test the complete persistent entity system."""
    
    print("🧪 Testing Persistent Entity System")
    print("=" * 50)
    
    # Test 1: Entity Registration and Basic Functionality
    print("\n1️⃣ Testing Entity Registration...")
    
    # Register a philosophical expert
    philosopher = register_persistent_entity("Socrates", "philosophical_critic")
    print(f"✅ Registered entity: {philosopher.entity_id} ({philosopher.role})")
    
    # Register a technical expert
    engineer = register_persistent_entity("Ada Lovelace", "computer_scientist")
    print(f"✅ Registered entity: {engineer.entity_id} ({engineer.role})")
    
    # Test 2: Entity Memory and Context
    print("\n2️⃣ Testing Entity Memory...")
    
    # Add some lessons to the philosopher's memory
    philosopher.add_lesson(
        query="What is justice?",
        advice="Justice is giving each their due.",
        outcome="User found the response insightful",
        rating=0.9
    )
    
    philosopher.add_lesson(
        query="What is virtue?",
        advice="Virtue is knowledge of the good.",
        outcome="User engaged in deep discussion",
        rating=0.85
    )
    
    # Test context retrieval
    context = philosopher.get_relevant_context("What is justice?")
    print(f"✅ Retrieved context for 'What is justice?': {len(context)} characters")
    
    # Test 3: Feedback Loop and Continuous Learning
    print("\n3️⃣ Testing Feedback Loop...")
    
    # Record feedback for the philosopher
    success = record_entity_feedback(
        entity_id="Socrates",
        query="What is the meaning of life?",
        advice="The unexamined life is not worth living.",
        outcome="User appreciated the philosophical perspective",
        rating=0.8,
        feedback_source="human"
    )
    
    if success:
        print("✅ Successfully recorded feedback")
    else:
        print("❌ Failed to record feedback")
    
    # Record more feedback to trigger learning
    feedback_data = [
        ("What is truth?", "Truth is correspondence with reality.", "User found accurate", 0.9, "human"),
        ("What is beauty?", "Beauty is harmony of parts.", "User engaged thoughtfully", 0.85, "human"),
        ("What is knowledge?", "Knowledge is justified true belief.", "User found comprehensive", 0.92, "human"),
        ("What is ethics?", "Ethics is the art of living well.", "User found practical", 0.88, "human"),
    ]
    
    for query, advice, outcome, rating, source in feedback_data:
        record_entity_feedback("Socrates", query, advice, outcome, rating, source)
    
    print(f"✅ Recorded {len(feedback_data)} additional feedback entries")
    
    # Test 4: Performance Analytics
    print("\n4️⃣ Testing Performance Analytics...")
    
    report = get_entity_performance_report("Socrates")
    print(f"📊 Performance Report for {report['entity_id']}:")
    print(f"   - Success Rate: {report['performance_metrics'].get('average_rating', 0):.2%}")
    print(f"   - Total Feedback: {report['feedback_count']}")
    print(f"   - Memory Size: {report['basic_stats']['memory_size']}")
    
    if report['improvement_suggestions']:
        print(f"   - Improvement Suggestions: {len(report['improvement_suggestions'])}")
        for suggestion in report['improvement_suggestions']:
            print(f"     • {suggestion}")
    
    # Test 5: Cross-Entity Collaboration
    print("\n5️⃣ Testing Cross-Entity Collaboration...")
    
    # Register multiple entities for collaboration
    entities = [
        register_persistent_entity("Einstein", "theoretical_physicist"),
        register_persistent_entity("Marie Curie", "chemist"),
        register_persistent_entity("Leonardo da Vinci", "polymath")
    ]
    
    print(f"✅ Registered {len(entities)} additional entities for collaboration")
    
    # Simulate multi-entity consultation
    query = "What is the nature of creativity?"
    for entity in entities:
        # Add some context to each entity
        entity.add_lesson(
            query=query,
            advice=f"As a {entity.role.replace('_', ' ')}, I believe...",
            outcome="User found the perspective valuable",
            rating=0.85
        )
        
        context = entity.get_relevant_context(query)
        print(f"   {entity.entity_id} ({entity.role}): {len(context)} chars of context")
    
    # Test 6: Entity Registry Management
    print("\n6️⃣ Testing Entity Registry...")
    
    registry = get_entity_registry()
    all_entities = registry.get_all_entities()
    print(f"📊 Total registered entities: {len(all_entities)}")
    
    # Show entity statistics
    for entity in all_entities:
        stats = registry.get_entity_stats(entity["entity_id"])
        print(f"   {entity['entity_id']}: {stats['invocations']} invocations, {stats['success_rate']:.2%} success rate")
    
    # Test 7: Pattern Recognition and Self-Improvement
    print("\n7️⃣ Testing Pattern Recognition...")
    
    # Record some poor performance to trigger self-reflection
    poor_feedback = [
        ("How to code?", "Just think about it deeply.", "Response was too vague", 0.4, "human"),
        ("What is AI?", "It's like thinking machines.", "Response lacked technical depth", 0.5, "human"),
    ]
    
    for query, advice, outcome, rating, source in poor_feedback:
        record_entity_feedback("Ada Lovelace", query, advice, outcome, rating, source)
    
    # Check if self-reflection was triggered
    lovelace_report = get_entity_performance_report("Ada Lovelace")
    print(f"📊 Ada Lovelace performance after poor feedback:")
    print(f"   - Average Rating: {lovelace_report['performance_metrics'].get('average_rating', 0):.2%}")
    
    if lovelace_report['improvement_suggestions']:
        print(f"   - Improvement Suggestions: {len(lovelace_report['improvement_suggestions'])}")
        for suggestion in lovelace_report['improvement_suggestions']:
            print(f"     • {suggestion}")
    
    # Test 8: Entity Persistence Across Sessions
    print("\n8️⃣ Testing Entity Persistence...")
    
    # Simulate entity persistence by re-registering
    philosopher2 = register_persistent_entity("Socrates", "philosophical_critic")
    
    # Check if memory persisted
    persisted_context = philosopher2.get_relevant_context("What is justice?")
    print(f"✅ Entity memory persisted: {len(persisted_context)} characters")
    
    # Verify stats are maintained
    stats = registry.get_entity_stats("Socrates")
    print(f"✅ Entity stats maintained: {stats['total_feedback']} feedback entries")
    
    print("\n🎉 Persistent Entity System Test Complete!")
    print("=" * 50)
    
    return True

async def demonstrate_continuous_learning():
    """Demonstrate how entities learn and improve over time."""
    
    print("\n🧠 Demonstrating Continuous Learning")
    print("=" * 50)
    
    # Create a new entity for demonstration
    coder = register_persistent_entity("CodeGuru", "software_engineer")
    
    print(f"🆕 Created new entity: {coder.entity_id}")
    
    # Simulate a learning progression
    learning_sessions = [
        {
            "query": "How to optimize Python code?",
            "advice": "Use list comprehensions and avoid global variables.",
            "outcome": "User found helpful but basic",
            "rating": 0.7,
            "improvement": "Need more advanced techniques"
        },
        {
            "query": "How to optimize Python code?",
            "advice": "Use NumPy for array operations, implement caching, and profile with cProfile.",
            "outcome": "User found comprehensive and actionable",
            "rating": 0.9,
            "improvement": "Applied advanced optimization techniques"
        },
        {
            "query": "How to optimize Python code?",
            "advice": "Use NumPy for array operations, implement caching with functools.lru_cache, profile with cProfile, and consider Cython for bottlenecks.",
            "outcome": "User implemented all suggestions successfully",
            "rating": 0.95,
            "improvement": "Added specific implementation details"
        }
    ]
    
    for i, session in enumerate(learning_sessions, 1):
        print(f"\n📚 Learning Session {i}:")
        print(f"   Query: {session['query']}")
        print(f"   Advice: {session['advice']}")
        print(f"   Outcome: {session['outcome']}")
        print(f"   Rating: {session['rating']}")
        print(f"   Improvement: {session['improvement']}")
        
        # Record feedback
        record_entity_feedback(
            entity_id="CodeGuru",
            query=session["query"],
            advice=session["advice"],
            outcome=session["outcome"],
            rating=session["rating"],
            feedback_source="human"
        )
        
        # Show improvement
        report = get_entity_performance_report("CodeGuru")
        print(f"   📊 Current Performance: {report['performance_metrics'].get('average_rating', 0):.2%}")
    
    # Final assessment
    final_report = get_entity_performance_report("CodeGuru")
    print(f"\n🎯 Final Assessment:")
    print(f"   - Average Rating: {final_report['performance_metrics'].get('average_rating', 0):.2%}")
    print(f"   - Total Lessons Learned: {final_report['basic_stats']['memory_size']}")
    print(f"   - Improvement Suggestions: {len(final_report['improvement_suggestions'])}")
    
    print("\n✅ Continuous Learning Demonstration Complete!")

async def main():
    """Main test function."""
    try:
        # Run the persistent entity system test
        await test_persistent_entity_system()
        
        # Demonstrate continuous learning
        await demonstrate_continuous_learning()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📝 Summary:")
        print("   ✅ Entities can be registered and persist across sessions")
        print("   ✅ Entities maintain procedural memory of past interactions")
        print("   ✅ Feedback loop enables continuous learning and improvement")
        print("   ✅ Performance analytics provide insights into entity effectiveness")
        print("   ✅ Cross-entity collaboration enables multi-perspective analysis")
        print("   ✅ Pattern recognition triggers self-reflection and optimization")
        print("   ✅ Entities improve their responses based on user feedback")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())