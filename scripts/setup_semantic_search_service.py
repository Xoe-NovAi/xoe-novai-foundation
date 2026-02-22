#!/usr/bin/env python3
"""
Phase 7: Setup script for semantic search service deployment

Handles:
- Consul service registration
- Service discovery configuration
- Prometheus metrics setup
- Systemd service file generation
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVICE_NAME = "semantic-search-service"
SERVICE_PORT = 8002
SERVICE_HOST = "localhost"
CONSUL_PORT = 8500
CONSUL_HOST = "localhost"

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str = SERVICE_NAME
    port: int = SERVICE_PORT
    host: str = SERVICE_HOST
    version: str = "1.0.0"
    tags: list = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = ["xnai-agent", "semantic-search", "knowledge-base"]


# ============================================================================
# CONSUL REGISTRATION
# ============================================================================

def register_with_consul(config: ServiceConfig) -> bool:
    """Register service with Consul"""
    try:
        import requests
    except ImportError:
        logger.warning("requests library not available, skipping Consul registration")
        return False
    
    consul_url = f"http://{CONSUL_HOST}:{CONSUL_PORT}"
    
    # Check if Consul is running
    try:
        response = requests.get(f"{consul_url}/v1/status/leader", timeout=2)
        if response.status_code != 200:
            logger.warning("Consul not responding, skipping registration")
            return False
    except Exception as e:
        logger.warning(f"Cannot reach Consul: {e}")
        return False
    
    # Register service
    service_data = {
        "ID": f"{config.name}-001",
        "Name": config.name,
        "Port": config.port,
        "Address": config.host,
        "Tags": config.tags,
        "Meta": {
            "version": config.version,
            "capabilities": "semantic_search,knowledge_base_query,documentation_lookup"
        },
        "Check": {
            "HTTP": f"http://{config.host}:{config.port}/health",
            "Interval": "10s",
            "Timeout": "5s"
        }
    }
    
    try:
        response = requests.put(
            f"{consul_url}/v1/agent/service/register",
            json=service_data,
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Registered {config.name} with Consul")
            return True
        else:
            logger.error(f"Failed to register with Consul: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error registering with Consul: {e}")
        return False


# ============================================================================
# SYSTEMD SERVICE FILE GENERATION
# ============================================================================

def create_systemd_service(config: ServiceConfig, repo_path: Path) -> Path:
    """Generate systemd service file"""
    
    service_file = f"""[Unit]
Description=XNAi Semantic Search Agent Bus Service
After=network.target redis.service
Requires=redis.service
Documentation=https://github.com/xnai-foundation/stack

[Service]
Type=simple
User=arcana-novai
WorkingDirectory={repo_path}
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 app/XNAi_rag_app/api/semantic_search_agent_bus.py
Restart=always
RestartSec=10

# Resource limits for Ryzen 7 5700U (6.6GB RAM)
MemoryLimit=2G
CPUQuota=50%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=semantic-search

[Install]
WantedBy=multi-user.target
"""
    
    service_path = Path(f"/tmp/{SERVICE_NAME}.service")
    service_path.write_text(service_file)
    
    logger.info(f"✅ Generated systemd service file: {service_path}")
    logger.info(f"\nTo install (requires sudo):")
    logger.info(f"  sudo cp {service_path} /etc/systemd/system/")
    logger.info(f"  sudo systemctl daemon-reload")
    logger.info(f"  sudo systemctl enable {SERVICE_NAME}")
    logger.info(f"  sudo systemctl start {SERVICE_NAME}")
    
    return service_path


# ============================================================================
# PROMETHEUS METRICS SETUP
# ============================================================================

def create_prometheus_config() -> str:
    """Generate Prometheus configuration for semantic search service"""
    
    config = f"""# Semantic Search Service Metrics
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'semantic-search-service'
    static_configs:
      - targets: ['{SERVICE_HOST}:{SERVICE_PORT}']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s

  # Consul service discovery (optional, if Consul running)
  - job_name: 'consul-semantic-search'
    consul_sd_configs:
      - server: '{CONSUL_HOST}:{CONSUL_PORT}'
    relabel_configs:
      - source_labels: [__meta_consul_service]
        regex: '{SERVICE_NAME}'
        action: keep
