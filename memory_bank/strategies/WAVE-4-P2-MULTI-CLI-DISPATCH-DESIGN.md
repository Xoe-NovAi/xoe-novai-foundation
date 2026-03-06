---
title: "Wave 4 Phase 2: Multi-Instance CLI Dispatch Protocol Design"
subtitle: "OpenCode, Copilot, Cline, and Local Orchestration Strategy"
status: draft
phase: "Wave 4 - Phase 2 Design"
created: 2026-02-23
updated: 2026-02-23
owner: "MC-Overseer"
tags: [wave-4, multi-cli, dispatch, orchestration]
---

# Wave 4 Phase 2: Multi-Instance CLI Dispatch Protocol Design

**Coordination Key**: `WAVE-4-P2-MULTI-CLI-DISPATCH-DESIGN`  
**Related**: `memory_bank/strategies/WAVE-4-PHASE-1-STATUS-REPORT.md`, `memory_bank/activeContext.md`

---

## Problem Statement

XNAi Foundation now has access to multiple CLI tools (OpenCode, Copilot, Cline) with:
- 8+ Antigravity accounts (1M context, frontier models)
- 8+ Copilot accounts (50 messages + 2K code completions)
- Cline CLI (MCP integration, file operations)
- Local llama-cpp (sovereign fallback)

**Challenge**: How to dispatch tasks intelligently to maximize throughput and minimize rate-limiting?

**Goal**: Design a dispatcher that:
1. Routes tasks to the most optimal CLI for that task type
2. Load-balances across multiple accounts
3. Handles quota limits gracefully
4. Integrates with Agent Bus
5. Supports multi-instance parallelization

---

## Analysis: CLI Capability Matrix

| Capability | OpenCode | Copilot | Cline | Local |
|------------|----------|---------|-------|-------|
| **Context Window** | 1M (Gemini 3) | 264K (Raptor Mini) | 200K | ~4K-8K |
| **Models Available** | 10+  | 4 (Raptor, Haiku, GPT, others) | 3-5 | 1-2 |
| **Speed** | Fast | Very Fast (free tier) | Medium | Slow (CPU-bound) |
| **Tool Use** | ✅ Yes | ⚠️ Limited | ✅ Yes | ⚠️ Limited |
| **File Operations** | Limited | ✅ Yes | ✅✅ Yes | ✅ Yes |
| **Multi-File Support** | ✅ Yes | ✅ Yes | ✅✅ Yes | Limited |
| **Batch Mode** | ⚠️ Partial | ✅ Yes | ✅ Yes | ✅ Yes |
| **Parallel Instances** | ✅ Yes (multiple accounts) | ✅ Yes (multiple accounts) | ⚠️ TBD | ✅ Yes |
| **Headless Mode** | ⚠️ Research | ✅ `gh copilot` | ✅ CLI flags | ✅ Yes |
| **Quota/Month** | Unlimited (free tier) | 50 messages × 8 = 400 | Unlimited | Unlimited |
| **Best For** | Large context, reasoning | Code completion, speed | Refactoring, MCP tasks | Sovereign, sensitive |

---

## Proposed Dispatch Strategy

### Tier 1: Task Classification

When a task arrives, classify it by:

```
Task Type Classification:
├─ REASONING (large context, complex logic)
│   └─ Route to: OpenCode (Gemini 3 Pro - 1M context)
│
├─ CODE_COMPLETION (inline suggestions, auto-fix)
│   └─ Route to: Copilot (Raptor Mini - free tier, 2K/month)
│
├─ REFACTORING (multi-file, structural changes)
│   └─ Route to: Cline (MCP integration, file I/O)
│
├─ SOVEREIGN (sensitive, local-only)
│   └─ Route to: Local llama-cpp (no external calls)
│
├─ BATCH (parallel, embarrassingly parallel)
│   └─ Route to: OpenCode (multi-instance, 8 accounts)
│
└─ FALLBACK (quota exhausted, fast needed)
    └─ Route to: Next available in tier stack
```

