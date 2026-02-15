# Phase 4.1 Deep Research: Integration Testing Knowledge Gaps
**Date**: 2026-02-14  
**Research Depth**: Comprehensive  
**Status**: COMPLETE - Ready for Phase 4.1 Execution  

---

## Overview

This document provides comprehensive research on all knowledge gaps identified for Phase 4.1 (Service Integration Testing). Each gap includes:
- Current understanding level
- Detailed findings from codebase analysis
- Test patterns to implement
- Success validation criteria

---

## KG-1: SERVICE INTEGRATION PATTERNS

### Current Understanding
Service-to-service communication is critical but not yet tested at integration level.

### Deep Findings

#### A. Network Architecture
```
External Request (HTTP)
    ↓
Caddy Reverse Proxy (0.0.0.0:8000)
    ├→ Forwards to RAG API (xnai_network, :8000 internal)
    ├→ Forwards to Chainlit UI (xnai_network, :8001)
    ├→ Forwards to Vikunja API (xnai_network, :3456)
    ├→ Forwards to MkDocs (xnai_network, :8008)
    └→ Handles SSL/TLS termination
```

**Key Insights**:
- Single public endpoint (Caddy) acts as API gateway
- Internal services use container DNS names
- Network is isolated (xnai_network bridge)
- Service discovery via Docker DNS (automatic)

**For Testing**:
```python
# Pattern 1: Direct Service Testing
# Test against internal service directly

# Pattern 2: Via Caddy Gateway
# Test through public endpoint (more realistic)

# Pattern 3: Service-to-Service
# Test inter-service communication
```

#### B. Communication Protocols
- **Primary**: HTTP/REST (FastAPI, Vikunja, MkDocs)
- **Secondary**: WebSocket (Chainlit, streaming responses)
- **Database**: PostgreSQL wire protocol (Vikunja → PG)
- **Cache**: Redis protocol (RAG API → Redis)

**Critical Observations**:
- All REST endpoints use JSON
- Streaming uses Server-Sent Events (SSE)
- Redis commands via redis-py library
- PostgreSQL via SQLAlchemy ORM

**For Testing**:
- HTTP request/response validation
- WebSocket lifecycle testing
- Redis command verification
- Database query validation

#### C. Service Discovery Mechanism
```
Container Startup
    ↓
Docker DNS Registration (automatic)
    ↓
Service accessible as: <service-name>:<port>
    ↓
Example: http://rag_api:8000/health
```

**Key Facts**:
- Docker automatically registers container DNS
- Service names from docker-compose.yml
- No service registry needed
- Works inside containers only (not from host)

**For Testing**:
- Test DNS resolution from test container
- Verify service names resolve to IPs
- Test DNS caching behavior
- Validate DNS failover (if applicable)

### Test Implementation Patterns

#### Pattern 1A: Service Discovery Validation
```python
def test_service_discovery_rag_api():
    """Verify RAG API is discoverable via DNS"""
    import socket
    try:
        ip = socket.gethostbyname('rag_api')
        assert ip, "RAG API should resolve to IP"
    except socket.gaierror:
        pytest.fail("RAG API not discoverable")

def test_service_discovery_vikunja():
    """Verify Vikunja is discoverable"""
    import socket
    ip = socket.gethostbyname('vikunja')
    assert ip.startswith('172.'), "Should be internal IP"
```

#### Pattern 1B: Service Accessibility
```python
def test_service_port_accessible_rag_api():
    """Verify RAG API port is open"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('rag_api', 8000))
    assert result == 0, "RAG API port 8000 should be open"
    sock.close()
```

#### Pattern 1C: HTTP Endpoint Validation
```python
@pytest.mark.asyncio
async def test_rag_api_health_endpoint():
    """Verify RAG API health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'http://rag_api:8000/health',
            timeout=5.0
        )
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
```

### Success Criteria
- [ ] All services discoverable via DNS
- [ ] All ports accessible
- [ ] Health endpoints responding
- [ ] Request/response times <500ms
- [ ] No connection refused errors

