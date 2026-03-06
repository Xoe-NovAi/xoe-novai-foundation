"""ORM models for agent management and research jobs."""

from sqlalchemy import Column, String, DateTime, UUID, JSON, Boolean, Numeric, ForeignKey, Table, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid
from datetime import datetime

Base = declarative_base()

# Association table for research collaborators
research_collaborators = Table(
    'research_collaborators', Base.metadata,
    Column('job_id', PGUUID(as_uuid=True), ForeignKey('research_jobs.id'), primary_key=True),
    Column('agent_id', PGUUID(as_uuid=True), ForeignKey('agents.id'), primary_key=True)
)


class Agent(Base):
    """Agent registry model."""
    
    __tablename__ = 'agents'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    runtime = Column(String(50), nullable=False, default='unknown')
    priority = Column(Numeric(precision=5, scale=2), nullable=False, default=0)
    personality_version = Column(Numeric(precision=5, scale=2), nullable=False, default=1)
    status = Column(String(50), nullable=False, default='active')
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    # Relationships
    preferences = relationship("AgentPreference", back_populates="agent", cascade="all, delete-orphan")
    claimed_jobs = relationship("ResearchJob", back_populates="claimed_by_agent")
    collaborations = relationship("ResearchJob", secondary=research_collaborators, back_populates="collaborators")
    metrics = relationship("AgentMetric", back_populates="agent", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_agents_priority', 'priority'),
        Index('idx_agents_status', 'status'),
        Index('idx_agents_last_seen', 'last_seen'),
    )


class AgentPreference(Base):
    """Agent domain preferences model."""
    
    __tablename__ = 'agent_preferences'
    
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), primary_key=True)
    domain = Column(String(255), primary_key=True)
    score = Column(Numeric(precision=5, scale=2), nullable=False, default=0)
    
    # Relationships
    agent = relationship("Agent", back_populates="preferences")
    
    __table_args__ = (
        Index('idx_agent_prefs_agent', 'agent_id'),
        Index('idx_agent_prefs_domain', 'domain'),
    )


class ResearchJob(Base):
    """Research job management model."""
    
    __tablename__ = 'research_jobs'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.uuid_generate_v4())
    slug = Column(String(255), nullable=False, unique=True)
    title = Column(String(500), nullable=False)
    description = Column(String, nullable=True)
    status = Column(String(50), nullable=False, default='open')
    claimed_by = Column(PGUUID(as_uuid=True), ForeignKey('agents.id', ondelete='SET NULL'), nullable=True)
    domain_tags = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    # Relationships
    claimed_by_agent = relationship("Agent", back_populates="claimed_jobs")
    collaborators = relationship("Agent", secondary=research_collaborators, back_populates="collaborations")
    
    __table_args__ = (
        Index('idx_research_jobs_status', 'status'),
        Index('idx_research_jobs_claimed_by', 'claimed_by'),
        Index('idx_research_jobs_slug', 'slug'),
    )


class AgentMetric(Base):
    """Agent performance metrics model."""
    
    __tablename__ = 'agent_metrics'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.uuid_generate_v4())
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    metric_name = Column(String(255), nullable=False)
    value = Column(Numeric(precision=12, scale=4), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    # Relationships
    agent = relationship("Agent", back_populates="metrics")
    
    __table_args__ = (
        Index('idx_agent_metrics_agent', 'agent_id'),
        Index('idx_agent_metrics_name', 'metric_name'),
        Index('idx_agent_metrics_time', 'recorded_at'),
    )


class AgentMemory(Base):
    """Agent memory storage model."""
    
    __tablename__ = 'agent_memories'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.uuid_generate_v4())
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    memory_type = Column(String(50), nullable=False)  # 'conversation', 'task', 'knowledge'
    content = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    # Relationships
    agent = relationship("Agent")
    
    __table_args__ = (
        Index('idx_agent_memories_agent', 'agent_id'),
        Index('idx_agent_memories_type', 'memory_type'),
        Index('idx_agent_memories_time', 'created_at'),
    )


class AgentPersonality(Base):
    """Agent personality versioning model."""
    
    __tablename__ = 'agent_personalities'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.uuid_generate_v4())
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    version = Column(Numeric(precision=5, scale=2), nullable=False)
    personality_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    # Relationships
    agent = relationship("Agent")
    
    __table_args__ = (
        Index('idx_agent_personalities_agent', 'agent_id'),
        Index('idx_agent_personalities_version', 'version'),
    )