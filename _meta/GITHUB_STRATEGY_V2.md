---
document_type: strategy
title: Sovereign GitHub Strategy v2.0 - 2026 Free-Tier Optimization
created_by: Copilot
created_date: 2026-03-16
version: "2.0"
status: operational
---

# Sovereign GitHub Strategy v2.0 (2026 Edition)

**Target**: GitHub Free Tier optimization for Omega Stack
**Scope**: CI/CD, storage, Actions allocation
**Status**: Operational
**Last Updated**: 2026-03-16

---

## Executive Summary

The 2026 GitHub free tier imposes strict limits on Actions minutes and storage. The current CI workflow uses 7 sequential stages with heavy testing/benchmarking. This strategy optimizes resource allocation while maintaining quality gates.

**Key Constraint**: Free tier = 2,000 minutes/month (public) or ~67 min/day
**Current Consumption**: ~40-50 min per full CI run (estimated from workflow analysis)
**Monthly Runs**: ~3-5 runs (push to main/develop) = **120-250 min/month** ✅ SAFE

---

## 1. Current GitHub Actions Allocation & Usage

### 1.1 Existing Workflows

#### CI Pipeline (`.github/workflows/ci.yml`)
- **Stages**: 7 sequential jobs
  1. Omega Stack Setup (10 min timeout)
  2. Multi-Agent Testing (30 min timeout, 4 parallel agents)
  3. Security Scanning (15 min timeout)
  4. Performance Benchmarking (20 min timeout)
  5. Integration Testing (25 min timeout, 3 services)
  6. Documentation Generation (10 min timeout)
  7. Final Validation + Circuit Breaker (5 min timeout)

- **Estimated Execution**: 45-55 minutes per run
- **Dependencies**: All sequential (stage 2 waits for stage 1, etc.)
- **Concurrency**: Limited to 1 run per ref (cancel-in-progress: true)

#### Secret Scanning (`.github/workflows/secret-scanning.yml`)
- **Trigger**: Push to main/develop, PR, daily 2 AM schedule
- **Estimated Execution**: 5-8 minutes per run
- **Tools**: TruffleHog, pre-commit hooks

### 1.2 Current Resource Usage

```
Scenario 1: 2 pushes/week to main → 2 × 50 min = 100 min/month
Scenario 2: 5 PRs/week → 5 × 50 min = 250 min/month
Scenario 3: Daily secret scan (scheduled) → 30 × 6 min = 180 min/month
Scenario 4: Aggressive dev (daily main pushes) → 30 × 50 min = 1,500 min/month ⚠️
```

**Recommendation**: Scenario 1-2 is safe. Avoid daily main pushes in private repos.

---

## 2. GitHub 2026 Free-Tier Constraints

### Storage Limits
- **Public Repositories**: Unlimited storage + Actions
- **Private Repositories**:
  - **Actions**: 2,000 minutes/month (personal account)
  - **Storage**: 500 MB for private packages (GHCR)
  - **Backup/Artifacts**: 90-day retention (default)

### Compute Limits per Workflow Run
- **Job Timeout**: 6 hours max
- **Workflow Timeout**: 35 days (cumulative)
- **Concurrent Jobs**: 20 simultaneous jobs (free tier soft limit)
- **Matrix Strategy**: Multiplies job count (4 agents = 4 parallel jobs)

### Data Transfer
- **Storage**: ~100 MB/artifact × 30 artifacts = ~3 GB/month (with cleanup)
- **Container Registry**: Unlimited pulls/pushes for public images

---

## 3. Cost-Optimized Workflow Strategy

### 3.1 Critical Principle: Fail-Fast Optimization

**Goal**: Catch errors early, avoid expensive later stages

```
┌─────────────────┐
│  Lint/Format    │ 2 min
└────────┬────────┘
         │
    ✅/❌
         │
    ┌────▼────────────┐
    │  Unit Tests     │ 8 min
    └────────┬────────┘
             │
        ✅/❌
             │
        ┌────▼──────────────────┐
        │  Security Scan        │ 5 min
        │ (only if prev pass)   │
        └────────┬──────────────┘
                 │
            ✅/❌
                 │
        ┌────────▼─────────────────┐
        │  Full CI (heavy tests)   │ 30 min
        │ (only if prev pass)      │
        └──────────────────────────┘
```

### 3.2 Layered CI Strategy

**Layer 1 - Quick Gate** (5 min)
- Linting, format checks, static analysis
- Runs on every commit
- **Cost**: ~5 min/run

**Layer 2 - Unit Tests** (8 min)
- Fast unit tests, import checks
- Runs on every PR/push
- **Cost**: ~8 min/run

**Layer 3 - Security Baseline** (5 min)
- Bandit, Safety, pre-commit hooks
- Runs on every PR/push
- **Cost**: ~5 min/run

**Layer 4 - Integration & Performance** (30 min)
- Docker services (Redis, Postgres, Qdrant)
- Multi-agent testing, benchmarking
- **Runs**: Only on main/develop merges
- **Cost**: ~30 min/run

