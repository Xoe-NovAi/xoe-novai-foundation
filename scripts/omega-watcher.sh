#!/bin/bash
# Omega Real-Time Watcher
# Periodically updates metrics for the dashboard.

echo "📡 Omega Pulse Active. Updating metrics every 10 seconds..."
while true; do
    python3 scripts/omega-metrics-collector.py > /dev/null 2>&1
    sleep 10
done
