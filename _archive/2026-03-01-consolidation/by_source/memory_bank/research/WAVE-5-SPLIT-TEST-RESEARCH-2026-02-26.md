# Research Findings — Wave 5 Split Test & Multi-Account

**Date**: 2026-02-26  
**Status**: Research Complete  
**Purpose**: Document latest research on Cline CLI, Qdrant, Antigravity

---

## 1. Cline CLI & kat-coder-pro Research

### Key Findings

| Finding | Source | Status |
|---------|--------|--------|
| **Cline CLI 2.0 released Feb 2026** | Official blog | ✅ CONFIRMED |
| **Kimi K2.5 free for limited time** | Cline blog | ✅ CONFIRMED |
| **code-supernova model (200K, free)** | Cline blog | ✅ NEW |
| **kat-coder-pro via OpenRouter** | OpenRouter API | ✅ AVAILABLE |
| **MiniMax M2.5 now free in Cline** | Cline blog | ✅ NEW |

### Model Options in Cline CLI

| Model | Context | Cost | Status |
|-------|---------|------|--------|
| Kimi K2.5 | 262K | Free (limited time) | ⚠️ Limited |
| code-supernova | 200K | Free (alpha) | ✅ Available |
| MiniMax M2.5 | 204K | Free | ✅ Available |
| kat-coder-pro | 262K | Via OpenRouter | ✅ Available |
| Claude Sonnet 4.5 | 200K+ | Paid | ✅ Available |

### Recommendations

1. **Primary Free Model**: Use code-supernova (200K, free during alpha)
2. **Backup Free Model**: MiniMax M2.5 (204K, free)
3. **Premium Option**: kat-coder-pro via OpenRouter for higher quality

---

## 2. Qdrant Collections Research

### Key Findings

| Finding | Source | Status |
|---------|--------|--------|
| **Snapshots for backup** | Qdrant docs | ✅ CONFIRMED |
| **Restore via API** | Qdrant docs | ✅ CONFIRMED |
| **Incremental backups only on Cloud** | GitHub issue | ⚠️ NOTE |
| **EBS snapshots for self-hosted** | Qdrant team | ✅ ALTERNATIVE |
| **Same version required for restore** | Qdrant FAQ | ⚠️ NOTE |

### Backup Strategy Recommendations

1. **Self-Hosted**: Use EBS/Google Cloud volume snapshots for incremental-style backups
2. **Collection Snapshots**: Full backups but portable between instances
3. **Version Locking**: Keep Qdrant version consistent for restore compatibility
4. **Migration Ready**: Snapshots useful for data migration between clusters

---

## 3. Antigravity Research

### Key Findings

| Finding | Source | Status |
|---------|--------|--------|
| **Free public preview** | Antigravity blog | ✅ CONFIRMED |
| **Gemini 3 Pro primary model** | Antigravity blog | ✅ CONFIRMED |
| **Claude Sonnet 4.5 available** | Antigravity blog | ✅ CONFIRMED |
| **GPT-OSS available** | Antigravity blog | ✅ CONFIRMED |
| **Kimi K2.5 via API** | SaaSCity blog | ✅ CONFIRMED |
| **MiniMax M2.1 integration** | LinkedIn | ✅ NEW |
| **Model quota visibility** | Medium article | ✅ NEW FEATURE |
| **2M token context for Gemini** | Antigravity docs | ✅ CONFIRMED |

### Antigravity as Free Tier Option

- **Free Tier**: Gemini 3 (2M context), Claude Sonnet 4.5, GPT-OSS
- **API Integration**: Kimi K2.5 and MiniMax available via external API
- **IDE Features**: Verifiable artifacts, parallel task inbox
- **Platform**: Cloud/Web-first, built for agentic development

---

## 4. Split Test Readiness

### ✅ Complete

| Component | Status |
|-----------|--------|
| Branch pushed | ✅ |
| Account registry (7 accounts, 325 msgs) | ✅ |
| Audit script | ✅ |
| Systemd timer | ✅ |
| 4-way split test plan | ✅ |
| Evaluation criteria | ✅ |
| Output directories created | ✅ |

### Model Commands

```bash
# Raptor Mini
copilot -m raptor-mini-preview "Create Wave 5 Manual..."

# Haiku 4.5
copilot -m claude-haiku-4-5 "Create Wave 5 Manual..."

# MiniMax M2.5
opencode --model minimax-m2.5-free "Create Wave 5 Manual..."

# kat-coder-pro
cline --model kat-coder-pro "Create Wave 5 Manual..."
```

---

## 5. Multi-Account Status

### Account Registry

| Account | Email | Status | Usage |
|---------|-------|--------|-------|
| admin | xoe.nova.ai@gmail.com | Daily Driver | 0/50 |
| contrib-01 | arcananovaai@gmail.com | SPLIT TEST READY | 25/50 |
| contrib-02-06 | Various | Ready after reset | 0/50 |

### Total Available

- **7 accounts** with 50 messages each = **350 messages/month**
- **Currently available**: 325 messages
- **Split test account**: arcananovaai@gmail.com (25 remaining)

---

**Next Research Jobs**

- **Vector Cache Integration** — prototype a caching layer to reduce redundant embedding lookups during repeated tests.
- **Parallel Execution Architecture** — blueprint for running models/memory banks simultaneously to cut runtime.
- **Automated Memory Bank Construction** — tools for scraping/indexing external data into structured banks.
- **Evaluation Metrics for Knowledge Banks** — research and propose metrics beyond raw similarity (recall, style, domain adherence).

**Last Updated**: 2026-02-26  
**Coordination Key**: `WAVE-5-SPLIT-TEST-2026-02-26`
