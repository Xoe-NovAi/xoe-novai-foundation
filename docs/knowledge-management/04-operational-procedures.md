---
title: Audit Logging Operational Procedures
last_updated: 2026-02-25
status: implemented
persona_focus: [devops-engineer, database-administrator]
---

# Audit Logging - Operational Procedures

## Overview

This document provides day-to-day operational procedures for managing the audit logging system. All procedures assume PostgreSQL 14+ with the audit schema initialized (see `02-audit-schema-implementation.sql`).

## Pre-Flight Checklist

Before going into production, verify:

- [ ] Audit schema created and permissions configured
- [ ] Initial monthly partition created
- [ ] Indexes built and analyzed
- [ ] Trigger functions registered on knowledge tables
- [ ] Application code updated with audit context middleware
- [ ] Retention policies configured
- [ ] Backup strategy tested

## 1. Daily Operations

### 1.1 Monitor Audit Log Health

```bash
#!/bin/bash
# Daily health check - run at 08:00 UTC

psql -U postgres -d xnai_knowledge << 'EOF'
-- Check table sizes
SELECT
  schemaname,
  tablename,
  ROUND(pg_total_relation_size(schemaname||'.'||tablename) / 1024.0 / 1024.0, 2) AS size_mb,
  n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = 'audit'
ORDER BY size_mb DESC;

-- Check for errors in last 24 hours
SELECT
  operation_type,
  COUNT(*) AS error_count,
  MAX(timestamp) AS latest_error,
  ARRAY_AGG(DISTINCT error_message ORDER BY error_message)[1:3] AS sample_errors
FROM audit.audit_log_current
WHERE NOT success
  AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY operation_type
HAVING COUNT(*) > 0
ORDER BY error_count DESC;

-- Performance check
SELECT
  operation_type,
  ROUND(AVG(execution_time_ms)::NUMERIC, 2) AS avg_ms,
  MAX(execution_time_ms) AS max_ms,
  COUNT(*) FILTER (WHERE execution_time_ms > 5000) AS slow_ops
FROM audit.audit_log_current
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY operation_type
ORDER BY avg_ms DESC
LIMIT 10;
EOF
```

### 1.2 Verify Trigger Functionality

```sql
-- Check if triggers are active
SELECT
  trigger_name,
  event_manipulation,
  event_object_table,
  action_orientation
FROM information_schema.triggers
WHERE trigger_schema IN ('public', 'knowledge')
  AND trigger_name LIKE 'trg_audit%'
ORDER BY event_object_table;

-- Verify recent audit entries exist
SELECT
  operation_type,
  COUNT(*) AS log_count,
  MAX(timestamp) AS latest,
  MIN(timestamp) AS oldest
FROM audit.audit_log_current
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY operation_type
ORDER BY log_count DESC;
```

### 1.3 Check Disk Usage Trends

```sql
-- Estimate daily growth rate
WITH daily_sizes AS (
  SELECT
    DATE(timestamp) AS log_date,
    COUNT(*) AS entry_count,
    SUM(COALESCE(data_size_bytes, 0)) AS total_bytes
  FROM audit.audit_log_current
  WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
  GROUP BY DATE(timestamp)
)
SELECT
  log_date,
  entry_count,
  ROUND(total_bytes / 1024.0 / 1024.0, 2) AS size_mb,
  ROUND(
    AVG(entry_count) OVER (
      ORDER BY log_date
      ROWS BETWEEN 7 PRECEDING AND CURRENT ROW
    ),
    0
  ) AS rolling_avg_entries
FROM daily_sizes
ORDER BY log_date DESC;
```

## 2. Weekly Operations

### 2.1 Audit Log Integrity Check

