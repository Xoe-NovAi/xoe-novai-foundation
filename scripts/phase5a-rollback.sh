#!/usr/bin/env bash
# Safe rollback for Phase-5A zRAM changes
# Reverses sysctl, systemd, and zram device configuration where possible.

set -euo pipefail
# allow environment overrides for testing and flexibility
BACKUP_DIR="${XNAI_PHASE5A_BACKUP_DIR:-/tmp/phase5a-backup}"
SYSCTL_FILE="${XNAI_SYSCTL_FILE:-/etc/sysctl.d/99-xnai-zram-tuning.conf}"
SERVICE_FILE="${XNAI_SERVICE_FILE:-/etc/systemd/system/xnai-zram.service}"
HEALTH_TIMER="${XNAI_HEALTH_TIMER:-/etc/systemd/system/xnai-zram-health.timer}"
HEALTH_SERVICE="${XNAI_HEALTH_SERVICE:-/etc/systemd/system/xnai-zram-health.service}"

echo "Phase 5A rollback — starting"
# Stop and disable services if present
if systemctl list-units --full -all | grep -q "xnai-zram"; then
  echo "Stopping xnai-zram.service (if running)"
  sudo systemctl stop xnai-zram.service || true
  sudo systemctl disable xnai-zram.service || true
fi

if systemctl list-units --full -all | grep -q "xnai-zram-health"; then
  echo "Stopping xnai-zram-health.timer/service"
  sudo systemctl stop xnai-zram-health.timer || true
  sudo systemctl disable xnai-zram-health.timer || true
  sudo systemctl stop xnai-zram-health.service || true
  sudo systemctl disable xnai-zram-health.service || true
fi

# Remove sysctl file (backup first)
if [ -f "$SYSCTL_FILE" ]; then
  echo "Backing up $SYSCTL_FILE to $BACKUP_DIR/sysctl-99-xnai-zram-tuning.conf.bak"
  sudo mkdir -p "$BACKUP_DIR"
  sudo cp -a "$SYSCTL_FILE" "$BACKUP_DIR/" || true
  sudo rm -f "$SYSCTL_FILE" || true
  sudo sysctl --system >/dev/null 2>&1 || true
fi

# Swapoff + zram reset
if swapon --show | grep -q zram0; then
  echo "Turning off zram swap /dev/zram0"
  sudo swapoff /dev/zram0 || true
fi

if command -v zramctl &>/dev/null; then
  # only attempt reset if present
  echo "Resetting /dev/zram0 (if exists)"
  sudo zramctl --reset /dev/zram0 || true
fi

# Remove systemd service files from /etc if present (backup first)
for f in "$SERVICE_FILE" "$HEALTH_SERVICE" "$HEALTH_TIMER"; do
  if [ -f "$f" ]; then
    echo "Backing up $f to $BACKUP_DIR"
    sudo mkdir -p "$BACKUP_DIR"
    sudo cp -a "$f" "$BACKUP_DIR/" || true
    sudo rm -f "$f" || true
  fi
done

# Reload systemd
sudo systemctl daemon-reload || true

echo "Rollback complete. Backups (if any) are in: $BACKUP_DIR"
exit 0
