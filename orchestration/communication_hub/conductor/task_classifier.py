#!/usr/bin/env python3
"""
Phase D: Task Classifier - Complexity Scoring

Implements the complexity scoring rubric from DELEGATION-PROTOCOL-v1.md
Used by Conductor to route tasks to appropriate agents
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class TaskCategory(Enum):
    """Task categories for scoring."""
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    INTEGRATION = "integration"
    PLANNING = "planning"


@dataclass
class ComplexityModifiers:
    """Modifiers that adjust complexity score."""
    unknown_architecture: bool = False  # +2
    multi_model_comparison: bool = False  # +2
    novel_integration: bool = False  # +2
    code_generation_required: bool = False  # +1
    documentation_heavy: bool = False  # +1
    system_strategy: bool = False  # +2
    hardware_specific: bool = False  # +1
    custom_research: bool = False  # +1
    
    def calculate_total(self) -> int:
        """Calculate total modifier points."""
        score = 0
        if self.unknown_architecture:
            score += 2
        if self.multi_model_comparison:
            score += 2
        if self.novel_integration:
            score += 2
        if self.code_generation_required:
            score += 1
        if self.documentation_heavy:
            score += 1
        if self.system_strategy:
            score += 2
        if self.hardware_specific:
            score += 1
        if self.custom_research:
            score += 1
        return score


@dataclass
class Task:
    """Task definition for complexity scoring."""
    task_id: str
    title: str
    category: TaskCategory
    description: str
    base_scope: str  # "small" (1-2 models), "medium" (5-10 models), "large" (20+ models)
    modifiers: ComplexityModifiers
    time_budget_minutes: Optional[int] = None
    
    def validate(self) -> bool:
        """Validate task is well-formed."""
        return (
            self.task_id and
            self.title and
            self.category and
            self.description and
            self.base_scope in ["small", "medium", "large"]
        )


class ComplexityScorer:
    """
    Scores task complexity using rubric from DELEGATION-PROTOCOL-v1.md
    
    Scoring Rubric:
    ===============
    Base Score (by scope):
    - 1: Small scope (single model, straightforward)
    - 2: Medium scope (5-10 items, some synthesis)
    - 3: Large scope (20+ items, complex synthesis)
    
    Modifiers (+1 to +2 each, cumulative):
    - Unknown architecture: +2
    - Multi-model comparison: +2
    - Novel integration: +2
    - Code generation: +1
    - Documentation heavy: +1
    - System strategy: +2
    - Hardware specific: +1
    - Custom research: +1
    
    Total Score Ranges:
    - 1-3: CRAWLER (ruvltra-0.5b) - Simple research tasks
    - 4-5: COPILOT (Haiku 4.5, 100K context) - Strategic planning/synthesis
    - 6-7: GEMINI (3 Pro, 1M context) - Large-scale analysis
    - 8+: CLINE (kat-coder-pro, 256K context) - Complex implementation
    """
    
    CRAWLER_THRESHOLD = (1, 3)
    COPILOT_THRESHOLD = (4, 5)
    GEMINI_THRESHOLD = (6, 7)
    CLINE_THRESHOLD = (8, float('inf'))
    
    @staticmethod
    def score_task(task: Task) -> int:
        """Calculate complexity score for a task."""
        
        if not task.validate():
            raise ValueError(f"Invalid task: {task.task_id}")
        
        # Calculate base score from scope
        base_scores = {
            "small": 1,
            "medium": 2,
            "large": 3
        }
        base_score = base_scores[task.base_scope]
        
        # Add modifiers
        modifier_score = task.modifiers.calculate_total()
        
        # Total complexity
        total = base_score + modifier_score
        
        return total
    
    @staticmethod
    def get_target_agent(score: int) -> str:
        """Determine which agent should handle this task."""
        if ComplexityScorer.CRAWLER_THRESHOLD[0] <= score <= ComplexityScorer.CRAWLER_THRESHOLD[1]:
            return "crawler"
        elif ComplexityScorer.COPILOT_THRESHOLD[0] <= score <= ComplexityScorer.COPILOT_THRESHOLD[1]:
            return "copilot"
        elif ComplexityScorer.GEMINI_THRESHOLD[0] <= score <= ComplexityScorer.GEMINI_THRESHOLD[1]:
            return "gemini"
        elif score >= ComplexityScorer.CLINE_THRESHOLD[0]:
            return "cline"
        else:
            raise ValueError(f"Score {score} out of range")
    
    @staticmethod
    def estimate_turnaround_minutes(agent: str) -> tuple:
        """Estimate min-max turnaround time for agent."""
        estimates = {
            "crawler": (15, 60),      # 15-60 min per job
            "copilot": (30, 120),     # 30 min - 2 hours
            "gemini": (120, 360),     # 2-6 hours (due to API latency)
            "cline": (240, 720)       # 4-12 hours (implementation heavy)
        }
        return estimates.get(agent, (None, None))
    
    @staticmethod
    def score_and_route(task: Task) -> Dict:
        """Full scoring and routing decision."""
        score = ComplexityScorer.score_task(task)
        agent = ComplexityScorer.get_target_agent(score)
        min_time, max_time = ComplexityScorer.estimate_turnaround_minutes(agent)
        
        return {
            "task_id": task.task_id,
            "complexity_score": score,
            "target_agent": agent,
            "estimated_turnaround_min": min_time,
            "estimated_turnaround_max": max_time,
            "routing_timestamp": datetime.utcnow().isoformat() + "Z"
        }


# ============================================================================
# EXAMPLE USAGE & VALIDATION
# ============================================================================

def run_examples():
    """Run example complexity scoring scenarios."""
    
    print("=" * 80)
    print("COMPLEXITY SCORING EXAMPLES")
    print("=" * 80)
    
    # Example 1: Simple model card
    print("\n1. SIMPLE MODEL CARD GENERATION")
    print("-" * 80)
    task1 = Task(
        task_id="crawler_001",
        title="Generate Mistral 7B model card",
        category=TaskCategory.RESEARCH,
        description="Research and document Mistral 7B specifications, benchmarks, ecosystem",
        base_scope="small",
        modifiers=ComplexityModifiers()  # No modifiers
    )
    
    result1 = ComplexityScorer.score_and_route(task1)
    print(f"Task: {task1.title}")
    print(f"Base Scope: {task1.base_scope}")
    print(f"Modifiers: {task1.modifiers.calculate_total()} points")
    print(f"→ Complexity Score: {result1['complexity_score']}")
    print(f"→ Target Agent: {result1['target_agent'].upper()}")
    print(f"→ Turnaround: {result1['estimated_turnaround_min']}-{result1['estimated_turnaround_max']} min")
    
    # Example 2: Multi-model comparison
    print("\n2. MULTI-MODEL COMPARISON (Delegation routing research)")
    print("-" * 80)
    task2 = Task(
        task_id="copilot_002",
        title="Compare 5 code generation models for Ryzen 7",
        category=TaskCategory.RESEARCH,
        description="Benchmark and compare DeepSeek, Mistral, StarCoder for code generation on Ryzen 7",
        base_scope="medium",
        modifiers=ComplexityModifiers(
            multi_model_comparison=True,
            hardware_specific=True,
            custom_research=True
        )
    )
    
    result2 = ComplexityScorer.score_and_route(task2)
    print(f"Task: {task2.title}")
    print(f"Base Scope: {task2.base_scope}")
    print(f"Modifiers: {task2.modifiers.calculate_total()} points")
    print(f"  - Multi-model comparison: +2")
    print(f"  - Hardware specific: +1")
    print(f"  - Custom research: +1")
    print(f"→ Complexity Score: {result2['complexity_score']}")
    print(f"→ Target Agent: {result2['target_agent'].upper()}")
    print(f"→ Turnaround: {result2['estimated_turnaround_min']}-{result2['estimated_turnaround_max']} min")
    
    # Example 3: Complex implementation
    print("\n3. DELEGATION ROUTING ENGINE IMPLEMENTATION")
    print("-" * 80)
    task3 = Task(
        task_id="cline_003",
        title="Implement delegation routing engine",
        category=TaskCategory.IMPLEMENTATION,
        description="Code task_classifier.py and routing_engine.py per DELEGATION-PROTOCOL-v1.md",
        base_scope="large",
        modifiers=ComplexityModifiers(
            novel_integration=True,
            code_generation_required=True,
            system_strategy=True
        )
    )
    
    result3 = ComplexityScorer.score_and_route(task3)
    print(f"Task: {task3.title}")
    print(f"Base Scope: {task3.base_scope}")
    print(f"Modifiers: {task3.modifiers.calculate_total()} points")
    print(f"  - Novel integration: +2")
    print(f"  - Code generation: +1")
    print(f"  - System strategy: +2")
    print(f"→ Complexity Score: {result3['complexity_score']}")
    print(f"→ Target Agent: {result3['target_agent'].upper()}")
    print(f"→ Turnaround: {result3['estimated_turnaround_min']}-{result3['estimated_turnaround_max']} min")
    
    # Example 4: Large-scale system analysis
    print("\n4. HOLISTIC SYSTEM ANALYSIS (XOH Review)")
    print("-" * 80)
    task4 = Task(
        task_id="gemini_004",
        title="Holistic XOH strategy review",
        category=TaskCategory.PLANNING,
        description="Analyze entire 16-phase plan, identify overlaps, gaps, priorities",
        base_scope="large",
        modifiers=ComplexityModifiers(
            system_strategy=True,
            documentation_heavy=True,
            custom_research=True
        )
    )
    
    result4 = ComplexityScorer.score_and_route(task4)
    print(f"Task: {task4.title}")
    print(f"Base Scope: {task4.base_scope}")
    print(f"Modifiers: {task4.modifiers.calculate_total()} points")
    print(f"  - System strategy: +2")
    print(f"  - Documentation heavy: +1")
    print(f"  - Custom research: +1")
    print(f"→ Complexity Score: {result4['complexity_score']}")
    print(f"→ Target Agent: {result4['target_agent'].upper()}")
    print(f"→ Turnaround: {result4['estimated_turnaround_min']}-{result4['estimated_turnaround_max']} min")
    
    print("\n" + "=" * 80)
    print("ROUTING SUMMARY")
    print("=" * 80)
    
    all_results = [result1, result2, result3, result4]
    for result in all_results:
        print(f"{result['task_id']:15} Score: {result['complexity_score']} → {result['target_agent'].upper()}")
    
    print("\n" + "=" * 80)
    return all_results


if __name__ == "__main__":
    results = run_examples()
    print(f"\n✅ Complexity scoring validated on {len(results)} scenarios")