"""
    
    prom_path = Path(f"/tmp/prometheus-{SERVICE_NAME}.yml")
    prom_path.write_text(config)
    
    logger.info(f"✅ Generated Prometheus config: {prom_path}")
    
    return config


# ============================================================================
# DOCKER COMPOSE GENERATION
# ============================================================================

def create_docker_compose() -> Path:
    """Generate docker-compose.yml for local development"""
    
    compose = f"""version: '3.8'

services:
  semantic-search-service:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - SERVICE_NAME={SERVICE_NAME}
    ports:
      - "{SERVICE_PORT}:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - REDIS_URL=redis://redis:6379
      - CONSUL_HOST=consul
    depends_on:
      - redis
      - consul
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    volumes:
      - ./knowledge:/app/knowledge:ro
      - ./communication_hub:/app/communication_hub
    networks:
      - xnai-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - xnai-network

  consul:
    image: consul:latest
    ports:
      - "8500:8500"
      - "8600:8600/udp"
    command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0
    networks:
      - xnai-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus-{SERVICE_NAME}.yml:/etc/prometheus/prometheus.yml:ro
    networks:
      - xnai-network

networks:
  xnai-network:
    driver: bridge
"""
    
    compose_path = Path(f"/tmp/docker-compose-{SERVICE_NAME}.yml")
    compose_path.write_text(compose)
    
    logger.info(f"✅ Generated docker-compose.yml: {compose_path}")
    
    return compose_path


# ============================================================================
# DEPLOYMENT GUIDE
# ============================================================================

def print_deployment_guide(config: ServiceConfig, repo_path: Path):
    """Print deployment guide"""
    
    guide = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║         SEMANTIC SEARCH SERVICE - DEPLOYMENT GUIDE                      ║
╚══════════════════════════════════════════════════════════════════════════╝

SERVICE INFORMATION
═══════════════════════════════════════════════════════════════════════════
  Service Name:     {config.name}
  Port:             {config.port}
  Host:             {config.host}
  Version:          {config.version}
  Repo Path:        {repo_path}

DEPLOYMENT OPTIONS
═══════════════════════════════════════════════════════════════════════════

1. STANDALONE (Python)
   ─────────────────────
   cd {repo_path}
   python3 app/XNAi_rag_app/api/semantic_search_agent_bus.py
   
   This mode:
   - Reads/writes messages from communication_hub directories
   - Listens for task assignments from Agent Bus coordinator
   - Sends heartbeats and task results back to coordinator

2. SYSTEMD SERVICE (Production)
   ────────────────────────────
   sudo cp /tmp/{SERVICE_NAME}.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable {SERVICE_NAME}
   sudo systemctl start {SERVICE_NAME}
   
   Check status:
   systemctl status {SERVICE_NAME}
   journalctl -u {SERVICE_NAME} -f

3. DOCKER (Development/Testing)
   ────────────────────────────
   docker-compose -f /tmp/docker-compose-{SERVICE_NAME}.yml up
   
   Services:
   - semantic-search: http://localhost:{SERVICE_PORT}
   - Consul UI: http://localhost:8500
   - Prometheus: http://localhost:9090

INTEGRATION POINTS
═══════════════════════════════════════════════════════════════════════════

Agent Bus Coordinator:
  - Listens on: {repo_path}/communication_hub/inbox/
  - Sends heartbeats to: outbox/
  - Registers with Consul (if available)

Knowledge Base:
  - Location: {repo_path}/knowledge/technical_manuals/
  - Size: ~5.04 MB
  - Format: Markdown with YAML frontmatter
  - Chunks indexed: 1,428

TESTING
═══════════════════════════════════════════════════════════════════════════

1. Manual Search Query
   curl -X POST "http://localhost:{SERVICE_PORT}/search" \\
     -H "Content-Type: application/json" \\
     -d {{"query": "Redis configuration", "top_k": 5}}

2. Health Check
   curl http://localhost:{SERVICE_PORT}/health

3. Agent Bus Simulation
   # Send task to service
   cat > /tmp/test_task.json << 'EOF_TASK'
   {{
     "message_id": "test-001",
     "timestamp": "2026-02-17T01:58:00Z",
     "sender": "agent_coordinator",
     "target": "{SERVICE_NAME}",
     "type": "task_assignment",
     "priority": "high",
     "content": {{
       "query": "Kubernetes deployment",
       "top_k": 5,
       "min_score": 0.3
     }}
   }}
   EOF_TASK
   
   cp /tmp/test_task.json {repo_path}/communication_hub/inbox/{SERVICE_NAME}-test-001.json
   
   # Monitor outbox for response
   watch -n 1 'ls -la {repo_path}/communication_hub/outbox/'

MONITORING
═══════════════════════════════════════════════════════════════════════════

Metrics Endpoint:
  http://localhost:{SERVICE_PORT}/metrics (Prometheus compatible)

Key Metrics:
  - semantic_search_queries_total (counter)
  - semantic_search_latency_ms (histogram)
  - search_results_count (gauge)
  - heartbeat_last_sent (gauge)

Prometheus Dashboard:
  http://localhost:9090
  Query examples:
    - rate(semantic_search_queries_total[5m])
    - histogram_quantile(0.95, semantic_search_latency_ms)

TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

Issue: Service won't start
  - Check Redis running: redis-cli ping
  - Check knowledge base: ls -la knowledge/technical_manuals/
  - Review logs: journalctl -u {SERVICE_NAME} -n 50

Issue: No Consul registration
  - Check Consul: curl http://localhost:8500/v1/status/leader
  - Consul optional; service works without it

Issue: Slow searches
  - Check indexes: du -sh knowledge/technical_manuals/
  - Monitor memory: free -h
  - Check CPU: top -p $(pgrep -f semantic_search)

NEXT STEPS
═══════════════════════════════════════════════════════════════════════════

1. ✅ Deploy service (choose option 1, 2, or 3 above)
2. ✅ Verify with health check
3. ✅ Send test query (see TESTING section)
4. ✅ Monitor with Prometheus
5. ✅ Register with Agent Bus coordinator
6. ✅ Add to system monitoring/alerting

═══════════════════════════════════════════════════════════════════════════
"""
    
    print(guide)


