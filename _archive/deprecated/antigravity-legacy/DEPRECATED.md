# Deprecated Antigravity & OpenCode Scripts

**Archived Date**: 2026-03-04
**Reason**: Replaced by Sovereign Antigravity Operations System

The following files have been deprecated and replaced by a more robust, "sovereign" implementation that bypasses upstream OpenCode CLI bugs and removes dependencies on external tools like `yq`.

## Archived Files

| File | Replacement | Reason |
|------|-------------|--------|
| `scripts/xnai-setup-opencode-providers.sh` | `scripts/antigravity-maintenance.sh` | Replaced by Python-based health/sync/provision tool. |
| `scripts/setup-opencode-multiaccount.sh` | `scripts/antigravity-maintenance.sh` | Combined setup/maintenance logic. |
| `scripts/xnai-inject-credentials.sh` | `scripts/antigravity-maintenance.sh` | `provision` command handles this now. |
| `scripts/xnai-setup-opencode-rotation.sh` | `scripts/antigravity-maintenance.sh` | Monitoring integrated into systemd service. |
| `config/templates/opencode-credentials.yaml.template` | `~/.config/opencode/antigravity-accounts.json` | Configuration is now managed directly via JSON/JS tools. |

## New System Architecture

- **Login**: `node scripts/antigravity-direct-login.js` (Bypasses OpenCode auth)
- **Maintenance**: `./scripts/antigravity-maintenance.sh` (Health, Sync, Provision)
- **Automation**: `scripts/systemd/xnai-antigravity-monitor.service`
- **Documentation**: `docs/ANTIGRAVITY_SOVEREIGN_OPS.md`
