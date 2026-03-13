#!/usr/bin/env python3
"""
XNAi Stack Scribe
=================

Autonomous documentation crawler that indexes the Omega stack's own 
manuals, architectural guides, and code standards.

Workflow:
1. Scan docs/, expert-knowledge/, and library/ for markdown files.
2. Filter for significant manuals.
3. Enqueue curation tasks to the Agent Bus for summarization and vector indexing.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List
from XNAi_rag_app.core.agent_bus import AgentBusClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("stack_scribe")

# Targeted directories
DOC_PATHS = [
    "docs",
    "expert-knowledge",
    "library",
    "memory_bank"
]

class StackScribe:
    def __init__(self, agent_id: str = "script:stack_scribe:001"):
        self.agent_id = agent_id
        # Support both container and host paths
        self.paths = {
            "docs": os.getenv("DOCS_PATH", "docs"),
            "expert-knowledge": os.getenv("KNOWLEDGE_PATH", "expert-knowledge"),
            "library": os.getenv("LIBRARY_PATH", "library"),
            "memory_bank": os.getenv("MEMORY_BANK_PATH", "memory_bank")
        }

    async def scan_and_enqueue(self):
        """Scan documentation and send tasks to Agent Bus."""
        logger.info("🚀 Stack Scribe starting scan...")
        
        # 1. Connect to Agent Bus
        async with AgentBusClient(agent_did=self.agent_id) as bus:
            found_count = 0
            
            for label, doc_dir in self.paths.items():
                dir_path = Path(doc_dir)
                if not dir_path.exists():
                    logger.warning(f"⚠️ Directory not found: {label} at {dir_path}")
                    continue
                
                logger.info(f"Scanning {label} in {dir_path}...")
                
                # Recursively find all .md files
                for md_file in dir_path.rglob("*.md"):
                    # Ignore archives and hidden files
                    if "_archive" in str(md_file) or md_file.name.startswith("."):
                        continue
                        
                    logger.info(f"  Indexing: {md_file}")
                    
                    # 2. Enqueue Curation Task
                    # We send a 'local' source type task
                    payload = {
                        "source_type": "local",
                        "directory": str(md_file.parent),
                        "query": md_file.name, # Use filename as query to target specific file
                        "category": f"stack-doc-{doc_dir}",
                        "max_items": 1
                    }
                    
                    try:
                        task_id = await bus.send_task(
                            target_did="worker:library_curator:001",
                            task_type="curation_task",
                            payload=payload
                        )
                        logger.info(f"    ✅ Task queued: {task_id}")
                        found_count += 1
                    except Exception as e:
                        logger.error(f"    ❌ Failed to queue task for {rel_path}: {e}")

            logger.info(f"✨ Scan complete. Queued {found_count} documentation tasks.")

if __name__ == "__main__":
    scribe = StackScribe()
    asyncio.run(scribe.scan_and_enqueue())
