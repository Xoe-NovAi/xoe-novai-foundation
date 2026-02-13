#!/usr/bin/env bash
# zRAM Health Check + node_exporter textfile output
# Writes a metric file to /var/lib/node_exporter/textfile_collector/ if writable

OUTPUT_DIR="/var/lib/node_exporter/textfile_collector"
TMPFILE="/tmp/xnai_zram.metrics"

# Gather compression ratio
ZRAM_LINE=$(zramctl 2>/dev/null | grep zram0 || true)
if [ -z "$ZRAM_LINE" ]; then
  echo "# xnai_zram_compression_ratio 0" > "$TMPFILE"
else
  # Parse DATA and COMPR columns (example: 1.2G 600M)
  DATA=$(echo "$ZRAM_LINE" | awk '{print $3}')
  COMPR=$(echo "$ZRAM_LINE" | awk '{print $4}')
  # Very simple parsing for M/G units
  to_mb(){ echo "$1" | sed -E 's/G/000/; s/M//; s/K/0/; s/b$//'; }
  DATA_MB=$(to_mb "$DATA")
  COMPR_MB=$(to_mb "$COMPR")
  if [ -n "$COMPR_MB" ] && [ "$COMPR_MB" -gt 0 ]; then
    RATIO=$(awk "BEGIN {printf \"%.2f\", $DATA_MB / $COMPR_MB}")
  else
    RATIO=0
  fi
  echo "# xnai_zram_compression_ratio $RATIO" > "$TMPFILE"
fi

# Write to node_exporter textfile collector if possible
if [ -w "$OUTPUT_DIR" ]; then
  sudo mkdir -p "$OUTPUT_DIR" 2>/dev/null || true
  sudo mv "$TMPFILE" "$OUTPUT_DIR/xnai_zram.prom" 2>/dev/null || sudo cp "$TMPFILE" "$OUTPUT_DIR/xnai_zram.prom"
  echo "Wrote metric to $OUTPUT_DIR/xnai_zram.prom"
else
  echo "Textfile collector not writable; printing metrics to stdout:" && cat "$TMPFILE"
fi

# Container runtime memory usage fallback (podman/docker)
if command -v podman &>/dev/null; then
  podman stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
elif command -v docker &>/dev/null; then
  docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
else
  echo "No container runtime detected"
fi

# Basic system status
free -h
zramctl || true

exit 0
