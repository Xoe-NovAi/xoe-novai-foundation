-- ============================================================================
-- Audit Logging Query Library
-- ============================================================================
-- Purpose: Pre-built queries for audit log analysis and compliance reporting
-- ============================================================================

-- ============================================================================
-- 1. DOCUMENT CHANGE TRACKING
-- ============================================================================

-- Find all changes to a specific document with full history
SELECT
  al.audit_id,
  al.timestamp,
  al.operation_type,
  al.user_id,
  al.agent_id,
  al.before_state,
  al.after_state,
  al.changes,
  al.success,
  al.error_message
FROM audit.audit_log_current al
WHERE al.resource_type = 'document'
  AND al.resource_id = '00000000-0000-0000-0000-000000000001'  -- Replace with doc_id
ORDER BY al.timestamp DESC;

-- Find who modified a specific field in a document
SELECT
  al.audit_id,
  al.timestamp,
  al.user_id,
  al.agent_id,
  al.changes->'field_name' AS field_changes,
  al.before_state->>'field_name' AS old_value,
  al.after_state->>'field_name' AS new_value
FROM audit.audit_log_current al
WHERE al.resource_type = 'document'
  AND al.resource_id = '00000000-0000-0000-0000-000000000001'
  AND al.changes ? 'field_name'
ORDER BY al.timestamp DESC;

-- Audit trail for specific document version
WITH document_versions AS (
  SELECT
    al.audit_id,
    al.timestamp,
    al.operation_type,
    al.user_id,
    al.after_state,
    ROW_NUMBER() OVER (ORDER BY al.timestamp) AS version
  FROM audit.audit_log_current al
  WHERE al.resource_type = 'document'
    AND al.resource_id = '00000000-0000-0000-0000-000000000001'
    AND al.operation_type IN ('doc_created', 'doc_updated')
)
SELECT * FROM document_versions
WHERE version <= 10  -- Show first 10 versions
ORDER BY timestamp DESC;

-- ============================================================================
-- 2. USER ACTIVITY AND ACCESS PATTERNS
-- ============================================================================

-- Find all operations performed by a user in a time range
SELECT
  al.audit_id,
  al.timestamp,
  al.operation_type,
  al.resource_type,
  al.resource_id,
  al.success,
  al.execution_time_ms,
  al.data_size_bytes
FROM audit.audit_log_current al
WHERE al.user_id = 'user_123'
  AND al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
  AND al.timestamp < CURRENT_TIMESTAMP
ORDER BY al.timestamp DESC;

