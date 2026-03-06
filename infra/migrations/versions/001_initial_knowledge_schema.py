"""Initial knowledge management schema creation

Revision ID: 001
Revises: 
Create Date: 2026-02-24 00:00:00.000000

This migration creates the initial PostgreSQL schema for the XNAi knowledge
management system, including:
- Knowledge domains (hierarchical taxonomy)
- Documents (core records with metadata)
- Chunks (token-aware document segments)
- Embeddings (vector metadata for external storage)
- Knowledge relations (document relationships)
- Agent personas (autonomous workers)
- Agent evolution logs (learning history)
- Curated collections (specialized document subsets)
- Audit logs (operation history)
- Query cache (performance optimization)
- Materialized views and triggers
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    """Create initial schema"""
    
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    
    # 1. KNOWLEDGE_DOMAINS Table
    op.create_table(
        'knowledge_domains',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint('length(trim(name)) > 0', name='domain_name_not_empty'),
        sa.ForeignKeyConstraint(['parent_id'], ['knowledge_domains.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='_knowledge_domains_name_unique')
    )
    
    op.create_index('idx_knowledge_domains_parent_id', 'knowledge_domains', ['parent_id'])
    op.create_index('idx_knowledge_domains_name', 'knowledge_domains', ['name'])
    
    # 2. DOCUMENTS Table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('title', sa.VARCHAR(500), nullable=False),
        sa.Column('path', sa.VARCHAR(1024), nullable=True),
        sa.Column('source', sa.VARCHAR(255), nullable=False),
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('status', sa.VARCHAR(50), nullable=False, server_default='active'),
        sa.Column('content_hash', sa.VARCHAR(64), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mime_type', sa.VARCHAR(100), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.CheckConstraint("status IN ('active', 'archived', 'deleted', 'processing')", name='_documents_status_check'),
        sa.CheckConstraint('chunk_count >= 0', name='_documents_chunk_count_check'),
        sa.CheckConstraint('length(trim(title)) > 0', name='title_not_empty'),
        sa.CheckConstraint('length(trim(source)) > 0', name='source_not_empty'),
        sa.ForeignKeyConstraint(['domain_id'], ['knowledge_domains.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('path', name='_documents_path_unique'),
        sa.UniqueConstraint('content_hash', name='_documents_content_hash_unique')
    )
    
    op.create_index('idx_documents_domain_id', 'documents', ['domain_id'])
    op.create_index('idx_documents_status', 'documents', ['status'])
    op.create_index('idx_documents_created_at', 'documents', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_documents_updated_at', 'documents', ['updated_at'], postgresql_ops={'updated_at': 'DESC'})
    op.create_index('idx_documents_content_hash', 'documents', ['content_hash'])
    op.create_index('idx_documents_title', 'documents', ['title'])
    
    # Full-text search index
    op.execute(
        "CREATE INDEX idx_documents_fts ON documents USING GIN(to_tsvector('english', title || ' ' || COALESCE(content, '')))"
    )
    
    # 3. CHUNKS Table
    op.create_table(
        'chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_num', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('position_in_doc', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('start_char', sa.Integer(), nullable=True),
        sa.Column('end_char', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint('chunk_num >= 0', name='_chunks_chunk_num_check'),
        sa.CheckConstraint('token_count > 0', name='_chunks_token_count_check'),
        sa.CheckConstraint('position_in_doc >= 0 AND position_in_doc <= 1', name='_chunks_position_check'),
        sa.CheckConstraint('start_char >= 0', name='_chunks_start_char_check'),
        sa.CheckConstraint('end_char > 0', name='_chunks_end_char_check'),
        sa.CheckConstraint('length(trim(content)) > 0', name='content_not_empty'),
        sa.ForeignKeyConstraint(['doc_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doc_id', 'chunk_num', name='_chunks_doc_id_chunk_num_unique')
    )
    
    op.create_index('idx_chunks_doc_id', 'chunks', ['doc_id'])
    op.create_index('idx_chunks_chunk_num', 'chunks', ['doc_id', 'chunk_num'])
    op.create_index('idx_chunks_position', 'chunks', ['doc_id', 'position_in_doc'])
    op.create_index('idx_chunks_token_count', 'chunks', ['token_count'])
    op.create_index('idx_chunks_created_at', 'chunks', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # Full-text search index for chunks
    op.execute(
        "CREATE INDEX idx_chunks_fts ON chunks USING GIN(to_tsvector('english', content))"
    )
    
    # 4. EMBEDDINGS Table
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('embedding_type', sa.VARCHAR(50), nullable=False),
        sa.Column('vector_dims', sa.Integer(), nullable=False),
        sa.Column('vector_norm', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('qdrant_id', sa.BigInteger(), nullable=True),
        sa.Column('qdrant_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.CheckConstraint("embedding_type IN ('fastembed', 'ancient-bert', 'onnx-minilm')", name='_embeddings_type_check'),
        sa.CheckConstraint('vector_dims > 0', name='_embeddings_dims_check'),
        sa.ForeignKeyConstraint(['chunk_id'], ['chunks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chunk_id', 'embedding_type', name='_embeddings_chunk_type_unique'),
        sa.UniqueConstraint('qdrant_id', name='_embeddings_qdrant_id_unique')
    )
    
    op.create_index('idx_embeddings_chunk_id', 'embeddings', ['chunk_id'])
    op.create_index('idx_embeddings_type', 'embeddings', ['embedding_type'])
    op.create_index('idx_embeddings_indexed_at', 'embeddings', ['indexed_at'], postgresql_ops={'indexed_at': 'DESC'})
    op.create_index('idx_embeddings_qdrant_id', 'embeddings', ['qdrant_id'])
    op.create_index('idx_embeddings_created_at', 'embeddings', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # 5. KNOWLEDGE_RELATIONS Table
    op.create_table(
        'knowledge_relations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('source_doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relation_type', sa.VARCHAR(100), nullable=False),
        sa.Column('strength', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint('source_doc_id != target_doc_id', name='no_self_relations'),
        sa.CheckConstraint('strength >= 0 AND strength <= 1', name='_relations_strength_check'),
        sa.CheckConstraint('length(trim(relation_type)) > 0', name='relation_type_not_empty'),
        sa.ForeignKeyConstraint(['source_doc_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_doc_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_doc_id', 'target_doc_id', 'relation_type', name='_relations_unique')
    )
    
    op.create_index('idx_knowledge_relations_source', 'knowledge_relations', ['source_doc_id'])
    op.create_index('idx_knowledge_relations_target', 'knowledge_relations', ['target_doc_id'])
    op.create_index('idx_knowledge_relations_type', 'knowledge_relations', ['relation_type'])
    op.create_index('idx_knowledge_relations_strength', 'knowledge_relations', ['strength'], postgresql_ops={'strength': 'DESC'})
    op.create_index('idx_knowledge_relations_created_at', 'knowledge_relations', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # 6. AGENT_PERSONAS Table
    op.create_table(
        'agent_personas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('agent_name', sa.VARCHAR(255), nullable=False),
        sa.Column('persona_type', sa.VARCHAR(100), nullable=False),
        sa.Column('domain_focus', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('learning_state_json', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('expertise_level', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('interaction_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint('expertise_level >= 0 AND expertise_level <= 1', name='_personas_expertise_check'),
        sa.CheckConstraint('interaction_count >= 0', name='_personas_interaction_check'),
        sa.CheckConstraint('length(trim(agent_name)) > 0', name='agent_name_not_empty'),
        sa.CheckConstraint('length(trim(persona_type)) > 0', name='persona_type_not_empty'),
        sa.ForeignKeyConstraint(['domain_focus'], ['knowledge_domains.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_name', name='_agent_personas_name_unique')
    )
    
    op.create_index('idx_agent_personas_name', 'agent_personas', ['agent_name'])
    op.create_index('idx_agent_personas_type', 'agent_personas', ['persona_type'])
    op.create_index('idx_agent_personas_domain', 'agent_personas', ['domain_focus'])
    op.create_index('idx_agent_personas_expertise', 'agent_personas', ['expertise_level'], postgresql_ops={'expertise_level': 'DESC'})
    op.create_index('idx_agent_personas_created_at', 'agent_personas', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # 7. AGENT_EVOLUTION_LOG Table
    op.create_table(
        'agent_evolution_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('change_type', sa.VARCHAR(100), nullable=False),
        sa.Column('old_values_json', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('new_values_json', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('interaction_count', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.CheckConstraint('interaction_count >= 0', name='_evolution_interaction_check'),
        sa.CheckConstraint('length(trim(change_type)) > 0', name='change_type_not_empty'),
        sa.ForeignKeyConstraint(['agent_id'], ['agent_personas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_agent_evolution_log_agent_id', 'agent_evolution_log', ['agent_id'])
    op.create_index('idx_agent_evolution_log_timestamp', 'agent_evolution_log', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_agent_evolution_log_change_type', 'agent_evolution_log', ['change_type'])
    op.create_index('idx_agent_evolution_log_agent_timestamp', 'agent_evolution_log', ['agent_id', 'timestamp'], postgresql_ops={'timestamp': 'DESC'})
    
    # 8. CURATED_COLLECTIONS Table
    op.create_table(
        'curated_collections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('owner_agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('documents_json', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint('length(trim(name)) > 0', name='name_not_empty'),
        sa.ForeignKeyConstraint(['domain_id'], ['knowledge_domains.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['owner_agent_id'], ['agent_personas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('owner_agent_id', 'domain_id', 'name', name='_collections_owner_domain_name_unique')
    )
    
    op.create_index('idx_curated_collections_owner', 'curated_collections', ['owner_agent_id'])
    op.create_index('idx_curated_collections_domain', 'curated_collections', ['domain_id'])
    op.create_index('idx_curated_collections_name', 'curated_collections', ['name'])
    op.create_index('idx_curated_collections_created_at', 'curated_collections', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # 9. AUDIT_LOG Table
    op.create_table(
        'audit_log',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('operation_type', sa.VARCHAR(100), nullable=False),
        sa.Column('resource_type', sa.VARCHAR(100), nullable=False),
        sa.Column('resource_id', sa.VARCHAR(255), nullable=True),
        sa.Column('user_id', sa.VARCHAR(255), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('before_state_json', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('after_state_json', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.CheckConstraint('length(trim(operation_type)) > 0', name='operation_type_not_empty'),
        sa.CheckConstraint('length(trim(resource_type)) > 0', name='resource_type_not_empty'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create sequence for audit_log
    op.execute("CREATE SEQUENCE audit_log_id_seq START WITH 1")
    op.execute("ALTER TABLE audit_log ALTER COLUMN id SET DEFAULT nextval('audit_log_id_seq'::regclass)")
    
    op.create_index('idx_audit_log_timestamp', 'audit_log', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_audit_log_resource', 'audit_log', ['resource_type', 'resource_id'])
    op.create_index('idx_audit_log_operation', 'audit_log', ['operation_type'])
    op.create_index('idx_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('idx_audit_log_resource_timestamp', 'audit_log', ['resource_type', 'timestamp'], postgresql_ops={'timestamp': 'DESC'})
    
    # 10. QUERY_CACHE Table
    op.create_table(
        'query_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.func.uuid_generate_v4()),
        sa.Column('query_hash', sa.VARCHAR(64), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('results_json', postgresql.JSONB(), nullable=False),
        sa.Column('result_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('hit_count', sa.Integer(), nullable=False, server_default='0'),
        sa.CheckConstraint('length(trim(query_hash)) > 0', name='query_hash_not_empty'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('query_hash', name='_query_cache_hash_unique')
    )
    
    op.create_index('idx_query_cache_hash', 'query_cache', ['query_hash'], postgresql_using='hash')
    op.create_index('idx_query_cache_expires_at', 'query_cache', ['expires_at'])
    op.create_index('idx_query_cache_created_at', 'query_cache', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # Create triggers and functions
    op.execute("""
    CREATE OR REPLACE FUNCTION update_document_chunk_count() RETURNS TRIGGER AS $$
    BEGIN
        UPDATE documents SET chunk_count = (SELECT COUNT(*) FROM chunks WHERE doc_id = NEW.doc_id)
        WHERE id = NEW.doc_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
    CREATE TRIGGER trg_update_chunk_count
    AFTER INSERT OR DELETE ON chunks
    FOR EACH ROW EXECUTE FUNCTION update_document_chunk_count();
    """)
    
    op.execute("""
    CREATE OR REPLACE FUNCTION update_document_timestamp() RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
    CREATE TRIGGER trg_update_document_timestamp
    BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_document_timestamp();
    """)
    
    op.execute("""
    CREATE TRIGGER trg_update_agent_timestamp
    BEFORE UPDATE ON agent_personas
    FOR EACH ROW EXECUTE FUNCTION update_document_timestamp();
    """)
    
    # Add table comments
    op.execute("COMMENT ON TABLE documents IS 'Core document records with full metadata and content tracking'")
    op.execute("COMMENT ON COLUMN documents.content_hash IS 'SHA256 hash of document content for deduplication'")
    op.execute("COMMENT ON COLUMN documents.chunk_count IS 'Cached count of chunks; maintained via trigger'")
    op.execute("COMMENT ON TABLE chunks IS 'Token-aware document chunks with positional metadata and overlap information'")
    op.execute("COMMENT ON COLUMN chunks.position_in_doc IS 'Normalized position (0-1) of chunk within document'")
    op.execute("COMMENT ON COLUMN chunks.token_count IS 'Approximate token count for the chunk content'")
    op.execute("COMMENT ON TABLE embeddings IS 'Metadata for embeddings stored externally (Qdrant, FAISS, etc.)'")
    op.execute("COMMENT ON COLUMN embeddings.qdrant_id IS 'Point ID in Qdrant vector database'")
    op.execute("COMMENT ON COLUMN embeddings.embedding_type IS 'Type of embedding model used'")
    op.execute("COMMENT ON TABLE agent_personas IS 'Agent configurations and learning state for autonomous knowledge workers'")
    op.execute("COMMENT ON COLUMN agent_personas.learning_state_json IS 'Serialized learning parameters, preferences, and state'")
    op.execute("COMMENT ON TABLE audit_log IS 'Complete operation history for compliance, debugging, and security monitoring'")


def downgrade() -> None:
    """Drop all schema objects"""
    
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_update_agent_timestamp ON agent_personas CASCADE")
    op.execute("DROP TRIGGER IF EXISTS trg_update_document_timestamp ON documents CASCADE")
    op.execute("DROP TRIGGER IF EXISTS trg_update_chunk_count ON chunks CASCADE")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_document_timestamp()")
    op.execute("DROP FUNCTION IF EXISTS update_document_chunk_count()")
    
    # Drop tables (order matters due to FK constraints)
    op.drop_table('query_cache')
    op.drop_table('audit_log')
    op.execute("DROP SEQUENCE IF EXISTS audit_log_id_seq")
    op.drop_table('curated_collections')
    op.drop_table('agent_evolution_log')
    op.drop_table('agent_personas')
    op.drop_table('embeddings')
    op.drop_table('knowledge_relations')
    op.drop_table('chunks')
    op.drop_table('documents')
    op.drop_table('knowledge_domains')