### Tier 2: Load-Balancing Algorithm

```python
class DispatchDecision:
    def __init__(self, task):
        self.task = task
        self.candidates = []  # List of suitable CLIs
        self.selected_cli = None
        
    def get_quota_score(self, cli_name, account_idx=0):
        """
        Score: 0-100 (100 = unlimited quota, 0 = exhausted)
        """
        quota_data = account_registry.get_quota(cli_name, account_idx)
        used_percent = quota_data['used'] / quota_data['total']
        return max(0, 100 - (used_percent * 100))
    
    def get_latency_score(self, cli_name):
        """
        Score: 0-100 (100 = fastest, 0 = slowest)
        Benchmark latencies (ms):
        - Copilot: ~200ms (local, direct API)
        - OpenCode: ~800ms (via Zen proxy)
        - Cline: ~1000ms (file I/O overhead)
        - Local: ~2000ms (CPU-bound, model load)
        """
        latency_map = {
            'copilot': 200,
            'opencode': 800,
            'cline': 1000,
            'local': 2000,
        }
        base_latency = latency_map.get(cli_name, 1000)
        return max(0, 100 - (base_latency / 20))  # Normalize 0-100
    
    def get_context_fit_score(self, cli_name):
        """
        Score: 0-100 (100 = perfect fit, 0 = too small)
        """
        context_needed = self.task.estimated_tokens
        cli_context = context_limits.get(cli_name)
        
        if context_needed <= cli_context * 0.5:
            return 100  # Underutilized but OK
        elif context_needed <= cli_context * 0.8:
            return 100  # Good fit
        elif context_needed <= cli_context:
            return 75  # Slightly tight
        else:
            return 0  # Won't fit
    
    def calculate_priority_score(self, cli_name, account_idx=0):
        """
        Composite score for dispatch decision
        Weights: quota (40%), latency (30%), context_fit (30%)
        """
        weights = {
            'quota': 0.40,
            'latency': 0.30,
            'context': 0.30,
        }
        
        quota_score = self.get_quota_score(cli_name, account_idx)
        latency_score = self.get_latency_score(cli_name)
        context_score = self.get_context_fit_score(cli_name)
        
        composite = (
            quota_score * weights['quota'] +
            latency_score * weights['latency'] +
            context_score * weights['context']
        )
        
        return composite
    
    def dispatch(self):
        """
        Main dispatch logic:
        1. Classify task
        2. Get candidates by task type
        3. Score each candidate (quota + latency + fit)
        4. Select highest score
        5. If score < threshold, use fallback
        """
        task_type = self.classify_task(self.task)
        self.candidates = self.get_candidates_for_type(task_type)
        
        best_score = -1
        best_cli = None
        best_account = 0
        
        for cli_name in self.candidates:
            if cli_name == 'opencode':
                # For OpenCode, iterate through account pool
                for account_idx in range(8):
                    score = self.calculate_priority_score(cli_name, account_idx)
                    if score > best_score:
                        best_score = score
                        best_cli = cli_name
                        best_account = account_idx
            else:
                # For Copilot, Cline, Local (simpler account handling)
                score = self.calculate_priority_score(cli_name)
                if score > best_score:
                    best_score = score
                    best_cli = cli_name
        
        # Fallback if primary score too low
        if best_score < 40:
            best_cli = 'local'  # Sovereign fallback
        
        self.selected_cli = best_cli
        self.selected_account = best_account if best_cli == 'opencode' else None
        return self.selected_cli, self.selected_account
```

### Tier 3: Multi-Instance Spawning

For parallelizable tasks (e.g., analyzing 10 files), spawn multiple CLI instances:

