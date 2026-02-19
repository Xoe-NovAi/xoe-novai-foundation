# Doc Taxonomy Writer Skill

## Purpose
Classify and organize documentation according to Diátaxis framework.

## Trigger
- New documentation created
- Documentation moved/renamed
- Taxonomy audit requested

## Diátaxis Framework

| Quadrant | Purpose | Content Type |
|----------|---------|--------------|
| Tutorials | Learning-oriented | Step-by-step guides |
| How-to | Problem-oriented | Task guides |
| Reference | Information-oriented | API docs, specs |
| Explanation | Understanding-oriented | Concepts, design |

## Classification Workflow

### Step 1: Analyze Content
Read document and identify:
- Target audience (beginner/intermediate/expert)
- Primary goal (learn/do/lookup/understand)
- Content structure (steps/reference/concepts)

### Step 2: Classify
Assign domain and quadrant:
```
Domain: [internal/external/api/guides]
Quadrant: [tutorial/howto/reference/explanation]
Confidence: [high/medium/low]
```

### Step 3: Update Frontmatter
```yaml
---
domain: internal
quadrant: tutorial
confidence: high
tags: [setup, getting-started]
dependencies: [prerequisites]
last_updated: 2026-02-17
---
```

### Step 4: Verify Placement
Check file location matches classification:
- `docs/tutorials/` - Learning guides
- `docs/how-to/` - Task guides
- `docs/reference/` - API/specs
- `docs/explanation/` - Concepts

## Directory Structure
```
docs/
├── tutorials/
│   ├── getting-started/
│   └── advanced-topics/
├── how-to/
│   ├── deployment/
│   ├── integration/
│   └── troubleshooting/
├── reference/
│   ├── api/
│   ├── configuration/
│   └── architecture/
└── explanation/
    ├── concepts/
    └── design-decisions/
```

## Classification Rules

### Tutorials
- Step-by-step instructions
- Assumes no prior knowledge
- Teaching fundamental concepts
- Has clear start and end

### How-to Guides
- Problem-focused
- Assumes some knowledge
- Practical task completion
- Multiple valid approaches

### Reference
- Information lookup
- Complete and accurate
- Structured and searchable
- Minimal explanation

### Explanation
- Conceptual understanding
- Background and context
- Why, not how
- Connects related concepts

## Output Format
```
## Taxonomy Classification
File: [path]
Domain: [domain]
Quadrant: [quadrant]
Confidence: [level]

### Recommended Location
[path]

### Tags
[tag1, tag2, tag3]

### Dependencies
[required reading]
```

## Integration
- Works with MkDocs literate-nav
- Updates `SUMMARY.md` navigation
- Notifies `memory-bank-loader` of doc structure
