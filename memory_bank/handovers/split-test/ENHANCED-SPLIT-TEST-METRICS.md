# Enhanced Split Test Metrics Infrastructure

**Date**: 2026-02-26  
**Status**: Design Document  
**Purpose**: Define comprehensive metrics, infrastructure, and data handling for Wave 5 Manual Split Test

---

## 1. Executive Summary

This document outlines the enhanced metrics infrastructure for the Raptor vs Haiku vs MiniMax M2.5 split test. We leverage existing XNAi Foundation infrastructure (Redis, PostgreSQL, session storage) to capture rich performance and quality data.

Recent enhancements include:

- **Local model support** via `LocalModelAdapter` allowing on‑disk ONNX/GGUF models to be evaluated alongside CLI-based providers.
- **Adapter flag (`--adapter`)** for switching seamlessly between CLI and local execution, enabling benchmarks against custom, domain‑tuned models.
- **Session logging**: every result is now stored in `SessionManager` under keys like `result:<model_id>` for debugging and history.
- **Knowledge indexing**: outputs are upserted into the knowledge vector store (KnowledgeClient/Qdrant) with fallback logic to ensure `qdrant_collection` is always available.
- **Error resilience**: non‑zero exit codes, missing CLIs, and unavailable Redis/Qdrant services are gracefully handled and reflected in metrics.

---

## 2. Additional Metrics to Measure

### 2.1 Timing Metrics

| Metric | Description | Infrastructure | Feasibility |
|--------|-------------|---------------|-------------|
| **Total Execution Time** | Wall-clock time from start to completion | Shell `time` command | ✅ High |
| **First Token Latency** | Time to first output | CLI output timestamps | ✅ High |
| **Token Generation Speed** | Tokens/second during output | CLI verbose mode | ✅ Medium |
| **Context Loading Time** | Time to load context files | Shell timestamps | ✅ High |
| **Thinking Time** | Time spent in reasoning (if available) | Model metadata | ⚠️ Partial |
| **Idle Time** | Time between interactions | Session logs | ✅ High |
| **Checkpoint Duration** | Time per phase/segment | Manual markers | ✅ High |

### 2.2 Token Metrics

| Metric | Description | Infrastructure | Feasibility |
|--------|-------------|---------------|-------------|
| **Input Tokens** | Tokens in context + prompt | Provider API (if available) | ⚠️ Estimate |
| **Output Tokens** | Tokens in generated manual | CLI output length | ✅ High |
| **Context Efficiency** | Output tokens / Input tokens ratio | Calculation | ✅ High |
| **Token Waste** | Redundant or repeated content | Quality analysis | ⚠️ Medium |

### 2.3 Quality Metrics

| Metric | Description | Infrastructure | Feasibility |
|--------|-------------|---------------|-------------|
| **File Path Accuracy** | % of valid file paths | Automated validation | ✅ High |
| **Technical Correctness** | Accuracy of technical details | Manual review | ✅ Manual |
| **Hallucination Rate** | Fabricated vs. factual content | Manual review | ✅ Manual |
| **Completeness Score** | Phases covered / 5 | Automated count | ✅ High |
| **Structure Score** | TOC presence, navigation | Automated validation | ✅ High |
| **Actionability Score** | Executable steps count | Automated analysis | ✅ High |

### 2.4 Behavioral Metrics

| Metric | Description | Infrastructure | Feasibility |
|--------|-------------|---------------|-------------|
| **Revision Count** | Number of edits/regenerations | Session events | ✅ High |
| **Prompt Iterations** | Times user prompted for changes | Session events | ✅ High |
| **Error Recovery** | Errors encountered and recovered | Session logs | ✅ High |
| **Tool Usage** | Commands/files accessed per session | Session tracking | ✅ Medium |

### 2.5 Infrastructure Metrics

