"""Create materialized views for performance optimization

Revision ID: 003
Revises: 002
Create Date: 2026-02-24 00:00:00.000000

This migration creates materialized views for query optimization:
- Document statistics by domain
- Embedding coverage statistics
- Agent learning progress tracking
"""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """Create materialized views"""
    
    # Document statistics by domain
    op.execute("""
    CREATE MATERIALIZED VIEW document_stats_by_domain AS
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
    """)
    
    # Create index on materialized view
    op.execute("""
    CREATE INDEX idx_doc_stats_domain_id ON document_stats_by_domain(domain_id);
    """)
    
    # Embedding coverage statistics
    op.execute("""
    CREATE MATERIALIZED VIEW embedding_coverage AS
    SELECT 
        e.embedding_type,
        COUNT(DISTINCT e.chunk_id) as embedded_chunks,
        COUNT(DISTINCT c.doc_id) as documents_with_embeddings,
        AVG(e.vector_dims)::INTEGER as avg_vector_dims,
        MAX(e.indexed_at) as latest_indexing
    FROM embeddings e
    JOIN chunks c ON c.id = e.chunk_id
    GROUP BY e.embedding_type;
    """)
    
    # Create index on embedding coverage view
    op.execute("""
    CREATE INDEX idx_embedding_coverage_type ON embedding_coverage(embedding_type);
    """)
    
    # Agent learning progress
    op.execute("""
    CREATE MATERIALIZED VIEW agent_learning_progress AS
    SELECT 
        ap.id,
        ap.agent_name,
        ap.persona_type,
        ap.interaction_count,
        ap.expertise_level,
        COUNT(DISTINCT ael.id) as evolution_events,
        MAX(ael.timestamp) as last_learning_event
    FROM agent_personas ap
    LEFT JOIN agent_evolution_log ael ON ael.agent_id = ap.id
    GROUP BY ap.id, ap.agent_name, ap.persona_type, ap.interaction_count, ap.expertise_level;
    """)
    
    # Create index on agent learning progress view
    op.execute("""
    CREATE INDEX idx_agent_learning_agent_id ON agent_learning_progress(id);
    """)
    
    # Create stored procedure to refresh materialized views
    op.execute("""
    CREATE OR REPLACE FUNCTION refresh_materialized_views() RETURNS void AS $$
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY document_stats_by_domain;
        REFRESH MATERIALIZED VIEW CONCURRENTLY embedding_coverage;
        REFRESH MATERIALIZED VIEW CONCURRENTLY agent_learning_progress;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Add table comments
    op.execute("COMMENT ON MATERIALIZED VIEW document_stats_by_domain IS 'Aggregated document and chunk statistics per knowledge domain'")
    op.execute("COMMENT ON MATERIALIZED VIEW embedding_coverage IS 'Coverage of embeddings across documents and embedding types'")
    op.execute("COMMENT ON MATERIALIZED VIEW agent_learning_progress IS 'Agent learning metrics and evolution tracking'")


def downgrade() -> None:
    """Drop materialized views and related objects"""
    
    # Drop function first
    op.execute("DROP FUNCTION IF EXISTS refresh_materialized_views()")
    
    # Drop materialized views
    op.execute("DROP MATERIALIZED VIEW IF EXISTS agent_learning_progress CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS embedding_coverage CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS document_stats_by_domain CASCADE")
