#!/usr/bin/env python3
"""
Document Deduplication Engine
Uses BM25 + content hashing + semantic similarity for efficient deduplication
"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Set, Tuple, Optional
import re
from datetime import datetime

# For BM25 implementation (lightweight)
import math


@dataclass
class Document:
    """Represents a document in the catalog"""
    doc_id: str
    path: str
    filename: str
    content: str
    size_bytes: int
    file_type: str
    content_hash: str = ""
    token_count: int = 0
    dedup_group_id: Optional[str] = None
    is_primary: bool = False
    
    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self.compute_hash()
        if self.token_count == 0:
            self.token_count = len(self.tokenize())
    
    def compute_hash(self) -> str:
        """Compute SHA256 hash of content"""
        return hashlib.sha256(self.content.encode()).hexdigest()
    
    def tokenize(self) -> List[str]:
        """Simple tokenization for BM25"""
        text = self.content.lower()
        # Remove special characters, keep alphanumeric and whitespace
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split on whitespace and filter
        tokens = [t for t in text.split() if len(t) > 1]
        return tokens
    
    def get_ngrams(self, n: int = 3) -> Set[str]:
        """Get n-grams for similarity matching"""
        tokens = self.tokenize()
        ngrams = set()
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i+n])
            ngrams.add(ngram)
        return ngrams


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate documents"""
    group_id: str
    primary_doc_id: str
    duplicates: List[str] = field(default_factory=list)
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    dup_type: str = "unknown"  # exact, near_exact, overlapping, versions
    confidence: float = 0.0


class BM25:
    """Lightweight BM25 implementation for document similarity"""
    
    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.n_docs = len(corpus)
        
        # Compute IDF
        self.doc_freqs = defaultdict(int)
        for doc in corpus:
            unique_tokens = set(doc)
            for token in unique_tokens:
                self.doc_freqs[token] += 1
        
        # Average document length
        self.avg_doc_len = sum(len(doc) for doc in corpus) / max(1, self.n_docs)
    
    def get_score(self, query_idx: int, doc_idx: int) -> float:
        """Calculate BM25 score between query and document"""
        if query_idx >= len(self.corpus) or doc_idx >= len(self.corpus):
            return 0.0
        
        query_tokens = self.corpus[query_idx]
        doc = self.corpus[doc_idx]
        doc_len = len(doc)
        
        score = 0.0
        for token in set(query_tokens):
            token_count = doc.count(token)
            if token_count == 0:
                continue
            
            idf = math.log(1 + (self.n_docs - self.doc_freqs[token] + 0.5) / 
                          (self.doc_freqs[token] + 0.5))
            
            tf = (token_count * (self.k1 + 1)) / (
                token_count + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
            )
            
            score += idf * tf
        
        return score


