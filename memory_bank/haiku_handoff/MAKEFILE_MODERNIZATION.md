# 🛠️ MAKEFILE MODERNIZATION SPEC (Migration to `Just`)
**Status**: PROPOSED | **Target**: Opus 4.6 Refactor
**Goal**: Replace the brittle "God Makefile" with a modular Task Runner.

## 1. The Problem
The current `Makefile` is 2,200+ lines. It handles:
-   Docker orchestration
-   Python dependency management
-   Documentation building
-   Agent summoning
-   System monitoring

It is fragile, shell-dependent, and hard to read.

## 2. The Solution: `Just`
**Just** is a modern command runner. It supports:
-   **Cross-platform** (Linux/macOS/Windows).
-   **Language-agnostic** (Recipes can be Bash, Python, JS).
-   **Environment loading** (`.env` automatic).

## 3. Migration Strategy

### Phase 1: The Wrapper
Create a `Justfile` that wraps existing Make commands.
```just
# Justfile
default:
    @just --list

setup:
    make setup

up:
    make up
```

### Phase 2: modularization
Break the `Makefile` logic into `tasks/` scripts (Python/Bash) and call them directly from `Just`.

**Example Structure:**
```
root/
├── Justfile
├── tasks/
│   ├── docker.py
│   ├── agents.py
│   └── docs.py
```

### Phase 3: Deprecation
Remove `Makefile` once all commands are migrated.

## 4. Immediate Action for Opus
1.  Install `just`.
2.  Create the initial `Justfile`.
3.  Move complex logic (like "build-tracking") out of Make and into `scripts/setup/`.


**Archon Signature**: `Jem-SESS27.7-Sovereign` 🔱
