# Quick Expert Creation Guide

**Date**: 2026-02-26  
**Purpose**: Create specialized domain experts using JSON/YAML without dedicated memory_bank

---

## Overview

This guide provides a lightweight method for creating specialized domain experts using YAML/JSON configuration files. These "quick experts" can be used for specific domains without creating a full memory_bank structure.

---

## Quick Expert Format

### YAML Format (Recommended)

```yaml
# expert-definition.yaml
expert_id: "domain-specialist"
domain: "specific_domain_name"
version: "1.0.0"
description: "Brief description of expert capabilities"

# Core knowledge - simple key-value pairs
knowledge:
  key_facts:
    - "Fact 1"
    - "Fact 2"
    
  references:
    file: "path/to/reference.md"
    section: "relevant_section"
    
  commands:
    primary: "command to run"
    fallback: "alternative command"

# Configuration (optional)
config:
  auto_load: true
  priority: 10
  dependencies:
    - "other_expert_id"

# Metadata
author: "XNAi Foundation"
created: "2026-02-26"
tags:
  - "tag1"
  - "tag2"
```

### JSON Format

```json
{
  "expert_id": "domain-specialist",
  "domain": "specific_domain_name",
  "version": "1.0.0",
  "description": "Brief description",
  "knowledge": {
    "key_facts": ["Fact 1", "Fact 2"],
    "references": {
      "file": "path/to/reference.md",
      "section": "relevant_section"
    },
    "commands": {
      "primary": "command to run",
      "fallback": "alternative command"
    }
  },
  "config": {
    "auto_load": true,
    "priority": 10
  },
  "metadata": {
    "author": "XNAi Foundation",
    "created": "2026-02-26",
    "tags": ["tag1", "tag2"]
  }
}
```

---

## Examples

### Example 1: GitHub Account Quick Reference

```yaml
# github-quick-expert.yaml
expert_id: "github-quick-ref"
domain: "github_accounts"
version: "1.0.0"
description: "Quick reference for GitHub account operations"

knowledge:
  current_account:
    email: "arcananovaai@gmail.com"
    quota_remaining: 25
    status: "active"
    
  commands:
    check_status: "gh auth status"
    switch_account: "gh auth switch --user <username>"
    check_rate_limit: "gh api rate_limit"
    audit: "python3 scripts/github-account-audit.py"
    
  rotation:
    strategy: "lowest-usage-first"
    current: "arcananovaai"
    next: "xoe.nova.ai"

config:
  auto_load: true
  priority: 5
  dependencies:
    - "multi-account-specialist"
```

### Example 2: Split Test Coordinator

```yaml
# split-test-expert.yaml
expert_id: "split-test-coordinator"
domain: "model_comparison"
version: "1.0.0"
description: "Coordinates split tests between models"

knowledge:
  models:
    - name: "Raptor Mini"
      provider: "Copilot"
      context: 264000
      command: "copilot -m raptor-mini-preview"
      
    - name: "Haiku 4.5"
      provider: "Copilot"
      context: 200000
      command: "copilot -m claude-haiku-4-5"
      
    - name: "MiniMax M2.5"
      provider: "OpenCode"
      context: 204800
      command: "opencode --model minimax-m2.5-free"

  test_parameters:
    context_files:
      - "memory_bank/handovers/RAPTOR-ONBOARDING-CONTEXT-DOCUMENT.md"
      - "memory_bank/handovers/WAVE-5-PREP-RESOURCES.md"
      
    evaluation_criteria:
      - "completeness"
      - "accuracy"
      - "actionability"
      - "efficiency"
      - "structure"

  execution_order:
    - model: "Raptor Mini"
      account: "xoe.nova.ai"
    - model: "Haiku 4.5"
      account: "arcananovaai"
    - model: "MiniMax M2.5"
      account: "OpenCode (unlimited)"

config:
  auto_load: false
  priority: 8
```

### Example 3: Quota Monitor

