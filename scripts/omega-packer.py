#!/usr/bin/env python3
"""
Omega Context Packer (v2.0)
===========================
Hardened collimator for the Omega Metropolis. 
Packages 8-domain experts, memory bank, and codebase into a single 
Markdown file for model injection (Grok, Gemini, etc.)
"""

import os
import datetime
import subprocess
from pathlib import Path
import yaml

INSTANCE_ROOT = "/tmp/xnai-instances"
OUTPUT_FILE = "artifacts/omega-context-pack.md"

# Essential files for every pack
CORE_FILES = [
    "memory_bank/activeContext.md",
    "memory_bank/techContext.md",
    "memory_bank/systemPatterns.md",
    "README.md",
    "docs/architecture/METROPOLIS-HIERARCHY.md"
]

def generate_pack():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    pack_content = f"""---
title: Omega Metropolis Context Pack
generated_at: {now}
architecture: Hierarchical 8-Domain Expert Network
---

# 🏙️ Omega Metropolis Context Pack

## 📊 Inventory Summary
"""
    
    # 1. Add Tree Summary
    try:
        tree = subprocess.check_output(["tree", "-L", "2", "--charset", "ascii"], text=True)
        pack_content += f"```\n{tree}\n```\n\n---\n"
    except:
        pack_content += "Tree summary unavailable.\n\n"

    # 2. Add Core Files
    for file_path in CORE_FILES:
        path = Path(file_path)
        if path.exists():
            content = path.read_text(encoding='utf-8')
            pack_content += f"\n## 📄 File: {file_path}\n```markdown\n{content}\n```\n"

    # 3. Add 8-Domain Expert Souls
    pack_content += "\n## 🧬 Expert Domain Pulse (Souls & Progress)\n"
    for i in range(1, 9):
        soul_path = Path(INSTANCE_ROOT) / f"instance-{i}/gemini-cli/.gemini/expert_soul.md"
        if soul_path.exists():
            content = soul_path.read_text(encoding='utf-8')
            pack_content += f"\n### District {i} Soul\n```markdown\n{content}\n```\n"

    # Write output
    os.makedirs("artifacts", exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(pack_content)
    
    print(f"✅ Omega Context Pack generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_pack()
