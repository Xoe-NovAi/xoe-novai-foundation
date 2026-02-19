# Technical Manual Scraping Plan - APPROVED FOR EXECUTION

**Date**: 2026-02-16T23:15:00Z  
**Status**: ✅ **APPROVED - PARALLELIZE FROM START**  
**Strategy**: Concurrent infrastructure + scraping job execution  
**Estimated Wall-Clock**: 8-10 hours (vs. 14-19 sequential)

---

## Approval Summary

✅ **15 services** approved (6 Phase 5A-5E + 6 Phase 6 + 3 Phase 7-8)  
✅ **4 scraper templates** approved (GitHub, OpenAPI, HTML, PyPI)  
✅ **6-phase workplan** approved (Phases 1-6)  
✅ **45+ deliverables** approved  
✅ **Parallel execution** approved  

**Decision**: Parallelize infrastructure setup with scraping job execution to maximize throughput.

---

## Execution Strategy

### Thread 1: Infrastructure Setup (Parallel with Thread 2)
- Build scraper framework & queue processor
- Create Pydantic schemas
- Implement 4 format handlers
- Setup Redis queue + Vikunja task templates
- Estimated: 1-2 hours

### Thread 2: Scraping Jobs (Parallel with Thread 1)
- Queue jobs immediately after Thread 1 partial completion
- Execute Phase 5A-5E services (CRITICAL priority)
- Execute Phase 6 services (HIGH priority)
- Execute Phase 7-8 services (MEDIUM priority)
- Estimated: 8-10 hours parallel

### Thread 3: Vector Indexing (After Thread 2 progress)
- Batch embed scraped content
- Index in Qdrant
- Estimated: 2-3 hours

### Thread 4: Testing & Docs (After Thread 3)
- Unit tests for each scraper
- Integration tests
- Operational documentation
- Estimated: 1-2 hours

**Total Wall-Clock**: 8-10 hours (vs. 14-19 sequential)

---

## Immediate Next Steps

1. **Phase 1.1** (0-30 min): Create core files & structures
   - `knowledge/schemas/scraping_job_schema.py`
   - `scripts/technical_manual_scraper.py` (skeleton)
   - `scripts/scrapers/base_scraper.py` (abstract base)

2. **Phase 1.2** (30 min - 1 hour): Implement queue processor
   - Redis queue management
   - Job lifecycle (pending → in_progress → completed)
   - Deduplication logic (hash-based)
   - Error handling & retries

3. **Phase 2.0** (After 1.0): Start scraping jobs
   - Queue Phase 5A-5E services immediately
   - Execute Phase 2 while Phase 1.2 completes
   - Phase 5A-5E: Redis, PostgreSQL, Docker, Podman, Prometheus, Grafana

4. **Phase 1.3** (Parallel with Phase 2): Implement scrapers
   - GitHub scraper (Template 1)
   - HTML scraper (Template 3 - uses crawl4ai)
   - OpenAPI scraper (Template 2)
   - PyPI scraper (Template 4)

5. **Phase 3.0** (After 2.0 starts): Phase 6 AI/ML services
   - Queue: Qdrant, llama-cpp-python, sentence-transformers, etc.

---

## Success Metrics for Parallel Execution

✓ Phase 1.1 complete (core infrastructure) by hour 0.5  
✓ Phase 1.2 complete (queue processor) by hour 1.0  
✓ First scraping job executed by hour 1.5  
✓ Phase 1.3 (all scrapers) complete by hour 3  
✓ Phase 2 services completed by hour 6  
✓ Phase 3 services completed by hour 9  
✓ Vector indexing complete by hour 11  
✓ Testing & docs complete by hour 12  

**Total**: 12 hours (vs. 8-10 hour estimate due to documentation overhead)

---

## Queue Management Strategy

### Redis Queue Structure
```
xnai:scrape:jobs:1:pending   → CRITICAL (Phase 5A-5E)
xnai:scrape:jobs:2:pending   → HIGH (Phase 6)
xnai:scrape:jobs:3:pending   → MEDIUM (Phase 7-8)

xnai:scrape:active:{service} → Job in progress
xnai:scrape:completed:{hash}  → Completed jobs (dedup check)
```

### Job Entry Format
```json
{
  "id": "scrape-redis-20260216-001",
  "service": "redis",
  "priority": 1,
  "urls": [
    "https://redis.io/docs/",
    "https://github.com/redis/redis/tree/unstable/docs"
  ],
  "format": "mixed",
  "scraper_template": "github+html",
  "retry_count": 0,
  "max_retries": 3,
  "created_at": "2026-02-16T23:15:00Z",
  "status": "pending"
}
```

### Execution Order
1. Queue all Phase 5 services (6 jobs) - priority 1
2. Queue all Phase 6 services (6 jobs) - priority 2
3. Queue all Phase 7 services (5 jobs) - priority 3
4. Execute FIFO with priority weighting (3x more often for priority 1)

---

## Parallel Execution Timeline

```
Time    Thread 1 (Infra)         Thread 2 (Scraping)
─────   ────────────────         ──────────────────
0-30m   Create schemas           (waiting)
        Create queue processor

30m-1h  Implement queuing        Queue Phase 5 jobs
        Start base scraper       

1h-2h   GitHub scraper           Execute Redis, PostgreSQL
        HTML scraper             

2h-3h   OpenAPI scraper          Continue Phase 5 + start Phase 6
        PyPI scraper             

3h-6h   Testing framework        Phase 5 + Phase 6 in parallel
        (scrapers running)       

6h-10h  (scraping complete)      Complete Phase 6 + Phase 7

10h-12h Vector indexing          Tests + docs + final validation
        Integration tests
```

