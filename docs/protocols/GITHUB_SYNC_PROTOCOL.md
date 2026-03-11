# 🌊 Protocol: GitHub & CI/CD Synchronization (v4.1.2)

**Status**: AUTHORITATIVE  
**Objective**: Maintain 100% parity between local Metropolis state and the remote GitHub repository while triggering the 7-stage CI pipeline.

---

## 🏛️ 1. Pre-Flight Checks (Local Stage)
Before any `git push`, the agent MUST verify the following local state:

1.  **Secret Scan (Push Protection)**:
    ```bash
    grep -r "GITHUB_PAT\|REDIS_PASSWORD\|VIKUNJA_JWT_SECRET" .
    ```
    *Ensure no secrets are staged.*

2.  **Local Security Audit (Mirror CI Stage 3)**:
    If `bandit` or `safety` are available, run a baseline scan:
    ```bash
    bandit -r app/ -ll
    ```

3.  **Hydration Check**:
    Verify the `memory_bank/` is hydrated with the current Coordination Key.

---

## 🏗️ 2. Branching & Multi-Account Strategy
- **Primary Development**: `develop` branch. All feature-hardened states (SESS-XX) target `develop` to trigger the CI validation.
- **Production Stable**: `main` branch. Merges to `main` occur only after `develop` CI passes Stage 7.
- **Account Identification**: Ensure `git config user.email` matches the authorized contributor for the `Xoe-NovAi` organization.

---

## 📝 3. Atomic Commit Standards
Commits must follow the **Metropolis High-Signal** format:

```text
[TYPE]([DOMAIN]): [SUMMARY]

- [Key Change 1]
- [Key Change 2]

Coordination-Key: [METROPOLIS-KEY]
```

---

## 🚀 4. The Sync Beat
1.  **Stage**: `git add .` (respecting `.gitignore`).
2.  **Commit**: Apply the High-Signal message.
3.  **Push**: `git push origin develop`.
4.  **Monitor**: Open GitHub Actions and verify Stage 1-7 completion.

---
*Protocol Sealed by Metropolis-Coordination-Key: METROPOLIS-HARDENED-20260312-V2*
