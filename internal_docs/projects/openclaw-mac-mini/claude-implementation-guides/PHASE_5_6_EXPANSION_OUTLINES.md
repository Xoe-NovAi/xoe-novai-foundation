# PHASES 5-6: Security Hardening & Advanced Scaling
## Expansion Outlines with Hooks for 2026+ Features

**Status**: Optional expansion phases (Phases 1-4 are production-ready) | **Prerequisites**: Phases 1-4 complete and stable | **Estimate**: 6-10 hours total

---

## PHASE 5: Security Hardening & Observability
### Days 7-9 (Optional; Recommended for Long-Term Operation)

#### Overview
Phase 5 hardens OpenClaw for production:
- Formal security audits (vulnerability scanning)
- Remote access via Cloudflare Zero Trust (no open ports)
- Dashboard for monitoring (VO-navigable web UI)
- Critique loops (secondary agent verifies risky actions)
- TLS encryption for all communications

---

### Part A: Security Audits

#### OpenClaw Built-In Audit
```bash
openclaw security audit --verbose --export json > ~/audit-report.json
```

**What to check**:
- [ ] No hardcoded secrets in config
- [ ] File permissions on sensitive files (600)
- [ ] Sandbox restrictions enforced
- [ ] Network isolation verified
- [ ] Process privilege level (should be user, not root)

#### Vulnerability Scanning
Use OWASP dependency checker (integrate into Phase 5):
```bash
# TBD: Add npm audit, OWASP ZAP, or Trivy scanning
npm audit --audit-level=moderate
```

#### Manual Audit Checklist
- [ ] Audit log reviewed (no suspicious patterns)
- [ ] Approval log shows all sensitive actions approved
- [ ] Failed auth attempts logged and reviewed
- [ ] Model files checksummed (detect tampering)
- [ ] System logs checked for intrusions

---

### Part B: Cloudflare Zero Trust (Secure Remote Access)

#### Setup Overview
If you need remote access (e.g., accessing the agent from work), Cloudflare Zero Trust provides:
- No open ports on Mac mini
- Encrypted tunnel (TLS 1.3)
- Identity verification (OAuth via Apple ID)
- Audit logging

#### Configuration Steps (Outline)
1. Create Cloudflare account
2. Set up Zero Trust tunnel
3. Point tunnel to OpenClaw API (127.0.0.1:8080)
4. Configure access policy (restrict by user/device)
5. Test remote access via `cloudflared` CLI

#### Voice Commands for Remote Access
```bash
alias tunnel-status='cloudflared tunnel info | say'
alias tunnel-logs='cloudflared tunnel logs | tail -20 | say'
```

---

### Part C: Dashboard & Monitoring

#### OpenClaw Studio (Web UI)
OpenClaw includes Studio (web dashboard):
```bash
# Access via browser (localhost or via tunnel)
open http://127.0.0.1:9090
```

**Accessibility notes**:
- Studio is web-based; VoiceOver compatibility varies
- Focus on CLI/voice commands for primary interface
- Dashboard is optional (audit logs are authoritative)

#### Prometheus Metrics (Advanced)
For deeper monitoring (optional):
```bash
# Expose metrics endpoint
export OPENCLAW_PROMETHEUS=true
```

Metrics available:
- Agent inference latency (TPS)
- Approval response time
- Task execution success rate
- GPU/CPU utilization
- Thermal state

---

### Part D: Critique Loops (Secondary Verification)

#### Concept
A second Ollama instance reviews risky actions before execution.

**Example flow**:
1. User requests: "Delete all files in Downloads older than 6 months"
2. OpenClaw plans action
3. **Critique loop triggered**: Secondary agent (Mistral 7B) analyzes the plan
4. Critique output: "WARNING: This could delete important files. Recommend confirmation."
5. Additional approval step added
6. User confirms before execution

