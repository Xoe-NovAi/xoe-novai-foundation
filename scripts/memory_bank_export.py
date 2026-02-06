#!/usr/bin/env python3
"""
Script to export memory_bank tasks as JSON for Vikunja import.
This script reads memory_bank markdown files, extracts frontmatter,
and prepares them for bulk import into Vikunja.
"""

import os
import frontmatter
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
    return parser.parse_args()


def extract_frontmatter(file_path):
    """Extract YAML frontmatter from markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return frontmatter.load(f)


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

    # Write to output file
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2, default=str)

    print(f"Successfully exported {len(tasks)} tasks to {args.output_file}")


if __name__ == "__main__":
    main()