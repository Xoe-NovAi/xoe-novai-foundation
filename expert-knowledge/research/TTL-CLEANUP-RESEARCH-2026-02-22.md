# Research: TTL Cleanup Systems for Staging Layers

> **Date**: 2026-02-22
> **Author**: GEMINI-MC
> **Status**: INITIAL DRAFT
> **Context**: JOB-R009 - Staging Layer TTL Cleanup

---

## 1. Overview

Staging layers often accumulate large volumes of transient data (scraped content, intermediate processing artifacts, temporary reports). Without a robust Time-To-Live (TTL) cleanup system, these directories can lead to disk exhaustion, performance degradation, and data governance issues.

## 2. Best Practices for TTL Cleanup

### 2.1 Policy Definition
- **Tiered Retention**: Different data types require different TTLs.
  - *Rejected content*: 24-48 hours.
  - *Raw/Extracted content*: 7 days.
  - *Processed/Distilled artifacts*: 30 days (or until verified).
- **Metadata-Driven**: Store TTL requirements in metadata (e.g., file headers, sidecar JSON, or directory naming conventions).
- **Safety Overlays**: Always exclude critical paths and active lock files.

### 2.2 Mechanism Selection
- **systemd-tmpfiles (Recommended)**: 
  - Standard Linux mechanism for managing temporary files.
  - Supports declarative configuration in `/etc/tmpfiles.d/` or `/usr/lib/tmpfiles.d/`.
  - Handles age-based cleanup, directory creation, and permission management.
- **systemd timers + cleanup script**:
  - Provides more flexibility for complex logic (e.g., checking database state before deletion).
  - Can integrate with application logs.
- **find + xargs + rm**:
  - Simple but prone to race conditions and performance issues with millions of files.
  - Harder to manage at scale.

### 2.3 Operational Safeguards
- **Dry-Run Mode**: Always support a "report-only" mode before active deletion.
- **Graceful Failure**: If cleanup fails (e.g., permission denied), it should not crash the system.
- **Atomic Operations**: Use tools that handle race conditions (e.g., `tmpwatch` handles files being moved while being checked).
- **Observability**: Log deletion counts and space reclaimed.

---

## 3. Tool Analysis: systemd-tmpfiles

`systemd-tmpfiles` is the modern standard for this task.

### 3.1 Configuration Syntax
```
# Type  Path            Mode UID  GID  Age  Argument
d       /path/to/dir    0755 root root 7d   -
e       /path/to/dir    -    -    -    1d   -
```
- `d`: Create directory if it doesn't exist and clean up old files.
- `e`: Clean up old files in existing directory.
- `Age`: Supports `s`, `m`, `h`, `d`, `w`.

### 3.2 Advantages
- **Built-in**: No extra dependencies on most modern distros.
- **Fast**: C-based implementation.
- **Safe**: Handles symlinks and recursive paths securely.
- **Standard**: Followed by system administrators.

---

## 4. Proposed Staging Layer Structure

Based on current project structure (`library/_staging`):

| Directory | TTL | Description |
|-----------|-----|-------------|
| `library/_staging/rejected/` | 2d | Content that failed quality gate |
| `library/_staging/extracted/` | 7d | Raw extracted content before distillation |
| `library/_staging/distilled/` | 30d | Final distilled artifacts before permanent storage |
| `data/scraping_results/` | 14d | Execution reports and raw scraping data |

---

## 5. Next Steps
1. Design the `systemd-tmpfiles` configuration.
2. Create a systemd timer for more granular control if needed.
3. Implement a manual cleanup script for ad-hoc maintenance.
