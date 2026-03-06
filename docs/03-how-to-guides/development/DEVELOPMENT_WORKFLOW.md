# XNAi Foundation: Development Workflow Guide

**Version**: 1.0.0  
**Date**: 2026-02-27  
**Status**: Draft  
**Purpose**: Comprehensive guide for development workflows in the modular architecture

## Overview

This guide provides detailed workflows for developing, testing, and deploying services in the XNAi Foundation modular architecture. It covers everything from local development setup to production deployment.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Service Development Workflow](#service-development-workflow)
3. [Testing Strategies](#testing-strategies)
4. [Code Quality and Standards](#code-quality-and-standards)
5. [Deployment Workflows](#deployment-workflows)
6. [Monitoring and Debugging](#monitoring-and-debugging)
7. [Troubleshooting Guide](#troubleshooting-guide)

## Development Environment Setup

### Prerequisites

```bash
# Required tools
- Docker 24.0+
- Docker Compose 2.20+
- Python 3.12+
- Node.js 18+ (for frontend development)
- Git 2.40+
- Make 4.3+
```

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Xoe-NovAi/xoe-novai-foundation.git
cd xoe-novai-foundation

# Set up environment
make setup

# Start development environment
make dev-up

# Verify setup
make health-check
```

### Environment Configuration

```bash
# Environment variables (create .env.local)
ENVIRONMENT=development
CONSUL_HOST=localhost
CONSUL_PORT=8500
REDIS_HOST=localhost
REDIS_PORT=6379
QDRANT_HOST=localhost
QDRANT_PORT=6333
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Development Tools Installation

```bash
# Install development dependencies
make install-dev

# Set up pre-commit hooks
make setup-hooks

# Configure IDE settings
make setup-ide
```

## Service Development Workflow

### 1. Creating a New Service

```bash
# Use the service generator
make create-service SERVICE_NAME=my-new-service

# This creates:
# - services/my-new-service/
# - services/my-new-service/Dockerfile
# - services/my-new-service/config.yaml
# - services/my-new-service/tests/
# - services/my-new-service/README.md
```

### 2. Service Development Process

#### Step 1: Define Service Contract
```yaml
# services/my-new-service/api-contract.yaml
openapi: 3.0.0
info:
  title: My New Service API
  version: 1.0.0
paths:
  /health:
    get:
      summary: Health check
      responses:
        '200':
          description: Service is healthy
```

#### Step 2: Implement Service
```python
# services/my-new-service/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class HealthResponse(BaseModel):
    status: str
    version: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", version="1.0.0")
```

#### Step 3: Add Configuration
```yaml
# services/my-new-service/config.yaml
service:
  name: my-new-service
  version: "1.0.0"
  
api:
  host: "0.0.0.0"
  port: 8000
  
dependencies:
  database:
    host: "${DB_HOST:-localhost}"
    port: "${DB_PORT:-5432}"
```

#### Step 4: Add Tests
```python
# services/my-new-service/tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 3. Service Integration

#### Update Docker Compose
```yaml
# docker-compose.yml
services:
  my-new-service:
    build:
      context: ./services/my-new-service
      dockerfile: Dockerfile
    image: xnai-my-new-service:latest
    container_name: xnai_my_new_service
    environment:
      - ENVIRONMENT=${ENVIRONMENT:-development}
      - DB_HOST=${DB_HOST:-postgres}
      - DB_PORT=${DB_PORT:-5432}
    depends_on:
      - postgres
    networks:
      - xnai_network
    restart: unless-stopped
```

#### Update Service Discovery
```yaml
# configs/services/my-new-service.yaml
service:
  name: my-new-service
  version: "1.0.0"
  
consul:
  service:
    name: my-new-service
    port: 8000
    tags:
      - api
      - microservice
    checks:
      - http: http://localhost:8000/health
        interval: 10s
        timeout: 5s
```

## Testing Strategies

### 1. Unit Testing

```bash
# Run unit tests for a specific service
make test SERVICE=my-new-service

# Run all unit tests
make test-all

# Run tests with coverage
make test-coverage
```

#### Test Structure
```
services/my-new-service/
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_models.py
│   ├── test_integration.py
│   └── fixtures/
│       ├── sample_data.json
│       └── mock_responses/
└── conftest.py
```

#### Test Configuration
```python
# services/my-new-service/conftest.py
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_database():
    with patch('my_service.database.get_connection') as mock_conn:
        yield mock_conn

@pytest.fixture
def test_client():
    from main import app
    from fastapi.testclient import TestClient
    return TestClient(app)
```

### 2. Integration Testing

```bash
# Run integration tests
make test-integration

# Run tests against real dependencies
make test-integration-real
```

#### Integration Test Example
```python
# services/my-new-service/tests/test_integration.py
import pytest
from main import app
from fastapi.testclient import TestClient

@pytest.mark.integration
def test_service_with_database():
    """Test service with real database connection"""
    client = TestClient(app)
    
    # Test database operations
    response = client.post("/data", json={"key": "value"})
    assert response.status_code == 200
    
    # Verify data was stored
    response = client.get("/data/key")
    assert response.json()["value"] == "value"
```

### 3. End-to-End Testing

```bash
# Run E2E tests
make test-e2e

# Run E2E tests with specific scenario
make test-e2e SCENARIO=user-journey
```

#### E2E Test Structure
```python
# tests/e2e/test_user_journey.py
import pytest
import requests
from selenium import webdriver

class TestUserJourney:
    def test_complete_workflow(self):
        """Test complete user workflow across services"""
        # 1. User authentication
        auth_response = requests.post("http://localhost:8001/auth", 
                                    json={"username": "test", "password": "test"})
        assert auth_response.status_code == 200
        token = auth_response.json()["token"]
        
        # 2. Create document
        headers = {"Authorization": f"Bearer {token}"}
        doc_response = requests.post("http://localhost:8000/documents", 
                                   json={"content": "test document"}, 
                                   headers=headers)
        assert doc_response.status_code == 201
        doc_id = doc_response.json()["id"]
        
        # 3. Query document
        query_response = requests.get(f"http://localhost:8000/documents/{doc_id}", 
                                    headers=headers)
        assert query_response.status_code == 200
```

### 4. Performance Testing

```bash
# Run performance tests
make test-performance

# Load testing
make test-load
```

#### Performance Test Example
```python
# tests/performance/test_load.py
import pytest
import requests
import time
from concurrent.futures import ThreadPoolExecutor

class TestLoad:
    def test_concurrent_requests(self):
        """Test service under concurrent load"""
        def make_request():
            response = requests.get("http://localhost:8000/health")
            return response.status_code
        
        # Test with 100 concurrent requests
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(result == 200 for result in results)
        
        # Response time should be under 1 second
        assert max(results) < 1000  # milliseconds
```

## Code Quality and Standards

### 1. Code Formatting

```bash
# Format code
make format

# Check formatting
make format-check

# Auto-fix issues
make lint-fix
```

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### 2. Static Analysis

```bash
# Run static analysis
make lint

# Security scanning
make security-scan

# Dependency vulnerability check
make check-vulnerabilities
```

#### Linting Configuration
```yaml
# pyproject.toml
[tool.ruff]
line-length = 88
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
]
ignore = ["E501"]  # line too long (handled by black)

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 3. Documentation Standards

```bash
# Generate documentation
make docs

# Check documentation links
make docs-check

# Validate API documentation
make docs-validate
```

#### Documentation Structure
```markdown
# services/my-new-service/README.md
# My New Service

## Overview
Brief description of the service purpose and functionality.

## API Reference
### Endpoints
- `GET /health` - Health check
- `POST /data` - Create data
- `GET /data/{id}` - Get data

## Configuration
### Environment Variables
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)

## Development
### Running Locally
```bash
cd services/my-new-service
python -m uvicorn main:app --reload
```

### Testing
```bash
pytest tests/
```
```

## Deployment Workflows

### 1. Local Development Deployment

```bash
# Start all services
make dev-up

# Start specific service
make dev-up SERVICE=my-new-service

# View logs
make logs SERVICE=my-new-service

# Stop services
make dev-down
```

#### Development Docker Compose
```yaml
# docker-compose.override.yml (development)
version: '3.8'

services:
  my-new-service:
    build:
      args:
        - ENVIRONMENT=development
    volumes:
      - ./services/my-new-service:/app:ro
      - ./configs:/app/configs:ro
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    ports:
      - "8003:8000"  # Expose for local development
```

### 2. Staging Deployment

```bash
# Deploy to staging
make deploy-staging

# Verify deployment
make health-check ENVIRONMENT=staging

# Rollback if needed
make rollback-staging
```

#### Staging Configuration
```yaml
# configs/environments/staging.yaml
services:
  my-new-service:
    replicas: 2
    environment: staging
    health_check_interval: 30
    
infrastructure:
  monitoring:
    enabled: true
    metrics_retention: "7d"
```

### 3. Production Deployment

```bash
# Deploy to production
make deploy-production

# Blue-green deployment
make deploy-production-strategy=blue-green

# Canary deployment
make deploy-production-strategy=canary PERCENTAGE=10
```

#### Production Docker Compose
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  my-new-service:
    image: xnai/my-new-service:${VERSION:-latest}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 4. CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy Service

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: make test SERVICE=my-new-service
      - name: Run linting
        run: make lint SERVICE=my-new-service
      - name: Run security scan
        run: make security-scan SERVICE=my-new-service

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t xnai/my-new-service:${{ github.sha }} ./services/my-new-service
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push xnai/my-new-service:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to staging
        run: |
          # Deployment logic here
          make deploy-staging VERSION=${{ github.sha }}
```

## Monitoring and Debugging

### 1. Service Monitoring

```bash
# View service metrics
make metrics SERVICE=my-new-service

# View logs
make logs SERVICE=my-new-service

# Health check
make health-check SERVICE=my-new-service
```

#### Monitoring Configuration
```yaml
# configs/monitoring/my-new-service.yaml
monitoring:
  metrics:
    enabled: true
    endpoint: /metrics
    port: 8002
    labels:
      service: my-new-service
      environment: development
  
  health_check:
    endpoint: /health
    interval: 30s
    timeout: 5s
    retries: 3
  
  alerts:
    - name: service_down
      condition: up{service="my-new-service"} == 0
      severity: critical
      message: "My New Service is down"
```

### 2. Distributed Tracing

```python
# services/my-new-service/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing():
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    return tracer
```

### 3. Debugging Tools

```bash
# Debug service
make debug SERVICE=my-new-service

# Profile service
make profile SERVICE=my-new-service

# Memory analysis
make memory-analysis SERVICE=my-new-service
```

#### Debug Configuration
```yaml
# configs/debug/my-new-service.yaml
debug:
  enabled: true
  profiler:
    enabled: true
    endpoint: /debug/pprof
  memory_profiler:
    enabled: true
    interval: 60s
  request_logging:
    enabled: true
    level: debug
    include_body: false
```

## Troubleshooting Guide

### Common Issues

#### 1. Service Won't Start
```bash
# Check service logs
make logs SERVICE=my-new-service

# Check configuration
make config-validate SERVICE=my-new-service

# Check dependencies
make health-check DEPENDENCIES=true
```

#### 2. Database Connection Issues
```bash
# Test database connection
make test-db-connection SERVICE=my-new-service

# Check database logs
make logs SERVICE=postgres

# Verify network connectivity
make network-check SERVICE=my-new-service
```

#### 3. Performance Issues
```bash
# Profile service
make profile SERVICE=my-new-service

# Check resource usage
make resources SERVICE=my-new-service

# Analyze slow queries
make slow-queries SERVICE=my-new-service
```

#### 4. Configuration Issues
```bash
# Validate configuration
make config-validate SERVICE=my-new-service

# Check environment variables
make env-check SERVICE=my-new-service

# Compare with defaults
make config-diff SERVICE=my-new-service
```

### Debug Commands

```bash
# Service-specific debugging
make debug SERVICE=my-new-service COMMAND=shell  # Start shell in container
make debug SERVICE=my-new-service COMMAND=logs   # View real-time logs
make debug SERVICE=my-new-service COMMAND=exec   # Execute command in container

# System-wide debugging
make system-status                    # Check overall system health
make network-status                   # Check network connectivity
make storage-status                   # Check storage health
```

### Emergency Procedures

#### Service Recovery
```bash
# Restart service
make restart SERVICE=my-new-service

# Force restart
make restart SERVICE=my-new-service FORCE=true

# Emergency rollback
make rollback SERVICE=my-new-service VERSION=previous
```

#### Data Recovery
```bash
# Backup data
make backup SERVICE=my-new-service

# Restore data
make restore SERVICE=my-new-service BACKUP_FILE=backup.tar.gz

# Verify data integrity
make verify-data SERVICE=my-new-service
```

## Best Practices

### 1. Development Practices
- **Feature Branches**: Always work on feature branches
- **Small Commits**: Make small, focused commits
- **Code Reviews**: Require code reviews for all changes
- **Test Coverage**: Maintain >80% test coverage

### 2. Deployment Practices
- **Blue-Green Deployments**: Use for zero-downtime deployments
- **Canary Releases**: Test changes with small user groups
- **Rollback Strategy**: Always have a rollback plan
- **Monitoring**: Monitor deployments in real-time

### 3. Security Practices
- **Secrets Management**: Never commit secrets to repository
- **Dependency Scanning**: Regularly scan for vulnerabilities
- **Access Control**: Implement proper access controls
- **Audit Logs**: Maintain audit logs for all changes

### 4. Performance Practices
- **Profiling**: Regularly profile services for performance
- **Caching**: Implement appropriate caching strategies
- **Resource Limits**: Set resource limits and requests
- **Monitoring**: Monitor performance metrics continuously

## Next Steps

1. **Service Development**: Follow the service development workflow
2. **Testing**: Implement comprehensive testing
3. **Documentation**: Maintain up-to-date documentation
4. **Monitoring**: Set up monitoring and alerting
5. **Deployment**: Use the deployment workflows for releases

This guide provides a comprehensive framework for developing and maintaining services in the XNAi Foundation modular architecture. Always refer to the specific service documentation for service-specific details and requirements.