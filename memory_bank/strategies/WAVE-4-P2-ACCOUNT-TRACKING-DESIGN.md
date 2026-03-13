---
title: "Wave 4 Phase 2: Account Tracking & Daily Audit System Design"
subtitle: "Quota Monitoring, Account Health, and Rotation Strategy"
status: draft
phase: "Wave 4 - Phase 2 Design"
created: 2026-02-23
updated: 2026-02-23
owner: "MC-Overseer"
tags: [wave-4, account-tracking, audit, quota-management]
---

# Wave 4 Phase 2: Account Tracking & Daily Audit System Design

**Coordination Key**: `WAVE-4-P2-ACCOUNT-TRACKING-DESIGN`  
**Related**: `memory_bank/ACCOUNT-REGISTRY.yaml`, `memory_bank/strategies/WAVE-4-PHASE-1-STATUS-REPORT.md`

---

## Executive Summary

**Challenge**: Manage 28+ accounts across 4 providers with varying quota limits, reset schedules, and access patterns.

**Solution**: Automated daily audit system that:
1. Tracks quota usage for all accounts
2. Detects quota exhaustion early
3. Manages account rotation
4. Alerts on anomalies
5. Maintains historical data for trend analysis

**Deliverable**: `memory_bank/ACCOUNT-REGISTRY-TRACKING.yaml` (daily updates) + audit dashboard

---

## Account Portfolio Overview

### Current Accounts

| Provider | Total | Quota Type | Reset Schedule | Status |
|----------|-------|-----------|-----------------|--------|
| **Antigravity** | 8 | Unlimited free tier | Never | ✅ Active (3 original + 5 added) |
| **Copilot** | 8 | 50 msgs/mo + 2K code completions | Monthly (2026-03-01) | ✅ Active |
| **OpenCode Zen** | 1 | Unlimited free tier | Never | ✅ Active |
| **Cline** | 1 | Unlimited | Never | ✅ Active (MCP integration) |
| **Local (llama-cpp)** | 1 | Unlimited | Never | ✅ Active |
| **Reserved/Research** | 8-15 | TBD | TBD | 🔵 Pending (free-tier providers) |
| **Total** | **27-35** | Mixed | Mixed | 🟢 Portfolio active |

### Priority Accounts (Immediate Focus)

```yaml
tier_1_critical:
  antigravity:
    accounts: 8
    value: "Unlimited free tier + frontier models (Opus, Gemini 3)"
    utilization_strategy: "Rotate for continuous throughput"
    
  copilot:
    accounts: 8
    value: "Raptor Mini (264K context) + code completions"
    utilization_strategy: "Reserve Raptor for code analysis; code completions secondary"

tier_2_high_value:
  opencode_zen:
    accounts: 1
    value: "Built-in models + local LLM access"
    utilization_strategy: "Backup for quota exhaustion"
    
  cline:
    accounts: 1
    value: "File operations + MCP integration"
    utilization_strategy: "Route refactoring/file-heavy tasks"

tier_3_future:
  free_tier_providers:
    accounts: "8-15 (TBD)"
    value: "Code completions, inference, specialized models"
    utilization_strategy: "Parallel inference, load balancing"
```

---

## Daily Audit System Architecture

### Tier 1: Data Collection (Automated Daily)

```yaml
# Run every 24 hours (cron: 0 2 * * * = 2 AM UTC)
audit_schedule:
  frequency: "daily"
  time: "02:00 UTC" # Off-peak
  timeout: "15 minutes"
  retry_policy: "exponential backoff up to 3x"

data_collection:
  antigravity:
    method: "API query + opencode.json parsing"
    endpoint: "~/.local/share/opencode/auth.json"
    metrics:
      - last_active_timestamp
      - approximate_usage (inferred from auth token age)
      - model_availability (hardcoded in spec)
      
  copilot:
    method: "gh CLI + GitHub Copilot API"
    command: "gh copilot status" or "gh api user --jq '.copilot_messages_remaining'"
    metrics:
      - messages_used
      - messages_remaining
      - code_completions_used
      - code_completions_remaining
      - reset_date
      
  opencode_zen:
    method: "opencode status" (if available)
    command: "opencode --version && opencode --model list"
    metrics:
      - service_health
      - available_models
      - last_connection_time
      
  cline:
    method: "cline status" or log parsing
    location: "~/.config/cline/logs/"
    metrics:
      - last_activity_timestamp
      - mcp_server_status
      - error_count_24h
      
  local_llm:
    method: "localhost:8080 health check"
    command: "curl http://localhost:8080/health"
    metrics:
      - service_status
      - model_loaded
      - memory_usage
```

### Tier 2: Data Processing & Analysis

