# Wave 5 Preparation Resources — Haiku Fleet Execution

**Date**: 2026-02-26  
**Purpose**: Comprehensive resource compilation for Haiku fleet execution to continue Wave 5  
**Status**: Ready for Haiku Fleet  
**Coordination Key**: `WAVE-5-PREP-RESOURCES-2026-02-26`

---

## 1. Wave 5 Phase Status Quick Reference

### Phase Completion Matrix

| Phase | Name | Completion | Key Deliverable | Blocker |
|-------|------|------------|------------------|---------|
| 5A | Session Management & Memory | 60% | zRAM config, SQLite sessions | Host-level persistence |
| 5B | Agent Bus & Multi-Agent | 90% | Core implementation | Ops documentation |
| 5C | IAM v2.0 & Ed25519 | 85% | Schema, Sovereign Handshake | API integration |
| 5D | Task Scheduler & Vikunja | 85% | Deployment config | Integration audit |
| 5E | E5 Onboarding Protocol | 80% | Protocol draft | Validation testing |

### Acceptance Criteria Summary

**Phase 5A** (zRAM):
- [ ] Integration tests show no OOMs under 5x load
- [ ] Compression ratio ≥ 1.5 (target ≥ 2.0)
- [ ] Node_exporter confirms metrics for 72h
- [ ] Host-level persistence applied and validated

**Phase 5B** (Agent Bus):
- [ ] Operations guide complete (RQ-151)
- [ ] Load testing passed
- [ ] Production validation complete

**Phase 5C** (IAM):
- [ ] API integration complete
- [ ] Production deployment ready
- [ ] Integration tests passing

**Phase 5D** (Vikunja):
- [ ] Full integration testing
- [ ] Production validation
- [ ] RQ-158 audit complete

**Phase 5E** (E5 Onboarding):
- [ ] Protocol validation
- [ ] User testing complete
- [ ] Documentation finalized

---

## 2. File Path Index by Phase

### Phase 5A Resources

```
memory_bank/PHASES/phase-5a-status.md                    # Status & acceptance criteria
internal_docs/01-strategic-planning/PHASE-5A-ZRAM-BEST-PRACTICES.md
internal_docs/01-strategic-planning/PHASE-5A-EXECUTION-CHECKLIST.md
scripts/zram-health-check.sh                            # Prometheus metrics
scripts/xnai-zram-init.sh                               # Auto-sizing wrapper
TEMPLATE-xnai-zram.service                              # Systemd unit
TEMPLATE-sysctl-zram-tuning.conf                        # Kernel tuning
scripts/runtime_probe.py                                # JSON + Prometheus output
tests/test_runtime_probe.py                             # Unit tests
monitoring/grafana/dashboards/xnai_zram_dashboard.json # Grafana dashboard
monitoring/prometheus/phase-5a-scrape.yml               # Prometheus scrape config
```

### Phase 5B Resources

```
memory_bank/strategies/WAVE-4-AGENT-BUS-HARDENING-BLUEPRINT.md
expert-knowledge/agent-tooling/redis-stream-bus-patterns.md
app/XNAi_rag_app/core/agent_bus.py                      # Core implementation
tests/unit/core/test_agent_bus.py                       # Unit tests
```

### Phase 5C Resources

```
expert-knowledge/security/iam-v2-schema-design.md
expert-knowledge/security/sovereign-trinity-expert-v1.0.0.md
app/XNAi_rag_app/core/iam_db.py                        # IAM implementation
tests/test_iam_persistence.py                           # Persistence tests
```

### Phase 5D Resources

```
docs/06-development-log/vikunja-integration/
memory_bank/infrastructure/QDRANT-STATE-AUDIT.md
expert-knowledge/sync/vikunja-deployment-review-v1.0.0.md
```

### Phase 5E Resources

```
memory_bank/strategies/                                 # E5 protocol docs
expert-knowledge/                                        # Onboarding materials
```

---

## 3. Multi-Account CLI Dispatch Reference

### Account Pool Configuration

```yaml
# Copilot Accounts (Primary)
copilot_accounts:
  - email: "primary@..."
    quota: 50 messages/month
    model: "Raptor Mini"
  # ... 8 total accounts

# Antigravity Accounts (Fallback)
antigravity_accounts:
  - email: "alt@..."
    quota: unlimited (weekly reset)
  # ... 8 total accounts
```

### Fleet Execution Strategy

| Tier | Model | Context | Use Case |
|------|-------|---------|----------|
| 1 | Raptor Mini | 264K | Multi-file analysis, large context |
| 2 | Haiku 4.5 | 200K | Fast tactical tasks |
| 3 | Gemini 1M | 1M | Full-repo research |
| 4 | kat-coder-pro | 262K | Cline CLI unlimited |

### Token Budget Allocation

**Haiku 4.5 Fleet (200K context)**:
- Per-agent budget: ~150K tokens (75% of context)
- Fleet size: 8 agents parallel
- Total capacity: ~1.2M tokens per session

---

## 4. Quick Command Reference

### Session Management

```bash
# Check zRAM status
sudo zramctl

# View zRAM metrics
cat /var/lib/node_exporter/textfile_collector/xnai_zram.prom

# Restart session service
sudo systemctl restart xnai-session.service
```

