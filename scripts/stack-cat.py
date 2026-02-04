#!/usr/bin/env python3
"""
stack_cat_enhanced.py — Enhanced context-pack generator (v1.5.0)
Evolution of stack_cat.py: config-driven, delta mode, archiving, EKB index integration

Features:
- Loads file lists from YAML config
- Delta mode: Generates only changed sections since last pack
- Auto-protocol versioning and change logging
- EKB index integration
- Archive management for superseded packs
- Custom config path support
- Tree inventory generation
"""

import os
import datetime
import subprocess
import argparse
import yaml
from pathlib import Path
import json
import shutil
import re
from typing import List, Dict, Optional, Any

# Default config
DEFAULT_CONFIG = "configs/stack-cat-config.yaml"

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def slugify(path_str: str) -> str:
    slug = path_str.lower().replace("/", "-").replace(".", "-").replace("_", "-").strip('-')
    return slug

def generate_tree_summary() -> str:
    try:
        summary = subprocess.check_output(
            ["tree", "-L", "3", "--charset", "ascii"], cwd=".", text=True, encoding='utf-8'
        )
        return f"## Summarized Inventory (Top-Level Tree)\n```\n{summary}\n```\n\n"
    except Exception:
        return "## Tree summary unavailable (tree command missing)\n\n"

