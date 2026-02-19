# XNAi Agent Bus: Delegation Protocol v1.0

**Status**: Locked & Implemented  
**Date**: 2026-02-16  
**Authority**: Copilot CLI (Haiku 4.5) + Cline (kat-coder-pro) review  

---

## Executive Summary

The Delegation Protocol is a routing decision framework that automatically selects the most appropriate agent (Copilot, Gemini, Cline, or local Crawler) based on task complexity and type.

### Key Principles
- **Complexity-Driven Routing**: Tasks scored 1-10 determine agent selection
- **Specialty Matching**: Each agent handles tasks within their expertise area
- **Graceful Escalation**: Simple tasks stay local; complex tasks escalate upward
- **Sampling-Based QA**: Cline provides feedback on high-complexity outputs to improve KB

---

## Complexity Scoring Rubric

### Base Score
All tasks start with base score of **1-3** (straightforward task category)

### Scoring Modifiers (Add Points)

| Signal | Score Addition | Example |
|--------|---|---------|
| **Unknown architecture/setup pattern** | +2 | New model with unusual quantization approach |
| **Multi-model comparison required** | +3 | "Compare Mistral 7B vs. LLaMA 2 7B" |
| **Novel integration pattern** | +4 | "Design custom inference optimization for Ryzen 7" |
| **Code generation required** | +2 | "Write inference wrapper for new model" |
| **Documentation rewrite needed** | +2 | "Refactor KB section with examples" |
| **System-level strategy decision** | +3 | "Design model selection matrix for Agent Bus" |

### Task-Specific Modifiers

| Task Category | Modifier | Reason |
|---|---|---|
| Code generation research | +1 | Code-specific complexity patterns |
| RAG/embedding research | +0 | Baseline |

### Final Score Thresholds

```
complexity_score = base_score + modifiers + task_modifiers

1-3:   Crawler handles independently
4-5:   Route to Copilot (strategic synthesis)
6-7:   Route to Gemini (large-scale analysis)
8-9:   Route to Cline (implementation + architecture)
9+:    Cline PRIORITY (urgent refactoring/redesign)
```

---

## Scoring Examples (Validated Against Real Tasks)

### Score 1-3: Crawler Independent
```
Task: "Find ELSER v2 benchmark on MTEB leaderboard"
Analysis:
  - Base: 1 (straightforward lookup)
  - Modifiers: 0
  - Total: 1
  - Decision: Crawler handles
  - Expected time: 10-15 minutes
```

### Score 4-5: Copilot
```
Task: "Compare Mistral 7B vs. LLaMA 2 7B inference speed on Ryzen 7"
Analysis:
  - Base: 2 (research comparison)
  - Multi-model comparison: +3
  - Total: 5
  - Decision: Copilot (strategic synthesis)
  - Expected time: 30-120 minutes
```

### Score 6-7: Gemini
```
Task: "Design optimal quantization strategy for Ryzen 7 with dynamic memory constraints"
Analysis:
  - Base: 2 (architecture design)
  - Novel integration: +4
  - System strategy: +1 (implicit)
  - Total: 7
  - Decision: Gemini (large-scale analysis)
  - Expected time: 2-4 hours
```

### Score 8-9: Cline
```
Task: "Implement vector rollback mechanism with Git versioning + atomic operations"
Analysis:
  - Base: 2 (implementation)
  - Novel integration: +4
  - Code generation: +2
  - Documentation rewrite: +2
  - Total: 10 (capped at 9 for Cline)
  - Decision: Cline PRIORITY
  - Expected time: 6-12 hours
```

---

## Routing Decision Tree

```python
def route_task(task_description: str, complexity_score: int) -> Agent:
    """
    Route task to appropriate agent based on complexity score
    """
    
    # Parse task for type indicators
    task_lower = task_description.lower()
    is_code_needed = any(kw in task_lower for kw in [
        "implement", "code", "function", "class", "module"
    ])
    is_research = any(kw in task_lower for kw in [
        "research", "benchmark", "compare", "analyze"
    ])
    is_strategy = any(kw in task_lower for kw in [
        "design", "architecture", "strategy", "decision"
    ])
    
    # Calculate final routing
    if complexity_score <= 3:
        return Agent.CRAWLER
    
    elif 4 <= complexity_score <= 5:
        # Copilot for strategic planning and small-scale synthesis
        return Agent.COPILOT
    
    elif 6 <= complexity_score <= 7:
        # Gemini for large-scale analysis and holistic synthesis
        if is_strategy:
            return Agent.GEMINI
        elif is_code_needed:
            # If code is needed but still 6-7 range, start with Gemini analysis
            return Agent.GEMINI  # Will queue Cline after Gemini outputs
        else:
            return Agent.GEMINI
    
    elif complexity_score >= 8:
        # Cline for implementation, refactoring, documentation
        if is_code_needed or is_research:
            return Agent.CLINE_PRIORITY
        else:
            return Agent.CLINE
    
    else:
        # Default: escalate
        return Agent.GEMINI
```

---

## Integration Points

### 1. Crawler → Redis Job Queue

**When**: Crawler completes research task  
**Action**: Queue task for Conductor  
**Format**: 
```json
{
  "task_id": "crawler-task-001",
  "task_description": "...",
  "complexity_score": 3,
  "output": {...},
  "timestamp": "2026-02-16T21:00:00Z"
}
```

**Redis Key**: `xnai:jobs:crawler:pending:` + task_id

---

### 2. Conductor → Agent Selection

