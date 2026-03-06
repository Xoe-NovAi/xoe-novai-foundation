# Omega-Stack Agent-Bus Implementation Guide

This document provides comprehensive documentation for the Omega-Stack Agent-Bus implementation, covering all components, services, and integration points.

## Overview

The Omega-Stack Agent-Bus is a comprehensive agent management and coordination system that provides:

- **Agent Registry**: Centralized management of AI agents with metadata and preferences
- **Research Job Management**: Structured workflow for research projects with collaboration support
- **Inter-Agent Communication**: Redis-based message bus for agent coordination
- **Performance Metrics**: Prometheus-based monitoring and agent ranking
- **Vikunja Integration**: Automated project and task management
- **Multi-Account CLI**: Enhanced Cline wrapper with account management

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Tools     │    │   Agent Bus      │    │   Web Interface │
│                 │    │   (Redis)        │    │                 │
│ • omega.py      │◄──►│ • Message Router │◄──►│ • Research UI   │
│ • cline-multi   │    │ • Pub/Sub        │    │ • Agent Monitor │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │    │   Services       │    │   External      │
│   (PostgreSQL)  │    │                  │    │   Integrations  │
│                 │    │ • AgentRegistry  │    │                 │
│ • Agents        │◄──►│ • ResearchManager│◄──►│ • Vikunja API   │
│ • Jobs          │    │ • AgentBus       │    │ • Prometheus    │
│ • Metrics       │    │ • MetricsManager │    │ • Redis         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### 1. Database Schema

The system uses PostgreSQL with the following key tables:

#### Agents Table
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    model VARCHAR(255),
    runtime VARCHAR(50) NOT NULL,
    priority NUMERIC(5,2) NOT NULL DEFAULT 0,
    personality_version NUMERIC(5,2) NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Research Jobs Table
```sql
CREATE TABLE research_jobs (
    id UUID PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    claimed_by UUID REFERENCES agents(id),
    domain_tags JSON NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Agent Metrics Table
```sql
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    metric_name VARCHAR(255) NOT NULL,
    value NUMERIC(12,4) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Service Layer

#### AgentRegistry
Manages agent lifecycle operations:
- Registration and deactivation
- Preference management
- Status tracking
- Personality versioning

**Key Methods:**
```python
# Register a new agent
agent = registry.register_agent(
    name="Researcher-X",
    model="gpt-4",
    runtime="openai"
)

# Set domain preferences
registry.set_agent_preferences(agent.id, {
    "machine_learning": 0.8,
    "nlp": 0.6,
    "computer_vision": 0.4
})
```

#### ResearchJobManager
Handles research project workflow:
- Job creation and management
- Agent claiming and collaboration
- Status tracking
- Domain-based job matching

**Key Methods:**
```python
# Create a new research job
job = jobs.create_job(
    slug="ml-optimization-study",
    title="Machine Learning Model Optimization",
    domain_tags=["machine_learning", "optimization"]
)

# Claim a job
jobs.claim_job(job.id, agent.id)

# Invite collaborators
jobs.invite_collaborator(job.id, other_agent.id)
```

#### AgentBus
Redis-based message bus for agent communication:
- Message routing and delivery
- Heartbeat monitoring
- Collaboration coordination
- Task assignment

**Key Features:**
- Pub/sub messaging with Redis
- Message types: registration, heartbeat, task assignment, collaboration
- Automatic message parsing and routing
- Connection management and error handling

### 3. CLI Tools

#### Omega CLI (`scripts/omega.py`)

Enhanced command-line interface for agent and job management:

```bash
# Agent management
omega agent list                                    # List all agents
omega agent register --name "Agent-X" --model "gpt-4"  # Register agent
omega agent status agent123 active                  # Update status
omega agent preferences agent123 ml:0.8 nlp:0.6     # Set preferences

# Job management
omega agent list-jobs --status open                 # List open jobs
omega agent claim agent123 job456                   # Claim a job
omega job create --slug "test" --title "Test Job"   # Create job
omega job complete job456                           # Complete job

# Metrics and memory
omega metrics record agent123 accuracy 0.95         # Record metric
omega memory store agent123 conversation "..."      # Store memory
omega memory list agent123                          # List memories
```

#### Multi-Account Cline (`scripts/cline_multi_account.py`)

Enhanced Cline wrapper with multi-account support:

