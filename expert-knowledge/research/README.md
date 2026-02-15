# Research Queue System

**Version**: 1.0.0  
**Status**: Operational  
**Last Updated**: 2026-02-13

## Overview

The Research Queue System provides structured research request submission, assignment, and tracking for the Xoe-NovAi team. It ensures research is systematically captured, prioritized, and integrated into the expert-knowledge repository.

## Quick Start

### Submitting a Research Request

**Option 1: Quick Submission** (for rapid logging)
```bash
# Create a quick request
cat > expert-knowledge/research/queue/pending/quick-req-$(date +%Y%m%d)-001.md << 'EOF'
**ID**: Quick-REQ-YYYYMMDD-001
**Type**: [model-research|technical|strategic|debug]
**Question**: [Your question]
**Priority**: [critical|high|medium|low]
**Submitted**: [Your name]
EOF
```

**Option 2: Full Template**
1. Copy `expert-knowledge/research/_templates/RESEARCH-REQUEST-TEMPLATE.md`
2. Fill in all sections
3. Save to `expert-knowledge/research/queue/pending/REQ-YYYY-MM-DD-XXX.md`

### Checking Queue Status

```bash
# View queue index
cat expert-knowledge/research/index.json

# List pending requests
ls -la expert-knowledge/research/queue/pending/

# View specific request
cat expert-knowledge/research/queue/pending/REQ-2026-02-13-001-big-pickle-analysis.md
```

### For Agents: Claiming and Completing Research

1. **Claim Request**: Move from `pending/` to `assigned/`
2. **Update Status**: Edit request file, set `status: "IN_PROGRESS"`
3. **Execute Research**: Follow methodology in request
4. **Document Findings**: Save to `completed/findings/`
5. **Complete Request**: Move to `completed/reports/`, update status to "COMPLETED"
6. **Integrate**: Move findings to appropriate expert-knowledge location
7. **Archive**: Move request to `queue/archive/`

## Directory Structure

```
expert-knowledge/research/
├── README.md                           # This file
├── research-request-system-v1.0.0.md  # Full system documentation
├── _templates/
│   └── RESEARCH-REQUEST-TEMPLATE.md   # Request template
├── queue/
│   ├── pending/                        # New requests
│   ├── prioritized/                    # Triaged and prioritized
│   ├── assigned/                       # Assigned to agents
│   └── archive/                        # Completed/cancelled
├── completed/
│   ├── findings/                       # Raw research outputs
│   └── reports/                        # Synthesized reports
└── index.json                          # Queue status index
```

## Request States

- **PENDING** → Submitted, awaiting triage
- **PRIORITIZED** → Triaged, awaiting assignment
- **ASSIGNED** → Assigned to specific agent
- **IN_PROGRESS** → Active research
- **COMPLETED** → Research done, findings captured
- **INTEGRATED** → Findings moved to expert-knowledge
- **ARCHIVED** → Request complete or cancelled

## Current Queue Status

See `index.json` for real-time queue status.

**Current Requests**:
1. REQ-2026-02-13-001: Big Pickle Model Analysis (HIGH)
2. REQ-2026-02-13-002: GPT-5 Nano Efficiency Analysis (MEDIUM)
3. REQ-2026-02-13-003: OpenCode Comparison Matrix (HIGH, blocked)

## Research Types

- **model-research**: AI model analysis, comparisons, capabilities
- **technical**: Technology investigation, integration research
- **strategic**: Architecture decisions, ecosystem analysis
- **debug**: Root cause analysis, problem investigation
- **comparison**: Comparative analysis between options

## Priority Levels

| Priority | Response Time | Use Case |
|----------|---------------|----------|
| **Critical** | 4-8 hours | Blockers, urgent decisions |
| **High** | 24 hours | Important features, blocking soon |
| **Medium** | 3-5 days | Optimization, planning |
| **Low** | 1-2 weeks | Background, nice-to-know |

## Agent Responsibilities

**Grok MC**:
- Daily queue triage
- Priority assignment
- Strategic research execution

**OpenCode**:
- Model research
- Technical deep-dives
- Multi-model validation

**Gemini CLI**:
- Verification tasks
- Ground truth validation

**Cline**:
- Implementation-focused research
- Code-heavy investigations

## Integration Workflow

Research findings should be integrated into:

1. **Model Research** → `expert-knowledge/model-reference/`
2. **Technical Research** → `expert-knowledge/<domain>/`
3. **Strategic Research** → `expert-knowledge/architect/` or `memory_bank/`
4. **Debug Research** → Project docs + `memory_bank/progress.md`

## Best Practices

1. **Clear Questions**: Ensure research questions are specific and answerable
2. **Context Matters**: Always provide background and related resources
3. **Success Criteria**: Define what "done" looks like
4. **Regular Updates**: Update status as work progresses
5. **Integration**: Don't let completed research sit in queue - integrate it!

## Examples

### Example 1: Model Research
```markdown
**ID**: REQ-2026-02-13-001
**Type**: model-research
**Question**: What is Big Pickle and when should we use it?
**Priority**: high
**Submitted**: OpenCode-Kimi-X
```

### Example 2: Technical Investigation
```markdown
**ID**: REQ-2026-02-20-005
**Type**: technical
**Question**: How does Podman rootless networking compare to Docker?
**Priority**: medium
**Submitted**: Cline-Trinity
```

### Example 3: Strategic Analysis
```markdown
**ID**: REQ-2026-03-01-012
**Type**: strategic
**Question**: Should we adopt WebAssembly for XNAi plugins?
**Priority**: high
**Submitted**: Grok MC
```

## Ma'at Alignment

- **Ideal 7 (Truth)**: Research truthfully reports findings and limitations
- **Ideal 18 (Balance)**: Systematic approach without bureaucracy
- **Ideal 36 (Integrity)**: Research is completed thoroughly
- **Ideal 41 (Advance)**: Research expands team capabilities

## Support

- **System Documentation**: `research-request-system-v1.0.0.md`
- **Request Template**: `_templates/RESEARCH-REQUEST-TEMPLATE.md`
- **Questions**: Ask Grok MC or OpenCode-Kimi-X

---

**Status**: ✅ System Operational  
**Next Review**: 2026-02-20
