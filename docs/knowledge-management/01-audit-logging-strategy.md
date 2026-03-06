---
title: Audit Logging Strategy for Knowledge Operations
last_updated: 2026-02-25
status: implemented
persona_focus: [database-architect, compliance-officer]
---

# Audit Logging Strategy for Knowledge Management

## Executive Summary

Comprehensive audit logging system for all knowledge management operations (KM operations), supporting 10K+ operations/day with <5% query overhead, full ACID compliance, and security/compliance auditing requirements.

## Operational Scope

### 1. Audit Categories

#### Document Lifecycle
- `doc_created`: New document ingested
- `doc_updated`: Document metadata or content modified
- `doc_deleted`: Document removed from system
- `doc_accessed`: Read operations (sampled at 1-in-100)

#### Chunk Management
- `chunk_created`: Document split into chunks
- `chunk_updated`: Chunk content/metadata modified
- `chunk_deleted`: Chunk removed
- `chunk_indexed`: Chunk added to vector index (sampled)

#### Embeddings
- `embedding_created`: Vector computed for content
- `embedding_updated`: Vector regenerated
- `embedding_deleted`: Vector removed
- `embedding_indexed`: Vector stored in index (sampled)

#### Query Operations
- `query_executed`: User/agent query initiated
- `query_completed`: Query returned results
- `query_error`: Query failed

#### Access Control
- `permission_granted`: User/agent granted access
- `permission_revoked`: Access removed
- `permission_checked`: Access validation (sampled)

### 2. Log Entry Schema

```sql
-- Core audit log entry
{
  audit_id: UUID (PRIMARY KEY),
  timestamp: TIMESTAMPTZ NOT NULL,
  operation_type: VARCHAR(32) NOT NULL,  -- doc_created, chunk_updated, etc.
  resource_type: VARCHAR(32) NOT NULL,   -- document, chunk, embedding, query
  resource_id: UUID NOT NULL,
  user_id: VARCHAR(255),                 -- NULL for system operations
  agent_id: VARCHAR(255),                -- NULL for user operations
  before_state: JSONB,                   -- Previous values (for UPDATE/DELETE)
  after_state: JSONB,                    -- New values (for CREATE/UPDATE)
  changes: JSONB,                        -- Structured diff of changes
  metadata: JSONB,                       -- Operation-specific metadata
  trace_id: UUID,                        -- For request tracing
  span_id: UUID,                         -- For distributed tracing
  success: BOOLEAN DEFAULT TRUE,
  error_message: TEXT,
  execution_time_ms: INTEGER,
  data_size_bytes: INTEGER,
  ip_address: INET,
  user_agent: TEXT
}
```

### 3. Logging Levels

| Level | Sampling | Use Case |
|-------|----------|----------|
| FULL | 100% | CREATE, UPDATE, DELETE operations |
| SAMPLED | 1% | READ operations, permission checks |
| NONE | 0% | High-frequency operations like health checks |

## Technical Implementation

### 1. Storage Architecture

#### Hot Storage (Current Year)
- **Table**: `audit_log_current`
- **Retention**: 1 year
- **Location**: Primary PostgreSQL
- **Indexing**: Comprehensive indexes on frequently queried fields

#### Archive Storage
- **Table**: `audit_log_archive`
- **Retention**: 7 years (legal requirement)
- **Location**: PostgreSQL (separate schema) or S3 with Parquet
- **Compression**: LZ4 for hot, Zstd for archive

#### Real-Time Stream (Optional)
- **Kafka/Redis Stream**: For real-time audit dashboards
- **Retention**: 7 days
- **Partition**: By operation_type and resource_type

### 2. Database Schema Design

```sql
-- Main audit log table (partitioned by month)
CREATE TABLE audit_log_current (
  audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMPTZ NOT NULL,
  operation_type VARCHAR(32) NOT NULL,
  resource_type VARCHAR(32) NOT NULL,
  resource_id UUID NOT NULL,
  user_id VARCHAR(255),
  agent_id VARCHAR(255),
  before_state JSONB,
  after_state JSONB,
  changes JSONB,
  metadata JSONB,
  trace_id UUID,
  span_id UUID,
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT,
  execution_time_ms INTEGER,
  data_size_bytes INTEGER,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Indexes for common queries
CREATE INDEX idx_audit_resource ON audit_log_current (resource_type, resource_id, timestamp DESC);
CREATE INDEX idx_audit_user ON audit_log_current (user_id, timestamp DESC);
CREATE INDEX idx_audit_agent ON audit_log_current (agent_id, timestamp DESC);
CREATE INDEX idx_audit_operation ON audit_log_current (operation_type, timestamp DESC);
CREATE INDEX idx_audit_timestamp ON audit_log_current (timestamp DESC);
CREATE INDEX idx_audit_trace ON audit_log_current (trace_id) WHERE trace_id IS NOT NULL;
CREATE INDEX idx_audit_success ON audit_log_current (success, timestamp DESC) WHERE NOT success;

-- GIN index for JSONB fields
CREATE INDEX idx_audit_metadata_gin ON audit_log_current USING GIN (metadata);
```