```bash
# Account management
omega-cline list-accounts                           # List accounts
omega-cline use claude                             # Switch account
omega-cline account add gemini --model gemini-pro --provider google

# Command execution
omega-cline run --account gemini ls                 # Run with specific account
omega-cline interactive --account default           # Interactive mode
```

### 4. Metrics and Monitoring

#### Prometheus Integration

The system exposes comprehensive metrics via Prometheus:

**Agent Performance Metrics:**
- `agent_task_success_rate`: Task completion success rate
- `agent_task_latency_seconds`: Task completion latency
- `agent_model_accuracy`: Model accuracy scores
- `agent_priority_score`: Agent priority for task assignment

**System Metrics:**
- `active_agents_total`: Number of active agents
- `open_jobs_total`: Number of open research jobs
- `claimed_jobs_total`: Number of claimed jobs
- `completed_jobs_total`: Number of completed jobs

**Metrics Server:**
```bash
# Start metrics server on port 8001
python scripts/agent_ranker.py 300  # 5-minute update interval
```

#### Agent Ranking

Automatic agent ranking based on performance metrics:

```python
# Get current rankings
ranker = AgentRankerService()
rankings = ranker.get_current_rankings()

# Composite score calculation
# Weighted combination of:
# - Success rate (30%)
# - Task latency (20%)
# - Model accuracy (25%)
# - Research quality (25%)
```

### 5. Vikunja Integration

Automated project and task management in Vikunja:

#### Project Creation
```python
# Automatic project creation when research job is created
sync = VikunjaSync()
project = sync.vikunja_client.create_project(
    title="Research: Machine Learning Study",
    description="Research project with automated task management"
)
```

#### Task Management
- Automatic task creation for research phases
- Status synchronization between Omega and Vikunja
- Agent assignment to Vikunja tasks
- Progress tracking and completion

#### Integration Points
- Research job creation → Vikunja project
- Job status changes → Task status updates
- Agent assignments → Task assignments
- Job completion → Project completion

## Installation and Setup

### Prerequisites

1. **Database**: PostgreSQL with the agent management migration applied
2. **Redis**: For message bus functionality
3. **Python**: 3.8+ with required dependencies
4. **Vikunja**: Optional, for project management integration

### Installation Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
# Additional dependencies:
# - sqlalchemy
# - redis
# - prometheus_client
# - pyyaml
# - requests
```

2. **Database Setup**
```bash
# Run the migration
alembic upgrade head

# Or manually create tables
python -c "from app.XNAi_rag_app.services.database import init_db; init_db()"
```

3. **Environment Configuration**
```bash
# Database connection
export DATABASE_URL="postgresql://user:password@localhost:5432/xnai"

# Redis connection
export REDIS_URL="redis://localhost:6379/0"

# Vikunja integration (optional)
export VIKUNJA_URL="http://localhost:3000"
export VIKUNJA_API_TOKEN="your-api-token"

# Prometheus metrics
export PROMETHEUS_PORT="8001"
```

4. **Start Services**
```bash
# Start agent bus
python -c "from app.XNAi_rag_app.services.agent_bus import agent_bus_manager; import asyncio; asyncio.run(agent_bus_manager.start())"

# Start metrics service
python scripts/agent_ranker.py

# Start CLI tools
python scripts/omega.py --help
python scripts/cline_multi_account.py --help
```

## Usage Examples

### Basic Agent Management

```bash
# Register a new agent
omega agent register --name "Researcher-Alpha" --model "gpt-4" --runtime "openai"

# Set agent preferences
omega agent preferences Researcher-Alpha machine_learning:0.9 nlp:0.7

# Update agent status
omega agent status Researcher-Alpha active
```

### Research Job Workflow

```bash
# Create a new research job
omega job create --slug "ai-ethics-study" --title "AI Ethics in Research" --domain-tags "ethics,ai,research"

# List available jobs
omega agent list-jobs --status open

# Claim a job
omega agent claim Researcher-Alpha ai-ethics-study

# Invite collaborators
omega agent invite Researcher-Alpha ai-ethics-study Researcher-Beta

# Complete the job
omega job complete ai-ethics-study
```

### Metrics and Monitoring

```bash
# Record metrics
omega metrics record Researcher-Alpha task_completion_rate 0.95
omega metrics record Researcher-Alpha model_accuracy 0.88

# Update rankings
omega metrics ranking

