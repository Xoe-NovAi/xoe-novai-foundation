import time
import uuid
import logging
from fastapi import Request
from ..core.dependencies import get_redis_client
from ..core.degradation import degradation_manager

logger = logging.getLogger(__name__)

async def query_transaction_log_middleware(request: Request, call_next):
    """
    Middleware to log query transactions to Redis Streams for auditing and recovery.
    """
    # Only log query and stream endpoints
    if not (request.url.path.endswith("/query") or request.url.path.endswith("/stream")):
        return await call_next(request)

    txn_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
    redis = get_redis_client()
    
    start_time = time.time()
    
    # 1. Log Initiation
    try:
        if redis:
            await redis.xadd("xnai_queries", {
                "txn_id": txn_id,
                "path": request.url.path,
                "status": "initiated",
                "tier": str(degradation_manager.current_tier),
                "timestamp": str(start_time)
            }, maxlen=1000)
    except Exception as e:
        logger.warning(f"Failed to log query initiation to Redis: {e}")

    # 2. Process Request
    response = await call_next(request)
    
    # 3. Log Completion
    duration = time.time() - start_time
    try:
        if redis:
            await redis.xadd("xnai_queries", {
                "txn_id": txn_id,
                "status": "completed",
                "status_code": str(response.status_code),
                "duration_ms": str(int(duration * 1000)),
                "timestamp": str(time.time())
            }, maxlen=1000)
    except Exception as e:
        logger.warning(f"Failed to log query completion to Redis: {e}")
        
    return response
