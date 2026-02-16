#!/usr/bin/env bash
# xnai-zram-init.sh
# Final Working Version for XNAi Foundation
# Version: 1.3.0

set -e

# Calculate optimal size (12GB for stability)
ZRAM_MB=12288

echo "XNAi zRAM Init: Activating 12GB zstd swap..."

# 1. Cleanup
for dev in /dev/zram*; do
    if [ -e "$dev" ]; then
        /usr/sbin/swapoff "$dev" 2>/dev/null || true
        /usr/sbin/zramctl --reset "$dev" 2>/dev/null || true
    fi
done

# 2. Reload module
/usr/sbin/modprobe -r zram 2>/dev/null || true
/usr/sbin/modprobe zram num_devices=1

# 3. Configure using working --find method
/usr/sbin/zramctl --find --size "${ZRAM_MB}M" --algorithm zstd

# 4. Activate
/usr/sbin/mkswap /dev/zram0
/usr/sbin/swapon -p 100 /dev/zram0

# 5. Kernel Tuning (ML Optimized)
echo "Setting vm.swappiness=180 and vm.page-cluster=0..."
/usr/sbin/sysctl -w vm.swappiness=180
/usr/sbin/sysctl -w vm.page-cluster=0

echo "✅ zRAM active."
/usr/sbin/zramctl
exit 0
