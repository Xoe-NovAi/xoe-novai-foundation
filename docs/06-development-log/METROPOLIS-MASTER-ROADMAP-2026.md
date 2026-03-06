# Metropolis Master Manual & Implementation Roadmap

## 1. The Prime Council (Distributed Consensus)

### Architecture Overview
The Prime Council implements a Byzantine Fault Tolerant (BFT) consensus mechanism using a modified Raft protocol with practical Byzantine fault tolerance (pBFT) characteristics. The system operates with 5 initial council nodes, requiring 3/5 consensus for state transitions.

### Implementation Specifications

**Node Configuration:**
```yaml
council:
  nodes:
    - id: prime-01
      address: 10.0.1.10:8443
      public_key: "ed25519:abc123..."
    - id: prime-02  
      address: 10.0.1.11:8443
      public_key: "ed25519:def456..."
    # ... additional nodes
  consensus_threshold: 3
  election_timeout: 1500ms
  heartbeat_interval: 500ms
```

**Consensus Protocol:**
- Three-phase commit protocol (Prepare, Commit, Apply)
- Digital signatures using Ed25519 for message authentication
- Merkle trees for state verification
- Automatic leader election with failover

**CLI Agent Execution Commands:**
```bash
# Initialize council node
metropolis council init --node-id prime-01 --config /etc/metropolis/council.yaml

# Join consensus cluster
metropolis council join --bootstrap-node 10.0.1.10:8443

# View consensus state
metropolis council status --verbose
```

## 2. Asynchronous Agent Bus (NATS/Redis Streams 2.0)

### Architecture Overview
Hybrid message bus combining NATS JetStream for high-throughput messaging and Redis Streams for persistent state and coordination. Implements exactly-once delivery semantics with dead-letter queues and automatic retry mechanisms.

### Implementation Specifications

**NATS JetStream Configuration:**
```yaml
jetstream:
  enabled: true
  store_dir: /var/lib/metropolis/jetstream
  max_memory_store: 2GB
  max_file_store: 10GB
  streams:
    - name: agent_commands
      subjects: ["agent.cmd.>"]
      retention: interest
      max_msgs_per_subject: 1000
    - name: telemetry_data
      subjects: ["telemetry.>"]
      retention: workqueue
      max_age: 24h
```

**Redis Streams Configuration:**
```yaml
redis_streams:
  enabled: true
  url: redis://127.0.0.1:6379
  streams:
    - name: agent_state
      max_len: 10000
    - name: coordination
      max_len: 5000
  consumer_groups:
    - name: agent_workers
      streams: ["agent_state"]
```

**Message Schema:**
```json
{
  "message_id": "uuid-v4",
  "timestamp": "iso8601",
  "source": "agent-id",
  "destination": "target-agent-id",
  "payload": {},
  "signature": "ed25519-signature",
  "ttl": 300
}
```

**CLI Agent Execution Commands:**
```bash
# Publish message to bus
metropolis bus publish --stream agent_commands --subject "agent.cmd.deploy" --payload @deploy.json

# Create consumer group
metropolis bus create-consumer --stream agent_state --group deploy-workers

# Monitor bus traffic
metropolis bus monitor --subject "agent.cmd.>" --follow
```

## 3. Telemetry Sentry (Prometheus/Grafana Loop)

### Architecture Overview
Comprehensive observability stack with Prometheus for metrics collection, Grafana for visualization, and custom exporters for Metropolis-specific telemetry. Implements automatic anomaly detection and alerting.

### Implementation Specifications

**Prometheus Configuration:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 30s

scrape_configs:
  - job_name: 'metropolis-agents'
    static_configs:
      - targets: ['10.0.1.10:9091', '10.0.1.11:9091']
    metrics_path: '/metrics'
    params:
      format: ['prometheus']

  - job_name: 'council-nodes'
    static_configs:
      - targets: ['10.0.1.10:9092', '10.0.1.11:9092']
```

**Custom Metrics Exporters:**
- Council consensus metrics (leader status, commit latency, node health)
- Message bus metrics (throughput, latency, error rates)
- Agent performance metrics (CPU, memory, execution times)

**Alerting Rules:**
```yaml
groups:
- name: metropolis-alerts
  rules:
  - alert: CouncilConsensusDegraded
    expr: council_consensus_health < 0.8
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Council consensus health degraded"
  
  - alert: MessageBusBacklog
    expr: rate(bus_messages_pending[5m]) > 1000
    for: 2m
    labels:
      severity: warning
```

**Grafana Dashboards:**
- Council Consensus Overview
- Message Bus Performance
- Agent Deployment Metrics
- System Health Status

**CLI Agent Execution Commands:**
```bash
# Export custom metrics
metropolis telemetry export --format prometheus --port 9091

# Check alert status
metropolis telemetry alerts --status

# Generate performance report
metropolis telemetry report --period 24h --output json
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Deploy initial Council nodes with basic consensus
- [ ] Set up NATS JetStream with core streams
- [ ] Implement basic Prometheus scraping
- [ ] Create initial Grafana dashboard templates

### Phase 2: Integration (Weeks 3-4)
- [ ] Implement Redis Streams integration
- [ ] Add exactly-once delivery semantics
- [ ] Deploy custom metrics exporters
- [ ] Configure alerting rules and notifications

### Phase 3: Optimization (Weeks 5-6)
- [ ] Implement automatic failover mechanisms
- [ ] Add message compression and encryption
- [ ] Deploy anomaly detection algorithms
- [ ] Optimize storage and retention policies

### Phase 4: Production (Weeks 7-8)
- [ ] Performance testing and load optimization
- [ ] Security audit and penetration testing
- [ ] Documentation finalization
- [ ] Production deployment and monitoring

## Security Considerations
- All inter-node communication uses mutual TLS
- Message payloads encrypted with AES-256-GCM
- Digital signatures for all consensus messages
- Regular key rotation and security audits

## Monitoring & Maintenance
- Automated health checks every 30 seconds
- Daily backup of consensus state and message queues
- Weekly performance reviews and optimization
- Monthly security updates and patches

---

*This roadmap implements the Phase 1 audit recommendations while providing a scalable, production-ready architecture for the Metropolis system. All components are designed for zero-downtime upgrades and automatic recovery from failures.*
