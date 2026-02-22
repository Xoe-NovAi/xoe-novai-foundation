# Gemini CLI Task Assignment: P-017 AWQ Removal & CLI Ecosystem Audit

**Task ID**: P-017 + CLI-AUDIT-001
**Priority**: P1 (Foundation Hardening)
**Assigned**: Gemini CLI
**Created**: 2026-02-21
**Author**: Cline (with MC Overseer enhancement)

---

## Task Summary

You have been assigned **two related tasks**:

1. **P-017: AWQ Removal & CPU+Vulkan Optimization** - Remove PyTorch-dependent AWQ components
2. **CLI-AUDIT-001: Multi-CLI Ecosystem Congruence Audit** - Ensure all CLI tools have congruent rules, skills, and agents

---

## Part 1: AWQ Removal Task

### Context

XNAi Foundation follows a **torch-free mandate** - no PyTorch dependencies are allowed. The stack is optimized for CPU+Vulkan inference using:
- **llama-cpp-python** with Vulkan + OpenBLAS
- **ONNX Runtime** for neural network inference
- **GGUF quantized models** (q4-q6)
- **Piper TTS** (ONNX) + **Faster-Whisper** (CTranslate2)

**Problem**: AWQ (Activation-aware Weight Quantization) requires PyTorch, creating a dependency conflict.

### Deliverables

1. **Review and enhance** the refactoring guide at `plans/AWQ-REMOVAL-REFACTORING-GUIDE.md`
2. **Create GPU research archive** structure at `expert-knowledge/_archive/gpu-research/`
3. **Document AWQ architecture** for future reference
4. **Break down tasks** into parallelizable groups with clear dependencies

**Important**: This is a **task creation and documentation** assignment. Do NOT modify the codebase directly.

---

## Part 2: CLI Ecosystem Congruence Audit (NEW)

### Objective

Review all CLI configuration folders to ensure rules, skills, and agents are congruent and up-to-date across the entire XNAi ecosystem.

### Folders to Audit

| Folder | CLI Tool | Contents |
|--------|----------|----------|
| `.clinerules/` | Cline CLI | Core rules, memory bank protocol, coding standards |
| `.opencode/` | OpenCode CLI | RULES.md, agents/, skills/, opencode.json |
| `~/.gemini/GEMINI.md` | Gemini CLI | Memories and context (ARCHIVED - redirect to memory_bank/) |
| `AGENTS.md` | All CLIs | Shared agent instructions |

### Audit Tasks

#### Task 1: Rules Congruence Check
Compare rules across all CLI configurations:
- [ ] Compare `.clinerules/` with `.opencode/RULES.md`
- [ ] Check for conflicting instructions
- [ ] Verify all rules reference same model matrix (v3.0.0)
- [ ] Ensure memory bank protocol is consistent
- [ ] Verify torch-free mandate is stated everywhere

#### Task 2: Skills Availability Audit
Ensure all skills are available where needed:

| Skill | OpenCode | Cline | Gemini CLI | Action |
|-------|----------|-------|------------|--------|
| memory-bank-loader | ✅ | ❓ | ❓ | Check/create |
| agent-bus-coordinator | ✅ | ❓ | ❓ | Check/create |
| phase-validator | ✅ | ❓ | ❓ | Check/create |
| sovereign-security-auditor | ✅ | ❓ | ❓ | Check/create |
| doc-taxonomy-writer | ✅ | ❓ | ❓ | Check/create |
| vikunja-task-manager | ✅ | ❓ | ❓ | Check/create |
| semantic-search | ✅ | ❓ | ❓ | Check/create |
| cli-dispatch | ✅ | ❓ | ❓ | Check/create |

#### Task 3: Agents Availability Audit
Ensure all agents are available across CLIs:

| Agent | OpenCode | Cline | Gemini CLI | Action |
|-------|----------|-------|------------|--------|
| architect | ✅ | ❓ | ❓ | Check/create |
| build | ✅ | ❓ | ❓ | Check/create |
| cli-dispatch | ✅ | ❓ | ❓ | Check/create |
| explore | ✅ | ❓ | ❓ | Check/create |
| plan | ✅ | ❓ | ❓ | Check/create |
| research | ✅ | ❓ | ❓ | Check/create |
| review | ✅ | ❓ | ❓ | Check/create |
| security | ✅ | ❓ | ❓ | Check/create |
| mc-overseer | ✅ (NEW) | ❓ | ❓ | Create |

