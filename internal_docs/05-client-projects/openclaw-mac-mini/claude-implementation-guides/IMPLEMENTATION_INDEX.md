# OpenClaw Hands-Free Implementation Manual
## Complete Guide: Autonomous AI Agent for Blind Users on Mac mini

**Last Updated**: February 2026 | **Status**: Production-Ready (Phases 1-4 Core) | **Platform**: Apple Silicon Mac mini (M1-M4) with 64GB RAM

---

## Quick Navigation

### Core Implementation Phases

| Phase | Duration | Focus | Status | Next |
|-------|----------|-------|--------|------|
| **1. Foundation & Isolation** | 2-4 hrs | VoiceOver setup, burner identity, approval mechanisms | ✅ Core | 2 |
| **2. Container Environment** | 2-3 hrs | Podman installation, GPU passthrough, thermal mgmt | ✅ Core | 3 |
| **3. Intelligence Layer** | 3-5 hrs | Ollama LLM setup, model optimization, benchmarking | ✅ Core | 4 |
| **4. OpenClaw Deployment** | 3-4 hrs | Agent integration, Telegram voice, approval flow | ✅ Core | 5 |
| **5. Security Hardening** | 2-3 hrs | Audits, Zero Trust, dashboard, critique loops | 📋 Outline | 6 |
| **6. Advanced Scaling** | 4-6 hrs | Multi-device clustering, optimization, automation | 📋 Outline | Done |

---

## Reading These Manuals

Each phase is a **standalone document** that:
1. Builds on the previous phase
2. Can be updated independently without rewriting others
3. Includes hands-free validation gates
4. Contains troubleshooting matrices

**Recommended approach**:
1. Read Phase 1-4 completely (they are production-ready)
2. Refer to specific troubleshooting sections as needed
3. Use the validation gates to confirm progress
4. Phase 5-6 are expansion guides; not required for basic operation

---

## Document Map

### 📄 PHASE 1: Foundation & Isolation
**File**: `PHASE_1_FOUNDATION_AND_ISOLATION.md`

**What you'll do**:
- Enable macOS VoiceOver (screen reader)
- Configure Dictation for hands-free typing
- Create burner Apple ID (data isolation)
- Set up approval mechanisms with voice feedback
- Test accessibility end-to-end

**Key skills learned**:
- VoiceOver navigation (VO + Right/Left/Space)
- Dictation with custom shortcuts
- System accessibility configuration
- Voice-based task approval

**Prerequisites**: None (fresh Mac mini)
**Time**: 2-4 hours
**Success criteria**: All VoiceOver tests pass, voice approval simulation works

---

### 📄 PHASE 2: Container Environment (Podman)
**File**: `PHASE_2_CONTAINER_ENVIRONMENT.md`

**What you'll do**:
- Install Podman (daemonless container runtime)
- Enable Vulkan-to-Metal GPU passthrough
- Configure compose for container orchestration
- Set up thermal monitoring
- Create voice-controlled container commands

**Key skills learned**:
- Podman machine initialization
- GPU passthrough fundamentals
- Docker-compose YAML configuration
- Container health monitoring
- Linux thermal management concepts

**Prerequisites**: Phase 1 complete
**Time**: 2-3 hours
**Success criteria**: GPU test passes, thermal monitor active, <5% overhead

---

### 📄 PHASE 3: Intelligence Layer (Ollama)
**File**: `PHASE_3_INTELLIGENCE_LAYER.md`

**What you'll do**:
- Install Ollama locally with Metal GPU support
- Download 3 optimized models (Llama 3.3, DeepSeek, Mistral)
- Configure model quantization (Q4_K_M, AWQ)
- Benchmark performance (25+ TPS target)
- Test voice latency for real-time interaction

**Key skills learned**:
- LLM quantization concepts (FP16 → Q4)
- Ollama CLI and API
- Model optimization trade-offs
- Performance benchmarking
- Context window tuning for voice

**Prerequisites**: Phases 1-2 complete
**Time**: 3-5 hours (includes model downloads)
**Success criteria**: 25+ TPS on Llama 3.3, <2s voice latency on Mistral

---

### 📄 PHASE 4: OpenClaw Deployment
**File**: `PHASE_4_OPENCLAW_DEPLOYMENT.md`

