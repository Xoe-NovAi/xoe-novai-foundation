#!/usr/bin/env python3
"""
Phase Organization Setup Script
Creates the complete directory structure and templates for 16-phase organization.
"""

import os
import shutil
from pathlib import Path

def create_phase_structure():
    """Create the complete phase directory structure."""
    base_path = Path("internal_docs/01-strategic-planning")
    
    # Create main directories
    directories = [
        "phases",
        "PHASE-EXECUTION-INDEXES", 
        "research-phases"
    ]
    
    for directory in directories:
        (base_path / directory).mkdir(exist_ok=True)
    
    # Create phase subdirectories
    for phase_num in range(0, 17):
        phase_dir = base_path / "phases" / f"PHASE-{phase_num}"
        subdirs = ["resources", "progress", "ai-generated-insights", "faiss-index"]
        
        for subdir in subdirs:
            (phase_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # Create README template
        create_phase_readme(phase_dir, phase_num)
    
    # Create index files
    create_master_index(base_path)
    create_phase_indexes(base_path)
    
    print("✅ Phase structure created successfully!")

def create_phase_readme(phase_dir, phase_num):
    """Create a standardized README for each phase."""
    readme_content = f"""# Phase {phase_num}: [Phase Name]
**Status**: Planning  
**Duration**: [X weeks] | **Complexity**: [1-5] | **Impact**: [Low/Medium/High/Critical]  
**Owner**: [Team/Agent] | **Dependencies**: [Previous phases]

## 📋 Overview
[Brief description of what this phase accomplishes]

## 🎯 Objectives
- [ ] Objective 1
- [ ] Objective 2
- [ ] Objective 3

## 📁 Documents
- **Executive Roadmap**: [Link to executive overview]
- **Implementation Plan**: [Link to detailed plan]
- **Tasks & Deliverables**: [Link to task list]
- **Progress Log**: [Link to progress tracking]
- **Completion Report**: [Link to final results]

## 🔗 Dependencies
- **Previous Phase**: [Link to previous phase]
- **Next Phase**: [Link to next phase]
- **Parallel Phases**: [Link to concurrent phases]

## 📊 Status Tracking
- **Start Date**: [Date]
- **End Date**: [Date]
- **Progress**: [0-100%]
- **Blockers**: [List of blockers]

## 🤖 Agent Notes
- **Key Documents**: [Most important documents for agents]
- **Common Queries**: [Frequently asked questions]
- **Search Terms**: [Keywords for semantic search]

## 📞 Contacts
- **Phase Owner**: [Contact information]
- **Technical Lead**: [Contact information]
- **QA Lead**: [Contact information]

---

**Last Updated**: [Date]  
**Next Review**: [Date]
"""
    
    with open(phase_dir / f"00-README-PHASE-{phase_num}.md", "w") as f:
        f.write(readme_content)

def create_master_index(base_path):
    """Create the master navigation index."""
    index_content = """# Master Navigation Index
**Last Updated**: February 17, 2026  
**Purpose**: Central navigation hub for all 16 phases

## 🗺️ Quick Navigation

### By Phase
"""
    
    for phase_num in range(0, 17):
        index_content += f"- [Phase {phase_num}](phases/PHASE-{phase_num}/00-README-PHASE-{phase_num}.md)\n"
    
    index_content += """
### By Category
- [Executive Roadmaps](#executive-roadmaps)
- [Implementation Plans](#implementation-plans)
- [Research Documents](#research-documents)
- [Progress Reports](#progress-reports)

### By Status
- [Planning](#planning)
- [In Progress](#in-progress)
- [Complete](#complete)

## 📚 Document Categories

### Executive Roadmaps
[Links to high-level phase overviews]

### Implementation Plans
[Links to detailed execution plans]

### Research Documents
[Links to research and analysis documents]

### Progress Reports
[Links to status and completion reports]

## 🔍 Search Tools

### Semantic Search
Use Qdrant to search for documents by content:
```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)
results = client.search("phase-5", "memory optimization", top=5)
```

### Redis Index
Quick document lookup by phase:
```bash
redis-cli HGETALL "doc:phase:5:resources"
```

## 🤖 Agent Navigation

### For AI Agents
1. Start at the appropriate phase README
2. Use semantic search for specific topics
3. Follow dependency links for related phases
4. Check progress logs for current status

### Common Agent Queries
- "Find Phase 5 implementation documents"
- "What are the dependencies for Phase 8?"
- "Show me research documents for Phase 3"

## 📞 Support

### Documentation Team
- **Lead**: [Contact]
- **Support**: [Contact]

### Technical Support
- **Infrastructure**: [Contact]
- **Search Tools**: [Contact]

---

**Note**: This index is automatically updated when new phases are added.
"""
    
    with open(base_path / "PHASE-EXECUTION-INDEXES" / "00-MASTER-NAVIGATION-INDEX.md", "w") as f:
        f.write(index_content)

def create_phase_indexes(base_path):
    """Create individual phase indexes."""
    for phase_num in range(0, 17):
        index_content = f"""# Phase {phase_num} Index
**Phase**: {phase_num} | **Created**: February 17, 2026  
**Purpose**: Complete document inventory for Phase {phase_num}

## 📁 Document Inventory

### Executive Documents
- [Phase {phase_num} Executive Roadmap](../phases/PHASE-{phase_num}/PHASE-{phase_num}-EXECUTIVE-ROADMAP.md)
- [Phase {phase_num} Completion Report](../phases/PHASE-{phase_num}/PHASE-{phase_num}-COMPLETION-REPORT.md)

### Implementation Documents
- [Phase {phase_num} Implementation Plan](../phases/PHASE-{phase_num}/PHASE-{phase_num}-IMPLEMENTATION-PLAN.md)
- [Phase {phase_num} Tasks & Deliverables](../phases/PHASE-{phase_num}/PHASE-{phase_num}-TASKS-AND-DELIVERABLES.md)

### Progress Documents
- [Phase {phase_num} Progress Log](../phases/PHASE-{phase_num}/progress/PHASE-{phase_num}-PROGRESS-LOG.md)

### Research Documents
[Links to research documents in resources/]

### Agent Documents
[Links to agent-specific documents in ai-generated-insights/]

## 🔗 Cross-Phase Dependencies

### Previous Phase
[Link to previous phase]

### Next Phase
[Link to next phase]

### Parallel Phases
[Links to concurrent phases]

## 🤖 Agent Resources

### Key Documents
[List of most important documents for agents]

### Search Terms
[List of keywords for semantic search]

### Common Queries
[List of frequently asked questions]

---

**Last Updated**: [Date]  
**Next Review**: [Date]
"""
        
        with open(base_path / "PHASE-EXECUTION-INDEXES" / f"{phase_num:02d}-PHASE-{phase_num}-INDEX.md", "w") as f:
            f.write(index_content)

if __name__ == "__main__":
    create_phase_structure()
    print("🎉 Phase organization setup complete!")