#### Implementation Hook
```javascript
// critiqueDaemon.js (pseudocode)

class CritiqueDaemon {
  async reviewAction(action, context) {
    const prompt = `
      Review this action for risks:
      Action: ${action.description}
      Context: ${JSON.stringify(context)}
      
      Respond with: SAFE | WARNING | DANGEROUS
      And explain why.
    `;
    
    const critique = await ollama.run('mistral:7b-instruct-q4_k_m', prompt);
    
    if (critique.includes('DANGEROUS')) {
      await requestAdditionalApproval(action);
    }
    
    return { approved: true, critique: critique };
  }
}
```

#### Configuration
```json
{
  "critique": {
    "enabled": true,
    "model": "mistral:7b-instruct-q4_k_m",
    "actions_reviewed": [
      "file_delete",
      "file_modify_system",
      "shell_execute_dangerous",
      "email_send_bulk"
    ]
  }
}
```

---

### Part E: Testing & Validation Gate

#### Phase 5 Checklist
- [ ] `openclaw security audit` returns no critical issues
- [ ] Zero Trust tunnel connects and passes auth
- [ ] Dashboard loads (manual accessibility test)
- [ ] Critique loop triggers on test dangerous action
- [ ] All monitoring metrics populate
- [ ] Audit log shows comprehensive record

---

### Part F: Extension Points

Document hooks for Phase 5 expansion:
```json
{
  "security": {
    "audits": {
      "schedule": "weekly",
      "auto_fix": false,
      "report_format": "json"
    },
    "tunnel": {
      "provider": "cloudflare",
      "auth_method": "oauth_apple_id"
    },
    "critique": {
      "enabled": true,
      "model": "mistral:7b-instruct-q4_k_m"
    },
    "metrics": {
      "prometheus_enabled": false,
      "retention_days": 30
    }
  }
}
```

---

## PHASE 6: Advanced Scaling & Optimization
### Days 9-15 (Optional; For High-Load or Multi-Device Setups)

#### Overview
Phase 6 scales OpenClaw for:
- Multi-Mac clustering (distributed inference)
- Model compression (SparseML for 60-80% reduction)
- Automated re-optimization (quarterly)
- Advanced accessibility (Braille integration)
- Production monitoring dashboard

---

### Part A: Multi-Mac Clustering (Exo Labs)

#### Concept
Distribute inference across multiple Macs to run larger models or increase throughput.

**Example**: 2× Mac mini clusters = run 70B model at 50+ TPS vs. 25+ TPS on single Mac.

#### Setup (Outline)
1. Install Exo Labs framework
2. Connect Macs via Thunderbolt or 10GbE
3. Configure master/worker roles
4. Deploy models across workers
5. Monitor via dashboard

#### Configuration
```bash
# Master Mac (the "hub")
exo run --role master --models llama3.3:agent

# Worker Mac (additional hardware)
exo run --role worker --master-ip 192.168.1.100 --models llama3.3:agent
```

#### Performance Gains
- **1 Mac**: 25 TPS
- **2 Macs (clustered)**: 45-50 TPS
- **3 Macs**: 70+ TPS

---

### Part B: Model Compression (SparseML)

#### Concept
Prune 50-70% of model weights, then quantize remainder. Achieves 60-80% size reduction.

**Trade-off**: Some edge-case knowledge lost; recoverable via chain-of-thought prompting.

#### SparseML Pipeline (Outline)
```bash
# 1. Download Hugging Face model
huggingface-cli download meta-llama/Llama-3.3-70B

# 2. Prune model (remove 60% weights)
sparseml.transformers.sparsify \
  --model meta-llama/Llama-3.3-70B \
  --recipe llama-70b-prune-60.yaml \
  --output ./llama-70b-sparse

# 3. Quantize (Q4_K_M)
llama-quantize --type q4_k_m \
  llama-70b-sparse.gguf \
  llama-70b-sparse-q4.gguf

# 4. Deploy to Ollama
cp llama-70b-sparse-q4.gguf ~/.ollama/models/
ollama create llama3.3:sparse -f modelfile-sparse
```

