# Online Library API Integration for Automated Book Discovery
## Knowledge Card: Internet Archive & OpenLibrary APIs

**Date**: February 15, 2026  
**Status**: Research Complete  
**Architect**: Xoe-NovAi Research  
**Focus**: Metadata-first book discovery integration  
**Last Updated**: 2026-02-15

---

## EXECUTIVE SUMMARY

Internet Archive and OpenLibrary provide mission-aligned, open-source APIs for autonomous book discovery and metadata extraction. Both prioritize human-centered, low-traffic use cases. This card documents API capabilities, integration patterns, and constraints for the XNAi RAG system's knowledge curation pipeline.

**Key Findings**:
- OpenLibrary: 1-3 requests/second (identified), excellent bibliographic metadata
- Internet Archive: Rich search/metadata APIs with WARC support for full-text indexing
- Both: No bulk harvesting; must use monthly data dumps for large-scale ingestion
- Metadata-first strategy: Payload in Redis → Vector generation on-demand

---

## 1. OPENLIBRARY API OVERVIEW

### 1.1 Core Capabilities

| API Endpoint | Purpose | Rate Limit | Best For |
|---|---|---|---|
| `/search.json` | Full-text book search | 3 req/sec (identified) | Batch discovery queries |
| `/works/{id}.json` | Work metadata (all editions) | 3 req/sec | Author bibliography |
| `/editions/{id}.json` | Edition-specific details | 3 req/sec | ISBN resolution |
| `/authors/{id}.json` | Author bio & bibliography | 3 req/sec | Author-centric queries |
| `/subjects/{name}.json` | Subject-based browsing | 3 req/sec | Topic discovery |
| `/covers/{id}` | Cover images | 3 req/sec | Visual content |
| `/search_inside` | Full-text search across books | 3 req/sec | Content extraction |

### 1.2 Authentication & Headers

No API keys required. **Required for identified use**:

```python
headers = {
    "User-Agent": "XNAi-LibraryBot/1.0 (contact@xnai.foundation)",
    "Accept": "application/json"
}
```

Identified requests with proper `User-Agent` enjoy **3x rate limit** (3 req/sec vs. 1 req/sec).

### 1.3 Response Structure Example

**Search Query**:
```bash
GET /search.json?title=dune&author=herbert&limit=10
```

**Response**:
```json
{
  "numFound": 5000,
  "start": 0,
  "docs": [
    {
      "key": "/works/OL45883W",
      "title": "Dune",
      "author_name": ["Frank Herbert"],
      "first_publish_year": 1965,
      "isbn": ["0441172717"],
      "edition_count": 240,
      "has_fulltext": true,
      "language": ["eng"],
      "cover_i": 1234567,
      "subject": ["Science fiction", "Fantasy"]
    }
  ]
}
```

### 1.4 Key Metadata Fields

For XNAi vector ingestion (metadata-first):

- **Identifiers**: `key` (OL ID), `isbn`, `oclc_id`, `lccn`
- **Bibliographic**: `title`, `subtitle`, `author_name`, `first_publish_year`, `edition_count`
- **Content**: `subject` (array), `has_fulltext` (boolean), `language` (array)
- **Visual**: `cover_i` (image ID for retrieval)
- **Full Text**: Available via `/search_inside` API

---

## 2. INTERNET ARCHIVE API OVERVIEW

### 2.1 Core Capabilities

| API Endpoint | Purpose | Authentication | Best For |
|---|---|---|---|
| `/advancedsearch.php` | Metadata search (items) | None | Discovery queries |
| `/metadata/{id}` | Full metadata + files | None | Item details |
| `/download/{id}/{filename}` | Download files | None | Content retrieval |
| `ia` CLI tool | Batch operations | Token (optional) | Large-scale operations |
| WARC format | Web archive search | None | Full-text indexing |

### 2.2 Search API Example

```bash
GET https://archive.org/advancedsearch.php?q=title:dune AND mediatype:texts&output=json&rows=50
```

**Key Query Operators**:
- `mediatype:(texts|audio|video|software|image)`
- `collection:(openlibrary|booksbyidentifier|books|journals)`
- `year:[1960 TO 1970]`
- `subject:(science-fiction|fantasy)`
- `language:eng`

### 2.3 Metadata API Response