```sql
-- Run weekly on Sunday
-- Verify record counts match expected volumes

WITH expected_volume AS (
  SELECT
    'documents' AS entity,
    (SELECT COUNT(*) FROM documents) * 0.5 AS expected_operations
  -- Assume 50% of documents are modified weekly
)
SELECT
  'Document operations' AS check_type,
  COUNT(*) AS actual_count,
  (SELECT expected_operations FROM expected_volume LIMIT 1) AS expected_count,
  CASE
    WHEN COUNT(*) < (SELECT expected_operations FROM expected_volume LIMIT 1) * 0.7
    THEN 'WARNING: Below expected volume'
    WHEN COUNT(*) > (SELECT expected_operations FROM expected_volume LIMIT 1) * 1.3
    THEN 'ALERT: Above expected volume'
    ELSE 'OK'
  END AS status
FROM audit.audit_log_current
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
  AND operation_type LIKE 'doc_%';
```

### 2.2 Review Access Patterns

```sql
-- Find unusual user activity
SELECT
  user_id,
  COUNT(*) AS operation_count,
  COUNT(DISTINCT resource_type) AS resource_types,
  COUNT(*) FILTER (WHERE NOT success) AS failures,
  MIN(timestamp) AS first_op,
  MAX(timestamp) AS last_op,
  (MAX(timestamp) - MIN(timestamp)) AS time_span
FROM audit.audit_log_current
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
  AND user_id IS NOT NULL
  AND user_id NOT IN (SELECT system_user FROM system_configuration)  -- Exclude service accounts
GROUP BY user_id
HAVING COUNT(*) > 1000  -- Threshold for investigation
ORDER BY operation_count DESC;
```

### 2.3 Performance Analysis

```sql
-- Identify slow operations needing optimization
SELECT
  operation_type,
  resource_type,
  COUNT(*) AS occurrence_count,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) AS p95_ms,
  MAX(execution_time_ms) AS max_ms,
  ROUND(AVG(execution_time_ms)::NUMERIC, 2) AS avg_ms,
  CASE
    WHEN PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) > 5000
    THEN 'OPTIMIZE: >5s'
    WHEN PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) > 1000
    THEN 'REVIEW: >1s'
    ELSE 'OK'
  END AS recommendation
FROM audit.audit_log_current
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY operation_type, resource_type
ORDER BY p95_ms DESC;
```

## 3. Monthly Operations

### 3.1 Archive Old Logs

**Run on 1st of month at 02:00 UTC**

```sql
-- Step 1: Archive logs older than 12 months
BEGIN TRANSACTION;

INSERT INTO audit.audit_log_archive
SELECT * FROM audit.audit_log_current
WHERE created_at < (CURRENT_DATE - INTERVAL '1 year')
ON CONFLICT (audit_id) DO NOTHING;

-- Step 2: Delete archived records from current
DELETE FROM audit.audit_log_current
WHERE created_at < (CURRENT_DATE - INTERVAL '1 year');

-- Step 3: Maintenance
VACUUM ANALYZE audit.audit_log_current;
VACUUM ANALYZE audit.audit_log_archive;

COMMIT;

-- Verify archive operation
SELECT
  COUNT(*) AS current_count,
  (SELECT COUNT(*) FROM audit.audit_log_archive) AS archive_count,
  ROUND(
    pg_total_relation_size('audit.audit_log_current') / 1024.0 / 1024.0,
    2
  ) AS current_size_mb,
  ROUND(
    pg_total_relation_size('audit.audit_log_archive') / 1024.0 / 1024.0,
    2
  ) AS archive_size_mb
FROM audit.audit_log_current;
```

### 3.2 Create Next Month Partition

**Run on 25th of month at 00:00 UTC**

```sql
-- Automatically create partition for next month
DO $$
DECLARE
  partition_name TEXT;
  start_date DATE;
  end_date DATE;
  next_month DATE;
BEGIN
  next_month := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month')::DATE;
  partition_name := 'audit_log_' || TO_CHAR(next_month, 'YYYY_MM');
  start_date := next_month;
  end_date := next_month + INTERVAL '1 month';
  
  EXECUTE FORMAT(
    'CREATE TABLE IF NOT EXISTS audit.%I PARTITION OF audit.audit_log_current
     FOR VALUES FROM (%L) TO (%L)',
    partition_name,
    start_date::TEXT,
    end_date::TEXT
  );
  
  RAISE NOTICE 'Created partition % for % to %',
    partition_name, start_date, end_date;
END
$$;

-- Rebuild indexes on new partition
REINDEX INDEX CONCURRENTLY idx_audit_resource;
REINDEX INDEX CONCURRENTLY idx_audit_timestamp;
```

