#!/usr/bin/env python3
"""
NovAiBooK Synchronization Script
=================================
Syncs the offline library (books, manuals) into the Research Environment (JupyterLab) volume.
"""

import os
import shutil
import logging
from pathlib import Path

# Configuration
LIBRARY_SOURCE = Path("library")
RESEARCH_DEST = Path("research-environment/jupyterlab/library")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("novai_sync")

def sync_library():
    """Sync library files to research environment."""
    if not LIBRARY_SOURCE.exists():
        logger.error(f"Source library not found: {LIBRARY_SOURCE}")
        return

    logger.info(f"Syncing {LIBRARY_SOURCE} -> {RESEARCH_DEST}...")
    
    # Create destination if needed
    RESEARCH_DEST.mkdir(parents=True, exist_ok=True)

    # Use rsync-like logic (copy if newer)
    count = 0
    for root, dirs, files in os.walk(LIBRARY_SOURCE):
        rel_path = os.path.relpath(root, LIBRARY_SOURCE)
        dest_dir = RESEARCH_DEST / rel_path
        dest_dir.mkdir(exist_ok=True)

        for file in files:
            src_file = Path(root) / file
            dest_file = dest_dir / file

            if not dest_file.exists() or src_file.stat().st_mtime > dest_file.stat().st_mtime:
                shutil.copy2(src_file, dest_file)
                count += 1
                logger.debug(f"Synced: {file}")

    logger.info(f"Sync complete. {count} files updated.")

if __name__ == "__main__":
    sync_library()