# View metrics server
curl http://localhost:8001/metrics
```

### Multi-Account Cline Usage

```bash
# List available accounts
omega-cline list-accounts

# Switch to a specific account
omega-cline use claude

# Run commands with specific account
omega-cline run --account gemini python script.py

# Start interactive session
omega-cline interactive --account default
```

## Configuration

### Database Configuration

```yaml
# config/database.yaml
database:
  url: "postgresql://user:password@localhost:5432/xnai"
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
```

### Agent Configuration

```yaml
# configs/agent-config.yaml
agents:
  default_priority: 0
  heartbeat_interval: 30
  max_concurrent_tasks: 5
  metrics_retention_days: 30
```

### Vikunja Configuration

```yaml
# configs/vikunja-config.yaml
vikunja:
  url: "http://localhost:3000"
  api_token: "your-api-token"
  auto_create_projects: true
  sync_interval: 300
```

### Prometheus Configuration

```yaml
# configs/prometheus-config.yaml
prometheus:
  port: 8001
  metrics_path: "/metrics"
  update_interval: 300
  retention_days: 90
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check database connectivity
python -c "from app.XNAi_rag_app.services.database import get_db_session; print('Database OK' if get_db_session() else 'Database Error')"

# Check Redis connectivity
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('Redis OK' if r.ping() else 'Redis Error')"

# Check agent bus status
curl http://localhost:8001/metrics | grep agent_bus
```

### Log Monitoring

```bash
# View agent bus logs
tail -f logs/agent-bus.log

# View metrics service logs
tail -f logs/metrics-service.log

# View CLI usage logs
tail -f logs/cli-usage.log
```

### Performance Tuning

1. **Database Optimization**
   - Ensure proper indexing on frequently queried fields
   - Monitor query performance with `EXPLAIN ANALYZE`
   - Consider connection pooling optimization

2. **Redis Optimization**
   - Monitor memory usage and connection counts
   - Configure appropriate eviction policies
   - Use Redis clustering for high availability

3. **Agent Performance**
   - Monitor agent response times
   - Adjust ranking algorithm weights based on performance
   - Implement circuit breakers for slow agents

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check connection string
   echo $DATABASE_URL
   
   # Test connection
   psql $DATABASE_URL -c "SELECT 1;"
   ```

2. **Redis Connection Issues**
   ```bash
   # Check Redis status
   redis-cli ping
   
   # Check connection URL
   echo $REDIS_URL
   ```

3. **Agent Registration Failures**
   ```bash
   # Check agent name uniqueness
   omega agent list | grep "agent-name"
   
   # Check agent status
   omega agent status agent-name
   ```

4. **Vikunja Integration Issues**
   ```bash
   # Test API connection
   curl -H "Authorization: Bearer $VIKUNJA_API_TOKEN" $VIKUNJA_URL/api/v1/projects
   
   # Check project creation
   omega job create --slug test --title "Test" --description "Test project"
   ```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart services with debug logging
python scripts/agent_ranker.py
```

## Security Considerations

1. **API Key Management**
   - Store API keys securely using environment variables
   - Use different keys for different environments
   - Implement key rotation policies

2. **Database Security**
   - Use strong passwords and connection encryption
   - Implement proper access controls
   - Regular security audits

3. **Message Bus Security**
   - Use Redis authentication
   - Implement message encryption for sensitive data
   - Monitor for unauthorized access

4. **Agent Isolation**
   - Implement proper resource limits per agent
   - Monitor agent behavior for anomalies
   - Implement sandboxing for untrusted agents

## Future Enhancements

1. **Advanced Analytics**
   - Machine learning for agent performance prediction
   - Anomaly detection for agent behavior
   - Predictive job assignment based on historical data

2. **Enhanced Collaboration**
   - Real-time collaboration features
   - Shared workspace for research teams
   - Advanced permission management

3. **Integration Expansion**
   - Support for additional project management tools
   - Integration with code repositories
   - CI/CD pipeline integration

4. **Performance Optimization**
   - Distributed agent execution
   - Caching strategies for frequently accessed data
   - Load balancing across multiple instances

## Support and Contributing

For support and contributions:

1. **Documentation**: Refer to individual component README files
2. **Issues**: Report bugs and feature requests via GitHub Issues
3. **Contributing**: Follow the project's contribution guidelines
4. **Community**: Join discussions in the project's communication channels

## License

This implementation is part of the Omega-Stack project and follows the project's licensing terms.