**What you'll do**:
- Install OpenClaw (Node.js-based agent)
- Configure Ollama as LLM backend
- Set up Telegram bot for voice interface
- Implement approval flow (voice-based task confirmation)
- Test end-to-end voice-in/voice-out workflow

**Key skills learned**:
- OpenClaw configuration and startup
- Telegram bot setup via BotFather
- Agent approval mechanisms
- Audit logging for transparency
- Hands-free task execution

**Prerequisites**: Phases 1-3 complete
**Time**: 3-4 hours
**Success criteria**: Telegram voice test passes, approval flow works, audit logs clean

**⚠️ At this point, you have a fully operational hands-free autonomous AI agent.**

---

### 📋 PHASE 5: Security Hardening (Outline)
**File**: Expand `PHASE_5_SECURITY_HARDENING.md` (template below)

**What you'll do**:
- Run OpenClaw security audit (`openclaw security audit`)
- Configure Cloudflare Zero Trust for secure remote access
- Deploy dashboard for monitoring (VO-navigable)
- Implement critique loops (secondary agent verifies actions)
- Set up TLS/encryption for all communications

**Key components**:
- Security audit checklist
- Cloudflare Zero Trust tunnel setup
- OpenClaw Studio dashboard (web UI)
- Critique agent (separate Ollama instance)
- Regular security reviews

**Time**: 2-3 hours
**Success criteria**: Audit passes, remote access works, critique loop detects 1+ issues

---

### 📋 PHASE 6: Advanced Scaling (Outline)
**File**: Expand `PHASE_6_ADVANCED_SCALING.md` (template below)

**What you'll do**:
- Cluster multiple Macs (Exo Labs for distributed inference)
- Deploy SparseML for 60-80% model compression
- Automate re-optimization (quarterly cycles)
- Integrate Braille displays (advanced accessibility)
- Set up monitoring dashboard

**Key components**:
- Exo Labs multi-device setup
- SparseML pruning pipelines
- Automated model re-quantization
- Braille integration (for Braille display users)
- Advanced monitoring

**Time**: 4-6 hours
**Success criteria**: Multi-device inference works, compression gains verified, dashboard active

---

## Quick-Start Checklist

### Before You Begin
- [ ] Mac mini with 64GB RAM, Apple Silicon (M1-M4)
- [ ] USB microphone (for dictation)
- [ ] Headphones or speakers (for TTS feedback)
- [ ] HDMI dummy plug
- [ ] Optional: Braille display (Focus 40 5th Gen or equivalent)
- [ ] Telegram account (for voice interface)
- [ ] Stable internet (for initial setup; local after that)

### Phase 1 (Foundation)
- [ ] Read PHASE_1 completely
- [ ] Enable VoiceOver (Cmd + F5)
- [ ] Test Dictation (Fn + Fn)
- [ ] Create burner Apple ID
- [ ] Pass accessibility validation gate

### Phase 2 (Podman)
- [ ] Read PHASE_2 completely
- [ ] Install Podman via Homebrew
- [ ] Initialize Podman machine
- [ ] Test GPU passthrough (Vulkan)
- [ ] Start thermal monitor
- [ ] Pass <5% overhead benchmark

### Phase 3 (Ollama)
- [ ] Read PHASE_3 completely
- [ ] Install Ollama natively
- [ ] Download 3 models (20-30 minutes each)
- [ ] Verify Metal GPU activation
- [ ] Benchmark: 25+ TPS on Llama 3.3
- [ ] Test voice latency <2s on Mistral

### Phase 4 (OpenClaw)
- [ ] Read PHASE_4 completely
- [ ] Install OpenClaw via npm
- [ ] Create telegram bot (BotFather)
- [ ] Get Telegram user ID (userinfobot)
- [ ] Configure openclaw.json with credentials
- [ ] Start daemon and test voice approval

---

## Validation Gate Checklist

### Phase 1 Gate: Accessibility Audit
Run before proceeding to Phase 2:
```bash
# Test VoiceOver navigation
# Test Dictation (Fn + Fn)
# Test Voice Control (say "Show grid")
# Test approval simulation (echo "Test approval" | say)
```

**Pass criteria**: All 4 tests successful, no errors in logs

---

