#!/usr/bin/env python3
"""
XNAi Expert Registry Initializer
================================

Populates the expert_system.registry with initial persistent personas.
"""

import os
import json
import psycopg2
from typing import List, Dict

# Configuration from environment or defaults
DB_URL = os.getenv("DATABASE_URL", "postgresql://vikunja:vikunja123@localhost:5432/vikunja")

EXPERTS = [
    {
        "name": "Jungian Expert",
        "system_prompt": "You are a Senior Analytical Psychologist specializing in Jungian Archetypes and the Collective Unconscious. Prioritize depth and symbolic interpretation.",
        "embedding_model": "bowphs/SPhilBerta",
        "rag_filter": {"category": "psychology"},
        "base_expertise": "Jungian Archetypes, Dream Analysis, Shadow Work"
    },
    {
        "name": "FastAPI Expert",
        "system_prompt": "You are a Principal Backend Engineer specializing in FastAPI, Pydantic, and AnyIO. Prioritize high-performance, asynchronous patterns.",
        "embedding_model": "all-MiniLM-L6-v2",
        "rag_filter": {"category": "technical_manuals"},
        "base_expertise": "FastAPI, Asynchronous Python, API Design"
    },
    {
        "name": "Gnosis Expert",
        "system_prompt": "You are a Scholarly Researcher of Ancient Philosophy and Gnosticism. You have deep knowledge of Greek texts and hermetic traditions.",
        "embedding_model": "pranaydeeps/Ancient-Greek-BERT",
        "rag_filter": {"category": "gnosis"},
        "base_expertise": "Neoplatonism, Gnosticism, Ancient Greek Philology"
    },
    {
        "name": "Documentation Expert",
        "system_prompt": "You are the primary custodian of the XNAi Foundation documentation. You know every manual, tutorial, and protocol in the docs/ folder.",
        "embedding_model": "all-MiniLM-L6-v2",
        "rag_filter": {"source": "internal_docs"},
        "base_expertise": "XNAi Stack, Protocols, Service Architecture"
    }
]

def initialize():
    print("🚀 Initializing XNAi Expert Registry...")
    try:
        conn = psycopg2.connect(DB_URL)
        with conn.cursor() as cur:
            # Ensure schema exists (in case migration didn't run yet)
            cur.execute("CREATE SCHEMA IF NOT EXISTS expert_system;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS expert_system.registry (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name TEXT UNIQUE NOT NULL,
                    system_prompt TEXT NOT NULL,
                    embedding_model TEXT,
                    rag_filter JSONB DEFAULT '{}',
                    model_override TEXT,
                    base_expertise TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            for expert in EXPERTS:
                cur.execute("""
                    INSERT INTO expert_system.registry (name, system_prompt, embedding_model, rag_filter, base_expertise)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        system_prompt = EXCLUDED.system_prompt,
                        embedding_model = EXCLUDED.embedding_model,
                        rag_filter = EXCLUDED.rag_filter,
                        base_expertise = EXCLUDED.base_expertise;
                """, (expert["name"], expert["system_prompt"], expert["embedding_model"], json.dumps(expert["rag_filter"]), expert["base_expertise"]))
            
            conn.commit()
            print(f"✅ Successfully initialized {len(EXPERTS)} experts.")
            
    except Exception as e:
        print(f"❌ Error initializing registry: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    initialize()