```json
{
  "metadata": {
    "identifier": "dune_1965",
    "title": "Dune",
    "creator": "Frank Herbert",
    "date": "1965",
    "mediatype": "texts",
    "subject": ["Science fiction", "Fantasy"],
    "description": "...",
    "language": "eng",
    "isbn": "0441172717",
    "licenseurl": "https://creativecommons.org/...",
    "ocr": true,
    "file_count": 5
  },
  "files": [
    {
      "name": "dune_1965_djvu.txt",
      "source": "djvu",
      "format": "Text",
      "size": "2845940",
      "mtime": "1234567890"
    }
  ]
}
```

### 2.4 Collection Access

**OpenLibrary Books in Internet Archive**:
```
https://archive.org/details/openlibrary_records
```

This collection contains metadata for books available through OpenLibrary, enabling cross-reference queries.

---

## 3. DATA MIGRATION STRATEGY: FAISS → QDRANT

### 3.1 Metadata-First Architecture

**Principle**: Store metadata in Redis as source-of-truth; vectors in Qdrant as search index.

```
┌──────────────────────────────────────────┐
│   OpenLibrary / Internet Archive         │
│   (Book Discovery via APIs)              │
└──────────────┬───────────────────────────┘
               │
               ├─→ Extract ISBN, Title, Author, Subject
               │   (METADATA ONLY)
               │
        ┌──────▼──────────────────────────┐
        │  Redis Stream/Hash              │
        │  (Source of Truth)              │
        │  - book:isbn:XXXXX              │
        │  - book:metadata:XXXXX          │
        │  - book:discovery_log           │
        └────────┬─────────────────────────┘
                 │
      ┌──────────┴──────────────┐
      │                         │
      ▼ (On-demand)           ▼ (Async)
  Vector Gen            Qdrant Upsert
  (FastEmbed)           (with payload)
      │                         │
      └──────────┬──────────────┘
                 │
        ┌────────▼──────────────┐
        │  Qdrant Collection     │
        │  books (dense vectors) │
        │  + payload (metadata)  │
        └───────────────────────┘
```

### 3.2 FAISS → Qdrant Migration Path

**Stage 1: Metadata Export (No Vector Loss)**

```python
# From FAISS index.faiss + metadata.json
import faiss
import json
import redis

# Load FAISS
index = faiss.read_index("index.faiss")
with open("metadata.json") as f:
    metadata_map = json.load(f)  # {doc_id: {title, isbn, ...}}

# Migrate to Redis
redis_client = redis.Redis(host="localhost", port=6379)
for doc_id, vector in enumerate(index):
    meta = metadata_map[str(doc_id)]
    redis_client.hset(
        f"book:meta:{meta['isbn']}",
        mapping={
            "title": meta["title"],
            "author": meta["author"],
            "isbn": meta["isbn"],
            "vector_id": doc_id,  # Qdrant ID (post-migration)
            "source": meta.get("source", "faiss_legacy")
        }
    )
```

**Stage 2: Vector Re-embedding (Qdrant Compatible)**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import numpy as np

client = QdrantClient("http://localhost:6333")

# Create collection
client.create_collection(
    collection_name="books",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)  # FastEmbed dim
)

# Upsert vectors with metadata payload
points = []
for doc_id, vector in enumerate(index):
    meta = metadata_map[str(doc_id)]
    points.append(PointStruct(
        id=doc_id + 1,  # Qdrant IDs start at 1
        vector=vector.tolist(),
        payload={
            "isbn": meta.get("isbn"),
            "title": meta.get("title"),
            "author": meta.get("author"),
            "subject": meta.get("subject", []),
            "language": meta.get("language", "en"),
            "source": "faiss_migration",
            "timestamp_migrated": datetime.now().isoformat()
        }
    ))

# Batch upsert
client.upsert(collection_name="books", points=points)
```

### 3.3 Redis Source-of-Truth Handover

**Phase 1: Parallel Operation (Validation)**

```python
import asyncio
from redis.asyncio import Redis
from qdrant_client.async_client import AsyncQdrantClient

