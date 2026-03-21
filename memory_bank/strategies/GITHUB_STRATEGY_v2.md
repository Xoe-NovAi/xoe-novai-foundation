# 🦅 OMEGA GitHub Strategy v2.0 (Sovereign Edition)
**Status**: ACTIVE | **Effect**: IMMEDIATE
**Context**: SESS-27.7 (Hardened 16GB)

---

## 1. THE CORE MANDATE: TRUNK INTEGRITY
**Problem**: Divergent histories (`fatal: refusing to merge unrelated histories`) and orphaned feature branches.
**Solution**: Rigid adherence to **Trunk-Based Development** with scoped feature branches.

### The Golden Rule
> **"Main is Production. Develop is Integration. Feature branches are Ephemeral."**

---

## 2. BRANCHING MODEL

| Branch | Role | Persistence | Protection |
| :--- | :--- | :--- | :--- |
| `main` | **Production Code**. Only `develop` merges here. | Permanent | **LOCKED**. No direct commits. |
| `develop` | **Integration Trunk**. All features merge here. | Permanent | **SEMI-PROTECTED**. PR/Review required. |
| `feature/*` | **Task Work**. Scoped to a specific objective. | Ephemeral | None. Delete on merge. |
| `fix/*` | **Bug Repair**. Urgent patches. | Ephemeral | None. Delete on merge. |
| `audit/*` | **Analysis**. Read-only/Log focused. | Ephemeral | None. Delete on merge. |

### Forbidden Patterns
- ❌ **Long-Lived Feature Branches**: If it lives > 48h, it is tech debt.
- ❌ **Orphan Branches**: Do not use `--orphan` unless initializing a completely separate artifact tree.
- ❌ **Direct Main Commits**: All changes must pass through `develop` for integration testing.

---

## 3. MERGE PROTOCOL (The Gatekeeper)

### 3.1 Pre-Merge Checklist
Before merging `feature/*` -> `develop`:
1.  **Rebase**: `git checkout feature/x && git rebase develop`. Resolve conflicts LOCALLY.
2.  **Squash**: `git rebase -i HEAD~N` to condense "WIP" commits into semantic units.
3.  **Test**: Run `pytest tests/smoke_import_test.py` (or project equivalent).

### 3.2 The Merge Action
```bash
git checkout develop
git merge --no-ff feature/x -m "Feat: Description (SESS-XX)"
git branch -d feature/x
git push origin develop
```

### 3.3 Main Release
When `develop` is stable:
```bash
git checkout main
git merge --fast-forward develop
git tag -a v4.X.X -m "Release SESS-XX"
git push origin main --tags
```

---

## 4. HANDLING DIVERGENCE (The "Unrelated Histories" Fix)
If a branch reports "unrelated histories," it is **Corrupted Context**.
**Protocol**:
1.  **Do NOT Force**: Never use `--allow-unrelated-histories` on code.
2.  **Archive**: Rename the bad branch to `_archive/corrupt/branch-name`.
3.  **Cherry-Pick**: Create a new branch off `develop` and cherry-pick valid commits.
4.  **Abandon**: If the drift is too large, abandon the branch and restart from `develop` using the files as reference.

---

## 5. AUTOMATION & TOOLING
-   **Commit Msg**: Must follow `Type: Subject (Context)` format.
    -   *Example*: `Feat: Add MB-MCP maintenance script (SESS-27.7)`
-   **GitIgnore**: 
    -   **Security**: `secrets/`, `.env`, `.oauth_key`, `internal_docs/`
    -   **Noise**: `projects/`, `*.log`, `__pycache__/`, `_archive/`, `backups/`
    -   **Gemini**: `.gemini/`, `**/*list_directory*`

**Archon Signature**: `Jem-SESS27.7-Sovereign` 🔱