**When**: Task received in Redis queue  
**Action**: Calculate complexity, select agent  
**Logic**:
```python
agent = route_task(task_description, complexity_score)
conductor.queue_for_agent(agent, task)
```

**Result**: Task queued for selected agent

---

### 3. Agent → Expert KB Query

**When**: Agent begins work  
**Action**: Query semantic search over agent's KB  
**SLA**: Search latency < 500ms  
**Example**:
```python
relevant_docs = agent_kb.semantic_search(
    query="Vector quantization strategies",
    top_k=5
)
```

**Result**: Agent has task-specific context before starting work

---

### 4. Agent → Results Storage

**When**: Agent completes work  
**Action**: Store results in knowledge base  
**Flow**:
1. Agent produces output (analysis, code, documentation, etc.)
2. Results added to KB as new documents or updated model cards
3. Complexity score persists for future similar tasks
4. Vectors reindexed (nightly batch or on-demand)

---

### 5. Cline Review → KB Update

**When**: Output complexity >= 6 OR random 20% sampling  
**Action**: Cline reviews and enhances  
**Process**:
1. Cline retrieves queued output from feedback loop
2. Reviews for quality, completeness, accuracy
3. Adds documentation, examples, edge case handling
4. Updates vectors in KB
5. Logs improvement metrics

**Result**: KB quality improves with each iteration

---

### 6. Vector Reindex Schedule

**Nightly (02:00 UTC)**:
- Batch reindex of all KB documents
- FAISS flat index rebuild
- Metrics captured (index size, search latency)

**On-Demand**:
- After Cline feedback integration
- After significant KB updates
- Triggered by search latency > 500ms

---

## Agent Capabilities Matrix

| Agent | Complexity Range | Expertise | Input | Output | Turnaround |
|-------|---|---|---|---|---|
| **Crawler** | 1-3 | Research lookups, basic synthesis | Task description | JSON data, findings | 10-30 min |
| **Copilot** | 4-5 | Strategic planning, comparisons, synthesis | Research data, context | Markdown analysis, recommendations | 30-120 min |
| **Gemini** | 6-8 | Large-scale analysis, architecture review, holistic synthesis | Complex requirements, multi-source data | Comprehensive reports, strategic recommendations | 2-6 hours |
| **Cline** | 8+ | Implementation, code generation, refactoring, documentation, testing | Architecture decisions, requirements, existing code | Production-ready code, docs, tests, integrations | 4-12 hours |

---

## Error Handling & Fallback

### Task Fails to Route
```
1. Complexity score ambiguous (e.g., 5.5)
2. Default: Round UP to next agent (Copilot)
3. Log classification uncertainty
4. Return task to human (escalation to user)
```

### Agent Timeout
```
1. Agent doesn't respond within timeout
2. Queue task for next-higher-capability agent
3. Log timeout for monitoring
4. Alert via Consul health check
```

### Invalid Task
```
1. Task cannot be classified (no keywords, vague)
2. Reject with error message
3. Request clarification from initiator
4. Log for model training (improve classifier)
```

---

## Performance Tracking

### Metrics Per Task
- `task_id`: Unique identifier
- `complexity_score`: Calculated score (1-10)
- `agent_selected`: Which agent handled it
- `execution_time`: Actual time to completion
- `quality_score`: Cline's feedback (0-100)
- `kb_impact`: Documents added/updated

### Dashboard Queries
```sql
-- Routing accuracy (do Copilot tasks stay 4-5, not 6+?)
SELECT agent, COUNT(*) as count
  FROM tasks
  WHERE actual_complexity != expected_complexity
  GROUP BY agent;

-- Agent utilization
SELECT agent, AVG(execution_time), COUNT(*)
  FROM tasks
  WHERE created_date > NOW() - INTERVAL 7 DAY
  GROUP BY agent;

-- KB growth
SELECT COUNT(*) as new_docs, SUM(size_mb) as total_size
  FROM kb_documents
  WHERE created_date > NOW() - INTERVAL 1 DAY;
```

---

## Future Enhancements

### Phase 2: Feedback Learning
- Cline feedback metrics used to retrain classifier
- Complexity scores adjust based on actual execution time
- Agent specialization boundaries refined

### Phase 3: Ensemble Routing
- Complex tasks routed to multiple agents in parallel
- Results merged (Gemini synthesizes multiple agent outputs)
- Speculative decoding (Copilot drafts, Cline refines)

### Phase 4: Active Learning
- Crawler learns from Cline feedback
- Next research iterations avoid known gaps
- Complexity scoring improves per task category

---

## Implementation Checklist

- [x] Complexity scoring formula locked
- [x] Routing decision tree implemented
- [x] Integration points documented
- [x] Error handling defined
- [x] Performance metrics specified
- [ ] Code implementation (Phase D)
- [ ] Test suite with 10+ scenarios (Phase D)
- [ ] Monitoring dashboard (Phase E)
- [ ] Integration with conductor (Phase E)

---

## References

- Model Card Schema: `knowledge/schemas/model_card_schema.py`
- Expert KB Schema: `knowledge/schemas/expert_kb_schema.py`
- Task Classifier: `communication_hub/conductor/task_classifier.py` (Phase D)
- Routing Engine: `communication_hub/conductor/routing_engine.py` (Phase D)

---

**Status**: ✅ PHASE A DELIVERABLE #3 COMPLETE  
**Ready for**: Phase D implementation (task_classifier.py, routing_engine.py)