async def validate_migration(isbn):
    redis = Redis(host="localhost", port=6379)
    qdrant = AsyncQdrantClient(url="http://localhost:6333")
    
    # Get from Redis (source of truth)
    redis_data = await redis.hgetall(f"book:meta:{isbn}")
    
    # Get from Qdrant (new index)
    search_result = await qdrant.search(
        collection_name="books",
        query_vector=[0.0] * 384,  # Placeholder
        query_filter={
            "must": [{
                "key": "isbn",
                "match": {"value": isbn}
            }]
        },
        limit=1
    )
    
    # Validate consistency
    if search_result:
        qdrant_data = search_result[0].payload
        assert redis_data["title"] == qdrant_data["title"]
        return True
    return False
```

**Phase 2: Read-Through Cache Pattern**

```python
async def get_book_metadata(isbn: str) -> dict:
    """
    1. Check Redis (write-through on misses)
    2. Query Qdrant for latest vectors
    3. Return enriched response
    """
    redis = Redis(host="localhost", port=6379)
    
    # Try Redis first
    cached = await redis.hgetall(f"book:meta:{isbn}")
    if cached:
        return cached
    
    # Query Qdrant (vector search or metadata filter)
    result = await qdrant_client.search(
        collection_name="books",
        query_filter={"must": [{"key": "isbn", "match": {"value": isbn}}]},
        limit=1
    )
    
    if result:
        payload = result[0].payload
        # Write to Redis for future hits
        await redis.hset(f"book:meta:{isbn}", mapping=payload)
        return payload
    
    return None
```

### 3.4 Bulk Migration (Data Dumps)

For large-scale migrations, use OpenLibrary **monthly data dumps**:

```bash
# Download dump
curl -O https://openlibrary.org/data/ol_dump_works_LATEST.jsonl.gz

# Parse and load
zcat ol_dump_works_LATEST.jsonl.gz | \
  python -c """
import sys, json, redis
r = redis.Redis()
for line in sys.stdin:
    work = json.loads(line)
    r.hset(
        f\"book:work:{work['key']}\",
        mapping={
            'title': work.get('title'),
            'author_key': ','.join(work.get('author_key', [])),
            'first_publish_year': work.get('first_publish_year')
        }
    )
"""
```

---

## 4. INTEGRATION PATTERNS

### 4.1 Discovery Pipeline (Python)

```python
import aiohttp
import asyncio
from qdrant_client.async_client import AsyncQdrantClient
from redis.asyncio import Redis

class BookDiscoveryPipeline:
    def __init__(self):
        self.ol_base = "https://openlibrary.org"
        self.ia_base = "https://archive.org"
        self.redis = Redis(host="localhost", port=6379)
        self.qdrant = AsyncQdrantClient(url="http://localhost:6333")
        self.session = None
    
    async def discover_by_subject(self, subject: str, limit: int = 50):
        """
        Discover books from OpenLibrary by subject.
        Pipeline: OL Search → Redis → Qdrant Upsert
        """
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "XNAi-LibraryBot/1.0 (contact@xnai.foundation)"
                }
            )
        
        # 1. Query OpenLibrary
        async with self.session.get(
            f"{self.ol_base}/subjects/{subject}.json",
            params={"limit": limit}
        ) as resp:
            ol_data = await resp.json()
        
        # 2. Cache metadata in Redis
        for work in ol_data.get("works", []):
            isbn = work.get("isbn", [work.get("key")])[0] if work.get("isbn") else work.get("key")
            await self.redis.hset(
                f"book:meta:{isbn}",
                mapping={
                    "title": work.get("title"),
                    "author": ",".join(work.get("author_name", [])),
                    "isbn": isbn,
                    "subject": subject,
                    "has_fulltext": work.get("has_fulltext", False),
                    "source": "openlibrary"
                }
            )
        
        return ol_data
    
    async def search_internet_archive(self, query: str):
        """
        Search Internet Archive for matching items.
        """
        async with self.session.get(
            f"{self.ia_base}/advancedsearch.php",
            params={
                "q": query,
                "output": "json",
                "rows": 50,
                "mediatype": "texts"
            }
        ) as resp:
            return await resp.json()

# Usage
pipeline = BookDiscoveryPipeline()
await pipeline.discover_by_subject("science-fiction")
```

### 4.2 Error Handling & Rate Limiting

```python
import asyncio
import time
from tenacity import retry, wait_exponential, stop_after_attempt

