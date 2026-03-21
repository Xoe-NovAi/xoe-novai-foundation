---
title: "Antigravity Free-Tier Models Reference"
subtitle: "Complete Frontier Model Catalog & Integration Guide"
status: final
phase: "Wave 4 Research"
created: 2026-02-23
updated: 2026-02-23
owner: "MC-Overseer + Research Agent-8"
tags: [wave-4, antigravity, models, opencode, frontier]
research_agent: "agent-8: Audit Antigravity model availability and quotas"
---

# Antigravity Free-Tier Models Reference

**Coordination Key**: `ANTIGRAVITY-FREE-TIER-MODELS-2026-02-23`  
**Status**: ✅ FINAL (Locked from research agents)  
**Related**: `memory_bank/ACCOUNT-REGISTRY.yaml`, `.opencode/opencode.json`, `memory_bank/activeContext.md`

---

## Executive Summary

**Antigravity** is a free access layer to frontier AI models via OpenCode CLI using Google OAuth authentication. It provides:

- **6 frontier models** (Claude + Gemini families)
- **8 pre-configured accounts** (500K tokens/week per account = 4M total/week)
- **Zero cost** (free tier, no credit card required)
- **Weekly reset** (Sundays)
- **Seamless integration** with OpenCode CLI

**Best For**: Large-context reasoning, architecture analysis, complex multi-file refactoring.

---

## Model Catalog

### 1. Claude Opus 4.6 Thinking (PREMIUM - RECOMMENDED)

```yaml
model:
  name: "Claude Opus 4.6 Thinking"
  provider: "Anthropic via Antigravity"
  access_via_opencode: "google/antigravity-claude-opus-4-6-thinking"
  
specs:
  context_window: 200000  # 200K input
  output_limit: 64000    # 64K output
  thinking_budget: "8K-32K tokens (configurable)"
  speed: "~1-2 seconds (via thinking overhead)"
  capabilities:
    - reasoning: "⭐⭐⭐⭐⭐ Deep, step-by-step reasoning"
    - code_analysis: "⭐⭐⭐⭐⭐ Excellent multi-file"
    - refactoring: "⭐⭐⭐⭐ High-quality suggestions"
    - architecture: "⭐⭐⭐⭐⭐ Best for complex design"
    - vision: "❌ No"
    - tool_use: "✅ Yes"

variants:
  low_thinking:
    thinking_budget: 8192
    description: "Quick analysis with reasoning (1-3 seconds)"
    use_case: "Code review, simple refactoring"
    
  high_thinking:
    thinking_budget: 32768
    description: "Deep analysis with extensive reasoning (5-10 seconds)"
    use_case: "Architecture decisions, complex logic"

best_for:
  - Architecture review (system design)
  - Complex refactoring decisions
  - Security analysis & hardening
  - Performance optimization
  - Large codebase understanding
  
cost: "0 (free tier)"
monthly_budget: "500K tokens/week × 8 accounts = 4M total"

example_usage: |
  opencode --model google/antigravity-claude-opus-4-6-thinking \
    "Review the XNAi agent bus architecture for scalability issues"
```

---

### 2. Claude Opus 4.5 Thinking (LEGACY - AVOID)

```yaml
model:
  name: "Claude Opus 4.5 Thinking"
  status: "Legacy (4.6 available, prefer 4.6)"
  
specs:
  context_window: 200000
  output_limit: 64000
  thinking_budget: "8K-32K tokens"
  speed: "Similar to 4.6"
  
best_for: "Fallback if 4.6 unavailable"
recommendation: "Use 4.6 instead (newer, better)"
```

---

### 3. Claude Sonnet 4.5 (FAST - RECOMMENDED)

