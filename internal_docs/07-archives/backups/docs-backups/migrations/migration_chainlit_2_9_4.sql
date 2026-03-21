-- Chainlit 2.9.4 Database Migration
-- Adds modes column to steps table for persistence schema migration
-- Run this before upgrading to Chainlit 2.9.4

-- For PostgreSQL (if using external DB):
-- ALTER TABLE steps ADD COLUMN IF NOT EXISTS modes JSONB;

-- For SQLite (default Chainlit):
-- This is handled automatically by Chainlit's migration system

-- If you encounter persistence errors after upgrading, run:
-- chainlit db migrate

-- Alternative manual migration for SQLite:
-- ALTER TABLE steps ADD COLUMN modes TEXT;  -- JSON as TEXT in SQLite

-- Verify migration:
-- SELECT name FROM sqlite_master WHERE type='table' AND name='steps';
-- PRAGMA table_info(steps);
