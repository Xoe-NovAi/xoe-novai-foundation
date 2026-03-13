# 📊 Usage Dashboard - XNAi Foundation

> **Last Updated**: 2026-02-23T00:00:00Z
> **Auto-Update**: Per-session

---

## 🎯 Quick Stats

| Platform | Total Available | Total Used | Remaining | % Used |
|----------|----------------|------------|-----------|--------|
| **Copilot Messages** | 400 | 0 | 400 | 0% |
| **Copilot Completions** | 16,000 | 0 | 16,000 | 0% |
| **Antigravity Tokens** | 4,000,000 | 0 | 4,000,000 | 0% |

---

## 📱 Copilot Account Pool

| Account | Status | Messages | Completions | Reset Date |
|---------|--------|----------|-------------|------------|
| copilot-01 | 🟢 ACTIVE | 0/50 (0%) | 0/2000 (0%) | 2026-03-01 |
| copilot-02 | 🟡 Ready | 0/50 (0%) | 0/2000 (0%) | 2026-03-01 |
| copilot-03 | 🟡 Ready | 0/50 (0%) | 0/2000 (0%) | 2026-03-01 |
| copilot-04 | 🟡 Ready | 0/50 (0%) | 0/2000 (0%) | 2026-03-01 |
| copilot-05 | 🟡 Ready | 0/50 (0%) | 0/2000 (0%) | 2026-03-01 |
| copilot-06 | 🟡 Ready | 0/50 (0%) | 0/2000 (0%) | 2026-03-01 |
| copilot-07 | 🟡 Ready | 0/50 (0%) | 0/2000 (0%) | 2026-03-01 |
| copilot-08 | 🟡 Ready | 0/50 (0%) | 0/2000 (0%) | 2026-03-01 |

### Copilot Model Preferences
- **Raptor Mini** ⚡ Fast, efficient for quick tasks
- **Claude Haiku 4.5** ⚡ Fast tactical operations

### Message Budget Allocation
| Category | Budget | Used | Remaining |
|----------|--------|------|-----------|
| Deep Reasoning | 10 | 0 | 10 |
| Code Generation | 15 | 0 | 15 |
| Quick Tasks | 10 | 0 | 10 |
| Research | 10 | 0 | 10 |
| Reserved | 5 | 0 | 5 |

---

## 🚀 Antigravity Account Pool

| Account | Status | Weekly Tokens | Current Model |
|---------|--------|---------------|---------------|
| antigravity-01 | 🟢 ACTIVE | 0/500,000 (0%) | claude-sonnet-4.6-antigravity |
| antigravity-02 | 🟡 Ready | 0/500,000 (0%) | - |
| antigravity-03 | 🟡 Ready | 0/500,000 (0%) | - |
| antigravity-04 | 🟡 Ready | 0/500,000 (0%) | - |
| antigravity-05 | 🟡 Ready | 0/500,000 (0%) | - |
| antigravity-06 | 🟡 Ready | 0/500,000 (0%) | - |
| antigravity-07 | 🟡 Ready | 0/500,000 (0%) | - |
| antigravity-08 | 🟡 Ready | 0/500,000 (0%) | - |

### Available Models (Antigravity)
| Model | Best For | Context | Priority |
|-------|----------|---------|----------|
| **Claude Opus 4.6 Thinking** | Deep reasoning, architecture | 200K | ⭐⭐⭐⭐⭐ |
| **Claude Sonnet 4.6** | Balanced tasks, code | 200K | ⭐⭐⭐⭐ |
| **Gemini 3.1 Pro** | Large context, multimodal | 1M+ | ⭐⭐⭐⭐⭐ |
| **DeepSeek v3** | Research, cost-effective | 64K | ⭐⭐⭐⭐ |
| **DeepSeek v1** | Simple tasks | 64K | ⭐⭐⭐ |
| **GPT-4.1** | General purpose | 128K | ⭐⭐⭐⭐ |
| **o3-mini** | Quick tasks | 200K | ⭐⭐⭐ |

---

## 🎨 Model Recommendations

### By Task Type

| Task Type | Recommended Model | Platform | Reason |
|-----------|-------------------|----------|--------|
| **Deep Analysis** | Opus 4.6 Thinking | Antigravity | Best reasoning |
| **Code Generation** | Claude Sonnet 4.6 | Antigravity | Quality/speed balance |
| **Quick Tasks** | Raptor Mini | Copilot | Preserve message budget |
| **Large Context** | Gemini 3.1 Pro | Antigravity | 1M+ context |
| **Research** | DeepSeek v3 | Antigravity | Cost-effective depth |
| **Testing** | Claude Haiku 4.5 | Copilot | Fast iteration |

---

## 📈 Usage Trends (Last 7 Days)

```
No data yet - tracking started 2026-02-23
```

---

## ⚠️ Alerts

| Alert | Threshold | Current | Status |
|-------|-----------|---------|--------|
| Copilot Low | 5 messages left | 50 | ✅ OK |
| Antigravity Low | 50,000 tokens left | 500,000 | ✅ OK |
| Account Rotation | 45 messages | 0 | ✅ OK |

---

## 📋 Recent Activity

| Timestamp | Account | Action | Tokens/Messages | Model |
|-----------|---------|--------|-----------------|-------|
| - | - | - | - | - |

---

## 🔧 Quick Commands

```bash
# View usage
cat memory_bank/usage/copilot-usage.json | jq '.totals'
cat memory_bank/usage/antigravity-usage.json | jq '.totals'

# Update dashboard
python scripts/update_usage_dashboard.py

# Check current account
echo $COPILOT_ACCOUNT
echo $ANTIGRAVITY_ACCOUNT
```

---

**Status**: ✅ All systems nominal
**Next Reset**: 2026-03-01 (Copilot) | Sunday (Antigravity)
