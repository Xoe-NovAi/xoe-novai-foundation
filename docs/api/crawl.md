# Crawl Worker API Reference

> **Generated**: 2026-02-21  
> **Source**: `app/XNAi_rag_app/workers/crawl.py`  
> **Version**: 0.1.0-alpha

---

## Overview

The Crawl Worker is a standalone Python script for library curation from external sources. It is not an HTTP API but a CLI tool that can be run as a containerized service or standalone script.

> **Note**: This is a worker process, not an HTTP API. For programmatic access, integrate via subprocess calls or the curation worker service.

---

## Supported Sources

| Source | Domain | Content Type |
|--------|--------|--------------|
| Project Gutenberg | `gutenberg.org` | Public domain books |
| arXiv | `arxiv.org` | Scientific papers |
| PubMed | `nih.gov` | Medical abstracts |
| YouTube | `youtube.com` | Video transcripts |

---

## Command Line Interface

### Basic Usage

```bash
# Curate from Gutenberg
python3 crawl.py --curate gutenberg -c classical-works -q "Plato"

# Curate from arXiv
python3 crawl.py --curate arxiv -c physics -q "quantum mechanics"

# Curate from PubMed  
python3 crawl.py --curate pubmed -c medicine -q "cancer research"

# Curate from YouTube
python3 crawl.py --curate youtube -c psychology -q "Jung lectures"

# Test run (dry mode)
python3 crawl.py --curate test --dry-run --stats
```

### Arguments

| Argument | Short | Description | Required |
|----------|-------|-------------|----------|
| `--curate` | `-c` | Source to curate from (gutenberg/arxiv/pubmed/youtube) | Yes |
| `--collection` | - | Collection name for organizing results | Yes |
| `--query` | `-q` | Search query | Yes |
| `--dry-run` | - | Test without saving | No |
| `--stats` | - | Show statistics | No |
| `--limit` | `-l` | Max items to fetch (default: 10) | No |
| `--output` | `-o` | Output directory | No |

### Docker Execution

```bash
# Run in container
podman exec xnai_crawler python3 /app/XNAi_rag_app/workers/crawl.py \
  --curate gutenberg -c philosophy -q "Marcus Aurelius"
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAWL4AI_NO_TELEMETRY` | `true` | Disable telemetry |
| `CRAWL_SANITIZE_SCRIPTS` | `true` | Remove script tags |
| `CRAWL_RATE_LIMIT_PER_MIN` | `30` | Rate limit |
| `CRAWL_CACHE_TTL` | `86400` | Cache TTL (seconds) |
| `REDIS_HOST` | `localhost` | Redis cache |
| `REDIS_PORT` | `6379` | Redis port |
| `LIBRARY_PATH` | `/library` | Output directory |
| `KNOWLEDGE_PATH` | `/knowledge` | Knowledge base |

### Allowlist Enforcement

Only domains in the allowlist can be crawled:

```
*.gutenberg.org
*.arxiv.org  
*.nih.gov
*.youtube.com
```

---

## Security Features

### Prompt Injection Sanitization

The crawler strips adversarial patterns from curated content:

```python
# Patterns removed:
- "Ignore previous instructions"
- "Bypass system prompt"
- "Ignore all previous rules"
```

### Script Sanitization

When `CRAWL_SANITIZE_SCRIPTS=true`:
- All `<script>` tags removed
- Event handlers stripped
- `javascript:` URLs blocked

---

## Output Format

### Directory Structure

```
library/
├── gutenberg/
│   └── classical-works/
│       ├── metadata.toml
│       └── content/
│           └── plato-republic/
├── arxiv/
│   └── physics/
│       ├── metadata.toml
│       └── content/
│           └── quantum-mechanics-2401.001/
├── pubmed/
│   └── medicine/
│       └── cancer-research/
└── youtube/
    └── psychology/
        └── jung-lectures/
```

### Metadata Format (metadata.toml)

```toml
[metadata]
source = "gutenberg"
source_id = "pg12345"
title = "The Republic"
author = "Plato"
collected_at = "2026-01-09T14:30:00Z"
query = "Plato"
collection = "classical-works"

[content]
path = "content/plato-republic/text.txt"
format = "plaintext"
size_bytes = 524288

[performance]
crawl_duration_ms = 1234
cache_hit = false
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Curation Rate | 50-200 items/hour |
| Cache Size | <500MB for 200 items |
| Memory Usage | <1GB during operation |
| Rate Limit | 30 requests/minute |

---

## Curation Worker Service

For production use, run the curation worker as a service:

### docker-compose Configuration

```yaml
curation_worker:
  build:
    context: .
    dockerfile: Dockerfile.curation_worker
  environment:
    - REDIS_HOST=redis
    - REDIS_PORT=6379
    - LIBRARY_PATH=/library
    - KNOWLEDGE_PATH=/knowledge
  volumes:
    - ./library:/library:Z
    - ./knowledge:/knowledge:Z
  restart: unless-stopped
```

### Running Jobs

```bash
# Schedule a curation job via Redis
redis-cli -a $REDIS_PASSWORD LPUSH xnai:curation_jobs \
  '{"source": "gutenberg", "collection": "philosophy", "query": "Stoicism"}'
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ALLOWLIST_VIOLATION` | URL not in allowlist | Check source domain |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| `CACHE_ERROR` | Redis connection failed | Check Redis service |
| `PARSE_ERROR` | Failed to parse content | Skip and log |

---

## Related Documentation

- [Crawler Operations Runbook](../CRAWLER-OPERATIONS-RUNBOOK.md)
- [Main API](main.md)
- [Configuration](../03-reference/configuration.md)
