# SQL Tracking Tables Implementation Guide

**Status**: ✅ COMPLETE  
**Date**: 2025-02-25  
**Version**: 1.0

## Implementation Summary

### Tables Created (6/6) ✅
1. **document_catalog** - Track documents with metadata
2. **document_changes** - Audit trail for document updates
3. **agent_persona** - Multi-agent personas and learning states
4. **agent_session_state** - Session persistence for agents
5. **knowledge_domain** - Domain hierarchy and organization
6. **embedding_strategy_map** - Query-to-strategy routing

### Indices Created (5/5) ✅
- `idx_document_catalog_domain_status` on (domain, embedding_status)
- `idx_document_changes_doc_timestamp` on (doc_id, timestamp)
- `idx_agent_persona_name_domain` on (agent_name, domain_focus)
- `idx_knowledge_domain_parent` on (parent_id)
- `idx_embedding_strategy_query_domain` on (query_type, content_domain)

### Sample Data ✅
- 8 embedding strategies loaded into `embedding_strategy_map`:
  - General semantic (all-minilm-l6-v2)
  - Code semantic (code-search-ada-code-001)
  - Documentation (all-mpnet-base-v2)
  - Knowledge-base (bge-large-en-v1.5)
  - Lexical fallback (bm25)
  - Hybrid ensemble (hybrid-ensemble)
  - Voice queries (all-minilm-l6-v2)
  - Reasoning queries (e5-large-v2)

## Verification Queries

### Verify Tables Exist
```sql
SELECT name FROM sqlite_master 
WHERE type='table' 
AND name IN ('document_catalog', 'document_changes', 'agent_persona', 
             'agent_session_state', 'knowledge_domain', 'embedding_strategy_map')
ORDER BY name;
```

**Expected**: 6 tables

### Verify Indices Exist
```sql
SELECT name FROM sqlite_master 
WHERE type='index' 
AND name LIKE 'idx_%'
ORDER BY name;
```

**Expected**: 5 indices

### Verify Sample Data
```sql
SELECT COUNT(*) as total_strategies, 
       COUNT(DISTINCT query_type) as query_types,
       COUNT(DISTINCT content_domain) as domains
FROM embedding_strategy_map;
```

**Expected**: 8 strategies, 3 query types, 5 domains

## Quick Start Examples

### 1. Register a Document
```sql
INSERT INTO document_catalog 
  (id, filename, source, domain, size_bytes, chunk_count, embedding_status)
VALUES 
  ('doc_001', 'api_guide.md', 'github', 'documentation', 5120, 10, 'pending');
```

### 2. Track Document Changes
```sql
INSERT INTO document_changes
  (id, doc_id, change_type, reason, changed_by)
VALUES
  ('chg_001', 'doc_001', 'created', 'Initial import', 'system');
```

### 3. Create Agent Persona
```sql
INSERT INTO agent_persona
  (id, agent_name, persona_type, domain_focus, expertise_level)
VALUES
  ('agent_001', 'CodeSpecialist', 'specialist', 'code', 0.92);
```

### 4. Store Agent Session
```sql
INSERT INTO agent_session_state
  (agent_id, session_id, last_query)
VALUES
  ('agent_001', 'sess_123', 'How do I optimize this function?');
```

### 5. Create Domain Hierarchy
```sql
INSERT INTO knowledge_domain
  (id, name, description, parent_id)
VALUES
  ('domain_eng', 'Engineering', 'Technical knowledge', NULL),
  ('domain_backend', 'Backend', 'Backend systems', 'domain_eng'),
  ('domain_api', 'APIs', 'API design and development', 'domain_backend');
```

### 6. Route Query to Strategy
```sql
SELECT embedding_model, preference_score
FROM embedding_strategy_map
WHERE query_type = 'semantic' AND content_domain = 'code'
ORDER BY preference_score DESC LIMIT 1;
```

## Performance Tuning

### Query Optimization Tips

1. **Find pending documents by domain** (uses index)
```sql
SELECT id, filename FROM document_catalog
WHERE domain = 'code' AND embedding_status = 'pending'
LIMIT 100;
```

2. **Get document change history** (uses index)
```sql
SELECT * FROM document_changes
WHERE doc_id = 'doc_001'
ORDER BY timestamp DESC LIMIT 50;
```

3. **Find specialized agents** (uses index)
```sql
SELECT * FROM agent_persona
WHERE domain_focus = 'documentation' AND expertise_level > 0.8;
```

