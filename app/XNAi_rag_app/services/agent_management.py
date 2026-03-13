"""Agent registry and research job management services."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.exc import IntegrityError
import json

from app.XNAi_rag_app.models.agent_models import (
    Agent, AgentPreference, ResearchJob, AgentMetric, 
    AgentMemory, AgentPersonality, Base
)
from app.XNAi_rag_app.services.database import get_db_session


class AgentRegistry:
    """Service for managing agent registration and lifecycle."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or get_db_session()
    
    def register_agent(
        self, 
        name: str, 
        model: str, 
        runtime: str = "unknown",
        email: Optional[str] = None
    ) -> Agent:
        """Register a new agent."""
        try:
            agent = Agent(
                name=name,
                model=model,
                runtime=runtime,
                email=email,
                priority=0,
                personality_version=1,
                status="active"
            )
            self.db.add(agent)
            self.db.commit()
            self.db.refresh(agent)
            return agent
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Agent with name '{name}' already exists")
    
    def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        """Get agent by ID."""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name."""
        return self.db.query(Agent).filter(Agent.name == name).first()
    
    def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all agents with optional status filter."""
        query = self.db.query(Agent)
        if status:
            query = query.filter(Agent.status == status)
        
        agents = query.order_by(Agent.priority.desc(), Agent.created_at).all()
        
        return [
            {
                "id": str(agent.id),
                "name": agent.name,
                "model": agent.model,
                "runtime": agent.runtime,
                "priority": float(agent.priority),
                "status": agent.status,
                "last_seen": agent.last_seen.isoformat() if agent.last_seen else None,
                "created_at": agent.created_at.isoformat()
            }
            for agent in agents
        ]
    
    def update_agent_status(self, agent_id: UUID, status: str) -> bool:
        """Update agent status."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.status = status
        if status == "active":
            agent.last_seen = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def update_agent_priority(self, agent_id: UUID, priority: float) -> bool:
        """Update agent priority."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.priority = priority
        self.db.commit()
        return True
    
    def delete_agent(self, agent_id: UUID) -> bool:
        """Delete agent (soft delete by setting status to inactive)."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        agent.status = "inactive"
        self.db.commit()
        return True
    
    def get_agent_preferences(self, agent_id: UUID) -> Dict[str, float]:
        """Get agent domain preferences."""
        preferences = self.db.query(AgentPreference).filter(
            AgentPreference.agent_id == agent_id
        ).all()
        
        return {pref.domain: float(pref.score) for pref in preferences}
    
    def set_agent_preferences(self, agent_id: UUID, preferences: Dict[str, float]) -> bool:
        """Set agent domain preferences."""
        # Remove existing preferences
        self.db.query(AgentPreference).filter(
            AgentPreference.agent_id == agent_id
        ).delete()
        
        # Add new preferences
        for domain, score in preferences.items():
            pref = AgentPreference(
                agent_id=agent_id,
                domain=domain,
                score=score
            )
            self.db.add(pref)
        
        self.db.commit()
        return True
    
    def update_agent_personality(self, agent_id: UUID, personality_data: Dict[str, Any]) -> bool:
        """Update agent personality and version."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        # Create personality history entry
        personality = AgentPersonality(
            agent_id=agent_id,
            version=agent.personality_version + 1,
            personality_json=personality_data
        )
        
        self.db.add(personality)
        agent.personality_version += 1
        self.db.commit()
        return True


