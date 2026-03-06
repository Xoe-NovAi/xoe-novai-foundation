# Alembic Database Migrations (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **Alembic** (v1.13+) is used to manage the schema evolution of the PostgreSQL 16 database. It utilizes SQLAlchemy 2.0 and is optimized for the knowledge management schema (Gnosis Engine), including UUIDs, JSONB, and Full-Text Search indices.

---

## 🛠 Schema Architecture

The initial schema (`001_initial_knowledge_schema.py`) establishes the core of the Gnosis Engine:

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `knowledge_domains` | Hierarchical taxonomy | UUID, Self-referential FK |
| `documents` | Core record storage | JSONB Metadata, Content Hashing, FTS Index |
| `chunks` | Document segments | Token counting, Positional metadata |
| `embeddings` | Vector metadata | Links to Qdrant IDs |
| `agent_personas` | Autonomous workers | Learning state (JSONB), Expertise tracking |
| `audit_log` | Compliance & History | BigInt sequence, Before/After state |

### Advanced Features
- **Triggers**: Automated `updated_at` timestamps and `chunk_count` caching.
- **Indices**: GIN indices for PostgreSQL Full-Text Search (english tsvector).
- **Constraints**: Strict status checks (e.g., `active`, `archived`) and uniqueness on content hashes.

---

## 📈 Operational Workflows

### 1. Generating Migrations
Alembic is configured to autogenerate migrations based on the SQLAlchemy models:
```bash
# Autogenerate a new migration
alembic revision --autogenerate -m "Add new field to documents"
```

### 2. Applying Migrations
Apply migrations to the production/local database:
```bash
# Upgrade to the latest version
alembic upgrade head

# Downgrade by one version (CAUTION)
alembic downgrade -1
```

### 3. Verification
Check the current migration status:
```bash
alembic current
alembic history --verbose
```

---

## 🧪 Implementation Patterns

### UUIDs & JSONB
The stack standardizes on `postgresql.UUID` and `postgresql.JSONB` for maximum flexibility and performance in metadata-heavy workloads.
```python
sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.uuid_generate_v4())
sa.Column('metadata', postgresql.JSONB(), server_default='{}')
```

### Full-Text Search
Custom SQL is used in migrations to create GIN indices for performance:
```python
op.execute("CREATE INDEX idx_docs_fts ON documents USING GIN(to_tsvector('english', title || ' ' || COALESCE(content, '')))")
```

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Out-of-sync Schema | Local DB differs from models | Run `alembic upgrade head` before starting development. |
| Duplicate Revisions | Branch merge conflict | Use `alembic merge` to combine heads. |
| Migration Failure | Locked tables or active connections | Ensure all agents/services are paused during migration. |

---

## 📚 References
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [XNAi Database Schema](migrations/versions/001_initial_knowledge_schema.py)
