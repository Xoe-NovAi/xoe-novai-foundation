#!/usr/bin/env python3
"""
stack_cat_enhanced.py — Enhanced context-pack generator
Evolution of stack_cat.py: config-driven, progress integration, flexible CLI

Features:
- Loads file lists from YAML config
- Integrates progress_tracker.json for metadata
- Optional tree skip
- Custom config path support
"""

import os
import datetime
import subprocess
import argparse
import yaml
from pathlib import Path
import json

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

def main():
    parser = argparse.ArgumentParser(description="Enhanced stack_cat.py")
    parser.add_argument("--mode", choices=["grok-pack", "onboarding", "minimal"], default="grok-pack",
                        help="Pack profile (default: grok-pack)")
    parser.add_argument("--output", default="grok-pack-latest.md",
                        help="Output markdown file")
    parser.add_argument("--version", default="2.1.0",
                        help="pack_version in frontmatter")
    parser.add_argument("--config", default=DEFAULT_CONFIG,
                        help="Path to YAML config file")
    parser.add_argument("--no-tree", action="store_true",
                        help="Skip tree summary generation")
    args = parser.parse_args()

    config = load_config(args.config)
    files = config.get("file_lists", {}).get(args.mode, [])
    now = datetime.datetime.now().isoformat(timespec="seconds")
    
    # Frontmatter + TOC skeleton
    header = f"""---
pack_version: {args.version}
focus: grok-sync, sovereignty, multi-agent, synergy-branding
generated_at: {now}
mode: {args.mode}
---

# Xoe-NovAi Context Pack ({args.mode.upper()})

Generated at: {now}

## Quick Jump
"""

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
    if not args.no_tree:
        header += generate_tree_summary()
    header += load_progress_metadata()
    header += "---\n\n"
    
    full_pack = header + "\n".join(body_sections)
    
    Path(args.output).write_text(full_pack, encoding="utf-8")
    print(f"Pack generated → {args.output} ({len(files)} files, {args.mode} mode)")

if __name__ == "__main__":
    main()