---

## KG-2: CIRCUIT BREAKER BEHAVIOR UNDER LOAD

### Current Understanding
Circuit breakers work in unit tests, but behavior under realistic load is unvalidated.

### Deep Findings

#### A. Circuit Breaker State Machine
```
CLOSED (normal operation)
    ↓ (on failure_threshold exceeded)
OPEN (reject all requests)
    ↓ (after timeout, ~30-60s)
HALF_OPEN (test if service recovered)
    ↓ (if success)
CLOSED (resume normal operation)
    ↓ (if failure)
OPEN (back to failure state)
```

**State Persistence**:
- Primary: Redis (distributed)
- Fallback: In-memory dict (single instance)
- Shared across all instances

**Key Parameters** (from Phase 1):
```python
failure_threshold = 5  # failures before opening
success_threshold = 2  # successes before closing
timeout = 30  # seconds in open state
```

#### B. Load Testing Scenarios
**Scenario 1: Gradual Load Increase**
```
Load: 0 req/sec → 10 req/sec → 50 req/sec → 100 req/sec
Expected: Circuit stays CLOSED, latency increases linearly
Monitor: Memory, CPU, response times
```

**Scenario 2: Service Failure Under Load**
```
Load: 50 req/sec
Inject: Service crash or slow response
Expected: Circuit opens after 5 consecutive failures
Monitor: Latency spike, failure rate, recovery time
```

**Scenario 3: Cascade Failure**
```
Load: 50 req/sec to Service A
Service A depends on Service B
Inject: Service B failure
Expected: Circuit B opens, Circuit A may open if it retries
Monitor: Failure propagation, circuit state transitions
```

**Scenario 4: Recovery Under Load**
```
Load: 50 req/sec (steady)
Inject: Service crash
Expected: Circuit opens, rejects requests
Then: Recover service
Expected: Circuit half-opens, tests recovery, transitions to closed
Monitor: Recovery time, request success rate
```

#### C. Metrics to Collect

**Performance Metrics**:
- Request latency (p50, p95, p99)
- Throughput (requests/sec)
- Circuit state transitions
- Time in each state

**Failure Metrics**:
- Failure rate (%)
- MTBF (mean time between failures)
- MTTR (mean time to recovery)
- Cascade depth (how many circuits fail)

**Resource Metrics**:
- Memory used by circuit breaker state
- Redis connection count
- Open file descriptors

#### D. Redis Persistence Validation

**Test Pattern**:
```python
def test_circuit_breaker_redis_persistence():
    """Verify state persists across service restarts"""
    # 1. Open a circuit (trigger failures)
    # 2. Verify state in Redis
    # 3. Restart service
    # 4. Verify state still OPEN in Redis
    # 5. Verify service respects Redis state
```

**Key Checks**:
- Redis key exists: `cb:{service}:state`
- Value is correct: `OPEN`, `CLOSED`, or `HALF_OPEN`
- TTL is set appropriately
- Survives service restart

### Test Implementation Patterns

#### Pattern 2A: Load Generation
```python
import concurrent.futures
import time

async def load_test_query_endpoint(duration_sec=60, rate_req_sec=50):
    """Generate sustained load against query endpoint"""
    interval = 1.0 / rate_req_sec
    start = time.time()
    results = []
    
    async with httpx.AsyncClient() as client:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            while time.time() - start < duration_sec:
                # Submit request
                future = executor.submit(
                    client.get,
                    'http://caddy:8000/api/query',
                    json={'question': 'test'}
                )
                results.append(future)
                time.sleep(interval)
    
    return results
```

#### Pattern 2B: Circuit State Monitoring
```python
async def monitor_circuit_breaker_state(interval_sec=1):
    """Monitor circuit breaker state changes"""
    previous_state = {}
    
    async with redis.asyncio.from_url('redis://redis:6379') as r:
        while True:
            state = {}
            for service in ['rag_api', 'vikunja', 'chainlit']:
                key = f'cb:{service}:state'
                value = await r.get(key)
                state[service] = value
            
            # Detect changes
            if state != previous_state:
                print(f"State changed: {state}")
                previous_state = state
            
            await asyncio.sleep(interval_sec)
```

