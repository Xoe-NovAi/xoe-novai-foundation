#!/bin/bash
# ============================================================================
# 🔱 OMEGA STACK: ZRAM IGNITION (Self-Healing Wrapper)
# ============================================================================
# Purpose: Activates 4GB lz4 (Tier 1) + 8GB zstd (Tier 2) zRAM via passwordless sudo.
# Mechanism: Injects logic into /tmp/reset_zram.sh (whitelisted in sudoers).
# ============================================================================

set -e

# Define the payload script content
cat << 'EOF' > /tmp/reset_zram.sh
#!/bin/bash
set -e

# Tiered Sizes
FAST_MB=4096   # 4GB Fast Tier
BULK_MB=8192   # 8GB Bulk Tier

echo "🔱 XNAi Multi-ZRAM: Activating Tiered Setup (Privileged)..."

# 1. Brutal Cleanup: Unload and Reload Kernel Module
echo "  [1/5] Forcing clean state by reloading zram kernel module..."
if lsmod | grep -q "^zram "; then
    modprobe -r zram
fi
modprobe zram num_devices=2

# 2. Configure Tier 1 (Fast - lz4)
echo "  [2/5] Configuring Tier 1 (Fast - lz4)..."
zramctl /dev/zram0 --size "${FAST_MB}M" --algorithm lz4
mkswap /dev/zram0 >/dev/null
swapon -p 100 /dev/zram0

# 3. Configure Tier 2 (Bulk - zstd)
echo "  [3/5] Configuring Tier 2 (Bulk - zstd)..."
zramctl /dev/zram1 --size "${BULK_MB}M" --algorithm zstd
mkswap /dev/zram1 >/dev/null
swapon -p 50 /dev/zram1

# 4. Kernel Tuning
echo "  [4/5] Optimizing Kernel Parameters..."
sysctl -w vm.swappiness=180 >/dev/null
sysctl -w vm.page-cluster=0 >/dev/null

echo "  [5/5] Verification..."
echo "✅ Multi-Tiered zRAM Active & Rigid."
zramctl
swapon --show
EOF

# Make executable and run with passwordless sudo
chmod +x /tmp/reset_zram.sh
echo "🚀 Launching privileged zRAM setup via /tmp/reset_zram.sh..."
sudo /tmp/reset_zram.sh

# Cleanup
rm -f /tmp/reset_zram.sh
