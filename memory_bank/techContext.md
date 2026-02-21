---
block:
  label: tech_context
  description: Technology stack, versions, dependencies, and development environment setup
  chars_limit: 5000
  read_only: false
  tier: core
  priority: 3
created: 2026-02-20
modified: 2026-02-20
version: "1.0"
---

# Tech Context - Xoe-NovAi Foundation Stack

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | Latest | REST API server |
| **Async Runtime** | AnyIO | Python 3.12 | Async task management |
| **LLM** | GGUF/ONNX | Quantized | Local language model |
| **Vector DB** | FAISS/Qdrant | Latest | Semantic search |
| **Cache** | Redis | 7.1.1 | State persistence, caching |
| **Database** | PostgreSQL | 14+ | Data persistence |
| **Reverse Proxy** | Caddy | 2.8 | Load balancing, routing |
| **Container Runtime** | Podman | Latest | Rootless containers |
| **Metrics** | VictoriaMetrics | Latest | Time-series storage (3-4x more efficient than Prometheus) |
| **Documentation** | MkDocs | 1.6.1 + Material 10.0.2 | Knowledge base |

## Stack Constraints

| Constraint | Requirement | Rationale |
|------------|-------------|-----------|
| Torch-free | No PyTorch/Torch/Triton/CUDA | Sovereignty, resource efficiency |
| Python | 3.12-slim containers | Modern async, smaller images |
| Async | AnyIO TaskGroups (never asyncio.gather) | Safer cancellation, structured concurrency |
| Containers | Rootless Podman with `:Z,U` volumes | Security, no root privileges |

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Caddy (main proxy) | 8000 | Public API |
| MkDocs (internal) | 8001 | Internal KB |
| VictoriaMetrics | 8428 | Time-series metrics |
| Redis | 6379 | Cache/state |
| PostgreSQL | 5432 | Primary DB |
| Semantic Search | 8000 | RAG queries |
| Agent Bus | 6379 | Redis Streams |
| Consul | 8500 | Service discovery |
| Vikunja | 3456 | Task management |

## Development Environment

### Local Setup
```bash
# Create isolated Python environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt
pip install -r requirements-crawl.txt

# Start development services
docker-compose up -d
make mkdocs-serve
```

### Development Tools

| Tool | Purpose |
|------|---------|
| VS Code | Code editor with Python/Docker extensions |
| pytest | Testing with coverage reporting |
| Black, isort, flake8 | Linting and formatting |
| Git + pre-commit | Version control with hooks |
| Podman | Rootless container runtime |

### Database Setup
```sql
CREATE DATABASE xnai_foundation;
CREATE USER xnai WITH PASSWORD 'secure_password';
GRANT ALL ON DATABASE xnai_foundation TO xnai;
```

## Dependency Groups

| File | Purpose |
|------|---------|
| `requirements.txt` | Core dependencies |
| `requirements-api.txt` | API server dependencies |
| `requirements-crawl.txt` | Web crawling dependencies |
| `pyproject.toml` | Project metadata and dev dependencies |

## Security Posture

### Zero-Telemetry Architecture
- No external data transmission
- No phone-home mechanisms
- No usage tracking
- Air-gap capable (works completely offline)

### Container Security

| Aspect | Implementation |
|--------|----------------|
| Rootless Execution | Services run as UID 1001 |
| Read-Only Filesystems | Immutable runtime |
| No New Privileges | CAP_DROP all |
| Resource Limits | Memory, CPU, file descriptor limits |
| Network Isolation | Private bridge network |

### Data Security

| Aspect | Implementation |
|--------|----------------|
| Encryption at Rest | Database encryption |
| Encryption in Transit | TLS for all external communication |
| Secret Management | Encrypted config files |
| Access Control | Role-based service access |

### Compliance

| Tool | Purpose |
|------|---------|
| Syft | SBOM generation for component tracking |
| Grype | CVE scanning for vulnerability detection |
| Trivy | Configuration scanning for secrets/misconfig |

## Related Documents

- `systemPatterns.md` - Architecture patterns
- `OPERATIONS.md` - Operational procedures
- `AGENTS.md` - Agent constraints

---
**Last Updated**: 2026-02-20
**Owner**: Architect
