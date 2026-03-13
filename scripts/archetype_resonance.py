#!/usr/bin/env python3
"""
🔱 ARCHETYPE RESONANCE ENGINE: The Initiation Engine
Calculates identity resonance between current agent context and the Archetype Library.
"""
import anyio
import sys
import argparse
import re
import math
from pathlib import Path
from typing import Dict, List, Set

def get_keywords(text: str) -> Set[str]:
    """Extract clean keywords from text."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    # Basic stop words filter
    stop_words = {'the', 'and', 'was', 'for', 'with', 'that', 'this', 'into'}
    return {w for w in words if w not in stop_words}

def calculate_cosine_similarity(vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
    """Calculate cosine similarity between two frequency vectors."""
    all_words = set(vec1.keys()) | set(vec2.keys())
    dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in all_words)
    
    magnitude1 = math.sqrt(sum(v**2 for v in vec1.values()))
    magnitude2 = math.sqrt(sum(v**2 for v in vec2.values()))
    
    if not magnitude1 or not magnitude2:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def vectorize(text: str) -> Dict[str, int]:
    """Create a frequency vector from text, filtering out code/JSON noise."""
    # Improved filter to remove code syntax
    code_noise = {
        'self', 'import', 'class', 'def', 'return', 'none', 'true', 'false',
        'json', 'version', 'title', 'core', 'essence', 'dynamic', 'traits',
        'init', 'print', 'from', 'datetime', 'random', 'json', 'loads',
        'weights', 'choices', ' weights', 'append', 'entry', 'copy',
        'try', 'except', 'pass', 'global', 'raise', 'yield'
    }
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    vec = {}
    for w in words:
        if w not in code_noise:
            vec[w] = vec.get(w, 0) + 1
    return vec

async def load_archetype_library(library_path: str) -> Dict[str, str]:
    """Parse the ARCHETYPE_LIBRARY.md for definitions."""
    path = Path(library_path)
    if not path.exists():
        return {}
    
    content = path.read_text()
    archetypes = {}
    # Extract sections like ### 1. 🔥 BRIGID: The Hearth Keeper
    sections = re.split(r'### \d+\.\s*', content)
    for section in sections[1:]:
        lines = section.split('\n')
        header = lines[0].strip()
        name = re.sub(r'[^a-zA-Z]', '', header.split(':')[0])
        archetypes[name] = section
    return archetypes

async def calculate_resonance(context_file: str):
    """Compare reasoning traces to Archetype embeddings."""
    print(f"🔱 Resonance: Calculating resonance for [{context_file}]...")
    
    lib_path = "artifacts/ARCHETYPE_LIBRARY.md"
    archetypes = await load_archetype_library(lib_path)
    
    if not archetypes:
        print(f"❌ Error: Could not load library at {lib_path}")
        return

    context_path = Path(context_file)
    if not context_path.exists():
        print(f"❌ Error: Context file {context_file} not found.")
        return
        
    context_text = context_path.read_text()
    context_vec = vectorize(context_text)
    
    print("🔱 Resonance Results:")
    results = []
    for name, definition in archetypes.items():
        archetype_vec = vectorize(definition)
        score = calculate_cosine_similarity(context_vec, archetype_vec)
        results.append((name, score))
    
    # Sort by score
    results.sort(key=lambda x: x[1], reverse=True)
    
    for name, score in results:
        print(f"  - {name:15}: {score*100:5.1f}%")
    
    top_name, top_score = results[0]
    if top_score > 0.3:
        print(f"\n✅ Initiation Suggestion: {top_name} (Resonance Alignment)")
    else:
        print("\n⚠️  Low Resonance: Context does not align with Oikos Archetypes.")

async def main():
    parser = argparse.ArgumentParser(description="Archetype Resonance Engine")
    parser.add_argument("file", help="The context file or reasoning trace to analyze")
    args = parser.parse_args()
    
    await calculate_resonance(args.file)

if __name__ == "__main__":
    anyio.run(main)
