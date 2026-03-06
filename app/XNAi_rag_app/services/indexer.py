"""Index research directories and sync with Postgres/Vikunja."""

import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class ResearchIndexer:
    def __init__(self, base_path: Path = Path("research")):
        self.base = base_path

    def scan(self) -> List[Path]:
        """Return list of project directories."""
        if not self.base.exists():
            return []
        dirs = [p for p in self.base.iterdir() if p.is_dir()]
        logger.debug(f"Found {len(dirs)} research dirs")
        return dirs

    def update_database(self):
        for d in self.scan():
            meta = d / "meta.yaml"
            if not meta.exists():
                continue
            # parse meta and upsert into research_jobs table
            logger.info(f"Indexing research job from {d}")