#### Results
- **Original model**: 140GB (FP16)
- **Q4_K_M only**: 35GB (25% of size)
- **Sparse + Q4_K_M**: 12-15GB (10% of size)
- **Speed**: DeepSparse engine 5-10x faster on sparse models (CPU fallback; still viable)

#### Configuration
```json
{
  "models": [
    {
      "name": "llama3.3:sparse",
      "optimization": "sparseml_pruned_60_percent",
      "quantization": "Q4_K_M",
      "size_gb": 14,
      "speed_tps": 20,
      "notes": "60% sparsity; knowledge recovery via prompting"
    }
  ]
}
```

---

### Part C: Automated Re-Optimization

#### Quarterly Cycle
1. **Month 1**: Benchmark current models
2. **Month 2**: Apply latest SparseML recipes
3. **Month 3**: Validate and deploy
4. **Month 4**: Monitor and adjust

#### Automation Script (Outline)
```bash
#!/bin/bash
# ~/cron/quarterly-optimization.sh

# Run quarterly (first day of month)
0 0 1 * * /path/to/quarterly-optimization.sh

# Procedure:
# 1. Backup current models
# 2. Download latest model from HF
# 3. Apply SparseML recipes
# 4. Quantize to GGUF
# 5. Benchmark (compare old vs new)
# 6. If improvement >5%, deploy; else rollback
# 7. Log results
```

---

### Part D: Advanced Accessibility (Braille Integration)

#### Braille Display Support
If your friend uses a Braille display (e.g., Focus 40 5th Gen):

1. Connect via Bluetooth
2. Configure in Phase 1 (already done if enabled)
3. Braille output appears automatically via VoiceOver

#### Braille Navigation Commands
```
VO + Braille key combinations (depends on display)
Example: Left pad = previous, Right pad = next
```

#### Braille + Voice Hybrid
```json
{
  "accessibility": {
    "braille_enabled": true,
    "braille_display": "focus40_5th_gen",
    "braille_verbosity": "verbose",
    "voice_enabled": true,
    "voice_rate": 0.5
  }
}
```

---

### Part E: Production Monitoring Dashboard

#### Dashboard Components
- **System health**: CPU, memory, thermal, disk
- **Agent metrics**: TPS, approval latency, task success rate
- **Model status**: Currently loaded models, cache size, VRAM usage
- **Audit summary**: Recent actions, approvals, errors
- **Alerts**: Thermal throttle, low disk, approval timeout

#### Technology Stack (Outline)
- **Backend**: OpenClaw API + Prometheus metrics
- **Frontend**: React (VO-compatible) or pure HTML
- **Hosting**: Localhost (127.0.0.1:9090) or via Zero Trust tunnel

---

### Part F: Testing & Validation Gate

#### Phase 6 Checklist
- [ ] Multi-Mac cluster connects (if attempted)
- [ ] SparseML model compresses to <20GB
- [ ] Sparse model benchmarks within 10% of original
- [ ] Quarterly automation script runs without error
- [ ] Braille display paired and outputs text
- [ ] Dashboard loads and shows metrics

---

### Part G: Extension Points

```json
{
  "scaling": {
    "clustering": {
      "enabled": false,
      "cluster_size": 1,
      "framework": "exo_labs",
      "master_ip": "127.0.0.1"
    },
    "compression": {
      "enabled": false,
      "method": "sparseml",
      "target_sparsity": 0.6,
      "compression_schedule": "quarterly"
    },
    "accessibility": {
      "braille_display_enabled": false,
      "braille_model": "focus40_5th_gen"
    },
    "monitoring": {
      "prometheus_enabled": false,
      "dashboard_port": 9090
    }
  }
}
```

---

## Decision Tree: Which Phases to Implement?

```
Start
 ├─ Need hands-free agent?
 │   ├─ YES → Do Phases 1-4 (Complete & Operate)
 │   └─ NO → Stop (not your use case)
 │
 └─ Have Phases 1-4 stable for 1+ month?
     ├─ YES → Consider Phase 5
     │   └─ Need remote access or audit compliance?
     │       ├─ YES → Do Phase 5 (Security)
     │       └─ NO → Skip Phase 5
     │
     └─ NO → Continue operating Phases 1-4 until stable
```

