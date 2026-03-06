# XNAi Foundation: Branching Strategy for Component Isolation

**Version**: 1.0.0  
**Date**: 2026-02-27  
**Status**: Design Phase  
**Purpose**: Define Git branching strategy for modular service development

## Overview

This branching strategy provides a systematic approach to managing the development, testing, and deployment of modular services while maintaining the integrity of the existing monolithic architecture during the transition period.

## Current Repository Structure

### Existing Branches
- **main**: Production-ready code
- **dev**: Development branch with latest features
- **feature/***: Feature branches for specific enhancements
- **hotfix/***: Emergency fixes for production issues

### Current Complexity
- **24 services** with sophisticated infrastructure
- **Complex Docker Compose** with service mesh
- **Advanced monitoring** and observability
- **Multi-environment** deployment configurations

## Proposed Branching Strategy

### 1. Main Branch Strategy

#### 1.1 Trunk-Based Development
```
main (production-ready)
├── dev (integration branch)
├── release/* (release preparation)
└── hotfix/* (emergency fixes)
```

#### 1.2 Service-Specific Branches
```
services/
├── rag-core/
│   ├── main (service production)
│   ├── dev (service development)
│   └── feature/* (service features)
├── knowledge-mgmt/
│   ├── main (service production)
│   ├── dev (service development)
│   └── feature/* (service features)
└── ui-service/
    ├── main (service production)
    ├── dev (service development)
    └── feature/* (service features)
```

### 2. Branch Naming Conventions

#### 2.1 Service Branches
```
service-{service-name}-{branch-type}
Examples:
- service-rag-core-main
- service-rag-core-dev
- service-knowledge-mgmt-main
- service-ui-service-dev
```

#### 2.2 Feature Branches
```
feature-{service-name}-{feature-description}
Examples:
- feature-rag-core-vector-search-optimization
- feature-knowledge-mgmt-document-parsing
- feature-ui-service-voice-interface
```

#### 2.3 Integration Branches
```
integration-{phase}-{description}
Examples:
- integration-phase1-configuration-management
- integration-phase2-service-discovery
- integration-phase3-data-synchronization
```

## Development Workflow

### 1. Service Development Workflow

#### 1.1 Creating a New Service Branch
```bash
# Create service development branch
git checkout main
git pull origin main
git checkout -b service-my-new-service-dev

# Push to remote with tracking
git push -u origin service-my-new-service-dev
```

#### 1.2 Feature Development
```bash
# Create feature branch from service dev
git checkout service-my-new-service-dev
git checkout -b feature-my-new-service-query-optimization

# Develop feature
# ... development work ...

# Commit changes
git add .
git commit -m "feat: optimize query processing in my-new-service"

# Push to remote
git push -u origin feature-my-new-service-query-optimization
```

#### 1.3 Feature Integration
```bash
# Merge feature into service dev branch
git checkout service-my-new-service-dev
git merge feature-my-new-service-query-optimization
git push origin service-my-new-service-dev

# Clean up feature branch
git branch -d feature-my-new-service-query-optimization
git push origin --delete feature-my-new-service-query-optimization
```

### 2. Cross-Service Integration

#### 2.1 Integration Testing Branch
```bash
# Create integration branch
git checkout main
git checkout -b integration-phase1-configuration-management

# Merge service branches
git merge service-configuration-manager-dev
git merge service-service-discovery-dev

# Resolve conflicts and test
# ... integration testing ...

# Push integration branch
git push -u origin integration-phase1-configuration-management
```

#### 2.2 Multi-Service Feature Development
```bash
# For features spanning multiple services
git checkout main
git checkout -b feature-cross-service-authentication

# Merge individual service changes
git merge service-auth-service-dev
git merge service-api-gateway-dev
git merge service-ui-service-dev

# Test integration
# ... comprehensive testing ...

# Push cross-service feature
git push -u origin feature-cross-service-authentication
```

## Merge Strategy

### 1. Pull Request Workflow

#### 1.1 Service Development PR
```bash
# Create PR from service dev to main
# Source: service-<name>-dev
# Target: main
# Title: "Service <name>: Development updates"
# Description: List of changes and testing performed
```

#### 1.2 Feature PR
```bash
# Create PR from feature to service dev
# Source: feature-<name>-<description>
# Target: service-<name>-dev
# Title: "Feature: <description>"
# Description: Feature details, testing, and impact assessment
```

#### 1.3 Integration PR
```bash
# Create PR from integration to main
# Source: integration-<phase>-<description>
# Target: main
# Title: "Integration: <phase> - <description>"
# Description: Integration details, testing, and rollback plan
```

### 2. Merge Requirements

#### 2.1 Automated Checks
- [ ] All tests pass
- [ ] Code coverage > 80%
- [ ] Security scan passes
- [ ] Performance benchmarks met
- [ ] Documentation updated

#### 2.2 Manual Review Requirements
- [ ] Code review by senior developer
- [ ] Architecture review for breaking changes
- [ ] Security review for sensitive changes
- [ ] Performance review for resource-intensive changes

#### 2.3 Deployment Validation
- [ ] Development environment deployment successful
- [ ] Integration tests pass
- [ ] Monitoring and observability configured
- [ ] Rollback procedure documented

## Service Isolation Strategy

### 1. Repository Structure for Services

#### 1.1 Monorepo Structure (Recommended)
```
xoe-novai-foundation/
├── services/
│   ├── rag-core/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── config.yaml
│   │   └── README.md
│   ├── knowledge-mgmt/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── config.yaml
│   │   └── README.md
│   └── ui-service/
│       ├── src/
│       ├── tests/
│       ├── Dockerfile
│       ├── config.yaml
│       └── README.md
├── shared/
│   ├── common/
│   ├── utils/
│   └── schemas/
├── infrastructure/
│   ├── docker-compose.yml
│   ├── configs/
│   └── scripts/
└── docs/
```

#### 1.2 Multi-Repo Structure (Alternative)
```
xoe-novai-foundation/
├── foundation-core/           # Core infrastructure
├── service-rag-core/          # RAG Core service
├── service-knowledge-mgmt/    # Knowledge Management service
├── service-ui/               # UI service
├── shared-libraries/         # Shared components
└── deployment-templates/     # Deployment configurations
```

### 2. Service Dependencies Management

#### 2.1 Dependency Graph
```
Service Dependencies
├── RAG Core
│   ├── Vector DB (Qdrant)
│   ├── LLM Providers
│   └── Cache (Redis)
├── Knowledge Management
│   ├── Document Storage
│   ├── Database (Postgres)
│   └── RAG Core (for validation)
└── UI Service
    ├── RAG Core (for queries)
    ├── Authentication Service
    └── Static Assets
```

#### 2.2 Version Management
```yaml
# services/versions.yaml
services:
  rag-core:
    version: "1.2.0"
    dependencies:
      qdrant: ">=1.8.0"
      redis: ">=7.0.0"
  
  knowledge-mgmt:
    version: "1.1.0"
    dependencies:
      postgres: ">=15.0"
      rag-core: ">=1.2.0"
  
  ui-service:
    version: "1.0.0"
    dependencies:
      rag-core: ">=1.2.0"
      auth-service: ">=1.0.0"
```

## Development Environment Setup

### 1. Local Development Workflow

#### 1.1 Service-Specific Development
```bash
# Clone repository
git clone https://github.com/Xoe-NovAi/xoe-novai-foundation.git
cd xoe-novai-foundation

# Checkout service development branch
git checkout service-<name>-dev

# Set up service-specific environment
make setup SERVICE=<name>

# Start service and dependencies
make dev-up SERVICE=<name>

# Develop and test
# ... development work ...

# Run service tests
make test SERVICE=<name>
```

#### 1.2 Cross-Service Development
```bash
# Checkout integration branch
git checkout integration-<phase>-<description>

# Set up all required services
make setup-all

# Start all services
make dev-up-all

# Develop and test cross-service features
# ... development work ...

# Run integration tests
make test-integration
```

### 2. Continuous Integration

#### 2.1 Service-Specific CI
```yaml
# .github/workflows/service-ci.yml
name: Service CI

on:
  push:
    branches:
      - 'service-*-dev'
      - 'feature-*'
  pull_request:
    branches:
      - 'service-*-dev'

jobs:
  test-service:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [rag-core, knowledge-mgmt, ui-service]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd services/${{ matrix.service }}
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          cd services/${{ matrix.service }}
          pytest tests/
      
      - name: Run linting
        run: |
          cd services/${{ matrix.service }}
          ruff check .
          mypy .
```

#### 2.2 Integration CI
```yaml
# .github/workflows/integration-ci.yml
name: Integration CI

on:
  push:
    branches:
      - 'integration-*'
      - 'main'
  pull_request:
    branches:
      - 'main'

jobs:
  integration-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker
        uses: docker/setup-buildx-action@v2
      
      - name: Build all services
        run: |
          make build-all
      
      - name: Start test environment
        run: |
          make test-up
      
      - name: Run integration tests
        run: |
          make test-integration
      
      - name: Run performance tests
        run: |
          make test-performance
      
      - name: Cleanup
        run: |
          make test-down
```

## Deployment Strategy

### 1. Service-Specific Deployment

#### 1.1 Development Deployment
```bash
# Deploy specific service to development
make deploy-dev SERVICE=<name> VERSION=<version>

# Verify deployment
make health-check SERVICE=<name> ENVIRONMENT=dev
```

#### 1.2 Staging Deployment
```bash
# Deploy service to staging
make deploy-staging SERVICE=<name> VERSION=<version>

# Run staging tests
make test-staging SERVICE=<name>

# Validate integration
make integration-test ENVIRONMENT=staging
```

#### 1.3 Production Deployment
```bash
# Deploy service to production
make deploy-production SERVICE=<name> VERSION=<version>

# Monitor deployment
make monitor-deployment SERVICE=<name>

# Validate production
make health-check SERVICE=<name> ENVIRONMENT=prod
```

### 2. Blue-Green Deployment

#### 2.1 Service Blue-Green
```bash
# Deploy to green environment
make deploy-green SERVICE=<name> VERSION=<version>

# Run health checks
make health-check SERVICE=<name> ENVIRONMENT=green

# Switch traffic
make switch-traffic ENVIRONMENT=green

# Monitor and validate
make monitor-production SERVICE=<name>

# Cleanup blue environment
make cleanup-blue SERVICE=<name>
```

#### 2.2 Canary Deployment
```bash
# Deploy to canary
make deploy-canary SERVICE=<name> VERSION=<version> PERCENTAGE=10

# Monitor canary metrics
make monitor-canary SERVICE=<name>

# Gradually increase traffic
make increase-canary-traffic SERVICE=<name> PERCENTAGE=25
make increase-canary-traffic SERVICE=<name> PERCENTAGE=50
make increase-canary-traffic SERVICE=<name> PERCENTAGE=100

# Complete deployment
make complete-canary SERVICE=<name>
```

## Rollback Strategy

### 1. Service Rollback

#### 1.1 Immediate Rollback
```bash
# Rollback specific service
make rollback SERVICE=<name> VERSION=<previous-version>

# Verify rollback
make health-check SERVICE=<name>

# Monitor for issues
make monitor-rollback SERVICE=<name>
```

#### 1.2 Database Rollback
```bash
# Rollback database changes
make rollback-database SERVICE=<name> MIGRATION=<previous-migration>

# Verify data integrity
make verify-data SERVICE=<name>

# Update service configuration
make update-config SERVICE=<name>
```

### 2. Integration Rollback

#### 2.1 Integration Rollback
```bash
# Rollback integration changes
git checkout main
git pull origin main
git checkout -b rollback-integration-<date>
git revert <integration-commit-hash>

# Test rollback
make test-integration

# Deploy rollback
make deploy-production VERSION=<rollback-version>
```

#### 2.2 Emergency Rollback
```bash
# Emergency rollback all services
make emergency-rollback

# Verify system health
make health-check-all

# Investigate issues
make investigate-issues

# Plan recovery
make plan-recovery
```

## Best Practices

### 1. Branch Management

#### 1.1 Branch Lifecycle
- **Create branches** for every feature, bug fix, or enhancement
- **Keep branches short-lived** (1-2 weeks maximum)
- **Merge frequently** to avoid large merge conflicts
- **Delete branches** after successful merge

#### 1.2 Commit Messages
```bash
# Use conventional commits
feat: add vector search optimization to rag-core
fix: resolve authentication timeout in ui-service
docs: update api documentation for knowledge-mgmt
refactor: improve code structure in shared utilities
test: add integration tests for cross-service authentication
chore: update dependencies in all services
```

#### 1.3 Pull Request Guidelines
- **Small, focused PRs** (max 400 lines of changes)
- **Clear descriptions** with context and impact
- **Link to issues** when applicable
- **Include testing instructions**
- **Update documentation** for user-facing changes

### 2. Code Quality

#### 2.1 Code Review Process
- **Mandatory code review** for all changes
- **Architecture review** for breaking changes
- **Security review** for sensitive changes
- **Performance review** for resource-intensive changes

#### 2.2 Testing Requirements
- **Unit tests** for all new functionality
- **Integration tests** for cross-service features
- **End-to-end tests** for user workflows
- **Performance tests** for critical paths

#### 2.3 Documentation Standards
- **API documentation** for all public interfaces
- **Service documentation** for deployment and operation
- **Architecture documentation** for design decisions
- **Troubleshooting guides** for common issues

### 3. Security Considerations

#### 3.1 Branch Protection
```yaml
# GitHub branch protection rules
protection_rules:
  main:
    required_reviews: 2
    dismiss_stale_reviews: true
    require_code_owner_reviews: true
    required_status_checks:
      - "test-service"
      - "security-scan"
      - "performance-test"
  
  service-*-dev:
    required_reviews: 1
    required_status_checks:
      - "test-service"
      - "lint-check"
```

#### 3.2 Secrets Management
- **Never commit secrets** to any branch
- **Use environment variables** for configuration
- **Implement secret rotation** procedures
- **Audit access** to sensitive branches

#### 3.3 Security Scanning
```yaml
# Security scanning in CI
security_scan:
  - name: Dependency vulnerability scan
    run: make security-scan SERVICE=${{ matrix.service }}
  
  - name: Code security analysis
    run: make code-security-analysis SERVICE=${{ matrix.service }}
  
  - name: Container security scan
    run: make container-security-scan SERVICE=${{ matrix.service }}
```

## Migration Timeline

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up service-specific branch structure
- [ ] Create service templates and generators
- [ ] Implement branch protection rules
- [ ] Set up service-specific CI/CD pipelines

### Phase 2: Service Development (Weeks 3-6)
- [ ] Extract RAG Core service with proper branching
- [ ] Extract Knowledge Management service
- [ ] Extract User Interface service
- [ ] Implement cross-service integration testing

### Phase 3: Integration (Weeks 7-8)
- [ ] Create integration branches for service communication
- [ ] Implement data synchronization between services
- [ ] Set up comprehensive integration testing
- [ ] Validate end-to-end workflows

### Phase 4: Production Readiness (Weeks 9-12)
- [ ] Implement blue-green deployment strategy
- [ ] Set up canary deployment capabilities
- [ ] Create comprehensive rollback procedures
- [ ] Validate production deployment workflows

## Conclusion

This branching strategy provides a robust foundation for managing the modular architecture development while maintaining the stability and reliability of the existing system. By implementing service-specific branches, comprehensive testing, and automated deployment workflows, the XNAi Foundation can successfully transition to a modular architecture while minimizing risk and maintaining development velocity.

The strategy balances the need for isolation and independence of services with the requirement for coordination and integration, ensuring that the modular architecture delivers on its promises of scalability, maintainability, and flexibility.