### Phase 2 Gate: Container Stability
Run before proceeding to Phase 3:
```bash
# Check Podman machine running
podman machine ls

# Test GPU passthrough
podman run --rm --device /dev/dri ubuntu:24.04 vulkaninfo | head -5

# Thermal monitoring for 5 minutes
~/.openclaw/thermal-monitor.sh

# Overhead benchmark
top -l 1 | grep "CPU usage"
```

**Pass criteria**: GPU detected, thermal stable, CPU <5%, memory <5GB

---

### Phase 3 Gate: LLM Performance
Run before proceeding to Phase 4:
```bash
# Verify Metal enabled
ollama serve  # Should show "metal: initialized"

# Test model loading
ollama run llama3.3:agent "Hello in 5 words"

# Benchmark (2-3 minutes)
~/.openclaw/benchmark-ollama.sh

# Voice latency test
~/.openclaw/latency-test.sh
```

**Pass criteria**: 25+ TPS, <2s latency, no OOM errors

---

### Phase 4 Gate: Agent Operability
Run before production use:
```bash
# Verify Ollama connectivity
curl http://127.0.0.1:11434/api/tags

# Start OpenClaw daemon
openclaw start --config ~/.openclaw/openclaw.json

# Test voice approval via Telegram (manual)
# Send voice message "Create a test file"
# Respond to approval request with "Approve"
# Verify file creation in logs

# Audit trail
tail -50 ~/.openclaw/audit.log
```

**Pass criteria**: OpenClaw daemon running, Telegram responsive, approval flow works, audit log clean

---

## Troubleshooting by Symptom

### "VoiceOver won't start"
1. Check System Settings > Sound > Output (volume not muted)
2. Restart VoiceOver: Cmd + F5 twice
3. Run: `defaults write com.apple.accessibility voiceOverOnOffKey -bool true`

### "Podman machine crashes"
1. Check logs: `podman machine ssh -- journalctl -xe`
2. Reinitialize: `podman machine rm openclaw-machine && podman machine init ...`
3. Check disk space: `df -h`

### "Ollama runs on CPU, not GPU"
1. Verify Metal: `ollama serve` should show "metal: initialized"
2. Check environment: `echo $OLLAMA_METAL` should return "1"
3. Reload shell: `source ~/.zshrc`

### "OpenClaw daemon crashes"
1. Check logs: `tail -100 ~/.openclaw/openclaw.log`
2. Verify Ollama running: `ollama list`
3. Verify Telegram token valid in config

### "Voice approval times out"
1. Check Telegram bot token in config
2. Verify user is in `approved_users` list
3. Increase timeout: Change `timeout_seconds` in openclaw.json to 120

---

## File Structure

After completing all phases, your `~/.openclaw` directory looks like:

```
~/.openclaw/
├── openclaw.json              # Main config
├── approval-config.yaml       # Approval flow settings
├── modelfile.llama            # Ollama model definition
├── podman-compose.yml         # Container orchestration
├── thermal-monitor.sh         # Thermal monitoring daemon
├── voice-commands.sh          # Voice command handler
│
├── models/                    # Ollama model cache (30-50GB)
│   └── blobs/                # GGUF model files
│
├── memory/                    # Agent memory (persistent)
│   └── conversation.json      # Chat history
│
├── logs/                      # Operational logs
│   ├── openclaw.log          # Main agent log
│   ├── audit.log             # Approval audit trail
│   └── thermal.log           # Thermal alerts
│
└── backups/                   # Daily backups (Phase 6)
    └── openclaw-config-[date].json
```

---

## Key Knowledge Gaps (Addressed in Manuals)

1. **GPU Passthrough on macOS**: Vulkan-to-Metal achieves 70-80% native speed
2. **Model Quantization**: Q4_K_M best for M-series; minimal accuracy loss
3. **Voice Latency**: 4K context gives <2s response; 8K context = 10s+
4. **Thermal Management**: Monitor pmset; reduce parallel inference if throttling
5. **Approval Flows**: Voice-first with keyboard fallback; always timeout-safe
6. **Data Isolation**: Burner identity + sandbox prevents leakage
7. **Knowledge Displacement**: Chain-of-thought prompting recovers quantization losses

---

## Next Steps After Completion

### Immediate (Week 1)
- Use agent for simple tasks (file creation, basic queries)
- Monitor logs for errors
- Adjust voice latency if needed (switch models)
- Test approval flow with real commands

