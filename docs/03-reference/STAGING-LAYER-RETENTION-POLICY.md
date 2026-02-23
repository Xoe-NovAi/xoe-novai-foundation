# Reference: Staging Layer Retention Policy

> **Status**: PROPOSAL
> **Date**: 2026-02-22
> **Context**: JOB-R009 - Staging Layer TTL Cleanup

---

## 1. Introduction

This document specifies the retention policies and cleanup mechanisms for the XNAi Foundation staging layer (`library/_staging/` and `data/scraping_results/`).

## 2. Retention Tiers

| Data Tier | Path | TTL | Justification |
|-----------|------|-----|---------------|
| **Rejected** | `library/_staging/rejected/` | 48 Hours | Low value; kept briefly for debugging extraction failures. |
| **Extracted** | `library/_staging/extracted/` | 7 Days | Raw content; needed during active distillation sprints. |
| **Distilled** | `library/_staging/distilled/` | 30 Days | High-value artifacts; kept until verified and moved to long-term memory. |
| **Scraping Logs** | `data/scraping_results/` | 14 Days | Execution reports; needed for performance analysis and retry logic. |

---

## 3. Cleanup Mechanism: systemd-tmpfiles

The primary cleanup mechanism is the standard `systemd-tmpfiles` utility.

### 3.1 Configuration (`/etc/tmpfiles.d/xnai-staging.conf`)

```conf
# Type  Path                         Mode UID  GID  Age  Argument
d       /home/arcana-novai/Documents/xnai-foundation/library/_staging/rejected  0755 root root 2d   -
d       /home/arcana-novai/Documents/xnai-foundation/library/_staging/extracted 0755 root root 7d   -
d       /home/arcana-novai/Documents/xnai-foundation/library/_staging/distilled 0755 root root 30d  -
d       /home/arcana-novai/Documents/xnai-foundation/data/scraping_results      0755 root root 14d  -
```

### 3.2 Manual Execution
To manually trigger the cleanup (dry-run):
```bash
systemd-tmpfiles --clean --dry-run /etc/tmpfiles.d/xnai-staging.conf
```

---

## 4. Operational Guardrails

1. **Lock File Protection**: Any directory containing a `.lock` file will be skipped by the cleanup process.
2. **Active Session Exclusion**: Files with a modification time newer than 1 hour will never be deleted, even if they exceed the TTL.
3. **Audit Logging**: Cleanup actions are logged to journald via `systemd-tmpfiles --clean`.

---

## 5. Next Steps
1. Create the `xnai-staging.conf` template in the `scripts/` or `deploy/` directory.
2. Implement a pre-flight check script to verify the existence of these paths.
3. Schedule a weekly "Deep Cleanup" via a systemd timer for larger artifacts.
