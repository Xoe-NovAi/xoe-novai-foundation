"""Escalation Researcher Service for 4-level research chain.

This service implements the core research workflow with escalating complexity:
- Level 1: Basic retrieval and summarization
- Level 2: Multi-source aggregation and cross-validation
- Level 3: Expert synthesis and analysis
- Level 4: Final dossier creation and validation

Architecture follows the research strategy from the handoff documents.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from sqlalchemy.orm import Session

from app.XNAi_rag_app.services.agent_management import ResearchJobManager, AgentRegistry
from app.XNAi_rag_app.services.database import get_db_session
from app.XNAi_rag_app.core.redis_streams import RedisStreamManager
from app.XNAi_rag_app.core.iam_db import IAMDatabase, AgentType
from app.XNAi_rag_app.core.agent_orchestrator import AgentOrchestrator


class ResearchLevel(str, Enum):
    """Research levels in the escalation chain."""
    BASIC = "basic"
    AGGREGATION = "aggregation"
    SYNTHESIS = "synthesis"
    EXPERT = "expert"


@dataclass
class ResearchResult:
    """Result from a research level."""
    level: ResearchLevel
    confidence: float
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class ResearchDossier:
    """Final research dossier combining all levels."""
    query: str
    levels: List[ResearchResult]
    final_answer: str
    confidence_score: float
    created_at: datetime
    validation_report: Dict[str, Any]


class EscalationResearcher:
    """Core research service implementing 4-level escalation."""
    
    def __init__(self, redis_client=None, db_session: Optional[Session] = None):
        self.logger = logging.getLogger(__name__)
        self.redis = redis_client
        self.db = db_session or get_db_session()
        self.jobs = ResearchJobManager(self.db)
        self.agents = AgentRegistry(self.db)
        self.iam = IAMDatabase()
        self.stream_manager = RedisStreamManager(self.redis) if self.redis else None
        
        # Configuration
        self.max_retries = 3
        self.timeout_per_level = 300  # 5 minutes per level
        self.confidence_thresholds = {
            ResearchLevel.BASIC: 0.6,
            ResearchLevel.AGGREGATION: 0.7,
            ResearchLevel.SYNTHESIS: 0.8,
            ResearchLevel.EXPERT: 0.9
        }
    
    async def research_stream(self, query: str) -> AsyncGenerator[ResearchResult, None]:
        """Execute the 4-level research chain and yield results."""
        self.logger.info(f"Starting research for query: {query}")
        
        levels = [
            ResearchLevel.BASIC,
            ResearchLevel.AGGREGATION, 
            ResearchLevel.SYNTHESIS,
            ResearchLevel.EXPERT
        ]
        
        current_context = {"query": query, "previous_results": []}
        
        for level in levels:
            try:
                # Get appropriate agent for this level
                agent = await self._get_agent_for_level(level)
                if not agent:
                    self.logger.error(f"No agent available for level {level}")
                    continue
                
                # Execute research at this level
                result = await self._execute_research_level(
                    level, query, current_context, agent
                )
                
                # Validate result
                if result and await self._validate_result(result, level):
                    # Update context with result
                    current_context["previous_results"].append(result)
                    
                    # Yield result
                    yield result
                    
                    # Check if we can stop early (high confidence)
                    if result.confidence >= self.confidence_thresholds[level]:
                        self.logger.info(f"Early termination at level {level} due to high confidence")
                        break
                else:
                    self.logger.warning(f"Result validation failed for level {level}")
                    
            except Exception as e:
                self.logger.error(f"Error in research level {level}: {e}")
                # Continue to next level or fail gracefully
    
    async def _get_agent_for_level(self, level: ResearchLevel) -> Optional[Dict[str, Any]]:
        """Get the most suitable agent for a research level."""
        try:
            # Get agents with appropriate capabilities
            agents = self.agents.list_agents(status='active')
            
            # Filter by capability requirements
            required_capabilities = self._get_capabilities_for_level(level)
            
            suitable_agents = []
            for agent in agents:
                agent_capabilities = self.iam.get_agent_capabilities(agent['id'])
                if all(cap in agent_capabilities for cap in required_capabilities):
                    suitable_agents.append(agent)
            
            if not suitable_agents:
                self.logger.warning(f"No suitable agents found for level {level}")
                return None
            
            # Sort by priority and select best
            suitable_agents.sort(key=lambda x: x.get('priority', 0), reverse=True)
            return suitable_agents[0]
            
        except Exception as e:
            self.logger.error(f"Error getting agent for level {level}: {e}")
            return None
    
    def _get_capabilities_for_level(self, level: ResearchLevel) -> List[str]:
        """Get required capabilities for each research level."""
        capability_map = {
            ResearchLevel.BASIC: ["basic_retrieval", "summarization"],
            ResearchLevel.AGGREGATION: ["multi_source_aggregation", "cross_validation"],
            ResearchLevel.SYNTHESIS: ["expert_synthesis", "analysis"],
            ResearchLevel.EXPERT: ["expert_validation", "dossier_creation"]
        }
        return capability_map.get(level, [])
    
    async def _execute_research_level(
        self, 
        level: ResearchLevel, 
        query: str, 
        context: Dict[str, Any], 
        agent: Dict[str, Any]
    ) -> Optional[ResearchResult]:
        """Execute research at a specific level."""
        try:
            # Create research job
            job = self.jobs.create_job(
                slug=f"research-{level}-{int(time.time())}",
                title=f"Research Level {level.value}: {query[:50]}...",
                domain_tags=["research", level.value]
            )
            
            # Use agent orchestrator for task delegation
            async with AgentOrchestrator(agent['id'], "placeholder_key") as orchestrator:
                # Send research task to agent
                task_payload = {
                    "query": query,
                    "level": level.value,
                    "context": context,
                    "job_id": str(job.id)
                }
                
                await orchestrator.bus.send_task(
                    agent['id'], 
                    "RESEARCH", 
                    task_payload
                )
                
                # Wait for result with timeout
                result = await self._wait_for_research_result(job.id, level)
                
                if result:
                    return ResearchResult(
                        level=level,
                        confidence=result.get('confidence', 0.5),
                        answer=result.get('answer', ''),
                        sources=result.get('sources', []),
                        metadata=result.get('metadata', {})
                    )
                else:
                    self.logger.error(f"No result received for level {level}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error executing research level {level}: {e}")
            return None
    
    async def _wait_for_research_result(
        self, 
        job_id: str, 
        level: ResearchLevel
    ) -> Optional[Dict[str, Any]]:
        """Wait for research result from agent."""
        timeout = self.timeout_per_level
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check for result in Redis stream
                if self.stream_manager:
                    messages = await self.stream_manager.get_messages(
                        f"xnai:research_results:{job_id}",
                        count=1
                    )
                    
                    if messages:
                        return messages[0]
                
                # Check job status in database
                job = self.jobs.get_job(job_id)
                if job and job.status == 'completed':
                    # Get result from job metadata
                    return job.metadata.get('result', {})
                
                await asyncio.sleep(2)  # Wait before checking again
                
            except Exception as e:
                self.logger.error(f"Error waiting for result: {e}")
                await asyncio.sleep(2)
        
        self.logger.error(f"Timeout waiting for research result for job {job_id}")
        return None
    
    async def _validate_result(self, result: ResearchResult, level: ResearchLevel) -> bool:
        """Validate research result quality."""
        try:
            # Check confidence threshold
            min_confidence = self.confidence_thresholds[level]
            if result.confidence < min_confidence:
                self.logger.warning(f"Result confidence {result.confidence} below threshold {min_confidence}")
                return False
            
            # Check answer quality
            if not result.answer or len(result.answer.strip()) < 10:
                self.logger.warning("Result answer too short or empty")
                return False
            
            # Check source quality (if available)
            if result.sources:
                valid_sources = [s for s in result.sources if s.get('reliability', 0) > 0.5]
                if len(valid_sources) < 2 and level in [ResearchLevel.AGGREGATION, ResearchLevel.SYNTHESIS]:
                    self.logger.warning("Insufficient reliable sources for aggregation/synthesis level")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating result: {e}")
            return False
    
    async def create_research_dossier(self, query: str) -> Optional[ResearchDossier]:
        """Create final research dossier from all levels."""
        try:
            levels = []
            async for result in self.research_stream(query):
                levels.append(result)
            
            if not levels:
                self.logger.error("No research levels completed successfully")
                return None
            
            # Combine results
            final_answer = self._synthesize_final_answer(levels)
            confidence_score = self._calculate_overall_confidence(levels)
            
            # Create validation report
            validation_report = self._create_validation_report(levels)
            
            dossier = ResearchDossier(
                query=query,
                levels=levels,
                final_answer=final_answer,
                confidence_score=confidence_score,
                created_at=datetime.utcnow(),
                validation_report=validation_report
            )
            
            # Store dossier in database
            await self._store_dossier(dossier)
            
            return dossier
            
        except Exception as e:
            self.logger.error(f"Error creating research dossier: {e}")
            return None
    
    def _synthesize_final_answer(self, levels: List[ResearchResult]) -> str:
        """Synthesize final answer from all research levels."""
        # Use the highest confidence answer as base
        best_result = max(levels, key=lambda x: x.confidence)
        
        # Add context from other levels
        additional_context = []
        for level in levels:
            if level != best_result and level.confidence > 0.7:
                additional_context.append(level.answer)
        
        if additional_context:
            return f"{best_result.answer}\n\nAdditional context: {' '.join(additional_context)}"
        else:
            return best_result.answer
    
    def _calculate_overall_confidence(self, levels: List[ResearchResult]) -> float:
        """Calculate overall confidence score."""
        # Weighted average based on level importance
        weights = {
            ResearchLevel.BASIC: 0.1,
            ResearchLevel.AGGREGATION: 0.2,
            ResearchLevel.SYNTHESIS: 0.3,
            ResearchLevel.EXPERT: 0.4
        }
        
        total_confidence = 0
        total_weight = 0
        
        for level in levels:
            weight = weights.get(level.level, 0.1)
            total_confidence += level.confidence * weight
            total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.5
    
    def _create_validation_report(self, levels: List[ResearchResult]) -> Dict[str, Any]:
        """Create validation report for research dossier."""
        return {
            "levels_completed": len(levels),
            "highest_confidence": max(l.confidence for l in levels),
            "lowest_confidence": min(l.confidence for l in levels),
            "average_confidence": sum(l.confidence for l in levels) / len(levels),
            "sources_count": sum(len(l.sources) for l in levels),
            "validation_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _store_dossier(self, dossier: ResearchDossier):
        """Store research dossier in database."""
        try:
            # This would require the research_dossiers table to be created
            # For now, we'll store in a simple way
            dossier_data = asdict(dossier)
            dossier_data['created_at'] = dossier.created_at.isoformat()
            
            # Store in Redis for quick access
            if self.redis:
                await self.redis.setex(
                    f"xnai:dossier:{hash(dossier.query)}",
                    86400,  # 24 hours
                    json.dumps(dossier_data)
                )
            
            self.logger.info(f"Research dossier stored for query: {dossier.query}")
            
        except Exception as e:
            self.logger.error(f"Error storing dossier: {e}")


# Legacy compatibility - for existing imports
class LegacyEscalationResearcher(EscalationResearcher):
    """Legacy wrapper for backward compatibility."""
    
    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self.logger.warning("LegacyEscalationResearcher is deprecated, use EscalationResearcher directly")