### Short-term (Weeks 2-4)
- Proceed to Phase 5 (Security Hardening)
- Implement critique loops (secondary verification)
- Set up remote access (Cloudflare Zero Trust)
- Increase task complexity

### Long-term (Month 2+)
- Proceed to Phase 6 (Advanced Scaling) if needed
- Consider multi-Mac clustering for >70B models
- Implement SparseML for 60-80% compression
- Automate monthly security audits

---

## Contact & Support

### Documentation
- **Ollama Docs**: https://docs.ollama.com
- **OpenClaw GitHub**: https://github.com/psteinberger/openclaw
- **macOS Accessibility**: https://support.apple.com/en-us/HT211022
- **Apple M-series GPU**: https://developer.apple.com/metal

### Troubleshooting Communities
- **Ollama Discord**: https://discord.gg/ollama
- **OpenClaw Discussions**: GitHub Issues
- **AppleVis (Blind accessibility)**: https://www.applevis.com

### Testing & Benchmarking
- **llm.aidatatools.com**: LLM benchmarking tool
- **NVIDIA Jetson Benchmarks**: For reference (not M-series specific)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2026 | Initial release; Phases 1-4 production-ready |
| 1.1 | (TBD) | Phase 5-6 detailed; SparseML 2026 updates |
| 2.0 | (TBD) | Multi-device clustering; Exo Labs integration |

---

## Appendix A: Environment Variables Reference

```bash
# Ollama
export OLLAMA_GPU_LAYERS=99        # All layers on GPU
export OLLAMA_NUM_GPU=1             # Single GPU
export OLLAMA_METAL=1               # Enable Metal
export OLLAMA_NUM_CTX=4096          # Context window
export OLLAMA_HOST=127.0.0.1:11434  # API endpoint

# Podman
export OLLAMA_VULKAN=1              # Vulkan passthrough
export PODMAN_CPUS=12               # CPU allocation

# OpenClaw
export OPENCLAW_MODEL=llama3.3:agent
export OPENCLAW_GATEWAY_HOST=0.0.0.0:8080
export OPENCLAW_TELEGRAM_BOT_TOKEN=[token]
```

---

## Appendix B: Accessibility Best Practices

### For VoiceOver Users
1. Keep outputs short (TTS reads faster)
2. Use simple language (avoid technical jargon in agent responses)
3. Announce actions clearly (e.g., "File created" not "Success")
4. Test every command before full deployment

### For Braille Display Users
1. Enable braille in Phase 1
2. Test braille display with each phase
3. Set appropriate braille table (US English or your language)

### For Voice-First Users
1. Dictation works best in quiet rooms
2. Speak clearly and at moderate pace
3. System training improves accuracy over time
4. Use Voice Control for app launching, Dictation for text input

---

## Appendix C: Security Audit Checklist

**Run monthly**:
```bash
openclaw security audit --verbose
```

**Manual checks**:
- [ ] Audit log reviewed (no unexpected actions)
- [ ] Approval log shows all actions approved
- [ ] No failed authentications
- [ ] Thermal log shows no critical throttling
- [ ] Disk usage <80%
- [ ] Model files untouched (checksum verification)

---

## Appendix D: Model Recommendations by Use Case

| Use Case | Primary Model | Fallback | Context |
|----------|---------------|----------|---------|
| Agent reasoning | Llama 3.3 70B | DeepSeek 33B | 4K |
| Code generation | DeepSeek 67B | Mistral 7B | 8K |
| Fast response | Mistral 7B | Llama 2 7B | 4K |
| Document analysis | Llama 3.3 70B | - | 8K |
| Brainstorming | Llama 3.3 70B | Mistral | 4K |

---

## Summary

You now have a **complete, hands-free, local AI agent** that:

✅ Runs entirely on your Mac (zero cloud data leakage)
✅ Communicates via voice (Telegram voice messages)
✅ Approves actions audibly (VoiceOver announcements)
✅ Executes tasks autonomously (file ops, research, automation)
✅ Logs everything (audit trail for transparency)
✅ Works for blind users (fully accessible)
✅ Achieves 25+ TPS (fast enough for real work)
✅ Costs $0 to operate (local hardware only)

**Next step**: Pick Phase 1 and begin.
