---
title: PHASE 4 Blueprint — Background Inference Integration (Week 4)
author: Copilot CLI (Token Optimization)
date: 2026-02-25T23:59:00Z
phase: 4
week: 4
effort: 14 hours
token_cost: 1200
---

# 📋 PHASE 4 BLUEPRINT: Background Inference Integration

## ⚡ Quick Summary

**What**: Deploy 24/7 ONNX model for research, curation, maintenance  
**When**: Week 4  
**Why**: Enable continuous knowledge improvement, research job execution, stack optimization  
**Effort**: 14 hours (infrastructure setup + job executor + monitoring)  
**Success**: Model runs stable <6GB RAM, executes 5+ jobs daily, zero OOM errors  

---

## ✅ EXECUTION CHECKLIST

### Task 1: Setup ONNX Runtime (2-2.5h)
- [ ] Install ONNX Runtime: `pip install onnxruntime`
- [ ] Download model: fastembed ONNX model (384-dim) or similar
- [ ] Store in: `models/fastembed-384-onnx/`
- [ ] Test: Load model, generate embedding for test query
- [ ] Verify: Latency <100ms, memory <1GB

### Task 2: Configure Vulkan GPU Support (1-1.5h)
- [ ] Enable Vulkan for GPU acceleration: `export ONNXRUNTIME_EXECUTION_PROVIDER=vulkan`
- [ ] Test on AMD RADV (current hardware)
- [ ] Verify: Latency <50ms with GPU (vs. 100ms CPU)
- [ ] Monitor: GPU memory usage (target: <2GB)

### Task 3: Create Research Job Executor (3-4h)
- [ ] Create `app/XNAi_rag_app/background/research_job_executor.py`
- [ ] Load research queue from database (RQ-161 through RQ-168)
- [ ] For each job:
    - [ ] Load job spec: name, effort estimate, parameters
    - [ ] Execute job using ONNX model + async
    - [ ] Store results in database
    - [ ] Mark job complete + timestamp
- [ ] Retry on failure: 3 attempts with exponential backoff
- [ ] Test: Execute 3 research jobs manually, verify results stored

### Task 4: Create Curation Worker (2-2.5h)
- [ ] Create `app/XNAi_rag_app/background/curation_worker.py`
- [ ] Scan new documents in knowledge base
- [ ] For each document:
    - [ ] Generate embedding using ONNX model
    - [ ] Extract key entities, tags
    - [ ] Assign quality score (0-100)
    - [ ] Store metadata in Qdrant
- [ ] Run daily: process all documents added in last 24h
- [ ] Test: Process 100 test documents, verify Qdrant updated

### Task 5: Create Maintenance Scheduler (2-2.5h)
- [ ] Create `app/XNAi_rag_app/background/maintenance_scheduler.py`
- [ ] Daily tasks:
    - [ ] Health check all services
    - [ ] Optimize Qdrant indices (HNSW ef_construct tuning)
    - [ ] Cleanup old logs/metrics (>30 days)
    - [ ] Generate health report (metrics, errors, warnings)
- [ ] Weekly tasks:
    - [ ] Rebuild full-text search index
    - [ ] Vacuum PostgreSQL database
    - [ ] Backup critical data
- [ ] Test: Execute daily tasks, verify no errors

### Task 6: Setup Continuous Execution (2-2.5h)
- [ ] Create systemd service: `xnai-background-inference.service`
- [ ] Start on boot, restart on failure
- [ ] Resource limits: `MemoryLimit=6G, CPUQuota=50%`
- [ ] Healthcheck: Verify model still responding every 5 minutes
- [ ] Test: Start service, verify running in background
- [ ] Verify: Process restarts if killed

### Task 7: Add Monitoring & Alerts (2-3h)
- [ ] Add Prometheus metrics:
    - [ ] `background_model_latency_ms` (histogram)
    - [ ] `background_research_jobs_completed` (counter)
    - [ ] `background_memory_usage_bytes` (gauge)
    - [ ] `background_errors_total` (counter)
- [ ] Setup Grafana dashboard: background model metrics
- [ ] Setup AlertManager rules:
    - [ ] Alert if model latency >1000ms
    - [ ] Alert if memory usage >7GB (OOM risk)
    - [ ] Alert if jobs failing >10% of time
- [ ] Test: Trigger alert conditions, verify notifications sent

---

## 🎯 SUCCESS CRITERIA

- ✅ ONNX model loads in <5 seconds on startup
- ✅ Inference latency <100ms (CPU) or <50ms (GPU)
- ✅ Memory usage stable <6GB
- ✅ Research job executor running continuously
- ✅ Curation worker processing new documents daily
- ✅ Maintenance scheduler executing on schedule
- ✅ Zero OOM errors in 72-hour test
- ✅ Background service restarts automatically on failure
- ✅ All metrics visible in Prometheus/Grafana
- ✅ Alerts firing correctly for error conditions

---

## 🚨 COMMON PITFALLS

### Pitfall 1: ONNX Model Won't Load on GPU
- **Problem**: GPU memory exhausted, model falls back to CPU
- **Solution**: Check GPU memory: `glxinfo | grep "Device:"` or AMD equivalent
- **Check**: Monitor `nvidia-smi` or AMD GPU metrics during startup

### Pitfall 2: Research Jobs Queued Forever
- **Problem**: Job executor crashed, queue never processes
- **Solution**: Add healthcheck, auto-restart on failure
- **Check**: Verify executor process running: `ps aux | grep research_job_executor`

### Pitfall 3: Memory Leak in Background Model
- **Problem**: Memory usage grows over 72 hours
- **Solution**: Properly cleanup ONNX session, close connections
- **Check**: Monitor memory every hour, should be <100MB delta

### Pitfall 4: Systemd Service Won't Start
- **Problem**: Service file syntax error, permission denied
- **Solution**: Check systemd logs: `journalctl -u xnai-background-inference -n 50`
- **Check**: Verify file permissions: `ls -la /etc/systemd/system/*.service`

### Pitfall 5: Alerts Firing Too Often (Noisy)
- **Problem**: Alert threshold too sensitive, spam notifications
- **Solution**: Add hysteresis (e.g., alert if >7GB for >5 minutes)
- **Check**: Tune thresholds based on baseline metrics

---

## 📞 CRITICAL NOTES

**From RJ-014 (MC Architecture Analysis)**:
- *When available, append MC Overseer scheduling considerations here*
- *May include batch vs. continuous execution guidance*
- *Current status: Pending completion*
- *ETA: 2026-02-26 EOD*

---

## 🔗 REFERENCE

- **ONNX patterns**: See CODE-EXAMPLES-REPOSITORY.md (Background Model section)
- **Scheduling**: See ARCHITECTURE-DECISION-RECORDS.md (ADR-004)
- **Monitoring**: `memory_bank/strategies/KNOWLEDGE-ABSORPTION-SYSTEM-DESIGN.md`
- **Research queue**: `memory_bank/RESEARCH-JOBS-QUEUE-UPDATED-2026-02-25.md`

---

**Effort**: 14 hours  
**Week**: 4  
**Token cost**: 1,200 tokens (this doc)  
**Success metric**: 24/7 background inference, 5+ research jobs daily  
**Status**: ✅ Ready for execution