class ResearchJobManager:
    """Service for managing research jobs and collaboration."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or get_db_session()
        self.registry = AgentRegistry(self.db)
    
    def create_job(
        self, 
        slug: str, 
        title: str, 
        description: Optional[str] = None,
        domain_tags: Optional[List[str]] = None
    ) -> ResearchJob:
        """Create a new research job."""
        try:
            job = ResearchJob(
                slug=slug,
                title=title,
                description=description,
                status="open",
                domain_tags=domain_tags or [],
                claimed_by=None
            )
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            return job
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Job with slug '{slug}' already exists")
    
    def get_job(self, job_id: UUID) -> Optional[ResearchJob]:
        """Get job by ID."""
        return self.db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    
    def get_job_by_slug(self, slug: str) -> Optional[ResearchJob]:
        """Get job by slug."""
        return self.db.query(ResearchJob).filter(ResearchJob.slug == slug).first()
    
    def list_jobs(
        self, 
        status: Optional[str] = None, 
        claimed_by: Optional[UUID] = None,
        domain_tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List jobs with optional filters."""
        query = self.db.query(ResearchJob)
        
        if status:
            query = query.filter(ResearchJob.status == status)
        
        if claimed_by:
            query = query.filter(ResearchJob.claimed_by == claimed_by)
        
        if domain_tags:
            # Filter jobs that have any of the specified domain tags
            query = query.filter(
                ResearchJob.domain_tags.op('&&')(domain_tags)
            )
        
        jobs = query.order_by(ResearchJob.created_at.desc()).all()
        
        return [
            {
                "id": str(job.id),
                "slug": job.slug,
                "title": job.title,
                "description": job.description,
                "status": job.status,
                "claimed_by": str(job.claimed_by) if job.claimed_by else None,
                "domain_tags": job.domain_tags,
                "created_at": job.created_at.isoformat(),
                "collaborators": [str(collab.id) for collab in job.collaborators]
            }
            for job in jobs
        ]
    
    def claim_job(self, job_id: UUID, agent_id: UUID) -> bool:
        """Claim a job for an agent."""
        job = self.get_job(job_id)
        agent = self.registry.get_agent(agent_id)
        
        if not job or not agent:
            return False
        
        if job.status != "open":
            return False
        
        job.status = "claimed"
        job.claimed_by = agent_id
        
        # Add agent as collaborator
        if agent not in job.collaborators:
            job.collaborators.append(agent)
        
        self.db.commit()
        return True
    
    def release_job(self, job_id: UUID) -> bool:
        """Release a claimed job."""
        job = self.get_job(job_id)
        if not job:
            return False
        
        job.status = "open"
        job.claimed_by = None
        job.collaborators = []  # Clear collaborators when releasing
        
        self.db.commit()
        return True
    
    def invite_collaborator(self, job_id: UUID, agent_id: UUID) -> bool:
        """Invite an agent to collaborate on a job."""
        job = self.get_job(job_id)
        agent = self.registry.get_agent(agent_id)
        
        if not job or not agent:
            return False
        
        if agent not in job.collaborators:
            job.collaborators.append(agent)
            self.db.commit()
        
        return True
    
    def remove_collaborator(self, job_id: UUID, agent_id: UUID) -> bool:
        """Remove an agent from job collaboration."""
        job = self.get_job(job_id)
        agent = self.registry.get_agent(agent_id)
        
        if not job or not agent:
            return False
        
        if agent in job.collaborators:
            job.collaborators.remove(agent)
            self.db.commit()
        
        return True
    
    def complete_job(self, job_id: UUID) -> bool:
        """Mark a job as completed."""
        job = self.get_job(job_id)
        if not job:
            return False
        
        job.status = "completed"
        self.db.commit()
        return True
    
    def get_available_jobs_for_agent(self, agent_id: UUID) -> List[Dict[str, Any]]:
        """Get jobs available for an agent based on preferences."""
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return []
        
        # Get agent preferences
        preferences = self.registry.get_agent_preferences(agent_id)
        
        # Get open jobs
        open_jobs = self.db.query(ResearchJob).filter(
            ResearchJob.status == "open"
        ).all()
        
        # Score jobs based on domain match
        scored_jobs = []
        for job in open_jobs:
            score = 0
            for tag in job.domain_tags:
                if tag in preferences:
                    score += preferences[tag]
            
            scored_jobs.append((job, score))
        
        # Sort by score and return
        scored_jobs.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                "id": str(job.id),
                "slug": job.slug,
                "title": job.title,
                "description": job.description,
                "domain_tags": job.domain_tags,
                "score": float(score),
                "created_at": job.created_at.isoformat()
            }
            for job, score in scored_jobs
        ]


class AgentMetricsManager:
    """Service for managing agent performance metrics."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or get_db_session()
    
    def record_metric(
        self, 
        agent_id: UUID, 
        metric_name: str, 
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMetric:
        """Record a metric for an agent."""
        metric = AgentMetric(
            agent_id=agent_id,
            metric_name=metric_name,
            value=value
        )
        
        if metadata:
            # Store metadata as JSON in a separate table or as part of the metric
            pass
        
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric
    
    def get_agent_metrics(
        self, 
        agent_id: UUID, 
        metric_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get metrics for an agent."""
        query = self.db.query(AgentMetric).filter(AgentMetric.agent_id == agent_id)
        
        if metric_name:
            query = query.filter(AgentMetric.metric_name == metric_name)
        
        metrics = query.order_by(desc(AgentMetric.recorded_at)).limit(limit).all()
        
        return [
            {
                "id": str(metric.id),
                "metric_name": metric.metric_name,
                "value": float(metric.value),
                "recorded_at": metric.recorded_at.isoformat()
            }
            for metric in metrics
        ]
    
    def get_agent_composite_score(self, agent_id: UUID) -> float:
        """Calculate composite score for an agent based on recent metrics."""
        # Get recent metrics (last 30 days)
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        metrics = self.db.query(AgentMetric).filter(
            AgentMetric.agent_id == agent_id,
            AgentMetric.recorded_at >= cutoff
        ).all()
        
        if not metrics:
            return 0.0
        
        # Simple scoring: average of all metrics
        total_score = sum(float(metric.value) for metric in metrics)
        return total_score / len(metrics)
    
    def update_agent_ranking(self) -> bool:
        """Update agent priorities based on metrics."""
        agents = self.db.query(Agent).filter(Agent.status == "active").all()
        
        for agent in agents:
            score = self.get_agent_composite_score(agent.id)
            agent.priority = score
        
        self.db.commit()
        return True


class AgentMemoryManager:
    """Service for managing agent memory storage."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or get_db_session()
    
    def store_memory(
        self, 
        agent_id: UUID, 
        memory_type: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMemory:
        """Store a memory for an agent."""
        memory = AgentMemory(
            agent_id=agent_id,
            memory_type=memory_type,
            content=content,
            metadata_json=metadata
        )
        
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory
    
    def get_memories(
        self, 
        agent_id: UUID, 
        memory_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get memories for an agent."""
        query = self.db.query(AgentMemory).filter(AgentMemory.agent_id == agent_id)
        
        if memory_type:
            query = query.filter(AgentMemory.memory_type == memory_type)
        
        memories = query.order_by(desc(AgentMemory.created_at)).limit(limit).all()
        
        return [
            {
                "id": str(memory.id),
                "memory_type": memory.memory_type,
                "content": memory.content,
                "metadata": memory.metadata_json,
                "created_at": memory.created_at.isoformat()
            }
            for memory in memories
        ]
    
    def clear_memories(self, agent_id: UUID, memory_type: Optional[str] = None) -> bool:
        """Clear memories for an agent."""
        query = self.db.query(AgentMemory).filter(AgentMemory.agent_id == agent_id)
        
        if memory_type:
            query = query.filter(AgentMemory.memory_type == memory_type)
        
        query.delete()
        self.db.commit()
        return True