### 3.3 Compliance Report Generation

```sql
-- Generate monthly compliance report
WITH monthly_stats AS (
  SELECT
    DATE_TRUNC('month', timestamp)::DATE AS report_month,
    COUNT(*) AS total_operations,
    COUNT(*) FILTER (WHERE success) AS successful,
    COUNT(*) FILTER (WHERE NOT success) AS failed,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(DISTINCT agent_id) AS unique_agents,
    COUNT(*) FILTER (WHERE operation_type LIKE 'doc_created') AS docs_created,
    COUNT(*) FILTER (WHERE operation_type LIKE 'doc_updated') AS docs_updated,
    COUNT(*) FILTER (WHERE operation_type LIKE 'doc_deleted') AS docs_deleted,
    SUM(COALESCE(data_size_bytes, 0)) / 1024.0 / 1024.0 / 1024.0 AS data_processed_gb
  FROM audit.audit_log_current
  WHERE timestamp >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
    AND timestamp < DATE_TRUNC('month', CURRENT_DATE)
  GROUP BY DATE_TRUNC('month', timestamp)
)
SELECT
  report_month,
  total_operations,
  successful,
  failed,
  ROUND(100.0 * failed / total_operations, 2) AS failure_rate_percent,
  unique_users,
  unique_agents,
  docs_created + docs_updated + docs_deleted AS total_document_changes,
  ROUND(data_processed_gb, 2) AS data_processed_gb
FROM monthly_stats;
```

## 4. Troubleshooting

### 4.1 Audit Log Missing for Expected Operations

```sql
-- Symptom: Audit entries not appearing for database changes
-- Diagnosis:

-- 1. Check trigger status
SELECT trigger_name, tgenabled
FROM pg_trigger
WHERE tgrelid = 'documents'::regclass;

-- 2. Verify trigger function
SELECT prosrc FROM pg_proc
WHERE proname = 'audit_trigger_function';

-- 3. Check application context
-- Run this in app code:
-- SELECT set_config('app.user_id', 'test_user', false);
-- Then perform operation and check:
SELECT * FROM audit.audit_log_current
WHERE user_id = 'test_user'
ORDER BY timestamp DESC
LIMIT 1;

-- 4. If triggers were disabled:
ALTER TABLE documents ENABLE TRIGGER ALL;
```

### 4.2 Audit Table Growing Too Quickly

```sql
-- Symptom: Disk usage increasing rapidly
-- Investigation:

-- Check volume by operation type
SELECT
  operation_type,
  COUNT(*) AS count,
  ROUND(COUNT(*) / 86400.0, 2) AS per_second,
  SUM(COALESCE(data_size_bytes, 0)) / 1024.0 / 1024.0 AS size_mb
FROM audit.audit_log_current
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY operation_type
ORDER BY count DESC;

-- Check if sampled operations are being logged at 100%
SELECT
  CASE
    WHEN operation_type LIKE '%_read' THEN 'Should be 1%'
    WHEN operation_type LIKE '%_accessed' THEN 'Should be 1%'
    ELSE '100%'
  END AS expected_sampling,
  operation_type,
  COUNT(*) / 3600.0 AS per_second
FROM audit.audit_log_current
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY operation_type
ORDER BY per_second DESC;
```

### 4.3 Query Performance Degradation