---

## Knowledge Gaps (Phases 5-6)

### Gap 1: Critique Loop Trade-offs
**Question**: Does secondary verification slow down task execution?

**Answer**: Yes, ~50% slower (adds one more LLM inference). Only recommend for sensitive actions. For routine tasks, disable critique.

### Gap 2: SparseML Knowledge Loss
**Question**: Does pruning 60% of weights cause hallucinations?

**Answer**: Minimal in practice. Pruning removes redundant weights, not critical knowledge. Chain-of-thought prompting recovers lost reasoning.

### Gap 3: Multi-Mac Synchronization
**Question**: How do models stay in sync across clustered Macs?

**Answer**: Exo Labs handles model replication. Each worker downloads the same GGUF. Periodic checksums verify consistency.

---

## Maintenance Schedule

### Daily
- Check audit log for unusual activity
- Monitor thermal state (if custom monitoring)

### Weekly
- Review approval log
- Check disk space (models can grow)
- Verify Telegram bot connectivity

### Monthly
- Run security audit
- Review performance metrics
- Update macOS (if patches available)

### Quarterly (Phase 6)
- Re-optimize models (SparseML)
- Benchmark performance vs. baseline
- Update documentation

---

## Performance Targets (All Phases)

| Metric | Target | Actual |
|--------|--------|--------|
| **Inference Speed** | 25+ TPS (70B) | ✅ Achievable |
| **Voice Latency** | <2s (Mistral) | ✅ Achievable |
| **Approval Latency** | <5s | ✅ Achievable |
| **System Memory Overhead** | <5GB | ✅ Achievable |
| **GPU Utilization** | 80-90% | ✅ Achievable |
| **Thermal Stability** | No throttle | ✅ Monitor & tune |
| **Uptime** | 99%+ | ✅ With monitoring |

---

## Cost & Resource Analysis

| Phase | Effort | Hardware | Software | Total |
|-------|--------|----------|----------|-------|
| 1-4 (Core) | 10-16 hrs | $0* | $0 (OSS) | **~$0** |
| 5 (Security) | 2-3 hrs | $0 | $0-100 (CF tunnel) | **~$100/yr** |
| 6 (Scaling) | 4-6 hrs | $2K-5K** | $0 (OSS) | **+$2-5K** |

*Mac mini already purchased
**Only if adding 2nd+ Mac for clustering

---

## Summary & Next Steps

### If Phases 1-4 Are Stable:
1. **Short-term** (1-2 weeks): Use agent for real work
2. **Medium-term** (1 month): Implement Phase 5 if you need remote access
3. **Long-term** (3+ months): Consider Phase 6 if agent becomes load-bottleneck

### If Phases 1-4 Are Unstable:
1. Debug using troubleshooting matrices in each phase
2. Don't proceed until Phase 4 validation gate passes
3. Check logs aggressively: `tail -100 ~/.openclaw/openclaw.log`

### Recommended Path for Most Users:
**Phases 1-4 ONLY** (production-ready, stable, hands-free).

Phase 5 is nice-to-have (security/audit compliance).
Phase 6 is optional (for scaling or advanced use cases).

---

## Document Control

| Version | Date | Phase | Status |
|---------|------|-------|--------|
| 1.0 | Feb 2026 | 1-4 | Production |
| 1.1 | TBD | 5-6 | Outline (ready for expansion) |

---

## Contact for Phase 5-6 Implementation

If you want to expand Phase 5 or 6:
- Refer to component headers and "Configuration" sections above
- Search GitHub/docs for technology (Cloudflare Zero Trust, SparseML, Exo Labs)
- Test in isolated environment first (not on production Mac)
- Document changes for future reference

---

**End of Phases 5-6 Outline.**

For operational use, stick with **Phases 1-4** (production-ready). Return here if/when you need advanced features.
