# AWQ Removal & CPU+Vulkan Optimization Refactoring Guide
## For Multi-Agent Parallel Execution

**Version**: 1.0.0
**Created**: 2026-02-21
**Author**: Cline (Task Assignment for Gemini CLI)
**Purpose**: Comprehensive refactoring guide for AWQ removal without code changes

---

## Executive Summary

This guide provides a systematic approach to remove AWQ (Activation-aware Weight Quantization) components from the XNAi Foundation stack while preserving all valuable GPU research knowledge and optimizing for the CPU+Vulkan architecture. The work is broken into parallelizable task groups optimized for AI code assistants.

**Critical Constraint**: This project follows a **torch-free mandate**. AWQ requires PyTorch, which conflicts with the Foundation's CPU+Vulkan-only architecture using ONNX Runtime and GGUF models.

---

## Current State Analysis

### AWQ Components Identified

| Component | Location | Status | Action |
|-----------|----------|--------|--------|
| Dockerfile.awq | `/Dockerfile.awq` | Active | Remove |
| PyTorch Dependencies | Dockerfile.awq | Active | Document for archive |
| autoawq Library | Dockerfile.awq | Active | Document for archive |
| optimum Library | Dockerfile.awq | Active | Evaluate (may be used elsewhere) |

### Foundation Stack Context

**Current Architecture**:
- **Base Image**: `xnai-base:latest` (Python 3.12-slim)
- **Inference**: llama-cpp-python with Vulkan + OpenBLAS
- **Voice**: Piper TTS (ONNX) + Faster-Whisper (CTranslate2)
- **Vector DB**: FAISS CPU + Qdrant ready
- **Orchestration**: LangChain (torch-free)

**Performance Targets**:
- Text latency: <500ms
- Voice latency: <300ms
- RAM usage: <6GB
- Hardware: Ryzen 7 5700U, Vega iGPU (Vulkan)

---

## Task Group Breakdown

### GROUP A: File System Cleanup

**Assigned Agent**: TBD
**Priority**: P1
**Dependencies**: None (can start immediately)
**Estimated Effort**: 30 minutes

#### Tasks

- [ ] **A.1**: Audit all files for AWQ references
  ```bash
  # Search command
  grep -r "awq\|AWQ\|autoawq" --include="*.py" --include="*.yaml" --include="*.yml" --include="*.md" --include="Dockerfile*"
  ```

- [ ] **A.2**: Create deletion checklist
  - Files to remove: `Dockerfile.awq`
  - Files to preserve: All GPU research in `expert-knowledge/`
  - Files to update: Any build scripts referencing AWQ

- [ ] **A.3**: Verify no runtime dependencies
  - Check `requirements*.txt` files for AWQ dependencies
  - Verify `docker-compose.yml` doesn't reference AWQ services
  - Check Makefile for AWQ-related targets

- [ ] **A.4**: Document shared dependencies
  - Identify any dependencies used by both AWQ and core stack
  - Create preservation list to prevent breaking changes

**Deliverable**: `plans/awq-removal-file-audit.md`

---

### GROUP B: Memory Bank & Documentation

**Assigned Agent**: TBD
**Priority**: P1
**Dependencies**: None (can start immediately)
**Estimated Effort**: 1 hour

#### Tasks

- [ ] **B.1**: Create GPU Research Archive
  - Location: `expert-knowledge/_archive/gpu-research/`
  - Content: All AWQ and GPU optimization research
  - Format: Preserve original structure with archive metadata

- [ ] **B.2**: Document AWQ Architecture
  - Create `expert-knowledge/_archive/gpu-research/AWQ-ARCHITECTURE.md`
  - Include: How AWQ works, why it was considered, why it's being removed
  - Preserve: All technical details for future reference

- [ ] **B.3**: Update Memory Bank Files
  - `memory_bank/techContext.md`: Remove AWQ references, update stack description
  - `memory_bank/progress.md`: Add AWQ removal milestone
  - `memory_bank/activeContext.md`: Update current priorities

- [ ] **B.4**: Create Migration Documentation
  - Document the removal process
  - Create rollback procedure (if needed)
  - Update any tutorials or guides mentioning AWQ

**Deliverable**: Updated memory bank files + GPU research archive

---

### GROUP C: Build System Updates

**Assigned Agent**: TBD
**Priority**: P1
**Dependencies**: Group A completion (file audit)
**Estimated Effort**: 30 minutes

#### Tasks

- [ ] **C.1**: Analyze Dockerfile.awq Integration
  - Identify all references in main Dockerfile
  - Check for build script dependencies
  - Verify base image compatibility

- [ ] **C.2**: Update Build Configuration
  - Remove AWQ from build targets (if present)
  - Update Makefile (if AWQ targets exist)
  - Verify CI/CD pipeline doesn't reference AWQ

- [ ] **C.3**: Validate Remaining Stack
  - Ensure Vulkan configuration remains intact
  - Verify OpenBLAS optimization preserved
  - Check Ryzen-specific tuning is maintained

