# IDE & CLI Tool Known Issues

**Created**: 2026-02-27  
**Status**: ACTIVE - Tracking Known Issues  
**Purpose**: Document known issues, limitations, and workarounds for AI assistants and IDEs

---

## Overview

This document tracks known issues with the AI coding assistants and IDEs used in the XNAi Foundation. These issues inform system design, memory management, and operational procedures.

---

## OpenCode CLI

### Memory Issues

#### CRITICAL: Never-Ending Memory Leak
| Aspect | Details |
|--------|---------|
| **Symptom** | OpenCode progressively fills BOTH RAM AND zRAM swap until system-wide OOM |
| **Root Cause** | Unknown - appears to be a memory leak in session/context management |
| **Impact** | **Filled entire 12GB zRAM drive** - caused system-wide OOM |
| **First Observed** | 2026-02-27 |

**Incident Timeline**:
- Physical RAM: 6.4 GB / 6.6 GB (97%)
- zRAM Swap: 11.3 GB / 12 GB (94%)
- OpenCode Process: 1.9 GB (27.5% of system RAM)
- **Result**: Complete system OOM - all processes killed

**CRITICAL Implication**: This is a **progressive, never-ending leak** that will eventually consume all available memory regardless of swap size. OpenCode MUST be restarted before it fills available resources.

#### Progressive Memory Growth
| Aspect | Details |
|--------|---------|
| **Symptom** | Memory usage grows from ~500MB to 2GB+ over extended sessions |
| **Cause** | Session history, tool outputs, and context accumulation not fully released |
| **Impact** | Can cause system-wide OOM on memory-constrained systems (6.6GB RAM + 12GB zRAM) |
| **First Observed** | 2026-02-27 |

**Timeline**:
- Start: ~500MB
- After 1 hour: ~800MB
- After 2 hours: ~1.2GB
- After 3+ hours: ~1.9GB+ (risk of OOM)

**Mitigation**:
```bash
# Restart OpenCode periodically (every 2-3 hours of heavy use)

# Clear session history (backup first)
cp ~/.local/share/opencode/opencode.db ~/.local/share/opencode/opencode.db.backup
rm -rf ~/.local/share/opencode/storage/session/*

# Clear tool outputs
rm -rf ~/.local/share/opencode/tool-output/*
```

#### Database Growth
| Aspect | Details |
|--------|---------|
| **Symptom** | `opencode.db` grows to 100MB+ |
| **Cause** | Conversation history, tool outputs, session state stored in SQLite |
| **Location** | `~/.local/share/opencode/opencode.db` |

**Mitigation**: Periodic database cleanup (backup first)

#### Context Compaction
| Aspect | Details |
|--------|---------|
| **Symptom** | "Compacting conversation..." messages appear |
| **Cause** | OpenCode compacts context at ~75% of model context window |
| **Note** | This is NOT the same as model context limit - it's OpenCode's internal memory management |

---

## VSCodium / VS Code Extensions

### Memory Issues

#### Extension Host Crashes
| Error Code | Meaning | Likely Cause |
|------------|---------|--------------|
| 15 (SIGTERM) | Killed externally | OOM killer |
| 133 (SIGSEGV) | Segmentation fault | Memory corruption/crash |

**Observed Crashes**:
- **fileWatcher**: Code 15 (killed by OOM)
- **extensionHost**: Code 133 (crashed)

#### GitHub Copilot Extension
| Issue | Status | Details |
|-------|--------|---------|
| Memory exhaustion in extension host | KNOWN | Known issue - GitHub Copilot causes high memory usage |
| Context window discrepancy | INVESTIGATING | 192K observed vs 264K expected in VS Code Insiders |

**Recommendations**:
1. Disable unused extensions
2. Use "Help: Start Extension Bisect" to find memory-hogging extensions
3. Limit concurrent AI operations
4. Close unused workspaces

---

## VS Code Insiders

### Specific Issues

#### Context Window Discrepancy
| Aspect | Details |
|--------|---------|
| **Expected** | 264K tokens |
| **Observed** | 192K tokens |
| **Environment** | Copilot Extension in VS Code Insiders |
| **Status** | INVESTIGATING - Research needed |

#### Additional Notes
- Same codebase as VSCodium
- Memory issues similar to VSCodium
- Need to verify if this is an Insiders-specific issue

---

## GitHub Copilot

### CLI vs Extension

| Aspect | CLI | Extension |
|--------|-----|----------|
| Context Window | TBD | 192K (observed) |
| Memory Management | Session-based | Extension host |
| Issues | Redis/Qdrant integration | Memory pressure |

---

## Workaround Summary

| Tool | Issue | Workaround |
|------|-------|------------|
| OpenCode | Memory growth | Restart every 2-3 hours |
| OpenCode | DB growth | Periodic cleanup |
| VSCodium | Extension OOM | Disable unused extensions |
| Copilot | High memory | Limit concurrent operations |
| VS Code Insiders | Context 192K | Research ongoing |

---

## Investigation Required

| Issue | Priority | Status |
|-------|----------|--------|
| Raptor context window (264K vs 192K) | P0 | Research pending |
| OpenCode memory leak root cause | P1 | Monitoring |
| VSCodium extension optimization | P2 | Pending |

---

**Last Updated**: 2026-02-27
**Owner**: MC-Overseer
**Review**: After each major session