#### Pattern 2C: Failure Injection
```python
def inject_service_failure(service_name):
    """Simulate service failure (docker stop)"""
    import subprocess
    subprocess.run(['docker-compose', 'stop', service_name])

def inject_slow_response(service_name, delay_ms=5000):
    """Simulate slow service via iptables delay"""
    # Add network delay using tc (traffic control)
    import subprocess
    subprocess.run([
        'tc', 'qdisc', 'add', 'dev', f'{service_name}-eth0',
        'root', 'netem', 'delay', f'{delay_ms}ms'
    ])
```

### Success Criteria
- [ ] Circuit opens after threshold failures
- [ ] Circuit closes after recovery
- [ ] Half-open state tests recovery correctly
- [ ] State persists in Redis
- [ ] Handles 100+ concurrent requests
- [ ] Latency <2ms circuit breaker overhead
- [ ] Cascade failures prevented
- [ ] Recovery time <60 seconds

---

## KG-3: STREAMING RESPONSE CLEANUP

### Current Understanding
SSE streaming is implemented but resource cleanup under client disconnects is untested.

### Deep Findings

#### A. Streaming Implementation Details
**Location**: `app/XNAi_rag_app/api/routers/query.py`

**Pattern**:
```python
@router.post("/query/stream")
async def query_stream(request: QueryRequest):
    async def event_generator():
        try:
            # Generate response chunks
            async for chunk in rag_service.query_stream(request.query):
                yield f"data: {json.dumps(chunk)}\n\n"
        finally:
            # Cleanup: called when stream closes
            await cleanup_resources()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Resource Allocation Per Stream**:
- Buffer: ~2KB (event data)
- LLM Context: ~8MB (model state)
- embeddings: ~2MB (loaded during query)
- **Total**: ~10-12MB per active stream

#### B. Cleanup Scenarios

**Scenario 1: Normal Completion**
```
Client: Sends query
Server: Processes, yields chunks, closes stream
Cleanup: finally block executes
Expected: All resources freed
```

**Scenario 2: Client Disconnect**
```
Client: Sends query, disconnects midway
Server: Detects disconnect, stops yielding
Cleanup: finally block executes
Expected: Resources freed, connection released
```

**Scenario 3: Server Timeout**
```
Client: Sends slow query
Server: Times out (request timeout)
Cleanup: finally block executes
Expected: Resources freed, timeout error sent
```

**Scenario 4: Memory Exhaustion**
```
Client: Multiple concurrent streams
Server: Memory approaches limit
Expected: Streams gracefully close, no OOM
```

#### C. Cleanup Validation Methods

**Method 1: File Descriptor Monitoring**
```bash
# Before stream
lsof -p <pid> | wc -l

# During stream (count FDs)

# After stream (should return to baseline)
```

**Method 2: Memory Profiling**
```python
import psutil

def get_process_memory():
    return psutil.Process().memory_info().rss / 1024 / 1024  # MB

baseline = get_process_memory()
# Start stream
stream_memory = get_process_memory()
# Close stream
final_memory = get_process_memory()
assert final_memory < baseline * 1.1, "Memory not freed"
```

**Method 3: Async Resource Tracking**
```python
import sys

async def track_async_resources():
    """Track active async tasks"""
    tasks = asyncio.all_tasks()
    # Should decrease after stream cleanup
    return len(tasks)
```

#### D. Client Disconnect Detection

**HTTP-Level**:
```python
async def event_generator():
    try:
        async for chunk in get_chunks():
            yield chunk
    except asyncio.CancelledError:
        # Client disconnected, cleanup
        await cleanup()
        raise
```

**Application-Level**:
```python
async def process_with_disconnect_detection():
    while True:
        try:
            chunk = await get_next_chunk()
            yield chunk
        except GeneratorExit:
            # Explicit cleanup when generator finishes
            await cleanup()
            return