def load_progress_metadata():
    try:
        with open('progress_tracker.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return f"## Progress Metadata\nLast Sync: {data['last_sync']}\nIncluded Files: {len(data['included_files'])}\n\n"
    except FileNotFoundError:
        return "## Progress Metadata: Unavailable\n\n"

def get_git_modified_files(since_commit: Optional[str] = None) -> List[str]:
    """Get list of modified files using git"""
    try:
        if since_commit:
            cmd = ["git", "diff", "--name-only", since_commit]
        else:
            cmd = ["git", "status", "--porcelain"]
        
        result = subprocess.check_output(cmd, text=True, encoding='utf-8').strip()
        if since_commit:
            return result.splitlines() if result else []
        
        modified_files = []
        for line in result.splitlines():
            if line:
                status, path = line.split(maxsplit=1)
                if status in ("M", "A"):
                    modified_files.append(path)
        
        return modified_files
    except Exception as e:
        print(f"Warning: Failed to get modified files - {e}")
        return []

def archive_superseded_pack(output_file: str):
    """Archive superseded pack"""
    archive_dir = Path("_archive")
    if not archive_dir.exists():
        archive_dir.mkdir()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    basename = Path(output_file).stem
    archive_path = archive_dir / f"{basename}_{timestamp}.md"
    
    if Path(output_file).exists():
        shutil.copy2(output_file, archive_path)
        print(f"Superseded pack archived → {archive_path}")
    
    return str(archive_path)

def update_ekb_index(files: List[str], protocol_version: str):
    """Update EKB index"""
    ekb_index_path = Path("expert-knowledge/_meta/ekb-index-v1.0.0.md")
    if not ekb_index_path.parent.exists():
        ekb_index_path.parent.mkdir(parents=True)
    
    if not ekb_index_path.exists():
        with open(ekb_index_path, 'w', encoding='utf-8') as f:
            f.write("---\nversion: 1.0.0\ngenerated_at: {}\n---\n\n# Expert Knowledge Base Index\n\n| Name | Path | Focus | Updated | Status | Revival Priority |\n|------|------|-------|---------|--------|-----------------|\n".format(datetime.datetime.now().isoformat(timespec="seconds")))
    
    with open(ekb_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if entry already exists
    updated_content = []
    for rel_path in files:
        path = Path(rel_path)
        if not path.exists():
            continue
        
        # Extract frontmatter
        try:
            content_str = path.read_text(encoding="utf-8")
            if content_str.startswith("---"):
                fm_end = content_str.find("---", 3)
                if fm_end != -1:
                    frontmatter = yaml.safe_load(content_str[3:fm_end])
                    name = frontmatter.get("expert_dataset_name", path.name)
                    focus = frontmatter.get("expertise_focus", "Not specified")
                    status = frontmatter.get("sync_status", "active")
                    priority = frontmatter.get("revival_priority", "MEDIUM")
                    updated = frontmatter.get("date", datetime.datetime.now().strftime("%Y-%m-%d"))
                else:
                    name = path.name
                    focus = "Not specified"
                    status = "active"
                    priority = "MEDIUM"
                    updated = datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                name = path.name
                focus = "Not specified"
                status = "active"
                priority = "MEDIUM"
                updated = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Create index entry
            entry = f"| {name} | {rel_path} | {focus} | {updated} | {status} | {priority} |"
            
            # Add to index if not already present
            if entry not in content:
                updated_content.append(entry)
        except Exception as e:
            print(f"Warning: Failed to index {rel_path} - {e}")
            continue
    
    if updated_content:
        with open(ekb_index_path, 'a', encoding='utf-8') as f:
            for entry in updated_content:
                f.write(f"{entry}\n")
        print(f"EKB index updated → {ekb_index_path}")
    else:
        print("EKB index is up to date")

def update_sync_protocol_change_log(change: str, rationale: str):
    """Update sync protocol change log"""
    protocol_path = Path("xoe-novai-sync/_meta/sync-protocols-v1.5.0.md")
    if not protocol_path.exists():
        with open(protocol_path, 'w', encoding='utf-8') as f:
            f.write("---\npack_version: 1.5.0\nfocus: grok-sync, sovereignty, multi-agent, synergy-branding\n---\n\n# Xoe-NovAi Sync Protocols v1.5.0\n\n## Change Log\n\n")
    
    with open(protocol_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    change_log_entry = f"- **{timestamp}**: {change}\n  - Rationale: {rationale}\n"
    
    # Insert at beginning of change log
    if "## Change Log" in content:
        content = content.replace("## Change Log\n\n", f"## Change Log\n\n{change_log_entry}")
    else:
        content += f"## Change Log\n\n{change_log_entry}"
    
    with open(protocol_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Sync protocol updated → {protocol_path}")

def main():
    parser = argparse.ArgumentParser(description="Enhanced stack_cat.py (v1.5.0)")
    parser.add_argument("--mode", choices=["grok-pack", "onboarding", "minimal"], default="grok-pack",
                        help="Pack profile (default: grok-pack)")
    parser.add_argument("--output", default="grok-pack-latest.md",
                        help="Output markdown file")
    parser.add_argument("--version", default="1.5.0",
                        help="pack_version in frontmatter")
    parser.add_argument("--config", default=DEFAULT_CONFIG,
                        help="Path to YAML config file")
    parser.add_argument("--no-tree", action="store_true",
                        help="Skip tree summary generation")
    parser.add_argument("--delta-mode", action="store_true",
                        help="Generate delta pack with only changed sections (requires git)")
    parser.add_argument("--since-commit", default=None,
                        help="Commit hash to compare against for delta mode")
    parser.add_argument("--update-protocol", action="store_true",
                        help="Update sync protocol with change log entry")
    parser.add_argument("--archive-superseded", action="store_true",
                        help="Archive superseded pack to _archive directory")
    parser.add_argument("--update-ekb-index", action="store_true",
                        help="Update EKB index with new files")
    parser.add_argument("--change-description", default="Pack generation",
                        help="Description of change for protocol update")
    parser.add_argument("--change-rationale", default="Generated new context pack",
                        help="Rationale for change for protocol update")
    args = parser.parse_args()

    config = load_config(args.config)
    files = config.get("file_lists", {}).get(args.mode, [])
    now = datetime.datetime.now().isoformat(timespec="seconds")
    
    # Handle delta mode
    if args.delta_mode:
        modified_files = get_git_modified_files(args.since_commit)
        filtered_files = [f for f in files if f in modified_files]
        print(f"Delta mode: {len(filtered_files)} of {len(files)} files modified")
        if not filtered_files:
            print("No files changed since last pack - skipping generation")
            return
        files = filtered_files
    else:
        filtered_files = files
    
    # Archive superseded pack if requested
    if args.archive_superseded and Path(args.output).exists():
        archive_superseded_pack(args.output)
    
    # Frontmatter + TOC skeleton
    header = f"""---
pack_version: {args.version}
focus: grok-sync, sovereignty, multi-agent, synergy-branding
generated_at: {now}
mode: {args.mode}
delta_mode: {args.delta_mode}
---

# Xoe-NovAi Context Pack ({args.mode.upper()})

Generated at: {now}

"""
    
    if args.delta_mode:
        header += f"## Delta Changes\n"
        if args.since_commit:
            header += f"Comparing to commit: {args.since_commit}\n"
        else:
            header += f"Comparing to last pack generation\n"
        header += f"Number of modified files: {len(files)}\n\n---\n\n"
    
    header += "## Quick Jump\n"
    
    toc_lines = []
    body_sections = []
    
    for rel_path in files:
        path = Path(rel_path)
        if not path.exists():
            body_sections.append(f"<!-- MISSING: {rel_path} -->")
            continue
    
        file_id = slugify(str(path))
        anchor = f"file-id-{file_id}-start-path-{rel_path}"
        toc_lines.append(f"- [{path.name}](#{anchor})")
    
        body_sections.append(f"\n<!-- FILE ID: {file_id} START (Path: {rel_path}) -->")
        # Optional per-file YAML frontmatter if present
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            fm, _, body = content.partition("---\n")
            body_sections.append(fm.strip())  # preserve inner frontmatter
            body_sections.append("\n---\n")
            body_sections.append(body.strip())
        else:
            body_sections.append(content.strip())
        body_sections.append(f"\n<!-- FILE ID: {file_id} END -->\n")
    
    header += "\n".join(toc_lines)
    header += "\n\n---\n\n"
    if not args.no_tree and not args.delta_mode:
        header += generate_tree_summary()
    if not args.delta_mode:
        header += load_progress_metadata()
    header += "---\n\n"
    
    full_pack = header + "\n".join(body_sections)
    
    Path(args.output).write_text(full_pack, encoding="utf-8")
    print(f"Pack generated → {args.output} ({len(files)} files, {args.mode} mode)")
    
    # Update sync protocol if requested
    if args.update_protocol:
        update_sync_protocol_change_log(args.change_description, args.change_rationale)
    
    # Update EKB index if requested
    if args.update_ekb_index:
        update_ekb_index(filtered_files, args.version)
    
    # Create receipt
    receipt_path = Path(f"ekb-exports/receipt-ack-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(receipt_path, 'w', encoding='utf-8') as f:
        f.write(f"""---
generated_at: {now}
pack_version: {args.version}
mode: {args.mode}
file_count: {len(files)}
delta_mode: {args.delta_mode}
---

# Context Pack Generation Receipt

Generated at: {now}
Version: {args.version}
Mode: {args.mode}
File Count: {len(files)}
Delta Mode: {args.delta_mode}
{'Comparison Commit: ' + args.since_commit if args.since_commit else ''}

## Included Files
""")
        for rel_path in files:
            f.write(f"- {rel_path}\n")
    
    print(f"Receipt generated → {receipt_path}")

if __name__ == "__main__":
    main()