#!/usr/bin/env python3
"""
Stale Content Detector
======================

Scans documentation directories and flags files that haven't been updated
for a significant period (default: 90 days).
Generates a markdown report for documentation maintenance.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Default thresholds
STALE_THRESHOLD_DAYS = 90
CRITICAL_THRESHOLD_DAYS = 180

# Directories to scan
TARGET_DIRS = [
    "docs",
    "expert-knowledge",
    "memory_bank"
]

def get_stale_files(root_dir: str, days: int):
    """Find files older than 'days' days."""
    root = Path(root_dir)
    stale_files = []
    threshold = datetime.now() - timedelta(days=days)
    
    for target in TARGET_DIRS:
        target_path = root / target
        if not target_path.exists():
            continue
            
        for file_path in target_path.rglob("*.md"):
            # Skip certain directories
            if "_archive" in str(file_path) or "archival" in str(file_path):
                continue
                
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < threshold:
                    stale_files.append({
                        "path": str(file_path.relative_to(root)),
                        "mtime": mtime,
                        "days_old": (datetime.now() - mtime).days
                    })
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                
    return sorted(stale_files, key=lambda x: x['days_old'], reverse=True)

def generate_report(stale_files: list, output_path: str):
    """Generate a markdown report of stale files."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.now().strftime("%Y-%m-%d")
    
    with open(output_path, "w") as f:
        f.write(f"# 🕒 Stale Content Report - {today}\n\n")
        f.write(f"**Report Generated**: {now}\n")
        f.write(f"**Total Stale Files (>90 days)**: {len(stale_files)}\n\n")
        
        if not stale_files:
            f.write("✅ No stale files detected! All documentation is up-to-date.\n")
            return

        f.write("## 🔴 Critical Attention (>180 days)\n\n")
        critical = [file for file in stale_files if file['days_old'] > CRITICAL_THRESHOLD_DAYS]
        if critical:
            f.write("| File Path | Days Old | Last Updated |\n")
            f.write("|-----------|----------|--------------|\n")
            for file in critical:
                f.write(f"| {file['path']} | {file['days_old']} | {file['mtime'].strftime('%Y-%m-%d')} |\n")
        else:
            f.write("None.\n")
            
        f.write("\n## 🟡 Stale Content (90-180 days)\n\n")
        warning = [file for file in stale_files if 90 <= file['days_old'] <= CRITICAL_THRESHOLD_DAYS]
        if warning:
            f.write("| File Path | Days Old | Last Updated |\n")
            f.write("|-----------|----------|--------------|\n")
            for file in warning:
                f.write(f"| {file['path']} | {file['days_old']} | {file['mtime'].strftime('%Y-%m-%d')} |\n")
        else:
            f.write("None.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect stale documentation content.")
    parser.add_argument("--days", type=int, default=STALE_THRESHOLD_DAYS, help="Stale threshold in days")
    parser.add_argument("--output", type=str, default="reports/stale-content.md", help="Output report path")
    args = parser.parse_args()
    
    project_root = os.getcwd()
    
    # Ensure reports directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    print(f"Scanning for files older than {args.days} days...")
    stale_files_list = get_stale_files(project_root, args.days)
    
    print(f"Found {len(stale_files_list)} stale files.")
    generate_report(stale_files_list, args.output)
    print(f"Report generated: {args.output}")
