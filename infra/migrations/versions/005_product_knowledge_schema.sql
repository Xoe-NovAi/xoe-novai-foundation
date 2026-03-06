-- XNAi Foundation - Product & Service Knowledge Schema
-- Purpose: Structured storage for competitive intelligence and technical specs.

CREATE SCHEMA IF NOT EXISTS product_knowledge;

-- 1. Manufacturers / Service Providers
CREATE TABLE IF NOT EXISTS product_knowledge.providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    website TEXT,
    description TEXT,
    category TEXT, -- e.g., Cloud Provider, Hardware, Software
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Products / Services
CREATE TABLE IF NOT EXISTS product_knowledge.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID REFERENCES product_knowledge.providers(id),
    name TEXT NOT NULL,
    version TEXT,
    category TEXT, -- e.g., LLM Model, Database, GPU
    specifications JSONB DEFAULT '{}', -- Technical specs
    pricing_model TEXT,
    documentation_url TEXT,
    status TEXT DEFAULT 'active', -- e.g., active, deprecated, beta
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Comparisons / Benchmarks
CREATE TABLE IF NOT EXISTS product_knowledge.benchmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES product_knowledge.products(id),
    metric_name TEXT NOT NULL,
    metric_value NUMERIC,
    unit TEXT,
    source_url TEXT,
    tested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Knowledge Graph Relations (Simplified for SQL storage)
CREATE TABLE IF NOT EXISTS product_knowledge.relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL,
    target_id UUID NOT NULL,
    relation_type TEXT NOT NULL, -- e.g., competes_with, integrates_with, powers
    metadata JSONB DEFAULT '{}'
);