-- User operation summary (last 7 days)
SELECT
  al.user_id,
  al.operation_type,
  COUNT(*) AS operation_count,
  COUNT(*) FILTER (WHERE al.success) AS successful,
  COUNT(*) FILTER (WHERE NOT al.success) AS failed,
  ROUND(AVG(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2) AS avg_time_ms,
  MAX(COALESCE(al.execution_time_ms, 0)) AS max_time_ms
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
  AND al.user_id IS NOT NULL
GROUP BY al.user_id, al.operation_type
ORDER BY al.user_id, operation_count DESC;

-- Find users with elevated activity (potential anomaly)
SELECT
  al.user_id,
  COUNT(*) AS operation_count,
  COUNT(DISTINCT al.resource_type) AS resource_types_accessed,
  MIN(al.timestamp) AS first_operation,
  MAX(al.timestamp) AS last_operation,
  ROUND(AVG(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2) AS avg_time_ms
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
  AND al.user_id IS NOT NULL
  AND al.success = TRUE
GROUP BY al.user_id
HAVING COUNT(*) > 100  -- Adjust threshold as needed
ORDER BY operation_count DESC;

-- ============================================================================
-- 3. AGENT ACTIVITY TRACKING
-- ============================================================================

-- Find all operations performed by a specific agent
SELECT
  al.audit_id,
  al.timestamp,
  al.operation_type,
  al.resource_type,
  COUNT(*) OVER (
    PARTITION BY al.agent_id, al.operation_type
    ORDER BY al.timestamp
    ROWS BETWEEN 99 PRECEDING AND CURRENT ROW
  ) AS recent_100_count,
  al.success,
  al.execution_time_ms
FROM audit.audit_log_current al
WHERE al.agent_id = 'agent_789'
  AND al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY al.timestamp DESC;

-- Agent performance metrics (last 24 hours)
SELECT
  al.agent_id,
  COUNT(*) AS total_operations,
  COUNT(*) FILTER (WHERE al.success) AS successful,
  COUNT(*) FILTER (WHERE NOT al.success) AS failed,
  ROUND(100.0 * COUNT(*) FILTER (WHERE al.success) / COUNT(*), 2) AS success_rate,
  ROUND(AVG(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2) AS avg_time_ms,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY al.execution_time_ms) AS p95_time_ms,
  MAX(COALESCE(al.execution_time_ms, 0)) AS max_time_ms,
  SUM(COALESCE(al.data_size_bytes, 0)) AS total_data_processed
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
  AND al.agent_id IS NOT NULL
GROUP BY al.agent_id
ORDER BY total_operations DESC;

-- ============================================================================
-- 4. ERROR ANALYSIS AND TROUBLESHOOTING
-- ============================================================================

-- Find recent failures by operation type
SELECT
  al.operation_type,
  COUNT(*) AS failure_count,
  al.error_message,
  MAX(al.timestamp) AS last_error,
  ARRAY_AGG(DISTINCT al.user_id ORDER BY al.user_id) AS affected_users
FROM audit.audit_log_current al
WHERE NOT al.success
  AND al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY al.operation_type, al.error_message
ORDER BY failure_count DESC, last_error DESC;

-- Error rate trending (hourly for last 7 days)
SELECT
  DATE_TRUNC('hour', al.timestamp) AS hour,
  al.operation_type,
  COUNT(*) AS total_count,
  COUNT(*) FILTER (WHERE NOT al.success) AS error_count,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE NOT al.success) / COUNT(*),
    2
  ) AS error_rate_percent
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', al.timestamp), al.operation_type
ORDER BY hour DESC, error_rate_percent DESC;

-- Find operations that exceed performance thresholds
SELECT
  al.audit_id,
  al.timestamp,
  al.operation_type,
  al.resource_type,
  al.execution_time_ms,
  al.user_id,
  al.agent_id,
  al.data_size_bytes,
  ROUND(al.execution_time_ms::NUMERIC / NULLIF(al.data_size_bytes, 0), 4) AS ms_per_byte
FROM audit.audit_log_current al
WHERE al.execution_time_ms > 5000  -- Operations taking >5 seconds
  AND al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY al.execution_time_ms DESC;

-- ============================================================================
-- 5. COMPLIANCE AND AUDIT REPORTS
-- ============================================================================

-- Compliance report: All document modifications in a period
SELECT
  DATE(al.timestamp) AS event_date,
  COUNT(*) AS total_changes,
  COUNT(*) FILTER (WHERE al.operation_type = 'doc_created') AS creates,
  COUNT(*) FILTER (WHERE al.operation_type = 'doc_updated') AS updates,
  COUNT(*) FILTER (WHERE al.operation_type = 'doc_deleted') AS deletes,
  COUNT(DISTINCT al.user_id) AS users_involved,
  COUNT(DISTINCT al.agent_id) AS agents_involved,
  COUNT(*) FILTER (WHERE NOT al.success) AS failed_operations
FROM audit.audit_log_current al
WHERE al.resource_type = 'document'
  AND al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '90 days'
GROUP BY DATE(al.timestamp)
ORDER BY event_date DESC;

-- Find orphaned records (deleted but accessed recently)
SELECT
  al.resource_id,
  al.resource_type,
  COUNT(*) FILTER (WHERE al.operation_type = 'doc_deleted') AS deletion_count,
  COUNT(*) FILTER (WHERE al.operation_type ~ 'accessed|read') AS post_deletion_access,
  MAX(al.timestamp) FILTER (WHERE al.operation_type = 'doc_deleted') AS deleted_at,
  MAX(al.timestamp) FILTER (WHERE al.operation_type ~ 'accessed|read') AS last_accessed
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY al.resource_id, al.resource_type
HAVING COUNT(*) FILTER (WHERE al.operation_type ~ 'accessed|read' AND al.operation_type != 'doc_deleted') > 0
ORDER BY last_accessed DESC;