```sql
-- Symptom: Audit queries running slowly
-- Resolution:

-- 1. Analyze all indexes
ANALYZE audit.audit_log_current;

-- 2. Check index bloat
SELECT
  schemaname,
  tablename,
  indexname,
  ROUND(100.0 * (pg_relation_size(idx) - pg_relation_size(idx, 'main')) / pg_relation_size(idx), 2) AS bloat_percent
FROM (
  SELECT
    schemaname,
    tablename,
    indexname,
    idx
  FROM pg_stat_user_indexes
  WHERE schemaname = 'audit'
) t
WHERE bloat_percent > 20
ORDER BY bloat_percent DESC;

-- 3. Reindex if needed
REINDEX INDEX CONCURRENTLY idx_audit_resource;
REINDEX INDEX CONCURRENTLY idx_audit_timestamp;

-- 4. Check slow query log
SELECT
  query,
  calls,
  ROUND(total_time::NUMERIC, 2) AS total_ms,
  ROUND((total_time / calls)::NUMERIC, 2) AS avg_ms
FROM pg_stat_statements
WHERE query LIKE '%audit%'
ORDER BY total_time DESC
LIMIT 10;
```

## 5. Disaster Recovery

### 5.1 Restore from Archive

```sql
-- If main table corrupted, recover from archive
BEGIN TRANSACTION;

-- 1. Backup current (corrupted) table
CREATE TABLE audit.audit_log_current_corrupted AS
SELECT * FROM audit.audit_log_current;

-- 2. Restore from archive
DELETE FROM audit.audit_log_current;
INSERT INTO audit.audit_log_current
SELECT * FROM audit.audit_log_archive
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month');

-- 3. Verify
SELECT COUNT(*) AS restored_count FROM audit.audit_log_current;

COMMIT;
```

### 5.2 Rebuild Indexes

```sql
-- If indexes become corrupted
BEGIN TRANSACTION;

-- Disable triggers temporarily to avoid new writes
ALTER TABLE documents DISABLE TRIGGER ALL;

-- Drop and recreate all indexes
DROP INDEX IF EXISTS audit.idx_audit_resource;
DROP INDEX IF EXISTS audit.idx_audit_user;
DROP INDEX IF EXISTS audit.idx_audit_operation;
DROP INDEX IF EXISTS audit.idx_audit_timestamp;
DROP INDEX IF EXISTS audit.idx_audit_trace;
DROP INDEX IF EXISTS audit.idx_audit_success;

-- Recreate indexes
CREATE INDEX idx_audit_resource ON audit.audit_log_current (resource_type, resource_id, timestamp DESC);
CREATE INDEX idx_audit_user ON audit.audit_log_current (user_id, timestamp DESC) WHERE user_id IS NOT NULL;
CREATE INDEX idx_audit_operation ON audit.audit_log_current (operation_type, timestamp DESC);
CREATE INDEX idx_audit_timestamp ON audit.audit_log_current (timestamp DESC);
CREATE INDEX idx_audit_trace ON audit.audit_log_current (trace_id) WHERE trace_id IS NOT NULL;
CREATE INDEX idx_audit_success ON audit.audit_log_current (success, timestamp DESC) WHERE NOT success;

-- Re-enable triggers
ALTER TABLE documents ENABLE TRIGGER ALL;

COMMIT;
```

## 6. Enabling/Disabling Logging

### 6.1 Temporarily Disable Audit Logging

**Use only for maintenance operations**

```sql
-- Disable all audit triggers
ALTER TABLE documents DISABLE TRIGGER trg_audit_documents;
ALTER TABLE chunks DISABLE TRIGGER trg_audit_chunks;
ALTER TABLE embeddings DISABLE TRIGGER trg_audit_embeddings;

-- Perform maintenance...

-- Re-enable
ALTER TABLE documents ENABLE TRIGGER trg_audit_documents;
ALTER TABLE chunks ENABLE TRIGGER trg_audit_chunks;
ALTER TABLE embeddings ENABLE TRIGGER trg_audit_embeddings;
```

### 6.2 Selective Logging Control

