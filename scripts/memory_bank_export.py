#!/usr/bin/env python3
"""
Script to export memory_bank tasks as JSON for Vikunja import.
This script reads memory_bank markdown files, extracts frontmatter,
and prepares them for bulk import into Vikunja.
"""

import os
try:
    import frontmatter  # type: ignore
except Exception:
    frontmatter = None  # Fallback if the package is not installed
import json
import argparse
from pathlib import Path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Export memory_bank tasks as JSON for Vikunja import"
    )
    parser.add_argument(
        "memory_bank_dir",
        type=str,
        default="memory_bank",
        help="Path to memory_bank directory"
    )
    parser.add_argument(
        "output_file",
        type=str,
        default="vikunja-import.json",
        help="Output JSON file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run (show count without writing file)"
    )
    return parser.parse_args()


def extract_frontmatter(file_path):
    """Extract YAML frontmatter from markdown file.

    We prefer using the 'frontmatter' package, but in restricted environments
    it may not be available. Provide a lightweight fallback parser that extracts
    a simple YAML-like frontmatter block delimited by --- markers and returns a
    dictionary-like object with a 'content' attribute (to satisfy downstream
    code that accesses post.content and post.get()).
    """
    if frontmatter is not None:
        try:
            # Try to use the standard library when available
            return frontmatter.load(open(file_path, "r", encoding="utf-8"))
        except Exception:
            pass
    # Fallback path if the frontmatter package isn't available or fails
    # Lightweight fallback parser (no external dependencies)
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    metadata = {}
    content = text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            fm = text[3:end]
            content = text[end + 3 :].lstrip()
            for line in fm.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, val = line.split(":", 1)
                    metadata[key.strip()] = val.strip()
    class SimplePost(dict):
        def __init__(self, metadata, content):
            super().__init__(metadata)
            self.content = content
    return SimplePost(metadata, content)


def map_labels_from_frontmatter(frontmatter_data):
    """Map memory_bank frontmatter to Vikunja labels."""
    labels = []

    # Map agents
    if "agents" in frontmatter_data:
        if isinstance(frontmatter_data["agents"], list):
            labels.extend(frontmatter_data["agents"])
        else:
            labels.append(frontmatter_data["agents"])

    # Map status
    if "status" in frontmatter_data:
        labels.append(frontmatter_data["status"])

    # Map priorities
    if "priority" in frontmatter_data:
        labels.append(f"priority-{frontmatter_data['priority']}")

    # Map Ma'at ideals
    if "ma_at_ideals" in frontmatter_data:
        if isinstance(frontmatter_data["ma_at_ideals"], list):
            for ideal in frontmatter_data["ma_at_ideals"]:
                labels.append(f"ma_at_{ideal}")
        else:
            labels.append(f"ma_at_{frontmatter_data['ma_at_ideals']}")

    # Map knowledge areas
    if "knowledge" in frontmatter_data:
        if isinstance(frontmatter_data["knowledge"], list):
            labels.extend(frontmatter_data["knowledge"])
        else:
            labels.append(frontmatter_data["knowledge"])

    # Map domains
    if "domains" in frontmatter_data:
        if isinstance(frontmatter_data["domains"], list):
            labels.extend(frontmatter_data["domains"])
        else:
            labels.append(frontmatter_data["domains"])

    return labels


def main():
    """Main export process."""
    args = parse_arguments()

    memory_bank_path = Path(args.memory_bank_dir)
    if not memory_bank_path.exists() or not memory_bank_path.is_dir():
        print(f"Error: {args.memory_bank_dir} does not exist or is not a directory")
        return

    tasks = []

    # Recursively find all markdown files in memory_bank
    for md_file in memory_bank_path.rglob("*.md"):
        try:
            post = extract_frontmatter(md_file)

            # Create task structure
            task = {
                "title": post.get("title", md_file.stem),
                "description": post.content.strip(),
                "labels": map_labels_from_frontmatter(post),
                "custom_fields": {},
                "project": "Sync",
                "status": post.get("status", "backlog")
            }

            # Add custom fields from frontmatter
            if "author" in post:
                task["custom_fields"]["Owner"] = post["author"]
            if "date" in post:
                task["custom_fields"]["Date"] = str(post["date"])
            if "ekb_links" in post:
                task["custom_fields"]["EKB-Link"] = ", ".join(post["ekb_links"]) if isinstance(post["ekb_links"], list) else post["ekb_links"]
            if "version" in post:
                task["custom_fields"]["Version"] = str(post["version"])
            if "account" in post:
                task["custom_fields"]["Account"] = post["account"]

            # Determine priority from frontmatter
            if "priority" in post:
                priority_map = {
                    "high": 1,
                    "medium": 2,
                    "low": 3,
                    "critical": 0
                }
                task["priority"] = priority_map.get(
                    str(post["priority"]).lower(), 2
                )

            tasks.append(task)

        except Exception as e:
            print(f"Error processing {md_file}: {e}")

    # Dry run or write to output file
    if args.dry_run:
        print(f"DRY RUN: Would export {len(tasks)} tasks to {args.output_file}")
        print("Task preview:")
        for i, task in enumerate(tasks[:3]):
            print(f"  {i+1}. {task['title']} - {len(task['labels'])} labels")
        if len(tasks) > 3:
            print(f"  ... and {len(tasks) - 3} more tasks")
    else:
        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2, default=str)

        print(f"Successfully exported {len(tasks)} tasks to {args.output_file}")


if __name__ == "__main__":
    main()