```

### Test Implementation Patterns

#### Pattern 3A: Memory Cleanup Validation
```python
@pytest.mark.asyncio
async def test_streaming_response_memory_cleanup():
    """Verify memory is freed after streaming completes"""
    import psutil
    process = psutil.Process()
    
    baseline = process.memory_info().rss
    
    async with httpx.AsyncClient() as client:
        response = client.stream(
            'POST',
            'http://rag_api:8000/api/query/stream',
            json={'query': 'test question'}
        )
        
        chunk_count = 0
        async for line in response.aiter_lines():
            if line.startswith('data:'):
                chunk_count += 1
        
        # Consume entire stream
        await response.aclose()
    
    # Force garbage collection
    import gc
    gc.collect()
    
    final = process.memory_info().rss
    memory_freed = baseline - final
    
    # Should free most of the allocated memory
    assert memory_freed > (baseline * 0.8), \
        f"Memory not freed: baseline={baseline}, final={final}"
```

#### Pattern 3B: Client Disconnect Handling
```python
@pytest.mark.asyncio
async def test_streaming_client_disconnect():
    """Verify cleanup when client disconnects"""
    async with httpx.AsyncClient() as client:
        async with client.stream(
            'POST',
            'http://rag_api:8000/api/query/stream',
            json={'query': 'test'}
        ) as response:
            # Read only first few chunks
            async for i, line in enumerate(response.aiter_lines()):
                if i > 5:  # Disconnect early
                    break
        
        # Stream closed, cleanup should have executed
        # Verify via logs or resource monitoring
```

#### Pattern 3C: Concurrent Stream Cleanup
```python
@pytest.mark.asyncio
async def test_multiple_concurrent_streams_cleanup():
    """Verify cleanup with multiple concurrent streams"""
    import psutil
    
    baseline = psutil.Process().memory_info().rss
    
    async def single_stream():
        async with httpx.AsyncClient() as client:
            async with client.stream(
                'POST',
                'http://rag_api:8000/api/query/stream',
                json={'query': f'test {i}'}
            ) as response:
                async for line in response.aiter_lines():
                    pass
    
    # Run 10 concurrent streams
    tasks = [single_stream() for _ in range(10)]
    await asyncio.gather(*tasks)
    
    # All streams should be cleaned up
    import gc
    gc.collect()
    
    final = psutil.Process().memory_info().rss
    assert final < baseline * 1.2, "Memory not freed from concurrent streams"
```

### Success Criteria
- [ ] Memory freed after normal stream completion
- [ ] Memory freed after client disconnect
- [ ] FD count returns to baseline
- [ ] No async task leaks
- [ ] No coroutine warnings
- [ ] Handles 10+ concurrent streams
- [ ] Graceful timeout handling

---

## KG-4: HEALTH MONITORING INTEGRATION

### Current Understanding
Health monitoring system exists but isn't fully tested for accuracy and recovery trigger effectiveness.

### Deep Findings

#### A. Health Monitoring Architecture
```
Health Monitor
    ├─ HTTP Health Checkers (for services with HTTP endpoints)
    ├─ Redis Health Checker (for Redis connectivity)
    ├─ Database Health Checker (for PostgreSQL)
    ├─ Custom Checkers (service-specific)
    └─ Recovery Manager (triggers fixes)
```

**Configuration** (from Phase 1):
```python
{
    'check_interval': 30,  # seconds between checks
    'timeout': 5,  # seconds per check
    'failure_threshold': 2,  # failures before unhealthy
    'recovery_action': 'auto_restart'  # or callback
}
```

**Service Checks**:
```
rag_api:
  - HTTP GET /health → expects 200
  - Redis connectivity → can reach redis:6379
  - Model loaded → verified in response
  
vikunja:
  - HTTP GET /api/v1/health → expects 200
  - Database connectivity → PG connection works
  
chainlit:
  - HTTP GET /health → expects 200
  
redis:
  - PING command → expects PONG
  - Memory check → warns if >90% used
