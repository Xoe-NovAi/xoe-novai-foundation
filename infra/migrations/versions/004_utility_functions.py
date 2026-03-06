"""Add utility functions and procedures

Revision ID: 004
Revises: 003
Create Date: 2026-02-24 00:00:00.000000

This migration adds utility functions for maintenance and operations:
- Cache cleanup procedures
- Schema information functions
- Health check procedures
"""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """Create utility functions"""
    
    # Stored procedure to clean expired query cache entries
    op.execute("""
    CREATE OR REPLACE FUNCTION cleanup_expired_cache() RETURNS void AS $$
    DECLARE
        deleted_count integer;
    BEGIN
        DELETE FROM query_cache WHERE expires_at < CURRENT_TIMESTAMP;
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE 'Deleted % expired cache entries', deleted_count;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Function to get schema version
    op.execute("""
    CREATE OR REPLACE FUNCTION get_schema_version() RETURNS TABLE(
        version_num varchar,
        revision_id varchar
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT alembic_version.version_num::varchar, alembic_version.version_num::varchar
        FROM alembic_version
        ORDER BY alembic_version.version_num DESC
        LIMIT 1;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Function to get database health statistics
    op.execute("""
    CREATE OR REPLACE FUNCTION get_db_health() RETURNS TABLE(
        table_name varchar,
        row_count bigint,
        size_bytes bigint,
        last_vacuum timestamp,
        last_analyze timestamp
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            schemaname::varchar || '.' || tablename::varchar,
            n_live_tup::bigint,
            pg_total_relation_size(schemaname||'.'||tablename)::bigint,
            last_vacuum,
            last_analyze
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY n_live_tup DESC;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Function to get cache statistics
    op.execute("""
    CREATE OR REPLACE FUNCTION get_cache_stats() RETURNS TABLE(
        total_entries bigint,
        expired_entries bigint,
        active_entries bigint,
        total_hits bigint,
        avg_hit_count numeric
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            COUNT(*)::bigint,
            COUNT(CASE WHEN expires_at < CURRENT_TIMESTAMP THEN 1 END)::bigint,
            COUNT(CASE WHEN expires_at >= CURRENT_TIMESTAMP THEN 1 END)::bigint,
            COALESCE(SUM(hit_count), 0)::bigint,
            COALESCE(AVG(hit_count), 0)::numeric
        FROM query_cache;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Function to get document coverage statistics
    op.execute("""
    CREATE OR REPLACE FUNCTION get_document_coverage() RETURNS TABLE(
        total_documents bigint,
        total_chunks bigint,
        total_embeddings bigint,
        embedded_coverage_percent numeric,
        avg_chunks_per_doc numeric,
        avg_tokens_per_chunk numeric
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            COUNT(DISTINCT d.id)::bigint,
            COUNT(DISTINCT c.id)::bigint,
            COUNT(DISTINCT e.id)::bigint,
            ROUND(100.0 * COUNT(DISTINCT e.chunk_id) / NULLIF(COUNT(DISTINCT c.id), 0), 2)::numeric,
            ROUND(AVG(d.chunk_count), 2)::numeric,
            ROUND(AVG(c.token_count), 2)::numeric
        FROM documents d
        LEFT JOIN chunks c ON c.doc_id = d.id
        LEFT JOIN embeddings e ON e.chunk_id = c.id
        WHERE d.status = 'active';
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Function to vacuum and analyze all tables
    op.execute("""
    CREATE OR REPLACE FUNCTION vacuum_analyze_all() RETURNS void AS $$
    BEGIN
        VACUUM FULL ANALYZE;
        RAISE NOTICE 'Completed vacuum and analyze';
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Add comments
    op.execute("COMMENT ON FUNCTION cleanup_expired_cache() IS 'Remove expired query cache entries'")
    op.execute("COMMENT ON FUNCTION get_schema_version() IS 'Get current database schema version'")
    op.execute("COMMENT ON FUNCTION get_db_health() IS 'Get health statistics for all tables'")
    op.execute("COMMENT ON FUNCTION get_cache_stats() IS 'Get query cache statistics'")
    op.execute("COMMENT ON FUNCTION get_document_coverage() IS 'Get document and embedding coverage statistics'")
    op.execute("COMMENT ON FUNCTION vacuum_analyze_all() IS 'Run full vacuum and analyze on all tables'")


def downgrade() -> None:
    """Drop utility functions"""
    
    op.execute("DROP FUNCTION IF EXISTS vacuum_analyze_all()")
    op.execute("DROP FUNCTION IF EXISTS get_document_coverage()")
    op.execute("DROP FUNCTION IF EXISTS get_cache_stats()")
    op.execute("DROP FUNCTION IF EXISTS get_db_health()")
    op.execute("DROP FUNCTION IF EXISTS get_schema_version()")
    op.execute("DROP FUNCTION IF EXISTS cleanup_expired_cache()")