### 3. Trigger-Based Automatic Logging

#### Document Table Trigger
```sql
CREATE OR REPLACE FUNCTION audit_document_changes()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log_current (
    operation_type, resource_type, resource_id, user_id,
    before_state, after_state, changes, timestamp, success
  ) VALUES (
    CASE
      WHEN TG_OP = 'INSERT' THEN 'doc_created'
      WHEN TG_OP = 'UPDATE' THEN 'doc_updated'
      WHEN TG_OP = 'DELETE' THEN 'doc_deleted'
    END,
    'document',
    COALESCE(NEW.id, OLD.id),
    COALESCE(current_setting('app.user_id'), NULL),
    CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
    CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END,
    CASE
      WHEN TG_OP = 'UPDATE' THEN
        jsonb_object_agg(
          key,
          jsonb_build_object('old', old_values->>key, 'new', new_values->>key)
        )
      ELSE NULL
    END,
    CURRENT_TIMESTAMP,
    TRUE
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_documents
AFTER INSERT OR UPDATE OR DELETE ON documents
FOR EACH ROW
EXECUTE FUNCTION audit_document_changes();
```

#### Sampling for High-Volume Operations
```sql
-- Sampled logging for queries (1 in 100)
CREATE OR REPLACE FUNCTION audit_query_execution()
RETURNS TRIGGER AS $$
BEGIN
  IF random() < 0.01 THEN  -- 1% sampling
    INSERT INTO audit_log_current (
      operation_type, resource_type, resource_id, user_id, agent_id,
      metadata, timestamp, execution_time_ms, success
    ) VALUES (
      'query_executed',
      'query',
      NEW.query_id,
      COALESCE(current_setting('app.user_id'), NULL),
      COALESCE(current_setting('app.agent_id'), NULL),
      jsonb_build_object(
        'query_text', NEW.query_text,
        'collection', NEW.collection,
        'limit', NEW.result_limit
      ),
      CURRENT_TIMESTAMP,
      NEW.execution_time_ms,
      NEW.success
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 4. Application-Level Logging

For operations not captured by triggers (e.g., API calls), use Python decorator:

```python
from functools import wraps
from typing import Any, Callable
import uuid
import time

def audit_log(operation_type: str, resource_type: str):
    """Decorator for audit logging at application level."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            audit_id = uuid.uuid4()
            start_time = time.time()
            
            try:
                # Capture before state
                before_state = kwargs.get('before_state', None)
                
                # Execute operation
                result = await func(*args, **kwargs)
                
                # Log success
                elapsed_ms = int((time.time() - start_time) * 1000)
                await log_audit_entry(
                    audit_id=audit_id,
                    operation_type=operation_type,
                    resource_type=resource_type,
                    resource_id=kwargs.get('resource_id'),
                    after_state=result,
                    execution_time_ms=elapsed_ms,
                    success=True
                )
                return result
            except Exception as e:
                # Log failure
                elapsed_ms = int((time.time() - start_time) * 1000)
                await log_audit_entry(
                    audit_id=audit_id,
                    operation_type=operation_type,
                    resource_type=resource_type,
                    resource_id=kwargs.get('resource_id'),
                    execution_time_ms=elapsed_ms,
                    success=False,
                    error_message=str(e)
                )
                raise
        
        return async_wrapper
    return decorator
```

## Performance Considerations

### 1. Overhead Budget

- **Target**: <5% query slowdown
- **Baseline**: Unlogged operation = 100ms
- **Allowed overhead**: 5ms per operation
- **Monitoring**: Track `execution_time_ms` distribution

### 2. Partitioning Strategy

- **Primary**: Monthly partitioning (RANGE on `created_at`)
- **Benefit**: Archive old partitions without full table scan
- **Rotation**: Auto-create next month partition on 25th

### 3. Index Tuning

| Index | Purpose | Query Type |
|-------|---------|-----------|
| `idx_audit_resource` | Find changes to specific resource | Compliance reports |
| `idx_audit_user` | Find user activity timeline | Access reviews |
| `idx_audit_operation` | Count by operation type | Usage metrics |
| `idx_audit_timestamp` | Range queries | Date-based reports |
| `idx_audit_trace` | Distributed tracing | Request correlation |

### 4. Async Logging

```python
# Use thread pool for I/O-bound logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

log_executor = ThreadPoolExecutor(max_workers=4)

async def async_log_audit(entry: Dict) -> None:
    """Non-blocking audit log insertion."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(log_executor, _sync_insert_audit, entry)