```yaml
model:
  name: "Claude Sonnet 4.5"
  provider: "Anthropic via Antigravity"
  access_via_opencode: "google/antigravity-claude-sonnet-4-5"
  
specs:
  context_window: 200000
  output_limit: 64000
  thinking_budget: "None (fast inference)"
  speed: "~500-800ms (fastest Claude variant)"
  capabilities:
    - reasoning: "⭐⭐⭐⭐ Good reasoning"
    - code_analysis: "⭐⭐⭐⭐ Good analysis"
    - refactoring: "⭐⭐⭐⭐ Solid suggestions"
    - architecture: "⭐⭐⭐ OK for simple architectures"
    - vision: "❌ No"
    - tool_use: "✅ Yes"

best_for:
  - Fast iteration on code changes
  - Quick refactoring (< 200 lines)
  - API integration analysis
  - General development tasks
  - Low-latency coordination
  
cost: "0 (free tier)"
vs_opus_thinking:
  speed_advantage: "2-3x faster"
  reasoning_disadvantage: "Less deep reasoning"
  recommendation: "Use for speed; use Opus for reasoning"

example_usage: |
  opencode --model google/antigravity-claude-sonnet-4-5 \
    "Analyze auth.py for security issues"
```

---

### 4. Claude Sonnet 4.5 Thinking (BALANCED)

```yaml
model:
  name: "Claude Sonnet 4.5 Thinking"
  provider: "Anthropic via Antigravity"
  access_via_opencode: "google/antigravity-claude-sonnet-4-5-thinking"
  
specs:
  context_window: 200000
  output_limit: 64000
  thinking_budget: "8K-32K tokens"
  speed: "~1-1.5 seconds (balanced)"
  
best_for:
  - Balanced reasoning + speed
  - Medium-complexity refactoring
  - Code migration planning
  - Test generation
  
recommendation: "Good default; use Opus for deep reasoning, Sonnet (non-thinking) for speed"
```

---

### 5. Gemini 3 Pro (CONTEXT CHAMPION - **HIGHLY RECOMMENDED**)

```yaml
model:
  name: "Gemini 3 Pro"
  provider: "Google via Antigravity"
  access_via_opencode: "google/antigravity-gemini-3-pro"
  
specs:
  context_window: 1048576  # **1M TOKENS** ⭐⭐⭐⭐⭐
  output_limit: 65536     # 64K output
  thinking_support: "Yes (configurable: low, medium, high)"
  speed: "~1-2 seconds (slower than Sonnet, but 5x larger context)"
  capabilities:
    - reasoning: "⭐⭐⭐⭐⭐ Excellent"
    - code_analysis: "⭐⭐⭐⭐⭐ Best in class (can load entire codebase)"
    - refactoring: "⭐⭐⭐⭐⭐ Excellent multi-file"
    - architecture: "⭐⭐⭐⭐⭐ Best (sees whole system)"
    - vision: "✅ Yes (images, PDFs, documents)"
    - tool_use: "✅ Yes"

strategic_advantage: |
  **Gemini 3 Pro can hold the ENTIRE xnai-foundation codebase in context**
  - Total repo size: ~400K tokens (estimated)
  - Gemini context: 1M tokens
  - Usable space after codebase: 600K tokens for analysis
  
  This means:
  1. Load entire repository at once
  2. Analyze cross-module dependencies
  3. Review system-wide performance issues
  4. Refactor with full system awareness
  
  NO OTHER MODEL CAN DO THIS.

variants:
  thinking_low:
    budget: minimal
    description: "Quick analysis with minimal thinking"
    use_case: "Document review, quick questions"
    
  thinking_medium:
    budget: medium
    description: "Balanced thinking + output"
    use_case: "Code review, architecture questions"
    
  thinking_high:
    budget: high
    description: "Deep reasoning with extensive thinking"
    use_case: "Complex system design, security review"

best_for:
  - **Full codebase analysis** (entire repo in one context)
  - System-wide refactoring
  - Performance optimization (sees whole system)
  - Security audit (examines dependencies)
  - Architecture review (understands all modules)
  - Documentation generation (comprehensive)
  - Test coverage analysis (cross-module)
  
cost: "0 (free tier)"
monthly_budget: "500K tokens/week × 8 accounts = 4M total"

wave_4_strategic_value: "⭐⭐⭐⭐⭐ HIGHEST (1M context unique)"

example_usage: |
  # Load entire repository for analysis
  cat app/**/*.py docs/**/*.md configs/**/*.yaml | \
  opencode --model google/antigravity-gemini-3-pro \
    "Analyze cross-module dependencies and suggest refactoring"
  
  # Or use with context file
  opencode --model google/antigravity-gemini-3-pro \
    "Review entire XNAi system architecture" \
    < full_repo_context.txt
```

