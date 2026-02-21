---
block:
  label: unified_execution_strategy
  description: Master strategy for MemGPT architecture, VictoriaMetrics, MCP, and A2A integration
  chars_limit: 15000
  read_only: false
  tier: core
  priority: 1
created: 2026-02-20
modified: 2026-02-20
version: "1.0"
---

# Unified Execution Strategy: MemGPT Memory Architecture

**Status**: Ready for Execution
**Timeline**: 6 Weeks
**Dependencies**: VictoriaMetrics, MCP SDK, A2A SDK

---

## Executive Summary

This strategy unifies four major initiatives into a cohesive implementation plan:

1. **VictoriaMetrics** - Replace Prometheus (3-4x memory savings)
2. **Grafana Dashboards** - Memory bank observability
3. **MCP Server** - Standardized memory access protocol
4. **A2A Protocol** - Agent-to-agent communication

**Key Insight**: These systems form complementary layers:
- **VictoriaMetrics**: Metrics storage (infra layer)
- **Grafana**: Visualization (presentation layer)
- **MCP**: Agent-to-tool communication
- **A2A**: Agent-to-agent communication

---

## Research Synthesis

### VictoriaMetrics Key Findings

| Finding | Implication |
|---------|-------------|
| **7x less RAM than Prometheus** | Fits <6GB constraint with headroom |
| **Single binary, no deps** | Air-gap compatible |
| **MetricsQL superset of PromQL** | 95% compatible, ergonomic improvements |
| **No telemetry** | Sovereignty verified |
| **-memory.allowedPercent=60** | Leave 40% for OS/caches |

**Critical Configuration**:
```bash
-memory.allowedPercent=60
-search.maxMemoryPerQuery=256MB
-search.maxConcurrentQueries=8
-retentionPeriod=365d
```

### Grafana Key Findings

| Finding | Implication |
|---------|-------------|
| **MetricsQL WITH templates** | Complex queries simplified |
| **Gauge + Time Series primary** | Memory visualization patterns |
| **Sidecar provisioning** | GitOps dashboard management |
| **Alert annotations** | Contextual alerting on dashboards |

**Dashboard Hierarchy**:
- Level 1: Overview (health, utilization)
- Level 2: Tactical (per-block metrics)
- Level 3: Diagnostic (raw events, traces)

### MCP Key Findings

| Finding | Implication |
|---------|-------------|
| **FastMCP high-level API** | Rapid server development |
| **stdio + streamable-http** | Local and remote transports |
| **Resources + Tools + Prompts** | Complete memory access model |
| **File watcher integration** | Real-time subscriptions |

**URI Scheme**: `memory://bank/{path}`

### A2A Key Findings

| Finding | Implication |
|---------|-------------|
| **Linux Foundation governance** | Vendor-neutral, stable |
| **Task lifecycle states** | Structured async communication |
| **Agent Card discovery** | Standardized capability advertisement |
| **Complements MCP** | Different layer (agent-to-agent) |

**Migration Path**: Parallel deployment → Hybrid mode → Full migration

---

## Systematic Execution Plan

### Week 1: Foundation - VictoriaMetrics Deployment

#### Step 1.1: Service Startup (Day 1-2)

**Objective**: Deploy and verify VictoriaMetrics service

**Tasks**:
1. Start VictoriaMetrics container
2. Verify health endpoint
3. Configure memory limits
4. Test basic write/query

**Commands**:
```bash
# Start service
podman-compose up -d victoriametrics

# Verify health
curl http://localhost:8428/health

# Test write
curl -X POST "http://localhost:8428/api/v1/write" \
  -d "test_metric{label=\"value\"} 42"

# Test query
curl "http://localhost:8428/api/v1/query?query=test_metric"
```

**Verification**:
- [ ] Health endpoint returns 200
- [ ] Write succeeds (204 response)
- [ ] Query returns written metric
- [ ] Memory usage < 200MB baseline

**Rollback**: Stop container, no data loss risk

#### Step 1.2: Memory Tools Integration (Day 2-3)

