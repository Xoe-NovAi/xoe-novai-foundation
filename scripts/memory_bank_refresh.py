#!/usr/bin/env python3
"""
Memory Bank Refresh Protocol - v1.0.0
Automatically updates memory_bank/ files with latest context from GROK_CONTEXT_PACK
Ensures consistency for local agents (Cline-Kat, Cline-Trinity, Cline-Gemini-Flash/Pro, Gemini CLI)
"""

import os
import re
import yaml
import sys
from datetime import datetime
import shutil
from pathlib import Path

# Configuration
MEMORY_BANK_DIR = "memory_bank"
EXPERT_KNOWLEDGE_DIR = "expert-knowledge"
EKB_EXPORTS_DIR = "ekb-exports"
ARCHIVE_DIR = "_archive"
GROK_PACK_FILE = "GROK_CONTEXT_PACK_v1.5.0.md"
GROK_PACK_DELTA_FILE = "GROK_CONTEXT_PACK_v1.5.0.delta.md"
SYNC_PROTOCOLS_FILE = "xoe-novai-sync/_meta/sync-protocols-v1.4.1.md"

# Active Models Reference block
ACTIVE_MODELS_BLOCK = """## Active Models Reference (as of {timestamp})
- Cline-Kat: kat-coder-pro (Kwaipilot) — strong coding
- Cline-Trinity: trinity-large (Arcee) — balanced reasoning
- Cline-Gemini-Flash: Gemini 3 Flash — fast/light default
- Cline-Gemini-Pro: Gemini 3 Pro — heavy/critical tasks only
- Gemini CLI: Terminal Gemini — ground truth executor
"""

# Standard YAML frontmatter
STANDARD_FRONTMATTER = """---
update_type: {update_type}
timestamp: {timestamp}
agent: Gemini CLI
priority: high
related_components: {related_components}
ma_at_ideal: 41 - Advance through own abilities
---
"""

def read_file(file_path):
    """Read file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    """Write content to file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote file: {file_path}")
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False

def backup_file(file_path):
    """Create backup of file before modification"""
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(ARCHIVE_DIR, f"{os.path.basename(file_path)}.backup.{timestamp}")
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Error creating backup for {file_path}: {e}")
        return None

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content"""
    frontmatter_match = re.match(r'^---\s*(.*?)\s*---', content, re.DOTALL)
    if frontmatter_match:
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            body = content[len(frontmatter_match.group(0)):].strip()
            return frontmatter, body
        except Exception as e:
            print(f"Error parsing frontmatter: {e}")
            return None, content.strip()
    return None, content.strip()

def update_frontmatter(content, update_type, related_components):
    """Update or add YAML frontmatter"""
    frontmatter, body = extract_frontmatter(content)
    
    timestamp = datetime.now().isoformat()
    
    new_frontmatter = STANDARD_FRONTMATTER.format(
        update_type=update_type,
        timestamp=timestamp,
        related_components=related_components
    )
    
    return new_frontmatter + '\n' + body

def inject_active_models_block(content, timestamp):
    """Inject Active Models Reference block"""
    # Check if block already exists
    if "Active Models Reference" in content:
        # Replace existing block
        pattern = r'## Active Models Reference \(as of .*\).*?(?=\n## |$)'
        replacement = ACTIVE_MODELS_BLOCK.format(timestamp=timestamp)
        return re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # Add new block after frontmatter
        frontmatter, body = extract_frontmatter(content)
        if frontmatter is not None:
            frontmatter_str = "---\n" + yaml.dump(frontmatter, sort_keys=False) + "---\n"
            return frontmatter_str + '\n' + ACTIVE_MODELS_BLOCK.format(timestamp=timestamp) + '\n' + body
        else:
            return ACTIVE_MODELS_BLOCK.format(timestamp=timestamp) + '\n' + content

def parse_grok_context():
    """Parse GROK_CONTEXT_PACK for key information"""
    # Check for delta pack first
    grok_file = GROK_PACK_DELTA_FILE if os.path.exists(GROK_PACK_DELTA_FILE) else GROK_PACK_FILE
    
    content = read_file(grok_file)
    if not content:
        return None
    
    # Extract phase progress
    phase_match = re.search(r'## 🚀 2026 Refactoring & Research Phase.*?\*\*Current Focus:\*\*(.*?)(?=\n##|\Z)', content, re.DOTALL)
    phase_progress = phase_match.group(1).strip() if phase_match else "Not specified"
    
    # Extract active models
    models_match = re.search(r'## Active Models Reference.*?(?=\n##|\Z)', content, re.DOTALL)
    active_models = models_match.group(0).strip() if models_match else "Not specified"
    
    # Extract sync hub status
    sync_match = re.search(r'### 📡 Synergy Ecosystem & AI Assistant Flows.*?(?=\n##|\Z)', content, re.DOTALL)
    sync_status = sync_match.group(0).strip() if sync_match else "Not specified"
    
    # Extract task locking notes
    task_locking_match = re.search(r'## Task Locking \(YAML Protocol\).*?(?=\n##|\Z)', content, re.DOTALL)
    task_locking = task_locking_match.group(0).strip() if task_locking_match else "Not specified"
    
    return {
        "phase_progress": phase_progress,
        "active_models": active_models,
        "sync_status": sync_status,
        "task_locking": task_locking,
        "source_file": grok_file
    }

def update_memory_bank_files(context):
    """Update all memory_bank files"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Files to update
    target_files = [
        os.path.join(MEMORY_BANK_DIR, "activeContext.md"),
        os.path.join(MEMORY_BANK_DIR, "teamProtocols.md"),
        os.path.join(EXPERT_KNOWLEDGE_DIR, "sync", "sovereign-synergy-expert-v1.0.0.md")
    ]
    
    updated_files = []
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        
        # Backup file
        backup_file(file_path)
        
        # Read file content
        content = read_file(file_path)
        if not content:
            continue
        
        # Update frontmatter
        update_type = "phase-progress" if "activeContext" in file_path else "sync-update"
        related_components = "[Phase 2, activeContext.md]" if "activeContext" in file_path else "[teamProtocols.md, sovereign-synergy]"
        
        updated_content = update_frontmatter(content, update_type, related_components)
        
        # Inject active models block
        updated_content = inject_active_models_block(updated_content, timestamp)
        
        # Write updated content
        if write_file(file_path, updated_content):
            updated_files.append(file_path)
    
    return updated_files

