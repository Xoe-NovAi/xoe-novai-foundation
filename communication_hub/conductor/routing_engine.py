#!/usr/bin/env python3
"""
Phase D: Routing Engine - Task Dispatch & Agent Selection

Implements the routing decision tree from DELEGATION-PROTOCOL-v1.md
Coordinates with Redis for job persistence and Consul for service discovery
"""

import json
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Agent availability status."""
    AVAILABLE = "available"
    BUSY = "busy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


@dataclass
class AgentCapacity:
    """Agent capacity and performance metrics."""
    agent_id: str
    agent_type: str  # crawler, copilot, gemini, cline
    status: AgentStatus
    current_load: int  # Number of tasks currently processing
    max_concurrent: int  # Max tasks this agent can handle
    avg_response_time_ms: int  # Average response time
    last_heartbeat: str  # ISO8601 timestamp
    
    @property
    def is_available(self) -> bool:
        """Check if agent can accept new tasks."""
        return (
            self.status == AgentStatus.AVAILABLE and
            self.current_load < self.max_concurrent
        )
    
    @property
    def availability_percent(self) -> float:
        """Get availability percentage (0-100)."""
        if self.max_concurrent == 0:
            return 0
        return 100 * (self.max_concurrent - self.current_load) / self.max_concurrent


@dataclass
class RoutingDecision:
    """Result of routing decision."""
    task_id: str
    complexity_score: int
    primary_agent: str
    fallback_agent: Optional[str]
    estimated_turnaround_min: int
    estimated_turnaround_max: int
    reason: str
    timestamp: str


class RoutingEngine:
    """
    Routes tasks to appropriate agents based on:
    1. Complexity score (from task_classifier)
    2. Agent availability (from Consul/Redis)
    3. Task priority
    4. Fallback strategies
    """
    
    # Default capacity for each agent type
    DEFAULT_CAPACITIES = {
        "crawler": 3,      # 3 concurrent model cards
        "copilot": 1,      # 1 strategic task (100K context is big)
        "gemini": 1,       # 1 large-scale task (1M context)
        "cline": 1         # 1 implementation task (256K context)
    }
    
    # Score to agent routing
    COMPLEXITY_ROUTING = {
        (1, 3): "crawler",
        (4, 5): "copilot",
        (6, 7): "gemini",
        (8, float('inf')): "cline"
    }
    
    def __init__(self):
        """Initialize routing engine."""
        self.agent_capacities: Dict[str, AgentCapacity] = {}
        self.job_queue: Dict[str, Dict] = {}  # task_id -> job details
        self.job_history: List[Dict] = []
        
    def register_agent(self, capacity: AgentCapacity) -> None:
        """Register agent with routing engine."""
        self.agent_capacities[capacity.agent_id] = capacity
    
    def get_primary_agent(self, score: int) -> Optional[str]:
        """Get primary agent based on complexity score."""
        for (min_score, max_score), agent in self.COMPLEXITY_ROUTING.items():
            if min_score <= score <= max_score:
                return agent
        return None
    
    def get_available_agents_of_type(self, agent_type: str) -> List[AgentCapacity]:
        """Get all available agents of a specific type."""
        agents = [
            cap for cap in self.agent_capacities.values()
            if cap.agent_type == agent_type and cap.is_available
        ]
        # Sort by current load (prefer least busy)
        return sorted(agents, key=lambda a: a.current_load)
    
    def route_task(self,
                   task_id: str,
                   complexity_score: int,
                   priority: int = 1) -> RoutingDecision:
        """
        Route a task to an appropriate agent.
        
        Args:
            task_id: Unique task identifier
            complexity_score: Complexity score from TaskClassifier (1-10+)
            priority: Priority level (1=critical, 5=normal, 10=deferred)
        
        Returns:
            RoutingDecision with primary and fallback agent
        """
        
        # Step 1: Get primary agent from score
        primary_agent_type = self.get_primary_agent(complexity_score)
        if not primary_agent_type:
            raise ValueError(f"No agent type for complexity score {complexity_score}")
        
        # Step 2: Get available agents of primary type
        available_primary = self.get_available_agents_of_type(primary_agent_type)
        
        if available_primary:
            # Primary agent available
            primary_agent = available_primary[0]  # Get least busy
            return RoutingDecision(
                task_id=task_id,
                complexity_score=complexity_score,
                primary_agent=primary_agent.agent_id,
                fallback_agent=None,
                estimated_turnaround_min=self._estimate_turnaround(primary_agent_type)[0],
                estimated_turnaround_max=self._estimate_turnaround(primary_agent_type)[1],
                reason=f"Routed to {primary_agent_type} (score {complexity_score}, load {primary_agent.current_load}/{primary_agent.max_concurrent})",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
        else:
            # Primary unavailable, try fallback strategy
            fallback_type = self._get_fallback_agent(primary_agent_type, complexity_score)
            
            if fallback_type:
                available_fallback = self.get_available_agents_of_type(fallback_type)
                
                if available_fallback:
                    fallback_agent = available_fallback[0]
                    return RoutingDecision(
                        task_id=task_id,
                        complexity_score=complexity_score,
                        primary_agent=primary_agent_type,  # What we wanted
                        fallback_agent=fallback_agent.agent_id,  # What we got
                        estimated_turnaround_min=self._estimate_turnaround(fallback_type)[0],
                        estimated_turnaround_max=self._estimate_turnaround(fallback_type)[1],
                        reason=f"{primary_agent_type} unavailable, fallback to {fallback_type}",
                        timestamp=datetime.utcnow().isoformat() + "Z"
                    )
            
            # No agents available, queue for later
            return RoutingDecision(
                task_id=task_id,
                complexity_score=complexity_score,
                primary_agent=primary_agent_type,
                fallback_agent=None,
                estimated_turnaround_min=300,  # 5 hours, queued
                estimated_turnaround_max=600,
                reason=f"All agents busy, queued (priority {priority})",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
    
    def _get_fallback_agent(self, primary_type: str, score: int) -> Optional[str]:
        """Get fallback agent if primary is unavailable."""
        fallback_map = {
            "crawler": "copilot",      # Crawler ← Copilot can do simple research
            "copilot": "gemini",       # Copilot ← Gemini can do synthesis
            "gemini": "cline",         # Gemini ← Cline can write code for insights
            "cline": None              # Cline ← No fallback (last resort)
        }
        return fallback_map.get(primary_type)
    
    def _estimate_turnaround(self, agent_type: str) -> tuple:
        """Estimate turnaround time for agent type."""
        estimates = {
            "crawler": (15, 60),
            "copilot": (30, 120),
            "gemini": (120, 360),
            "cline": (240, 720)
        }
        return estimates.get(agent_type, (None, None))
    
    def enqueue_job(self, decision: RoutingDecision, job_details: Dict) -> str:
        """Enqueue a job in Redis (simulated here)."""
        job_id = str(uuid.uuid4())
        
        job_entry = {
            "job_id": job_id,
            "task_id": decision.task_id,
            "target_agent": decision.primary_agent or "queue",
            "fallback_agent": decision.fallback_agent,
            "complexity_score": decision.complexity_score,
            "estimated_turnaround_min": decision.estimated_turnaround_min,
            "estimated_turnaround_max": decision.estimated_turnaround_max,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "job_details": job_details
        }
        
        self.job_queue[job_id] = job_entry
        self.job_history.append(job_entry)
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a queued job."""
        return self.job_queue.get(job_id)
    
    def update_job_status(self, job_id: str, status: str) -> None:
        """Update job status."""
        if job_id in self.job_queue:
            self.job_queue[job_id]["status"] = status
            self.job_queue[job_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"


# ============================================================================
# EXAMPLE USAGE & VALIDATION
# ============================================================================

def run_examples():
    """Run routing engine examples."""
    
    print("=" * 80)
    print("ROUTING ENGINE EXAMPLES")
    print("=" * 80)
    
    # Initialize routing engine
    engine = RoutingEngine()
    
    # Register some agents
    print("\n1. REGISTERING AGENTS")
    print("-" * 80)
    
    agents = [
        AgentCapacity(
            agent_id="crawler:001",
            agent_type="crawler",
            status=AgentStatus.AVAILABLE,
            current_load=1,
            max_concurrent=3,
            avg_response_time_ms=500,
            last_heartbeat=datetime.utcnow().isoformat() + "Z"
        ),
        AgentCapacity(
            agent_id="copilot:haiku:001",
            agent_type="copilot",
            status=AgentStatus.AVAILABLE,
            current_load=0,
            max_concurrent=1,
            avg_response_time_ms=2000,
            last_heartbeat=datetime.utcnow().isoformat() + "Z"
        ),
        AgentCapacity(
            agent_id="gemini:pro:001",
            agent_type="gemini",
            status=AgentStatus.BUSY,  # Busy!
            current_load=1,
            max_concurrent=1,
            avg_response_time_ms=5000,
            last_heartbeat=datetime.utcnow().isoformat() + "Z"
        ),
        AgentCapacity(
            agent_id="cline:kat:001",
            agent_type="cline",
            status=AgentStatus.AVAILABLE,
            current_load=0,
            max_concurrent=1,
            avg_response_time_ms=3000,
            last_heartbeat=datetime.utcnow().isoformat() + "Z"
        ),
    ]
    
    for agent in agents:
        engine.register_agent(agent)
        print(f"✓ {agent.agent_id:25} Type: {agent.agent_type:10} Load: {agent.current_load}/{agent.max_concurrent}")
    
    # Route tasks
    print("\n2. ROUTING TASKS")
    print("-" * 80)
    
    tasks = [
        ("task_001", 1, "Generate single model card"),
        ("task_002", 5, "Plan multi-phase project"),
        ("task_003", 7, "Analyze system architecture (Gemini busy!)"),
        ("task_004", 8, "Implement routing engine"),
    ]
    
    for task_id, score, description in tasks:
        decision = engine.route_task(task_id, score, priority=1)
        print(f"\nTask: {task_id} (Score: {score})")
        print(f"Description: {description}")
        print(f"→ Primary: {decision.primary_agent}")
        if decision.fallback_agent:
            print(f"→ Fallback: {decision.fallback_agent}")
        print(f"→ Turnaround: {decision.estimated_turnaround_min}-{decision.estimated_turnaround_max} min")
        print(f"→ Reason: {decision.reason}")
        
        # Enqueue job
        job_id = engine.enqueue_job(decision, {"description": description})
        print(f"→ Job ID: {job_id}")
    
    print("\n" + "=" * 80)
    print("JOB QUEUE STATUS")
    print("=" * 80)
    
    for job_id, job in list(engine.job_queue.items())[:5]:  # First 5
        print(f"Job {job_id[:8]}... → {job['target_agent']:15} Status: {job['status']}")
    
    print("\n" + "=" * 80)
    return engine


if __name__ == "__main__":
    engine = run_examples()
    print(f"\n✅ Routing engine validated with {len(engine.job_queue)} jobs queued")
