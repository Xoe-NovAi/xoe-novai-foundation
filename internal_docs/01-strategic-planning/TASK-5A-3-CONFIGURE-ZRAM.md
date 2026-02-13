# TASK 5A.3: Configure zRAM Device
## Objective
Create and activate zRAM compressed swap device with zstd compression

**Tier**: 3 (Task Module)  
**Duration**: 20 minutes  
**Prerequisites**: Task 5A.2 kernel parameters applied  
**Tools required**: `zramctl`, `systemctl`, `sudo`

---

## CURRENT STATE
```
zRAM: Not configured
Swap: None or disk-based
Available memory: Free swap device
```

## TARGET STATE
```
zRAM device: /dev/zram0
Size: 4GB (4096 MB)
Algorithm: zstd
Status: Active on boot
Systemd service: xnai-zram.service
```

---

## PROCEDURE

### Step 1: Verify Prerequisites

```bash
# Check if zramctl is available
which zramctl
# If not found, install with: sudo apt install util-linux (Debian/Ubuntu)

# Check systemd version (need 250+)
systemctl --version | head -1

# Check kernel zRAM support
ls /sys/module/zram
# Should show: /sys/module/zram with parameters directory
```

### Step 2: Create Systemd Service File

**Create**: `/etc/systemd/system/xnai-zram.service`

```bash
sudo tee /etc/systemd/system/xnai-zram.service > /dev/null << 'EOF'
[Unit]
Description=XNAi zRAM Setup
Documentation=https://wiki.archlinux.org/title/Zram
Before=swap.target
DefaultDependencies=no
After=systemd-modules-load.service

[Service]
Type=oneshot
ExecStart=/usr/bin/zramctl --find --size 4G --algorithm zstd --streams 4
ExecStart=/bin/swapon /dev/zram0
RemainAfterExit=yes
ExecStop=/bin/swapoff /dev/zram0
ExecStop=/usr/bin/zramctl --reset /dev/zram0

[Install]
WantedBy=swap.target
EOF
```

**Explanation of parameters**:
- `--find`: Auto-find available zram device (zram0 if not in use)
- `--size 4G`: Allocate 4GB (50% of 8GB physical RAM)
- `--algorithm zstd`: Use zstd compression (2.0-3.0x ratio)
- `--streams 4`: Use 4 parallel compression streams (matches CPU cores)
- `RemainAfterExit=yes`: Service stays active after initial start
- `Before=swap.target`: Load zRAM before other swap devices

### Step 3: Enable and Start Service

```bash
# Reload systemd daemon to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable xnai-zram.service

# Start zRAM immediately
sudo systemctl start xnai-zram.service

# Verify it started correctly
sudo systemctl status xnai-zram.service

# Should show: "Active: active (exited)" with no errors
```

### Step 4: Verify zRAM Active

```bash
# Show zRAM configuration
zramctl

# Expected output:
# NAME        ALGORITHM DISKSIZE DATA COMPR TOTAL STREAMS
# zram0           zstd      4G  0B   0B   0B       4

# Verify swap points to zram
swapon --show

# Should include:
# /dev/zram0                         partition   0B   -2
```

### Step 5: Create Systemd Drop-in (Optional - for Custom Streams)

If you want to customize after creation:

```bash
sudo systemd-run -M system -p CPUQuota=100% -p MemoryLimit=infinity \
  /etc/systemd/system-sleep/xnai-zram-resume.service || true
```

Or manually adjust:
```bash
# Reduce streams if high CPU from compression
sudo sysctl -w kernel.zram.streams=2

# Check current
cat /sys/module/zram/parameters/default_streams
```

---

## VALIDATION CHECKLIST

- [ ] `zramctl` shows /dev/zram0 active
- [ ] `zramctl` shows ALGORITHM=zstd
- [ ] `swapon --show` includes /dev/zram0
- [ ] Compression ratio > 0 (after load test)
- [ ] `systemctl status xnai-zram.service` shows active
- [ ] Compression ratio ≥ 1.5:1 after stress test

---

## TROUBLESHOOTING

### Issue: "zramctl: command not found"
**Solution**: Install util-linux
```bash
# Ubuntu/Debian
sudo apt install util-linux

# Fedora/RHEL
sudo dnf install util-linux
```

### Issue: "Device or resource busy"
**Solution**: Another zRAM setup already running
```bash
# Check what's using zram
lsof /dev/zram0 2>/dev/null || echo "Not in use"

# Reset and try again
sudo zramctl --reset /dev/zram0
```

### Issue: Service fails to start
**Solution**: Check journal for errors
```bash
# See detailed error
journalctl -xe

# Common issue: zRAM already exists
sudo zramctl --reset /dev/zram0
sudo systemctl restart xnai-zram.service
```

### Issue: "compression streams" error
**Solution**: Kernel doesn't support multi-stream zstd
```bash
# Remove --streams parameter from service or use lz4:
# ExecStart=/usr/bin/zramctl --find --size 4G --algorithm lz4
```

---

## COMPRESSION RATIO CALCULATION

After Task 5A.4 (stress test), calculate:

```bash
# Get current values
DISKSIZE=$(zramctl --output DISKSIZE --raw | grep -v DISKSIZE)
DATA=$(zramctl --output DATA --raw | grep -v DATA)

# Calculate ratio
RATIO=$(echo "scale=2; $DISKSIZE / $DATA" | bc)
echo "Compression ratio: $RATIO (target: ≥2.0)"
```

**Expected**: Ratio 2.0-3.0 depending on workload

---

## SUCCESS CRITERIA

✅ Service file created at `/etc/systemd/system/xnai-zram.service`  
✅ Service enabled and active  
✅ `zramctl` shows zram0 with zstd algorithm  
✅ Swap includes /dev/zram0  
✅ Proceed to Task 5A.4

---

## NEXT TASK
→ Task 5A.4: Execute Stress Test

---

**Documentation**: XNAi Phase 5A Memory Optimization  
**Date**: 2026-02-12  
**Created by**: Copilot-Haiku during Phase 5A execution