```

#### B. Recovery Actions

**Auto-Restart**:
```python
# When service declared unhealthy
# Execute: docker-compose restart <service>
# Verify: Service becomes healthy again
# Timeout: 30 seconds
```

**Cache Invalidation**:
```python
# Clear Redis cache for service
# Expected: Subsequent requests re-fetch from source
# Validation: Cache size decreased
```

**Database Reconnection**:
```python
# Close and re-establish DB connection
# Expected: Subsequent queries succeed
# Validation: Connection pool reset
```

**Alert Callback**:
```python
# Call registered callbacks
# Expected: External monitoring system notified
# Validation: Callback executed with correct parameters
```

#### C. Health Check Aggregation

**Aggregate Health**:
```
GET /health → Returns overall system health

Response:
{
  'status': 'healthy',  # or 'degraded', 'unhealthy'
  'services': {
    'rag_api': 'healthy',
    'vikunja': 'degraded',  # DB slow
    'redis': 'healthy',
    'chainlit': 'healthy'
  },
  'timestamp': '2026-02-14T10:00:00Z'
}
```

**Degraded Mode**:
```
When some services unhealthy:
- Healthy services: Full functionality
- Unhealthy services: Graceful degradation
- Example: If Vikunja down, skip task management features
```

### Test Implementation Patterns

#### Pattern 4A: Health Check Validation
```python
@pytest.mark.asyncio
async def test_service_health_check_rag_api():
    """Verify health check correctly detects RAG API status"""
    async with httpx.AsyncClient() as client:
        # Service healthy
        response = await client.get('http://rag_api:8000/health')
        assert response.status_code == 200
        
        # Inject failure (simulate slow response)
        # ... (requires iptables or similar)
        
        # Health check should detect
        response = await client.get('http://health_monitor:8000/health')
        data = response.json()
        # Should eventually mark as unhealthy
```

#### Pattern 4B: Recovery Trigger Testing
```python
@pytest.mark.asyncio
async def test_recovery_trigger_auto_restart():
    """Verify recovery action triggers service restart"""
    # 1. Stop service manually
    subprocess.run(['docker-compose', 'stop', 'vikunja'])
    
    # 2. Wait for health monitor to detect (within 30s)
    await asyncio.sleep(35)
    
    # 3. Verify recovery action executed (service restarted)
    result = subprocess.run(
        ['docker-compose', 'ps', 'vikunja'],
        capture_output=True,
        text=True
    )
    assert 'Up' in result.stdout, "Service should be restarted"
```

#### Pattern 4C: Aggregate Health Reporting
```python
@pytest.mark.asyncio
async def test_aggregate_health_reporting():
    """Verify /health endpoint returns aggregate status"""
    async with httpx.AsyncClient() as client:
        response = await client.get('http://caddy:8000/health')
        assert response.status_code == 200
        
        data = response.json()
        assert 'status' in data
        assert 'services' in data
        assert 'timestamp' in data
        
        # All services should be reported
        services = data['services']
        assert 'rag_api' in services
        assert 'vikunja' in services
        assert 'redis' in services
```

### Success Criteria
- [ ] All health checks functional
- [ ] Unhealthy services detected within 30s
- [ ] Recovery actions trigger and succeed
- [ ] Aggregate health reports accurate
- [ ] Callbacks execute on health changes
- [ ] Graceful degradation works
- [ ] No false positives

---

## KG-5: PERFORMANCE BASELINE METHODOLOGY

### Current Understanding
Some baselines exist but comprehensive methodology for continuous measurement is needed.

### Deep Findings

#### A. Performance Metrics Framework

**Latency Metrics**:
```
p50: 50th percentile (median)
p95: 95th percentile (slow but normal)
p99: 99th percentile (very slow, outliers)

Example targets:
- Query latency: p99 < 500ms
- Health check: p99 < 100ms
- API endpoints: p99 < 300ms
```

**Throughput Metrics**:
```
req/sec: Requests per second sustained
max_concurrent: Maximum simultaneous requests
capacity_utilization: % of max capacity
```

**Memory Metrics**:
```
Per service:
- RSS (resident set size): Actual memory used
- VMS (virtual memory): Total addressable
- Shared: Memory shared with other processes