| Metric | Description | Infrastructure | Feasibility |
|--------|-------------|---------------|-------------|
| **Memory Usage** | Peak memory during execution | `psutil` / `free` | ✅ High |
| **CPU Usage** | Average CPU % during execution | `psutil` | ✅ High |
| **Network I/O** | Bytes sent/received | `psutil` | ✅ High |
| **Disk I/O** | Read/write operations | `iostat` | ✅ Medium |

---

## 3. Infrastructure Capabilities

### 3.1 Available Infrastructure

| Component | Location | Capability | Use Case |
|-----------|----------|------------|----------|
| **Redis** | `app/XNAi_rag_app/core/redis_streams.py` | Session cache, streams | Real-time metrics, event queue |
| **PostgreSQL** | `app/XNAi_rag_app/core/database_connection_pool.py` | Structured data | Long-term metrics storage |
| **Prometheus** | `app/XNAi_rag_app/core/metrics.py` | Time-series metrics | System monitoring |
| **Copilot Sessions** | `~/.copilot/session-state/` | Chat logs, events | Conversation history, thinking |
| **OpenCode Sessions** | `~/.local/share/opencode/storage/session/` | Chat logs | Conversation history |
| **Qdrant** | Vector database | Semantic search | Query past performance |
| **FAISS** | Local vector store | Similarity search | Compare outputs |
| **Vikunja** | Task management | Task tracking | Test execution tracking |

### 3.2 Session Storage Analysis

**Copilot CLI** (`~/.copilot/session-state/{session_id}/`):
```
├── events.jsonl        # Full conversation + metadata (15MB)
├── plan.md            # Implementation plan
├── checkpoints/       # State snapshots
└── files/            # Referenced files
```

**OpenCode CLI** (`~/.local/share/opencode/storage/session/{hash}/`):
```
├── ses_{id}.json     # Session conversation
└── ...               # Additional files
```

---

## 4. Chat Log & Thinking Capture

### 4.1 Current Capabilities

**Copilot CLI**:
- `events.jsonl` contains: role, content, timestamps, tool_calls
- Model metadata (if thinking enabled): reasoning content
- Captures: full conversation history

**OpenCode CLI**:
- Session JSON contains: messages, timestamps, token usage
- Can enable verbose mode for detailed logs

### 4.2 Capture Strategy

```bash
# Capture Copilot session
SESSION_ID="bd405cba-b149-40b4-ab56-c489d05be959"
cat ~/.copilot/session-state/$SESSION_ID/events.jsonl > \
    outputs/raptor-wave5-manual/events.jsonl

# Capture OpenCode session
cp ~/.local/share/opencode/storage/session/*/ses_*.json \
    outputs/minimax-wave5-manual/session.json
```

---