**Objective**: Connect memory tools to VictoriaMetrics

**Implementation**:
```python
# In metrics_collector.py
class MemoryMetricsCollector:
    async def write_metric(self, name: str, value: float, labels: dict):
        metric_line = f"{name}{{{','.join(f'{k}=\"{v}\"' for k, v in labels.items())}}} {value}"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.vm_endpoint}/api/v1/import/prometheus",
                data=metric_line
            ) as resp:
                return resp.status == 204
```

**Verification**:
- [ ] Block utilization metrics visible in VM
- [ ] Tool invocation metrics visible
- [ ] Overflow events tracked

#### Step 1.3: Redis + VictoriaMetrics Split (Day 3-4)

**Objective**: Use Redis for real-time, VM for historical

| Metric Type | Storage | Purpose |
|-------------|---------|---------|
| Block utilization | Redis + VM | Real-time + historical |
| Tool invocations | Redis + VM | Real-time + historical |
| Overflow events | VM only | Audit trail |
| Session continuity | Redis only | Transient state |

**Implementation**:
```python
async def record_block_utilization(self, block: str, chars: int, limit: int):
    util = chars / limit
    # Real-time to Redis
    await self.redis.hset(f"memory:blocks:{block}", "utilization", util)
    # Historical to VictoriaMetrics
    await self.write_metric("memory_block_utilization", util, {"block": block})
```

**Verification**:
- [ ] Redis shows current values
- [ ] VM shows time series
- [ ] Query both sources

---

### Week 2: Observability - Grafana Dashboards

#### Step 2.1: Datasource Configuration (Day 1)

**Objective**: Configure VictoriaMetrics as Grafana datasource

**Provisioning File**:
```yaml
# provisioning/datasources/victoriametrics.yml
apiVersion: 1
datasources:
  - name: VictoriaMetrics
    type: victoriametrics-metrics-datasource
    access: proxy
    url: http://victoriametrics:8428
    isDefault: true
    editable: false
```

**Verification**:
- [ ] Datasource appears in Grafana
- [ ] Query test succeeds
- [ ] MetricsQL syntax highlighting works

#### Step 2.2: Overview Dashboard (Day 2-3)

**Objective**: Create high-level memory health dashboard

**Panels**:

| Panel | Query | Type |
|-------|-------|------|
| Core Utilization | `memory_block_utilization{tier="core"}` | Gauge |
| Active Sessions | `count(memory_session_active)` | Stat |
| Tool Calls/min | `rate(memory_tool_calls_total[5m])*60` | Time Series |
| Overflow Events | `rate(memory_overflow_events_total[1h])` | Time Series |
| Continuity Score | `memory_session_continuity_score` | Gauge |

**Thresholds**:
- Green: 0-70%
- Yellow: 70-90%
- Red: 90-100%

**Verification**:
- [ ] Dashboard renders correctly
- [ ] Data flows from VictoriaMetrics
- [ ] Thresholds display correctly

#### Step 2.3: Block Detail Dashboard (Day 3-4)

**Objective**: Per-block metrics with drill-down

**Variables**:
```yaml
variables:
  - name: block
    type: Query
    query: label_values(memory_block_utilization, block)
  - name: tier
    type: Query
    query: label_values(memory_block_utilization, tier)
```

**Panels**:
- Block utilization over time
- Character count vs limit
- Update frequency
- Last modified timestamp

#### Step 2.4: Alerting Rules (Day 5)

**Objective**: Proactive monitoring

**Alerts**:
```yaml
groups:
  - name: memory_bank
    rules:
      - alert: HighBlockUtilization
        expr: memory_block_utilization > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Block {{ $labels.block }} at {{ $value }}%"

      - alert: OverflowEventSpike
        expr: rate(memory_overflow_events_total[5m]) > 1
        for: 2m
        labels:
          severity: warning

      - alert: LowSessionContinuity
        expr: avg(memory_session_continuity_score) < 50
        for: 15m
        labels:
          severity: warning
```

