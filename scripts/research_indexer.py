#!/usr/bin/env python3
"""Index research project directories and sync with DB."""

import logging
from app.XNAi_rag_app.services.indexer import ResearchIndexer

logging.basicConfig(level=logging.INFO)


def main():
    idx = ResearchIndexer()
    idx.update_database()


if __name__ == "__main__":
    main()
