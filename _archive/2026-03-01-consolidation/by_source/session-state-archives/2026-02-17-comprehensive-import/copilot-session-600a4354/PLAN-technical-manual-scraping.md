# Technical Manual Scraping & Knowledge Curation Job Plan

**Session**: 600a4354-1bd2-4f7c-aacd-366110f48273  
**Mode**: [[PLAN]]  
**Created**: 2026-02-16T23:00:00Z  
**Status**: PLANNING  
**Owner**: Copilot CLI (orchestration) + Local crawler (execution) + Gemini CLI (synthesis)

---

## Problem Statement

The XNAi Foundation stack depends on critical technical services (Redis, Qdrant, crawl4ai, llama-cpp-python, etc.), but their manuals and documentation are scattered across web resources with diverse formats (HTML, Markdown, PDF, REST API docs, GitHub wikis, etc.). We need:

1. **Systematic scraping** of high-priority technical manuals in order of XOH 16-phase hardening dependencies
2. **Format handling** - Different manuals have different structures (API docs, getting-started guides, API references, etc.)
3. **Queue-based job management** - Use Redis + Vikunja to track scraping jobs, avoid duplicates, enable parallelization
4. **Structured knowledge** - Convert raw HTML/text into vector-indexed knowledge base entries
5. **Fallback strategies** - Handle rate limiting, 404s, authentication, and dynamic content

---

## Project Scope & Approach

### High-Priority Services (Phase 5-6 Dependencies)
Based on XOH 16-phase roadmap, we prioritize by hardening phases:

1. **Phase 5A-5E Foundation Services** (CRITICAL)
   - Redis (job queue, caching, session state)
   - Prometheus + Grafana (observability)
   - PostgreSQL (IAM, task storage)
   - Docker/Podman (containerization)

2. **Phase 6 AI/ML Services** (HIGH)
   - Qdrant (vector database)
   - llama-cpp-python (inference)
   - sentence-transformers (embeddings)
   - crawl4ai (web scraping)

3. **Phase 7-8 Infrastructure** (MEDIUM)
   - OpenTelemetry (tracing)
   - Jaeger (distributed tracing)
   - Helm/Kubernetes patterns (if scaling)

### Scraping Strategy

**Pattern-Based Format Handling**:
- **GitHub Docs**: Clone repository, extract from `/docs/` folder
- **REST API Docs**: Parse Swagger/OpenAPI specs, convert to markdown
- **Official Websites**: Use crawl4ai with JavaScript support for dynamic content
- **README.md files**: Fetch directly from GitHub API
- **Package Docs**: pip-installed packages have bundled docs (`/site-packages/*/docs/`)

**De-duplication & Versioning**:
- Hash-based deduplication (SHA256 of content)
- Version tracking (store URL + commit SHA + scrape date)
- Store in `knowledge/technical_manuals/{service}/{version}/{section}.md`

**Queue-Based Execution**:
- Use Redis queue: `xnai:scrape:jobs:{priority}:pending`
- Store job metadata in Redis + Vikunja tasks
- Rate limiting (1-3 jobs/min per service to avoid blocking)

---

## Workplan

### Phase 1: Infrastructure Setup (1-2 hours)

- [ ] Create scraping job schema (Pydantic) with source, format, retry logic
- [ ] Implement job queue processor (`scripts/technical_manual_scraper.py`)
  - [ ] Queue management (add, dequeue, retry failed jobs)
  - [ ] Format detection (GitHub, REST API, HTML)
  - [ ] De-duplication via content hash
  - [ ] Retry logic with exponential backoff
- [ ] Create format handlers for each source type
  - [ ] GitHub repository handler (clone + extract)
  - [ ] OpenAPI spec handler (parse + convert to markdown)
  - [ ] HTML handler (crawl4ai-based)
  - [ ] README handler (GitHub API)
- [ ] Setup Redis queue keys and Vikunja task templates
- [ ] Create test fixtures for each format

**Deliverables**:
- `scripts/technical_manual_scraper.py` (main orchestrator)
- `scripts/scrapers/github_scraper.py`
- `scripts/scrapers/openapi_scraper.py`
- `scripts/scrapers/html_scraper.py`
- `scripts/scrapers/readme_scraper.py`
- `knowledge/schemas/scraping_job_schema.py`
- `tests/test_manual_scraping_*.py`

