# Git Strategy & Branch Management — GPT-4.1 Recommendation #1

**Confidence**: 80% (pending approval of strategy)

## Current State

### Branch Status
- **main**: production (remote: origin/main)
- **develop**: integration/staging (current HEAD @ cc8938f)
- **Remote features**:
  - audit/service-orchestrator-lazy-init
  - feature/multi-account-hardening
  - phase5a/account-naming-onboarding
  - phase5a/rollback-automation
  - xnai-agent-bus/harden-infra

### Recent Commit History
- cc8938f: chore(secrets) — redact exposed Google API key (SECURITY FIX)
- 29e9bb7: chore: sync development work
- Earlier: metropolis features, memory-bank MCP, service fixes

## Issues Identified

1. **Branch naming inconsistency**: Mix of audit/, feature/, phase5a/, xnai-agent-bus/
2. **Feature branches not merged**: 6 remote feature branches with unclear status
3. **No documented merge order**: Risk of breaking changes
4. **No rollback scripts**: Cannot safely undo problematic merges

## Recommended Strategy

### 1. Branch Naming Convention
```
main/
develop/
feature/<name>           # new features
hotfix/<name>           # urgent production fixes
audit/<component>       # audit/review branches (read-only)
phase5a/<component>     # phase-specific work (temporary)
xnai-agent-bus/<name>   # account-hardening work
```

### 2. Merge Order (Dependency Graph)
```
audit/* → (read-only, no merge)
hotfix/* → main → develop
feature/multi-account-hardening → develop (BLOCKS phase5a/*)
phase5a/* → develop (AFTER multi-account-hardening)
xnai-agent-bus/* → develop
```

### 3. PR-Based Merge Process
- [ ] All merges must have PR with code review
- [ ] Branch protection rules on main (require 1+ approval)
- [ ] Automated tests must pass
- [ ] Squash commits for feature branches (keep history clean)
- [ ] Tag releases on main (v1.0.0, v1.1.0, etc.)

### 4. Rollback Scripts
```bash
# Safe rollback (revert single commit)
git revert -n <commit> && git commit -m "revert: <reason>"

# Rollback to tag (if merge caused issues)
git reset --hard <tag> && git force-push origin <branch>

# Rollback with notification
./scripts/rollback-merge.sh <branch> <reason>
```

## Implementation Steps

1. **Tag current state**: `git tag v1.0.0-pre-gpt4-review`
2. **Review feature branches**: Assess each remote branch for merge readiness
3. **Build dependency graph**: Create BRANCH_DEPENDENCIES.md
4. **Create merge checklist**: Document testing & review gates
5. **Deploy branch protection rules**: GitHub Actions + rulesets
6. **Create rollback automation**: scripts/rollback-merge.sh

## Next Review
- After GPT-4.1 feedback on dependency priorities
- Before executing any merges