- [ ] **C.4**: Create Verification Script
  - Script to verify AWQ is fully removed
  - Check for orphaned dependencies
  - Validate stack functionality

**Deliverable**: Updated build files + verification script

---

### GROUP D: Foundation Stack Integration

**Assigned Agent**: TBD
**Priority**: P2
**Dependencies**: Groups A, B, C completion
**Estimated Effort**: 1 hour

#### Tasks

- [ ] **D.1**: Agent Bus Task Registration
  - Publish AWQ removal task to `xnai:agent_bus`
  - Subscribe agents to coordination stream
  - Set up progress tracking

- [ ] **D.2**: Consul Service Registration
  - Register AWQ removal as service in Consul
  - Configure health checks for task completion
  - Set up service discovery for coordination

- [ ] **D.3**: Vikunja Task Creation
  - Create parent task: "AWQ Removal & CPU+Vulkan Optimization"
  - Create subtasks for each group
  - Set up label schema: `tier:P1`, `project:P-025`, `awq-removal`

- [ ] **D.4**: Circuit Breaker Configuration
  - Set up Redis-backed circuit breakers for agent coordination
  - Configure failure thresholds (3 consecutive failures)
  - Set recovery timeout (30 seconds)

**Deliverable**: Integrated task tracking in Foundation stack

---

## Agent Bus Coordination Protocol

### Message Format

All agents must use this message format when publishing to the Agent Bus:

```json
{
  "agent_id": "agent-group-X",
  "role": "awq_removal",
  "action": "task_progress",
  "payload": {
    "task": "A.1",
    "status": "completed",
    "details": "Found 3 AWQ references"
  },
  "timestamp": "2026-02-21T12:00:00Z",
  "correlation_id": "awq-removal-001"
}
```

### Stream Channels

| Stream | Purpose |
|--------|---------|
| `xnai:agent_bus` | Task progress and coordination |
| `xnai:alerts` | Error broadcasting and conflict resolution |
| `xnai:heartbeat` | Agent health monitoring |

### Coordination Workflow

1. **Task Start**: Agent publishes `task_started` to `xnai:agent_bus`
2. **Progress Updates**: Agent publishes `task_progress` every 5 minutes
3. **Task Complete**: Agent publishes `task_completed` with deliverables
4. **Conflict Detection**: Agents monitor `xnai:alerts` for conflicts
5. **Handoff**: Next agent acknowledges via `xnai:agent_bus`

---

## GPU Research Preservation

### What to Preserve

| Category | Location | Preservation Action |
|----------|----------|---------------------|
| AWQ Architecture | `expert-knowledge/_archive/gpu-research/` | Full documentation |
| Quantization Research | `expert-knowledge/_archive/gpu-research/` | Research notes |
| GPU Optimization | `expert-knowledge/_archive/gpu-research/` | Techniques for future use |
| PyTorch Alternatives | `expert-knowledge/` | Keep active (GGUF, ONNX) |

### What to Remove

| Category | Location | Removal Action |
|----------|----------|----------------|
| Dockerfile.awq | Root directory | Delete file |
| AWQ Build Targets | Makefile | Remove targets |
| AWQ Documentation | docs/ | Update or remove references |

---

## Validation Checklist

### Pre-Removal Verification

- [ ] All agents have read memory bank context
- [ ] Agent Bus is operational (`localhost:6379`)
- [ ] Consul is accessible (`localhost:8500`)
- [ ] Vikunja is ready for task creation (`localhost:3456`)

### Post-Removal Verification

- [ ] No AWQ references in codebase (`grep -r "awq\|AWQ"`)
- [ ] Build succeeds without AWQ (`make build`)
- [ ] Stack starts correctly (`podman-compose up`)
- [ ] Memory bank updated with changes
- [ ] GPU research archived properly
- [ ] All tests pass (`pytest tests/`)

---

## Rollback Procedure

If removal causes issues:

1. **Restore Dockerfile.awq** from git history
2. **Rebuild base image** with AWQ support
3. **Revert memory bank** changes from backup
4. **Document failure** in `memory_bank/activeContext.md`

```bash
# Rollback commands
git checkout HEAD~1 -- Dockerfile.awq
podman-compose build --no-cache
```

---

## Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| AWQ References | 0 | `grep -r "awq"` returns empty |
| Build Success | 100% | `make build` completes |
| Stack Functionality | 100% | All services healthy |
| Memory Bank Accuracy | 100% | All files updated |
| Documentation Quality | 95%+ | No orphaned references |

---

## Appendix: Foundation Stack Endpoints

| Service | Endpoint | Purpose |
|---------|----------|---------|
| Agent Bus | `localhost:6379` | Redis Streams coordination |
| Consul | `localhost:8500` | Service discovery |
| Vikunja | `localhost:3456` | Task management |
| Prometheus | `localhost:9090` | Metrics collection |
| Grafana | `localhost:3000` | Monitoring dashboards |

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-02-21 | Cline | Initial guide creation |

---

*This guide is designed for multi-agent parallel execution. Each group can work independently with coordination through the Foundation Agent Bus.*