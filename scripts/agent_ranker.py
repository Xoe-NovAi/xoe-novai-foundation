#!/usr/bin/env python3
"""Agent ranking service with Prometheus metrics collection."""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import os

from prometheus_client import Gauge, Counter, Histogram, start_http_server, CollectorRegistry
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.XNAi_rag_app.services.agent_management import AgentRegistry, AgentMetricsManager, ResearchJobManager
from app.XNAi_rag_app.services.database import get_db_session


# Prometheus metrics
registry = CollectorRegistry()

# Agent performance metrics
agent_success_rate = Gauge('agent_task_success_rate', 'Agent task success rate', ['agent_id', 'agent_name'], registry=registry)
agent_latency_seconds = Histogram('agent_task_latency_seconds', 'Agent task completion latency', ['agent_id', 'agent_name'], registry=registry)
agent_model_accuracy = Gauge('agent_model_accuracy', 'Agent model accuracy score', ['agent_id', 'agent_name', 'model'], registry=registry)
agent_research_outcomes = Counter('agent_research_outcomes_total', 'Agent research outcomes', ['agent_id', 'agent_name', 'outcome'], registry=registry)
agent_priority_score = Gauge('agent_priority_score', 'Agent priority score for task assignment', ['agent_id', 'agent_name'], registry=registry)

# System metrics
active_agents = Gauge('active_agents_total', 'Number of active agents', registry=registry)
open_jobs = Gauge('open_jobs_total', 'Number of open research jobs', registry=registry)
claimed_jobs = Gauge('claimed_jobs_total', 'Number of claimed research jobs', registry=registry)
completed_jobs = Gauge('completed_jobs_total', 'Number of completed research jobs', registry=registry)


@dataclass
class AgentMetrics:
    """Agent metrics for ranking calculation."""
    agent_id: str
    agent_name: str
    model: str
    success_rate: float
    avg_latency: float
    model_accuracy: float
    research_score: float
    composite_score: float
    last_activity: Optional[datetime]
    total_tasks: int
    completed_tasks: int


