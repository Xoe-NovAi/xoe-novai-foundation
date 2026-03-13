#!/bin/bash
# 🔱 scripts/optimize_ryzen.sh - Optimized for Ryzen 5700U
# [AP:memory_bank/techContext.md#L14] (Ryzen Opt)

echo "🚀 Applying Ryzen 5700U Optimizations for Xoe-NovAi..."

# 1. Set CPU Governor to Performance
if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
    echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
    echo "✅ CPU Governor: Performance"
else
    echo "⚠️  CPU Governor path not found (WSL?)"
fi

# 2. Pin AI tasks to physical cores (0-7), avoiding logical threads (8-15)
# This is used when starting llama-cpp or other inference engines
# Alias is exported for session-level steering
alias xnai-steer='taskset -cp 0-7'
echo "✅ Core Steering: Phys-Cores 0-7 (taskset -cp 0-7)"

# 3. Transparent Hugepages for model memory
if [ -f /sys/kernel/mm/transparent_hugepage/enabled ]; then
    echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    echo "✅ Hugepages: Enabled (Always)"
else
    echo "⚠️  Transparent Hugepages path not found"
fi

# 4. ZRAM check (Avoid swapping if possible)
if command -v zramctl > /dev/null; then
    echo "✅ ZRAM: Detected"
    zramctl
else
    echo "⚠️  ZRAM: Not detected. Check swap usage during large model loads."
fi

echo "🔱 Metropolis Optimization Sealed."
