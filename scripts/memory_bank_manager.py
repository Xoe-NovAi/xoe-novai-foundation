#!/usr/bin/env python3
"""
Memory Bank Tier Manager
========================

Automates the tiering of memory bank files:
- Core: Always loaded (in memory_bank/ root)
- Recall: Recent history (in memory_bank/recall/) - 90 day retention
- Archival: Long-term storage (in memory_bank/archival/) - Permanent

Usage:
    python3 scripts/memory_bank_manager.py --action tier
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Core files that MUST stay in the root
CORE_FILES = [
    "projectbrief.md",
    "productContext.md",
    "systemPatterns.md",
    "techContext.md",
    "activeContext.md",
    "progress.md",
    "ARCHITECTURE.md",
    "INDEX.md",
    "BLOCKS.yaml",
    "OPERATIONS.md",
    "teamProtocols.md",
    "ACCOUNT-REGISTRY.yaml"
]

# Retention policies
RECALL_RETENTION_DAYS = 90

def manage_tiers(root_dir: str, dry_run: bool = False):
    """Move non-core files to recall, and old recall to archival."""
    root = Path(root_dir)
    bank_root = root / "memory_bank"
    recall_dir = bank_root / "recall"
    archival_dir = bank_root / "archival"
    
    # Ensure dirs exist
    recall_dir.mkdir(exist_ok=True)
    archival_dir.mkdir(exist_ok=True)
    
    print(f"Managing memory tiers in {bank_root}...")
    
    # 1. Tier from Root to Recall
    # Any .md file in root NOT in CORE_FILES should go to recall
    for file_path in bank_root.glob("*.md"):
        if file_path.name not in CORE_FILES:
            target = recall_dir / file_path.name
            print(f"[Tier] Root -> Recall: {file_path.name}")
            if not dry_run:
                shutil.move(str(file_path), str(target))

    # 2. Tier from Recall to Archival
    # Files in recall older than RECALL_RETENTION_DAYS go to archival
    threshold = datetime.now() - timedelta(days=RECALL_RETENTION_DAYS)
    for file_path in recall_dir.rglob("*.md"):
        if file_path.is_file():
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < threshold:
                # Determine archival subfolder based on parent folder in recall
                # or just use 'general'
                rel_path = file_path.relative_to(recall_dir)
                target = archival_dir / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                
                print(f"[Tier] Recall -> Archival: {rel_path} ({ (datetime.now()-mtime).days } days old)")
                if not dry_run:
                    shutil.move(str(file_path), str(target))

def archive_by_pattern(root_dir: str, pattern: str, target_tier: str, dry_run: bool = False):
    """Manually move files matching pattern to a tier."""
    root = Path(root_dir)
    bank_root = root / "memory_bank"
    target_dir = bank_root / target_tier
    
    if not target_dir.exists():
        print(f"Target tier {target_tier} does not exist.")
        return

    for file_path in bank_root.glob(pattern):
        if file_path.name in CORE_FILES:
            continue
        
        target = target_dir / file_path.name
        print(f"[Manual] -> {target_tier}: {file_path.name}")
        if not dry_run:
            shutil.move(str(file_path), str(target))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage memory bank tiers.")
    parser.add_argument("--action", choices=["tier", "cleanup"], default="tier")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    project_root = os.getcwd()
    
    if args.action == "tier":
        manage_tiers(project_root, args.dry_run)
    elif args.action == "cleanup":
        # Specific cleanup for research reports and old handovers
        archive_by_pattern(project_root, "RESEARCH-TASK-*.md", "archival/research", args.dry_run)
        archive_by_pattern(project_root, "RJ-*.md", "archival/research", args.dry_run)
        archive_by_pattern(project_root, "SESSION-*.md", "recall/conversations", args.dry_run)
        archive_by_pattern(project_root, "PHASE-*-REPORT.md", "recall/handovers", args.dry_run)
