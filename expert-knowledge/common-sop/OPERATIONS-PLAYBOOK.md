# Common SOPs - Shared by All Agents

## Redis Operations Playbook

### Redis Connection & Auth
```bash
# Connect with authentication
redis-cli -a changeme123

# Verify connection
PING  # Should return PONG

# Check memory usage
INFO memory

# Check key count by category
SCAN 0 MATCH "xnai:*" COUNT 100
```

### Standard Key Patterns

**Session Context**
```
xnai:session:{session_id}:trace_id = "uuid"
xnai:session:{session_id}:conductor_state = JSON
xnai:session:{session_id}:agent_assignments = JSON
```

**Agent State**
```
xnai:agent:{agent_id}:status = "idle|busy|error"
xnai:agent:{agent_id}:current_task = JSON
xnai:agent:{agent_id}:last_heartbeat = "2026-02-16T21:00:00Z"
xnai:agent:{agent_id}:capability_score = "0.95"
```

**Job Queue**
```
xnai:jobs:critical:pending = [task_ids...]
xnai:jobs:normal:pending = [task_ids...]
xnai:jobs:deferred:pending = [task_ids...]

xnai:jobs:{task_id}:definition = JSON (full task spec)
xnai:jobs:{task_id}:result = JSON (after completion)
xnai:jobs:{task_id}:status = "pending|running|complete|failed"
```

**Execution Tracking**
```
xnai:execution:{session_id}:timeline = JSON (phase transitions)
xnai:execution:{session_id}:metrics = JSON (performance data)
xnai:execution:{session_id}:blockers = [blocker_ids...] (current blockers)
```

### Common Commands

```bash
# Check job queue
LRANGE xnai:jobs:critical:pending 0 -1
LLEN xnai:jobs:normal:pending

# Set session state
SET xnai:session:{id}:conductor_state '{"phase": "B", "agents": []}'

# Update agent heartbeat
SET xnai:agent:{id}:last_heartbeat "2026-02-16T21:15:00Z"

# Get all agent statuses
KEYS xnai:agent:*:status
MGET xnai:agent:{id1}:status xnai:agent:{id2}:status

# Monitor key changes
MONITOR  # Real-time key operations
```

### Troubleshooting

**Redis Not Responding**
```bash
# Check service status
docker-compose ps redis

# View logs
docker-compose logs redis | tail -50

# Restart Redis (last resort)
docker-compose restart redis
```

**Memory Getting Full**
```bash
# Check memory stats
INFO memory

# If > 80% used:
1. Identify large keys: SCAN 0 MATCH "*" TYPE string
2. Archive old sessions: KEYS "xnai:session:*" (filter by date)
3. Delete archived: DEL {old_keys}
4. Verify: INFO memory
```

---

## Consul Service Discovery Playbook

### Service Registration Pattern
```
Agent registers when starting:
POST /v1/agent/service/register
{
  "ID": "{agent_id}",
  "Name": "xnai-agent-{type}",
  "Tags": ["xnai", "{agent_type}", "{status}"],
  "Address": "localhost",
  "Port": 8000,
  "Check": {
    "HTTP": "http://localhost:8000/health",
    "Interval": "10s",
    "Timeout": "5s"
  }
}
```

### Service Discovery
```bash
# List all registered services
curl http://localhost:8500/v1/catalog/services

# Check specific service health
curl http://localhost:8500/v1/catalog/service/{service_name}

# Get agent status
curl http://localhost:8500/v1/agent/self
```

### Dependency Tracking
```
When agent completes work:
PUT /v1/kv/xnai/dependencies/{task_id}
Value: {
  "completed_by": "{agent_id}",
  "timestamp": "2026-02-16T21:00:00Z",
  "depends_on": ["{task_id1}", "{task_id2}"],
  "status": "ready_for_next_phase"
}
```

---

## Vikunja Task Management Playbook

### Task Creation via API
```bash
curl -X POST http://localhost:8000/vikunja/api/v1/tasks \
  -H "Authorization: Bearer {token}" \
  -d '{
    "title": "Phase C: Create Agent KBs",
    "description": "Synthesize expert knowledge bases for all agents",
    "priority": 2,
    "list_id": 1,
    "due_date": "2026-02-17T21:00:00Z",
    "assignments": [{"id": "agent:gemini"}]
  }'
```

### Task Status Updates
```bash
# Mark task complete
curl -X PUT http://localhost:8000/vikunja/api/v1/tasks/{task_id} \
  -d '{"done": true, "done_at": "2026-02-16T22:00:00Z"}'

# Add checklist items (subtasks)
curl -X POST http://localhost:8000/vikunja/api/v1/tasks/{task_id}/checklist \
  -d '[
    {"title": "Create Copilot KB", "done": true},
    {"title": "Create Gemini KB", "done": false}
  ]'
```