---

## Checkpoints & Validations

**Checkpoint 1** (Hour 1): Queue processor ready, first job queued
- [ ] Redis queue operational
- [ ] Job structure valid
- [ ] Vikunja task created
- [ ] Base scraper works

**Checkpoint 2** (Hour 3): First scrapers complete
- [ ] Redis manual scraped (50+ KB)
- [ ] PostgreSQL manual scraped (500+ KB)
- [ ] Content deduplicated & indexed
- [ ] No format errors

**Checkpoint 3** (Hour 6): Phase 5 complete, Phase 6 in progress
- [ ] All 6 Phase 5 services scraped
- [ ] Total: 2+ MB content
- [ ] Phase 6 jobs executing
- [ ] Deduplication verified

**Checkpoint 4** (Hour 10): All scraping complete
- [ ] All 17 services scraped
- [ ] 300+ KB total (estimated)
- [ ] Zero duplicates
- [ ] Content quality validated

**Checkpoint 5** (Hour 12): Complete integration
- [ ] All tests passing (6/6)
- [ ] Qdrant indexed
- [ ] Agent KBs updated
- [ ] Documentation complete

---

## Risk Mitigation for Parallel Execution

| Risk | Mitigation |
|------|-----------|
| Queue processor not ready | Start scraping manually, migrate to queue later |
| Scraper format issues | Fall back to HTML crawler for all services temporarily |
| Rate limiting | Implement backoff + cache locally, retry later |
| Duplicate detection fails | Manual review + cleanup step |
| Qdrant not available | Store embeddings as JSON, migrate when ready |

---

## Deliverables per Phase

### Phase 1.1-1.3 (Infrastructure) - Hours 0-3
```
scripts/technical_manual_scraper.py (main)
scripts/scrapers/base_scraper.py (abstract)
scripts/scrapers/github_scraper.py
scripts/scrapers/html_scraper.py
scripts/scrapers/openapi_scraper.py
scripts/scrapers/pypi_scraper.py
knowledge/schemas/scraping_job_schema.py
```

### Phase 2 (Phase 5A-5E services) - Hours 1-6
```
knowledge/technical_manuals/redis/
knowledge/technical_manuals/postgresql/
knowledge/technical_manuals/docker/
knowledge/technical_manuals/podman/
knowledge/technical_manuals/prometheus/
knowledge/technical_manuals/grafana/
knowledge/technical_manuals/INDEX-PHASE-5.md
```

### Phase 3 (Phase 6 services) - Hours 4-9
```
knowledge/technical_manuals/qdrant/
knowledge/technical_manuals/llama-cpp-python/
knowledge/technical_manuals/sentence-transformers/
knowledge/technical_manuals/crawl4ai/
knowledge/technical_manuals/openai/
knowledge/technical_manuals/anthropic/
knowledge/technical_manuals/INDEX-PHASE-6.md
```

### Phase 4 (Phase 7-8 services) - Hours 6-10
```
knowledge/technical_manuals/opentelemetry/
knowledge/technical_manuals/jaeger/
knowledge/technical_manuals/fastapi/
knowledge/technical_manuals/redis-py/
knowledge/technical_manuals/sqlalchemy/
knowledge/technical_manuals/INDEX-PHASE-7-8.md
knowledge/technical_manuals/INDEX-MASTER.md
```

### Phase 5 (Vector Indexing) - Hours 9-11
```
scripts/index_technical_manuals.py
scripts/search_technical_manuals.py
knowledge/vectors/technical_manuals_index.json
(Integration with expert-knowledge/*/SYSTEM-INSTRUCTIONS.md)
```

### Phase 6 (Testing & Docs) - Hours 11-12
```
tests/test_github_scraper.py
tests/test_openapi_scraper.py
tests/test_html_scraper.py
tests/test_pypi_scraper.py
tests/test_scraping_queue.py
tests/test_manual_integration.py
docs/TECHNICAL-MANUAL-SCRAPING-GUIDE.md
docs/SCRAPER-CUSTOMIZATION-TEMPLATES.md
docs/TROUBLESHOOTING-MANUAL-SCRAPING.md
```

---

## Final Approval Notes

✅ Plan approved for parallel execution  
✅ All services & templates approved  
✅ Timeline realistic (8-10h wall-clock, 14-19h effort)  
✅ Risk mitigation strategies in place  
✅ Integration points clear  
✅ Fallback strategies defined  

**Status**: **READY TO EXECUTE**

---

## How to Monitor Progress

1. **Redis Queue**: `LLEN xnai:scrape:jobs:1:pending` (remaining CRITICAL jobs)
2. **Vikunja**: View task board (each service has one task)
3. **Knowledge Base**: `ls knowledge/technical_manuals/*/` (completed services)
4. **Logs**: Check `scripts/technical_manual_scraper.py` output

---

**Approved by**: User  
**Plan created by**: Copilot CLI  
**Status**: ✅ APPROVED - EXECUTION READY

Ready to start Phase 1.1 when user gives go signal.

