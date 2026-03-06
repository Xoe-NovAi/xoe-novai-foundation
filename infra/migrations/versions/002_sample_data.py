"""Sample data for knowledge management system

Revision ID: 002
Revises: 001
Create Date: 2026-02-24 00:00:00.000000

This migration adds sample data to the schema for testing and development:
- Sample knowledge domains
- Sample documents and chunks
- Sample agent personas
- Sample embeddings
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone
import uuid


def upgrade() -> None:
    """Insert sample data"""
    
    # Insert sample knowledge domains
    op.execute("""
        INSERT INTO knowledge_domains (id, name, description, created_at, updated_at)
        VALUES 
            ('550e8400-e29b-41d4-a716-446655440001'::uuid, 'Machine Learning', 'ML and AI concepts', NOW(), NOW()),
            ('550e8400-e29b-41d4-a716-446655440002'::uuid, 'Data Engineering', 'Data processing and pipelines', NOW(), NOW()),
            ('550e8400-e29b-41d4-a716-446655440003'::uuid, 'Cloud Infrastructure', 'Cloud platforms and DevOps', NOW(), NOW()),
            ('550e8400-e29b-41d4-a716-446655440004'::uuid, 'Security', 'Security practices and protocols', NOW(), NOW());
    """)
    
    # Insert sample documents
    op.execute("""
        INSERT INTO documents (id, title, source, domain_id, status, chunk_count, created_at, updated_at, content_hash, mime_type)
        VALUES 
            ('650e8400-e29b-41d4-a716-446655440001'::uuid, 'Neural Networks Basics', 'documentation', '550e8400-e29b-41d4-a716-446655440001'::uuid, 'active', 5, NOW(), NOW(), 'hash1', 'text/plain'),
            ('650e8400-e29b-41d4-a716-446655440002'::uuid, 'PostgreSQL Performance', 'tutorial', '550e8400-e29b-41d4-a716-446655440002'::uuid, 'active', 8, NOW(), NOW(), 'hash2', 'text/plain'),
            ('650e8400-e29b-41d4-a716-446655440003'::uuid, 'Kubernetes Deployment', 'guide', '550e8400-e29b-41d4-a716-446655440003'::uuid, 'active', 12, NOW(), NOW(), 'hash3', 'text/plain');
    """)
    
    # Insert sample chunks
    op.execute("""
        INSERT INTO chunks (id, doc_id, chunk_num, content, token_count, position_in_doc, start_char, end_char, created_at, updated_at)
        VALUES 
            ('750e8400-e29b-41d4-a716-446655440001'::uuid, '650e8400-e29b-41d4-a716-446655440001'::uuid, 0, 'Neural networks are computational models inspired by biological neural networks.', 15, 0.0, 0, 76, NOW(), NOW()),
            ('750e8400-e29b-41d4-a716-446655440002'::uuid, '650e8400-e29b-41d4-a716-446655440001'::uuid, 1, 'They consist of interconnected nodes called neurons that process information.', 14, 0.2, 77, 150, NOW(), NOW()),
            ('750e8400-e29b-41d4-a716-446655440003'::uuid, '650e8400-e29b-41d4-a716-446655440002'::uuid, 0, 'PostgreSQL performance optimization requires understanding query execution.', 12, 0.0, 0, 72, NOW(), NOW()),
            ('750e8400-e29b-41d4-a716-446655440004'::uuid, '650e8400-e29b-41d4-a716-446655440002'::uuid, 1, 'Indexes are crucial for improving query performance on large datasets.', 12, 0.15, 73, 141, NOW(), NOW());
    """)
    
    # Insert sample agent personas
    op.execute("""
        INSERT INTO agent_personas (id, agent_name, persona_type, domain_focus, expertise_level, interaction_count, created_at, updated_at)
        VALUES 
            ('850e8400-e29b-41d4-a716-446655440001'::uuid, 'ML-Researcher', 'researcher', '550e8400-e29b-41d4-a716-446655440001'::uuid, 0.85, 150, NOW(), NOW()),
            ('850e8400-e29b-41d4-a716-446655440002'::uuid, 'DevOps-Engineer', 'engineer', '550e8400-e29b-41d4-a716-446655440003'::uuid, 0.92, 240, NOW(), NOW()),
            ('850e8400-e29b-41d4-a716-446655440003'::uuid, 'Security-Advisor', 'advisor', '550e8400-e29b-41d4-a716-446655440004'::uuid, 0.88, 180, NOW(), NOW());
    """)
    
    # Insert sample embeddings
    op.execute("""
        INSERT INTO embeddings (id, chunk_id, embedding_type, vector_dims, qdrant_id, created_at, indexed_at)
        VALUES 
            ('950e8400-e29b-41d4-a716-446655440001'::uuid, '750e8400-e29b-41d4-a716-446655440001'::uuid, 'fastembed', 384, 1, NOW(), NOW()),
            ('950e8400-e29b-41d4-a716-446655440002'::uuid, '750e8400-e29b-41d4-a716-446655440002'::uuid, 'fastembed', 384, 2, NOW(), NOW()),
            ('950e8400-e29b-41d4-a716-446655440003'::uuid, '750e8400-e29b-41d4-a716-446655440003'::uuid, 'onnx-minilm', 384, 3, NOW(), NOW());
    """)
    
    # Insert sample knowledge relations
    op.execute("""
        INSERT INTO knowledge_relations (id, source_doc_id, target_doc_id, relation_type, strength, created_at, updated_at)
        VALUES 
            ('a50e8400-e29b-41d4-a716-446655440001'::uuid, '650e8400-e29b-41d4-a716-446655440001'::uuid, '650e8400-e29b-41d4-a716-446655440002'::uuid, 'references', 0.75, NOW(), NOW()),
            ('a50e8400-e29b-41d4-a716-446655440002'::uuid, '650e8400-e29b-41d4-a716-446655440002'::uuid, '650e8400-e29b-41d4-a716-446655440003'::uuid, 'complements', 0.60, NOW(), NOW());
    """)


def downgrade() -> None:
    """Remove sample data"""
    op.execute("DELETE FROM knowledge_relations WHERE id IN ('a50e8400-e29b-41d4-a716-446655440001'::uuid, 'a50e8400-e29b-41d4-a716-446655440002'::uuid)")
    op.execute("DELETE FROM embeddings WHERE id LIKE 'a50e8400%'::uuid OR id LIKE '950e8400%'::uuid")
    op.execute("DELETE FROM agent_personas WHERE id LIKE '850e8400%'::uuid")
    op.execute("DELETE FROM chunks WHERE id LIKE '750e8400%'::uuid")
    op.execute("DELETE FROM documents WHERE id LIKE '650e8400%'::uuid")
    op.execute("DELETE FROM knowledge_domains WHERE id LIKE '550e8400%'::uuid")
