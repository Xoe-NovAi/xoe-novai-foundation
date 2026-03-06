# XNAi Foundation: Service Decomposition Framework

**Version**: 1.0.0  
**Date**: 2026-02-27  
**Status**: Design Phase  
**Purpose**: Define service boundaries and decomposition patterns for modular architecture

## Overview

This framework provides a systematic approach to decomposing the XNAi Foundation monolithic services into focused, independently deployable microservices while maintaining the existing sophisticated infrastructure.

## Current Service Analysis

### Core Services (Current)
- **RAG API** (`rag`): FastAPI backend with vector search
- **UI** (`ui`): Chainlit frontend with voice interface
- **Crawler** (`crawler`): Ingestion engine for content
- **Curation Worker** (`curation_worker`): Knowledge refinement
- **MKDocs** (`mkdocs`): Documentation system
- **Vikunja** (`vikunja`): Project management
- **Supporting Services**: Consul, Redis, Qdrant, VictoriaMetrics, Grafana, Caddy

### Service Dependencies
```
UI → RAG API → Vector DB (Qdrant)
Crawler → RAG API → Vector DB
Curation Worker → RAG API → Vector DB
MKDocs → Static Content
Vikunja → PostgreSQL
Monitoring Stack → All Services
```

## Service Decomposition Strategy

### 1. Core Domain Services

#### 1.1 RAG Core Service
**Purpose**: Core retrieval and generation logic
**Responsibilities**:
- Vector search operations
- LLM orchestration
- Query processing
- Response generation

**Boundaries**:
- Input: Query requests
- Output: Generated responses
- Dependencies: Vector DB, LLM providers

#### 1.2 Knowledge Management Service
**Purpose**: Content ingestion and curation
**Responsibilities**:
- Document processing
- Content extraction
- Knowledge curation
- Quality assessment

**Boundaries**:
- Input: Raw documents
- Output: Curated knowledge
- Dependencies: Storage, RAG Core

#### 1.3 User Interface Service
**Purpose**: User interaction and presentation
**Responsibilities**:
- Web interface
- Voice interface
- Authentication
- Session management

**Boundaries**:
- Input: User requests
- Output: UI responses
- Dependencies: RAG Core, Authentication

### 2. Infrastructure Services

#### 2.1 Service Discovery & Configuration
**Purpose**: Service registration and configuration management
**Current**: Consul
**Enhancement**: Configuration templating, environment-specific overrides

#### 2.2 Message Bus
**Purpose**: Inter-service communication
**Current**: Redis Streams
**Enhancement**: Enhanced event schemas, dead letter queues

#### 2.3 Monitoring & Observability
**Purpose**: System health and performance monitoring
**Current**: VictoriaMetrics + Grafana
**Enhancement**: Service-specific metrics, distributed tracing

### 3. Supporting Services

#### 3.1 Authentication & Authorization
**Purpose**: User and service authentication
**Current**: JWT-based
**Enhancement**: OAuth integration, service-to-service auth

#### 3.2 Storage Service
**Purpose**: Document and data storage
**Current**: Local filesystem + PostgreSQL
**Enhancement**: Object storage abstraction, multi-backend support

## Service Communication Patterns

### 1. Synchronous Communication
- **Pattern**: REST API with JSON
- **Use Cases**: User requests, service queries
- **Implementation**: FastAPI with OpenAPI specs

### 2. Asynchronous Communication
- **Pattern**: Event-driven via Redis Streams
- **Use Cases**: Document processing, notifications
- **Implementation**: Redis Streams with consumer groups

### 3. Service Discovery
- **Pattern**: Consul service registry
- **Use Cases**: Dynamic service location
- **Implementation**: Consul DNS + API

## Configuration Management

### 1. Configuration Hierarchy
```
Base Configuration (common)
├── Environment Overrides (dev/staging/prod)
└── Service-Specific Overrides
```

### 2. Configuration Sources
- **Environment Variables**: Runtime configuration
- **Consul KV**: Service discovery and config
- **YAML Files**: Static configuration
- **Secrets Management**: Sensitive data

### 3. Configuration Schema
```yaml
service:
  name: rag-core
  version: 1.0.0
  environment: development
  
api:
  host: 0.0.0.0
  port: 8000
  workers: 1
  
dependencies:
  vector_db:
    host: qdrant
    port: 6333
  llm_providers:
    - name: openai
      endpoint: https://api.openai.com
      model: gpt-4
```

## Service Deployment Patterns

### 1. Container Strategy
- **Base Image**: Shared base with common dependencies
- **Service Image**: Service-specific additions
- **Multi-stage Builds**: Optimized for size and security

### 2. Orchestration
- **Development**: Docker Compose with service isolation
- **Production**: Kubernetes with Helm charts
- **Standalone**: Single-container deployment

### 3. Scaling Strategy
- **Horizontal**: Service-specific scaling
- **Vertical**: Resource allocation per service
- **Auto-scaling**: Based on metrics and load

## Migration Strategy

### Phase 1: Service Identification
- [ ] Map current service boundaries
- [ ] Identify service dependencies
- [ ] Define service contracts

### Phase 2: Infrastructure Preparation
- [ ] Enhance service discovery
- [ ] Implement configuration management
- [ ] Set up monitoring for new services

### Phase 3: Service Extraction
- [ ] Extract RAG Core service
- [ ] Extract Knowledge Management
- [ ] Extract User Interface components

### Phase 4: Integration & Testing
- [ ] Implement service communication
- [ ] Set up integration testing
- [ ] Validate service contracts

### Phase 5: Deployment & Monitoring
- [ ] Deploy to development environment
- [ ] Monitor service interactions
- [ ] Optimize performance

## Benefits

### 1. Development Benefits
- **Independent Development**: Teams can work on different services
- **Technology Flexibility**: Different services can use different tech stacks
- **Faster Deployment**: Services can be deployed independently

### 2. Operational Benefits
- **Improved Reliability**: Service isolation prevents cascading failures
- **Better Scalability**: Services can be scaled independently
- **Enhanced Monitoring**: Service-specific metrics and logging

### 3. Business Benefits
- **Faster Time-to-Market**: Parallel development and deployment
- **Reduced Risk**: Smaller, focused changes
- **Improved Maintainability**: Clear service boundaries

## Implementation Guidelines

### 1. Service Design Principles
- **Single Responsibility**: Each service has one clear purpose
- **Loose Coupling**: Minimal dependencies between services
- **High Cohesion**: Related functionality grouped together

### 2. API Design Principles
- **RESTful**: Use REST conventions for HTTP APIs
- **Versioning**: Implement API versioning strategy
- **Documentation**: Maintain OpenAPI specifications

### 3. Data Management
- **Database per Service**: Each service owns its data
- **Event Sourcing**: Use events for data synchronization
- **CQRS**: Separate read and write models where appropriate

## Next Steps

1. **Service Boundary Analysis**: Detailed analysis of current service boundaries
2. **API Contract Design**: Define service interfaces and contracts
3. **Infrastructure Enhancement**: Enhance existing infrastructure for microservices
4. **Pilot Implementation**: Implement one service as proof of concept

## References

- [Microservices.io Patterns](https://microservices.io/patterns/)
- [12-Factor App Methodology](https://12factor.net/)
- [Domain-Driven Design](https://dddcommunity.org/)