---

### Week 3: Protocol - MCP Server Implementation

#### Step 3.1: Server Skeleton (Day 1-2)

**Objective**: Create basic MCP server with FastMCP

**Structure**:
```
mcp-servers/
└── xnai-memory/
    ├── __init__.py
    ├── server.py          # Main server
    ├── resources.py       # Resource handlers
    ├── tools.py           # Tool handlers
    └── prompts.py         # Prompt templates
```

**Core Server**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("XNAi Memory Bank")

@mcp.resource("memory://bank/{path:path}")
async def read_memory(path: str) -> str:
    """Read memory bank file."""
    return (MEMORY_BANK_ROOT / path).read_text()

@mcp.tool()
async def get_core_context() -> str:
    """Get compiled core context."""
    # Implementation

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Verification**:
- [ ] Server starts without errors
- [ ] MCP Inspector can connect
- [ ] Resources list correctly
- [ ] Tools execute successfully

#### Step 3.2: Resource Implementation (Day 2-3)

**Objective**: Full resource hierarchy

**Resources**:
| URI | Description |
|-----|-------------|
| `memory://bank/{path}` | Any memory file |
| `memory://bank/core/*` | Core blocks |
| `memory://bank/recall/*` | Recall tier |
| `memory://bank/archival/*` | Archival tier |

**List Resources**:
```python
@mcp.list_resources()
async def list_memory_files() -> list[Resource]:
    resources = []
    for f in MEMORY_BANK_ROOT.rglob("*.md"):
        rel = f.relative_to(MEMORY_BANK_ROOT)
        resources.append(Resource(
            uri=f"memory://bank/{rel}",
            name=f.stem,
            mimeType="text/markdown"
        ))
    return resources
```

#### Step 3.3: Tool Implementation (Day 3-4)

**Objective**: Memory manipulation tools

**Tools**:
| Tool | Purpose |
|------|---------|
| `get_core_context` | Load core blocks |
| `get_active_context` | Current priorities |
| `get_progress_status` | Project status |
| `search_memory_bank` | Semantic search |
| `update_memory_file` | Modify memory |

**Input Validation**:
```python
from pydantic import BaseModel, Field

class MemoryUpdate(BaseModel):
    path: str = Field(description="Relative path")
    content: str = Field(description="New content")
    mode: str = Field(default="replace", description="replace or append")
```

#### Step 3.4: File Watcher (Day 5)

**Objective**: Real-time change notifications

**Implementation**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MemoryWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            uri = f"memory://bank/{relative_path}"
            # Notify subscribers
            await notify_resource_updated(uri)
```

#### Step 3.5: Client Configuration (Day 5)

**Claude Desktop**:
```json
{
  "mcpServers": {
    "xnai-memory": {
      "command": "uv",
      "args": ["run", "mcp-servers/xnai-memory/server.py"]
    }
  }
}
```

**Cline**:
```json
{
  "mcpServers": {
    "xnai-memory": {
      "command": "uv",
      "args": ["run", "mcp-servers/xnai-memory/server.py"],
      "alwaysAllow": ["get_core_context", "search_memory_bank"]
    }
  }
}
```

---

### Week 4-5: Integration - A2A Protocol

#### Step 4.1: A2A SDK Setup (Day 1)

**Objective**: Install and configure A2A

```bash
pip install "a2a-sdk[http-server]"
```

#### Step 4.2: Agent Card Definition (Day 1-2)

**Objective**: Define XNAi agent capabilities

```json
{
  "name": "XNAi RAG Agent",
  "description": "Semantic search and memory management",
  "url": "http://localhost:8000/a2a",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "semantic-search",
      "name": "Semantic Search",
      "description": "Search memory bank"
    },
    {
      "id": "context-load",
      "name": "Load Context",
      "description": "Load memory context"
    }
  ]
}
```

#### Step 4.3: Hybrid Bus Adapter (Day 2-4)

**Objective**: Bridge A2A and legacy bus

```python
class HybridAgentBus:
    def __init__(self):
        self.a2a_client = A2AClient(url="http://localhost:8000/a2a")
        self.legacy_bus = AgentBusClient(redis_url="redis://localhost:6379")
    
    async def send_task(self, target: str, task: dict):
        if self._is_a2a_capable(target):
            return await self.a2a_client.send_message(...)
        return await self.legacy_bus.send_task(...)
