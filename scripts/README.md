# Scripts Directory Organization

**Last Updated**: 2026-03-01

## Overview

The scripts directory contains operational, maintenance, and development scripts for the XNAi Foundation Stack.

## Active Scripts (Regularly Used)

### Core Operations
| Script | Purpose | Status |
|--------|---------|--------|
| `offline_library_manager.py` | Library/book ingestion | ✅ ACTIVE |
| `library_sentry.py` | Monitors bookdrop folder | ✅ ACTIVE |
| `initialize_experts.py` | Expert persona initialization | ✅ ACTIVE |
| `memory_bank_manager.py` | Memory bank operations | ✅ ACTIVE |

### Infrastructure
| Script | Purpose | Status |
|--------|---------|--------|
| `stack_health_check.sh` | Health monitoring | ✅ ACTIVE |
| `redis_health_check.py` | Redis health | ✅ ACTIVE |
| `system_probe.py` | System diagnostics | ✅ ACTIVE |
| `verify_infrastructure.py` | Infra validation | ✅ ACTIVE |

### Backup & Restore
| Script | Purpose | Status |
|--------|---------|--------|
| `backup-atomic-all.sh` | Full system backup | ✅ ACTIVE |
| `backup-redis.sh` | Redis backup | ✅ ACTIVE |
| `backup-qdrant.sh` | Qdrant backup | ✅ ACTIVE |
| `backup-postgresql.sh` | PostgreSQL backup | ✅ ACTIVE |
| `restore-*.sh` | Restore scripts | ✅ ACTIVE |

### Wave 5 (Split Test & Strategy)
| Script | Purpose | Status |
|--------|---------|--------|
| `wave5_strategy_manager.py` | Strategy management | ✅ ACTIVE |
| `wave5-strategy-analyzer.py` | Strategy analysis | ✅ ACTIVE |

### Account Management
| Script | Purpose | Status |
|--------|---------|--------|
| `agent-account-manager.py` | Multi-account management | ✅ ACTIVE |
| `agent-health-monitor.py` | Account health | ✅ ACTIVE |
| `xnai-quota-auditor.py` | Quota auditing | ✅ ACTIVE |
| `github-account-audit.py` | GitHub audit | ✅ ACTIVE |

## Obsolete Scripts (Moved to Archive)

### Phase Execution Scripts
| Original Location | Status | Reason |
|------------------|--------|--------|
| `execute_autonomous_phase2.py` | ❌ OBSOLETE | Phase complete |
| `execute_autonomous_phase3.py` | ❌ OBSOLETE | Phase complete |
| `execute_autonomous_phase4.py` | ❌ OBSOLETE | Phase complete |
| `execute_phase2.py` | ❌ OBSOLETE | Phase complete |
| `phase5*.py` (multiple) | ❌ OBSOLETE | Replaced by wave5 scripts |

### Duplicate Scripts
| Original Location | Status | Reason |
|------------------|--------|--------|
| `agent_state_redis.py` | ❌ DUPLICATE | Superseded by v2 |
| `agent_state_redis2.py` | ❌ DUPLICATE | Keep v2 only |

### Deprecated
| Original Location | Status | Reason |
|------------------|--------|--------|
| `phase_b_*.py` | ❌ DEPRECATED | Old research |
| `validate_phase*.py` | ❌ DEPRECATED | Consolidated |

## Systemd Services

Located in: `scripts/systemd/`

| File | Purpose |
|------|---------|
| `runtime-probe.service` | System probe service |
| `runtime-probe.timer` | Scheduled probe |
| `xnai-quota-audit.service` | Quota audit service |
| `xnai-quota-audit.timer` | Quota audit schedule |
| `xnai-github-audit.service` | GitHub audit service |
| `xnai-github-audit.timer` | GitHub audit schedule |

## Docker Timer Units

Located in: `scripts/*.timer`

| File | Purpose |
|------|---------|
| `xnai-quota-audit.timer` | Daily quota check |
| `xnai-github-audit.timer` | GitHub account audit |

## Directory Structure

```
scripts/
├── _archive/                    # Archived scripts
│   ├── obsolete/                # Phase-complete scripts
│   └── duplicate/               # Superseded duplicates
├── account_management/          # Account utilities
├── build_tools/                 # Build utilities
├── recovery/                    # Recovery scripts
├── scrapers/                    # Web scrapers
├── split_test/                  # Split testing
├── sql/                         # SQL utilities
├── stack-cat/                   # Stack catalog tools
├── systemd/                     # Systemd services
├── *.sh                         # Shell scripts
└── *.py                         # Python scripts
```

## Adding New Scripts

1. Place in appropriate directory
2. Add to this index
3. Ensure executable bit set for shell scripts
4. Document in related docs if complex

## Cleanup Schedule

Review scripts quarterly for:
- Duplicates
- Obsolete functionality
- Missing dependencies