def create_receipt(updated_files, context):
    """Create receipt file in ekb-exports/"""
    if not os.path.exists(EKB_EXPORTS_DIR):
        os.makedirs(EKB_EXPORTS_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    receipt_path = os.path.join(EKB_EXPORTS_DIR, f"receipt-ack-{timestamp}.md")
    
    receipt_content = f"""---
version: 1.0.0
tags: [refresh, memory-bank, sync]
date: {datetime.now().isoformat()}
ma_at_mappings: [41: Advance through own abilities]
sync_status: active
---

# Memory Bank Refresh Receipt

## Refresh Details
- **Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Agent**: Gemini CLI
- **Source Context**: {context['source_file']}
- **Files Updated**: {len(updated_files)}

## Updated Files
"""
    
    for file_path in updated_files:
        receipt_content += f"- {file_path}\n"
    
    receipt_content += f"""
## Key Information Extracted from GROK_CONTEXT_PACK

### Phase Progress
{context['phase_progress']}

### Sync Status
{context['sync_status']}

## Drift Prevention Protocol
This refresh ensures memory_bank/ files stay current with the latest GROK_CONTEXT_PACK.
Run this protocol after every major task (Phase 2 milestones, nomenclature changes, pack generations).
"""
    
    if write_file(receipt_path, receipt_content):
        print(f"Receipt created: {receipt_path}")
        return receipt_path
    return None

def update_sync_protocols():
    """Update sync protocols to include refresh requirement"""
    # Check if we need to bump version
    if os.path.exists(SYNC_PROTOCOLS_FILE):
        current_content = read_file(SYNC_PROTOCOLS_FILE)
    else:
        # Check for v1.4.0 and create v1.4.1
        v140_path = "xoe-novai-sync/_meta/sync-protocols-v1.4.0.md"
        if os.path.exists(v140_path):
            current_content = read_file(v140_path)
        else:
            current_content = """---
pack_version: 1.4.1
focus: grok-sync, sovereignty, multi-agent, synergy-branding
---

# Xoe-NovAi Sync Protocols (v1.4.1)
"""
    
    # Check if refresh protocol is already documented
    if "memory_bank_refresh.py" in current_content:
        print("Sync protocols already include refresh requirement")
        return False
    
    # Add refresh protocol section
    refresh_section = """
## Memory Bank Refresh Protocol

### Standing Order
Run `memory_bank_refresh.py` after every major task:
- Phase 2 milestones
- Nomenclature changes
- Pack generations
- Any significant architectural decisions

### Command
```bash
make refresh-memory
```

### Purpose
Ensures memory_bank/ files stay razor-current for local agents:
- Cline-Kat (kat-coder-pro)
- Cline-Trinity (trinity-large) 
- Cline-Gemini-Flash/Pro (Gemini 3)
- Gemini CLI (Terminal Gemini)
"""
    
    updated_content = current_content.rstrip() + refresh_section
    
    if write_file(SYNC_PROTOCOLS_FILE, updated_content):
        print(f"Sync protocols updated: {SYNC_PROTOCOLS_FILE}")
        return True
    return False

def main():
    """Main refresh protocol"""
    print("=" * 60)
    print("Memory Bank Refresh Protocol - v1.0.0")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Parse GROK_CONTEXT_PACK
    print("\n1. Parsing GROK_CONTEXT_PACK...")
    context = parse_grok_context()
    if not context:
        print("Error: Failed to parse GROK_CONTEXT_PACK")
        return 1
    
    print(f"Successfully parsed from: {context['source_file']}")
    
    # Step 2: Update memory_bank files
    print("\n2. Updating memory_bank files...")
    updated_files = update_memory_bank_files(context)
    if not updated_files:
        print("Error: No files updated")
        return 1
    
    print(f"Successfully updated {len(updated_files)} files:")
    for file_path in updated_files:
        print(f"  - {file_path}")
    
    # Step 3: Create receipt
    print("\n3. Creating refresh receipt...")
    receipt_path = create_receipt(updated_files, context)
    if receipt_path:
        print(f"Receipt created: {receipt_path}")
    
    # Step 4: Update sync protocols
    print("\n4. Updating sync protocols...")
    if update_sync_protocols():
        print("Sync protocols updated")
    else:
        print("Sync protocols already up to date")
    
    print("\n" + "=" * 60)
    print("Refresh protocol completed successfully!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nRefresh protocol interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)