```python
class DailyAuditProcessor:
    def __init__(self):
        self.audit_date = datetime.now().date()
        self.findings = {
            'accounts': {},
            'alerts': [],
            'recommendations': [],
            'trends': {}
        }
    
    def process_quota_data(self, provider: str, account_data: dict):
        """
        For each account, calculate:
        1. Remaining quota percentage
        2. Burn rate (tokens/hour or msgs/day)
        3. Days until exhaustion (if burn rate continues)
        4. Health status (green/yellow/red)
        """
        quota_total = account_data['quota_total']
        quota_used = account_data['quota_used']
        quota_remaining = quota_total - quota_used
        used_percent = (quota_used / quota_total) * 100
        
        # Calculate burn rate
        days_elapsed = (datetime.now() - account_data['account_created']).days
        burn_rate_per_day = quota_used / max(days_elapsed, 1)
        days_until_exhaustion = quota_remaining / max(burn_rate_per_day, 1)
        
        # Health status
        if used_percent < 50:
            status = 'green'
        elif used_percent < 80:
            status = 'yellow'
        else:
            status = 'red'
        
        self.findings['accounts'][f"{provider}_{account_id}"] = {
            'provider': provider,
            'account_id': account_id,
            'quota_used_percent': used_percent,
            'remaining_quota': quota_remaining,
            'burn_rate_per_day': burn_rate_per_day,
            'days_until_exhaustion': days_until_exhaustion,
            'health_status': status,
            'audit_timestamp': datetime.now().isoformat(),
        }
        
        # Generate alerts
        if status == 'red':
            self.findings['alerts'].append({
                'severity': 'critical',
                'account': f"{provider}_{account_id}",
                'message': f"Quota exhaustion imminent ({used_percent:.1f}% used)",
                'action_required': 'Rotate to next account or implement fallback'
            })
        elif status == 'yellow' and days_until_exhaustion < 7:
            self.findings['alerts'].append({
                'severity': 'warning',
                'account': f"{provider}_{account_id}",
                'message': f"Quota running low: {days_until_exhaustion:.1f} days remaining",
                'action_required': 'Plan account rotation'
            })
```

### Tier 3: Storage & Reporting

```yaml
# Daily audit output: memory_bank/ACCOUNT-TRACKING-{YYYY-MM-DD}.yaml
account_audit_report:
  audit_date: 2026-02-23
  audit_time: "02:15:30 UTC"
  
  summary:
    total_accounts: 27
    healthy_accounts: 24
    warning_accounts: 2
    critical_accounts: 1
    
  alerts:
    - severity: critical
      account: copilot_dev_3
      message: "Quota exhausted (50/50 messages used)"
      action: "Rotate to copilot_dev_4"
      
    - severity: warning
      account: antigravity_user_1
      message: "Estimated 5 days until quota exhaustion"
      action: "Monitor usage, consider activation of copilot_dev_2"
  
  account_details:
    antigravity_user_1:
      provider: antigravity
      email: user1@example.com
      status: green
      estimated_quota: unlimited_free_tier
      last_used: 2026-02-23T12:45:00Z
      models_available: [claude-opus-4-6-thinking, gemini-3-pro, gemini-3-flash]
      
    antigravity_user_2:
      provider: antigravity
      email: user2@example.com
      status: green
      ...
    
    copilot_dev_1:
      provider: copilot
      email: copilot-dev-1@example.com
      status: green
      quota_used: 28/50  # messages
      quota_used_percent: 56%
      code_completions_remaining: 1987/2000
      burn_rate: "4.7 messages/day"
      days_until_exhaustion: 4.6
      reset_date: 2026-03-01
      last_used: 2026-02-23T14:20:00Z
    
    copilot_dev_3:
      provider: copilot
      email: copilot-dev-3@example.com
      status: red
      quota_used: 50/50  # EXHAUSTED
      code_completions_remaining: 450/2000
      last_used: 2026-02-23T09:15:00Z
      action_required: "Rotate out of primary rotation"
    
    opencode_zen:
      provider: opencode
      status: green
      service_health: operational
      available_models: [big-pickle, glm-5, gpt-5-nano, kimi-k2.5, minimax-m2.5]
      last_connection: 2026-02-23T14:30:00Z
    
    cline:
      provider: cline
      status: green
      last_activity: 2026-02-23T13:00:00Z
      mcp_servers: [xnai-agentbus, xnai-rag]
      error_count_24h: 0
    
    local_llm:
      provider: local
      status: green
      service: llama-cpp-python (port 8080)
      model_loaded: llama-2-7b
      memory_usage: 4.2GB
      health: operational
  
  recommendations:
    - priority: high
      action: "Activate copilot_dev_2 or copilot_dev_4 to replace exhausted dev_3"
      rationale: "4 out of 8 Copilot accounts approaching quota limit"
      
    - priority: medium
      action: "Research + onboard 3-5 free-tier providers for load balancing"
      rationale: "Reduce dependency on single provider pools"
      
    - priority: low
      action: "Monitor antigravity_user_1 usage trend; may rotate in 10 days"
      rationale: "Preventive rotation to avoid mid-month exhaustion"
  
  historical_trends:
    copilot_average_burn_rate: "4.8 messages/day"
    antigravity_health: "100% operational, no degradation"
    opencode_availability: "99.9% uptime"
    estimated_monthly_capacity: "400 Copilot msgs + unlimited Antigravity/OpenCode"
```

