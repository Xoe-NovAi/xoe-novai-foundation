# Documentation Index & Navigation Map

**Last Updated**: March 7, 2026  
**Maintenance**: Auto-generated, keep current!

---

## 🚀 START HERE

**New to the project?**
1. Read: `README.md`
2. Follow: `QUICK_START.md`
3. Understand: `docs/ARCHITECTURE.md`

---

## 📋 CURRENT DOCUMENTS (Active)

### Strategic & Planning
- **OPUS_4_6_AUDIT_HANDOFF.md** - Current system audit & issues
- **OPUS_4_6_COMPREHENSIVE_HANDOFF.md** - Detailed analysis for Opus 4.6
- **SESSION_COMPLETION_SUMMARY.md** - Last recovery & system state

### Status & Progress  
- **STACK_STATUS_MARCH_7_2026.md** - Current services status
- **memory_bank/progress.md** - Current phase status
- **memory_bank/activeContext.md** - Current priorities

### Configuration & Operations
- **docs/protocols/INDEX.md** - Central registry of system protocols
- **docs/operations/INDEX.md** - Step-by-step operational procedures
- **memory_bank/OPERATIONS.md** - How to build, test, deploy
- **memory_bank/AGENTS.md** - Environment configuration
- **memory_bank/ACCOUNT-REGISTRY.yaml** - Credentials mapping
- **config/gemini-cli-integration.yaml** - Gemini setup
- **memory_bank/BLOCKS.yaml** - Memory configuration (CRITICAL)

### Implementation Guides
- **MEMORY_BANK_MCP_INTEGRATION.md** - Containerization guide
- **SETUP_MULTI_ACCOUNT_OAUTH.md** - OAuth implementation
- **USER_GUIDE_MULTI_ACCOUNT_OAUTH.md** - User guide for multi-account

### Architecture & Design
- **docs/ARCHITECTURE.md** - System architecture
- **memory_bank/ARCHITECTURE.md** - Additional details

### Infrastructure & Deployment
- **Makefile** - Build commands
- **infra/docker/docker-compose.yml** - Service definitions
- **infra/k8s/** - Kubernetes manifests

---

## 📚 ARCHIVED DOCUMENTS

**See `_archive/ARCHIVE-INDEX.md` for historical documents:**

- Implementation Completed
- Task Dispatch History  
- Strategy Versions (v1.0)
- Research Archive
- Session Handoffs

---

## 🎯 FIND DOCUMENTS BY PURPOSE

### "I need to..."

**...understand the system**
→ `docs/ARCHITECTURE.md`

**...get started quickly**
→ `QUICK_START.md`

**...see what's broken**
→ `OPUS_4_6_AUDIT_HANDOFF.md`

**...deploy/build**
→ `memory_bank/OPERATIONS.md`

**...configure something**
→ `config/` directory + `memory_bank/AGENTS.md`

**...understand OAuth**
→ `SETUP_MULTI_ACCOUNT_OAUTH.md`

**...understand Gemini setup**
→ `config/gemini-cli-integration.yaml`

**...understand memory system**
→ `MEMORY_BANK_MCP_INTEGRATION.md`

**...see old decisions**
→ `_archive/` + `ARCHIVE-INDEX.md`

**...understand current status**
→ `STACK_STATUS_MARCH_7_2026.md`

---

## 📂 DIRECTORY STRUCTURE

```
omega-stack/
├── README.md                          (Main entry point)
├── QUICK_START.md                     (Getting started)
├── docs/                              (Documentation)
│   ├── ARCHITECTURE.md
│   ├── DOCUMENTATION-INDEX.md         (This file)
│   └── ...
├── _archive/                          (Historical docs)
│   ├── implementation-completed/
│   ├── task-dispatch-history/
│   ├── strategy-versions/
│   ├── research-2026-02-27/
│   ├── session-handoffs/
│   └── ARCHIVE-INDEX.md
├── memory_bank/                       (System knowledge)
│   ├── BLOCKS.yaml                    (CRITICAL CONFIG)
│   ├── OPERATIONS.md
│   ├── AGENTS.md
│   └── ...
├── config/                            (Configuration files)
├── infra/                             (Infrastructure)
├── mcp-servers/                       (MCP implementations)
├── app/                               (Application code)
└── ... (other code directories)
```

---

## ✅ MAINTENANCE CHECKLIST

When adding new documentation:
- [ ] Decide: Active doc or archive?
- [ ] If active: Update DOCUMENTATION-INDEX.md
- [ ] If archive: Move to _archive/ with category
- [ ] Update _archive/ARCHIVE-INDEX.md
- [ ] Test navigation from README.md

---

## 🔍 SEARCH TIPS

**To find a document**:
```bash
find . -name "*.md" -type f | grep -i "keyword"
```

**To find by category**:
```bash
ls _archive/*/          # List archive categories
ls docs/               # List doc categories
```

**To see all active docs**:
```bash
ls -1 *.md             # Root level docs only
```

---

## 🎓 HANDOFF NOTES FOR OPUS 4.6

See these detailed analyses for strategic review:
- **OPUS_4_6_COMPREHENSIVE_HANDOFF.md** - Main strategic document
- **Additional analyses in session workspace** - Deep dives

---

**Navigation Last Updated**: March 7, 2026
