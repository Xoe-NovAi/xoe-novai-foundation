"""
XNAi Curation Manager - Autonomous RAG Orchestrator
===================================================

The central nervous system for the advanced self-evolving RAG stack.
Orchestrates memory, knowledge retrieval (Vector + Graph), and self-correction.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
"""

import anyio
import logging
from typing import Dict, Any, List, Optional
from app.XNAi_rag_app.core.infrastructure.knowledge_client import KnowledgeClient
from app.XNAi_rag_app.core.agent_memory import AgentMemory, LocalMemoryProvider
from app.XNAi_rag_app.core.curation.evaluator import CurationEvaluator
from app.XNAi_rag_app.core.curation.rewriter import QueryRewriter
from app.XNAi_rag_app.core.curation.optimizer import PromptOptimizer
from app.XNAi_rag_app.core.openpipe_integration import openpipe_manager
from app.XNAi_rag_app.core.curation.wisdom import WisdomProvider, AgentLesson

logger = logging.getLogger(__name__)

class CurationManager:
    """
    Orchestrates the advanced RAG inner loop.
    """

    def __init__(self, knowledge_client: KnowledgeClient, model_func=None, db_pool=None):
        self.knowledge = knowledge_client
        self.memory = AgentMemory(LocalMemoryProvider()) # Fallback to local
        self.evaluator = CurationEvaluator(model_func)
        self.rewriter = QueryRewriter(model_func)
        self.optimizer = PromptOptimizer()
        self.wisdom = WisdomProvider(db_pool)
        self.confidence_threshold = 0.95
        self.max_rounds = 3

    async def processed_query(self, query: str, agent_id: str, session_id: str, domain: str = "general") -> Dict[str, Any]:
        """
        Execute a full agentic RAG loop with recursive research and shared wisdom: 
        Wisdom Recall -> Optimizer -> Retrieval -> Evaluator -> [Recursive Research] -> Wisdom Publish -> Synthesis
        """
        # 0. Recall Shared Wisdom
        lessons = await self.wisdom.recall_similar_wisdom(query, domain)
        wisdom_context = "\n".join([f"Lesson: {l.lesson_learned}" for l in lessons])
        
        # 1. Optimize Prompt
        optimized_query = self.optimizer.get_optimized_prompt(query, f"{agent_id}_query")
        if wisdom_context:
            optimized_query = f"PAST LESSONS:\n{wisdom_context}\n\nCURRENT QUERY: {optimized_query}"
        
        current_query = optimized_query
        results = []
        eval_res = None
        
        # 2. Recursive Research Loop (3-Round Rule)
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"Round {round_num}: Processing query for {agent_id}")
            
            # Snapshot state
            await self.memory.snapshot(agent_id, session_id, {
                "query": current_query, 
                "round": round_num,
                "status": "searching"
            })

            # Hybrid Retrieval (Vector + Graph)
            results = await self.knowledge.search(current_query)
            context_chunks = [r.content for r in results]

            # Evaluate Context (95% Confidence Threshold)
            eval_res = await self.evaluator.evaluate_context(current_query, context_chunks)
            
            if eval_res.score >= self.confidence_threshold:
                logger.info(f"High confidence ({eval_res.score}) reached in round {round_num}")
                
                # 2.1 Publish successful lesson
                if round_num > 1: # Only publish if we actually learned something new
                    await self.wisdom.publish_lesson(AgentLesson(
                        agent_id=agent_id,
                        lesson_learned=f"Found accurate info for '{query}' by searching for '{current_query}'",
                        domain=domain,
                        confidence_score=eval_res.score
                    ))
                break
            
            if round_num < self.max_rounds:
                logger.warning(f"Confidence {eval_res.score} below threshold. Triggering discovery round...")
                await self._trigger_discovery(current_query, agent_id)
                rewritten = await self.rewriter.rewrite(current_query)
                current_query = rewritten[0]
        
        # 3. Final State Snapshot
        await self.memory.snapshot(agent_id, session_id, {
            "final_query": current_query, 
            "result_count": len(results),
            "final_score": eval_res.score if eval_res else 0,
            "status": "completed"
        })

        return {
            "query": current_query,
            "results": [r.to_dict() for r in results],
            "evaluation": eval_res.__dict__ if eval_res else {},
            "session_id": session_id,
            "rounds_completed": round_num
        }

    async def _trigger_discovery(self, query: str, agent_id: str):
        """
        Placeholder for triggering the Agent Bus to perform deep research.
        """
        logger.info(f"Discovery round triggered for: {query}")
        # In production, this would send a message to xnai:jobs:crawler:pending

    async def ingest_manual(self, content: str, metadata: Dict[str, Any]):
        """
        Index a new manual into both Vector and Graph databases.
        """
        # Vector index
        await self.knowledge.add_document(content, metadata)
        
        # Graph index (incremental)
        if hasattr(self.knowledge, "_lightrag_client") and self.knowledge._use_lightrag:
            await self.knowledge._lightrag_client.insert(content)
            logger.info("Document indexed in Knowledge Graph")
