# 🎯 STRATEGIC BLUEPRINT: Agent Bus & CLI Agent Hardening

> **Created**: 2026-02-23
> **Owner**: MC-Overseer Agent
> **Status**: 🔵 ACTIVE - Wave 4 Foundation
> **Coordination Key**: `CLI-HARDENING-WAVE-4-2026-02-23`

---

## 📋 Executive Summary

This blueprint addresses the comprehensive hardening of XNAi Foundation's multi-CLI agent dispatch system, account usage tracking, and strategic model utilization. It synthesizes findings from the double OpenCode CLI dispatch and establishes protocols for maximum efficiency across all free-tier AI resources.

---

## 1️⃣ DOUBLE OPENCODE CLI DISPATCH ANALYSIS

### 1.1 What Happened

Two OpenCode CLI instances were dispatched in parallel:

| Dispatch ID | Model | Task | Status |
|-------------|-------|------|--------|
| CLI-20260223-001 | glm-5-free | API Endpoint Tests | Completed |
| CLI-20260223-002 | minimax-m2.5-free | Edge Case Tests | Completed |

### 1.2 Key Learnings

| Learning | Implication | Action |
|----------|-------------|--------|
| **Parallel dispatch works** | Multiple instances can run simultaneously | Scale to 4+ instances |
| **No collision detected** | File writes were coordinated | Add explicit file locking |
| **Memory bank coordination** | Both read same context files | Add read timestamps |
| **Output capture incomplete** | Logs not fully captured | Improve logging protocol |
| **No usage tracking** | Token usage not recorded | Add telemetry (local) |

### 1.3 Metrics Framework to Track

```yaml
dispatch_metrics:
  pre_dispatch:
    - dispatch_id: "CLI-YYYYMMDD-HHMMSS-NN"
    - model: "model-id"
    - task_type: "implementation|research|review"
    - priority: "P0|P1|P2|P3"
    - input_tokens: 0
    - files_to_read: []
    
  during_dispatch:
    - start_time: "ISO8601"
    - files_read: []
    - files_modified: []
    - tools_used: []
    - checkpoint_times: []
    
  post_dispatch:
    - end_time: "ISO8601"
    - duration_seconds: 0
    - output_tokens: 0
    - total_tokens: 0
    - success: true|false
    - deliverables: []
    - errors: []
```

---

## 2️⃣ ACCOUNT USAGE TRACKING SYSTEM

### 2.1 GitHub Copilot (8 Accounts × 50 Messages = 400 Total)

```yaml
copilot_accounts:
  account_pool:
    - id: "copilot-01"
      email: "[account-1-email]"
      messages_used: 0
      messages_limit: 50
      completions_used: 0
      completions_limit: 2000
      reset_date: "monthly"
      models_preferred: ["raptor-mini", "claude-haiku-4.5"]
      
    - id: "copilot-02"
      email: "[account-2-email]"
      messages_used: 0
      messages_limit: 50
      # ... repeat for 8 accounts
      
  rotation_strategy:
    method: "lowest-usage-first"
    auto_switch: true
    warning_threshold: 45  # Switch when 45/50 used
    exhaustion_action: "rotate-to-next"
    
  usage_tracking:
    file: "memory_bank/usage/copilot-usage.json"
    update_frequency: "per-message"
    dashboard_display: true
```

### 2.2 Antigravity Account (Free Tier Weekly Limits)

```yaml
antigravity_accounts:
  account_pool:
    - id: "antigravity-01"
      status: "active"
      weekly_tokens_used: 0
      weekly_token_limit: 500000  # Estimated
      reset_day: "sunday"
      models_available:
        - "claude-opus-4.6-thinking"
        - "claude-sonnet-4.6-antigravity"
        - "gemini-3.1-pro"
        - "deepseek-v3"
        - "deepseek-v1"
        - "gpt-4.1"
        - "o3-mini"
      current_model: "claude-sonnet-4.6-antigravity"
      
  rotation_strategy:
    method: "limit-based-rotation"
    auto_switch: true
    warning_threshold: 0.9  # 90% of limit
    exhaustion_action: "rotate-to-next-account"
    
  token_optimization:
    - use_compact_prompts: true
    - batch_similar_tasks: true
    - prefer_smaller_models_for_simple_tasks: true
    - use_thinking_models_strategically: true
```

### 2.3 Usage Dashboard Specification

```yaml
dashboard:
  location: "memory_bank/usage/DASHBOARD.md"
  auto_update: true
  update_interval: "per-session"
  
  sections:
    - name: "Account Overview"
      type: "table"
      columns: ["Account", "Type", "Used", "Limit", "%", "Status"]
      
    - name: "Copilot Pool"
      type: "grid"
      accounts: 8
      display: ["messages", "completions", "reset_date"]
      
    - name: "Antigravity Pool"  
      type: "progress-bars"
      accounts: 8
      display: ["tokens", "model_access", "reset_day"]
      
    - name: "Model Recommendations"
      type: "cards"
      content: "current best model for task type"
      
    - name: "Usage Trends"
      type: "chart"
      data: "last-7-days"
      
  cli_access:
    command: "xnai-usage"
    output: "json|markdown|table"
```