4. **Build domain tree** (uses parent_id index)
```sql
WITH RECURSIVE domain_tree AS (
  SELECT id, name, parent_id, 0 as level
  FROM knowledge_domain
  WHERE parent_id IS NULL
  UNION ALL
  SELECT kd.id, kd.name, kd.parent_id, dt.level + 1
  FROM knowledge_domain kd
  JOIN domain_tree dt ON kd.parent_id = dt.id
)
SELECT * FROM domain_tree ORDER BY level, name;
```

### Index Usage Analysis

```sql
-- Check which indices are available
PRAGMA index_info('idx_document_catalog_domain_status');
PRAGMA index_info('idx_document_changes_doc_timestamp');
PRAGMA index_info('idx_agent_persona_name_domain');
PRAGMA index_info('idx_knowledge_domain_parent');
PRAGMA index_info('idx_embedding_strategy_query_domain');
```

## Data Scaling

### Capacity Planning

| Table | Est. Rows | Storage | Index Size |
|-------|-----------|---------|-----------|
| document_catalog | 100K | ~50MB | ~10MB |
| document_changes | 500K | ~150MB | ~30MB |
| agent_persona | 1K-10K | ~5-50MB | ~2MB |
| agent_session_state | 10K-100K | ~50-500MB | ~10MB |
| knowledge_domain | 1K | ~1MB | ~200KB |
| embedding_strategy_map | 50-100 | ~100KB | ~20KB |

### Maintenance Recommendations

```sql
-- Archive old changes (quarterly)
DELETE FROM document_changes 
WHERE timestamp < datetime('now', '-90 days');

-- Update statistics (monthly)
ANALYZE;

-- Vacuum fragmentation (quarterly)
VACUUM;
```

## Integration with Existing Code

### Python Example
```python
import sqlite3
import json

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Query documents pending embedding
cursor.execute("""
    SELECT id, filename, chunk_count 
    FROM document_catalog 
    WHERE embedding_status = 'pending' 
    AND domain = 'code'
    ORDER BY created_at ASC
    LIMIT 100
""")

for doc_id, filename, chunks in cursor.fetchall():
    # Process document
    print(f"Processing {filename}")
    
    # Update status
    cursor.execute("""
        UPDATE document_catalog 
        SET embedding_status = 'in_progress', updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (doc_id,))
    
    # Log change
    cursor.execute("""
        INSERT INTO document_changes (id, doc_id, change_type, reason, changed_by)
        VALUES (?, ?, 're_embedded', 'Batch processing', 'embedding_service')
    """, (f"chg_{doc_id}_{int(time.time())}", doc_id))

conn.commit()
```

### Query Builder Pattern
```python
def find_documents(domain=None, status=None, limit=100):
    query = "SELECT * FROM document_catalog WHERE 1=1"
    params = []
    
    if domain:
        query += " AND domain = ?"
        params.append(domain)
    
    if status:
        query += " AND embedding_status = ?"
        params.append(status)
    
    query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    return cursor.fetchall()

# Usage
results = find_documents(domain='code', status='pending')
```

## Troubleshooting

### Check Schema Integrity
```sql
-- Verify all tables
SELECT COUNT(*) as table_count 
FROM sqlite_master 
WHERE type='table' 
AND name IN ('document_catalog', 'document_changes', 'agent_persona',
             'agent_session_state', 'knowledge_domain', 'embedding_strategy_map');
-- Should return: 6

-- Verify all indices
SELECT COUNT(*) as index_count
FROM sqlite_master
WHERE type='index'
AND name LIKE 'idx_%';
-- Should return: 5
```

### Monitor Table Growth
```sql
SELECT 
    name,
    COUNT(*) as row_count,
    SUM(pgoffset) as approx_bytes
FROM sqlite_master m
JOIN document_catalog dc ON m.name = 'document_catalog'
GROUP BY m.name;
```

### Check Performance
```sql
EXPLAIN QUERY PLAN
SELECT * FROM document_catalog
WHERE domain = 'code' AND embedding_status = 'pending';
```

## Migration Notes

### If Adding to Existing Database
1. Run `scripts/sql/01-create-tracking-tables.sql`
2. Run `scripts/sql/02-sample-data-embedding-strategies.sql`
3. Verify with the verification queries above
4. Begin populating tables incrementally

### Backing Up
```bash
# Create backup
sqlite3 session.db ".backup session_backup.db"

# Restore from backup
sqlite3 session.db ".restore session_backup.db"
```

## Documentation Files

- **Schema Definition**: `TRACKING-TABLES-SCHEMA.md`
- **DDL Script**: `01-create-tracking-tables.sql`
- **Sample Data**: `02-sample-data-embedding-strategies.sql`
- **This Guide**: `IMPLEMENTATION-GUIDE.md`

---

**Created**: 2025-02-25  
**Version**: 1.0  
**Status**: Production Ready
