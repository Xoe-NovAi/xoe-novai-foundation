#!/usr/bin/env python3
"""
Documentation Link Validator
============================

Validates internal links and image references within Markdown files.
Scans docs/, expert-knowledge/, and memory_bank/.
"""

import os
import re
from pathlib import Path
import argparse
from datetime import datetime

# Markdown link patterns
# 1. [text](link)
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
# 2. ![alt](img_link)
IMAGE_PATTERN = re.compile(r'\!\[([^\]]*)\]\(([^)]+)\)')
# 3. [[link]] (wikilinks - some agents use these)
WIKILINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')

TARGET_DIRS = ["docs", "expert-knowledge", "memory_bank"]

def validate_links(root_dir: str):
    """Validate all links in target directories."""
    root = Path(root_dir)
    results = {
        "files_scanned": 0,
        "links_checked": 0,
        "broken_links": []
    }
    
    for target in TARGET_DIRS:
        target_path = root / target
        if not target_path.exists():
            continue
            
        for file_path in target_path.rglob("*.md"):
            results["files_scanned"] += 1
            file_broken = check_file_links(file_path, root)
            if file_broken:
                results["broken_links"].extend(file_broken)
                
    return results

def check_file_links(file_path: Path, root: Path):
    """Check links within a single file."""
    broken = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return broken
        
    # Find all links
    links = LINK_PATTERN.findall(content)
    images = IMAGE_PATTERN.findall(content)
    wikilinks = WIKILINK_PATTERN.findall(content)
    
    # Process standard links
    for text, link in links:
        if is_internal_link(link):
            if not resolve_and_check(link, file_path, root):
                broken.append({
                    "file": str(file_path.relative_to(root)),
                    "link": link,
                    "type": "standard"
                })
                
    # Process images
    for alt, link in images:
        if is_internal_link(link):
            if not resolve_and_check(link, file_path, root):
                broken.append({
                    "file": str(file_path.relative_to(root)),
                    "link": link,
                    "type": "image"
                })

    # Process wikilinks
    for link in wikilinks:
        # Wikilinks often omit .md
        if not resolve_and_check(link, file_path, root, is_wikilink=True):
            broken.append({
                "file": str(file_path.relative_to(root)),
                "link": link,
                "type": "wikilink"
            })
            
    return broken

def is_internal_link(link: str):
    """Check if a link is internal (not http/https/mailto)."""
    if link.startswith(('http://', 'https://', 'mailto:', '#', 'tel:')):
        return False
    return True

def resolve_and_check(link: str, current_file: Path, root: Path, is_wikilink: bool = False):
    """Resolve a link relative to current file and check if it exists."""
    # Strip anchors
    clean_link = link.split('#')[0]
    if not clean_link:
        return True # Just an anchor to same file
        
    # Remove query params
    clean_link = clean_link.split('?')[0]
    
    # Handle absolute paths (relative to root)
    if clean_link.startswith('/'):
        target = root / clean_link.lstrip('/')
    else:
        target = (current_file.parent / clean_link).resolve()
        
    # Check existence
    if target.exists():
        return True
        
    # If wikilink or missing .md, try adding it
    if is_wikilink or not target.suffix:
        if (target.with_suffix('.md')).exists():
            return True
        # Also check if it's a directory index
        if (target / "index.md").exists():
            return True
            
    return False

def generate_link_report(results: dict, output_path: str):
    """Generate markdown report for broken links."""
    today = datetime.now().strftime("%Y-%m-%d")
    with open(output_path, "w") as f:
        f.write(f"# 🔗 Broken Link Report - {today}\n\n")
        f.write(f"**Files Scanned**: {results['files_scanned']}\n")
        f.write(f"**Broken Links Found**: {len(results['broken_links'])}\n\n")
        
        if not results['broken_links']:
            f.write("✅ No broken links detected! Documentation integrity is high.\n")
            return
            
        f.write("| File Containing Link | Broken Target | Type |\n")
        f.write("|----------------------|---------------|------|\n")
        for error in results['broken_links']:
            f.write(f"| {error['file']} | `{error['link']}` | {error['type']} |\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate documentation links.")
    parser.add_argument("--output", type=str, default="reports/broken-links.md", help="Output report path")
    args = parser.parse_args()
    
    project_root = os.getcwd()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    print("Validating links...")
    val_results = validate_links(project_root)
    
    print(f"Scanned {val_results['files_scanned']} files.")
    print(f"Found {len(val_results['broken_links'])} broken links.")
    
    generate_link_report(val_results, args.output)
    print(f"Report generated: {args.output}")
