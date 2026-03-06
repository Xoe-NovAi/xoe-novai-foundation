#!/usr/bin/env python3
"""
Xoe-NovAi Zotero Metadata Injector
==================================

Reads Better BibTeX (.bib) exports from 'library/incoming' and prepends
scholarly metadata to the ingested Markdown documents.

Ensures LLMs have access to grounded citations (DOI, Author, Year).
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("zotero_injector")

class ZoteroInjector:
    def __init__(self, bib_path: str = "library/incoming/library.bib"):
        self.bib_path = Path(bib_path)
        self.metadata_cache: Dict[str, Dict[str, str]] = {}
        if self.bib_path.exists():
            self._parse_bib()

    def _parse_bib(self):
        """Simple BibTeX parser for Better BibTeX exports."""
        try:
            content = self.bib_path.read_text(encoding="utf-8")
            # Match @type{citekey, ...}
            entries = re.finditer(r'@(\w+)\{([^,]+),([^@]+)\}', content, re.DOTALL)
            for entry in entries:
                citekey = entry.group(2).strip()
                fields_raw = entry.group(3)
                fields = {}
                # Match key = {value} or key = "value"
                field_matches = re.finditer(r'(\w+)\s*=\s*[\{"]([^"\}]+)[\}"],?', fields_raw)
                for f in field_matches:
                    fields[f.group(1).lower()] = f.group(2)
                self.metadata_cache[citekey] = fields
            logger.info(f"Loaded {len(self.metadata_cache)} entries from {self.bib_path.name}")
        except Exception as e:
            logger.error(f"Failed to parse BibTeX: {e}")

    def inject_metadata(self, markdown_content: str, citekey: str) -> str:
        """Prepend metadata block to markdown."""
        if citekey not in self.metadata_cache:
            return markdown_content
        
        meta = self.metadata_cache[citekey]
        header = "---
"
        header += f"title: "{meta.get('title', 'Unknown')}"
"
        header += f"author: "{meta.get('author', 'Unknown')}"
"
        header += f"year: {meta.get('year', 'Unknown')}
"
        if 'doi' in meta:
            header += f"doi: {meta['doi']}
"
        header += f"citekey: {citekey}
"
        header += "---

"
        
        return header + markdown_content

if __name__ == "__main__":
    # Test execution
    injector = ZoteroInjector()
    if injector.metadata_cache:
        test_key = list(injector.metadata_cache.keys())[0]
        print(f"Test Injection for {test_key}:")
        print(injector.inject_metadata("# Sample Document", test_key))