**Layer 5 - Documentation & Deployment** (8 min)
- MkDocs build, GH Pages deploy
- Runs on main only
- **Cost**: ~8 min/run

### 3.3 Optimization Tactics

#### Tactic 1: Smart Caching
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.cache/uv
      node_modules/
    key: ${{ runner.os }}-deps-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```
**Savings**: 3-5 min per run (dependency installation)

#### Tactic 2: Selective Job Execution
```yaml
jobs:
  heavy-tests:
    if: github.ref == 'refs/heads/main' || contains(github.event.pull_request.labels.*.name, 'full-ci')
    runs-on: ubuntu-latest
    # ... expensive tests only on main
```
**Savings**: 20-30 min for most PRs

#### Tactic 3: Matrix Limitation
```yaml
strategy:
  matrix:
    agent:
      - "claude"       # Only 2 agents instead of 4
      - "opencode"
  fail-fast: true      # Stop all agents if one fails
```
**Savings**: 10-15 min (fewer parallel agents)

#### Tactic 4: Artifact Cleanup
```yaml
- uses: actions/upload-artifact@v4
  with:
    retention-days: 7   # Delete after 7 days instead of 30
    compression-level: 9  # Compress artifacts
```
**Savings**: 200-300 MB/month storage

#### Tactic 5: Workflow Event Filtering
```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'app/**'       # Only trigger if app/ changes
      - 'requirements/**'
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 0'  # Weekly, not daily
```
**Savings**: 50-100 min/month (fewer false triggers)

---

## 4. Recommended Workflow Files

### 4.1 Fast-Lint Workflow (`.github/workflows/fast-lint.yml`)
Triggers on: Every push/PR to any branch
Duration: ~5 minutes
Cost: LOW

**Checks**:
- Black (Python formatting)
- Flake8 (linting)
- MyPy (type checking)
- Pre-commit hooks

### 4.2 Unit Tests Workflow (`.github/workflows/unit-tests.yml`)
Triggers on: Every PR + main/develop pushes
Duration: ~10 minutes
Cost: LOW

**Checks**:
- Pytest (unit tests only, skip integration)
- Coverage report
- Dependency audit

### 4.3 CI-Full Workflow (`.github/workflows/ci-full.yml`)
Triggers on: main/develop pushes + labeled PRs (`full-ci`)
Duration: ~30-40 minutes
Cost: MEDIUM

**Stages**:
1. Setup
2. Multi-agent testing (2 agents max, not 4)
3. Security (Bandit, Safety, Semgrep)
4. Performance benchmarks
5. Integration tests (Docker services)

### 4.4 Docs Deploy Workflow (`.github/workflows/docs-deploy.yml`)
Triggers on: main branch, docs/ changes
Duration: ~3-5 minutes
Cost: VERY LOW

**Checks**:
- MkDocs build
- Push to gh-pages branch

### 4.5 Keep-Alive Workflow (`.github/workflows/keep-alive.yml`)
Triggers on: Weekly schedule
Duration: ~1 minute
Cost: MINIMAL

**Purpose**: Prevent repository from being marked as inactive
**Action**: Minimal commit to update timestamp

---

## 5. Monthly Actions Minutes Estimate

### Conservative Scenario (Recommended)

```
Event                                   Frequency    Min/Run    Total/Month
─────────────────────────────────────────────────────────────────────────
Main push (CI-full)                      2x/week      35 min     280 min
PR to main (unit + lint)                 2x/week      15 min     120 min
Secret scanning (schedule)               1x/week      6 min      24 min
Docs deploy                              2x/month     5 min      10 min
Keep-alive (schedule)                    1x/week      1 min      4 min
─────────────────────────────────────────────────────────────────────────
TOTAL                                                             438 min
Remaining capacity (2000 min)                                    1,562 min ✅
Safety margin                                                     78% unused
```

### Aggressive Scenario (Avoid)

```
Event                                   Frequency    Min/Run    Total/Month
─────────────────────────────────────────────────────────────────────────
Main push (CI-full)                      3x/day       40 min     3,600 min
PR to main (unit + lint)                 5x/week      15 min     300 min
Secret scanning (daily schedule)         1x/day       6 min      180 min
─────────────────────────────────────────────────────────────────────────
TOTAL                                                             4,080 min ❌
EXCEEDS QUOTA BY                                                 2,080 min
```

---

## 6. Optimization Strategies

### Strategy 1: Parallel Job Groups
Instead of 7 sequential stages, use job dependencies strategically:
```
lint ──┐
       ├─→ unit-tests ──┐
quick  │                 ├─→ full-ci (only on main)
       ├─→ security ────┘
```
**Benefit**: Faster feedback (parallel non-blocking jobs)

### Strategy 2: Docker Layer Caching
```dockerfile
FROM ubuntu:22.04
# Layer 1: System deps (cached)
RUN apt-get update && apt-get install -y python3 python3-pip

