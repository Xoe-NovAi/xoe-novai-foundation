#!/usr/bin/env python3
"""
Add frontmatter to archived files for proper provenance tracking.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def add_frontmatter_to_file(file_path):
    """Add frontmatter to a single file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if file already has frontmatter
        if content.startswith('---'):
            print(f"Skipping {file_path} - already has frontmatter")
            return
        
        # Extract timestamp from filename
        filename = file_path.name
        if '.backup.' in filename:
            timestamp = filename.split('.backup.')[1].split('.')[0]
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create frontmatter
        frontmatter = f"""---
archived_from: {file_path.name.replace('.backup.' + timestamp, '')}
archived_at: {timestamp}
reason: drift
---

"""
        
        # Write updated content
        with open(file_path, 'w') as f:
            f.write(frontmatter + content)
        
        print(f"Added frontmatter to {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    """Process all archived files."""
    archive_dir = Path('_archive/memory_bank')
    
    if not archive_dir.exists():
        print("No archive directory found")
        return
    
    for file_path in archive_dir.glob('*.md'):
        add_frontmatter_to_file(file_path)

if __name__ == "__main__":
    main()