---

## 3️⃣ STRATEGIC MODEL UTILIZATION PROTOCOLS

### 3.1 Model Assignment Matrix

| Task Type | Primary Model | Fallback | Rationale |
|-----------|--------------|----------|-----------|
| **Deep Reasoning** | Opus 4.6 Thinking | Gemini 3.1 Pro | Best for complex analysis |
| **Code Generation** | Claude Sonnet 4.6 | DeepSeek v3 | Balance of speed/quality |
| **Quick Tasks** | Raptor Mini | Haiku 4.5 | Preserve message limits |
| **Large Context** | Gemini 3.1 Pro | DeepSeek v3 | 1M+ context window |
| **Research** | DeepSeek v3 | Gemini 3.1 Pro | Cost-effective depth |
| **Architecture** | Opus 4.6 Thinking | Sonnet 4.6 | Complex reasoning |
| **Testing** | Haiku 4.5 | Raptor Mini | Fast iteration |
| **Documentation** | Sonnet 4.6 | Gemini 3.1 Flash | Quality writing |

### 3.2 Message Budget Strategy (Copilot 50/month)

```yaml
message_budget:
  allocation:
    deep_reasoning: 10  # 20% - Use sparingly
    code_generation: 15  # 30% - Primary use
    quick_tasks: 10     # 20% - Daily operations
    research: 10        # 20% - Learning
    reserved: 5         # 10% - Emergency/buffer
    
  conservation_tactics:
    - batch_similar_questions: true
    - use_context_efficiently: true
    - prefer_code_completions_over_chat: true
    - save_complex_tasks_for_antigravity: true
```

### 3.3 Token Optimization Strategies

```yaml
token_optimization:
  prompt_engineering:
    - use_bullet_points: true
    - avoid_redundancy: true
    - reference_files_not_paste: true
    - use_templates: true
    
  context_management:
    - compact_old_context: true
    - use_memory_bank: true
    - archive_completed_tasks: true
    
  model_selection:
    simple_tasks: "haiku|raptor-mini"
    medium_tasks: "sonnet|gemini-flash"
    complex_tasks: "opus-thinking|deepseek-v3"
```

---

## 4️⃣ CLI DISPATCH PROTOCOLS (HARDENED)

### 4.1 Pre-Dispatch Checklist

```markdown
- [ ] Read coordination key document
- [ ] Verify model availability in current account
- [ ] Check usage limits (warn if >80%)
- [ ] Assign unique dispatch ID
- [ ] Create dispatch log file
- [ ] Publish to Agent Bus
- [ ] Execute with timeout
- [ ] Capture output to log
- [ ] Update memory bank
- [ ] Record usage metrics
```

### 4.2 Template: Agent Dispatch Prompt

```markdown
You are [AGENT-ID] (did:xnai:[agent-id]).

## Identity
- Agent ID: did:xnai:[agent-id]
- CLI: [CLI-NAME]
- Model: [MODEL-ID]
- Session: [DISPATCH-ID]

## Coordination Key
Search for: [COORDINATION-KEY]

## Account Status
- Account: [ACCOUNT-ID]
- Messages Remaining: [X]/50
- Conserve messages: [true/false]

## Your Assigned Tasks
[TASK LIST]

## Special Instructions
1. **Read Context First**: Read memory_bank/activeContext.md
2. **Conserve Tokens**: Be efficient with prompts
3. **Report Progress**: Publish to xnai:agent_bus
4. **Update Memory Bank**: After completion
5. **Usage Reporting**: Log token usage

## Deliverables
[EXPECTED OUTPUT FILES]

## Success Criteria
[MEASURABLE OUTCOMES]

## Timeout
[X] minutes maximum.
```

### 4.3 Special Instructions by CLI Type

#### OpenCode CLI
```yaml
instructions:
  - Use `opencode run -m MODEL "prompt"` for dispatch
  - JSON output available via --format json
  - Supports multiple models via -m flag
  - Can attach to running server for efficiency
```

#### Copilot CLI
```yaml
instructions:
  - Use `copilot -p "prompt" --model MODEL`
  - 50 messages/month budget - CONSERVE
  - Prefer completions over chat
  - Track usage after each message
```

#### Gemini CLI
```yaml
instructions:
  - Use `gemini --prompt "prompt"`
  - 1M context - use for large tasks
  - Free tier generous - good for research
  - Cold start latency - allow 45-60s
```

#### Cline CLI
```yaml
instructions:
  - Use `cline -y --timeout 600 "prompt"`
  - Requires interactive auth first
  - Supports multiple providers
  - Good for CI/CD integration
```

