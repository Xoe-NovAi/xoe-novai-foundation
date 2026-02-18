# Semantic Search Skill

## Purpose
Query the Foundation RAG API for semantic and lexical search.

## Trigger
- Research needed
- Context lookup
- Documentation search
- Code pattern search

## API Endpoint
`POST http://localhost:8000/search`

## Request Format
```json
{
  "query": "implement authentication",
  "mode": "hybrid",
  "top_k": 10,
  "filters": {
    "doc_type": "code",
    "domain": "security"
  }
}
```

## Search Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| semantic | Vector similarity | Concept search |
| lexical | BM25 keyword | Exact terms |
| hybrid | Combined | Best results |

## Workflow

### Step 1: Formulate Query
Convert user need to search query:
- Identify key concepts
- Add relevant filters
- Set appropriate top_k

### Step 2: Execute Search
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "...",
    "mode": "hybrid",
    "top_k": 5
  }'
```

### Step 3: Process Results
Parse response:
```json
{
  "results": [
    {
      "content": "...",
      "source": "docs/api/auth.md",
      "score": 0.92,
      "metadata": {...}
    }
  ],
  "total": 15,
  "latency_ms": 45
  }
```

### Step 4: Present Findings
Format results for user:
```
## Search Results
Query: [query]
Mode: [mode]
Latency: [ms]ms

### Top Results
1. **[source]** (score: 0.92)
   [content excerpt]

2. **[source]** (score: 0.87)
   [content excerpt]
```

## Filter Options

| Filter | Values | Purpose |
|--------|--------|---------|
| doc_type | code, docs, config | Content type |
| domain | api, internal, guides | Document domain |
| phase | 1-7 | Project phase |
| date_range | ISO dates | Time filter |

## Performance Targets
- Latency: <500ms
- Relevance: Top 3 > 0.8 score
- Coverage: All indexed content

## Index Coverage
The RAG index includes:
- `docs/` - Documentation
- `app/` - Application code
- `memory_bank/` - Project context
- `internal_docs/` - Internal docs

## Output Format
```
## Semantic Search
Query: [query]
Results: [count]
Latency: [ms]ms

### Relevant Content
[Summarized findings with sources]

### Sources
1. [path] - [relevance]
2. [path] - [relevance]
```

## Integration
- Used by `memory-bank-loader` for context enrichment
- Supports `doc-taxonomy-writer` classification
- Enhances `research` agent capabilities

## Fallback
If RAG API unavailable:
1. Fall back to local grep/code search
2. Check `memory_bank/` directly
3. Notify user of degraded mode