## 5. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPLIT TEST EXECUTION                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │ RAPTOR   │    │  HAIKU   │    │ MINIMAX  │                  │
│  │   CLI    │    │   CLI    │    │   CLI    │                  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘                  │
│       │               │               │                         │
│       ▼               ▼               ▼                         │
│  ┌──────────────────────────────────────────┐                  │
│  │         METRICS COLLECTION LAYER           │                  │
│  │  - Time tracking (shell)                  │                  │
│  │  - Token counting (CLI output)            │                  │
│  │  - Session capture (file copy)            │                  │
│  │  - System metrics (psutil)                │                  │
│  └──────────────────┬─────────────────────────┘                  │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────┐                  │
│  │            DATA STORAGE LAYER              │                  │
│  ├──────────────────────────────────────────┤                  │
│  │ Redis Streams    │ Real-time events     │                  │
│  │ PostgreSQL      │ Structured metrics    │                  │
│  │ File System     │ Chat logs, outputs   │                  │
│  │ Qdrant          │ Semantic analysis     │                  │
│  └──────────────────┬─────────────────────────┘                  │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────┐                  │
│  │           ANALYSIS LAYER                   │                  │
│  │  - Comparative analysis                    │                  │
│  │  - Quality scoring                        │                  │
│  │  - Pattern detection                      │                  │
│  └──────────────────────────────────────────┘                  │
```

---

## 6. Enhanced Metrics JSON Schema

```json
{
  "test_id": "WAVE-5-MANUAL-SPLIT-TEST-2026-02-26",
  "model": "raptor-mini",
  "run_id": "raptor-run-001",
  
  "timing": {
    "total_execution_seconds": 7200,
    "first_token_latency_ms": 1500,
    "avg_token_generation_tokens_per_sec": 45,
    "context_loading_seconds": 30,
    "thinking_time_seconds": null,
    "idle_time_seconds": 120,
    "checkpoint_durations": {
      "phase_5a": 1200,
      "phase_5b": 900,
      "phase_5c": 1100,
      "phase_5d": 800,
      "phase_5e": 950
    }
  },
  
  "tokens": {
    "input_tokens_estimated": 45000,
    "output_tokens": 18500,
    "context_efficiency": 0.41,
    "token_waste_percentage": 5
  },
  
  "quality": {
    "file_path_accuracy": 0.95,
    "technical_correctness_score": 4.2,
    "hallucination_rate": 0.02,
    "completeness_score": 1.0,
    "structure_score": 4.5,
    "actionability_score": 4.0
  },
  
  "behavioral": {
    "revision_count": 3,
    "prompt_iterations": 2,
    "error_count": 1,
    "error_recovery_time_seconds": 60,
    "tools_used": ["read", "write", "grep", "glob"],
    "files_accessed": 24
  },
  
  "infrastructure": {
    "peak_memory_mb": 2048,
    "avg_cpu_percent": 35,
    "network_bytes_sent": 1500000,
    "network_bytes_received": 8000000,
    "disk_read_mb": 450,
    "disk_write_mb": 120
  },
  
  "session": {
    "session_id": "copilot-session-uuid",
    "events_file": "events.jsonl",
    "has_thinking_logs": true,
    "conversation_turns": 156,
    "total_messages": 312
  },
  
  "output": {
    "file_path": "WAVE-5-MANUAL.md",
    "file_size_bytes": 85000,
    "line_count": 2450,
    "word_count": 15200
  }
}
```

---

## 7. Implementation Components

### 7.1 Metrics Collection Script

```python
#!/usr/bin/env python3
"""
Split Test Metrics Collector
Collects timing, token, quality, and behavioral metrics
"""

import json
import time
import psutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class SplitTestMetrics:
    def __init__(self, model_name: str, output_dir: Path):
        self.model_name = model_name
        self.output_dir = output_dir
        self.start_time = None
        self.metrics = {
            "test_id": "WAVE-5-MANUAL-SPLIT-TEST-2026-02-26",
            "model": model_name,
            "run_id": f"{model_name}-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timing": {},
            "tokens": {},
            "quality": {},
            "behavioral": {},
            "infrastructure": {},
            "session": {},
            "output": {}
        }
        
    def start(self):
        """Start metrics collection"""
        self.start_time = time.time()
        self.metrics["start_timestamp"] = datetime.now().isoformat()
        
    def collect_system_metrics(self):
        """Collect CPU, memory, network metrics"""
        self.metrics["infrastructure"] = {
            "peak_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
            "avg_cpu_percent": psutil.cpu_percent(interval=1),
            "network_io": psutil.net_io_counters()._asdict()
        }
        
    def capture_session(self, session_path: str):
        """Copy session logs for analysis"""
        # Copy events.jsonl or session.json
        pass
        
    def finalize(self):
        """Complete metrics collection"""
        self.metrics["timing"]["total_execution_seconds"] = time.time() - self.start_time
        self.metrics["end_timestamp"] = datetime.now().isoformat()
        
        # Save metrics
        output_file = self.output_dir / "METRICS.json"
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
        return self.metrics
```

### 7.2 Redis Stream Integration

```python
# Push metrics to Redis for real-time monitoring
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def push_metrics(metrics: Dict):
    """Push metrics to Redis stream"""
    r.xadd('split-test-metrics', {
        'model': metrics['model'],
        'run_id': metrics['run_id'],
        'timing': json.dumps(metrics['timing']),
        'timestamp': datetime.now().isoformat()
    })
