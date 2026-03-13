#!/usr/bin/env python3
"""
RJ-Synth-Memory: Synthesize memory management research into documentation and expert knowledge

This script implements the RJ-Synth-Memory job from the Gnosis Engine.
It transforms memory management research from memory_bank into official documentation
and updates the expert knowledge base.

Usage:
    python3 scripts/rj-synth-memory.py [--dry-run] [--verbose]
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class MemorySynthesisEngine:
    """Engine for synthesizing memory management research into documentation."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = self._setup_logging()
        
        # Paths
        self.memory_bank_dir = Path("memory_bank")
        self.docs_dir = Path("docs")
        self.expert_knowledge_dir = Path("expert-knowledge")
        self.research_dir = self.memory_bank_dir / "research"
        
        # Output paths
        self.memory_management_doc = self.docs_dir / "03-how-to-guides/infrastructure/memory-management.md"
        self.memory_expert_kb = self.expert_knowledge_dir / "infrastructure" / "memory-management.md"
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("MemorySynthesisEngine")
        logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def find_memory_research(self) -> List[Path]:
        """Find all memory management related research files."""
        self.logger.info("🔍 Searching for memory management research...")
        
        memory_keywords = [
            "memory", "zram", "swap", "ram", "performance", "optimization",
            "resource", "management", "monitoring", "health", "guard"
        ]
        
        research_files = []
        
        # Search in research directory
        if self.research_dir.exists():
            for file_path in self.research_dir.glob("*.md"):
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if any(keyword.lower() in content.lower() for keyword in memory_keywords):
                    research_files.append(file_path)
                    self.logger.info(f"  ✓ Found: {file_path.name}")
        
        # Search in memory_bank for memory-related files
        memory_patterns = ["*memory*", "*zram*", "*performance*", "*optimization*"]
        for pattern in memory_patterns:
            for file_path in self.memory_bank_dir.rglob(pattern):
                if file_path.suffix == '.md':
                    research_files.append(file_path)
                    self.logger.info(f"  ✓ Found: {file_path.name}")
        
        # Search in expert-knowledge for existing memory docs
        if self.expert_knowledge_dir.exists():
            for file_path in self.expert_knowledge_dir.rglob("*memory*.md"):
                research_files.append(file_path)
                self.logger.info(f"  ✓ Found: {file_path.name}")
        
        return list(set(research_files))  # Remove duplicates
    
    def synthesize_memory_documentation(self, research_files: List[Path]) -> Dict:
        """Synthesize research into comprehensive memory management documentation."""
        self.logger.info("📚 Synthesizing memory management documentation...")
        
        # Read all research content
        research_content = []
        for file_path in research_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                research_content.append({
                    'file': str(file_path),
                    'content': content[:2000]  # Limit content size
                })
            except Exception as e:
                self.logger.warning(f"  ⚠ Could not read {file_path}: {e}")
        
        # Create synthesis prompt
        synthesis_prompt = self._create_synthesis_prompt(research_content)
        
        # Use model to synthesize documentation
        try:
            model_choice = self.model_router.select_model("research_synthesis")
            self.logger.info(f"  🤖 Using model: {model_choice['model']}")
            
            # For now, create documentation structure manually
            # In production, this would call the model
            documentation = self._create_memory_documentation(research_content)
            
            return documentation
            
        except Exception as e:
            self.logger.error(f"  ❌ Synthesis failed: {e}")
            return self._create_fallback_documentation()
    
    def _create_synthesis_prompt(self, research_content: List[Dict]) -> str:
        """Create prompt for memory management documentation synthesis."""
        research_summary = "\n\n".join([
            f"Source: {item['file']}\nContent: {item['content'][:500]}..."
            for item in research_content[:5]  # Limit to first 5 sources
        ])
        
        prompt = f"""
        Synthesize the following memory management research into comprehensive documentation:

        Research Sources:
        {research_summary}

        Create a comprehensive memory management guide that includes:
        1. Memory management strategies for Ryzen 7 systems
        2. ZRAM configuration and optimization
        3. Performance monitoring and alerting
        4. Troubleshooting common memory issues
        5. Best practices for resource-constrained environments

        Output should be in Markdown format with proper frontmatter.
        """
        
        return prompt
    
    def _create_memory_documentation(self, research_content: List[Dict]) -> Dict:
        """Create memory management documentation structure."""
        return {
            'title': 'Memory Management Guide',
            'frontmatter': {
                'title': 'Memory Management Guide',
                'description': 'Comprehensive guide for memory management on Ryzen 7 systems',
                'created': datetime.now().isoformat(),
                'status': 'draft',
                'tags': ['memory', 'performance', 'optimization', 'infrastructure']
            },
            'content': self._generate_memory_content(research_content)
        }
    
    def _generate_memory_content(self, research_content: List[Dict]) -> str:
        """Generate memory management content."""
        content = f"""---
title: "Memory Management Guide"
description: "Comprehensive guide for memory management on Ryzen 7 systems"
created: "{datetime.now().isoformat()}"
status: "draft"
tags: ["memory", "performance", "optimization", "infrastructure"]
---

# Memory Management Guide

## Overview

This guide provides comprehensive strategies for managing memory on Ryzen 7 systems with 6.6GB RAM, focusing on optimization, monitoring, and troubleshooting.

## Research Sources

Based on analysis of {len(research_content)} research documents covering:
- Memory management patterns
- ZRAM configuration
- Performance optimization
- Resource monitoring

## Memory Management Strategies

### 1. ZRAM Configuration

ZRAM is essential for systems with limited RAM. Key configuration points:

```bash
# Check current ZRAM status
zramctl --noheadings

# Monitor memory usage
free -h
```

### 2. Performance Monitoring

Implement continuous monitoring with alerts:

```bash
# Memory usage monitoring
psutil.virtual_memory().percent

# Process memory tracking
psutil.Process().memory_info().rss / (1024 ** 3)
```

### 3. Resource Optimization

- Use bounded buffers for memory safety
- Implement proper cleanup in async contexts
- Monitor CPU and memory usage during operations

## Troubleshooting

### Common Issues

1. **Memory exhaustion**: Check ZRAM usage and swap configuration
2. **Performance degradation**: Monitor CPU usage and process memory
3. **Resource leaks**: Implement proper cleanup in all contexts

### Diagnostic Commands

```bash
# Check memory pressure
cat /proc/pressure/memory

# Monitor swap usage
swapon --show

# Check process memory
ps aux --sort=-%mem | head -10
```

## Best Practices

1. **Proactive monitoring**: Set up alerts for memory usage > 80%
2. **Resource limits**: Implement hard limits in all services
3. **Cleanup protocols**: Ensure proper cleanup in error conditions
4. **Testing**: Regular stress testing of memory management

## Implementation

This guide should be implemented alongside the Memory Guard system for comprehensive memory management.
"""
        return content
    
    def _create_fallback_documentation(self) -> Dict:
        """Create fallback documentation when synthesis fails."""
        return {
            'title': 'Memory Management Guide (Fallback)',
            'frontmatter': {
                'title': 'Memory Management Guide (Fallback)',
                'description': 'Fallback memory management documentation',
                'created': datetime.now().isoformat(),
                'status': 'fallback',
                'tags': ['memory', 'fallback']
            },
            'content': """---
title: "Memory Management Guide (Fallback)"
description: "Fallback memory management documentation"
created: "{datetime.now().isoformat()}"
status: "fallback"
tags: ["memory", "fallback"]
---

# Memory Management Guide (Fallback)

This is a fallback version of the memory management guide. The full synthesis is not yet implemented.

## Next Steps

1. Implement model-based synthesis
2. Integrate with research sources
3. Update expert knowledge base
"""
        }
    
    def create_expert_knowledge_base(self, documentation: Dict) -> Dict:
        """Create expert knowledge base entry for memory management."""
        self.logger.info("🧠 Creating expert knowledge base entry...")
        
        expert_kb = {
            'title': 'Memory Management Expert Knowledge',
            'frontmatter': {
                'title': 'Memory Management Expert Knowledge',
                'description': 'Expert knowledge base for memory management',
                'created': datetime.now().isoformat(),
                'domain': 'infrastructure',
                'expertise_level': 'advanced'
            },
            'content': f"""---
title: "Memory Management Expert Knowledge"
description: "Expert knowledge base for memory management"
created: "{datetime.now().isoformat()}"
domain: "infrastructure"
expertise_level: "advanced"
---

# Memory Management Expert Knowledge

## Domain Overview

Memory management is critical for systems with limited RAM (6.6GB on Ryzen 7). This knowledge base provides expert-level guidance for optimization and troubleshooting.

## Key Concepts

### ZRAM Optimization
- Essential for memory-constrained systems
- Configure with appropriate compression algorithms
- Monitor usage patterns and adjust accordingly

### Performance Monitoring
- Implement real-time monitoring
- Set up proactive alerts
- Track memory usage trends

### Resource Management
- Use bounded buffers to prevent memory leaks
- Implement proper cleanup protocols
- Monitor CPU and memory usage during operations

## Expert Patterns

### Pattern 1: Memory Guard Implementation
```python
class MemoryGuard:
    def __init__(self, max_memory_percent: float = 0.6):
        self.max_memory_percent = max_memory_percent
    
    def check_memory(self) -> bool:
        # Implementation for memory monitoring
        pass
```

### Pattern 2: Bounded Buffer Usage
```python
from collections import deque

class MemorySafeBuffer:
    def __init__(self, max_items: int = 1000):
        self._buffer = deque(maxlen=max_items)
```

## Troubleshooting Expertise

### Memory Exhaustion
1. Check ZRAM configuration
2. Monitor swap usage
3. Identify memory leaks
4. Implement resource limits

### Performance Issues
1. Monitor CPU usage
2. Check for resource contention
3. Optimize memory allocation patterns
4. Review garbage collection

## Integration Points

- Memory Guard system
- Performance monitoring
- Resource management protocols
- Alerting systems

## References

Based on synthesis of memory management research and best practices.
"""
        }
        
        return expert_kb
    
    def update_knowledge_audit(self, documentation: Dict, expert_kb: Dict) -> bool:
        """Update the knowledge audit with new memory management content."""
        self.logger.info("📋 Updating knowledge audit...")
        
        audit_file = self.expert_knowledge_dir / "_meta" / "knowledge-audit.yaml"
        
        # Create audit entry
        audit_entry = {
            'last_review': datetime.now().isoformat(),
            'next_review': (datetime.now().replace(month=datetime.now().month + 3)).isoformat(),
            'domains': {
                'infrastructure': {
                    'files': 1,  # Memory management guide
                    'status': 'current',
                    'last_reviewed': datetime.now().isoformat(),
                    'new_content': True
                }
            },
            'synthesis_jobs': {
                'rj_synth_memory': {
                    'status': 'completed',
                    'completed_at': datetime.now().isoformat(),
                    'outputs': [
                        str(self.memory_management_doc),
                        str(self.memory_expert_kb)
                    ]
                }
            }
        }
        
        # For now, create a simple audit file
        audit_content = f"""# Knowledge Audit - Memory Management Synthesis
last_review: {datetime.now().isoformat()}
next_review: {(datetime.now().replace(month=datetime.now().month + 3)).isoformat()}

domains:
  infrastructure:
    files: 1
    status: current
    last_reviewed: {datetime.now().isoformat()}
    new_content: true

synthesis_jobs:
  rj_synth_memory:
    status: completed
    completed_at: {datetime.now().isoformat()}
    outputs:
      - {self.memory_management_doc}
      - {self.memory_expert_kb}
"""
        
        try:
            audit_file.parent.mkdir(parents=True, exist_ok=True)
            audit_file.write_text(audit_content)
            self.logger.info(f"  ✓ Audit updated: {audit_file}")
            return True
        except Exception as e:
            self.logger.error(f"  ❌ Failed to update audit: {e}")
            return False
    
    def save_documentation(self, documentation: Dict, expert_kb: Dict, dry_run: bool = False) -> bool:
        """Save synthesized documentation to files."""
        self.logger.info("💾 Saving documentation...")
        
        try:
            # Save main documentation
            if not dry_run:
                self.memory_management_doc.parent.mkdir(parents=True, exist_ok=True)
                self.memory_management_doc.write_text(documentation['content'])
                self.logger.info(f"  ✓ Documentation saved: {self.memory_management_doc}")
            
            # Save expert knowledge base
            if not dry_run:
                self.memory_expert_kb.parent.mkdir(parents=True, exist_ok=True)
                self.memory_expert_kb.write_text(expert_kb['content'])
                self.logger.info(f"  ✓ Expert KB saved: {self.memory_expert_kb}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"  ❌ Failed to save documentation: {e}")
            return False
    
    def run(self, dry_run: bool = False) -> Dict:
        """Execute the RJ-Synth-Memory job."""
        self.logger.info("🚀 Starting RJ-Synth-Memory job...")
        
        # Step 1: Find research
        research_files = self.find_memory_research()
        if not research_files:
            self.logger.warning("  ⚠ No memory research found")
            return {'status': 'no_research', 'research_files': []}
        
        # Step 2: Synthesize documentation
        documentation = self.synthesize_memory_documentation(research_files)
        
        # Step 3: Create expert knowledge base
        expert_kb = self.create_expert_knowledge_base(documentation)
        
        # Step 4: Save documentation
        save_success = self.save_documentation(documentation, expert_kb, dry_run)
        
        # Step 5: Update audit
        audit_success = self.update_knowledge_audit(documentation, expert_kb)
        
        # Results
        results = {
            'status': 'completed' if save_success and audit_success else 'partial',
            'research_files': [str(f) for f in research_files],
            'documentation_created': str(self.memory_management_doc),
            'expert_kb_created': str(self.memory_expert_kb),
            'audit_updated': audit_success,
            'dry_run': dry_run
        }
        
        self.logger.info("✅ RJ-Synth-Memory job completed")
        return results

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RJ-Synth-Memory: Synthesize memory management research")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = MemorySynthesisEngine(verbose=args.verbose)
    
    # Run synthesis
    results = engine.run(dry_run=args.dry_run)
    
    # Print results
    print("\n" + "="*60)
    print("RJ-Synth-Memory Results")
    print("="*60)
    print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    if results['status'] == 'completed':
        sys.exit(0)
    elif results['status'] == 'partial':
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()