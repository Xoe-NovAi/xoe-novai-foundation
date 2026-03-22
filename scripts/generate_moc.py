#!/usr/bin/env python3
"""
scripts/generate_moc.py
---------------------------------------------------
Gnostic Vault Map of Content (MoC) Generator
Scans the Zettelkasten and updates the Topological Gnosis-Graph (TGG).
SESS-27.7 - Sovereign Stack
---------------------------------------------------
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Adjust path to include project root
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.core.gmc_normalizer import GMCNormalizer

MEMORY_BANK_ROOT = Path("memory_bank")
OUTPUT_FILE = MEMORY_BANK_ROOT / "MAP_OF_CONTENT.json"

def scan_vault() -> Dict[str, Any]:
    """Scans the Memory Bank for markdown files and extracts metadata."""
    graph: Dict[str, Any] = {"files": {}, "tags": {}, "links": []}

    for root, _, files in os.walk(MEMORY_BANK_ROOT):
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                relative_path = str(file_path.relative_to(MEMORY_BANK_ROOT))
                
                # Basic metadata extraction
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Extract frontmatter (simple regex or yaml parse)
                    match = GMCNormalizer.FRONTMATTER_PATTERN.match(content)
                    metadata = {}
                    if match:
                        try:
                            metadata = yaml.safe_load(match.group(1))
                        except yaml.YAMLError:
                            pass
                    
                    graph["files"][relative_path] = {
                        "path": relative_path,
                        "metadata": metadata,
                        "hash": GMCNormalizer.compute_rigidity_hash(content)
                    }
                    
                    # Tag indexing
                    if "tags" in metadata:
                        tags = metadata["tags"]
                        if isinstance(tags, str):
                            tags = [tags]
                        for tag in tags:
                            if tag not in graph["tags"]:
                                graph["tags"][tag] = []
                            graph["tags"][tag].append(relative_path)

                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")

    return graph

def save_graph(graph: Dict[str, Any]):
    """Saves the graph to JSON."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"Map of Content generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    print("Generating Gnostic Map of Content...")
    graph = scan_vault()
    save_graph(graph)