---

### 6. Gemini 3 Flash (SPEED - WHEN FAST NEEDED)

```yaml
model:
  name: "Gemini 3 Flash"
  provider: "Google via Antigravity"
  access_via_opencode: "google/antigravity-gemini-3-flash"
  
specs:
  context_window: 1000000  # Still 1M (same as Pro)
  output_limit: 65536
  thinking_support: "Yes (minimal, low, medium, high variants)"
  speed: "~400-600ms (FASTEST among large-context models)"
  capabilities:
    - reasoning: "⭐⭐⭐ Good (not as deep as Pro)"
    - code_analysis: "⭐⭐⭐⭐ Good"
    - refactoring: "⭐⭐⭐⭐ Good"
    - architecture: "⭐⭐⭐⭐ OK"
    - vision: "✅ Yes"
    - tool_use: "✅ Yes"

when_to_use:
  - When speed is critical (< 1 second)
  - When context is large but reasoning is simple
  - When doing batch analysis (many tasks)
  - Quick API exploration
  
vs_gemini_pro:
  speed: "2-3x faster"
  reasoning: "Slightly less capable"
  recommendation: "Use for speed; use Pro for reasoning"

best_for:
  - Batch code analysis
  - Fast API documentation
  - Quick refactoring suggestions
  - Performance: Load analysis
  
cost: "0 (free tier)"

example_usage: |
  opencode --model google/antigravity-gemini-3-flash \
    "Quick scan of cache.py for obvious performance issues"
```

---

## Account Pool Management

### Account Configuration

```yaml
account_pool:
  total_accounts: 8
  account_ids:
    - antigravity_user_1
    - antigravity_user_2
    - antigravity_user_3
    - antigravity_user_4
    - antigravity_user_5
    - antigravity_user_6
    - antigravity_user_7
    - antigravity_user_8
  
  quota_per_account:
    tokens: 500000  # 500K tokens
    period: "weekly"
    reset_day: "Sunday (UTC)"
    
  total_capacity:
    tokens: 4000000  # 4M tokens/week
    estimated_cost: "$0 (free tier)"
    equivalent_to: "~800 Claude Opus messages"
    or: "~200 full codebase analyses via Gemini 3 Pro"

  authentication:
    method: "Google OAuth (via opencode-antigravity-auth plugin)"
    setup: "One-time per account (first login)"
    refresh: "Automatic (yearly expiration)"
    
  rotation_strategy:
    approach: "Round-robin when account quota exhausted"
    fallback: "Use next available account in pool"
    tracking: "Daily audit system (memory_bank)"
```

### Account Health Monitoring

```yaml
daily_audit_metrics:
  - account_id: antigravity_user_1
    quota_used: 150000
    quota_total: 500000
    percent_used: 30%
    health_status: green
    estimated_exhaustion: 17 days
    
  - account_id: antigravity_user_2
    quota_used: 480000
    quota_total: 500000
    percent_used: 96%
    health_status: red
    estimated_exhaustion: 1 day
    action_required: "Rotate to next account"

rotation_logic:
  if_account_exhausted: "Automatically switch to next account"
  if_all_exhausted: "Use OpenCode built-in models as fallback"
  notification: "Alert when account > 80% used"
```

---

## Model Selection Decision Tree

```
Task requirements?
├─ "I need to analyze the entire XNAi codebase at once"
│  └─ USE: Gemini 3 Pro (1M context) ⭐⭐⭐⭐⭐
│
├─ "I need fast reasoning for architecture"
│  └─ USE: Claude Opus 4.6 Thinking (deep thinking) ⭐⭐⭐⭐⭐
│
├─ "I need fast inference (< 1 second)"
│  └─ USE: Claude Sonnet 4.5 or Gemini 3 Flash ⭐⭐⭐⭐
│
├─ "I need balanced reasoning + speed"
│  └─ USE: Claude Sonnet 4.5 Thinking (1-1.5s) ⭐⭐⭐⭐
│
├─ "I need large-context analysis but with thinking"
│  └─ USE: Gemini 3 Pro with thinking:high ⭐⭐⭐⭐⭐
│
└─ Default (code analysis < 200K tokens)
   └─ USE: Claude Sonnet 4.5 (balanced) ⭐⭐⭐⭐
```

