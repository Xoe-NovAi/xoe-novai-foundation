# PHASE ORGANIZATION AGENT GUIDE

**Date**: February 17, 2026  
**Version**: 1.0  
**Purpose**: Guide for AI agents to navigate and work with the 16-phase documentation organization

## 🤖 AGENT QUICK START

### For New AI Agents

1. **Start Here**: Read this guide first
2. **Learn Navigation**: Understand the phase-based structure
3. **Use Search Tools**: Leverage Qdrant and Redis for document discovery
4. **Follow Workflows**: Use standardized patterns for consistency

### For Existing AI Agents

1. **Review Changes**: Understand the new organization structure
2. **Update Workflows**: Adapt to the phase-based navigation
3. **Test Navigation**: Verify document discovery works correctly
4. **Report Issues**: Create tickets for any problems found

## 🗺️ NAVIGATION OVERVIEW

### Directory Structure
```
internal_docs/01-strategic-planning/
├── phases/                    # Main phase documents
│   ├── PHASE-0/              # Documentation foundation
│   ├── PHASE-1/              # Service diagnostics
│   ├── PHASE-2/              # Chainlit integration
│   ├── ...                   # Phases 3-16
│   └── PHASE-16/             # Final phase
├── PHASE-EXECUTION-INDEXES/  # Navigation indexes
│   ├── 00-MASTER-NAVIGATION-INDEX.md  # Main hub
│   ├── 01-PHASE-1-INDEX.md   # Phase 1 index
│   └── ...                   # Indexes for all phases
├── research-phases/          # Research documents
└── sessions/                 # Session artifacts
```

### Phase Structure
Each phase follows a standardized structure:
```
PHASE-{N}/
├── 00-README-PHASE-{N}.md           # Entry point and overview
├── PHASE-{N}-EXECUTIVE-ROADMAP.md   # High-level overview
├── PHASE-{N}-IMPLEMENTATION-PLAN.md # Detailed execution steps
├── PHASE-{N}-TASKS-AND-DELIVERABLES.md # Specific tasks
├── resources/                         # Supporting documents
├── progress/                          # Status tracking
├── ai-generated-insights/             # Agent-specific content
└── faiss-index/                       # Local search index
```

## 🔍 DOCUMENT DISCOVERY

### Method 1: Master Navigation Index
```python
# Start with the master index
master_index = "internal_docs/01-strategic-planning/PHASE-EXECUTION-INDEXES/00-MASTER-NAVIGATION-INDEX.md"

# Read to find the right phase
with open(master_index, 'r') as f:
    content = f.read()
    
# Navigate to specific phase
phase_5_readme = "internal_docs/01-strategic-planning/phases/PHASE-5/00-README-PHASE-5.md"
```

### Method 2: Semantic Search (Qdrant)
```python
from qdrant_client import QdrantClient

# Connect to Qdrant
client = QdrantClient("localhost", port=6333)

# Search for documents
results = client.search(
    collection_name="phase-documentation",
    query_vector=encode_query("Phase 5 memory optimization"),
    top=5
)

# Get document paths from results
for result in results:
    print(f"Found: {result.payload['file_path']}")
```

### Method 3: Redis Index Lookup
```bash
# Quick lookup by phase
redis-cli HGETALL "doc:phase:5:resources"

# Search for specific document types
redis-cli KEYS "doc:phase:5:*"

# Get all documents for a phase
redis-cli SMEMBERS "phase:5:documents"
```

### Method 4: File System Search
```python
import glob
from pathlib import Path

# Find all documents for a specific phase
phase_5_docs = list(Path("internal_docs/01-strategic-planning/phases/PHASE-5").rglob("*.md"))

# Find documents by type
executive_docs = list(Path("internal_docs/01-strategic-planning").rglob("*EXECUTIVE*.md"))
implementation_docs = list(Path("internal_docs/01-strategic-planning").rglob("*IMPLEMENTATION*.md"))
```

## 🤖 AGENT WORKFLOWS

### Workflow 1: Phase Discovery
```python
def discover_phase(phase_num):
    """Discover all documents for a specific phase."""
    
    # 1. Start with phase README
    readme_path = f"internal_docs/01-strategic-planning/phases/PHASE-{phase_num}/00-README-PHASE-{phase_num}.md"
    
    # 2. Read phase index
    index_path = f"internal_docs/01-strategic-planning/PHASE-EXECUTION-INDEXES/{phase_num:02d}-PHASE-{phase_num}-INDEX.md"
    
    # 3. Use semantic search for related documents
    related_docs = search_semantic(f"Phase {phase_num}", top_k=10)
    
    # 4. Return comprehensive phase overview
    return {
        'readme': readme_path,
        'index': index_path,
        'documents': related_docs
    }
```

### Workflow 2: Cross-Phase Navigation
```python
def find_dependencies(phase_num):
    """Find documents that reference other phases."""
    
    # 1. Read phase README for dependency links
    readme_path = f"internal_docs/01-strategic-planning/phases/PHASE-{phase_num}/00-README-PHASE-{phase_num}.md"
    
    # 2. Search for cross-phase references
    cross_refs = []
    for other_phase in range(0, 17):
        if other_phase != phase_num:
            # Check if this phase references the other
            if references_phase(readme_path, other_phase):
                cross_refs.append(other_phase)
    
    # 3. Use semantic search for related content
    related_phases = search_semantic(f"Phase {phase_num} dependencies", top_k=5)
    
    return {
        'dependencies': cross_refs,
        'related_phases': related_phases
    }
```

