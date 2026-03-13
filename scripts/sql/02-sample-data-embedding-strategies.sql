-- Sample Data for Embedding Strategy Map
-- Provides routing guidance for optimal embedding models
-- Created: 2025-02-25

-- Default Strategy: General semantic search
INSERT OR IGNORE INTO embedding_strategy_map 
  (id, query_type, content_domain, embedding_model, preference_score, notes) 
VALUES
  ('strat_001', 'semantic', 'general', 'all-minilm-l6-v2', 0.95, 'Default general-purpose embeddings');

-- Code Domain: Specialized for code search and retrieval
INSERT OR IGNORE INTO embedding_strategy_map 
  (id, query_type, content_domain, embedding_model, preference_score, notes) 
VALUES
  ('strat_002', 'semantic', 'code', 'code-search-ada-code-001', 0.92, 'Optimized for code search and retrieval');

-- Documentation Domain: Technical documentation retrieval
INSERT OR IGNORE INTO embedding_strategy_map 
  (id, query_type, content_domain, embedding_model, preference_score, notes) 
VALUES
  ('strat_003', 'semantic', 'documentation', 'all-mpnet-base-v2', 0.90, 'Optimized for technical documentation');

-- Knowledge Base: High-quality knowledge retrieval
INSERT OR IGNORE INTO embedding_strategy_map 
  (id, query_type, content_domain, embedding_model, preference_score, notes) 
VALUES
  ('strat_004', 'semantic', 'knowledge-base', 'bge-large-en-v1.5', 0.93, 'High-quality knowledge retrieval');

-- Lexical Search: Fast fallback for simple queries
INSERT OR IGNORE INTO embedding_strategy_map 
  (id, query_type, content_domain, embedding_model, preference_score, notes) 
VALUES
  ('strat_005', 'lexical', 'general', 'bm25', 0.75, 'Fast lexical search fallback');

-- Hybrid Search: Combined semantic and lexical search
INSERT OR IGNORE INTO embedding_strategy_map 
  (id, query_type, content_domain, embedding_model, preference_score, notes) 
VALUES
  ('strat_006', 'hybrid', 'general', 'hybrid-ensemble', 0.97, 'Combined semantic and lexical search');

-- Voice Queries: Optimized for voice-based embeddings
INSERT OR IGNORE INTO embedding_strategy_map 
  (id, query_type, content_domain, embedding_model, preference_score, notes) 
VALUES
  ('strat_007', 'semantic', 'voice', 'all-minilm-l6-v2', 0.88, 'Voice query embeddings');

-- Reasoning Queries: Enhanced for complex reasoning
INSERT OR IGNORE INTO embedding_strategy_map 
  (id, query_type, content_domain, embedding_model, preference_score, notes) 
VALUES
  ('strat_008', 'semantic', 'reasoning', 'e5-large-v2', 0.94, 'Enhanced for complex reasoning queries');
