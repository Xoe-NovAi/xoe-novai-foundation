#!/usr/bin/env python3
"""
Xoe-NovAi Documentation Indexer
Automated indexing system for comprehensive documentation management.

Features:
- Full metadata extraction from YAML frontmatter
- Content analysis (word count, headings, links, code blocks)
- Relationship mapping between documents
- Incremental index updates
- Search index generation

Author: Xoe-NovAi Documentation Enhancement Team
Date: January 27, 2026
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import hashlib
from dataclasses import dataclass, asdict


@dataclass
class DocumentMetadata:
    """Structured document metadata."""
    file_path: str
    file_size: int
    last_modified: str
    word_count: int
    line_count: int
    title: str = ""
    headings: List[str] = None
    links: List[Dict[str, str]] = None
    code_blocks: int = 0
    tables: int = 0
    frontmatter: Dict[str, Any] = None

    def __post_init__(self):
        if self.headings is None:
            self.headings = []
        if self.links is None:
            self.links = []
        if self.frontmatter is None:
            self.frontmatter = {}


class DocsIndexer:
    """Comprehensive documentation indexing system."""

    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.index_file = docs_root / "index.json"
        self.search_index_file = docs_root / "search_index.json"
        self.metadata_cache: Dict[str, DocumentMetadata] = {}
        self.index_hash = None

        # Regex patterns for content analysis
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.code_block_pattern = re.compile(r'```[\s\S]*?```')
        self.table_pattern = re.compile(r'^\|.*\|.*\|$', re.MULTILINE)

    def build_full_index(self) -> Dict[str, Any]:
        """
        Build comprehensive index of all documentation.

        Returns:
            Dict containing:
            - metadata: Index metadata and statistics
            - documents: Document metadata by relative path
            - relationships: Document relationship mappings
            - search_terms: Inverted search index
        """

        print("🔍 Building comprehensive documentation index...")

        index = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_files": 0,
                "categories": {},
                "tags": set(),
                "authors": set(),
                "index_hash": None
            },
            "documents": {},
            "relationships": {},
            "search_terms": {}
        }

        # Index all markdown files
        processed_files = 0
        for md_file in self.docs_root.rglob("*.md"):
            if self._should_index(md_file):
                doc_metadata = self._index_document(md_file)
                if doc_metadata:
                    rel_path = str(md_file.relative_to(self.docs_root))
                    # Convert to dict and handle datetime objects
                    doc_dict = asdict(doc_metadata)
                    doc_dict['last_modified'] = doc_dict['last_modified']  # Already ISO string
                    index["documents"][rel_path] = doc_dict

                    # Update category counts
                    category = doc_metadata.frontmatter.get("category", "uncategorized")
                    index["metadata"]["categories"][category] = \
                        index["metadata"]["categories"].get(category, 0) + 1

                    # Collect tags and authors
                    tags = doc_metadata.frontmatter.get("tags", [])
                    index["metadata"]["tags"].update(tags)

                    authors = doc_metadata.frontmatter.get("authors", [])
                    if isinstance(authors, list):
                        for author in authors:
                            if isinstance(author, dict):
                                index["metadata"]["authors"].add(author.get("name", ""))
                            else:
                                index["metadata"]["authors"].add(str(author))

                    processed_files += 1
                    if processed_files % 10 == 0:
                        print(f"📄 Processed {processed_files} files...")

        index["metadata"]["total_files"] = len(index["documents"])
        index["metadata"]["tags"] = list(index["metadata"]["tags"])
        index["metadata"]["authors"] = list(index["metadata"]["authors"])

        # Generate index hash for change detection - simplified approach
        try:
            index_content = json.dumps(index["documents"], sort_keys=True, default=str)
        except Exception as e:
            print(f"⚠️ JSON serialization issue: {e}, using simplified approach")
            # Fallback: convert everything to strings
            def safe_serialize(obj):
                if isinstance(obj, dict):
                    return {k: safe_serialize(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [safe_serialize(item) for item in obj]
                else:
                    return str(obj)

            safe_docs = safe_serialize(index["documents"])
            index_content = json.dumps(safe_docs, sort_keys=True)
        index["metadata"]["index_hash"] = hashlib.sha256(index_content.encode()).hexdigest()

        # Build search index
        print("🔍 Building search index...")
        index["search_terms"] = self._build_search_index(index["documents"])

        # Build relationship map
        print("🔗 Building relationship maps...")
        index["relationships"] = self._build_relationships(index["documents"])

        print(f"✅ Index complete: {index['metadata']['total_files']} documents indexed")
        return index

    def _should_index(self, file_path: Path) -> bool:
        """Determine if a file should be indexed."""
        # Skip archive files
        if "archive" in str(file_path):
            return False

        # Skip hidden files and directories
        if file_path.name.startswith('.'):
            return False

        # Only index markdown files
        if file_path.suffix != '.md':
            return False

        return True

    def _index_document(self, file_path: Path) -> Optional[DocumentMetadata]:
        """Extract comprehensive metadata from document."""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            frontmatter = {}
            body = content

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        body = parts[2]
                    except yaml.YAMLError as e:
                        print(f"⚠️ YAML parsing error in {file_path}: {e}")
                        frontmatter = {}

            # Create metadata object
            metadata = DocumentMetadata(
                file_path=str(file_path.relative_to(self.docs_root)),
                file_size=file_path.stat().st_size,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                word_count=len(body.split()),
                line_count=len(body.split('\n')),
                title=self._extract_title(body),
                headings=self._extract_headings(body),
                links=self._extract_links(body),
                code_blocks=len(self.code_block_pattern.findall(body)),
                tables=len(self.table_pattern.findall(body)),
                frontmatter=frontmatter
            )

            return metadata

        except Exception as e:
            print(f"❌ Error indexing {file_path}: {e}")
            return None

    def _extract_title(self, content: str) -> str:
        """Extract document title from content."""
        # Look for title in frontmatter first
        # Then check for # heading
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled Document"

    def _extract_headings(self, content: str) -> List[str]:
        """Extract all headings from document."""
        headings = []
        for match in self.heading_pattern.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append(title)
        return headings

    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract all links from document."""
        links = []
        for match in self.link_pattern.finditer(content):
            links.append({
                "text": match.group(1),
                "target": match.group(2),
                "type": "internal" if not match.group(2).startswith(('http://', 'https://')) else "external"
            })
        return links

    def _build_search_index(self, documents: Dict) -> Dict[str, List[str]]:
        """Build inverted search index for full-text search."""

        search_index = {}

        for doc_path, metadata in documents.items():
            # Index title
            title = metadata.get("title", "").lower()
            self._add_to_search_index(search_index, title, doc_path)

            # Index tags
            for tag in metadata.get("tags", []):
                self._add_to_search_index(search_index, str(tag).lower(), doc_path)

            # Index category
            category = metadata.get("category", "").lower()
            self._add_to_search_index(search_index, category, doc_path)

            # Index headings
            for heading in metadata.get("headings", []):
                self._add_to_search_index(search_index, heading.lower(), doc_path)

            # Index author names
            for author in metadata.get("authors", []):
                if isinstance(author, dict):
                    author_name = author.get("name", "")
                else:
                    author_name = str(author)
                self._add_to_search_index(search_index, author_name.lower(), doc_path)

        return search_index

    def _add_to_search_index(self, search_index: Dict, term: str, doc_path: str):
        """Add term to inverted search index."""
        # Simple tokenization (split on spaces and punctuation)
        tokens = re.findall(r'\b\w+\b', term.lower())

        for token in tokens:
            if len(token) > 2:  # Skip very short tokens
                if token not in search_index:
                    search_index[token] = []
                if doc_path not in search_index[token]:
                    search_index[token].append(doc_path)

    def _build_relationships(self, documents: Dict) -> Dict[str, List[str]]:
        """Build document relationship map."""

        relationships = {}

        for doc_path, metadata in documents.items():
            relationships[doc_path] = []

            # Find related documents based on tags, category, etc.
            for other_path, other_metadata in documents.items():
                if other_path != doc_path:
                    if self._are_related(metadata, other_metadata):
                        relationships[doc_path].append(other_path)

        return relationships

    def _are_related(self, doc1: Dict, doc2: Dict) -> bool:
        """Determine if two documents are related."""

        # Same category
        if doc1.get("category") == doc2.get("category"):
            return True

        # Shared tags
        tags1 = set(doc1.get("tags", []))
        tags2 = set(doc2.get("tags", []))
        if tags1 & tags2:
            return True

        # Shared authors
        authors1 = set()
        authors2 = set()

        for author in doc1.get("authors", []):
            if isinstance(author, dict):
                authors1.add(author.get("name", ""))
            else:
                authors1.add(str(author))

        for author in doc2.get("authors", []):
            if isinstance(author, dict):
                authors2.add(author.get("name", ""))
            else:
                authors2.add(str(author))

        if authors1 & authors2:
            return True

        return False

    def search(self, query: str, filters: Dict = None, limit: int = 20) -> List[Dict]:
        """
        Search documentation with advanced filtering.

        Args:
            query: Search query string
            filters: Optional filters (category, status, etc.)
            limit: Maximum results to return

        Returns:
            List of search results with relevance scores
        """

        # Load current index if not cached
        if not self.metadata_cache:
            self._load_index()

        results = []
        query_terms = query.lower().split()

        for doc_path, metadata in self.metadata_cache.items():
            score = self._calculate_search_score(metadata, query_terms, filters)
            if score > 0:
                results.append({
                    "path": doc_path,
                    "metadata": metadata,
                    "score": score,
                    "highlights": self._generate_highlights(metadata, query_terms)
                })

        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:limit]

    def _calculate_search_score(self, metadata: DocumentMetadata, query_terms: List[str], filters: Dict = None) -> float:
        """Calculate relevance score for search results."""

        score = 0

        # Apply filters first
        if filters:
            for key, value in filters.items():
                if key == "category" and metadata.frontmatter.get("category") != value:
                    return 0
                elif key == "status" and metadata.frontmatter.get("status") != value:
                    return 0
                elif key == "tags" and value not in metadata.frontmatter.get("tags", []):
                    return 0

        # Title matches (highest weight)
        title = metadata.title.lower()
        for term in query_terms:
            if term in title:
                score += 10

        # Tag matches
        tags = [str(tag).lower() for tag in metadata.frontmatter.get("tags", [])]
        for term in query_terms:
            if any(term in tag for tag in tags):
                score += 5

        # Category matches
        category = metadata.frontmatter.get("category", "").lower()
        for term in query_terms:
            if term in category:
                score += 3

        # Heading matches
        for heading in metadata.headings:
            heading_lower = heading.lower()
            for term in query_terms:
                if term in heading_lower:
                    score += 2

        # Author matches
        for author in metadata.frontmatter.get("authors", []):
            if isinstance(author, dict):
                author_name = author.get("name", "")
            else:
                author_name = str(author)
            author_lower = author_name.lower()
            for term in query_terms:
                if term in author_lower:
                    score += 1

        return score

    def _generate_highlights(self, metadata: DocumentMetadata, query_terms: List[str]) -> List[str]:
        """Generate search result highlights."""
        highlights = []

        # Title highlights
        if any(term in metadata.title.lower() for term in query_terms):
            highlights.append(f"**{metadata.title}**")

        # Tag highlights
        matching_tags = [
            tag for tag in metadata.frontmatter.get("tags", [])
            if any(term in str(tag).lower() for term in query_terms)
        ]
        if matching_tags:
            highlights.extend([f"🏷️ {tag}" for tag in matching_tags])

        return highlights[:3]  # Limit to 3 highlights

    def _load_index(self):
        """Load index from disk into cache."""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    index_data = json.load(f)

                # Convert back to DocumentMetadata objects
                for path, data in index_data.get("documents", {}).items():
                    self.metadata_cache[path] = DocumentMetadata(**data)

        except Exception as e:
            print(f"⚠️ Error loading index: {e}")

    def save_index(self, index: Dict):
        """Save index to disk."""
        try:
            # Use default=str to handle all non-serializable objects
            with open(self.index_file, 'w') as f:
                json.dump(index, f, indent=2, default=str)

            # Save search index separately for faster loading
            with open(self.search_index_file, 'w') as f:
                json.dump(index.get("search_terms", {}), f, indent=2, default=str)

            print(f"💾 Index saved: {self.index_file}")
            print(f"💾 Search index saved: {self.search_index_file}")

        except Exception as e:
            print(f"❌ Error saving index: {e}")

    def is_index_stale(self) -> bool:
        """Check if index needs rebuilding."""
        try:
            if not self.index_file.exists():
                return True

            with open(self.index_file, 'r') as f:
                index_data = json.load(f)

            current_hash = index_data["metadata"].get("index_hash")
            if not current_hash:
                return True

            # Calculate current hash
            docs_content = ""
            for md_file in self.docs_root.rglob("*.md"):
                if self._should_index(md_file):
                    try:
                        with open(md_file, 'r') as f:
                            docs_content += f.read()
                    except:
                        pass

            new_hash = hashlib.sha256(docs_content.encode()).hexdigest()
            return current_hash != new_hash

        except Exception:
            return True


def main():
    """Main indexer execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Xoe-NovAi Documentation Indexer")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of index")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--filter", action="append", help="Search filters (key:value)")
    parser.add_argument("--limit", type=int, default=20, help="Maximum search results")

    args = parser.parse_args()

    docs_root = Path("docs/")
    indexer = DocsIndexer(docs_root)

    if args.search:
        # Search mode
        filters = {}
        if args.filter:
            for f in args.filter:
                if ":" in f:
                    key, value = f.split(":", 1)
                    filters[key] = value

        results = indexer.search(args.search, filters, args.limit)

        print(f"🔍 Search results for '{args.search}':")
        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            print(f"{i}. {result['path']} (score: {result['score']:.1f})")
            print(f"   Title: {metadata.title}")
            if result["highlights"]:
                print(f"   Highlights: {' | '.join(result['highlights'])}")
            print()

    else:
        # Index mode
        if not args.rebuild and not indexer.is_index_stale():
            print("✅ Index is up to date")
            return

        print("🔄 Building documentation index...")
        index = indexer.build_full_index()
        indexer.save_index(index)

        print("✅ Indexing complete!")


if __name__ == "__main__":
    main()