```

### 7.3 PostgreSQL Schema

```sql
CREATE TABLE split_test_results (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(100),
    model VARCHAR(50),
    run_id VARCHAR(100),
    total_time_seconds FLOAT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    completeness_score FLOAT,
    accuracy_score FLOAT,
    actionability_score FLOAT,
    file_path_accuracy FLOAT,
    revision_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE split_test_events (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(100),
    event_type VARCHAR(50),
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. Knowledge Gaps & Recommendations

### 8.1 Identified Gaps

| Gap | Status | Priority | Recommendation |
|-----|--------|----------|-----------------|
| Exact token counting per model | ❓ Unknown | HIGH | Use CLI verbose output or estimate |
| Thinking time capture | ⚠️ Partial | MEDIUM | Enable thinking mode, capture metadata |
| Cross-session comparison | ❓ Unknown | HIGH | Use Qdrant for semantic similarity |
| Automated quality scoring | ⚠️ Manual | MEDIUM | Create rubric-based scorer |
| Real-time dashboard | ❌ None | LOW | Build Streamlit app |

### 8.2 Recommendations

1. **Use Redis Streams** for real-time metrics during execution
2. **Capture session logs** immediately after each run
3. **Store in PostgreSQL** for structured querying
4. **Index in Qdrant** for semantic similarity analysis
5. **Build comparison dashboard** for visual analysis

---

## 9. Updated Execution Protocol

### 9.1 Pre-Execution

```bash
# 1. Start Redis for real-time metrics
redis-server --daemonize yes

# 2. Initialize PostgreSQL table
psql -f create_split_test_tables.sql

# 3. Create output directories
mkdir -p outputs/{raptor,haiku,minimax}-wave5-manual/{metrics,sessions}

# 4. Start system monitoring (background)
python3 scripts/monitor_system.py &
```

### 9.2 Per-Model Execution

```bash
# Raptor Mini
START_TIME=$(date +%s)
copilot -m raptor-mini-preview "Create Wave 5 Manual..." 2>&1 | tee raptor_output.log
END_TIME=$(date +%s)

# Capture metrics
python3 scripts/collect_metrics.py \
    --model raptor-mini \
    --output-dir outputs/raptor-wave5-manual \
    --start-time $START_TIME \
    --end-time $END_TIME

# Capture session
cp ~/.copilot/session-state/*/events.jsonl outputs/raptor-wave5-manual/sessions/

# Store in Redis
python3 scripts/push_to_redis.py outputs/raptor-wave5-manual/METRICS.json
```

### 9.3 Post-Execution Analysis

```bash
# Compare outputs
python3 scripts/compare_results.py \
    outputs/raptor-wave5-manual \
    outputs/haiku-wave5-manual \
    outputs/minimax-wave5-manual

# Semantic analysis with Qdrant
python3 scripts/qdrant_index.py

# Generate comparison report
python3 scripts/generate_report.py
```

---

## 10. File Manifest

### New Files to Create

| File | Purpose |
|------|---------|
| `scripts/split_test_metrics.py` | Main metrics collector |
| `scripts/monitor_system.py` | Background system monitoring |
| `scripts/compare_results.py` | Comparative analysis |
| `scripts/qdrant_index.py` | Qdrant indexing for similarity |
| `scripts/push_to_redis.py` | Redis stream pusher |
| `scripts/generate_report.py` | Report generator |
| `sql/split_test_tables.sql` | PostgreSQL schema |
| `configs/split_test_config.yaml` | Test configuration |

---

## 11. Next Steps

1. **Create metrics collection scripts** (this session)
2. **Set up PostgreSQL table** (pre-execution)
3. **Verify Redis accessibility** (pre-execution)
4. **Test Qdrant indexing** (post-execution)
5. **Build comparison dashboard** (post-execution)

---

**Last Updated**: 2026-02-26  
**Status**: Ready for Implementation  
**Coordination Key**: `SPLIT-TEST-METRICS-INFRASTRUCTURE-2026-02-26`