-- Data retention compliance check
SELECT
  'audit_log_current' AS table_name,
  COUNT(*) AS record_count,
  MIN(al.timestamp) AS oldest_record,
  MAX(al.timestamp) AS newest_record,
  ROUND((EXTRACT(EPOCH FROM (MAX(al.timestamp) - MIN(al.timestamp))) / 86400)::NUMERIC, 1) AS age_days,
  ROUND(
    pg_total_relation_size('audit.audit_log_current') / 1024.0 / 1024.0 / 1024.0,
    2
  ) AS size_gb
FROM audit.audit_log_current al
UNION ALL
SELECT
  'audit_log_archive',
  COUNT(*),
  MIN(al.timestamp),
  MAX(al.timestamp),
  ROUND((EXTRACT(EPOCH FROM (MAX(al.timestamp) - MIN(al.timestamp))) / 86400)::NUMERIC, 1),
  ROUND(
    pg_total_relation_size('audit.audit_log_archive') / 1024.0 / 1024.0 / 1024.0,
    2
  )
FROM audit.audit_log_archive al;

-- ============================================================================
-- 6. PERFORMANCE ANALYSIS
-- ============================================================================

-- Operation latency percentiles (24 hours)
SELECT
  al.operation_type,
  COUNT(*) AS operation_count,
  ROUND(MIN(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2) AS min_ms,
  ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY al.execution_time_ms)::NUMERIC, 2) AS p25_ms,
  ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY al.execution_time_ms)::NUMERIC, 2) AS median_ms,
  ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY al.execution_time_ms)::NUMERIC, 2) AS p75_ms,
  ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY al.execution_time_ms)::NUMERIC, 2) AS p95_ms,
  ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY al.execution_time_ms)::NUMERIC, 2) AS p99_ms,
  ROUND(MAX(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2) AS max_ms
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY al.operation_type
ORDER BY p99_ms DESC;

-- Throughput by hour (operations per second)
SELECT
  DATE_TRUNC('hour', al.timestamp) AS hour,
  COUNT(*) AS operation_count,
  ROUND(COUNT(*) / 3600.0, 2) AS ops_per_second,
  COUNT(*) FILTER (WHERE al.success) AS successful,
  COUNT(*) FILTER (WHERE NOT al.success) AS failed,
  ROUND(AVG(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2) AS avg_time_ms
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', al.timestamp)
ORDER BY hour DESC;

-- Data volume trends (daily for last 30 days)
SELECT
  DATE(al.timestamp) AS day,
  COUNT(*) AS log_entries,
  COUNT(DISTINCT al.resource_id) AS unique_resources,
  COUNT(DISTINCT al.user_id) AS unique_users,
  COUNT(DISTINCT al.agent_id) AS unique_agents,
  SUM(COALESCE(al.data_size_bytes, 0)) / 1024 / 1024 AS data_volume_mb,
  ROUND(AVG(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2) AS avg_time_ms
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY DATE(al.timestamp)
ORDER BY day DESC;

-- ============================================================================
-- 7. DISTRIBUTED TRACING
-- ============================================================================

-- Find all operations in a request trace
SELECT
  al.audit_id,
  al.timestamp,
  al.operation_type,
  al.resource_type,
  al.user_id,
  al.agent_id,
  al.span_id,
  al.success,
  al.execution_time_ms
FROM audit.audit_log_current al
WHERE al.trace_id = '00000000-0000-0000-0000-000000000002'  -- Replace with trace_id
ORDER BY al.timestamp ASC;

-- Calculate total latency for a request trace
WITH trace_operations AS (
  SELECT
    al.trace_id,
    MIN(al.timestamp) AS trace_start,
    MAX(al.timestamp) AS trace_end,
    COUNT(*) AS operation_count,
    SUM(al.execution_time_ms) AS total_operation_time,
    STRING_AGG(DISTINCT al.operation_type, ', ') AS operations
  FROM audit.audit_log_current al
  WHERE al.trace_id IS NOT NULL
    AND al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
  GROUP BY al.trace_id
)
SELECT
  trace_id,
  operation_count,
  ROUND(
    EXTRACT(EPOCH FROM (trace_end - trace_start)) * 1000,
    2
  ) AS total_trace_time_ms,
  total_operation_time AS operation_time_ms,
  ROUND(
    EXTRACT(EPOCH FROM (trace_end - trace_start)) * 1000 - total_operation_time,
    2
  ) AS overhead_ms,
  operations
FROM trace_operations
ORDER BY total_trace_time_ms DESC
LIMIT 100;

-- ============================================================================
-- 8. RESOURCE-SPECIFIC ANALYSIS
-- ============================================================================

-- Most frequently accessed resources (last 7 days, sampled)
SELECT
  al.resource_type,
  al.resource_id,
  COUNT(*) AS access_count,
  COUNT(*) FILTER (WHERE al.operation_type = 'doc_created') AS creates,
  COUNT(*) FILTER (WHERE al.operation_type = 'doc_updated') AS updates,
  COUNT(*) FILTER (WHERE al.operation_type ~ 'accessed|read') AS reads,
  COUNT(*) FILTER (WHERE al.operation_type = 'doc_deleted') AS deletes,
  COUNT(DISTINCT al.user_id) AS unique_users,
  MAX(al.timestamp) AS last_modified
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY al.resource_type, al.resource_id
ORDER BY access_count DESC
LIMIT 100;

-- ============================================================================
-- 9. METADATA ANALYSIS
-- ============================================================================

-- Find audit logs with specific metadata patterns
SELECT
  al.audit_id,
  al.timestamp,
  al.operation_type,
  al.user_id,
  al.metadata,
  al.execution_time_ms
FROM audit.audit_log_current al
WHERE al.metadata @> '{"source": "api"}'  -- Find API operations
  AND al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY al.timestamp DESC;

-- Metadata distribution analysis
SELECT
  al.metadata->>'source' AS source,
  al.metadata->>'version' AS version,
  COUNT(*) AS operation_count,
  ROUND(AVG(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2) AS avg_time_ms
FROM audit.audit_log_current al
WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
  AND al.metadata IS NOT NULL
GROUP BY al.metadata->>'source', al.metadata->>'version'
ORDER BY operation_count DESC;

-- ============================================================================
-- 10. SECURITY AND ANOMALY DETECTION
-- ============================================================================

-- Find failed deletion attempts
SELECT
  al.audit_id,
  al.timestamp,
  al.resource_type,
  al.resource_id,
  al.user_id,
  al.agent_id,
  al.error_message,
  al.before_state
FROM audit.audit_log_current al
WHERE al.operation_type LIKE '%deleted'
  AND NOT al.success
  AND al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY al.timestamp DESC;

-- Find rapid succession operations (potential script attack)
WITH operation_sequence AS (
  SELECT
    al.user_id,
    al.timestamp,
    LAG(al.timestamp) OVER (PARTITION BY al.user_id ORDER BY al.timestamp) AS prev_timestamp,
    EXTRACT(EPOCH FROM al.timestamp - LAG(al.timestamp) OVER (PARTITION BY al.user_id ORDER BY al.timestamp)) AS seconds_since_prev
  FROM audit.audit_log_current al
  WHERE al.timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
)
SELECT
  user_id,
  COUNT(*) AS rapid_operations,
  COUNT(*) FILTER (WHERE seconds_since_prev < 1) AS sub_second_gap_count,
  MIN(seconds_since_prev) AS min_gap_seconds
FROM operation_sequence
WHERE seconds_since_prev IS NOT NULL
  AND seconds_since_prev < 1
GROUP BY user_id
ORDER BY rapid_operations DESC;

-- ============================================================================
-- 11. CLEANUP AND MAINTENANCE QUERIES
-- ============================================================================

-- Find empty/null audit logs
SELECT
  COUNT(*) AS null_audit_ids,
  COUNT(*) FILTER (WHERE resource_id IS NULL) AS null_resource_ids,
  COUNT(*) FILTER (WHERE operation_type IS NULL) AS null_operation_types,
  COUNT(*) FILTER (WHERE user_id IS NULL AND agent_id IS NULL) AS no_actor
FROM audit.audit_log_current;

-- Identify partitions ready for archival
SELECT
  tablename,
  n_live_tup AS row_count,
  ROUND(pg_total_relation_size(schemaname||'.'||tablename) / 1024.0 / 1024.0, 2) AS size_mb,
  (SELECT MAX(created_at) FROM audit.audit_log_current al 
   WHERE al::TEXT LIKE tablename) AS latest_record
FROM pg_stat_user_tables
WHERE schemaname = 'audit'
  AND tablename LIKE 'audit_log_%'
ORDER BY tablename;
