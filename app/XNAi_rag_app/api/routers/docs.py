"""
Xoe-NovAi Documentation Search API
=================================

Provides unified search across Documentation, Expert Knowledge, and Memory Bank
using the Semantic Index (YAML concept map).
"""

import os
import yaml
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

# Path to the semantic index
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.resolve()
INDEX_PATH = PROJECT_ROOT / "docs/knowledge-synthesis/SEMANTIC-INDEX.yaml"

class ConceptSearchResult(BaseModel):
    """Search result for a concept"""
    id: str
    name: str
    description: str
    links: Dict[str, List[str]]
    score: float = 1.0

class SearchResponse(BaseModel):
    """Unified search response"""
    query: str
    results: List[ConceptSearchResult]
    total: int

def load_semantic_index() -> Dict[str, Any]:
    """Load the semantic index from YAML."""
    if not INDEX_PATH.exists():
        logger.error(f"Semantic index not found at {INDEX_PATH}")
        return {"concepts": []}
    
    try:
        with open(INDEX_PATH, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load semantic index: {e}")
        return {"concepts": []}

@router.get("/search", response_model=SearchResponse)
async def search_docs(
    query: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search across documentation, EKB, and memory bank using the semantic index.
    """
    data = load_semantic_index()
    concepts = data.get("concepts", [])
    
    results = []
    query_lower = query.lower()
    
    for concept in concepts:
        name = concept.get("name", "").lower()
        description = concept.get("description", "").lower()
        id_ = concept.get("id", "").lower()
        
        # Simple keyword matching (can be improved with fuzzy search or embeddings)
        if query_lower in name or query_lower in description or query_lower in id_:
            results.append(ConceptSearchResult(
                id=concept.get("id"),
                name=concept.get("name"),
                description=concept.get("description"),
                links=concept.get("links", {})
            ))
            
    # Sort results (could implement more complex scoring)
    # results.sort(key=lambda x: x.score, reverse=True)
    
    return SearchResponse(
        query=query,
        results=results[:limit],
        total=len(results)
    )

@router.get("/concepts", response_model=List[Dict[str, Any]])
async def get_all_concepts():
    """Get all concepts from the semantic index."""
    data = load_semantic_index()
    return data.get("concepts", [])
