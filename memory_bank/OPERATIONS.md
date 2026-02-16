# Operations Guide - Building, Testing, and Deploying

**Last Updated**: 2026-02-14  
**Consolidates**: mkdocs-commands, documentation-system-implementation, agent_capabilities

---

## 🚀 COMMON OPERATIONS

### Development Environment Setup
```bash
# Create and activate venv
python3.13 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt          # Core
pip install -r requirements-api.txt      # API server
pip install -r requirements-chainlit.txt # Web UI
pip install -r requirements-crawl.txt    # Web crawler
pip install -r requirements-curation_worker.txt # Curation

# Optional: Verify installation
python -c "import fastapi, redis, pytest; print('✓ All imports successful')"
```

### Building Docker Images
```bash
# Build all images
make build

# Build specific service
docker build -t xnai/rag-api:latest -f Dockerfile.base .

# Build with buildkit cache
DOCKER_BUILDKIT=1 docker build --cache-from type=local -f Dockerfile.base .

# Rebuild from scratch (clean)
make clean-images
make build
```

### Running Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs for a service
docker-compose logs -f rag-api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Running Tests
```bash
# Activate venv first
source venv/bin/activate

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_circuit_breaker_chaos.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_circuit_breaker_chaos.py::test_circuit_state_transitions -v

# Run with output
pytest -s tests/test_circuit_breaker_chaos.py
```

### Code Quality
```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Run pre-commit hooks
pre-commit run --all-files
```

---

## 📚 DOCUMENTATION SYSTEM

### MkDocs - Documentation Serving

#### Start Internal Knowledge Base (Primary)
```bash
# Serves on http://localhost:8001
make mkdocs-serve
# Or directly:
mkdocs serve -f mkdocs-internal.yml -a localhost:8001
```

#### Serve Public Documentation
```bash
# Serves on http://localhost:8000
make mkdocs-serve-public
# Or directly:
mkdocs serve -f mkdocs.yml -a localhost:8000
```

#### Build Documentation for Deployment
```bash
# Build both internal and public
make mkdocs-build

# Build only internal
mkdocs build -f mkdocs-internal.yml -d site-internal/

# Build only public
mkdocs build -f mkdocs.yml -d site/
```

#### Documentation Structure
```
docs/               - Public documentation (GitHub Pages)
internal_docs/      - Internal knowledge base (employees only)
  ├── 00-system/           - System genealogy, strategy
  ├── 01-strategic-planning/ - PILLARS, roadmaps, indices
  ├── 02-research-lab/       - Research findings
  ├── 03-infrastructure-ops/ - Deployment, incidents
  ├── 04-code-quality/       - Audits, implementation guides
  ├── 05-client-projects/    - Client project templates
  ├── 06-team-knowledge/     - Team knowledge base
  └── 07-archives/           - Historical records
```

#### Adding Documentation
1. Create markdown file in appropriate directory
2. Update `mkdocs.yml` (public) or `mkdocs-internal.yml` (internal)
3. Add to nav section with proper hierarchy
4. Run `mkdocs serve` to verify
5. Commit both markdown and yml files

#### Search Functionality
- Full-text search available in web UI (🔍 icon)
- Works on both public and internal docs
- Instant search as you type
- Filters by page titles and content

### Makefile Documentation Targets

| Target | Purpose | Command |
|--------|---------|---------|
| mkdocs-serve | Serve internal KB on 8001 | `make mkdocs-serve` |
| mkdocs-serve-public | Serve public docs on 8000 | `make mkdocs-serve-public` |
| mkdocs-build | Build both static sites | `make mkdocs-build` |
| docs-system | Show doc system status | `make docs-system` |

---

## 🔄 DEPLOYMENT WORKFLOW

### Pre-Deployment Checklist
```bash
# 1. Verify tests pass
pytest tests/ --cov=app

# 2. Check code quality
flake8 app/
black --check app/
isort --check app/

# 3. Verify no secrets in code
trivy config .
grype .

# 4. Build images
make build

# 5. Test deployment
docker-compose up -d
curl http://localhost:8000/health  # Should return 200

# 6. Stop before real deploy
docker-compose down
```

### Production Deployment
```bash
# 1. Tag version
git tag v0.1.0
git push origin v0.1.0

# 2. Build with version
docker build --label version=0.1.0 -t xnai/rag-api:0.1.0 .

# 3. Push to registry (if applicable)
docker push xnai/rag-api:0.1.0

# 4. Deploy via compose
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify health
for i in {1..30}; do
  if curl -f http://localhost:8000/health; then
    echo "✓ API healthy"
    break
  fi
  sleep 1
done

# 6. Monitor logs
docker-compose logs -f --tail=100
```

---

## 🛠️ TROUBLESHOOTING

### Common Issues & Solutions

#### Docker Build Failures
```bash
# Clear cache and rebuild
docker system prune -a
make clean-images
make build

# Build with verbose output
docker build --progress=plain -f Dockerfile.base .
```

#### Permission Issues
```bash
# Fix ownership
sudo chown -R $USER:$USER /data /logs /secrets

# Fix directory permissions
chmod 755 /data /logs /secrets
chmod 600 /secrets/*
```

#### Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Verify dependencies
docker network ls  # Check xnai_network exists

