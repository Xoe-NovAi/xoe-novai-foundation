#!/usr/bin/env bash
# xnai-zram-multi.sh
# Experimental Multi-Tiered zRAM for XNAi Foundation
# Tier 1 (Fast): lz4, high priority
# Tier 2 (Bulk): zstd, medium priority

set -e

# Tiered Sizes
FAST_MB=2048   # 2GB Fast Tier
BULK_MB=10240  # 10GB Bulk Tier

echo "XNAi Multi-ZRAM: Activating Tiered Setup..."

# 1. Cleanup
echo "Cleaning up..."
for dev in /dev/zram*; do
    if [ -e "$dev" ]; then
        /usr/sbin/swapoff "$dev" 2>/dev/null || true
        /usr/sbin/zramctl --reset "$dev" 2>/dev/null || true
    fi
done

# 2. Reload module with enough devices
/usr/sbin/modprobe -r zram 2>/dev/null || true
/usr/sbin/modprobe zram num_devices=2

# 3. Configure Tier 1 (Fast)
echo "Configuring Tier 1 (Fast - lz4)..."
/usr/sbin/zramctl --find --size "${FAST_MB}M" --algorithm lz4
/usr/sbin/mkswap /dev/zram0
/usr/sbin/swapon -p 100 /dev/zram0

# 4. Configure Tier 2 (Bulk)
echo "Configuring Tier 2 (Bulk - zstd)..."
/usr/sbin/zramctl --find --size "${BULK_MB}M" --algorithm zstd
/usr/sbin/mkswap /dev/zram1
/usr/sbin/swapon -p 50 /dev/zram1

# 5. Kernel Tuning (ML Optimized)
echo "Setting vm.swappiness=180 and vm.page-cluster=0..."
/usr/sbin/sysctl -w vm.swappiness=180
/usr/sbin/sysctl -w vm.page-cluster=0

echo "✅ Multi-Tiered zRAM active."
/usr/sbin/zramctl
swapon --show
exit 0
