# OpenCode Skills Recommendations

## Overview

Skills define reusable workflows in OpenCode. This document covers recommended skills for the XNAi Foundation project.

## Core Skills

### 1. memory-bank-loader

**Purpose**: Automatically load project context from memory_bank/.

**Trigger**: Session start, before architectural decisions.

**Workflow**:
1. Read `memory_bank/INDEX.md`
2. Load priority files (activeContext, progress, systemPatterns)
3. Assemble working context
4. Validate completeness

**Returns**:
- Current phase
- Top priority
- Active blockers
- Relevant patterns

### 2. agent-bus-coordinator

**Purpose**: Coordinate multiple agents via Redis Streams.

**Trigger**: Multi-agent tasks, parallel execution.

**Workflow**:
1. Analyze task requirements
2. Select appropriate agents
3. Publish task to `xnai:tasks`
4. Monitor heartbeat
5. Collect results from `xnai:results`

**Returns**:
- Active agent count
- Pending tasks
- Completion status
- Circuit breaker state

### 3. phase-validator

**Purpose**: Verify phase completion criteria.

**Trigger**: Phase completion claimed, milestone reached.

**Workflow**:
1. Read current phase from progress.md
2. Check completion criteria
3. Run validation tests
4. Generate report

**Returns**:
- Phase status (READY/BLOCKED/INCOMPLETE)
- Completed items
- Remaining tasks
- Blockers

### 4. sovereign-security-auditor

**Purpose**: Ensure changes meet security standards.

**Trigger**: Before git commit, pre-deployment.

**Workflow**:
1. Scan security-sensitive files
2. Check container security
3. Analyze code for vulnerabilities
4. Verify permissions

**Returns**:
- Security status (PASS/FAIL/WARN)
- Passed checks
- Warnings
- Failures

### 5. doc-taxonomy-writer

**Purpose**: Classify documentation per Diátaxis framework.

**Trigger**: New docs created, taxonomy audit.

**Workflow**:
1. Analyze content
2. Classify by domain and quadrant
3. Update frontmatter
4. Verify placement

**Returns**:
- Classification result
- Recommended location
- Tags
- Dependencies

### 6. vikunja-task-manager

**Purpose**: Create and track tasks in Vikunja.

**Trigger**: New task identified, status change.

**Workflow**:
1. Identify task from request
2. Create task via API
3. Link to memory bank
4. Track progress

**Returns**:
- Task ID
- Title
- Priority
- Next steps

### 7. semantic-search

**Purpose**: Query Foundation RAG API.

**Trigger**: Research needed, context lookup.

**Workflow**:
1. Formulate query
2. Execute search
3. Process results
4. Present findings

**Returns**:
- Query results
- Latency
- Sources
- Relevance scores

## Skill Development

### SKILL.md Template

```markdown
# Skill Name

## Purpose
Brief description of what this skill does.

## Trigger
- Condition 1
- Condition 2

## Workflow

### Step 1: Title
Description of step.

### Step 2: Title
Description of step.

## Output Format
```
## Result Header
- Item 1
- Item 2
```

## Integration
- Works with skill X
- Triggers skill Y
```

### Directory Structure

```
.opencode/skills/
├── memory-bank-loader/
│   └── SKILL.md
├── agent-bus-coordinator/
│   └── SKILL.md
└── ...
```

## Skill Best Practices

### 1. Single Responsibility
Each skill should do one thing well.

### 2. Clear Triggers
Define when skills should activate.

### 3. Explicit Outputs
Document expected return format.

### 4. Error Handling
Include fallback behaviors.

### 5. Integration Points
Reference related skills and agents.

## Skill Chaining

Skills can trigger other skills:

```markdown
## Integration
- Uses `memory-bank-loader` for context
- Triggers `phase-validator` after completion
- Notifies `vikunja-task-manager` of changes
```

## Activation Modes

| Mode | Description |
|------|-------------|
| `auto` | Automatically triggered |
| `manual` | Explicitly invoked |
| `conditional` | Triggered by conditions |

## Performance Targets

| Skill | Target Latency |
|-------|----------------|
| memory-bank-loader | <500ms |
| semantic-search | <300ms |
| phase-validator | <1s |
| sovereign-security-auditor | <2s |

## Testing Skills

```bash
# Run skill directly
opencode --skill memory-bank-loader

# Test with verbose output
opencode --skill semantic-search --verbose

# Dry run
opencode --skill phase-validator --dry-run
```