```yaml
# quota-monitor-expert.yaml
expert_id: "quota-monitor"
domain: "quota_management"
version: "1.0.0"
description: "Monitors and alerts on quota usage"

knowledge:
  providers:
    github:
      accounts: 7
      total_quota: 350
      current_usage: 25
      reset_date: "2026-03-01"
      
    antigravity:
      accounts: 8
      total_quota: 4000000
      current_usage: 0
      reset_date: "weekly"
      
    opencode:
      accounts: 1
      quota: "unlimited"
      status: "active"

  alert_thresholds:
    warning: 40  # percent
    critical: 10  # percent
    
  commands:
    check_all: "python3 scripts/xnai-quota-audit.py"
    check_github: "python3 scripts/github-account-audit.py"
    dashboard: "cat memory_bank/usage/DASHBOARD.md"

config:
  auto_load: true
  priority: 9
```

---

## Quick Expert Loader

### Python Implementation

```python
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional

class QuickExpertLoader:
    """Load and manage quick experts from YAML/JSON."""
    
    def __init__(self, experts_dir: str = "memory_bank/experts/"):
        self.experts_dir = Path(experts_dir)
        self.experts: Dict[str, Dict] = {}
        
    def load_expert(self, filename: str) -> Optional[Dict]:
        """Load a single expert definition."""
        filepath = self.experts_dir / filename
        
        if not filepath.exists():
            return None
            
        with open(filepath) as f:
            if filepath.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif filepath.suffix == '.json':
                return json.load(f)
                
        return None
    
    def load_all(self):
        """Load all experts from directory."""
        for filepath in self.experts_dir.glob("*.yaml"):
            expert = self.load_expert(filepath.name)
            if expert:
                self.experts[expert['expert_id']] = expert
                
        for filepath in self.experts_dir.glob("*.json"):
            expert = self.load_expert(filepath.name)
            if expert:
                self.experts[expert['expert_id']] = expert
                
    def get_expert(self, expert_id: str) -> Optional[Dict]:
        """Get expert by ID."""
        return self.experts.get(expert_id)
    
    def find_by_domain(self, domain: str) -> list:
        """Find experts by domain."""
        return [
            e for e in self.experts.values()
            if e.get('domain') == domain
        ]
    
    def get_knowledge(self, expert_id: str, key: str) -> Any:
        """Get specific knowledge from expert."""
        expert = self.get_expert(expert_id)
        if expert:
            return expert.get('knowledge', {}).get(key)
        return None
```

### Usage

```python
# Load all quick experts
loader = QuickExpertLoader()
loader.load_all()

# Get specific expert
github_quick = loader.get_expert("github-quick-ref")

# Get knowledge
current_account = loader.get_knowledge("github-quick-ref", "current_account")

# Find by domain
quota_experts = loader.find_by_domain("quota_management")
```

---

## Integration with Memory Bank

### Loading Quick Experts

Quick experts can be loaded into the memory bank system:

```python
# In memory bank loader
from quick_expert_loader import QuickExpertLoader

loader = QuickExpertLoader()
loader.load_all()

# Convert to memory block format
for expert_id, expert in loader.experts.items():
    memory_block = {
        "expert_id": expert_id,
        "domain": expert.get("domain"),
        "knowledge": expert.get("knowledge"),
        "config": expert.get("config"),
        "source": "quick_expert"
    }
    # Add to memory bank
```

---

## Best Practices

### When to Use Quick Experts

| Use Case | Recommendation |
|----------|-----------------|
| **Simple reference** | ✅ Quick expert (YAML/JSON) |
| **Complex procedures** | ❌ Full memory_bank expert |
| **One-off task** | ✅ Quick expert |
| **Multi-session domain** | ❌ Full memory_bank expert |
| **Integration-heavy** | ❌ Full memory_bank expert |

### Naming Conventions

```
{domain}-{type}-expert.yaml

Examples:
├── github-account-expert.yaml
├── split-test-expert.yaml
├── quota-monitor-expert.yaml
└── model-router-expert.yaml
```

### Storage Location

Quick experts can be stored in:

```
memory_bank/experts/
├── github-quick.yaml
├── split-test.yaml
└── quota-monitor.yaml
```

Or inline in existing configs:

```
memory_bank/usage/
├── github-accounts.yaml    # Includes quick expert
└── quota-status.json       # Includes quota expert
```

---

## Status

**Created**: 2026-02-26  
**Purpose**: Enable lightweight expert creation without full memory_bank structure  
**Integration**: Works with `QuickExpertLoader` class

---

**Last Updated**: 2026-02-26
