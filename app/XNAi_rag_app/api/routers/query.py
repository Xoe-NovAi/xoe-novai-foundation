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

from XNAi_rag_app.schemas import QueryRequest, QueryResponse
from XNAi_rag_app.core.metrics import (
    record_tokens_generated,
    record_query_processed,
    update_token_rate,
    MetricsTimer,
    response_latency_ms,
    record_error
)
from XNAi_rag_app.core.logging_config import PerformanceLogger, get_logger
from XNAi_rag_app.core.circuit_breakers import CircuitBreakerError

logger = get_logger(__name__)
perf_logger = PerformanceLogger(logger)
router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: Request, query_req: QueryRequest):
    """Synchronous query endpoint."""
    services = getattr(request.app.state, 'services', {})
    rag_service = services.get('rag')
    vectorstore = services.get('vectorstore')
    
    # Access global LLM from entrypoint (for now, until Phase 2 is complete)
    # Actually, we should probably move LLM initialization to orchestrator too.
    import XNAi_rag_app.api.entrypoint as ep
    
    with MetricsTimer(response_latency_ms, endpoint='/query', method='POST'):
        start_time = time.time()
        
        try:
            # Initialize LLM (lazy loading with circuit breaker)
            if ep.llm is None:
                ep.llm = ep.load_llm_with_circuit_breaker()
            
            # Retrieve context
            sources = []
            context = ""
            if query_req.use_rag and vectorstore:
                context, sources = await rag_service.retrieve_context(query_req.query)
            
            # Generate prompt
            prompt = rag_service.generate_prompt(query_req.query, context)
            
            # Generate response
            gen_start = time.time()
            response = ep.llm.invoke(
                prompt,
                max_tokens=query_req.max_tokens,
                temperature=query_req.temperature,
                top_p=query_req.top_p
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
    """Streaming query endpoint."""
    services = getattr(request.app.state, 'services', {})
    rag_service = services.get('rag')
    vectorstore = services.get('vectorstore')
    import XNAi_rag_app.api.entrypoint as ep
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            if ep.llm is None:
                ep.llm = ep.load_llm_with_circuit_breaker()
            
            sources = []
            context = ""
            if query_req.use_rag and vectorstore:
                context, sources = await rag_service.retrieve_context(query_req.query)
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\\n\\n"
            
            prompt = rag_service.generate_prompt(query_req.query, context)
            token_count = 0
            gen_start = time.time()
            
            for token in ep.llm.stream(
                prompt,
                max_tokens=query_req.max_tokens,
                temperature=query_req.temperature,
                top_p=query_req.top_p
            ):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\\n\\n"
                token_count += 1
                if token_count % 10 == 0:
                    await asyncio.sleep(0.01)
            
            gen_duration = time.time() - gen_start
            latency_ms = gen_duration * 1000
            yield f"data: {json.dumps({'type': 'done', 'tokens': token_count, 'latency_ms': latency_ms})}\\n\\n"
            
        except CircuitBreakerError:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Circuit open'})}\\n\\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\\n\\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")