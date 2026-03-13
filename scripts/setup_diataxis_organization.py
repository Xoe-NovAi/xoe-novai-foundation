#!/usr/bin/env python3
"""
Diataxis-Enhanced Phase Organization Setup Script
Creates the complete Diataxis-compliant directory structure and integrates Copilot session-state artifacts.
"""

import os
import shutil
from pathlib import Path

def create_diataxis_structure():
    """Create the complete Diataxis-compliant phase directory structure."""
    base_path = Path("internal_docs/01-strategic-planning")
    
    # Create main directories
    directories = [
        "phases",
        "PHASE-EXECUTION-INDEXES", 
        "session-state-organization"
    ]
    
    for directory in directories:
        (base_path / directory).mkdir(exist_ok=True)
    
    # Create Diataxis phase subdirectories
    for phase_num in range(0, 17):
        phase_dir = base_path / "phases" / f"PHASE-{phase_num}"
        
        # Create Diataxis categories
        diataxis_categories = [
            "🚀 TUTORIALS",
            "🛠️ HOW-TO-GUIDES", 
            "📖 REFERENCE",
            "🧠 EXPLANATION"
        ]
        
        for category in diataxis_categories:
            (phase_dir / category).mkdir(parents=True, exist_ok=True)
        
        # Create standard subdirectories
        subdirs = ["resources", "progress", "ai-generated-insights", "faiss-index"]
        for subdir in subdirs:
            (phase_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # Create README template
        create_diataxis_phase_readme(phase_dir, phase_num)
    
    # Create index files
    create_diataxis_master_index(base_path)
    create_diataxis_phase_indexes(base_path)
    
    # Create session-state organization
    create_session_state_organization(base_path)
    
    print("✅ Diataxis structure created successfully!")

def create_diataxis_phase_readme(phase_dir, phase_num):
    """Create a Diataxis-compliant README for each phase."""
    readme_content = f"""# Phase {phase_num}: [Phase Name]
**Status**: Planning  
**Duration**: [X weeks] | **Complexity**: [1-5] | **Impact**: [Low/Medium/High/Critical]  
**Owner**: [Team/Agent] | **Dependencies**: [Previous phases]

## 🎯 Phase Overview
[Brief description of what this phase accomplishes]

## 📋 Diataxis Navigation

### 🚀 Tutorials (Learning)
Learn the fundamentals of this phase:
- [Getting Started](🚀 TUTORIALS/getting-started.md)
- [Quick Start](🚀 TUTORIALS/quick-start.md)
- [Learning Path](🚀 TUTORIALS/learning-path.md)

### 🛠️ How-to Guides (Problem-Solving)  
Solve specific problems in this phase:
- [Implementation Guide](🛠️ HOW-TO-GUIDES/implementation-guide.md)
- [Troubleshooting](🛠️ HOW-TO-GUIDES/troubleshooting.md)
- [Best Practices](🛠️ HOW-TO-GUIDES/best-practices.md)

### 📖 Reference (Information)
Technical specifications and references:
- [API Reference](📖 REFERENCE/api-reference.md)
- [Configuration](📖 REFERENCE/configuration.md)
- [Technical Specs](📖 REFERENCE/technical-specs.md)

### 🧠 Explanation (Understanding)
Conceptual understanding and architecture:
- [Architecture Overview](🧠 EXPLANATION/architecture.md)
- [Design Decisions](🧠 EXPLANATION/design-decisions.md)
- [Phase Explanation](🧠 EXPLANATION/phase-explanation.md)

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

def create_diataxis_master_index(base_path):
    """Create the Diataxis-compliant master navigation index."""
    index_content = """# Master Navigation Index - Diataxis Framework
**Last Updated**: February 17, 2026  
**Purpose**: Central navigation hub for all 16 phases with Diataxis categorization

## 🗺️ Quick Navigation

### By Phase
"""
    
    for phase_num in range(0, 17):
        index_content += f"- [Phase {phase_num}](phases/PHASE-{phase_num}/00-README-PHASE-{phase_num}.md)\n"
    
    index_content += """
### By Diataxis Category

#### 🚀 Tutorials (Learning)
Learn the fundamentals across all phases:
"""
    
    for phase_num in range(0, 17):
        index_content += f"- [Phase {phase_num} Tutorials](phases/PHASE-{phase_num}/🚀 TUTORIALS/)\n"
    
    index_content += """
#### 🛠️ How-to Guides (Problem-Solving)
Solve specific problems across all phases:
"""
    
    for phase_num in range(0, 17):
        index_content += f"- [Phase {phase_num} How-to Guides](phases/PHASE-{phase_num}/🛠️ HOW-TO-GUIDES/)\n"
    
    index_content += """
#### 📖 Reference (Information)
Technical specifications across all phases:
"""
    
    for phase_num in range(0, 17):
        index_content += f"- [Phase {phase_num} Reference](phases/PHASE-{phase_num}/📖 REFERENCE/)\n"
    
    index_content += """
#### 🧠 Explanation (Understanding)
Conceptual understanding across all phases:
"""
    
    for phase_num in range(0, 17):
        index_content += f"- [Phase {phase_num} Explanation](phases/PHASE-{phase_num}/🧠 EXPLANATION/)\n"
    
    index_content += """
## 🤖 Agent Navigation

### For AI Agents
1. Start at the appropriate phase README
2. Use Diataxis categories to find relevant content
3. Use semantic search for specific topics
4. Follow dependency links for related phases
5. Check progress logs for current status

### Common Agent Queries
- "Find Phase 5 implementation documents"
- "What are the dependencies for Phase 8?"
- "Show me research documents for Phase 3"
- "Find tutorials for Phase 1"

---

**Note**: This index is automatically updated when new phases are added.
"""
    
    with open(base_path / "PHASE-EXECUTION-INDEXES" / "00-MASTER-NAVIGATION-INDEX.md", "w") as f:
        f.write(index_content)

def create_diataxis_phase_indexes(base_path):
    """Create Diataxis-compliant individual phase indexes."""
    for phase_num in range(0, 17):
        index_content = f"""# Phase {phase_num} Index - Diataxis Framework
**Phase**: {phase_num} | **Created**: February 17, 2026  
**Purpose**: Complete document inventory for Phase {phase_num} with Diataxis categorization

## 📁 Document Inventory

### 🚀 Tutorials (Learning)
Learn the fundamentals of Phase {phase_num}:
- [Getting Started](../phases/PHASE-{phase_num}/🚀 TUTORIALS/getting-started.md)
- [Quick Start](../phases/PHASE-{phase_num}/🚀 TUTORIALS/quick-start.md)
- [Learning Path](../phases/PHASE-{phase_num}/🚀 TUTORIALS/learning-path.md)

### 🛠️ How-to Guides (Problem-Solving)
Solve specific problems in Phase {phase_num}:
- [Implementation Guide](../phases/PHASE-{phase_num}/🛠️ HOW-TO-GUIDES/implementation-guide.md)
- [Troubleshooting](../phases/PHASE-{phase_num}/🛠️ HOW-TO-GUIDES/troubleshooting.md)
- [Best Practices](../phases/PHASE-{phase_num}/🛠️ HOW-TO-GUIDES/best-practices.md)

### 📖 Reference (Information)
Technical specifications for Phase {phase_num}:
- [API Reference](../phases/PHASE-{phase_num}/📖 REFERENCE/api-reference.md)
- [Configuration](../phases/PHASE-{phase_num}/📖 REFERENCE/configuration.md)
- [Technical Specs](../phases/PHASE-{phase_num}/📖 REFERENCE/technical-specs.md)

### 🧠 Explanation (Understanding)
Conceptual understanding of Phase {phase_num}:
- [Architecture Overview](../phases/PHASE-{phase_num}/🧠 EXPLANATION/architecture.md)
- [Design Decisions](../phases/PHASE-{phase_num}/🧠 EXPLANATION/design-decisions.md)
- [Phase Explanation](../phases/PHASE-{phase_num}/🧠 EXPLANATION/phase-explanation.md)

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

def create_session_state_organization(base_path):
    """Create session-state organization structure and mapping."""
    session_org_dir = base_path / "session-state-organization"
    
    # Create session-state organization structure
    (session_org_dir / "mappings").mkdir(exist_ok=True)
    (session_org_dir / "migrated").mkdir(exist_ok=True)
    (session_org_dir / "archive").mkdir(exist_ok=True)
    
    # Create session-to-phase mapping
    mapping_content = """# Session-State to Phase Mapping

## Date-Based Mapping
| Session ID | Date Modified | Mapped Phase | Content Type | Destination | Status |
|------------|---------------|--------------|--------------|-------------|--------|
| 803a2811-658a-48f5-a572-0bc9d077b89f | Feb 17 01:29 | Phase 2 | Completion Report | phases/PHASE-2/🧠 EXPLANATION/ | ✅ Migrated |
| 6de50880-2c00-4a90-b974-ce708aab09a2 | Feb 17 00:00 | Phase 1 | Session Artifacts | phases/PHASE-1/ | ⏳ Pending |
| edef43d2-fc6c-4f9b-82a9-9691dcec40e1 | Feb 16 23:54 | Phase 1 | Session Artifacts | phases/PHASE-1/ | ⏳ Pending |
| 600a4354-1bd2-4f7c-aacd-366110f48273 | Feb 16 22:09 | Phase 7 | Comprehensive | phases/PHASE-7/ | ⏳ Pending |
| 392fed92-9f81-4db6-afe4-8729d6f28e1b | Feb 16 08:11 | Phase 0 | Audit Plan | phases/PHASE-0/🚀 TUTORIALS/ | ⏳ Pending |
| f0d96237-97be-4cbc-964e-92a5db367068 | Feb 15 16:01 | Phase 6 | Session Artifacts | phases/PHASE-6/ | ⏳ Pending |

## Content Classification
### 🧠 Explanation Content
- Completion reports
- Architecture overviews
- Design decisions
- Phase explanations

### 🚀 Tutorial Content
- Getting started guides
- Learning paths
- Setup instructions
- Audit plans

### 🛠️ How-to Guide Content
- Implementation guides
- Troubleshooting guides
- Best practices
- Configuration guides

### 📖 Reference Content
- Technical specifications
- API documentation
- Configuration references
- Command references

## Migration Status
- ✅ Phase 0: Audit plan migrated to tutorials
- ✅ Phase 2: Completion report migrated to explanation
- ⏳ Phase 1: Session artifacts pending analysis
- ⏳ Phase 6: Session artifacts pending analysis
- ⏳ Phase 7: Comprehensive artifacts pending analysis

## Next Steps
1. Analyze remaining session artifacts
2. Classify content by Diataxis category
3. Migrate to appropriate phase directories
4. Update cross-references
5. Validate MkDocs integration
"""
    
    with open(session_org_dir / "MAPPING.md", "w") as f:
        f.write(mapping_content)
    
    print("✅ Session-state organization created successfully!")

if __name__ == "__main__":
    create_diataxis_structure()
    print("🎉 Diataxis organization setup complete!")