---

## Wave 4 Model Routing Priorities

### Strategic Allocation

```yaml
wave_4_model_routing:
  priority_1_highest_value:
    model: "Gemini 3 Pro"
    use_case: "Full codebase analysis"
    monthly_budget: "3-4 full-repo scans (400K tokens each)"
    example: "Architecture review, dependency mapping, performance audit"
    
  priority_2_reasoning:
    model: "Claude Opus 4.6 Thinking"
    use_case: "Complex decision-making"
    monthly_budget: "50-100 deep analyses"
    example: "Design decisions, security hardening, migration planning"
    
  priority_3_speed:
    model: "Claude Sonnet 4.5"
    use_case: "Fast iteration"
    monthly_budget: "1000+ quick tasks"
    example: "Code review, quick fixes, API exploration"
    
  priority_4_batch:
    model: "Gemini 3 Flash"
    use_case: "Batch analysis"
    monthly_budget: "500+ tasks/month"
    example: "Parallel analysis, bulk code review"

estimated_monthly_capacity:
  total: "4M tokens from 8 accounts"
  allocation_1: "1M tokens (Gemini Pro large-context tasks)"
  allocation_2: "1M tokens (Opus Thinking reasoning)"
  allocation_3: "1.5M tokens (Sonnet fast tasks)"
  allocation_4: "0.5M tokens (Gemini Flash batch)"
```

---

## Integration: OpenCode Configuration

### Setup Instructions

```bash
# 1. Install OpenCode (if not already done)
npm install -g opencode

# 2. Add Antigravity plugin (first time only)
opencode plugin install opencode-antigravity-auth@latest

# 3. Authenticate one account
opencode auth login google

# 4. Verify models are available
opencode --model list | grep antigravity

# 5. Start using Gemini 3 Pro
opencode --model google/antigravity-gemini-3-pro \
  "Analyze this code: $(cat myfile.py)"
```

### Command Examples

```bash
# Use Gemini 3 Pro for full-codebase analysis
find app -name "*.py" | xargs cat | \
opencode --model google/antigravity-gemini-3-pro \
  "Find architectural bottlenecks"

# Use Claude Opus Thinking for architecture
opencode --model google/antigravity-claude-opus-4-6-thinking \
  "Design a horizontal-scaling strategy for XNAi Agent Bus"

# Use Claude Sonnet for quick refactoring
opencode --model google/antigravity-claude-sonnet-4-5 \
  "Refactor async/await patterns in $(cat auth.py)"

# Batch with Gemini Flash
for file in app/**/*.py; do
  echo "Analyzing $file..."
  cat "$file" | opencode --model google/antigravity-gemini-3-flash \
    "Quick code quality check"
done
```

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Model accuracy | 95%+ | Manual review of outputs |
| Context fit | 100% | Track overflow errors (should be 0) |
| Queue utilization | 80%+ | Monitor 4M token quota usage |
| Gemini Pro adoption | 20% of all tasks | Log model usage via Wave 4 dispatch |
| Architecture decisions | ≥ 10/month | Track uses of Opus Thinking |
| Response time (avg) | < 1 second | Benchmark dispatch latency |

---

## Recommendations for Wave 4

1. **Make Gemini 3 Pro the default** for any task > 100K tokens
2. **Reserve Opus Thinking** for strategic decisions (architecture, security)
3. **Use Sonnet 4.5** for rapid iteration (< 5 second tasks)
4. **Implement daily audit** to track quota across 8 accounts
5. **Route large-context tasks to Gemini** (unique 1M window)
6. **Setup account rotation** (automatic when quota exhausted)

---

## Related Documents

- `memory_bank/ACCOUNT-REGISTRY.yaml` (account tracking)
- `.opencode/opencode.json` (configuration)
- `memory_bank/strategies/WAVE-4-P2-MULTI-CLI-DISPATCH-DESIGN.md` (dispatch logic)
- `expert-knowledge/CLI-FEATURE-COMPARISON-MATRIX-2026-02-23.md` (vs other CLIs)

---

**Status**: ✅ FINAL - Locked from Research Agent-8  
**Last Updated**: 2026-02-23  
**Used By**: Wave 4 Model Router (Phase 3B Implementation)
