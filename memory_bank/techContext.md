---
block:
  label: tech_context
  description: Technology stack, versions, dependencies, and development environment setup
  chars_limit: 5000
  read_only: false
  tier: core
  priority: 3
created: 2026-02-20
modified: 2026-03-04
version: "1.1"
---

# Tech Context - Xoe-NovAi Foundation Stack

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | Latest | REST API server (Prosopon) |
| **Async Runtime** | AnyIO | Python 3.12 | Structured TaskGroups (No asyncio.gather) |
| **Gnostic Models**| Krikri-8B-Instruct | Q5_K_M GGUF | Local Sovereign Reasoning |
| **Linguistic Model**| Ancient-Greek-BERT | 768-dim | Zipped Logos / RDS Anchoring |
| **Router** | Logosforge (OpenPipe) | 1.0.0 | Intelligent Routing & Oikonomia |
| **Vector DB** | Qdrant | Latest | HELLENIC_SCRIBE_CORE collection |
| **Graph DB** | Neo4j / Memgraph | Latest | Gnosis Relationship Mapping |
| **Cache/Bus** | Redis Streams | 7.1.1 | Synapses / Agent Bus |
| **Reverse Proxy** | Prophetis (Caddy) | 2.8 | Port 80 Routing & TLS |
| **Container Runtime** | Podman | Latest | Rootless UID 1000 containers |

## Service Ports

| Service | Port | Layer | Purpose |
|:---|:---|:---|:---|
| Prophetis (Caddy) | 80 / 443 | Layer 1 | Main Gnostic Gateway |
| Prosopon (FastAPI) | 8006 | Layer 1 | Primary API Service |
| Orchestrion (MCP) | 8005 | Layer 3 | Central Reasoning & RCF |
| Synapses (Redis) | 6379 | Layer 2 | High-Throughput Bus |
| Silicon Oracle (Qdrant)| 6333 | Layer 0 | Vector Gnosis DB |
| Silicon Oracle (Neo4j) | 7474 | Layer 0 | Graph Gnosis DB |
| MkDocs (Internal) | 8001 | Layer 3 | Internal Knowledge Base |

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
| proxychains4 | 🌐 Regional bypass for API retrieval |

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

### Zero-Telemetry & Sovereignty Architecture
- **No external data transmission**: Air-gap capable.
- **Sovereign OAuth**: `oauth_manager.py` uses Fernet-encrypted storage with support for `XNAI_OAUTH_KEY` environment variable injection.
- **Portability Protocol**: All scripts use the Central Path Resolver (`paths.py`) to avoid hardcoded absolute paths.
### CLI Stability (Crash Remediation)
- **Memory Allocation**: Set `export NODE_OPTIONS="--max-old-space-size=8192"` to prevent Node.js OOM during high-context operations.
- **Context Management**: Mandatory `/compress` when context exceeds 400K tokens.
- **Discovery Safety**: Use sub-agents (e.g., `generalist`) for recursive `grep` or large file reads to prevent CLI OOM.


### Container Security

| Aspect | Implementation |
|--------|----------------|
| Rootless Execution | Services run as UID 1001 |
| Universal Dispatcher | Tool isolation via `/tmp/xnai-instances/` |
| Pulse Filter | Output scrubbing for secrets/PII |
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
**Last Updated**: 2026-03-04 (Metropolis Hardening)
**Owner**: MC-Overseer
