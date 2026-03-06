# Vikunja Implementation Guide (Claude Edition)

This directory contains consolidated and organized documentation for integrating Vikunja into the Xoe-NovAi Foundation stack.

## 📁 Directory Structure

### 🚀 [Guides](./guides/)
Action-oriented documents for resolving current blockers and deploying quickly.
- **[00_YOUR_3_QUESTIONS_ANSWERED.md](./guides/00_YOUR_3_QUESTIONS_ANSWERED.md)**: Executive summary answering the core build and requirement questions.
- **[UPDATED_VIKUNJA_BLOCKER_RESOLUTION.md](./guides/UPDATED_VIKUNJA_BLOCKER_RESOLUTION.md)**: The definitive guide to fixing Podman secret mounting and network issues.
- **[QUICK_DEPLOY_CHECKLIST.md](./guides/QUICK_DEPLOY_CHECKLIST.md)**: Step-by-step copy-paste ready commands for deployment.

### 📚 [Manual](./manual/)
Comprehensive 5-part manual for a deep understanding of the architecture and configuration.
- **[00-VIKUNJA_INDEX.md](./manual/00-VIKUNJA_INDEX.md)**: Master navigation for the manual.
- **[01-ARCHITECTURE_GAPS.md](./manual/01-VIKUNJA_ARCHITECTURE_GAPS.md)**: Understanding Vikunja design and rootless Podman.
- **[02-PREDEPLOYMENT.md](./manual/02-VIKUNJA_PREDEPLOYMENT.md)**: Environment validation and configuration setup.
- **[03-DEPLOYMENT.md](./manual/03-VIKUNJA_DEPLOYMENT.md)**: Docker Compose details and stack startup.
- **[04-TESTING.md](./manual/04-VIKUNJA_TESTING.md)**: Validation, performance baselines, and troubleshooting.
- **[05-ADVANCED.md](./manual/05-VIKUNJA_ADVANCED.md)**: Future features, API reference, and voice integration roadmap.

### 🔍 [Reference](./reference/)
Technical deep dives and background information.
- **[VIKUNJA_PODMAN_SECRETS_DEEP_DIVE.md](./reference/VIKUNJA_PODMAN_SECRETS_DEEP_DIVE.md)**: Technical explanation of why native Podman secrets fail in overlay compose files and why environment variables are the solution.

### 🗃️ [_archive](./_archive/)
Redundant, superseded, or duplicate files retained for data integrity.

---

## 🎯 Quick Start
1. Read **[00_YOUR_3_QUESTIONS_ANSWERED.md](./guides/00_YOUR_3_QUESTIONS_ANSWERED.md)** for the executive summary.
2. Follow **[QUICK_DEPLOY_CHECKLIST.md](./guides/QUICK_DEPLOY_CHECKLIST.md)** for implementation.
3. Consult the **[Manual](./manual/00-VIKUNJA_INDEX.md)** for deep dives into specific components.