# ============================================================================
# MAIN
# ============================================================================

def main():
    logger.info("Semantic Search Service - Deployment Setup")
    logger.info("=" * 70)
    
    repo_path = Path("/home/arcana-novai/Documents/xnai-foundation")
    if not repo_path.exists():
        logger.error(f"Repository path not found: {repo_path}")
        return 1
    
    config = ServiceConfig()
    
    # Generate artifacts
    logger.info("\nGenerating deployment artifacts...")
    
    # Systemd service
    service_file = create_systemd_service(config, repo_path)
    
    # Prometheus config
    prom_config = create_prometheus_config()
    
    # Docker Compose
    compose_file = create_docker_compose()
    
    # Consul registration (optional)
    logger.info("\nAttempting Consul registration...")
    consul_success = register_with_consul(config)
    if not consul_success:
        logger.info("(Consul registration optional; service works without it)")
    
    # Print deployment guide
    print_deployment_guide(config, repo_path)
    
    logger.info("\n✅ Deployment setup complete!")
    logger.info("\nNext steps:")
    logger.info("1. Copy systemd service: sudo cp {} /etc/systemd/system/".format(service_file))
    logger.info("2. Start service: sudo systemctl start {}".format(SERVICE_NAME))
    logger.info("3. Check status: systemctl status {}".format(SERVICE_NAME))
    
    return 0


if __name__ == "__main__":
    exit(main())