def compute_jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Compute Jaccard similarity between two sets"""
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / max(1, union)


def compute_overlap_percentage(tokens1: List[str], tokens2: List[str]) -> float:
    """Compute content overlap percentage"""
    if not tokens1 or not tokens2:
        return 0.0
    
    set1 = set(tokens1)
    set2 = set(tokens2)
    intersection = len(set1 & set2)
    min_len = min(len(set1), len(set2))
    
    if min_len == 0:
        return 0.0
    return (intersection / min_len) * 100


class DeduplicationEngine:
    """Main deduplication engine"""
    
    def __init__(self, doc_dirs: List[str], min_doc_size: int = 100):
        self.doc_dirs = doc_dirs
        self.min_doc_size = min_doc_size
        self.documents: Dict[str, Document] = {}
        self.duplicate_groups: Dict[str, DuplicateGroup] = {}
        self.hash_index: Dict[str, List[str]] = defaultdict(list)  # hash -> doc_ids
        self.ngram_index: Dict[str, Set[str]] = defaultdict(set)  # ngram -> doc_ids
    
    def load_documents(self) -> int:
        """Load all documents from configured directories"""
        doc_id = 0
        supported_extensions = {'.md', '.txt', '.json', '.yaml', '.yml', '.py', '.js'}
        
        for base_dir in self.doc_dirs:
            if not os.path.exists(base_dir):
                continue
            
            for root, dirs, files in os.walk(base_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    ext = Path(filename).suffix.lower()
                    
                    if ext not in supported_extensions:
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if len(content) < self.min_doc_size:
                            continue
                        
                        rel_path = os.path.relpath(file_path, base_dir)
                        doc_id_str = f"doc_{doc_id}"
                        
                        doc = Document(
                            doc_id=doc_id_str,
                            path=file_path,
                            filename=filename,
                            content=content,
                            size_bytes=len(content),
                            file_type=ext
                        )
                        
                        self.documents[doc_id_str] = doc
                        self.hash_index[doc.content_hash].append(doc_id_str)
                        
                        doc_id += 1
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        return len(self.documents)
    
    def build_ngram_index(self, n: int = 3):
        """Build n-gram index for fast similarity search"""
        for doc_id, doc in self.documents.items():
            ngrams = doc.get_ngrams(n)
            for ngram in ngrams:
                self.ngram_index[ngram].add(doc_id)
    
    def find_exact_duplicates(self) -> List[DuplicateGroup]:
        """Find documents with identical content"""
        groups = []
        processed_hashes = set()
        
        for content_hash, doc_ids in self.hash_index.items():
            if len(doc_ids) <= 1:
                continue
            if content_hash in processed_hashes:
                continue
            
            processed_hashes.add(content_hash)
            group_id = f"exact_dup_{len(groups)}"
            
            # Select primary as oldest by filename
            sorted_docs = sorted(
                [self.documents[did] for did in doc_ids],
                key=lambda d: (d.filename, d.size_bytes)
            )
            
            primary = sorted_docs[0]
            duplicates = doc_ids.copy()
            duplicates.remove(primary.doc_id)
            
            group = DuplicateGroup(
                group_id=group_id,
                primary_doc_id=primary.doc_id,
                duplicates=duplicates,
                similarity_scores={did: 1.0 for did in duplicates},
                dup_type="exact",
                confidence=1.0
            )
            
            groups.append(group)
        
        return groups
    
    def find_near_duplicates(self, threshold: float = 0.95) -> List[DuplicateGroup]:
        """Find near-duplicate documents using BM25"""
        groups = []
        doc_ids = list(self.documents.keys())
        
        if len(doc_ids) < 2:
            return groups
        
        # Prepare corpus for BM25
        corpus = [self.documents[did].tokenize() for did in doc_ids]
        bm25 = BM25(corpus)
        
        processed_pairs = set()
        group_counter = 0
        
        for i, doc_id1 in enumerate(doc_ids):
            doc1 = self.documents[doc_id1]
            
            # Skip if already in a group
            if doc1.dedup_group_id:
                continue
            
            similar_docs = [(doc_id1, 1.0)]
            
            for j, doc_id2 in enumerate(doc_ids):
                if i >= j:
                    continue
                
                pair_key = (min(i, j), max(i, j))
                if pair_key in processed_pairs:
                    continue
                
                doc2 = self.documents[doc_id2]
                if doc2.dedup_group_id:
                    continue
                
                # Calculate BM25 score
                score1 = bm25.get_score(i, j)
                score2 = bm25.get_score(j, i)
                avg_score = (score1 + score2) / 2
                
                # Normalize to 0-1
                normalized_score = min(1.0, avg_score / 50.0)
                
                if normalized_score >= threshold:
                    similar_docs.append((doc_id2, normalized_score))
                    processed_pairs.add(pair_key)
            
            if len(similar_docs) > 1:
                group_id = f"near_dup_{group_counter}"
                primary = similar_docs[0][0]
                duplicates = [did for did, _ in similar_docs[1:]]
                scores = {did: score for did, score in similar_docs[1:]}
                
                group = DuplicateGroup(
                    group_id=group_id,
                    primary_doc_id=primary,
                    duplicates=duplicates,
                    similarity_scores=scores,
                    dup_type="near_exact",
                    confidence=min(1.0, avg(scores.values()) if scores else 0.95)
                )
                
                groups.append(group)
                group_counter += 1
        
        return groups
    
    def find_overlapping_content(self, threshold: float = 0.70) -> List[DuplicateGroup]:
        """Find documents with significant content overlap"""
        groups = []
        doc_ids = list(self.documents.keys())
        
        if len(doc_ids) < 2:
            return groups
        
        processed_pairs = set()
        group_counter = 0
        
        for i, doc_id1 in enumerate(doc_ids):
            doc1 = self.documents[doc_id1]
            if doc1.dedup_group_id:
                continue
            
            tokens1 = doc1.tokenize()
            overlapping = [(doc_id1, 100.0)]
            
            for j, doc_id2 in enumerate(doc_ids):
                if i >= j:
                    continue
                
                pair_key = (i, j)
                if pair_key in processed_pairs:
                    continue
                
                doc2 = self.documents[doc_id2]
                if doc2.dedup_group_id:
                    continue
                
                tokens2 = doc2.tokenize()
                overlap_pct = compute_overlap_percentage(tokens1, tokens2)
                
                if overlap_pct >= threshold * 100:
                    overlapping.append((doc_id2, overlap_pct))
                    processed_pairs.add(pair_key)
            
            if len(overlapping) > 1:
                group_id = f"overlap_dup_{group_counter}"
                primary = overlapping[0][0]
                duplicates = [did for did, _ in overlapping[1:]]
                scores = {did: pct / 100.0 for did, pct in overlapping[1:]}
                
                group = DuplicateGroup(
                    group_id=group_id,
                    primary_doc_id=primary,
                    duplicates=duplicates,
                    similarity_scores=scores,
                    dup_type="overlapping",
                    confidence=min(1.0, avg(scores.values()) if scores else 0.70)
                )
                
                groups.append(group)
                group_counter += 1
        
        return groups
    
    def deduplicate(self):
        """Run full deduplication pipeline"""
        print("Loading documents...")
        doc_count = self.load_documents()
        print(f"Loaded {doc_count} documents")
        
        print("\nBuilding n-gram index...")
        self.build_ngram_index()
        
        print("Finding exact duplicates...")
        exact_groups = self.find_exact_duplicates()
        print(f"Found {len(exact_groups)} exact duplicate groups")
        
        # Mark exact duplicates
        for group in exact_groups:
            for doc_id in [group.primary_doc_id] + group.duplicates:
                self.documents[doc_id].dedup_group_id = group.group_id
            self.documents[group.primary_doc_id].is_primary = True
            self.duplicate_groups[group.group_id] = group
        
        print("Finding near duplicates...")
        near_groups = self.find_near_duplicates(threshold=0.95)
        print(f"Found {len(near_groups)} near duplicate groups")
        
        for group in near_groups:
            for doc_id in [group.primary_doc_id] + group.duplicates:
                if not self.documents[doc_id].dedup_group_id:
                    self.documents[doc_id].dedup_group_id = group.group_id
            if not self.documents[group.primary_doc_id].is_primary:
                self.documents[group.primary_doc_id].is_primary = True
            if group.group_id not in self.duplicate_groups:
                self.duplicate_groups[group.group_id] = group
        
        print("Finding overlapping content...")
        overlap_groups = self.find_overlapping_content(threshold=0.70)
        print(f"Found {len(overlap_groups)} overlapping content groups")
        
        for group in overlap_groups:
            for doc_id in [group.primary_doc_id] + group.duplicates:
                if not self.documents[doc_id].dedup_group_id:
                    self.documents[doc_id].dedup_group_id = group.group_id
            if not self.documents[group.primary_doc_id].is_primary:
                self.documents[group.primary_doc_id].is_primary = True
            if group.group_id not in self.duplicate_groups:
                self.duplicate_groups[group.group_id] = group
        
        return len(self.duplicate_groups)


def avg(values: List[float]) -> float:
    """Calculate average"""
    return sum(values) / len(values) if values else 0.0


def generate_report(engine: DeduplicationEngine, output_file: str):
    """Generate deduplication report"""
    unique_docs = sum(1 for doc in engine.documents.values() if not doc.dedup_group_id)
    duplicate_docs = sum(1 for doc in engine.documents.values() if doc.dedup_group_id)
    total_docs = len(engine.documents)
    
    report_lines = [
        "# Document Deduplication Report",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Summary Statistics",
        f"- Total documents scanned: {total_docs}",
        f"- Unique documents: {unique_docs}",
        f"- Duplicate documents: {duplicate_docs}",
        f"- Duplicate groups found: {len(engine.duplicate_groups)}",
        f"- Potential reduction: {(duplicate_docs/total_docs*100):.1f}% if all duplicates removed",
        "",
        "## Deduplication Groups",
        "",
    ]
    
    for group_id, group in sorted(engine.duplicate_groups.items()):
        primary_doc = engine.documents[group.primary_doc_id]
        report_lines.extend([
            f"### Group: {group_id}",
            f"- Type: {group.dup_type}",
            f"- Confidence: {group.confidence:.1%}",
            f"- Primary: {primary_doc.filename} ({primary_doc.size_bytes} bytes)",
            f"- Duplicates: {len(group.duplicates)}",
        ])
        
        for dup_id in group.duplicates:
            dup_doc = engine.documents[dup_id]
            similarity = group.similarity_scores.get(dup_id, 0.0)
            report_lines.append(
                f"  - {dup_doc.filename} ({dup_doc.size_bytes} bytes) - "
                f"Similarity: {similarity:.1%}"
            )
        
        report_lines.append("")
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    return report_lines


def generate_recommendations(engine: DeduplicationEngine, output_file: str):
    """Generate deduplication recommendations"""
    recommendations = {
        "summary": {
            "total_groups": len(engine.duplicate_groups),
            "total_docs": len(engine.documents),
            "unique_docs": sum(1 for d in engine.documents.values() if not d.dedup_group_id),
            "duplicate_docs": sum(1 for d in engine.documents.values() if d.dedup_group_id),
            "potential_reduction_percent": (
                sum(1 for d in engine.documents.values() if d.dedup_group_id) / 
                len(engine.documents) * 100
            ),
            "estimated_space_savings_percent": (
                sum(1 for d in engine.documents.values() if d.dedup_group_id) * 100 /
                len(engine.documents)
            )
        },
        "actions": []
    }
    
    for group_id, group in sorted(engine.duplicate_groups.items()):
        primary = engine.documents[group.primary_doc_id]
        
        action = {
            "group_id": group_id,
            "type": group.dup_type,
            "confidence": group.confidence,
            "action": "DELETE" if group.dup_type == "exact" else "REVIEW_AND_MERGE",
            "keep": primary.filename,
            "keep_path": primary.path,
            "remove": []
        }
        
        for dup_id in group.duplicates:
            dup_doc = engine.documents[dup_id]
            action["remove"].append({
                "filename": dup_doc.filename,
                "path": dup_doc.path,
                "size_bytes": dup_doc.size_bytes,
                "similarity": group.similarity_scores.get(dup_id, 0.0)
            })
        
        recommendations["actions"].append(action)
    
    with open(output_file, 'w') as f:
        json.dump(recommendations, f, indent=2)
    
    return recommendations


def generate_catalog(engine: DeduplicationEngine, output_file: str):
    """Generate updated document catalog"""
    catalog = []
    
    for doc_id, doc in sorted(engine.documents.items()):
        catalog.append({
            "doc_id": doc.doc_id,
            "filename": doc.filename,
            "path": doc.path,
            "size_bytes": doc.size_bytes,
            "file_type": doc.file_type,
            "content_hash": doc.content_hash,
            "token_count": doc.token_count,
            "dedup_group_id": doc.dedup_group_id,
            "is_primary": doc.is_primary
        })
    
    with open(output_file, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    return len(catalog)


if __name__ == "__main__":
    # Configure document directories
    doc_dirs = [
        "/home/arcana-novai/Documents/xnai-foundation/expert-knowledge",
        "/home/arcana-novai/Documents/xnai-foundation/knowledge",
        "/home/arcana-novai/Documents/xnai-foundation/docs"
    ]
    
    # Create engine and run deduplication
    engine = DeduplicationEngine(doc_dirs, min_doc_size=100)
    dup_count = engine.deduplicate()
    
    print(f"\n✓ Deduplication complete: {dup_count} duplicate groups found")
    
    # Generate outputs
    print("Generating report...")
    report_file = "/tmp/dedup_report.md"
    generate_report(engine, report_file)
    print(f"✓ Report: {report_file}")
    
    print("Generating recommendations...")
    rec_file = "/tmp/dedup_recommendations.json"
    recommendations = generate_recommendations(engine, rec_file)
    print(f"✓ Recommendations: {rec_file}")
    
    print("Generating catalog...")
    cat_file = "/tmp/document_catalog.json"
    cat_count = generate_catalog(engine, cat_file)
    print(f"✓ Catalog: {cat_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("DEDUPLICATION SUMMARY")
    print("="*60)
    stats = recommendations["summary"]
    print(f"Total documents: {stats['total_docs']}")
    print(f"Unique documents: {stats['unique_docs']}")
    print(f"Duplicate documents: {stats['duplicate_docs']}")
    print(f"Duplicate groups: {stats['total_groups']}")
    print(f"Potential reduction: {stats['potential_reduction_percent']:.1f}%")
    print("="*60)
