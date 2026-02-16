"""
Xoe-NovAi Query Router
======================
Endpoints for RAG queries and streaming responses.
"""

import time
import json
import logging
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse

from ...schemas import QueryRequest, QueryResponse
from ...core.metrics import (
    record_tokens_generated,
    record_query_processed,
    update_token_rate,
    MetricsTimer,
    response_latency_ms,
    record_error
)
from ...core.logging_config import PerformanceLogger, get_logger
from ...core.circuit_breakers import CircuitBreakerError
from ...core.tier_config import get_current_rag_config, get_current_llm_config, tier_config_factory
from ...core.transaction_logger import transaction_logger

logger = get_logger(__name__)
perf_logger = PerformanceLogger(logger)
router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: Request, query_req: QueryRequest):
    """Synchronous query endpoint with tiered degradation support."""
    # Get services from app state (already initialized during startup)
    services = getattr(request.app.state, 'services', {})
    rag_service = services.get('rag')
    vectorstore = services.get('vectorstore')
    
    # Access global LLM from entrypoint
    from .. import entrypoint as ep
    
    with MetricsTimer(response_latency_ms, endpoint='/query', method='POST'):
        start_time = time.time()
        
        try:
            # Initialize LLM (lazy loading with circuit breaker)
            if ep.llm is None:
                ep.llm = await ep.load_llm_with_circuit_breaker()
            
            # Get current tier configuration
            rag_config = get_current_rag_config()
            llm_config = get_current_llm_config()
            
            # Retrieve context with tier-aware parameters
            sources = []
            context = ""
            if query_req.use_rag and vectorstore and rag_config.retrieval_enabled:
                # Use tier-specific top_k and context limits
                context, sources = await rag_service.retrieve_context(
                    query=query_req.query,
                    top_k=rag_config.top_k,
                    max_context_chars=rag_config.max_context_chars
                )
            
            # Generate prompt
            prompt = rag_service.generate_prompt(query_req.query, context)
            
            # Generate response with tier-aware token limits
            gen_start = time.time()
            
            # Apply tier-based max_tokens override
            effective_max_tokens = min(query_req.max_tokens, llm_config.max_tokens)
            
            response = ep.llm.invoke(
                prompt,
                max_tokens=effective_max_tokens,
                temperature=llm_config.temperature,
                top_p=llm_config.top_p
            )
            gen_duration = time.time() - gen_start
            
            # Metrics
            tokens_approx = len(response.split())
            token_rate = tokens_approx / gen_duration if gen_duration > 0 else 0
            
            record_tokens_generated(tokens_approx)
            record_query_processed(query_req.use_rag)
            update_token_rate(token_rate)
            
            perf_logger.log_token_generation(tokens=tokens_approx, duration_s=gen_duration)
            
            total_duration_ms = (time.time() - start_time) * 1000
            
            # Log tier information for observability
            current_tier = tier_config_factory.get_current_tier()
            logger.info(f"Query processed with tier {current_tier}: max_tokens={effective_max_tokens}, top_k={rag_config.top_k}, context_chars={len(context)}")
            
            # Audit Trail Logging
            await transaction_logger.log_transaction(
                transaction_type="query",
                query=query_req.query,
                response=response,
                sources=sources,
                metrics={
                    "tokens": tokens_approx,
                    "duration_ms": total_duration_ms,
                    "token_rate": token_rate
                },
                metadata={"tier": current_tier}
            )
            
            return QueryResponse(
                response=response,
                sources=sources,
                tokens_generated=tokens_approx,
                duration_ms=round(total_duration_ms, 2),
                token_rate_tps=round(token_rate, 2)
            )
            
        except CircuitBreakerError:
            record_error('circuit_breaker_open', 'llm')
            return JSONResponse(
                status_code=503,
                content={"error": "LLM service unavailable (circuit open)"}
            )
        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_endpoint(request: Request, query_req: QueryRequest):
    """Streaming query endpoint with tiered degradation support."""
    services = getattr(request.app.state, 'services', {})
    rag_service = services.get('rag')
    vectorstore = services.get('vectorstore')
    from .. import entrypoint as ep
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            if ep.llm is None:
                ep.llm = await ep.load_llm_with_circuit_breaker()
            
            # Get current tier configuration
            rag_config = get_current_rag_config()
            llm_config = get_current_llm_config()
            
            sources = []
            context = ""
            if query_req.use_rag and vectorstore and rag_config.retrieval_enabled:
                # Use tier-specific top_k and context limits
                context, sources = await rag_service.retrieve_context(
                    query=query_req.query,
                    top_k=rag_config.top_k,
                    max_context_chars=rag_config.max_context_chars
                )
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\\n\\n"
            
            prompt = rag_service.generate_prompt(query_req.query, context)
            token_count = 0
            gen_start = time.time()
            
            # Apply tier-based max_tokens override
            effective_max_tokens = min(query_req.max_tokens, llm_config.max_tokens)
            
            for token in ep.llm.stream(
                prompt,
                max_tokens=effective_max_tokens,
                temperature=llm_config.temperature,
                top_p=llm_config.top_p
            ):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\\n\\n"
                token_count += 1
                if token_count % 10 == 0:
                    await asyncio.sleep(0.01)
            
            gen_duration = time.time() - gen_start
            latency_ms = gen_duration * 1000
            
            # Log tier information for observability
            current_tier = tier_config_factory.get_current_tier()
            logger.info(f"Stream processed with tier {current_tier}: max_tokens={effective_max_tokens}, top_k={rag_config.top_k}, context_chars={len(context)}")
            
            yield f"data: {json.dumps({'type': 'done', 'tokens': token_count, 'latency_ms': latency_ms})}\\n\\n"
            
            # Audit Trail Logging (Async)
            await transaction_logger.log_transaction(
                transaction_type="stream",
                query=query_req.query,
                response="[STREAMED]", 
                sources=sources,
                metrics={
                    "tokens": token_count,
                    "duration_ms": latency_ms
                },
                metadata={"tier": current_tier}
            )
            
        except CircuitBreakerError:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Circuit open'})}\\n\\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\\n\\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