```python
class ParallelDispatcher:
    def __init__(self, tasks, max_parallel=3):
        self.tasks = tasks
        self.max_parallel = max_parallel
        self.results = {}
    
    def dispatch_batch(self):
        """
        For batch of N tasks:
        1. Classify each task
        2. Calculate dispatch scores
        3. Spawn up to max_parallel instances
        4. Rotate CLI/account selection to avoid quota spikes
        """
        # Group tasks by type
        by_type = self._group_by_type(self.tasks)
        
        # For each group, spawn parallel instances
        for task_type, task_list in by_type.items():
            dispatchers = [SingleDispatcher(task) for task in task_list]
            assignments = self._assign_dispatchers(dispatchers, task_type)
            
            # Spawn up to max_parallel
            for i, (dispatcher, cli_name, account) in enumerate(assignments):
                if i % self.max_parallel == 0:
                    # Batch N tasks, wait for completion, then next batch
                    self._wait_for_batch()
                
                self._spawn_instance(dispatcher, cli_name, account)
    
    def _assign_dispatchers(self, dispatchers, task_type):
        """
        Round-robin assignment with quota awareness
        Example: 3 OpenCode tasks → assign to accounts 0, 1, 2
        """
        assignments = []
        cli_rotation = self._get_cli_order_for_type(task_type)
        
        for i, dispatcher in enumerate(dispatchers):
            cli_name = cli_rotation[i % len(cli_rotation)]
            
            if cli_name == 'opencode':
                account = i % 8  # Rotate through 8 accounts
            else:
                account = 0
            
            assignments.append((dispatcher, cli_name, account))
        
        return assignments
```

### Tier 4: Integration with Agent Bus

```yaml
# Agent Bus Task Route Configuration
routing:
  # Dispatch decision rules
  decision_rules:
    - task_type: REASONING
      preferred_cli: opencode
      fallback: [copilot, local]
      weight:
        context_required: 0.5
        latency_critical: 0.2
        quota_capacity: 0.3
    
    - task_type: CODE_COMPLETION
      preferred_cli: copilot
      fallback: [cline, local]
      weight:
        context_required: 0.2
        latency_critical: 0.6
        quota_capacity: 0.2
    
    - task_type: REFACTORING
      preferred_cli: cline
      fallback: [opencode, local]
      weight:
        context_required: 0.4
        latency_critical: 0.2
        quota_capacity: 0.4
    
    - task_type: SOVEREIGN
      preferred_cli: local
      fallback: []
      weight:
        context_required: 0.2
        latency_critical: 0.3
        quota_capacity: 0.5
  
  # Quota tracking and rotation
  quota_tracking:
    update_interval: 5m
    alert_threshold: 0.8
    rotation_strategy: least_used
    
  # Account pool management
  account_pools:
    opencode:
      total_accounts: 8
      quota_per_account: unlimited_free_tier
      reset_policy: never
      
    copilot:
      total_accounts: 8
      quota_per_account: "50 messages/month"
      reset_policy: "monthly_2026-03-01"
      
    cline:
      total_accounts: 1
      quota_per_account: unlimited
      reset_policy: never
      
    local:
      total_accounts: 1
      quota_per_account: unlimited
      reset_policy: never
```

---

## Execution Flow

```
Task Arrives at Agent Bus
    ↓
[Dispatch Decision]
  1. Parse task requirements
  2. Classify by type (REASONING, CODE_COMPLETION, REFACTORING, etc.)
  3. Get candidate CLIs
  4. Score each (quota + latency + fit)
  5. Select best + account
    ↓
[Pre-Execution Checks]
  1. Verify CLI is running
  2. Verify account quota available
  3. Load provider credentials
  4. Set up any MCP servers (if Cline)
    ↓
[Execution]
  1. Spawn CLI instance (or use existing)
  2. Send task parameters
  3. Monitor execution
  4. Collect results
    ↓
[Post-Execution]
  1. Update quota tracking
  2. Log execution metrics
  3. Return results to Agent Bus
    ↓
Task Complete
```

---

## Multi-Instance Parallelization Example

**Scenario**: User wants to analyze 10 Python files for code smells