class RateLimitedClient:
    def __init__(self, max_rps: float = 2.5):  # 2.5 req/sec (identified)
        self.max_rps = max_rps
        self.last_request = 0
        self.lock = asyncio.Lock()
    
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5)
    )
    async def request(self, url: str, **kwargs):
        async with self.lock:
            elapsed = time.time() - self.last_request
            if elapsed < 1 / self.max_rps:
                await asyncio.sleep(1 / self.max_rps - elapsed)
            
            self.last_request = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, **kwargs) as resp:
                if resp.status == 429:
                    raise Exception("Rate limited")
                return await resp.json()
```

---

## 5. CONSTRAINTS & RECOMMENDATIONS

### 5.1 API Limitations

| Constraint | Impact | Workaround |
|---|---|---|
| No bulk harvesting | Can't batch-load entire collections | Use monthly data dumps (`openlibrary/data`) |
| 3 req/sec max (identified) | Limits real-time discovery speed | Batch queries; cache aggressively in Redis |
| Single-line API requests | No multi-step queries | Compose in application logic |
| Limited full-text access | Can't index all content via API | Use `/search_inside` for excerpts; fallback to WARC |

### 5.2 Best Practices

1. **Identify Your Bot**: Always use proper `User-Agent` header
   ```python
   headers = {
       "User-Agent": "XNAi-LibraryBot/1.0 (research@xnai.foundation)"
   }
   ```

2. **Cache Aggressively**: Redis is your friend
   - Cache metadata for 24-48 hours
   - Cache ISBN → OL ID mappings permanently
   - Cache covers locally (avoid re-fetching)

3. **Batch Queries**: Use `/search.json` instead of individual requests
   ```python
   # Good: 1 request for 10 books
   await client.request("/search.json?title=dune&author=herbert&limit=10")
   
   # Bad: 10 requests for 10 books
   for isbn in isbns:
       await client.request(f"/editions/{isbn}.json")
   ```

4. **Respect Rate Limits**: Use AsyncIO + semaphore
   ```python
   semaphore = asyncio.Semaphore(2)  # 2 concurrent requests
   async def fetch_book(isbn):
       async with semaphore:
           return await client.request(f"/editions/{isbn}.json")
   ```

5. **Monitor Full-Text Availability**: Check `has_fulltext` before deep-indexing
   ```python
   if work.get("has_fulltext"):
       full_text = await fetch_search_inside(work["key"])
   ```

---

## 6. REDIS SCHEMA DESIGN

**Metadata-first approach**:

```
# Book metadata (source of truth)
book:meta:{isbn} → {title, author, subject, language, source, created_at}
book:meta:{ol_key} → {title, author, ...}

# Discovery tracking
book:discovery_log → Set of recently discovered ISBNs
book:sync:{collection} → Last sync timestamp for bulk operations

# Vector tracking
book:vector_id:{isbn} → Qdrant point ID (after migration)
book:bulk_sync:{batch_id} → Migration batch status

# Performance indices
book:by_subject:{subject} → Set of ISBNs
book:by_author:{author} → Set of ISBNs
```

---

## 7. IMPLEMENTATION CHECKLIST

- [ ] Create `BookDiscoveryPipeline` class (async)
- [ ] Implement Redis caching layer
- [ ] Set up rate-limited HTTP client
- [ ] Integrate OpenLibrary search API
- [ ] Integrate Internet Archive search API
- [ ] Create metadata → Qdrant payload serialization
- [ ] Implement error handling & retry logic
- [ ] Add telemetry for discovery pipeline
- [ ] Test with 100-book batch
- [ ] Profile memory usage (Ryzen 7 constraints)
- [ ] Document API keys & secrets (if needed)
- [ ] Create integration tests

---

## REFERENCES & RESOURCES

- **OpenLibrary API Docs**: https://openlibrary.org/developers/api
- **OpenLibrary Data Dumps**: https://openlibrary.org/developers/dumps
- **Internet Archive API**: https://archive.org/services/docs/api/
- **Open Library Client Library**: https://github.com/internetarchive/openlibrary-client
- **Internet Archive Python Library**: https://github.com/internetarchive/internetarchive

---

**Knowledge Card Version**: 1.0.0  
**Next Update**: 2026-03-15  
**Maintainer**: Xoe-NovAi Research Team
