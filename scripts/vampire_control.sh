#!/bin/bash
# ============================================================================
# XNAi Vampire Control (v0.1.0)
# ============================================================================
# Purpose: Manages background network-dependent systemd timers to save
#          bandwidth and CPU.
# ============================================================================

ACTION=$1

TIMERS=(
    "xnai-github-audit.timer"
    "xnai-quota-audit.timer"
    "runtime-probe.timer"
    "xnai-antigravity-monitor.timer"
)

usage() {
    echo "Usage: $0 [status|stop|start]"
    echo "  status: Show current status of XNAi timers"
    echo "  stop:   Disable and stop all background timers (Vampire Purge)"
    echo "  start:  Enable and start all background timers"
    exit 1
}

case $ACTION in
    "status")
        echo "--- XNAi Background Timers Status ---"
        for timer in "${TIMERS[@]}"; do
            systemctl --user is-active "$timer" >/dev/null 2>&1
            ACTIVE=$?
            if [ $ACTIVE -eq 0 ]; then
                echo "🟢 $timer is ACTIVE"
            else
                echo "🔴 $timer is INACTIVE"
            fi
        done
        ;;
    "stop")
        echo "🧛 Executing Vampire Purge..."
        for timer in "${TIMERS[@]}"; do
            systemctl --user disable --now "$timer" >/dev/null 2>&1
            echo "✅ Stopped $timer"
        done
        ;;
    "start")
        echo "🚀 Restoring Background Services..."
        for timer in "${TIMERS[@]}"; do
            systemctl --user enable --now "$timer" >/dev/null 2>&1
            echo "✅ Started $timer"
        done
        ;;
    *)
        usage
        ;;
esac
