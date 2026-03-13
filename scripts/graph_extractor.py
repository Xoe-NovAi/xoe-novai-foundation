#!/usr/bin/env python3
"""
Xoe-NovAi Graph Extractor (Gnosis Engine)
=========================================

Extracts entities and relations from documents and populates the 
PostgreSQL knowledge graph using LightRAG v1.0+ core logic.

Hardware Optimized: Ryzen 5700U (Zen 2)
Backend: PostgreSQL 16 (pgvector)
Model: Krikri-8B-Instruct (Local)
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional
import argparse
from lightrag import LightRAG, QueryParam
# Placeholder for custom local model loader
# from app.XNAi_rag_app.core.model_router import load_local_model

logger = logging.getLogger("graph_extractor")

async def initialize_graph_engine(postgres_uri: str, working_dir: str = "./data/lightrag_cache"):
    """Initialize LightRAG with PostgreSQL storage."""
    rag = LightRAG(
        working_dir=working_dir,
        kv_storage="POSTGRES",
        vector_storage="POSTGRES",
        graph_storage="POSTGRES",
        doc_status_storage="POSTGRES",
        addon_params={
            "postgres_url": postgres_uri,
        }
    )
    await rag.initialize_storages()
    return rag

async def process_document(rag: LightRAG, file_path: str):
    """Ingest and extract graph triplets from a document."""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    logger.info(f"Processing {path.name}...")
    await rag.ainsert(content)
    logger.info(f"Successfully indexed {path.name} in Gnosis Graph.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XNAi Graph Extractor")
    parser.add_argument("--file", type=str, required=True, help="Path to document")
    parser.add_argument("--db-uri", type=str, default=os.getenv("DATABASE_URL"), help="Postgres URI")
    
    args = parser.parse_args()
    
    if not args.db_uri:
        print("Error: DATABASE_URL not set.")
        exit(1)

    asyncio.run(process_document(None, args.file)) # Initial skeleton