### Phase 2: Phase 5A-5E Services (3-4 hours)

**Priority Order** (by XOH 16-phase dependencies):

1. **Redis** (CRITICAL - foundation for job queue itself!)
   - Sources:
     - https://redis.io/documentation (official)
     - https://redis.io/docs/manual/ (detailed manual)
     - GitHub: https://github.com/redis/redis/tree/unstable/docs
   - Sections: Getting Started, Commands Reference, Admin Guide, Persistence
   - Expected: 150-200 KB of documentation

2. **PostgreSQL** (CRITICAL - IAM & task storage)
   - Sources:
     - https://www.postgresql.org/docs/
     - https://github.com/postgres/postgres/tree/master/doc/src/sgml
   - Sections: Installation, Client Apps, SQL Reference, Administration
   - Expected: 500+ KB (large, may split into multiple jobs)

3. **Docker/Podman** (CRITICAL - containerization)
   - Sources:
     - https://docs.docker.com/
     - https://podman.io/docs/
   - Sections: Install, CLI Reference, Compose, Networking
   - Expected: 300+ KB each

4. **Prometheus** (HIGH - observability)
   - Sources:
     - https://prometheus.io/docs/
     - https://github.com/prometheus/prometheus/tree/main/docs
   - Sections: Getting Started, Configuration, Querying, Rules
   - Expected: 200+ KB

5. **Grafana** (HIGH - dashboards)
   - Sources:
     - https://grafana.com/docs/
     - https://github.com/grafana/grafana/tree/main/docs
   - Sections: Install, Dashboards, Plugins, Provisioning
   - Expected: 300+ KB

- [ ] Create Vikunja tasks for each service
- [ ] Queue scraping jobs in Redis with priority (CRITICAL = 1, HIGH = 2)
- [ ] Execute scraping jobs
- [ ] Validate output (no empty files, reasonable size)
- [ ] Store in `knowledge/technical_manuals/{service}/`
- [ ] Generate index markdown per service

**Deliverables**:
- `knowledge/technical_manuals/redis/` (indexed markdown files)
- `knowledge/technical_manuals/postgresql/` (indexed markdown files)
- `knowledge/technical_manuals/docker/` (indexed markdown files)
- `knowledge/technical_manuals/podman/` (indexed markdown files)
- `knowledge/technical_manuals/prometheus/` (indexed markdown files)
- `knowledge/technical_manuals/grafana/` (indexed markdown files)
- `knowledge/technical_manuals/INDEX-PHASE-5.md` (summary)

### Phase 3: Phase 6 AI/ML Services (3-4 hours)

**Priority Order**:

1. **Qdrant** (CRITICAL - vector database for Phase 6A)
   - Sources:
     - https://qdrant.tech/documentation/
     - https://github.com/qdrant/qdrant/tree/master/docs
   - Sections: Getting Started, API, Configuration, Concepts
   - Expected: 150+ KB

2. **llama-cpp-python** (HIGH - local inference)
   - Sources:
     - https://github.com/abetlen/llama-cpp-python (README + docs/)
     - PyPI: https://pypi.org/project/llama-cpp-python/
   - Sections: Install, Usage, API, Examples
   - Expected: 100+ KB

3. **Sentence-Transformers** (HIGH - embeddings)
   - Sources:
     - https://www.sbert.net/ (main docs)
     - https://github.com/UKPLab/sentence-transformers/tree/main/docs
   - Sections: Installation, Model Selection, Usage, Training
   - Expected: 150+ KB

4. **crawl4ai** (HIGH - web scraping for Phase 5E curation)
   - Sources:
     - https://github.com/unclecode/crawl4ai (README + docs/)
     - Documentation: API, Features, Configuration
   - Expected: 100+ KB

5. **OpenAI API** (reference - alternative to local models)
   - Sources:
     - https://platform.openai.com/docs/
   - Sections: API Reference, Models, Examples
   - Expected: 200+ KB

6. **Anthropic Claude API** (reference - comparison point)
   - Sources:
     - https://docs.anthropic.com/
   - Sections: API Reference, Models, Examples
   - Expected: 150+ KB

- [ ] Create Vikunja tasks
- [ ] Queue scraping jobs
- [ ] Execute scraping
- [ ] Store in `knowledge/technical_manuals/{service}/`
- [ ] Cross-reference with Phase 5 services