class AgentRanker:
    """Service for ranking agents based on performance metrics."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or get_db_session()
        self.registry = AgentRegistry(self.db)
        self.metrics = AgentMetricsManager(self.db)
        self.jobs = ResearchJobManager(self.db)
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.weight_success_rate = 0.3
        self.weight_latency = 0.2
        self.weight_accuracy = 0.25
        self.weight_research = 0.25
        self.recent_days = 30  # Consider metrics from last 30 days
        
    def calculate_composite_score(self, agent_id: str) -> float:
        """Calculate composite score for an agent."""
        try:
            # Get recent metrics
            cutoff = datetime.utcnow() - timedelta(days=self.recent_days)
            
            # Success rate (from task completion metrics)
            success_rate = self._get_success_rate(agent_id, cutoff)
            
            # Average latency (from task duration metrics)
            avg_latency = self._get_avg_latency(agent_id, cutoff)
            
            # Model accuracy (from model-specific metrics)
            model_accuracy = self._get_model_accuracy(agent_id, cutoff)
            
            # Research score (from research job completion and quality)
            research_score = self._get_research_score(agent_id, cutoff)
            
            # Normalize latency (lower is better, so we invert it)
            normalized_latency = 1.0 / (1.0 + avg_latency) if avg_latency > 0 else 1.0
            
            # Calculate weighted composite score
            composite_score = (
                self.weight_success_rate * success_rate +
                self.weight_latency * normalized_latency +
                self.weight_accuracy * model_accuracy +
                self.weight_research * research_score
            )
            
            return composite_score
            
        except Exception as e:
            self.logger.error(f"Error calculating composite score for agent {agent_id}: {e}")
            return 0.0
    
    def _get_success_rate(self, agent_id: str, cutoff: datetime) -> float:
        """Get task success rate for an agent."""
        try:
            # Count successful vs total tasks
            # This would depend on how you track task success/failure
            # For now, we'll use a simplified approach based on job completion
            
            total_jobs = self.db.query(func.count(ResearchJob.id)).filter(
                ResearchJob.claimed_by == agent_id
            ).scalar() or 0
            
            completed_jobs = self.db.query(func.count(ResearchJob.id)).filter(
                ResearchJob.claimed_by == agent_id,
                ResearchJob.status == 'completed'
            ).scalar() or 0
            
            if total_jobs == 0:
                return 0.5  # Neutral score for new agents
            
            return completed_jobs / total_jobs
            
        except Exception as e:
            self.logger.error(f"Error getting success rate for agent {agent_id}: {e}")
            return 0.0
    
    def _get_avg_latency(self, agent_id: str, cutoff: datetime) -> float:
        """Get average task completion latency for an agent."""
        try:
            # This would typically come from timing metrics
            # For now, return a placeholder value
            return 0.1  # Placeholder average latency in hours
            
        except Exception as e:
            self.logger.error(f"Error getting avg latency for agent {agent_id}: {e}")
            return 1.0
    
    def _get_model_accuracy(self, agent_id: str, cutoff: datetime) -> float:
        """Get model accuracy score for an agent."""
        try:
            # Get model accuracy metrics
            accuracy_metrics = self.db.query(AgentMetric).filter(
                AgentMetric.agent_id == agent_id,
                AgentMetric.metric_name == 'model_accuracy',
                AgentMetric.recorded_at >= cutoff
            ).all()
            
            if not accuracy_metrics:
                return 0.5  # Neutral score for agents without accuracy data
            
            # Calculate average accuracy
            total_accuracy = sum(float(m.value) for m in accuracy_metrics)
            return total_accuracy / len(accuracy_metrics)
            
        except Exception as e:
            self.logger.error(f"Error getting model accuracy for agent {agent_id}: {e}")
            return 0.5
    
    def _get_research_score(self, agent_id: str, cutoff: datetime) -> float:
        """Get research quality score for an agent."""
        try:
            # Count research jobs and their quality indicators
            # This could include:
            # - Number of completed research jobs
            # - Quality ratings from peer reviews
            # - Integration with memory bank
            # - Documentation quality
            
            completed_jobs = self.db.query(func.count(ResearchJob.id)).filter(
                ResearchJob.claimed_by == agent_id,
                ResearchJob.status == 'completed'
            ).scalar() or 0
            
            # Simple scoring based on number of completed jobs
            # In a real implementation, this would be more sophisticated
            return min(completed_jobs * 0.1, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.error(f"Error getting research score for agent {agent_id}: {e}")
            return 0.0
    
    def update_agent_rankings(self) -> Dict[str, AgentMetrics]:
        """Update agent rankings and return current metrics."""
        try:
            # Get all active agents
            active_agents_list = self.registry.list_agents(status='active')
            
            agent_metrics = {}
            
            for agent_data in active_agents_list:
                agent_id = agent_data['id']
                agent_name = agent_data['name']
                model = agent_data['model']
                
                # Calculate metrics
                composite_score = self.calculate_composite_score(agent_id)
                success_rate = self._get_success_rate(agent_id, datetime.utcnow() - timedelta(days=self.recent_days))
                avg_latency = self._get_avg_latency(agent_id, datetime.utcnow() - timedelta(days=self.recent_days))
                model_accuracy = self._get_model_accuracy(agent_id, datetime.utcnow() - timedelta(days=self.recent_days))
                research_score = self._get_research_score(agent_id, datetime.utcnow() - timedelta(days=self.recent_days))
                
                # Get task statistics
                total_tasks = self.db.query(func.count(ResearchJob.id)).filter(
                    ResearchJob.claimed_by == agent_id
                ).scalar() or 0
                
                completed_tasks = self.db.query(func.count(ResearchJob.id)).filter(
                    ResearchJob.claimed_by == agent_id,
                    ResearchJob.status == 'completed'
                ).scalar() or 0
                
                # Update agent priority in database
                self.registry.update_agent_priority(agent_id, composite_score)
                
                # Store metrics
                metrics = AgentMetrics(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    model=model,
                    success_rate=success_rate,
                    avg_latency=avg_latency,
                    model_accuracy=model_accuracy,
                    research_score=research_score,
                    composite_score=composite_score,
                    last_activity=datetime.utcnow(),
                    total_tasks=total_tasks,
                    completed_tasks=completed_tasks
                )
                
                agent_metrics[agent_id] = metrics
                
                # Update Prometheus metrics
                self._update_prometheus_metrics(metrics)
            
            self.logger.info(f"Updated rankings for {len(agent_metrics)} agents")
            return agent_metrics
            
        except Exception as e:
            self.logger.error(f"Error updating agent rankings: {e}")
            return {}
    
    def _update_prometheus_metrics(self, metrics: AgentMetrics):
        """Update Prometheus metrics with agent data."""
        try:
            # Update individual metrics
            agent_success_rate.labels(
                agent_id=metrics.agent_id,
                agent_name=metrics.agent_name
            ).set(metrics.success_rate)
            
            agent_latency_seconds.labels(
                agent_id=metrics.agent_id,
                agent_name=metrics.agent_name
            ).observe(metrics.avg_latency)
            
            agent_model_accuracy.labels(
                agent_id=metrics.agent_id,
                agent_name=metrics.agent_name,
                model=metrics.model
            ).set(metrics.model_accuracy)
            
            agent_priority_score.labels(
                agent_id=metrics.agent_id,
                agent_name=metrics.agent_name
            ).set(metrics.composite_score)
            
            # Update system metrics
            active_agents.set(self._get_active_agent_count())
            open_jobs.set(self._get_job_count('open'))
            claimed_jobs.set(self._get_job_count('claimed'))
            completed_jobs.set(self._get_job_count('completed'))
            
        except Exception as e:
            self.logger.error(f"Error updating Prometheus metrics: {e}")
    
    def _get_active_agent_count(self) -> int:
        """Get count of active agents."""
        try:
            return self.db.query(func.count(Agent.id)).filter(
                Agent.status == 'active'
            ).scalar() or 0
        except:
            return 0
    
    def _get_job_count(self, status: str) -> int:
        """Get count of jobs with specific status."""
        try:
            return self.db.query(func.count(ResearchJob.id)).filter(
                ResearchJob.status == status
            ).scalar() or 0
        except:
            return 0
    
    def get_leaderboard(self, limit: int = 10) -> List[AgentMetrics]:
        """Get agent leaderboard sorted by composite score."""
        agent_metrics = self.update_agent_rankings()
        sorted_agents = sorted(
            agent_metrics.values(),
            key=lambda x: x.composite_score,
            reverse=True
        )
        return sorted_agents[:limit]


class AgentRankerService:
    """Background service for agent ranking and metrics collection."""
    
    def __init__(self, update_interval: int = 300):  # Default 5 minutes
        self.ranker = AgentRanker()
        self.update_interval = update_interval
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the ranking service."""
        self.running = True
        self.logger.info(f"Starting agent ranking service with {self.update_interval}s interval")
        
        # Start Prometheus metrics server
        prometheus_port = int(os.getenv('PROMETHEUS_PORT', '8001'))
        start_http_server(prometheus_port, registry=registry)
        self.logger.info(f"Prometheus metrics server started on port {prometheus_port}")
        
        # Start ranking loop
        asyncio.create_task(self._ranking_loop())
    
    async def stop(self):
        """Stop the ranking service."""
        self.running = False
        self.logger.info("Stopping agent ranking service")
    
    async def _ranking_loop(self):
        """Main ranking update loop."""
        while self.running:
            try:
                self.logger.info("Updating agent rankings...")
                agent_metrics = self.ranker.update_agent_rankings()
                
                # Log top performers
                if agent_metrics:
                    sorted_agents = sorted(
                        agent_metrics.values(),
                        key=lambda x: x.composite_score,
                        reverse=True
                    )
                    
                    self.logger.info("Top 5 agents:")
                    for i, agent in enumerate(sorted_agents[:5], 1):
                        self.logger.info(f"  {i}. {agent.agent_name} (score: {agent.composite_score:.3f})")
                
            except Exception as e:
                self.logger.error(f"Error in ranking loop: {e}")
            
            await asyncio.sleep(self.update_interval)
    
    def get_current_rankings(self) -> List[Dict]:
        """Get current agent rankings."""
        leaderboard = self.ranker.get_leaderboard()
        return [
            {
                'rank': i + 1,
                'agent_id': agent.agent_id,
                'agent_name': agent.agent_name,
                'model': agent.model,
                'composite_score': round(agent.composite_score, 3),
                'success_rate': round(agent.success_rate, 3),
                'avg_latency': round(agent.avg_latency, 3),
                'model_accuracy': round(agent.model_accuracy, 3),
                'research_score': round(agent.research_score, 3),
                'total_tasks': agent.total_tasks,
                'completed_tasks': agent.completed_tasks
            }
            for i, agent in enumerate(leaderboard)
        ]


# Global service instance
ranker_service = AgentRankerService()


async def get_ranker_service() -> AgentRankerService:
    """Get the global ranking service instance."""
    return ranker_service


if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        update_interval = int(sys.argv[1])
    else:
        update_interval = 300  # 5 minutes default
    
    # Start the service
    service = AgentRankerService(update_interval)
    
    async def main():
        await service.start()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await service.stop()
    
    # Run the service
    asyncio.run(main())