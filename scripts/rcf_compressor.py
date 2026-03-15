#!/usr/bin/env python3
"""
RCF Compressor: Semantic Signal Extraction and Compression
Purpose: Multi-pass summarization to Atomic Gnosis Signals
Created: 2026-03-14
Author: Archon (validated by Copilot)

This module extracts semantic signals from text documents and compresses them
into Atomic Gnosis Signals following the Maat Ideals framework.

Extraction Schema: [Fact], [Axiom], [Pointer]
Target Compression Ratios:
  - Session logs: 10:1 reduction
  - Technical documentation: 3:1 reduction
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class AtomicSignal:
    """Represents a compressed semantic signal."""
    fact: str
    axiom: str
    pointer: str

    def to_dict(self) -> Dict:
        return asdict(self)


class RCFCompressor:
    """
    RCF Compressor: Reduces documents to Atomic Gnosis Signals.
    
    Axiom mapping based on Maat Ideals:
    - A1_AUTONOMY: Ideals 32, 40, 41 (inner guidance, integrity, abilities)
    - A2_SINCERITY: Ideals 7, 9, 37 (truth, speech, good intent)
    - A3_BALANCE: Ideals 18, 20, 25 (emotions, purity, harmony)
    - A4_REVERENCE: Ideals 8, 13 (altars, animals)
    - A5_PEACE: Ideals 3, 12, 30 (peaceful, relating in peace, respect)
    - A6_INTEGRITY: Ideals 14, 40, 41 (trustworthiness, integrity, abilities)
    - A7_ALETHIA_GROUNDING: Ideals 7, 20, 36 (truth, purity, keeping waters pure)
    """

    AXIOM_KEYWORDS = {
        "A1_AUTONOMY": [
            "autonomy", "independent", "sovereignty", "self-governing",
            "freedom", "choice", "local", "self-directed", "agency"
        ],
        "A2_SINCERITY": [
            "truth", "sincere", "honest", "genuine", "authentic",
            "transparent", "frank", "candid", "straightforward"
        ],
        "A3_BALANCE": [
            "balance", "equilibrium", "harmony", "moderation",
            "symmetry", "stability", "poise", "measured"
        ],
        "A4_REVERENCE": [
            "respect", "sacred", "reverent", "honor", "dignity",
            "esteem", "venerate", "revere", "reverence"
        ],
        "A5_PEACE": [
            "peace", "peaceful", "harmony", "tranquil", "calm",
            "serene", "quiet", "restful", "non-violent"
        ],
        "A6_INTEGRITY": [
            "integrity", "trustworthy", "reliable", "consistent",
            "honest", "dependable", "wholeness", "principled"
        ],
        "A7_ALETHIA_GROUNDING": [
            "grounding", "ground truth", "factual", "empirical",
            "evidence", "data", "measurement", "concrete", "verifiable"
        ],
    }

    SEMANTIC_SEPARATORS = r"[.!?\n]"

    def __init__(self, source_path: Optional[str] = None):
        """Initialize RCF Compressor."""
        self.source_path = source_path
        self.original_length = 0
        self.compressed_length = 0
        self.compression_ratio = 0.0

    def _split_into_units(self, text: str) -> List[str]:
        """
        Split text into semantic units (sentences/paragraphs).
        Returns non-empty, stripped strings.
        For logs: extract only distinct information patterns.
        For docs: extract substantive paragraphs.
        """
        sentences = re.split(self.SEMANTIC_SEPARATORS, text)
        units = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
        
        # Aggressive deduplication for repetitive content (logs)
        # Keep only first occurrence of similar patterns
        seen = {}
        deduplicated = []
        for unit in units:
            # Extract key part for comparison (first 40 chars, lowercase)
            key = unit[:40].lower()
            key_words = tuple(sorted(set(re.findall(r'\w+', key))))
            
            # Skip if we've seen a similar pattern
            should_add = True
            for existing_key in list(seen.keys()):
                existing_words = set(existing_key)
                new_words = set(key_words)
                # If >60% word overlap, skip this unit
                if existing_words and new_words:
                    overlap = len(existing_words & new_words) / len(existing_words | new_words)
                    if overlap > 0.6:
                        should_add = False
                        break
            
            if should_add:
                seen[key_words] = True
                deduplicated.append(unit)
        
        return deduplicated

    def _extract_fact(self, unit: str) -> str:
        """
        Extract a distilled fact from a semantic unit.
        Creates ultra-concise atomic claim.
        """
        text = unit.strip()
        text = re.sub(r"\s+", " ", text)
        
        # Remove timestamps and log metadata
        text = re.sub(r"\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}[^\]]*\]", "", text)
        text = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^\s]*", "", text)
        text = re.sub(r"\(retry\s+\d+/\d+\)", "", text)
        
        # Remove log level prefixes
        text = re.sub(r"\b(DEBUG|INFO|WARN|WARNING|ERROR|TRACE):\s*", "", text, flags=re.IGNORECASE)
        
        # Extract meaningful words (remove articles, prepositions when possible)
        # But keep enough for understanding
        words = text.split()
        if len(words) > 12:
            # Keep only critical content - first few words and final outcome
            keywords = [w for w in words if len(w) > 3 and w.lower() not in {
                'with', 'from', 'that', 'this', 'have', 'been', 'were', 'also'
            }]
            if keywords:
                text = ' '.join(keywords[:8])
        
        text = re.sub(r"\s+", " ", text).strip()
        return text[:100] if text else unit[:100]

    def _detect_axiom(self, unit: str) -> str:
        """
        Detect which Maat Ideal/Axiom applies to this unit.
        Uses keyword matching with priority ordering and context awareness.
        """
        text_lower = unit.lower()
        
        # Score each axiom
        scores = {}
        for axiom, keywords in self.AXIOM_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Exact word match scores higher
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    score += 2
                elif keyword in text_lower:
                    score += 1
            if score > 0:
                scores[axiom] = score
        
        if not scores:
            # Default to grounding for factual content
            if any(word in text_lower for word in ['error', 'failed', 'success', 'completed', 'status', 'log']):
                return "A7_ALETHIA_GROUNDING"
            else:
                return "A2_SINCERITY"
        
        # Return highest scoring axiom
        best_axiom = max(scores.items(), key=lambda x: x[1])[0]
        return best_axiom

    def _format_pointer(self, line_number: int = 0) -> str:
        """
        Format pointer as file_path:line_number.
        """
        if self.source_path:
            return f"{self.source_path}:{line_number + 1}"
        return f"input:{line_number + 1}"

    def compress(
        self,
        text: str,
        source_path: Optional[str] = None
    ) -> Tuple[List[AtomicSignal], Dict[str, float]]:
        """
        Compress input text to Atomic Gnosis Signals.
        
        Compression ratio measures semantic reduction:
        - original_tokens = word count in source
        - compressed_tokens = words in all facts
        - ratio = original_tokens / compressed_tokens
        
        Args:
            text: Input text to compress
            source_path: Optional source file path for pointers
            
        Returns:
            Tuple of (signals, metrics)
        """
        if source_path:
            self.source_path = source_path
        
        self.original_length = len(text)
        
        if not text.strip():
            return [], {"original_chars": 0, "compressed_tokens": 0, "ratio": 0.0}
        
        # Count original tokens (words)
        original_words = len(text.split())
        
        units = self._split_into_units(text)
        signals = []
        
        for idx, unit in enumerate(units):
            if len(unit) < 5:
                continue
            
            fact = self._extract_fact(unit)
            axiom = self._detect_axiom(unit)
            pointer = self._format_pointer(idx)
            
            signal = AtomicSignal(fact=fact, axiom=axiom, pointer=pointer)
            signals.append(signal)
        
        # Count compressed tokens (only the fact content)
        compressed_words = sum(len(s.fact.split()) for s in signals)
        
        if compressed_words > 0:
            self.compression_ratio = original_words / compressed_words
        else:
            self.compression_ratio = 0.0
        
        metrics = {
            "original_chars": self.original_length,
            "original_tokens": original_words,
            "compressed_tokens": compressed_words,
            "ratio": self.compression_ratio,
            "signal_count": len(signals),
        }
        
        return signals, metrics

    def process_file(self, file_path: str) -> Tuple[List[AtomicSignal], Dict]:
        """
        Process a file and return signals with metrics.
        
        Args:
            file_path: Path to file to process
            
        Returns:
            Tuple of (signals, metrics)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        
        try:
            relative_path = str(path.relative_to(Path.cwd()))
        except ValueError:
            relative_path = str(path)
        
        return self.compress(text, source_path=relative_path)

    def batch_process(
        self,
        file_paths: List[str]
    ) -> Dict[str, Tuple[List[AtomicSignal], Dict]]:
        """
        Process multiple files.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            Dictionary mapping file paths to (signals, metrics) tuples
        """
        results = {}
        for file_path in file_paths:
            try:
                signals, metrics = self.process_file(file_path)
                results[file_path] = (signals, metrics)
            except Exception as e:
                results[file_path] = ([], {"error": str(e)})
        return results


def output_signals(
    signals: List[AtomicSignal],
    output_file: Optional[str] = None
) -> str:
    """
    Output signals as JSON.
    
    Args:
        signals: List of AtomicSignal objects
        output_file: Optional file path to write output
        
    Returns:
        JSON string
    """
    json_output = json.dumps(
        [s.to_dict() for s in signals],
        indent=2
    )
    
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_output)
    
    return json_output


def main():
    """Example usage."""
    compressor = RCFCompressor()
    
    example_text = """
    Local processing improves user autonomy and data privacy.
    Systems must maintain integrity through honest reporting.
    Balance between performance and resource usage is essential.
    Truth in documentation requires factual, verifiable claims.
    """
    
    signals, metrics = compressor.compress(example_text, "example.txt")
    
    print("=" * 60)
    print("RCF COMPRESSOR - Example Output")
    print("=" * 60)
    print(f"\nOriginal: {metrics['original_tokens']} tokens")
    print(f"Compressed: {metrics['compressed_tokens']} tokens (facts)")
    print(f"Compression Ratio: {metrics['ratio']:.2f}:1\n")
    print(output_signals(signals))


if __name__ == "__main__":
    main()