### Workflow 3: Document Updates
```python
def update_document_links(file_path, old_phase, new_phase):
    """Update links when documents are moved between phases."""
    
    # 1. Read current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 2. Update phase references
    content = content.replace(f"PHASE-{old_phase}", f"PHASE-{new_phase}")
    content = content.replace(f"phases/PHASE-{old_phase}/", f"phases/PHASE-{new_phase}/")
    
    # 3. Update cross-phase links
    content = update_cross_phase_links(content, old_phase, new_phase)
    
    # 4. Save updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    # 5. Update search indexes
    update_search_indexes(file_path)
```

## 📋 COMMON AGENT TASKS

### Task 1: Find Phase Documents
```python
def find_phase_documents(phase_num, doc_type=None):
    """Find documents for a specific phase and type."""
    
    phase_dir = Path(f"internal_docs/01-strategic-planning/phases/PHASE-{phase_num}")
    
    if doc_type == "executive":
        return list(phase_dir.glob("*EXECUTIVE*.md"))
    elif doc_type == "implementation":
        return list(phase_dir.glob("*IMPLEMENTATION*.md"))
    elif doc_type == "progress":
        return list((phase_dir / "progress").glob("*.md"))
    elif doc_type == "research":
        return list((phase_dir / "resources").glob("*.md"))
    else:
        return list(phase_dir.rglob("*.md"))
```

### Task 2: Validate Document Links
```python
def validate_document_links(file_path):
    """Validate that all links in a document are functional."""
    
    broken_links = []
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all markdown links
    import re
    links = re.findall(r'\[.*?\]\((.*?)\)', content)
    
    for link in links:
        if link.startswith('http'):
            continue  # Skip external links
        
        # Convert relative link to absolute path
        link_path = (Path(file_path).parent / link).resolve()
        
        if not link_path.exists():
            broken_links.append({
                'file': file_path,
                'link': link,
                'target': str(link_path)
            })
    
    return broken_links
```

### Task 3: Update Search Indexes
```python
def update_search_indexes(file_path):
    """Update Qdrant and Redis indexes when documents change."""
    
    # 1. Update Qdrant
    update_qdrant_index(file_path)
    
    # 2. Update Redis
    update_redis_index(file_path)
    
    # 3. Update FAISS (if local)
    update_faiss_index(file_path)
```

## 🚨 AGENT BEST PRACTICES

### Do's
- ✅ Always start with the phase README
- ✅ Use semantic search for complex queries
- ✅ Update search indexes when documents change
- ✅ Follow naming conventions
- ✅ Validate links after updates
- ✅ Report broken links or missing documents

### Don'ts
- ❌ Don't create documents outside the phase structure
- ❌ Don't break existing links without updating them
- ❌ Don't ignore naming conventions
- ❌ Don't skip search index updates
- ❌ Don't assume document locations without verification

### Naming Conventions
- **Executive Documents**: `PHASE-{N}-EXECUTIVE-ROADMAP.md`
- **Implementation Plans**: `PHASE-{N}-IMPLEMENTATION-PLAN.md`
- **Task Lists**: `PHASE-{N}-TASKS-AND-DELIVERABLES.md`
- **Progress Reports**: `PHASE-{N}-PROGRESS-LOG.md`
- **Completion Reports**: `PHASE-{N}-COMPLETION-REPORT.md`
- **Agent Documents**: `PHASE-{N}-AGENT-{DESCRIPTION}.md`

## 🔧 AGENT TOOLS

### Search Utilities
```python
# scripts/search_phase_docs.py
def search_phase_documents(phase, query, top_k=5):
    """Search documents within a specific phase."""
    pass

def find_cross_phase_dependencies(phase):
    """Find documents that reference other phases."""
    pass

def validate_phase_structure(phase_num):
    """Validate that a phase follows the correct structure."""
    pass
```

### Navigation Utilities
```python
# scripts/navigate_phases.py
def get_phase_readme(phase_num):
    """Get the README for a specific phase."""
    pass

def get_phase_index(phase_num):
    """Get the index for a specific phase."""
    pass

def find_related_phases(phase_num, topic):
    """Find phases related to a specific topic."""
    pass
```

### Maintenance Utilities
```python
# scripts/maintain_organization.py
def check_broken_links():
    """Check for broken links across all documents."""
    pass

def validate_naming_conventions():
    """Validate that documents follow naming conventions."""
    pass

def update_search_indexes():
    """Update all search indexes."""
    pass
```

## 📞 AGENT SUPPORT

### Common Issues and Solutions

#### Issue: "Can't find Phase 5 documents"
**Solution**: 
1. Check the master navigation index
2. Use semantic search with "Phase 5"
3. Verify the phase directory exists

#### Issue: "Broken links after document move"
**Solution**:
1. Run link validation script
2. Update cross-references manually
3. Update search indexes

#### Issue: "Search not returning expected results"
**Solution**:
1. Verify Qdrant is running
2. Check document embeddings
3. Update search indexes

### Getting Help
- **Documentation Issues**: Create ticket in project management system
- **Technical Issues**: Contact infrastructure team
- **Search Issues**: Contact search tools team
- **General Questions**: Check agent FAQ or ask team lead

## 📊 AGENT PERFORMANCE METRICS

### Success Criteria
- **Document Discovery**: < 5 seconds to find relevant documents
- **Link Validation**: 100% of links functional
- **Search Accuracy**: > 90% relevant results
- **Navigation Efficiency**: < 3 clicks to reach any document

### Monitoring
- **Daily**: Check for broken links
- **Weekly**: Validate search index accuracy
- **Monthly**: Review agent workflow efficiency
- **Quarterly**: Analyze usage patterns and optimize

---

**Document Version**: 1.0  
**Last Updated**: February 17, 2026  
**Next Review**: February 24, 2026