```sql
-- Log selectively by operation type
-- Use application context to control logging level

-- In application code:
-- SET app.audit_level = 'full'     -- Log everything
-- SET app.audit_level = 'minimal'  -- Log only important ops
-- SET app.audit_level = 'none'     -- Disable logging

-- In trigger:
CREATE OR REPLACE FUNCTION audit.audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
  CASE current_setting('app.audit_level', true)
    WHEN 'none' THEN RETURN COALESCE(NEW, OLD);
    WHEN 'minimal' THEN
      IF TG_OP = 'DELETE' THEN
        -- Always log deletes
      ELSIF TG_OP = 'UPDATE' AND (NEW).importance_level > 5 THEN
        -- Log important updates
      ELSIF TG_OP = 'INSERT' THEN
        -- Always log creates
      ELSE
        RETURN COALESCE(NEW, OLD);
      END IF;
    ELSE
      -- Full logging (default)
  END CASE;
  
  -- Insert audit log...
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

## 7. Performance Tuning

### 7.1 Optimize Audit Index Usage

```sql
-- Check index usage statistics
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan AS scans,
  idx_tup_read AS tuples_read,
  idx_tup_fetch AS tuples_fetched,
  CASE WHEN idx_scan = 0 THEN 'UNUSED' ELSE 'ACTIVE' END AS status
FROM pg_stat_user_indexes
WHERE schemaname = 'audit'
ORDER BY idx_scan DESC;

-- Identify unused indexes (consider dropping)
SELECT indexname
FROM pg_stat_user_indexes
WHERE schemaname = 'audit'
  AND idx_scan = 0
  AND indexname NOT LIKE '%_pk'
ORDER BY idx_scan DESC;
```

### 7.2 Monitor Partition Size

```sql
-- Check partition balance
SELECT
  schemaname,
  tablename,
  ROUND(pg_total_relation_size(schemaname||'.'||tablename) / 1024.0 / 1024.0, 2) AS size_mb,
  n_live_tup AS row_count,
  ROUND(n_live_tup / pg_total_relation_size(schemaname||'.'||tablename), 6) AS rows_per_byte
FROM pg_stat_user_tables
WHERE schemaname = 'audit'
  AND tablename LIKE 'audit_log_%'
ORDER BY n_live_tup DESC;
```

## 8. Automation Scripts

### 8.1 Cron Schedule (pg_cron)

```sql
-- Install extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule daily health check
SELECT cron.schedule(
  'audit_daily_health_check',
  '0 8 * * *',  -- 08:00 UTC daily
  $$
    -- Health check queries here
  $$
);

-- Schedule monthly archival
SELECT cron.schedule(
  'audit_monthly_archive',
  '0 2 1 * *',  -- 02:00 UTC on 1st
  'CALL audit.archive_old_logs(12)'
);

-- Schedule partition creation
SELECT cron.schedule(
  'audit_create_next_partition',
  '0 0 25 * *',  -- 00:00 UTC on 25th
  'CALL audit.create_next_partition()'
);
```

## 9. Runbooks

### 9.1 Emergency: Audit Table Full

**Disk space exhausted**

```bash
#!/bin/bash
# Emergency procedures

echo "Step 1: Archive immediately"
psql -U postgres -d xnai_knowledge -c "CALL audit.archive_old_logs(6);"

echo "Step 2: Check space"
psql -U postgres -d xnai_knowledge -c "
  SELECT pg_database.datname, pg_size_pretty(pg_database_size(datname))
  FROM pg_database
  WHERE datname = 'xnai_knowledge';
"

echo "Step 3: If still full, move to archive table"
psql -U postgres -d xnai_knowledge -c "CALL audit.archive_old_logs(1);"

echo "Step 4: Expand storage and reindex"
# Expand disk as needed, then:
# REINDEX audit.audit_log_current;
```

## Reference

- **Schema**: `02-audit-schema-implementation.sql`
- **Queries**: `03-audit-queries.sql`
- **Strategy**: `01-audit-logging-strategy.md`
