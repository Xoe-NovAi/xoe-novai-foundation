-- ============================================================================
-- Audit Logging Schema Implementation
-- ============================================================================
-- Purpose: Complete PostgreSQL schema for audit logging of knowledge operations
-- Supports: 10K+ ops/day, <5% overhead, 1-year hot storage + 7-year archive
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- ============================================================================
-- 1. SCHEMA AND ROLES
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS audit;

-- Read-only role for compliance reviews
CREATE ROLE audit_reader NOLOGIN;
GRANT USAGE ON SCHEMA audit TO audit_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO audit_reader;

-- Admin role for maintenance
CREATE ROLE audit_admin NOLOGIN;
GRANT ALL PRIVILEGES ON SCHEMA audit TO audit_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO audit_admin;

-- ============================================================================
-- 2. CURRENT AUDIT LOG (HOT STORAGE)
-- ============================================================================

-- Main table with range partitioning by month
CREATE TABLE IF NOT EXISTS audit.audit_log_current (
  audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
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

-- Create initial partition for current month
DO $$
DECLARE
  partition_name TEXT;
  start_date TEXT;
  end_date TEXT;
BEGIN
  partition_name := 'audit_log_' || TO_CHAR(CURRENT_DATE, 'YYYY_MM');
  start_date := TO_CHAR(DATE_TRUNC('month', CURRENT_DATE), 'YYYY-MM-DD');
  end_date := TO_CHAR(DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month', 'YYYY-MM-DD');
  
  EXECUTE FORMAT(
    'CREATE TABLE IF NOT EXISTS audit.%I PARTITION OF audit.audit_log_current
     FOR VALUES FROM (%L) TO (%L)',
    partition_name, start_date, end_date
  );
END
$$;

-- ============================================================================
-- 3. ARCHIVE LOG (COLD STORAGE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit.audit_log_archive (
  audit_id UUID PRIMARY KEY,
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
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  archived_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- ============================================================================
-- 4. INDEXES
-- ============================================================================

-- Query by resource
CREATE INDEX IF NOT EXISTS idx_audit_resource 
ON audit.audit_log_current (resource_type, resource_id, timestamp DESC);

-- Query by user
CREATE INDEX IF NOT EXISTS idx_audit_user 
ON audit.audit_log_current (user_id, timestamp DESC) 
WHERE user_id IS NOT NULL;

-- Query by agent
CREATE INDEX IF NOT EXISTS idx_audit_agent 
ON audit.audit_log_current (agent_id, timestamp DESC) 
WHERE agent_id IS NOT NULL;

-- Query by operation type
CREATE INDEX IF NOT EXISTS idx_audit_operation 
ON audit.audit_log_current (operation_type, timestamp DESC);

-- Time range queries
CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
ON audit.audit_log_current (timestamp DESC);

-- Distributed tracing
CREATE INDEX IF NOT EXISTS idx_audit_trace 
ON audit.audit_log_current (trace_id) 
WHERE trace_id IS NOT NULL;

-- Error tracking
CREATE INDEX IF NOT EXISTS idx_audit_success 
ON audit.audit_log_current (success, timestamp DESC) 
WHERE NOT success;

-- JSONB metadata search
CREATE INDEX IF NOT EXISTS idx_audit_metadata_gin 
ON audit.audit_log_current USING GIN (metadata);

-- Same indexes on archive
CREATE INDEX IF NOT EXISTS idx_archive_resource 
ON audit.audit_log_archive (resource_type, resource_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_archive_user 
ON audit.audit_log_archive (user_id, timestamp DESC) 
WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_archive_timestamp 
ON audit.audit_log_archive (timestamp DESC);

-- ============================================================================
-- 5. HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate field changes (for UPDATE operations)
CREATE OR REPLACE FUNCTION audit.calculate_changes(
  old_record RECORD,
  new_record RECORD
) RETURNS JSONB AS $$
DECLARE
  result JSONB := '{}'::JSONB;
  old_json JSONB;
  new_json JSONB;
  key TEXT;
BEGIN
  old_json := row_to_json(old_record);
  new_json := row_to_json(new_record);
  
  FOR key IN SELECT jsonb_object_keys(new_json)
  LOOP
    IF (old_json ->> key) IS DISTINCT FROM (new_json ->> key) THEN
      result := result || jsonb_build_object(
        key,
        jsonb_build_object(
          'old', old_json ->> key,
          'new', new_json ->> key
        )
      );
    END IF;
  END LOOP;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to get current user/agent context
CREATE OR REPLACE FUNCTION audit.get_current_context()
RETURNS TABLE (user_id VARCHAR, agent_id VARCHAR, trace_id UUID, span_id UUID) AS $$
BEGIN
  RETURN QUERY SELECT
    COALESCE(current_setting('app.user_id', true), NULL)::VARCHAR,
    COALESCE(current_setting('app.agent_id', true), NULL)::VARCHAR,
    COALESCE(current_setting('app.trace_id', true)::UUID, NULL),
    COALESCE(current_setting('app.span_id', true)::UUID, NULL);
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 6. AUDIT LOG INSERTION FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION audit.insert_audit_log(
  operation_type VARCHAR(32),
  resource_type VARCHAR(32),
  resource_id UUID,
  before_state JSONB DEFAULT NULL,
  after_state JSONB DEFAULT NULL,
  metadata JSONB DEFAULT NULL,
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT DEFAULT NULL,
  execution_time_ms INTEGER DEFAULT 0,
  data_size_bytes INTEGER DEFAULT 0
) RETURNS UUID AS $$
DECLARE
  audit_id UUID;
  ctx RECORD;
BEGIN
  SELECT * INTO ctx FROM audit.get_current_context();
  
  audit_id := gen_random_uuid();
  
  INSERT INTO audit.audit_log_current (
    audit_id, timestamp, operation_type, resource_type, resource_id,
    user_id, agent_id, before_state, after_state,
    changes, metadata, trace_id, span_id,
    success, error_message, execution_time_ms, data_size_bytes,
    created_at
  ) VALUES (
    audit_id, CURRENT_TIMESTAMP, operation_type, resource_type, resource_id,
    ctx.user_id, ctx.agent_id, before_state, after_state,
    CASE
      WHEN before_state IS NOT NULL AND after_state IS NOT NULL
      THEN audit.calculate_changes(to_record(before_state), to_record(after_state))
      ELSE NULL
    END,
    metadata, ctx.trace_id, ctx.span_id,
    success, error_message, execution_time_ms, data_size_bytes,
    CURRENT_TIMESTAMP
  );
  
  RETURN audit_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. AUDIT TRIGGERS
-- ============================================================================

-- Generic audit trigger function for INSERT/UPDATE/DELETE
CREATE OR REPLACE FUNCTION audit.audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
  operation_type VARCHAR(32);
  before_json JSONB;
  after_json JSONB;
  ctx RECORD;
BEGIN
  SELECT * INTO ctx FROM audit.get_current_context();
  
  operation_type := CASE
    WHEN TG_OP = 'INSERT' THEN 'created'
    WHEN TG_OP = 'UPDATE' THEN 'updated'
    WHEN TG_OP = 'DELETE' THEN 'deleted'
  END;
  
  before_json := CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END;
  after_json := CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END;
  
  INSERT INTO audit.audit_log_current (
    audit_id, timestamp, operation_type, resource_type, resource_id,
    user_id, agent_id, before_state, after_state, changes,
    trace_id, span_id, success, created_at
  ) VALUES (
    gen_random_uuid(), CURRENT_TIMESTAMP,
    TG_ARGV[0] || '_' || operation_type,  -- e.g., 'document_created'
    TG_ARGV[0],                            -- resource type from arg
    COALESCE(NEW.id, OLD.id),
    ctx.user_id, ctx.agent_id,
    before_json, after_json,
    CASE
      WHEN TG_OP = 'UPDATE' AND before_json IS NOT NULL
      THEN audit.calculate_changes(OLD, NEW)
      ELSE NULL
    END,
    ctx.trace_id, ctx.span_id,
    TRUE, CURRENT_TIMESTAMP
  );
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Example: Create trigger for documents table
-- Uncomment once documents table exists
-- CREATE TRIGGER trg_audit_documents
-- AFTER INSERT OR UPDATE OR DELETE ON documents
-- FOR EACH ROW
-- EXECUTE FUNCTION audit.audit_trigger_function('document');

-- ============================================================================
-- 8. SAMPLING FUNCTION FOR HIGH-VOLUME OPERATIONS
-- ============================================================================

-- Sampled audit logging (e.g., 1% of reads)
CREATE OR REPLACE FUNCTION audit.should_log_sampled(sampling_rate FLOAT8 DEFAULT 0.01)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN random() < sampling_rate;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 9. ARCHIVAL FUNCTIONS
-- ============================================================================

-- Archive logs older than X months
CREATE OR REPLACE PROCEDURE audit.archive_old_logs(
  months_to_keep INTEGER DEFAULT 12
) LANGUAGE plpgsql AS $$
DECLARE
  cutoff_date TIMESTAMPTZ;
  archive_month TEXT;
  partition_name TEXT;
BEGIN
  cutoff_date := CURRENT_TIMESTAMP - MAKE_INTERVAL(months => months_to_keep);
  
  -- Insert old records into archive
  INSERT INTO audit.audit_log_archive
  SELECT * FROM audit.audit_log_current
  WHERE created_at < cutoff_date
  ON CONFLICT (audit_id) DO NOTHING;
  
  -- Delete from current (cascades via FK if set up)
  DELETE FROM audit.audit_log_current WHERE created_at < cutoff_date;
  
  -- Vacuum and analyze
  VACUUM ANALYZE audit.audit_log_current;
  VACUUM ANALYZE audit.audit_log_archive;
  
  RAISE NOTICE 'Archived logs before %', cutoff_date;
END;
$$;

-- Create new monthly partition
CREATE OR REPLACE PROCEDURE audit.create_next_partition()
LANGUAGE plpgsql AS $$
DECLARE
  partition_name TEXT;
  start_date DATE;
  end_date DATE;
BEGIN
  start_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month')::DATE;
  end_date := start_date + INTERVAL '1 month';
  partition_name := 'audit_log_' || TO_CHAR(start_date, 'YYYY_MM');
  
  EXECUTE FORMAT(
    'CREATE TABLE IF NOT EXISTS audit.%I PARTITION OF audit.audit_log_current
     FOR VALUES FROM (%L) TO (%L)',
    partition_name,
    start_date::TEXT,
    end_date::TEXT
  );
  
  RAISE NOTICE 'Created partition %', partition_name;
END;
$$;

-- ============================================================================
-- 10. QUERY FUNCTIONS
-- ============================================================================

-- Find all changes to a specific document
CREATE OR REPLACE FUNCTION audit.get_document_changes(
  doc_id UUID
) RETURNS TABLE (
  audit_id UUID,
  timestamp TIMESTAMPTZ,
  operation_type VARCHAR,
  user_id VARCHAR,
  agent_id VARCHAR,
  changes JSONB,
  success BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    al.audit_id,
    al.timestamp,
    al.operation_type,
    al.user_id,
    al.agent_id,
    al.changes,
    al.success
  FROM audit.audit_log_current al
  WHERE al.resource_type = 'document'
    AND al.resource_id = doc_id
  ORDER BY al.timestamp DESC;
END;
$$ LANGUAGE plpgsql;

-- Find all operations by a user in a time range
CREATE OR REPLACE FUNCTION audit.get_user_activity(
  user_id_param VARCHAR(255),
  start_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP - INTERVAL '30 days',
  end_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) RETURNS TABLE (
  audit_id UUID,
  timestamp TIMESTAMPTZ,
  operation_type VARCHAR,
  resource_type VARCHAR,
  resource_id UUID,
  success BOOLEAN,
  execution_time_ms INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    al.audit_id,
    al.timestamp,
    al.operation_type,
    al.resource_type,
    al.resource_id,
    al.success,
    al.execution_time_ms
  FROM audit.audit_log_current al
  WHERE al.user_id = user_id_param
    AND al.timestamp >= start_date
    AND al.timestamp < end_date
  ORDER BY al.timestamp DESC;
END;
$$ LANGUAGE plpgsql;

-- Get error statistics by operation type
CREATE OR REPLACE FUNCTION audit.get_error_stats(
  start_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP - INTERVAL '7 days'
) RETURNS TABLE (
  operation_type VARCHAR,
  error_count BIGINT,
  total_count BIGINT,
  error_rate NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    al.operation_type,
    COUNT(*) FILTER (WHERE NOT al.success) AS error_count,
    COUNT(*) AS total_count,
    ROUND(
      100.0 * COUNT(*) FILTER (WHERE NOT al.success) / COUNT(*),
      2
    ) AS error_rate
  FROM audit.audit_log_current al
  WHERE al.timestamp >= start_date
  GROUP BY al.operation_type
  ORDER BY error_rate DESC;
END;
$$ LANGUAGE plpgsql;

-- Get performance metrics by operation type
CREATE OR REPLACE FUNCTION audit.get_performance_metrics(
  start_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP - INTERVAL '7 days'
) RETURNS TABLE (
  operation_type VARCHAR,
  avg_time_ms NUMERIC,
  max_time_ms INTEGER,
  min_time_ms INTEGER,
  p95_time_ms NUMERIC,
  p99_time_ms NUMERIC,
  operation_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    al.operation_type,
    ROUND(AVG(COALESCE(al.execution_time_ms, 0))::NUMERIC, 2),
    MAX(COALESCE(al.execution_time_ms, 0)),
    MIN(COALESCE(al.execution_time_ms, 0)),
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY al.execution_time_ms)::NUMERIC, 2),
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY al.execution_time_ms)::NUMERIC, 2),
    COUNT(*)
  FROM audit.audit_log_current al
  WHERE al.timestamp >= start_date
  GROUP BY al.operation_type
  ORDER BY avg_time_ms DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 11. RETENTION AND COMPLIANCE
-- ============================================================================

-- Create checksums for integrity verification
CREATE TABLE IF NOT EXISTS audit.audit_log_checksums (
  partition_id VARCHAR(32) PRIMARY KEY,
  record_count BIGINT,
  checksum_hash BYTEA,
  previous_hash BYTEA,
  computed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  verified_at TIMESTAMPTZ
);

-- Compute partition checksum
CREATE OR REPLACE FUNCTION audit.compute_partition_checksum(
  partition_name TEXT
) RETURNS BYTEA AS $$
DECLARE
  checksum BYTEA;
BEGIN
  EXECUTE FORMAT(
    'SELECT digest(
      string_agg(audit_id::TEXT, ''|'' ORDER BY audit_id),
      ''sha256''
    ) FROM audit.%I',
    partition_name
  ) INTO checksum;
  
  RETURN checksum;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 12. GRANT PERMISSIONS
-- ============================================================================

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT SELECT ON TABLES TO audit_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT ALL ON TABLES TO audit_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT ALL ON FUNCTIONS TO audit_admin;

-- ============================================================================
-- 13. CREATE SCHEDULED JOBS (if pg_cron extension available)
-- ============================================================================

-- Uncomment if pg_cron is installed:
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- SELECT cron.schedule(
--   'archive_audit_logs_monthly',
--   '0 2 1 * *',  -- 02:00 UTC on 1st of month
--   'CALL audit.archive_old_logs(12)'
-- );

-- SELECT cron.schedule(
--   'create_next_audit_partition',
--   '0 0 25 * *',  -- 00:00 UTC on 25th of month
--   'CALL audit.create_next_partition()'
-- );

-- ============================================================================
-- 14. SAMPLE DATA AND INITIALIZATION
-- ============================================================================

-- Set application context for testing
-- SELECT set_config('app.user_id', 'test_user_123', false);
-- SELECT set_config('app.agent_id', 'agent_456', false);
-- SELECT set_config('app.trace_id', gen_random_uuid()::TEXT, false);

-- Example: Insert a test audit log
-- SELECT audit.insert_audit_log(
--   'doc_created',
--   'document',
--   gen_random_uuid(),
--   NULL,
--   '{"title": "New Doc", "status": "draft"}',
--   '{"source": "api", "version": "1.0"}',
--   TRUE,
--   NULL,
--   15,
--   2048
-- );

-- ============================================================================
-- 15. VIEWS FOR COMMON QUERIES
-- ============================================================================

CREATE OR REPLACE VIEW audit.v_recent_operations AS
SELECT
  audit_id,
  timestamp,
  operation_type,
  resource_type,
  resource_id,
  user_id,
  agent_id,
  success,
  execution_time_ms,
  error_message
FROM audit.audit_log_current
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY timestamp DESC;

CREATE OR REPLACE VIEW audit.v_failed_operations AS
SELECT
  audit_id,
  timestamp,
  operation_type,
  resource_type,
  resource_id,
  user_id,
  agent_id,
  error_message,
  execution_time_ms
FROM audit.audit_log_current
WHERE NOT success
ORDER BY timestamp DESC;

CREATE OR REPLACE VIEW audit.v_high_latency_operations AS
SELECT
  audit_id,
  timestamp,
  operation_type,
  resource_type,
  execution_time_ms,
  user_id,
  agent_id
FROM audit.audit_log_current
WHERE execution_time_ms > 1000
ORDER BY execution_time_ms DESC;

COMMIT;
