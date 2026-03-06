---
title: Phase 1 Database Schema Documentation
description: Complete PostgreSQL schema, relationships, and query examples
last_updated: 2026-02-25
status: active
persona_focus: Database Administrators, Backend Developers
---

# Phase 1 Database Schema Documentation

Complete reference for the PostgreSQL schema in Phase 1, including table definitions, relationships, indices, and sample queries.

---

## Schema Overview

The Phase 1 database (`xnai`) implements a comprehensive knowledge management system with:

- **Hierarchical Domains:** Organize knowledge into structured categories
- **Documents & Chunks:** Manage raw content and token-aware segments
- **Embeddings:** Reference to vector representations (stored in Qdrant)
- **Relations:** Explicit links between entities
- **Agent Learning:** Track AI agent persona evolution
- **Audit Trail:** Compliance and debugging
- **Query Cache:** Performance optimization

**Total Tables:** 10 core tables + 3 materialized views

---

## Table Specifications

### 1. KNOWLEDGE_DOMAINS

**Purpose:** Hierarchical taxonomy for organizing knowledge

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS knowledge_domains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES knowledge_domains(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT domain_name_not_empty CHECK (length(trim(name)) > 0)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| name | VARCHAR(255) | Domain name | Required, Unique, Non-empty |
| description | TEXT | Domain description | Optional |
| parent_id | UUID | Parent domain (for hierarchy) | Optional, Foreign Key |
| metadata | JSONB | Custom metadata | Default: empty object |
| created_at | TIMESTAMP TZ | Creation timestamp | Auto-set |
| updated_at | TIMESTAMP TZ | Last update timestamp | Auto-set |

**Indices:**
- `idx_knowledge_domains_parent_id` - Hierarchy traversal
- `idx_knowledge_domains_name` - Domain lookup by name

**Example Hierarchy:**
```
Technology (parent_id=NULL)
├── AI & Machine Learning (parent_id=tech_id)
├── DevOps & Infrastructure (parent_id=tech_id)
└── Web Development (parent_id=tech_id)
```

---

### 2. DOCUMENTS

**Purpose:** Core document storage with metadata and content

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    path VARCHAR(1024) UNIQUE,
    source VARCHAR(255) NOT NULL,
    domain_id UUID NOT NULL REFERENCES knowledge_domains(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted', 'processing')),
    content_hash VARCHAR(64) UNIQUE,
    chunk_count INTEGER DEFAULT 0 CHECK (chunk_count >= 0),
    content TEXT,
    file_size INTEGER DEFAULT 0,
    mime_type VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT title_not_empty CHECK (length(trim(title)) > 0),
    CONSTRAINT source_not_empty CHECK (length(trim(source)) > 0)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| title | VARCHAR(500) | Document title | Required, Non-empty |
| path | VARCHAR(1024) | Source file path | Unique, Optional |
| source | VARCHAR(255) | Data source (URL/file/API) | Required, Non-empty |
| domain_id | UUID | Knowledge domain | Required, Foreign Key |
| created_at | TIMESTAMP TZ | Creation timestamp | Auto-set |
| updated_at | TIMESTAMP TZ | Last update timestamp | Auto-set |
| status | VARCHAR(50) | Processing state | active \| archived \| deleted \| processing |
| content_hash | VARCHAR(64) | SHA256 of content | Unique, for deduplication |
| chunk_count | INTEGER | Number of chunks | >= 0 |
| content | TEXT | Raw document content | Optional |
| file_size | INTEGER | Original file size in bytes | >= 0 |
| mime_type | VARCHAR(100) | MIME type | text/plain, application/pdf, etc. |
| metadata | JSONB | Custom metadata | author, tags, source_url, etc. |

**Indices:**
- `idx_documents_fts` - Full-text search (GIN index)
- `idx_documents_domain_id` - Domain lookups
- `idx_documents_status` - Status filtering
- `idx_documents_created_at` - Time-based queries
- `idx_documents_updated_at` - Recency queries
- `idx_documents_content_hash` - Deduplication
- `idx_documents_title` - Title search

**Document Lifecycle:**
```
INSERT (status='processing')
    ↓
CURATION WORKER processes
    ↓
UPDATE (status='active')
    ↓
Available for queries
    ↓
OPTIONAL: UPDATE (status='archived' or 'deleted')
```

---

### 3. CHUNKS

**Purpose:** Token-aware document segments with positional metadata

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_num INTEGER NOT NULL CHECK (chunk_num >= 0),
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL CHECK (token_count > 0),
    position_in_doc DECIMAL(10, 4) NOT NULL CHECK (position_in_doc >= 0 AND position_in_doc <= 1),
    start_char INTEGER CHECK (start_char >= 0),
    end_char INTEGER CHECK (end_char > 0),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(doc_id, chunk_num),
    CONSTRAINT content_not_empty CHECK (length(trim(content)) > 0)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| doc_id | UUID | Parent document | Required, Foreign Key, Cascade delete |
| chunk_num | INTEGER | Chunk sequence | >= 0 |
| content | TEXT | Chunk text | Required, Non-empty |
| token_count | INTEGER | BPE token count | > 0 |
| position_in_doc | DECIMAL | Position ratio (0-1) | 0 ≤ x ≤ 1 |
| start_char | INTEGER | Character offset start | >= 0 |
| end_char | INTEGER | Character offset end | > 0 |
| metadata | JSONB | Strategy, overlap info | {strategy: "semantic", overlap: 0.1} |
| created_at | TIMESTAMP TZ | Creation timestamp | Auto-set |
| updated_at | TIMESTAMP TZ | Last update timestamp | Auto-set |

**Indices:**
- `idx_chunks_doc_id` - Chunks per document
- `idx_chunks_chunk_num` - Chunk ordering
- `idx_chunks_position` - Positional queries
- `idx_chunks_token_count` - Size-based queries
- `idx_chunks_fts` - Full-text search
- `idx_chunks_created_at` - Time-based queries

**Token Count Validation:**
```python
# Use tiktoken or similar
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
tokens = enc.encode(chunk_content)
token_count = len(tokens)

# Validate: 100 < tokens < 2000 (recommended)
assert 100 < token_count < 2000
```

---

### 4. EMBEDDINGS

**Purpose:** Metadata for vectors stored in Qdrant

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    embedding_type VARCHAR(50) NOT NULL CHECK (embedding_type IN ('fastembed', 'ancient-bert', 'onnx-minilm')),
    vector_dims INTEGER NOT NULL CHECK (vector_dims > 0),
    vector_norm DECIMAL(5, 4),
    qdrant_id BIGINT UNIQUE,
    qdrant_score DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    indexed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    UNIQUE(chunk_id, embedding_type)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| chunk_id | UUID | Parent chunk | Required, Foreign Key, Cascade delete |
| embedding_type | VARCHAR(50) | Model type | fastembed \| ancient-bert \| onnx-minilm |
| vector_dims | INTEGER | Embedding dimension | > 0 (384, 768, etc.) |
| vector_norm | DECIMAL(5, 4) | L2 norm (0-1) | For validation |
| qdrant_id | BIGINT | Qdrant point ID | Unique, for sync |
| qdrant_score | DECIMAL(5, 4) | Last search score | 0-1 range |
| created_at | TIMESTAMP TZ | Creation timestamp | Auto-set |
| indexed_at | TIMESTAMP TZ | When indexed in Qdrant | Set during indexing |
| metadata | JSONB | Model version, etc. | {model_version: "0.1.0"} |

**Indices:**
- `idx_embeddings_chunk_id` - Chunk lookups
- `idx_embeddings_type` - Model-specific queries
- `idx_embeddings_indexed_at` - Recently indexed
- `idx_embeddings_qdrant_id` - Qdrant sync
- `idx_embeddings_created_at` - Time-based queries

**Embedding Models:**

| Model | Dimension | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| FastEmbed | 384 | Fast | Good | Primary (recommended) |
| Ancient-BERT | 768 | Medium | Excellent | High-quality search |
| ONNX-MiniLM | 384 | Very Fast | Good | Low-latency queries |

---

### 5. KNOWLEDGE_RELATIONS

**Purpose:** Explicit links between documents with typed relationships

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS knowledge_relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    target_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    relation_type VARCHAR(100) NOT NULL,
    strength DECIMAL(3, 2) NOT NULL CHECK (strength >= 0 AND strength <= 1),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT no_self_relations CHECK (source_doc_id != target_doc_id),
    CONSTRAINT relation_type_not_empty CHECK (length(trim(relation_type)) > 0),
    UNIQUE(source_doc_id, target_doc_id, relation_type)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| source_doc_id | UUID | Source document | Required, Foreign Key |
| target_doc_id | UUID | Target document | Required, Foreign Key |
| relation_type | VARCHAR(100) | Type of relation | references, extends, contradicts, etc. |
| strength | DECIMAL(3, 2) | Relation strength | 0-1 (0=weak, 1=strong) |
| metadata | JSONB | Additional context | {confidence: 0.95} |
| created_at | TIMESTAMP TZ | Creation timestamp | Auto-set |
| updated_at | TIMESTAMP TZ | Last update timestamp | Auto-set |

**Indices:**
- `idx_knowledge_relations_source` - Outgoing relations
- `idx_knowledge_relations_target` - Incoming relations
- `idx_knowledge_relations_type` - Type filtering
- `idx_knowledge_relations_strength` - Strength ranking
- `idx_knowledge_relations_created_at` - Time-based queries

**Relation Types (Examples):**
- `references` - Document A references Document B
- `extends` - Document A builds on Document B
- `contradicts` - Document A contradicts Document B
- `related_to` - General relevance link
- `prerequisite` - Document A is prerequisite for B

---

### 6. AGENT_PERSONAS

**Purpose:** AI agent configuration and learning state

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS agent_personas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(255) NOT NULL UNIQUE,
    persona_type VARCHAR(100) NOT NULL,
    domain_focus UUID REFERENCES knowledge_domains(id) ON DELETE SET NULL,
    learning_state_json JSONB DEFAULT '{}'::jsonb,
    expertise_level DECIMAL(3, 2) CHECK (expertise_level >= 0 AND expertise_level <= 1),
    interaction_count INTEGER DEFAULT 0 CHECK (interaction_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT agent_name_not_empty CHECK (length(trim(agent_name)) > 0),
    CONSTRAINT persona_type_not_empty CHECK (length(trim(persona_type)) > 0)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| agent_name | VARCHAR(255) | Agent identifier | Required, Unique, Non-empty |
| persona_type | VARCHAR(100) | Agent role type | assistant, researcher, reviewer, etc. |
| domain_focus | UUID | Primary domain | Optional, Foreign Key |
| learning_state_json | JSONB | Agent memory/learning | {context: {...}, preferences: {...}} |
| expertise_level | DECIMAL(3, 2) | Proficiency (0-1) | 0 = novice, 1 = expert |
| interaction_count | INTEGER | Total interactions | >= 0 |
| created_at | TIMESTAMP TZ | Creation timestamp | Auto-set |
| updated_at | TIMESTAMP TZ | Last update timestamp | Auto-set |

**Indices:**
- `idx_agent_personas_name` - Agent lookup
- `idx_agent_personas_type` - Type filtering
- `idx_agent_personas_domain` - Domain-specific agents
- `idx_agent_personas_expertise` - Expertise ranking
- `idx_agent_personas_created_at` - Time-based queries

---

### 7. AGENT_EVOLUTION_LOG

**Purpose:** Audit trail of agent learning and state changes

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS agent_evolution_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agent_personas(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    change_type VARCHAR(100) NOT NULL,
    old_values_json JSONB DEFAULT '{}'::jsonb,
    new_values_json JSONB DEFAULT '{}'::jsonb,
    interaction_count INTEGER CHECK (interaction_count >= 0),
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT change_type_not_empty CHECK (length(trim(change_type)) > 0)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| agent_id | UUID | Related agent | Required, Foreign Key, Cascade delete |
| timestamp | TIMESTAMP TZ | Change timestamp | Auto-set |
| change_type | VARCHAR(100) | Type of change | learning, expertise_update, domain_shift, etc. |
| old_values_json | JSONB | Previous state | Snapshot of old values |
| new_values_json | JSONB | New state | Snapshot of new values |
| interaction_count | INTEGER | Cumulative interactions | >= 0 |
| metadata | JSONB | Additional context | {confidence_delta: 0.05} |

**Indices:**
- `idx_agent_evolution_log_agent_id` - Agent history
- `idx_agent_evolution_log_timestamp` - Time-based queries
- `idx_agent_evolution_log_change_type` - Change filtering
- `idx_agent_evolution_log_agent_timestamp` - Agent + time combo

---

### 8. CURATED_COLLECTIONS

**Purpose:** User/agent-curated document subsets

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS curated_collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    owner_agent_id UUID NOT NULL REFERENCES agent_personas(id) ON DELETE CASCADE,
    domain_id UUID REFERENCES knowledge_domains(id) ON DELETE SET NULL,
    documents_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT name_not_empty CHECK (length(trim(name)) > 0),
    UNIQUE(owner_agent_id, domain_id, name)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| name | VARCHAR(255) | Collection name | Required, Non-empty |
| owner_agent_id | UUID | Curator agent | Required, Foreign Key |
| domain_id | UUID | Associated domain | Optional, Foreign Key |
| documents_json | JSONB | Array of doc IDs | [{id: "...", position: 0}, ...] |
| description | TEXT | Collection description | Optional |
| metadata | JSONB | Custom metadata | {tags: [...], ratings: [...]} |
| created_at | TIMESTAMP TZ | Creation timestamp | Auto-set |
| updated_at | TIMESTAMP TZ | Last update timestamp | Auto-set |

**Indices:**
- `idx_curated_collections_owner` - Agent's collections
- `idx_curated_collections_domain` - Domain collections
- `idx_curated_collections_name` - Collection lookup
- `idx_curated_collections_created_at` - Time-based queries

---

### 9. AUDIT_LOG

**Purpose:** Comprehensive operational history for compliance and debugging

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    operation_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    user_id VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    before_state_json JSONB DEFAULT '{}'::jsonb,
    after_state_json JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT operation_type_not_empty CHECK (length(trim(operation_type)) > 0),
    CONSTRAINT resource_type_not_empty CHECK (length(trim(resource_type)) > 0)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | BIGSERIAL | Primary key (sequential) | Auto-increment |
| operation_type | VARCHAR(100) | Operation: CREATE/UPDATE/DELETE | Required, Non-empty |
| resource_type | VARCHAR(100) | Resource: document/chunk/user | Required, Non-empty |
| resource_id | VARCHAR(255) | Resource identifier | Optional |
| user_id | VARCHAR(255) | User performing operation | Optional |
| timestamp | TIMESTAMP TZ | Operation timestamp | Auto-set, indexed |
| before_state_json | JSONB | Previous state snapshot | For updates |
| after_state_json | JSONB | New state snapshot | For updates |
| ip_address | INET | Client IP address | For security audit |
| user_agent | TEXT | HTTP user agent | For security audit |
| metadata | JSONB | Additional context | {trace_id: "...", duration_ms: 123} |

**Indices:**
- `idx_audit_log_timestamp` - Time-based queries
- `idx_audit_log_resource` - Resource lookups
- `idx_audit_log_operation` - Operation filtering
- `idx_audit_log_user_id` - User activity tracking
- `idx_audit_log_resource_timestamp` - Resource timeline

**Retention Policy:**
- GDPR: Keep for 7 years max
- Default: Keep for 1 year
- Query: `DELETE FROM audit_log WHERE timestamp < NOW() - INTERVAL '1 year'`

---

### 10. QUERY_CACHE

**Purpose:** Caching query results for performance optimization

**Definition:**
```sql
CREATE TABLE IF NOT EXISTS query_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_hash VARCHAR(64) NOT NULL UNIQUE,
    query_text TEXT NOT NULL,
    results_json JSONB NOT NULL,
    result_count INTEGER DEFAULT 0,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    hit_count INTEGER DEFAULT 0,
    
    CONSTRAINT query_hash_not_empty CHECK (length(trim(query_hash)) > 0)
);
```

**Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary key | Unique, auto-generated |
| query_hash | VARCHAR(64) | SHA256 of query | Required, Unique, Non-empty |
| query_text | TEXT | Original query | Full text for debugging |
| results_json | JSONB | Cached results | Serialized result set |
| result_count | INTEGER | Number of results | >= 0 |
| execution_time_ms | INTEGER | Execution time | For metrics |
| created_at | TIMESTAMP TZ | Cache creation time | Auto-set |
| expires_at | TIMESTAMP TZ | Cache expiration | Query TTL (e.g., +5 minutes) |
| hit_count | INTEGER | Number of cache hits | Incremented on access |

**Indices:**
- `idx_query_cache_hash` - HASH index for O(1) lookup
- `idx_query_cache_expires_at` - Expiration cleanup
- `idx_query_cache_created_at` - Time-based stats

**Cleanup Query:**
```sql
-- Run periodically (e.g., nightly)
DELETE FROM query_cache WHERE expires_at < NOW();
```

---

## Materialized Views

### 1. document_stats_by_domain

**Purpose:** Performance statistics aggregated by domain

```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS document_stats_by_domain AS
SELECT 
    kd.id as domain_id,
    kd.name as domain_name,
    COUNT(DISTINCT d.id) as total_documents,
    COUNT(DISTINCT c.id) as total_chunks,
    SUM(c.token_count) as total_tokens,
    AVG(c.token_count)::INTEGER as avg_tokens_per_chunk,
    MIN(d.created_at) as oldest_document,
    MAX(d.updated_at) as latest_update
FROM knowledge_domains kd
LEFT JOIN documents d ON d.domain_id = kd.id AND d.status = 'active'
LEFT JOIN chunks c ON c.doc_id = d.id
GROUP BY kd.id, kd.name;

CREATE INDEX ON document_stats_by_domain(domain_id);
```

**Usage:**
```sql
SELECT * FROM document_stats_by_domain WHERE domain_name = 'Technology';
```

### 2. chunk_stats_by_model

**Purpose:** Embedding model coverage and statistics

```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS chunk_stats_by_model AS
SELECT 
    e.embedding_type as model,
    e.vector_dims as dimensions,
    COUNT(DISTINCT e.id) as total_embeddings,
    COUNT(DISTINCT c.id) as chunks_covered,
    COUNT(DISTINCT d.id) as documents_covered,
    AVG(c.token_count)::INTEGER as avg_chunk_tokens,
    MAX(e.indexed_at) as latest_indexed
FROM embeddings e
JOIN chunks c ON e.chunk_id = c.id
JOIN documents d ON c.doc_id = d.id
GROUP BY e.embedding_type, e.vector_dims;

CREATE INDEX ON chunk_stats_by_model(model);
```

### 3. agent_interaction_metrics

**Purpose:** Agent activity and learning metrics

```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS agent_interaction_metrics AS
SELECT 
    ap.id as agent_id,
    ap.agent_name,
    ap.persona_type,
    ap.expertise_level,
    ap.interaction_count,
    COUNT(DISTINCT ael.id) as state_changes,
    MAX(ael.timestamp) as last_state_change,
    COUNT(DISTINCT cc.id) as curated_collections
FROM agent_personas ap
LEFT JOIN agent_evolution_log ael ON ap.id = ael.agent_id
LEFT JOIN curated_collections cc ON ap.id = cc.owner_agent_id
GROUP BY ap.id, ap.agent_name, ap.persona_type, ap.expertise_level, ap.interaction_count;

CREATE INDEX ON agent_interaction_metrics(agent_id);
```

---

## Sample Queries

### Document Retrieval

```sql
-- Get all active documents in a domain
SELECT d.id, d.title, d.source, COUNT(c.id) as chunk_count
FROM documents d
LEFT JOIN chunks c ON d.id = c.doc_id
WHERE d.domain_id = $1 AND d.status = 'active'
GROUP BY d.id, d.title, d.source;

-- Find documents updated in last 7 days
SELECT id, title, updated_at
FROM documents
WHERE updated_at > NOW() - INTERVAL '7 days'
ORDER BY updated_at DESC;

-- Full-text search
SELECT id, title, ts_rank(to_tsvector('english', title || ' ' || content), query) as rank
FROM documents, to_tsquery('english', 'machine learning') query
WHERE to_tsvector('english', title || ' ' || content) @@ query
ORDER BY rank DESC;
```

### Chunk Analysis

```sql
-- Get chunks for a document
SELECT chunk_num, token_count, position_in_doc
FROM chunks
WHERE doc_id = $1
ORDER BY chunk_num;

-- Find large chunks (potential split candidates)
SELECT id, doc_id, chunk_num, token_count
FROM chunks
WHERE token_count > 1500
ORDER BY token_count DESC;

-- Calculate domain token distribution
SELECT d.id, d.name, SUM(c.token_count) as total_tokens
FROM knowledge_domains d
LEFT JOIN documents doc ON d.id = doc.domain_id
LEFT JOIN chunks c ON doc.id = c.doc_id
GROUP BY d.id, d.name
ORDER BY total_tokens DESC;
```

### Embedding Coverage

```sql
-- Check embedding coverage per model
SELECT 
    embedding_type,
    COUNT(*) as total,
    COUNT(indexed_at) as indexed,
    COUNT(*) - COUNT(indexed_at) as pending
FROM embeddings
GROUP BY embedding_type;

-- Find chunks without embeddings
SELECT c.id, c.doc_id, c.chunk_num
FROM chunks c
LEFT JOIN embeddings e ON c.id = e.chunk_id
WHERE e.id IS NULL;

-- List embeddings by recency
SELECT chunk_id, embedding_type, indexed_at
FROM embeddings
ORDER BY indexed_at DESC
LIMIT 20;
```

### Relationship Analysis

```sql
-- Find all relations for a document
SELECT 
    kr.relation_type,
    COUNT(*) as count,
    AVG(kr.strength) as avg_strength
FROM knowledge_relations kr
WHERE kr.source_doc_id = $1
GROUP BY kr.relation_type;

-- Find strongly related documents (strength >= 0.8)
SELECT target_doc_id, relation_type, strength
FROM knowledge_relations
WHERE source_doc_id = $1 AND strength >= 0.8
ORDER BY strength DESC;

-- Transitive relations (A -> B -> C)
SELECT 
    kr1.source_doc_id as from_doc,
    kr2.target_doc_id as to_doc,
    kr1.relation_type || ' -> ' || kr2.relation_type as path
FROM knowledge_relations kr1
JOIN knowledge_relations kr2 ON kr1.target_doc_id = kr2.source_doc_id
WHERE kr1.source_doc_id = $1;
```

### Agent Analysis

```sql
-- Agent expertise and activity
SELECT 
    agent_name,
    persona_type,
    expertise_level,
    interaction_count,
    updated_at
FROM agent_personas
ORDER BY expertise_level DESC, interaction_count DESC;

-- Track agent learning over time
SELECT 
    agent_id,
    timestamp,
    change_type,
    new_values_json -> 'expertise_level' as new_expertise
FROM agent_evolution_log
WHERE change_type = 'expertise_update'
ORDER BY timestamp DESC;

-- Agent collections
SELECT 
    ap.agent_name,
    cc.name,
    jsonb_array_length(cc.documents_json) as doc_count,
    cc.created_at
FROM agent_personas ap
JOIN curated_collections cc ON ap.id = cc.owner_agent_id
ORDER BY cc.created_at DESC;
```

### Audit & Compliance

```sql
-- User activity log
SELECT 
    user_id,
    operation_type,
    COUNT(*) as count,
    MAX(timestamp) as last_activity
FROM audit_log
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY user_id, operation_type
ORDER BY count DESC;

-- All changes to a specific document
SELECT 
    timestamp,
    operation_type,
    user_id,
    before_state_json,
    after_state_json
FROM audit_log
WHERE resource_type = 'document' AND resource_id = $1
ORDER BY timestamp DESC;

-- Access patterns
SELECT 
    resource_type,
    COUNT(*) as access_count,
    COUNT(DISTINCT user_id) as unique_users
FROM audit_log
WHERE timestamp > NOW() - INTERVAL '1 week'
GROUP BY resource_type
ORDER BY access_count DESC;
```

### Performance Metrics

```sql
-- Cache hit rate
SELECT 
    COUNT(CASE WHEN hit_count > 0 THEN 1 END)::float / COUNT(*) as hit_rate,
    COUNT(CASE WHEN hit_count > 0 THEN 1 END) as hits,
    COUNT(*) as total_queries
FROM query_cache
WHERE created_at > NOW() - INTERVAL '1 hour';

-- Query performance distribution
SELECT 
    MIN(execution_time_ms) as min_ms,
    AVG(execution_time_ms) as avg_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) as p95_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY execution_time_ms) as p99_ms,
    MAX(execution_time_ms) as max_ms
FROM query_cache
WHERE created_at > NOW() - INTERVAL '1 day';

-- Most expensive queries
SELECT 
    query_hash,
    query_text,
    COUNT(*) as run_count,
    AVG(execution_time_ms) as avg_ms,
    MAX(execution_time_ms) as max_ms
FROM query_cache
GROUP BY query_hash, query_text
ORDER BY avg_ms DESC
LIMIT 10;
```

---

## Constraints & Referential Integrity

### Foreign Key Relationships

```
knowledge_domains (self-referential)
    ↓ parent_id
    └─ knowledge_domains

documents
    ├─ domain_id → knowledge_domains
    └─ ON DELETE RESTRICT

chunks
    ├─ doc_id → documents
    └─ ON DELETE CASCADE

embeddings
    ├─ chunk_id → chunks
    └─ ON DELETE CASCADE

knowledge_relations
    ├─ source_doc_id → documents
    ├─ target_doc_id → documents
    └─ ON DELETE CASCADE

agent_personas
    └─ domain_focus → knowledge_domains

agent_evolution_log
    └─ agent_id → agent_personas (CASCADE)

curated_collections
    ├─ owner_agent_id → agent_personas (CASCADE)
    └─ domain_id → knowledge_domains
```

### Check Constraints

- Domain names must be non-empty
- Document titles must be non-empty
- Chunk content must be non-empty
- Relation strength must be 0-1
- Expertise level must be 0-1
- No self-relations allowed

---

**Document Version:** 1.0
**Last Updated:** 2026-02-25
**Status:** Active
**Audience:** Database Administrators, Backend Developers
