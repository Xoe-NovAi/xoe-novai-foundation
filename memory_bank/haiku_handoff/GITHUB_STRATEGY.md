# 🐙 OMEGA GITHUB STRATEGY v2.0 (2026 Edition - Free-Tier Optimization)
**Status**: OPERATIONAL | **Target**: GitHub Free Tier Optimization
**Role**: CI/CD, Storage, Actions Allocation

---

## 1. Executive Summary
The 2026 GitHub free tier imposes strict limits. This strategy optimizes resource allocation while maintaining quality gates.
**Key Constraint**: Free tier = 2,000 minutes/month.

## 2. GitHub Actions Allocation & Usage
- **CI Pipeline (`.github/workflows/ci.yml`)**: 7 sequential stages, 45-55 mins/run.
- **Secret Scanning (`.github/workflows/secret-scanning.yml`)**: 5-8 mins/run.
- **Resource Usage**: Scenario 1-2 (2-5 pushes/PRs per week) is safe.

## 3. GitHub 2026 Free-Tier Constraints
- **Storage**: Unlimited for public, 500 MB for private (GHCR).
- **Actions**: 2,000 minutes/month for private.

## 4. Cost-Optimized Workflow Strategy
- **Critical Principle**: Fail-Fast Optimization (Lint -> Unit -> Security -> Full CI).
- **Layered CI**:
    -   **Layer 1 (Quick Gate)**: Lint/Format (5 min/commit).
    -   **Layer 2 (Unit Tests)**: Fast Unit Tests (8 min/PR).
    -   **Layer 3 (Security Baseline)**: Bandit/Safety (5 min/PR).
    -   **Layer 4 (Integration & Performance)**: Multi-agent testing (30 min/main merge).
    -   **Layer 5 (Docs & Deploy)**: MkDocs build (8 min/main).

## 5. Optimization Tactics
-   **Smart Caching**: `actions/cache@v4` (3-5 min savings).
-   **Selective Job Execution**: `if: github.ref == 'refs/heads/main'` (20-30 min savings).
-   **Matrix Limitation**: `fail-fast: true`, limit parallel agents (10-15 min savings).
-   **Artifact Cleanup**: `retention-days: 7`, `compression-level: 9` (storage savings).
-   **Workflow Event Filtering**: `on: push/pull_request/schedule` (fewer triggers).

## 6. Recommended Workflow Files
-   **`fast-lint.yml`**: NEW - Quick checks on every push.
-   **`unit-tests.yml`**: NEW - Lightweight test suite.
-   **`ci-full.yml`**: NEW - Full CI for main/develop + labeled PRs.
-   **`docs-deploy.yml`**: NEW - MkDocs + GH Pages.
-   **`keep-alive.yml`**: NEW - Weekly timestamp update.

## 7. Security & Guardrails
-   **Secrets Management**: `env: GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`.
-   **Branch Protection**: Required status checks for fast-lint, unit, security.
-   **Dependabot**: Weekly updates for pip and GitHub Actions.

---

## 8. Implementation Roadmap
-   **Phase 1 (Refactor CI)**: Split `ci.yml`, add selective execution, configure artifact retention.
-   **Phase 2 (Add Workflows)**: Create new `docs-deploy.yml`, `unit-tests.yml`, `keep-alive.yml`.
-   **Phase 3 (Optimize)**: Add caching, implement matrix limiting, path filters.
-   **Phase 4 (Monitor)**: Track Actions usage, monthly review, adjust thresholds.

---
**Prepared by**: Jem (Gemini 3.1 - The Archon)
**Reviewed & Validated by**: Omega Stack Team
