#!/usr/bin/env python3
"""
CLI Pruner for Hellenic Ingestion Pipeline
Strips noise from raw session logs before semantic indexing
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class CliPruner:
    """Removes noise from raw session logs for semantic indexing."""
    
    def __init__(self):
        self.timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
        self.tool_call_pattern = re.compile(r'Tool call:.*?(?=\n\S|\Z)', re.DOTALL)
    
    def remove_timestamps(self, text: str) -> str:
        """Remove ISO 8601 timestamps."""
        return self.timestamp_pattern.sub('', text)
    
    def remove_tool_calls(self, text: str) -> str:
        """Remove tool-call headers and next 2 lines."""
        lines = text.split('\n')
        result = []
        i = 0
        while i < len(lines):
            if lines[i].startswith('Tool call:'):
                i += 3
            else:
                result.append(lines[i])
                i += 1
        return '\n'.join(result)
    
    def remove_metadata(self, text: str) -> str:
        """Remove redundant metadata fields (JSON-style only)."""
        # Only remove JSON-style metadata fields, not natural language
        text = re.sub(r'"session_id":\s*"[^"]*"[,\s]*', '', text)
        text = re.sub(r'"event_id":\s*"[^"]*"[,\s]*', '', text)
        text = re.sub(r'"timestamp":\s*"[^"]*"[,\s]*', '', text)
        text = re.sub(r'"id":\s*"[a-f0-9_-]+"[,\s]*', '', text)
        return text
    
    def clean_whitespace(self, text: str) -> str:
        """Remove excessive whitespace while preserving paragraph structure."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def split_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        Split text into chunks preserving semantic units (paragraphs).
        """
        if not text:
            return []
        
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def deduplicate(self, chunks: List[str]) -> List[str]:
        """Remove exact duplicate chunks."""
        seen = set()
        unique = []
        for chunk in chunks:
            if chunk not in seen:
                seen.add(chunk)
                unique.append(chunk)
        return unique
    
    def process_file(self, file_path: Path) -> Dict:
        """Process a single log file and return pruned data with metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_text = f.read()
        except Exception as e:
            return {'error': f'Failed to read {file_path}: {str(e)}'}
        
        original_size = len(original_text)
        
        pruned_text = original_text
        pruned_text = self.remove_timestamps(pruned_text)
        pruned_text = self.remove_tool_calls(pruned_text)
        pruned_text = self.remove_metadata(pruned_text)
        pruned_text = self.clean_whitespace(pruned_text)
        
        chunks = self.split_into_chunks(pruned_text)
        unique_chunks = self.deduplicate(chunks)
        final_text = '\n\n'.join(unique_chunks)
        
        pruned_size = len(final_text)
        compression_ratio = original_size / pruned_size if pruned_size > 0 else 0
        
        return {
            'pruned_text': final_text,
            'source': str(file_path),
            'original_size': original_size,
            'pruned_size': pruned_size,
            'compression_ratio': round(compression_ratio, 2),
            'chunks_count': len(unique_chunks),
            'processed_at': datetime.now().isoformat()
        }
    
    def process_directory(self, dir_path: Path, pattern: str = "*.log") -> List[Dict]:
        """Process all log files in a directory."""
        results = []
        log_files = list(dir_path.glob(pattern))
        
        if not log_files:
            print(f"No log files found matching '{pattern}' in {dir_path}")
            return results
        
        for log_file in log_files:
            print(f"Processing: {log_file.name}")
            result = self.process_file(log_file)
            results.append(result)
        
        return results
    
    def save_results(self, results: List[Dict], output_dir: Path):
        """Save pruned results as JSON files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, result in enumerate(results):
            if 'error' in result:
                print(f"⚠️  {result['error']}")
                continue
            
            source_name = Path(result['source']).stem
            output_file = output_dir / f"pruned_{source_name}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            
            print(f"✅ Saved: {output_file.name}")
            print(f"   Original: {result['original_size']} bytes → Pruned: {result['pruned_size']} bytes")
            print(f"   Compression ratio: {result['compression_ratio']}x")


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli_pruner.py <input_directory> [output_directory]")
        print("Example: python cli_pruner.py ~/.logs/sessions/General ./output")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1]).expanduser()
    output_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "./pruned_logs")
    
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    pruner = CliPruner()
    results = pruner.process_directory(input_dir)
    pruner.save_results(results, output_dir)
    
    if results:
        total_original = sum(r.get('original_size', 0) for r in results)
        total_pruned = sum(r.get('pruned_size', 0) for r in results)
        avg_compression = total_original / total_pruned if total_pruned > 0 else 0
        
        print(f"\n📊 Summary:")
        print(f"   Files processed: {len(results)}")
        print(f"   Total original: {total_original} bytes")
        print(f"   Total pruned: {total_pruned} bytes")
        print(f"   Average compression ratio: {avg_compression:.2f}x")


if __name__ == "__main__":
    main()