### Agent Bus

```bash
# Check Redis streams
redis-cli XINFO STREAM xnai:agent_bus

# Monitor consumer groups
redis-cli XINFO GROUPS xnai:agent_bus
```

### Vikunja

```bash
# Check Vikunja status
podman ps | grep vikunja

# View logs
podman logs vikunja
```

---

## 5. Testing & Validation Checklist

### Pre-Execution Validation

- [ ] All credentials configured in `~/.config/xnai/`
- [ ] Redis connection verified
- [ ] Account quotas checked
- [ ] Session storage initialized

### Phase 5A Validation

```bash
# Run zRAM health check
bash scripts/zram-health-check.sh

# Verify Prometheus metrics
curl http://localhost:9100/metrics | grep xnai_zram

# Check compression ratio
cat /sys/block/zram0/compr_data_size
cat /sys/block/zram0/orig_data_size
```

### Phase 5B Validation

```bash
# Test Agent Bus message flow
python -m pytest tests/unit/core/test_agent_bus.py -v

# Verify consumer group
redis-cli XREADGROUP GROUP xnai consumers 1
```

---

## 6. Troubleshooting Guide

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| zRAM not mounting | `zramctl` shows no devices | Check kernel module, run `modprobe zram` |
| Agent Bus blocked | Messages queueing | Check Redis connection, consumer health |
| Quota exhausted | "Rate limit" errors | Rotate to next account tier |
| Session lost | Context reset | Check SQLite persistence |

### Debug Commands

```bash
# Check system memory
free -h

# View zRAM debug
dmesg | grep zram

# Redis diagnostics
redis-cli INFO | grep -E "used_memory_human|connected_clients"

# Agent Bus health
redis-cli XLEN xnai:agent_bus
```

---

## 7. Research Queue (RQ) Items for Wave 5

### Critical Path (Must Complete)

| RQ | Description | Effort | Priority |
|----|-------------|--------|----------|
| RQ-151 | Agent Bus ops documentation | 4h | CRITICAL |
| RQ-152 | Voice cascade degradation spec | 3h | CRITICAL |
| RQ-153 | IAM integration guide | 4h | HIGH |
| RQ-158 | Vikunja integration audit | 3h | HIGH |

### High Priority

| RQ | Description | Effort | Priority |
|----|-------------|--------|----------|
| RQ-141 | LLM-as-Judge quality scoring | 3h | HIGH |
| RQ-142 | Redis consumer group tuning | 2h | HIGH |
| RQ-144 | Connection pooling | 4h | HIGH |
| RQ-146 | Performance optimization loop | 2.5h | HIGH |

### Reference: Full RQ List

See: `memory_bank/strategies/RESEARCH-JOBS-QUEUE.md`

---

## 8. Handoff Protocol

### Starting Haiku Fleet Session

1. **Load Context** (in order):
   - Read `RAPTOR-ONBOARDING-CONTEXT-DOCUMENT.md`
   - Read `WAVE-5-IMPLEMENTATION-MANUAL.md`
   - Review phase-specific files from Section 2

2. **Validate Environment**:
   - Check credentials configured
   - Verify Redis accessible
   - Confirm account quotas available

3. **Execute Phase Tasks**:
   - Start with highest completion phase (5B: 90%)
   - Progress to lowest (5A: 60%)
   - Document all changes

4. **Report Progress**:
   - Update `activeContext.md`
   - Log to `memory_bank/agent_actions.log`
   - Notify via Agent Bus if blocking

### Coordination Keys

- **This Session**: `WAVE-5-PREP-RESOURCES-2026-02-26`
- **Raptor Context**: `RAPTOR-ONBOARDING-CONTEXT-2026-02-26`
- **Wave 5**: `WAVE-4-MULTI-ACCOUNT-INTEGRATION-2026-02-23`

---

## 9. File Manifest

### Documents Created This Session

| File | Purpose |
|------|---------|
| `RAPTOR-ONBOARDING-CONTEXT-DOCUMENT.md` | Context for Raptor to create Haiku onboarding |
| `WAVE-5-PREP-RESOURCES.md` | This file - resources for Haiku fleet execution |

### Existing Key Documents

| File | Purpose |
|------|---------|
| `WAVE-5-IMPLEMENTATION-MANUAL.md` | Complete Wave 5 guide (2907 lines) |
| `COMPLETE-SYNTHESIS-FOR-OPUS_46.md` | Strategic synthesis |
| `STRATEGIC-BLUEPRINT-CLI-HARDENING.md` | CLI dispatch strategy |

---

## 10. Success Metrics

### Wave 5 Completion Targets

| Metric | Target | Current |
|--------|--------|---------|
| Phase Completion | 100% | 70% |
| Acceptance Criteria Met | 100% | 0% |
| RQ Items Resolved | 20+ | 0 |
| Test Coverage | 95% | 80-95% |

### Fleet Execution Targets

| Metric | Target |
|--------|--------|
| Parallel Agents | 8 |
| Tokens/Agent | 150K |
| Total Capacity | 1.2M/session |
| Session Duration | 2-4 hours |

---

**Last Updated**: 2026-02-26  
**Status**: Ready for Haiku Fleet Execution  
**Next Step**: Load context → Validate environment → Execute Wave 5 tasks