```

## Retention and Archival

### 1. Retention Policy

```sql
-- Current operations: 1 year
ALTER TABLE audit_log_current ENABLE ROW LEVEL SECURITY;
CREATE POLICY audit_retention ON audit_log_current
  USING (created_at >= CURRENT_DATE - INTERVAL '1 year');

-- Archive: 7 years
ALTER TABLE audit_log_archive ENABLE ROW LEVEL SECURITY;
CREATE POLICY archive_retention ON audit_log_archive
  USING (created_at >= CURRENT_DATE - INTERVAL '7 years');
```

### 2. Monthly Archival Process

```sql
-- Run on 1st of each month at 02:00 UTC
CREATE PROCEDURE archive_audit_logs(
  archive_month DATE DEFAULT CURRENT_DATE - INTERVAL '1 month'
) AS $$
BEGIN
  -- Move previous month partition to archive
  INSERT INTO audit_log_archive
  SELECT * FROM audit_log_current
  WHERE created_at >= DATE_TRUNC('month', archive_month)
    AND created_at < DATE_TRUNC('month', archive_month + INTERVAL '1 month');
  
  -- Drop old partition
  EXECUTE FORMAT('DROP TABLE IF EXISTS audit_log_current_%s',
    TO_CHAR(archive_month, 'YYYY_MM'));
  
  -- Vacuum and reindex
  VACUUM ANALYZE audit_log_current;
END;
$$ LANGUAGE plpgsql;
```

### 3. Long-Term Archive (S3)

```python
# Quarterly export to S3 for 7-year retention
async def export_audit_logs_to_s3(quarter: str) -> None:
    """Export quarterly audit logs to S3 with Parquet compression."""
    query = f"""
    SELECT * FROM audit_log_archive
    WHERE created_at >= '{quarter_start}'
      AND created_at < '{quarter_end}'
    """
    
    df = await read_query_to_dataframe(query)
    
    # Save to S3 with Zstd compression
    s3_path = f"s3://xnai-audit-archive/{year}/{quarter}/audit_logs.parquet.zst"
    df.to_parquet(s3_path, compression='zstd', index=False)
    
    logger.info(f"Exported {len(df)} audit logs to {s3_path}")
```

## Compliance and Security

### 1. Immutability

- **Write-Once**: Audit logs are append-only, never updated/deleted
- **Constraint**: No UPDATE or DELETE permissions on audit tables for users
- **Enforcement**: Database-level REVOKE statements

### 2. Access Control

```sql
-- Create audit reader role (read-only)
CREATE ROLE audit_reader;
GRANT SELECT ON audit_log_current, audit_log_archive TO audit_reader;

-- Create audit admin role (maintenance only)
CREATE ROLE audit_admin;
GRANT ALL ON audit_log_current, audit_log_archive TO audit_admin;
```

### 3. Tamper Detection

```sql
-- Hash-chain for tamper detection (optional)
CREATE TABLE audit_log_checksums (
  partition_id VARCHAR(32) PRIMARY KEY,
  record_count BIGINT,
  checksum_hash BYTEA,
  previous_hash BYTEA,
  computed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Verify integrity
CREATE OR REPLACE FUNCTION verify_audit_integrity(
  partition_id VARCHAR(32)
) RETURNS TABLE(is_valid BOOLEAN, details TEXT) AS $$
BEGIN
  -- Recalculate hash of all records in partition
  -- Compare with stored checksum
END;
$$ LANGUAGE plpgsql;
```

## Reporting and Queries

### 1. Pre-Built Queries

See `02-audit-queries.sql` for:
- Find all changes to a document
- User activity timeline
- Compliance reports
- Error analysis
- Performance metrics

### 2. Dashboard Metrics

- **Daily audit entry count**: `SELECT COUNT(*) FROM audit_log_current WHERE created_at >= CURRENT_DATE`
- **Success rate**: `SELECT success, COUNT(*) FROM audit_log_current GROUP BY success`
- **Avg execution time**: `SELECT operation_type, AVG(execution_time_ms) FROM audit_log_current GROUP BY operation_type`
- **Error rate by operation**: `SELECT operation_type, COUNT(*) FROM audit_log_current WHERE NOT success GROUP BY operation_type`

## Implementation Roadmap

| Phase | Deliverable | Timeline |
|-------|-------------|----------|
| 1 | Schema design & triggers | Week 1 |
| 2 | Application-level logging | Week 2 |
| 3 | Query library & dashboards | Week 3 |
| 4 | Archival & retention policies | Week 4 |
| 5 | Compliance validation | Week 5 |

## Related Documentation

- `02-audit-queries.sql`: Pre-built query library
- `03-operational-procedures.md`: Day-to-day operations
- `04-performance-tuning.md`: Optimization guide
- `../README.md`: Knowledge management overview