#### Task 4: CLI-Specific Strengths Analysis

Research and document how each CLI can leverage its unique strengths:

**Cline CLI Strengths:**
- VS Code/VSCodium IDE integration
- Large context window (200K+ tokens)
- Visual file editing with diff preview
- Best for: Complex refactoring, multi-file changes, IDE-based development

**Gemini CLI Strengths:**
- 1M token context window (ideal for large codebase analysis)
- Native Google Cloud integration
- Best for: Large-scale research, documentation review, full codebase audits

**OpenCode CLI Strengths:**
- Terminal-native TUI interface
- Skill and agent system
- Antigravity plugin for premium models
- Best for: Terminal workflows, skill-based automation

**Copilot CLI Strengths:**
- Quick terminal coding assistance
- GitHub integration
- Best for: Quick prototyping, git workflows

#### Task 5: Configuration Sync Recommendations

Create recommendations for:
1. Which rules should be shared vs CLI-specific
2. How to propagate rule updates across CLIs
3. Folder structure standardization
4. Memory bank access patterns for each CLI

---

## MC Overseer Integration

### New Agent: MC Overseer

A new **MC Overseer** agent has been created at `.opencode/agents/mc-overseer.md`. This agent acts as:
- Master Coordinator across all projects
- Strategic Advisor for technical decisions
- Cross-CLI orchestration authority

**Task for Gemini**: Create equivalent MC Overseer configurations for Cline CLI and Gemini CLI if they don't exist.

---

## Foundation Stack Endpoints

Use these for agent coordination:

| Service | Endpoint | Purpose |
|---------|----------|---------|
| Agent Bus | `localhost:6379` | Redis Streams coordination |
| Consul | `localhost:8500` | Service discovery |
| Vikunja | `localhost:3456` | Task management |

**Note**: Redis currently requires authentication. The MCP server may need configuration updates.

---

## Task Output Requirements

### Required Deliverables

1. **AWQ Removal Guide Enhancement**
   - Updated `plans/AWQ-REMOVAL-REFACTORING-GUIDE.md`
   - GPU research archive structure

2. **CLI Audit Report**
   - Create `plans/CLI-ECOSYSTEM-AUDIT-REPORT.md`
   - Document all findings
   - List discrepancies and recommendations

3. **Cross-CLI Configuration Proposal**
   - Create `plans/CROSS-CLI-CONFIG-SYNC-PROPOSAL.md`
   - Define synchronization strategy
   - Identify automation opportunities

4. **Updated Task for Cline CLI**
   - Create task in `expert-knowledge/cline/` inbox
   - Specific implementation tasks based on findings

---

## Success Criteria

- [ ] All CLI configurations reviewed
- [ ] Discrepancies documented
- [ ] Skills/agents availability matrix complete
- [ ] CLI-specific strengths documented
- [ ] Cross-CLI sync proposal created
- [ ] MC Overseer agent available across CLIs
- [ ] Memory bank updated with findings

---

## Communication Protocol

Report progress via Agent Bus:

```json
{
  "agent_id": "gemini-cli",
  "role": "cli-auditor",
  "action": "audit_progress",
  "payload": {
    "task": "CLI-AUDIT-001",
    "status": "in_progress",
    "findings": ["..."]
  },
  "timestamp": "ISO-8601",
  "correlation_id": "cli-audit-001"
}
```

---

## Files to Reference

| File | Purpose |
|------|---------|
| `plans/AWQ-REMOVAL-REFACTORING-GUIDE.md` | Main refactoring guide |
| `memory_bank/strategies/PROJECT-QUEUE.yaml` | Project task queue |
| `.clinerules/` | Cline CLI rules |
| `.opencode/RULES.md` | OpenCode CLI rules |
| `.opencode/agents/` | OpenCode agents |
| `.opencode/skills/` | OpenCode skills |
| `AGENTS.md` | Shared agent instructions |
| `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v3.0.0.md` | Model routing |

---

*This task leverages Gemini CLI's 1M token context window for comprehensive ecosystem analysis.*