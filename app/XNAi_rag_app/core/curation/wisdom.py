"""
XNAi Shared Wisdom - Inter-Agent Procedural Learning
=====================================================

Provides an interface for agents to publish and recall "Lessons Learned".
Allows cross-domain evolution (e.g., Jungian Expert learning from FastAPI Expert).
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AgentLesson:
    agent_id: str
    lesson_learned: str
    domain: str
    confidence_score: float
    metadata: Dict[str, Any] = None
    created_at: Optional[datetime] = None

@dataclass
class ModelIntelligence:
    model_id: str
    parameter_base: str
    strengths: List[str]
    lessons_learned: str
    task_success_rate: float = 0.0

class WisdomProvider:
    """
    Manages the shared wisdom repository in Postgres.
    """

    def __init__(self, pool=None):
        self.pool = pool

    async def record_model_intel(self, intel: ModelIntelligence) -> bool:
        """
        Record model-specific strengths and lessons from high-reasoning escalations.
        """
        if not self.pool:
            return False
        
        query = """
        INSERT INTO expert_system.model_intelligence (model_id, parameter_base, strengths, lessons_learned, task_success_rate)
        VALUES (%s, %s, %s, %s, %s);
        """
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cur:
                cur.execute(query, (intel.model_id, intel.parameter_base, json.dumps(intel.strengths), intel.lessons_learned, intel.task_success_rate))
            conn.commit()
            self.pool.putconn(conn)
            return True
        except Exception as e:
            logger.error(f"Failed to record model intel: {e}")
            return False

    async def publish_lesson(self, lesson: AgentLesson) -> bool:
        """
        Store a new lesson in the expert_system.shared_wisdom table.
        """
        if not self.pool:
            logger.warning("No DB pool available for Shared Wisdom")
            return False

        query = """
        INSERT INTO expert_system.shared_wisdom (agent_id, lesson_learned, domain, confidence_score)
        VALUES (%s, %s, %s, %s);
        """
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cur:
                cur.execute(query, (lesson.agent_id, lesson.lesson_learned, lesson.domain, lesson.confidence_score))
            conn.commit()
            self.pool.putconn(conn)
            logger.info(f"Agent {lesson.agent_id} published a new lesson in {lesson.domain}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish wisdom: {e}")
            return False

    async def recall_similar_wisdom(self, query: str, domain: Optional[str] = None) -> List[AgentLesson]:
        """
        Retrieve relevant lessons based on semantic similarity or domain.
        Note: In v4.0 baseline, this is a simple domain-based recall.
        Future: Integrate with KnowledgeClient for semantic search over lessons.
        """
        if not self.pool:
            return []

        query_str = "SELECT agent_id, lesson_learned, domain, confidence_score, created_at FROM expert_system.shared_wisdom"
        params = []
        if domain:
            query_str += " WHERE domain = %s"
            params.append(domain)
        query_str += " ORDER BY confidence_score DESC LIMIT 5;"

        try:
            conn = self.pool.getconn()
            with conn.cursor() as cur:
                cur.execute(query_str, params)
                rows = cur.fetchall()
            self.pool.putconn(conn)
            return [AgentLesson(agent_id=r[0], lesson_learned=r[1], domain=r[2], confidence_score=float(r[3]), created_at=r[4]) for r in rows]
        except Exception as e:
            logger.error(f"Failed to recall wisdom: {e}")
            return []