### Task Querying
```bash
# Get all incomplete Phase C tasks
curl "http://localhost:8000/vikunja/api/v1/tasks/search?query=Phase+C&done=false"

# Get tasks assigned to agent
curl "http://localhost:8000/vikunja/api/v1/tasks?assigned_user=agent:gemini"
```

---

## Ed25519 Identity Handshake Protocol

### Agent Identity Initialization
```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# Generate identity keypair (do once, save securely)
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Store in secure config
config = {
    "agent_id": "copilot:haiku:001",
    "private_key": private_key.private_bytes(...),  # Store in env/vault
    "public_key": public_key.public_bytes(...)
}
```

### Message Signing (Agent → Agent)
```python
# Agent A sends message to Agent B
message = {
    "from": "copilot:haiku:001",
    "to": "gemini:pro:001",
    "task_id": "task_12345",
    "payload": {...}
}

# Sign with private key
signature = private_key.sign(json.dumps(message).encode())

# Send with signature
transmission = {
    "message": message,
    "signature": signature.hex(),
    "public_key": public_key_hex
}
```

### Message Verification (Agent B receives)
```python
# Agent B verifies signature
from cryptography.hazmat.primitives.asymmetric import ed25519

public_key = ed25519.Ed25519PublicKey.from_public_bytes(
    bytes.fromhex(transmission["public_key"])
)

try:
    public_key.verify(
        bytes.fromhex(transmission["signature"]),
        json.dumps(transmission["message"]).encode()
    )
    # ✅ Signature valid, message authentic
except:
    # ❌ Signature invalid, reject message
    raise AuthenticationError("Invalid agent signature")
```

---

## Error Handling & Recovery

### Standard Exception Hierarchy
```python
XNAiException (base)
├─ TaskRoutingError
├─ AgentCommunicationError
├─ RedisError
├─ ConsulError
├─ VectorSearchError
└─ ValidationError
```

### Error Response Format
```json
{
  "error_code": "TASK_ROUTING_FAILED",
  "message": "No suitable agent found for score 7.5",
  "trace_id": "uuid",
  "span_id": "uuid",
  "timestamp": "2026-02-16T21:00:00Z",
  "context": {
    "task_id": "task_123",
    "attempted_routing": ["copilot", "gemini"],
    "blockers": ["Agent capacity exceeded", "Redis timeout"]
  }
}
```

### Recovery Procedures

**Redis Connection Lost**
1. Log error with trace_id
2. Retry with exponential backoff (100ms, 200ms, 400ms)
3. If persistent, store to fallback queue (disk JSON)
4. Alert conductor via Consul health check

**Agent Not Responding**
1. Check Consul health status
2. If unhealthy: mark agent offline, requeue task
3. Escalate to Copilot for alternate routing
4. After 3 failures: escalate to human review

**Vector Search Timeout**
1. Fall back to FAISS local index
2. If FAISS also fails: use keyword search
3. Return best-effort results with degraded flag
4. Alert team for performance investigation

---

## Monitoring & Health Checks

### Agent Health Status
```bash
# Every 30 seconds, each agent sends:
GET /health
{
  "agent_id": "copilot:haiku:001",
  "status": "healthy|degraded|unhealthy",
  "metrics": {
    "cpu_percent": 45.2,
    "memory_mb": 1250,
    "response_latency_ms": 250,
    "tasks_completed_hour": 12
  },
  "timestamp": "2026-02-16T21:00:00Z"
}
```

### Performance SLAs
- Task routing decision: < 100ms
- Agent health check: < 1s
- Vector search query: < 500ms
- Vikunja task sync: < 2s
- Message signing/verification: < 50ms

### Alerting
Alert conditions (stored in Consul):
- Agent unhealthy: > 30s without heartbeat
- Memory pressure: > 90% of host available
- Latency spike: > 2x SLA baseline
- Error rate: > 5% of operations

---

## Zero-Telemetry Enforcement

### What's Allowed
- Local logging to files/Redis
- Metrics to internal Prometheus (if deployed)
- Health checks to internal Consul
- Task results to Redis/Vikunja

### What's NOT Allowed
- External cloud logging (no Google Cloud Logging, DataDog, etc.)
- External error tracking (no Sentry, Rollbar)
- External analytics (no Mixpanel, Amplitude)
- External APM (no New Relic, Datadog APM)

### Verification Command
```bash
# Check for external API calls
docker-compose exec {service} netstat -an | grep ESTABLISHED | grep -v 127.0.0.1 | grep -v 172.

# Should show only internal Docker network (172.x.x.x to other containers)
# If any external IPs: investigate and document approval
```

---

**Last Updated**: 2026-02-16T21:00:00Z
**Maintained By**: XNAi Ops Team
**Review Cycle**: Monthly
