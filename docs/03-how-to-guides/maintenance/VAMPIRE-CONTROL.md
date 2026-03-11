# 🧛 Vampire Control: Managing Background Network Activity

This guide explains how to use the `vampire_control.sh` script to manage background systemd timers that perform periodic network requests.

## 📌 Overview
The XNAi Foundation Stack includes several automated timers for auditing and monitoring. While useful, these can consume bandwidth and CPU at inconvenient times. `vampire_control.sh` provides a single interface to purge or restore these "vampire" background tasks.

## 🚀 Usage

The script is located at `scripts/vampire_control.sh`.

### Check Status
To see which timers are currently running:
```bash
./scripts/vampire_control.sh status
```

### Stop Background Activity (The Purge)
To disable and stop all background network timers immediately:
```bash
./scripts/vampire_control.sh stop
```

### Restore Background Activity
To re-enable and start all background timers:
```bash
./scripts/vampire_control.sh start
```

## 🛠️ Managed Timers
The following timers are controlled by this script:
1.  **xnai-github-audit.timer**: Queries the GitHub API for account/repo status.
2.  **xnai-quota-audit.timer**: Checks current API and compute quotas.
3.  **runtime-probe.timer**: Periodic local system health checks.
4.  **xnai-antigravity-monitor.timer**: Monitors the Antigravity context state.

## 🛡️ Best Practices
- **Dev Mode**: Run `./scripts/vampire_control.sh stop` during heavy development or build sessions to maximize bandwidth.
- **Maintenance**: Run `./scripts/vampire_control.sh start` once a week to ensure your audits and health checks stay up to date.