---

## Account Rotation & Failover Strategy

### Rotation Decision Tree

```
Task arrives needing provider X (e.g., Copilot Raptor)
    ↓
Query daily audit: Which Copilot accounts are healthy?
    ├─ If account 1-3 healthy: Use round-robin
    ├─ If account 1-3 depleted: Use account 4-8
    └─ If all depleted: Fallback to Gemini 3 Pro (OpenCode)
    ↓
Execute task
    ↓
Log usage to account_tracking
    ↓
Next task: Same account (if same type) or next in rotation
```

### Multi-Account Dispatch with Fallback

```yaml
dispatch_priority:
  copilot_raptor_code_analysis:
    tier_1:
      cli: copilot
      model: raptor-mini
      rotation_strategy: round-robin
      fallback_on_quota_exhaustion: tier_2
      
    tier_2:
      cli: opencode
      model: gemini-3-pro
      rotation_strategy: single_account
      fallback_on_exhaustion: tier_3
      
    tier_3:
      cli: local
      model: llama-2
      rotation_strategy: single
      fallback_on_exhaustion: fail
  
  antigravity_frontier_reasoning:
    tier_1:
      cli: opencode
      model: claude-opus-4-6-thinking
      rotation_strategy: round-robin_8_accounts
      fallback_on_exhaustion: tier_2
      
    tier_2:
      cli: copilot
      model: gpt-preview
      rotation_strategy: single
      fallback_on_exhaustion: tier_3
      
    tier_3:
      cli: local
      model: llama-2
      rotation_strategy: single
      fallback_on_exhaustion: fail
```

---

## Dashboard Metrics

### Real-Time Monitoring (Web-Based or CLI)

```
╔════════════════════════════════════════════════════════════╗
║                  Wave 4 Account Status Dashboard           ║
║                  Last Updated: 2026-02-23 14:35            ║
╠════════════════════════════════════════════════════════════╣
║  Provider         │ Accounts │ Health │ Capacity │ Trend   ║
╟────────────────────────────────────────────────────────────╢
║  Antigravity      │   8/8    │   🟢   │  100%    │  ↗ Up   ║
║  Copilot          │   6/8    │   🟡   │  56%     │  ↗ Up   ║
║  OpenCode Zen     │   1/1    │   🟢   │  100%    │  →      ║
║  Cline            │   1/1    │   🟢   │  100%    │  →      ║
║  Local LLM        │   1/1    │   🟢   │  100%    │  →      ║
╠════════════════════════════════════════════════════════════╣
║  ⚠️  Warnings:                                              ║
║  - Copilot dev_3: QUOTA EXHAUSTED (50/50 messages)         ║
║  - Copilot dev_1: 56% used (4.6 days remaining)            ║
║                                                             ║
║  📊 Capacity:                                               ║
║  - Copilot: 224/400 messages remaining (56% used)          ║
║  - Antigravity: Unlimited free tier (optimal utilization)  ║
║  - Combined: ~95% of Wave 4 monthly capacity available     ║
║                                                             ║
║  🔄 Next Rotation: Account 7 (Copilot) in 3 days          ║
╚════════════════════════════════════════════════════════════╝
```

### Alert Thresholds

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Quota Used % | < 50% | 50-80% | > 80% |
| Days Until Exhaustion | > 14 | 7-14 | < 7 |
| Service Health | Operational | Degraded | Down |
| Error Rate 24h | < 0.1% | 0.1-5% | > 5% |

---

## Implementation Roadmap

### Phase 2A: Design (THIS)
- [x] Account portfolio documented
- [x] Audit system architecture designed
- [x] Quota tracking algorithm specified
- [x] Rotation strategy mapped
- [x] Alert thresholds defined
- [ ] User feedback

### Phase 3A: Implementation
- [ ] Create audit data collector (Python/Bash)
- [ ] Build quota analyzer
- [ ] Setup daily cron job (2 AM UTC)
- [ ] Create dashboard (CLI or web)
- [ ] Implement alert system (email/Slack)

### Phase 4A: Testing & Validation
- [ ] Test quota tracking accuracy
- [ ] Verify alert triggering
- [ ] Validate rotation logic
- [ ] Performance test (audit < 15 min)

---

## Related Documents

- `memory_bank/ACCOUNT-REGISTRY.yaml` (account metadata)
- `memory_bank/strategies/WAVE-4-PHASE-1-STATUS-REPORT.md` (account confirmation)
- `memory_bank/activeContext.md` (current status)
- `WAVE-4-P2-MULTI-CLI-DISPATCH-DESIGN.md` (dispatch routing)

---

**Status**: 🔵 DRAFT - Awaiting User Review  
**Last Updated**: 2026-02-23  
**Next Checkpoint**: Implementation Phase 3A