```
Task: AnalyzeCodeSmells(files=[file1..file10])
    ↓
Dispatch Decision:
  - Task Type: REFACTORING
  - Preferred: Cline
  - Batch Size: 10 files
  - Max Parallel: 3 (avoid overload)
    ↓
Spawn Wave 1 (parallel):
  - OpenCode.analyze(files[0:4], account=0)
  - OpenCode.analyze(files[4:7], account=1)
  - Cline.analyze(files[7:10])
    ↓
Wait for Wave 1 completion (~3 seconds)
    ↓
Collect Results → Merge → Return
```

---

## Account Rotation Logic

```python
class AccountRotationManager:
    def __init__(self):
        self.quota_tracking = {}  # {cli_name: [{account_idx: quota_data}]}
        self.last_used = {}  # {cli_name: {account_idx: timestamp}}
    
    def get_next_account(self, cli_name):
        """
        Select next account based on:
        1. Quota availability (prefer < 80% used)
        2. Time since last use (prefer oldest)
        3. Account index (prefer lower, for consistency)
        """
        if cli_name == 'opencode':
            accounts = range(8)
        elif cli_name == 'copilot':
            accounts = range(8)
        else:
            return 0  # Single account
        
        # Filter: accounts with < 80% quota used
        available = [
            acc for acc in accounts
            if self.quota_tracking[cli_name][acc]['used_percent'] < 0.8
        ]
        
        if not available:
            # All accounts over 80% - fallback to least-used
            available = accounts
        
        # Select: oldest last_used
        best_account = min(available, key=lambda acc: self.last_used[cli_name].get(acc, 0))
        
        # Update tracking
        self.last_used[cli_name][best_account] = time.time()
        
        return best_account
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **OpenCode as Tier 1** | 1M context (Gemini 3), unlimited free tier, best for reasoning |
| **Copilot as Tier 2** | Free code completions (2K/month × 8 = 16K), very fast |
| **Cline as Tier 3** | MCP integration, best for file operations and refactoring |
| **Local as Tier 4** | Sovereign fallback, no external dependencies |
| **Round-robin rotation** | Simpler than quota-aware; prevents starvation |
| **40/30/30 scoring** | Quota matters most (avoid limits), latency important (UX), context fit secondary |
| **Max 3 parallel** | Avoid resource exhaustion, keep under rate limits |
| **5-minute quota update** | Balance freshness vs. polling overhead |

---

## Success Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Task dispatch latency | < 200ms | Benchmark dispatch_decision() |
| Quota utilization | 70-90% per account | Track quota_tracking data |
| CLI selection accuracy | 90%+ correct tier | Manual audit of 100 tasks |
| Parallel throughput | 3x single-instance | Compare 3 parallel vs. 1 sequential |
| Fallback triggering | < 5% of tasks | Monitor fallback_count / total_tasks |

---

## Implementation Roadmap

### Phase 2B: Design Review (THIS)
- [x] Task classification matrix
- [x] Load-balancing algorithm
- [x] Multi-instance spawning
- [ ] User feedback

### Phase 3B: Implementation
- [ ] Dispatcher class in Python
- [ ] Account rotation manager
- [ ] Agent Bus integration
- [ ] Quota tracking system

### Phase 4B: Testing & Validation
- [ ] Load test (1000 tasks)
- [ ] Quota accuracy test
- [ ] Fallback behavior test
- [ ] Performance benchmarks

---

## Related Documents

- `memory_bank/ACCOUNT-REGISTRY.yaml` (account metadata)
- `memory_bank/activeContext.md` (current status)
- `WAVE-4-P2-CONFIG-INJECTION-DESIGN.md` (credential injection)
- `expert-knowledge/CLI-FEATURE-COMPARISON-MATRIX-2026-02-23.md` (TBD - from research agents)

---

**Status**: 🔵 DRAFT - Awaiting Research Agent Input  
**Last Updated**: 2026-02-23  
**Next Checkpoint**: Phase 2C (Raptor Integration)
