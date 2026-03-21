# TASK 5A.2: Apply Kernel Parameters
## Objective
Configure kernel memory management tunables for aggressive zRAM usage

**Tier**: 3 (Task Module)  
**Duration**: 15 minutes  
**Prerequisites**: Task 5A.1 baseline collected  
**Tools required**: `sysctl`, `sudo` privileges

---

## CURRENT STATE
```
vm.swappiness = 10           (default: 60, old config: 35)
vm.page-cluster = 3          (default: 3)
vm.watermark_boost_factor = 15000  (default: 15000)
vm.vfs_cache_pressure = 100  (default: 100)
```

## TARGET STATE
```
vm.swappiness = 180          (aggressive zRAM usage)
vm.page-cluster = 0          (single-page swap for zRAM latency)
vm.watermark_boost_factor = 0     (disable boost)
vm.watermark_scale_factor = 125   (aggressive memory reclaim)
vm.vfs_cache_pressure = 50   (preserve filesystem cache)
vm.dirty_ratio = 40          (reduce writeback frequency)
vm.dirty_background_ratio = 20
```

---

## PROCEDURE

### Method 1: Persistent Configuration (Recommended)

**Step 1: Create sysctl configuration file**
```bash
sudo tee /etc/sysctl.d/99-xnai-zram-tuning.conf > /dev/null << 'EOF'
# XNAi zRAM Memory Optimization
# Applied: Phase 5A Task 5A.2
# Purpose: Aggressive zRAM usage for memory-constrained systems

vm.swappiness = 180
vm.page-cluster = 0
vm.watermark_boost_factor = 0
vm.watermark_scale_factor = 125
vm.vfs_cache_pressure = 50
vm.dirty_ratio = 40
vm.dirty_background_ratio = 20
vm.overcommit_memory = 0
vm.overcommit_ratio = 50
EOF
```

**Step 2: Apply configuration**
```bash
# Reload sysctl configuration
sudo sysctl -p /etc/sysctl.d/99-xnai-zram-tuning.conf

# Verify (should show all 180, 0, 0, 125, 50, etc.)
sysctl vm.swappiness vm.page-cluster vm.watermark_boost_factor
```

**Step 3: Verify Applied**
```bash
# Check each parameter
cat /proc/sys/vm/swappiness           # Should be 180
cat /proc/sys/vm/page-cluster         # Should be 0
cat /proc/sys/vm/watermark_boost_factor # Should be 0
```

### Method 2: Temporary (for testing)

If you need to test without persistence:
```bash
sudo sysctl -w vm.swappiness=180
sudo sysctl -w vm.page-cluster=0
sudo sysctl -w vm.watermark_boost_factor=0
sudo sysctl -w vm.watermark_scale_factor=125
```

**Note**: These revert on system reboot. Use Method 1 for permanent configuration.

---

## VALIDATION CHECKLIST

- [ ] `/etc/sysctl.d/99-xnai-zram-tuning.conf` created
- [ ] `sysctl -p` executed successfully
- [ ] `vm.swappiness = 180` confirmed
- [ ] `vm.page-cluster = 0` confirmed
- [ ] `vm.watermark_boost_factor = 0` confirmed
- [ ] No sysctl errors on reload

---

## TROUBLESHOOTING

### Issue: "Permission denied" on sysctl -w
**Solution**: Use `sudo sysctl -w` instead
```bash
sudo sysctl -w vm.swappiness=180
```

### Issue: Parameter not in system
**Solution**: Check kernel version - ensure 5.10+ (check with `uname -r`)
```bash
uname -r  # Should show 5.10 or later
```

### Issue: Setting not persistent after reboot
**Solution**: Verify `/etc/sysctl.d/99-xnai-zram-tuning.conf` exists
```bash
cat /etc/sysctl.d/99-xnai-zram-tuning.conf
```

---

## SUCCESS CRITERIA

✅ All 5 parameters applied to running system  
✅ Values persist across system reboot  
✅ No errors in `sysctl -p` output  
✅ Proceed to Task 5A.3

---

## NEXT TASK
→ Task 5A.3: Configure zRAM Device

---

**Documentation**: XNAi Phase 5A Memory Optimization  
**Date**: 2026-02-12  
**Created by**: Copilot-Haiku during Phase 5A execution
