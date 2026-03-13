#!/usr/bin/env python3
"""
Knowledge Synthesis Validator
============================

Validates the SEMANTIC-INDEX.yaml for structural integrity, path existence,
and concept coverage across Docs, EKB, and Memory Bank.
"""

import os
import sys
from pathlib import Path
import yaml
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def validate_synthesis(root_dir: str):
    """Validate the knowledge synthesis index."""
    root = Path(root_dir)
    index_path = root / "docs/knowledge-synthesis/SEMANTIC-INDEX.yaml"
    
    if not index_path.exists():
        logger.error(f"Semantic index not found at {index_path}")
        return False

    try:
        with open(index_path, 'r') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to parse YAML: {e}")
        return False

    if 'concepts' not in data:
        logger.error("Missing 'concepts' section in index")
        return False

    errors = 0
    concepts = data['concepts']
    logger.info(f"Validating {len(concepts)} concepts...")

    for concept in concepts:
        cid = concept.get('id', 'unknown')
        name = concept.get('name', cid)
        links = concept.get('links', {})

        # Check for mandatory tiers
        for tier in ['docs', 'ekb', 'memory']:
            if tier not in links:
                logger.warning(f"Concept '{name}' ({cid}) missing tier: {tier}")
                # We don't increment errors for missing tiers yet, just warn
            
            # Validate paths
            tier_links = links.get(tier, [])
            for link in tier_links:
                # Resolve path relative to project root
                # Note: links in YAML might be relative to docs/knowledge-synthesis/
                # or absolute from root. We'll handle both.
                
                if link.startswith('../'):
                    # Relative to docs/knowledge-synthesis/
                    abs_path = (index_path.parent / link).resolve()
                else:
                    # Assume relative to project root
                    abs_path = (root / link).resolve()
                
                if not abs_path.exists():
                    logger.error(f"[{cid}] Broken {tier} link: {link} (Resolved: {abs_path})")
                    errors += 1
                elif not abs_path.is_file() and not abs_path.is_dir():
                    logger.error(f"[{cid}] Invalid {tier} link type: {link}")
                    errors += 1

    if errors == 0:
        logger.info("✅ Knowledge synthesis validation passed!")
        return True
    else:
        logger.error(f"❌ Knowledge synthesis validation failed with {errors} errors.")
        return False

if __name__ == "__main__":
    project_root = os.getcwd()
    success = validate_synthesis(project_root)
    sys.exit(0 if success else 1)