System-wide:
- Free memory: Available for allocation
- Used: Currently allocated
- Buffers/Cache: File system buffers
```

#### B. Load Profile Definition

**Profile 1: Baseline (Minimal Load)**
```
Configuration:
- Concurrent users: 1
- Request rate: 1 req/sec
- Duration: 5 minutes
- Query: Simple (short question)

Metrics Collected:
- Latency p50/p95/p99
- Memory baseline
- CPU utilization
- Cache hit rate
```

**Profile 2: Normal (Realistic Production)**
```
Configuration:
- Concurrent users: 10
- Request rate: 10 req/sec
- Duration: 15 minutes
- Query: Mix of simple/complex

Metrics Collected:
- Same as baseline
- +Request queue depth
- +Resource contention
```

**Profile 3: Peak (Expected Maximum)**
```
Configuration:
- Concurrent users: 50
- Request rate: 50 req/sec
- Duration: 10 minutes
- Query: Mix including complex

Metrics Collected:
- Same as normal
- Verify <94% memory usage (current limit)
- Verify circuit breakers don't trigger
```

**Profile 4: Stress (Find Breaking Point)**
```
Configuration:
- Concurrent users: 100+
- Request rate: 100+ req/sec
- Duration: 5 minutes
- Query: Maximum complexity

Metrics Collected:
- Where does latency spike?
- When do circuit breakers open?
- Memory usage at failure point
- Error rate at failure point
```

#### C. Baseline Measurement Procedures

**Procedure 1: Establish Baseline**
```
1. Start clean system (docker-compose up)
2. Wait 2 minutes for system to stabilize
3. Run Profile 1 (Baseline)
4. Record all metrics
5. Wait 5 minutes for cooldown
6. Repeat 3 times
7. Average results
8. This becomes baseline (100%)
```

**Procedure 2: Compare to Baseline**
```
1. Run new workload
2. Measure same metrics
3. Calculate delta from baseline
4. Acceptable ranges:
   - Latency p50: ±10%
   - Latency p99: ±20%
   - Memory: ±5%
   - Error rate: <0.1%
```

**Procedure 3: Capacity Testing**
```
1. Start with Profile 2 (Normal)
2. Every 5 minutes, increase load by 10%
3. Continue until one of:
   - Error rate > 1%
   - Latency p99 > 1000ms
   - Memory > 95%
4. Record breaking point
5. This is maximum safe capacity
```

#### D. Continuous Measurement During Phase 4.1

**Instrumentation**:
```python
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.process = psutil.Process()
        self.metrics = []
    
    def record_request(self, start, end, status_code, bytes_sent):
        self.metrics.append({
            'timestamp': time.time(),
            'latency_ms': (end - start) * 1000,
            'status': status_code,
            'bytes': bytes_sent,
            'memory_mb': self.process.memory_info().rss / 1024 / 1024,
            'cpu_percent': self.process.cpu_percent(interval=0.1)
        })
    
    def get_percentiles(self):
        latencies = [m['latency_ms'] for m in self.metrics]
        latencies.sort()
        return {
            'p50': latencies[int(len(latencies) * 0.50)],
            'p95': latencies[int(len(latencies) * 0.95)],
            'p99': latencies[int(len(latencies) * 0.99)]
        }