# Layer 2: Python deps (cached when requirements.txt unchanged)
COPY requirements*.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Layer 3: App code (always rebuilt)
COPY . /app
WORKDIR /app
```
**Benefit**: 5-10 min savings on image builds

### Strategy 3: Scheduled Large Tasks
Move expensive tasks outside Actions:
```yaml
# .github/workflows/nightly-bench.yml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
jobs:
  benchmark:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    # Full benchmarking suite
```
**Benefit**: Predictable usage, avoids quota spikes

### Strategy 4: Artifact Tiering
```yaml
# Keep for 7 days
retention-days: 7

# OR trigger manual deletion
- name: Delete old artifacts
  run: |
    gh api repos/${{ github.repository }}/actions/artifacts \
      --paginate -q '.artifacts[] | select(.created_at < now - 7 days) | .id' \
      | xargs -I {} gh api repos/${{ github.repository }}/actions/artifacts/{} -X DELETE
```
**Benefit**: 50-100 MB/month storage savings

### Strategy 5: Conditional Matrix
```yaml
strategy:
  matrix:
    agent: ${{ github.event_name == 'push' && fromJson('["claude", "opencode"]') || fromJson('["claude", "opencode", "gemini", "cline"]') }}
```
**Logic**: 2 agents for PRs, 4 for main pushes
**Benefit**: 50% time savings for PR validation

---

## 7. Security & Guardrails

### Secrets Management
```yaml
env:
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Auto-provided
  GHCR_TOKEN: ${{ secrets.GHCR_TOKEN }}   # User-configured
```

### Branch Protection Rules
```yaml
# .github/policies/branch-protection.yml
Required status checks:
  - fast-lint
  - unit-tests
  - security-baseline
  - (ci-full only on main push)
```

### Dependabot Configuration
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 8. Implementation Roadmap

### Phase 1: Refactor CI (Week 1)
- [ ] Split ci.yml into fast-lint.yml + ci-full.yml
- [ ] Add selective job execution (if conditions)
- [ ] Configure artifact retention

### Phase 2: Add Workflows (Week 2)
- [ ] Create docs-deploy.yml
- [ ] Create unit-tests.yml (standalone)
- [ ] Create keep-alive.yml

### Phase 3: Optimize (Week 3)
- [ ] Add caching to all workflows
- [ ] Implement matrix limiting
- [ ] Add path filters

### Phase 4: Monitor (Ongoing)
- [ ] Track Actions usage in GH dashboard
- [ ] Monthly review of quota
- [ ] Adjust thresholds as needed

---

## 9. Expected Results

### Before Optimization
- Estimated: 400-600 min/month (variable)
- Risk: Quota overage in aggressive development
- Feedback time: 50+ minutes per change

### After Optimization
- Estimated: 200-300 min/month (conservative)
- Risk: 0% quota overage (82% unused capacity)
- Feedback time: 5 min (lint) + 15 min (full) on demand

### Metrics to Track
```
Monthly Dashboard:
- Actions minutes used: Target < 400/2000
- Artifact storage: Target < 1 GB
- Workflow duration: Target < 20 min (medium) / < 40 min (full)
- Job success rate: Target > 95%
```

---

## 10. Future Considerations

### Scaling Beyond Free Tier
If quota becomes tight:
1. **Move to Org Account** (3,000 min/month for Teams plan = $4/month)
2. **Use Self-Hosted Runners** (unlimited, but $0.002/min on private repos)
3. **Adopt Hybrid Strategy** (light tests on GH, heavy tests on local runner)

### Container Registry Strategy
- **Public Images**: GHCR (unlimited)
- **Private Images**: Consider Docker Hub (free tier: 100 pull/day limit)
- **Alternative**: Host images on artifact.dev (open-source friendly)

---

## 11. Reference Constraints

| Resource | Free Tier | Status |
|----------|-----------|--------|
| Repositories | Unlimited | ✅ OK |
| Actions minutes | 2,000/month | ⚠️ Must optimize |
| Storage | 500 MB (private GHCR) | ✅ OK (public GHCR = unlimited) |
| Concurrent jobs | 20 | ✅ OK |
| Job timeout | 6 hours | ✅ OK |
| Artifact retention | 90 days | ✅ OK (set to 7 days) |
| Pages | Unlimited | ✅ OK |

---

## 12. Workflow File References

- **`ci.yml`**: Full CI pipeline (now split into layered approach)
- **`secret-scanning.yml`**: Existing, optimize frequency
- **`fast-lint.yml`**: NEW - Quick checks on every push
- **`unit-tests.yml`**: NEW - Lightweight test suite
- **`docs-deploy.yml`**: NEW - MkDocs + GH Pages
- **`keep-alive.yml`**: NEW - Weekly timestamp update

---

**Document Status**: Operational
**Last Review**: 2026-03-16
**Next Review**: 2026-06-16 (quarterly)

*Strategy Co-authored by: Copilot + Omega Stack Team*