---

## 5️⃣ XOE-NOVAI SOVEREIGNTY PHILOSOPHY

### 5.1 Core Principles

```yaml
sovereignty_manifesto:
  mission: |
    Build an advanced local RAG system that offers total offline sovereignty
    on a mid-grade computer that rivals paid cloud solutions.
    
  values:
    - Zero external telemetry (air-gap capable)
    - Complete data ownership
    - Graceful degradation (works offline)
    - Community-first (open source)
    - Accessible (mid-grade hardware)
    
  philosophy: |
    Use free cloud tools to build the ultimate local solution.
    Give back to the community that made this possible.
    Document the journey for others to follow.
```

### 5.2 Origin Story (For Documentation)

```yaml
origin_story:
  title: "Building XNAi Foundation: A Non-Programmer's Journey"
  
  narrative: |
    I began this project to fill a gap in the local AI community - 
    an advanced local RAG system that offers total offline sovereignty
    on a mid-grade computer that rivals paid cloud solutions.
    
    As a non-programmer, I used free AI tools to build this:
    - OpenCode CLI (free models)
    - GitHub Copilot (free tier)
    - Grok.com (free access)
    - Gemini CLI (generous free tier)
    
    This entire project was built at zero cost using:
    - Free cloud AI tools for development
    - Open source libraries
    - Community knowledge
    
    The goal: Give back to the community that made this possible.
    
  documentation_targets:
    - articles: "Medium, Dev.to, Substack"
    - videos: "YouTube tutorials"
    - talks: "Local AI meetups"
    - papers: "ArXiv (optional)"
```

---

## 6️⃣ IMPLEMENTATION ROADMAP

### Phase 1: Usage Tracking (Week 1)

| Task | Priority | Deliverable |
|------|----------|-------------|
| Create usage directory | P0 | `memory_bank/usage/` |
| Copilot usage tracker | P0 | `copilot-usage.json` |
| Antigravity usage tracker | P0 | `antigravity-usage.json` |
| Dashboard markdown | P1 | `DASHBOARD.md` |

### Phase 2: Protocol Hardening (Week 1-2)

| Task | Priority | Deliverable |
|------|----------|-------------|
| Update dispatch templates | P0 | `CLI-DISPATCH-PROTOCOLS.md` v2 |
| Add usage logging | P1 | Usage tracking in dispatch |
| Create model selection CLI | P1 | `xnai-select-model` script |

### Phase 3: Dashboard & Automation (Week 2-3)

| Task | Priority | Deliverable |
|------|----------|-------------|
| Build usage dashboard | P1 | Auto-updating dashboard |
| Account rotation logic | P1 | Automatic rotation script |
| Alert system | P2 | Warning at 80% usage |

### Phase 4: Documentation & Origin Story (Week 3-4)

| Task | Priority | Deliverable |
|------|----------|-------------|
| Document origin story | P2 | `ORIGIN-STORY.md` |
| Create article outline | P2 | Article draft |
| Video script | P3 | YouTube outline |

---

## 7️⃣ FILES TO CREATE

| File | Purpose | Status |
|------|---------|--------|
| `memory_bank/usage/copilot-usage.json` | Track Copilot accounts | ⏳ TODO |
| `memory_bank/usage/antigravity-usage.json` | Track Antigravity | ⏳ TODO |
| `memory_bank/usage/DASHBOARD.md` | Usage dashboard | ⏳ TODO |
| `memory_bank/usage/DISPATCH-LOG.json` | Dispatch history | ⏳ TODO |
| `memory_bank/recall/ORIGIN-STORY.md` | Journey documentation | ⏳ TODO |
| `scripts/xnai-usage` | CLI usage tool | ⏳ TODO |
| `scripts/xnai-rotate-account` | Account rotation | ⏳ TODO |

---

## 8️⃣ SUCCESS METRICS

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| Copilot message efficiency | Unknown | >90% useful | Track outcomes |
| Account rotation | Manual | Automatic | Script |
| Token usage visibility | 0% | 100% | Dashboard |
| Dispatch success rate | ~95% | >98% | Log analysis |
| Protocol compliance | Partial | 100% | Checklist |

---

## 🔗 RELATED DOCUMENTS

- `memory_bank/strategies/CLI-DISPATCH-PROTOCOLS.md`
- `expert-knowledge/research/CLI-OPTIONS-ONLINE-2026-02-23.md`
- `expert-knowledge/model-reference/copilot-cli-models-v1.0.0.md`
- `configs/cli-shared-config.yaml`

---

**Created**: 2026-02-23
**Owner**: MC-Overseer Agent
**Coordination Key**: `CLI-HARDENING-WAVE-4-2026-02-23`
**Status**: 🔵 ACTIVE - Ready for Implementation
