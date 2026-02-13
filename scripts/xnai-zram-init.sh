#!/usr/bin/env bash
# xnai-zram-init.sh
# Calculate safe zRAM size and start zram device. Supports --dry-run.

DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
  esac
done

RAM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
RAM_MB=$(( RAM_KB / 1024 ))
# Default: 50% of RAM, min 2048MB, max RAM-2048MB
ZRAM_MB=$(( RAM_MB / 2 ))
if [ "$ZRAM_MB" -lt 2048 ]; then ZRAM_MB=2048; fi
if [ $((RAM_MB - 2048)) -lt "$ZRAM_MB" ]; then ZRAM_MB=$((RAM_MB - 2048)); fi
if [ "$ZRAM_MB" -lt 1024 ]; then ZRAM_MB=1024; fi
STREAMS=$(nproc)

echo "Calculated zRAM size: ${ZRAM_MB}M (physical RAM: ${RAM_MB}MB)"
echo "Compression streams: ${STREAMS}"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "Dry run mode; exiting"
  exit 0
fi

# Create zRAM device
/usr/bin/zramctl --find --size "${ZRAM_MB}M" --algorithm zstd --streams ${STREAMS} || exit 1
/bin/swapon /dev/zram0 || exit 1

# Done
exit 0