# Inspect container
docker inspect container-name

# Recreate from scratch
docker-compose down -v
docker-compose up -d
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# See what's using memory
docker-compose exec rag-api ps aux --sort=-%mem

# Clear cache
docker-compose exec redis redis-cli FLUSHALL

# Monitor zRAM
watch -n1 'zramctl; echo "---"; swapon -s'
```

#### Redis Connection Issues
```bash
# Test Redis connection
docker-compose exec redis redis-cli ping  # Should return PONG

# Check Redis logs
docker-compose logs redis

# Clear and rebuild Redis
docker-compose down
rm -rf data/redis/
docker-compose up -d redis
```

---

## 📊 MONITORING & DIAGNOSTICS

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health

# Check specific service
curl http://localhost:8000/health/redis
curl http://localhost:8000/health/postgres

# Get detailed metrics
curl http://localhost:8000/metrics
```

### Performance Profiling
```bash
# Profile memory during test
python -m memory_profiler app/XNAi_rag_app/main.py

# Profile CPU during test
python -m cProfile -s cumtime app/XNAi_rag_app/main.py

# Generate flame graph
py-spy record -o profile.svg -- python app/main.py
```

### Log Analysis
```bash
# Follow API logs
docker-compose logs -f rag-api

# Search logs for errors
docker-compose logs | grep ERROR

# Get last N lines
docker-compose logs --tail=100

# Filter by service and follow
docker-compose logs -f --tail=50 redis postgres
```

### Resource Monitoring
```bash
# Real-time resource usage
docker stats --no-stream

# Monitor over time
watch -n2 docker stats

# Check disk usage
df -h
du -sh /data/*

# Check memory with zRAM
free -h
zramctl
```

---

## 🤖 AGENT CAPABILITIES REFERENCE

### AI Team Personas

| Persona | Role | Best For | Command/Interface |
|:--- | :--- | :--- | :--- |
| **Human Director** | Vision & Strategy | Strategic direction, final decisions | User input |
| **Cline** | Code & Execution | Deep refactors, debugging, audits | VS Code + Cline Extension |
| **Grok** | Research & Strategy | Strategic Mastermind, research synthesis | Grok.com / Vikunja |
| **Gemini** | Ground Truth & Scribe | Filesystem management, auditing, documentation | Gemini CLI |
| **Copilot** | Tactical Support | Quick code gen, support execution | Copilot tool / VS Code |
| **OpenCode** | Multi-Model Research | Research synthesis, alternative perspectives | Terminal execution |

### Technical Identity Mapping
Usage of specific technical accounts (e.g., `Copilot-Raptor-27`, `Cline-X`) is documented in `docs/AGENT_ACCOUNT_PROTOCOL.md` for quota and audit purposes.

### How to Use Agents

#### Copilot CLI (This Tool)
```bash
# Direct task execution
copilot "Create integration test for service X"

# Run bash commands
copilot "Install dependencies: pip install redis"

# File operations
copilot "Add error handling to file X"

# Research tasks
copilot "Research best practices for Y"
```

#### Cline (VS Code Integration)
1. Open VS Code with Cline extension
2. Type task in chat window
3. Cline reads/edits files as needed
4. Execute commands in terminal
5. Verify changes in editor

#### Gemini CLI (Terminal)
```bash
# Run automation scripts
gemini-cli "Deploy stack to production"

# System diagnostics
gemini-cli "Check all service health"

# File operations
gemini-cli "Backup database"
```

#### OpenCode (Multi-Model)
```bash
# Research comparison
opencode "Compare Kimi K2.5 vs GPT-5 Mini for task X"

# Generate analysis
opencode "Analyze performance metrics"

# Multi-model validation
opencode "Get consensus from 3 models on problem X"
```

---

## 📋 MAINTENANCE SCHEDULE

### Daily
- [ ] Monitor system health via `docker stats`
- [ ] Check error logs for exceptions
- [ ] Verify services responding to health checks

### Weekly
- [ ] Run full test suite
- [ ] Review documentation for updates needed
- [ ] Check disk space usage
- [ ] Rotate logs if needed

### Monthly
- [ ] Security updates (Trivy, Grype)
- [ ] Dependency updates (pip, npm)
- [ ] Performance review
- [ ] Memory profiling

### Quarterly
- [ ] Full system audit
- [ ] Security penetration testing
- [ ] Architecture review
- [ ] Roadmap planning

---

## 🔗 QUICK REFERENCE

### Essential Commands
```bash
# Start development
make dev                    # Start all services + docs

# Run tests
pytest tests/ -v           # Verbose test output
pytest --cov=app           # With coverage

# Build & deploy
make build                  # Build images
make deploy                 # Deploy stack

# View documentation
open http://localhost:8001  # Internal KB
open http://localhost:8000  # Public docs

# Monitor
docker stats                # Real-time resource usage
docker-compose logs -f      # Streaming logs
```

### Environment Variables
```bash
# Development
DEBUG_MODE=true
LOG_LEVEL=DEBUG
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://xnai:password@localhost:5432/xnai

# Production (from .env.prod)
# Do not commit passwords to version control!
```

---

**Last Review**: 2026-02-14  
**Next Review**: Monthly  
**Owner**: DevOps / Infrastructure Team
