"""Agent & research job management schema

Revision ID: 006
Revises: 005_product_knowledge_schema
Create Date: 2026-03-02 00:00:00.000000

Adds tables supporting agent registry, research jobs, preferences, metrics,
and collaboration tracking.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005_product_knowledge_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Agents registry
    op.create_table(
        'agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.func.uuid_generate_v4()),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('email', sa.VARCHAR(255), nullable=True),
        sa.Column('model', sa.VARCHAR(255), nullable=True),
        sa.Column('runtime', sa.VARCHAR(50), nullable=False, server_default='unknown'),
        sa.Column('priority', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('personality_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.VARCHAR(50), nullable=False, server_default='active'),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='_agents_name_unique')
    )
    op.create_index('idx_agents_priority', 'agents', ['priority'])
    op.create_index('idx_agents_status', 'agents', ['status'])

    # Preferences
    op.create_table(
        'agent_preferences',
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain', sa.VARCHAR(255), nullable=False),
        sa.Column('score', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('agent_id', 'domain')
    )
    op.create_index('idx_agent_prefs_agent', 'agent_preferences', ['agent_id'])
    op.create_index('idx_agent_prefs_domain', 'agent_preferences', ['domain'])

    # Research jobs
    op.create_table(
        'research_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.func.uuid_generate_v4()),
        sa.Column('slug', sa.VARCHAR(255), nullable=False),
        sa.Column('title', sa.VARCHAR(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.VARCHAR(50), nullable=False, server_default='open'),
        sa.Column('claimed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('domain_tags', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['claimed_by'], ['agents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug', name='_research_jobs_slug_unique')
    )
    op.create_index('idx_research_jobs_status', 'research_jobs', ['status'])
    op.create_index('idx_research_jobs_claimed_by', 'research_jobs', ['claimed_by'])

    # Collaborators mapping
    op.create_table(
        'research_collaborators',
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['research_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('job_id', 'agent_id')
    )

    # Metrics
    op.create_table(
        'agent_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.func.uuid_generate_v4()),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_name', sa.VARCHAR(255), nullable=False),
        sa.Column('value', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_agent_metrics_agent', 'agent_metrics', ['agent_id'])
    op.create_index('idx_agent_metrics_name', 'agent_metrics', ['metric_name'])
    op.create_index('idx_agent_metrics_time', 'agent_metrics', ['recorded_at'], postgresql_ops={'recorded_at':'DESC'})


def downgrade() -> None:
    op.drop_table('agent_metrics')
    op.drop_table('research_collaborators')
    op.drop_table('research_jobs')
    op.drop_table('agent_preferences')
    op.drop_table('agents')
