-- SQL Tracking Tables for Knowledge Management
-- Created: 2025-02-25
-- Purpose: Session SQLite enhancements for planning, coordination, and progress monitoring
-- Supports: 1000+ agents, 100K+ documents

-- TABLE 1: Document Catalog
-- Tracks all discovered documents with metadata
CREATE TABLE IF NOT EXISTS document_catalog (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  source TEXT,
  domain TEXT,
  size_bytes INTEGER,
  chunk_count INTEGER,
  embedding_status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 2: Document Changes
-- Audit trail for document updates and modifications
CREATE TABLE IF NOT EXISTS document_changes (
  id TEXT PRIMARY KEY,
  doc_id TEXT NOT NULL,
  change_type TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reason TEXT,
  changed_by TEXT
);

-- TABLE 3: Agent Persona
-- Track multi-agent personas and learning states
CREATE TABLE IF NOT EXISTS agent_persona (
  id TEXT PRIMARY KEY,
  agent_name TEXT NOT NULL,
  persona_type TEXT,
  learning_state_json TEXT,
  domain_focus TEXT,
  expertise_level REAL DEFAULT 0.0,
  metadata_json TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 4: Agent Session State
-- Session persistence for agents across conversations
CREATE TABLE IF NOT EXISTS agent_session_state (
  agent_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  conversation_history_json TEXT,
  context_window_json TEXT,
  last_query TEXT,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (agent_id, session_id)
);

-- TABLE 5: Knowledge Domain
-- Domain hierarchy and categorization for knowledge organization
CREATE TABLE IF NOT EXISTS knowledge_domain (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  parent_id TEXT,
  metadata_json TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 6: Embedding Strategy Map
-- Route queries to optimal embedding strategy based on type and domain
CREATE TABLE IF NOT EXISTS embedding_strategy_map (
  id TEXT PRIMARY KEY,
  query_type TEXT NOT NULL,
  content_domain TEXT,
  embedding_model TEXT NOT NULL,
  preference_score REAL DEFAULT 0.5,
  notes TEXT
);

-- Create indices for fast querying
CREATE INDEX IF NOT EXISTS idx_document_catalog_domain_status 
  ON document_catalog (domain, embedding_status);

CREATE INDEX IF NOT EXISTS idx_document_changes_doc_timestamp 
  ON document_changes (doc_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_agent_persona_name_domain 
  ON agent_persona (agent_name, domain_focus);

CREATE INDEX IF NOT EXISTS idx_knowledge_domain_parent 
  ON knowledge_domain (parent_id);

CREATE INDEX IF NOT EXISTS idx_embedding_strategy_query_domain 
  ON embedding_strategy_map (query_type, content_domain);