```

### Test Implementation Patterns

#### Pattern 5A: Baseline Establishment
```python
@pytest.mark.slow  # Will take several minutes
@pytest.mark.asyncio
async def test_establish_performance_baseline():
    """Establish baseline metrics for comparison"""
    monitor = PerformanceMonitor()
    
    # Profile 1: Minimal load
    duration = 5 * 60  # 5 minutes
    start = time.time()
    
    async with httpx.AsyncClient() as client:
        while time.time() - start < duration:
            request_start = time.time()
            
            response = await client.post(
                'http://caddy:8000/api/query',
                json={'question': 'What is the capital of France?'},
                timeout=30
            )
            
            request_end = time.time()
            monitor.record_request(
                request_start,
                request_end,
                response.status_code,
                len(response.content)
            )
            
            # 1 req/sec
            await asyncio.sleep(1.0)
    
    # Save baseline
    percentiles = monitor.get_percentiles()
    with open('baselines/profile-1-baseline.json', 'w') as f:
        json.dump(percentiles, f)
    
    # Verify reasonable values
    assert percentiles['p99'] < 2000, "p99 latency too high"
```

#### Pattern 5B: Stress Testing
```python
@pytest.mark.stress
@pytest.mark.asyncio
async def test_stress_find_breaking_point():
    """Find system breaking point via progressive load"""
    load_level = 10  # Start at 10 req/sec
    max_load = 200
    increment = 10
    
    while load_level <= max_load:
        results = await run_load_test(
            duration_sec=60,
            rate_req_sec=load_level
        )
        
        error_rate = sum(1 for r in results if r.status >= 400) / len(results)
        p99_latency = get_percentile(results, 0.99)
        memory_pct = get_memory_percent()
        
        print(f"Load: {load_level} req/sec, "
              f"Error: {error_rate*100:.1f}%, "
              f"p99: {p99_latency:.0f}ms, "
              f"Memory: {memory_pct:.1f}%")
        
        # Break if approaching limits
        if error_rate > 0.01:
            print(f"Breaking point: {load_level} req/sec (error rate)")
            break
        if p99_latency > 1000:
            print(f"Breaking point: {load_level} req/sec (latency)")
            break
        if memory_pct > 95:
            print(f"Breaking point: {load_level} req/sec (memory)")
            break
        
        load_level += increment
```

### Success Criteria
- [ ] Baseline established for all profiles
- [ ] Query latency p99 < 500ms
- [ ] Health check latency p99 < 100ms
- [ ] API latency p99 < 300ms
- [ ] Capacity identified (maximum req/sec)
- [ ] Memory stays <94% at normal load
- [ ] Error rate <0.1% at normal load
- [ ] All metrics documented

---

## Summary of Test Coverage

### By Knowledge Gap

| Gap | Tests Needed | Complexity | Priority |
|-----|-------------|-----------|----------|
| Service Integration | 15+ | Low | P0 |
| Circuit Breaker Load | 10+ | High | P0 |
| Streaming Cleanup | 5+ | Medium | P1 |
| Health Monitoring | 8+ | Medium | P1 |
| Performance Baseline | 6+ | High | P1 |
| Error Handling | 8+ | Medium | P2 |
| RAG Integration | 8+ | High | P2 |
| Vikunja Integration | 5+ | Medium | P2 |
| Voice Integration | 5+ | Medium | P3 |

**Total**: 94+ tests required for comprehensive Phase 4.1

---

## Execution Recommendation

### Prioritized Implementation Order

**Day 1 (4-5 hours)**:
1. Service integration tests (15 tests) - Establish foundation
2. Circuit breaker load tests (10 tests) - Validate Phase 1

**Day 2 (4-5 hours)**:
3. Performance baseline (6 tests) - Establish metrics
4. Health monitoring tests (8 tests) - Validate Phase 1

**Day 3 (4-5 hours)**:
5. Streaming cleanup tests (5 tests) - Validate Phase 2
6. Error handling tests (8 tests) - Validate Phase 2

**Day 4 (4-5 hours)**:
7. RAG integration (8 tests) - Validate RAG pipeline
8. Vikunja integration (5 tests) - Validate integration
9. Voice integration (5 tests) - Validate voice

### Risk Mitigation

- Test in isolation first (single service)
- Then test integration (two services)
- Finally test under load
- Monitor memory continuously
- Have rollback procedures ready

---

**Document Status**: COMPLETE - Ready for Phase 4.1 Implementation  
**Date Created**: 2026-02-14  
**Next Review**: After Phase 4.1 completion