**Deliverables**:
- `knowledge/technical_manuals/qdrant/` (indexed markdown files)
- `knowledge/technical_manuals/llama-cpp-python/` (indexed markdown files)
- `knowledge/technical_manuals/sentence-transformers/` (indexed markdown files)
- `knowledge/technical_manuals/crawl4ai/` (indexed markdown files)
- `knowledge/technical_manuals/openai/` (indexed markdown files)
- `knowledge/technical_manuals/anthropic/` (indexed markdown files)
- `knowledge/technical_manuals/INDEX-PHASE-6.md` (summary)

### Phase 4: Phase 7-8 Infrastructure (2-3 hours)

**Additional Services**:

1. **OpenTelemetry** (tracing foundation)
   - https://opentelemetry.io/docs/
2. **Jaeger** (distributed tracing)
   - https://www.jaegertracing.io/docs/
3. **FastAPI** (API framework)
   - https://fastapi.tiangolo.com/
4. **Redis-py** (Python Redis client)
   - https://redis-py.readthedocs.io/
5. **SQLAlchemy** (ORM)
   - https://docs.sqlalchemy.org/

- [ ] Queue scraping jobs
- [ ] Execute (likely parallelizable)
- [ ] Store in `knowledge/technical_manuals/`

**Deliverables**:
- `knowledge/technical_manuals/opentelemetry/` (indexed markdown files)
- `knowledge/technical_manuals/jaeger/` (indexed markdown files)
- `knowledge/technical_manuals/fastapi/` (indexed markdown files)
- `knowledge/technical_manuals/redis-py/` (indexed markdown files)
- `knowledge/technical_manuals/sqlalchemy/` (indexed markdown files)
- `knowledge/technical_manuals/INDEX-PHASE-7-8.md` (summary)

### Phase 5: Vector Indexing & Knowledge Base Integration (2-3 hours)

- [ ] Create Qdrant collection for technical manuals
- [ ] Batch-embed all scraped content via sentence-transformers
- [ ] Store embeddings with metadata (service, section, URL, version)
- [ ] Create semantic search index
- [ ] Integrate with agent knowledge bases (expert-knowledge/common-sop/)
- [ ] Test retrieval for each service type
- [ ] Create search interface (for agent use)

**Deliverables**:
- `scripts/index_technical_manuals.py` (embedding + Qdrant storage)
- `knowledge/vectors/technical_manuals_index.json` (metadata)
- `scripts/search_technical_manuals.py` (semantic search utility)
- Integration instructions in `expert-knowledge/common-sop/OPERATIONS-PLAYBOOK.md`

### Phase 6: Testing, Validation & Documentation (1-2 hours)

- [ ] Unit tests for each scraper type (GitHub, REST API, HTML)
- [ ] Integration tests for queue management
- [ ] Validation tests (content not empty, reasonable size, proper markdown)
- [ ] Load tests (concurrent scraping jobs)
- [ ] End-to-end test (scrape a service → embed → search)
- [ ] Create troubleshooting guide (rate limiting, 404s, dynamic content)
- [ ] Update operational procedures in runbook
- [ ] Document template customization for new services

**Deliverables**:
- `tests/test_github_scraper.py`
- `tests/test_openapi_scraper.py`
- `tests/test_html_scraper.py`
- `tests/test_scraping_queue.py`
- `tests/test_manual_integration.py`
- `docs/TECHNICAL-MANUAL-SCRAPING-GUIDE.md` (user guide)
- `docs/SCRAPER-CUSTOMIZATION-TEMPLATES.md` (for new services)

---

## Format Templates & Customization

### Template 1: GitHub Repository Scraper

```python
# Pattern:
# 1. Clone or fetch repo (git clone --depth 1)
# 2. Find /docs/, README.md, /manual/ folders
# 3. Extract markdown files
# 4. Parse frontmatter for metadata
# 5. Convert to normalized markdown
```

**Services Using This**:
- Redis (redis/redis)
- Prometheus (prometheus/prometheus)
- Grafana (grafana/grafana)
- llama-cpp-python (abetlen/llama-cpp-python)
- Qdrant (qdrant/qdrant)
- crawl4ai (unclecode/crawl4ai)

### Template 2: OpenAPI/Swagger Scraper

```python
# Pattern:
# 1. Fetch openapi.json or swagger.json
# 2. Parse spec structure
# 3. Generate markdown for each endpoint
#    - Method, Path, Parameters
#    - Request/Response schemas
#    - Examples
# 4. Generate API reference index
```