```

#### Step 4.4: Task Store Migration (Day 4-5)

**Objective**: Move task state to A2A TaskStore

```python
from a2a.server.tasks import InMemoryTaskStore

# Later: DatabaseTaskStore for persistence
task_store = InMemoryTaskStore()
```

---

### Week 6: Testing & Validation

#### Step 5.1: Integration Tests (Day 1-2)

**Test Matrix**:
| Component | Test | Expected |
|-----------|------|----------|
| VictoriaMetrics | Write/query | < 100ms |
| Grafana | Dashboard load | < 2s |
| MCP | Tool execution | < 500ms |
| A2A | Message round-trip | < 200ms |

#### Step 5.2: Performance Benchmarks (Day 3)

**Benchmarks**:
- Memory utilization tracking overhead
- Context compilation latency
- Search query latency
- Concurrent client handling

#### Step 5.3: Documentation (Day 4-5)

**Documents**:
- MCP server README
- A2A integration guide
- Grafana dashboard guide
- Migration runbook

---

## Metrics for Strategy Effectiveness

### Primary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Block Compliance** | 100% | Automated check via get_block_status() |
| **Context Load Time** | < 500ms | Instrumentation in compile_context() |
| **Memory Overhead** | < 100MB | VictoriaMetrics + MCP + A2A overhead |
| **Query Latency p95** | < 200ms | VictoriaMetrics histogram |
| **Tool Success Rate** | > 99% | Counter in metrics_collector |
| **Session Continuity** | > 80% | Continuity score calculation |

### Secondary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dashboard load time | < 2s | Grafana metrics |
| Alert response time | < 30s | Alert-to-notification latency |
| MCP connection time | < 1s | Client connection metrics |
| A2A discovery time | < 500ms | Agent card fetch time |

### Tracking Mechanism

```python
# metrics_collector.py
class StrategyMetrics:
    async def track_execution(self, step: str, duration_ms: float, success: bool):
        await self.write_metric("strategy_step_duration_ms", duration_ms, {"step": step})
        await self.write_metric("strategy_step_success", 1 if success else 0, {"step": step})
```

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| VictoriaMetrics OOM | Low | High | Set -memory.allowedPercent=60 |
| MCP client incompatibility | Medium | Medium | Test with multiple clients |
| A2A migration disruption | Medium | High | Hybrid adapter with fallback |
| Dashboard performance | Low | Low | Limit queries, use caching |

---

## Success Criteria

### Week 1 Success
- [ ] VictoriaMetrics healthy and receiving metrics
- [ ] Memory tools integrated with metrics collection
- [ ] Real-time + historical split working

### Week 2 Success
- [ ] Overview dashboard operational
- [ ] Block detail dashboard operational
- [ ] Alerting rules firing correctly

### Week 3 Success
- [ ] MCP server responding to queries
- [ ] Claude Desktop / Cline integration working
- [ ] File watcher notifying changes

### Week 4-5 Success
- [ ] A2A server operational
- [ ] Hybrid adapter working
- [ ] Legacy bus fallback functional

### Week 6 Success
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Performance within targets

---

## Knowledge Gaps Requiring Further Research

| Gap | Impact | Research Needed |
|------|--------|-----------------|
| VictoriaMetrics cluster mode | Future scaling | Evaluate for > 10M series |
| MCP authentication | Production security | OAuth 2.1 integration |
| A2A skill schemas | Tool interoperability | JSON Schema conventions |
| Grafana multi-tenancy | Multi-user dashboards | Organization isolation |

---

**Status**: Ready for execution approval
**Next Action**: Begin Week 1, Step 1.1
**Owner**: Implementation Team