**Services Using This**:
- Qdrant API (REST + OpenAPI)
- Redis Modules (some have OpenAPI)
- FastAPI services (auto-generated OpenAPI)

### Template 3: Official Website Scraper (crawl4ai)

```python
# Pattern:
# 1. Fetch landing page with JS rendering
# 2. Extract main documentation links
# 3. Crawl each link recursively (with depth limit)
# 4. Extract text + code blocks
# 5. Restructure into markdown with navigation
```

**Services Using This**:
- PostgreSQL (official .org site)
- Docker (docs.docker.com)
- Podman (podman.io)
- Prometheus (prometheus.io)
- Grafana (grafana.com)
- Qdrant (qdrant.tech)
- OpenTelemetry (opentelemetry.io)

### Template 4: PyPI + pip Documentation

```python
# Pattern:
# 1. Fetch PyPI package page
# 2. Get GitHub URL from package metadata
# 3. Clone repo or fetch from URL
# 4. Extract README + bundled docs
# 5. Install package locally and extract bundled docs from site-packages
```

**Services Using This**:
- llama-cpp-python
- redis-py
- sentence-transformers
- sqlalchemy
- crawl4ai

### Fallback Strategy for Each Service

| Service | Primary | Fallback 1 | Fallback 2 | Rate Limit |
|---------|---------|-----------|-----------|-----------|
| Redis | GitHub (redis/redis) | redis.io docs | RedisJSON module docs | 1 req/10s |
| PostgreSQL | Official docs | GitHub (postgres/postgres) | PostgreSQL wiki | 1 req/5s |
| Docker | docs.docker.com | GitHub (moby/moby) | Docker Hub | 1 req/3s |
| Podman | podman.io | GitHub (containers/podman) | Fedora docs | 1 req/5s |
| Prometheus | prometheus.io | GitHub (prometheus/prometheus) | Prometheus book | 1 req/5s |
| Grafana | grafana.com | GitHub (grafana/grafana) | Grafana Cloud docs | 1 req/3s |
| Qdrant | qdrant.tech | GitHub (qdrant/qdrant) | Qdrant Python docs | 1 req/5s |
| llama-cpp-python | GitHub (abetlen/llama-cpp-python) | PyPI package | Local package docs | n/a |
| sentence-transformers | sbert.net | GitHub (UKPLab/*) | Hugging Face Hub | 1 req/5s |
| crawl4ai | GitHub (unclecode/crawl4ai) | PyPI package | Built-in --help | n/a |

---

## File Structure

```
knowledge/technical_manuals/
├── INDEX-MASTER.md (master index of all manuals)
├── INDEX-PHASE-5.md (Phase 5A-5E services)
├── INDEX-PHASE-6.md (Phase 6 AI/ML services)
├── INDEX-PHASE-7-8.md (Phase 7-8 infrastructure)
│
├── redis/
│   ├── 00-OVERVIEW.md
│   ├── 01-installation.md
│   ├── 02-getting-started.md
│   ├── 03-commands-reference.md
│   ├── 04-admin-guide.md
│   ├── 05-persistence.md
│   └── metadata.json (version, scrape_date, source_url)
│
├── postgresql/
│   ├── 00-OVERVIEW.md
│   ├── 01-installation.md
│   ├── 02-client-apps.md
│   ├── 03-sql-reference.md
│   ├── 04-administration.md
│   ├── 05-server-admin.md
│   └── metadata.json
│
├── qdrant/
│   ├── 00-OVERVIEW.md
│   ├── 01-getting-started.md
│   ├── 02-api-reference.md
│   ├── 03-configuration.md
│   ├── 04-concepts.md
│   └── metadata.json
│
... (other services)

scripts/
├── technical_manual_scraper.py (main orchestrator)
├── scrapers/
│   ├── __init__.py
│   ├── github_scraper.py (template 1)
│   ├── openapi_scraper.py (template 2)
│   ├── html_scraper.py (template 3)
│   ├── pypi_scraper.py (template 4)
│   └── base_scraper.py (abstract base)
├── index_technical_manuals.py (vector embedding)
└── search_technical_manuals.py (search utility)

tests/
├── test_github_scraper.py
├── test_openapi_scraper.py
├── test_html_scraper.py
├── test_pypi_scraper.py
├── test_scraping_queue.py
└── test_manual_integration.py

docs/
├── TECHNICAL-MANUAL-SCRAPING-GUIDE.md (user guide)
├── SCRAPER-CUSTOMIZATION-TEMPLATES.md (adding new services)
└── TROUBLESHOOTING-MANUAL-SCRAPING.md (common issues)
```

---

## Implementation Considerations

### Rate Limiting & Politeness

- Respect robots.txt and rate limits
- Use User-Agent: `XNAi-Foundation/1.0 (https://github.com/xnai-foundation)`
- Add delays between requests (1-10s per service)
- Cache responses locally (avoid re-scraping)
- Implement backoff for 429/503 responses

### Error Handling

- **HTTP Errors**: Retry up to 3x with exponential backoff
- **Timeout**: 30s default, retry with longer timeout
- **JavaScript Content**: Use crawl4ai for rendering
- **Authentication**: Support API keys for private repos/services
- **Malformed Content**: Validate and alert, don't skip

### Deduplication Strategy

```
Hash(content) + URL + version → unique key
Store in Redis: xnai:manual:hash:{hash} → {service, version, date}
Check before processing to avoid re-scraping
```

### Queue Prioritization

```
Priority 1 (CRITICAL): Foundation services (Redis, PostgreSQL, Docker)
Priority 2 (HIGH): AI/ML services (Qdrant, llama-cpp-python)
Priority 3 (MEDIUM): Infrastructure (OpenTelemetry, Jaeger)

Job structure:
{
  "service": "redis",
  "priority": 1,
  "url": "https://redis.io/docs/",
  "format": "html",
  "retry_count": 0,
  "max_retries": 3,
  "created_at": "2026-02-16T23:00:00Z",
  "status": "pending"
}
```

---

## Success Criteria

- ✅ All Phase 5A-5E services scraped successfully
- ✅ All Phase 6 services scraped successfully
- ✅ 300+ KB of total documentation collected
- ✅ Zero duplicate content (hash-based deduplication verified)
- ✅ All content properly markdown-formatted and indexed
- ✅ Vector embeddings generated for all content
- ✅ Semantic search working across all manuals
- ✅ All 6 test suites passing (100%)
- ✅ Operational guide complete with troubleshooting

---

## Timeline & Dependencies

```
Phase 1 (Infra Setup)
  ├─ 1-2 hours
  └─ Blocks Phase 2-6

Phase 2 (Phase 5A-5E Services)
  ├─ 3-4 hours
  ├─ Depends on Phase 1
  └─ Can run in parallel with Phase 3

Phase 3 (Phase 6 Services)
  ├─ 3-4 hours
  ├─ Depends on Phase 1
  └─ Can run in parallel with Phase 2

Phase 4 (Phase 7-8 Services)
  ├─ 2-3 hours
  ├─ Depends on Phase 1
  └─ Can run in parallel with Phases 2-3

Phase 5 (Vector Indexing)
  ├─ 2-3 hours
  └─ Depends on Phases 2-4 (completion)

Phase 6 (Testing & Documentation)
  ├─ 1-2 hours
  └─ Depends on Phase 5

Total: 14-19 hours (can parallelize phases 2-4)
```

---

## Integration with Agent KBs

Once scraping is complete, integrate with expert knowledge bases:

- **Copilot KB**: Reference docs for strategic planning
- **Gemini KB**: Large-scale service architecture relationships
- **Cline KB**: Implementation patterns for each service
- **Crawler KB**: Service selection and prioritization
- **Common SOP**: Reference URLs and update procedures

Update:
- `expert-knowledge/common-sop/OPERATIONS-PLAYBOOK.md` with service links
- `expert-knowledge/*/SYSTEM-INSTRUCTIONS.md` with relevant manual sections
- Create cross-references in agent task descriptions

---

## Next Steps (If Approved)

1. Confirm services list and prioritization
2. Review and adjust fallback strategies
3. Begin Phase 1 (infrastructure setup)
4. Setup Redis queue and Vikunja task templates
5. Implement first scraper (GitHub template, Redis service)
6. Test end-to-end before scaling to all services

---

**Plan Status**: READY FOR REVIEW  
**Estimated Total Effort**: 14-19 hours (parallelizable to 8-10 hours wall-clock)  
**Quality Target**: Production-ready knowledge base for all critical services

