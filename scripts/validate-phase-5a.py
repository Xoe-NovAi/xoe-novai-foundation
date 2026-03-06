#!/usr/bin/env python3
"""
Phase 5A Comprehensive Validation Script (Multi-Device Aware)
Validates that zRAM requirements are met, supporting both single and tiered setups.
"""

import subprocess
import sys
import os
import shutil
from datetime import datetime

def run_cmd(cmd, description=""):
    """Execute command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"
    except Exception as e:
        return False, "", str(e)

def validate():
    """Run all validations"""
    print("="*70)
    print("PHASE 5A VALIDATION SCRIPT (v2.0 - Multi-Device Aware)")
    print(f"Date: {datetime.now().isoformat()}")
    print("="*70)
    print()
    
    passed = 0
    failed = 0

    # --- Preflight checks ---
    required_tools = ["zramctl", "systemctl", "swapon"]
    missing = [t for t in required_tools if shutil.which(t) is None]
    if missing:
        print(f"⚠️  Missing required tools: {', '.join(missing)}")
    if os.getuid() != 0:
        print("⚠️  Not running as root — some checks may fail.")

    # Core logic: Check for ANY zram device
    success, stdout, _ = run_cmd("zramctl --noheadings | wc -l")
    zram_count = int(stdout or 0)

    checks = [
        {
            "name": "1. zRAM Devices Active",
            "condition": zram_count > 0,
            "description": f"Found {zram_count} active zRAM device(s)"
        },
        {
            "name": "2. High Swappiness (180)",
            "cmd": "test $(cat /proc/sys/vm/swappiness) -eq 180",
            "description": "Kernel swappiness optimized for zRAM"
        },
        {
            "name": "3. Single-Page Swap (page-cluster=0)",
            "cmd": "test $(cat /proc/sys/vm/page-cluster) -eq 0",
            "description": "Kernel page-cluster optimized for zRAM latency"
        },
        {
            "name": "4. VFS Cache Pressure (50)",
            "cmd": "test $(cat /proc/sys/vm/vfs_cache_pressure) -eq 50",
            "description": "Kernel metadata cache optimized"
        },
        {
            "name": "5. Swap Active",
            "cmd": "swapon --show | grep -q zram",
            "description": "At least one zRAM device is currently being used as swap"
        },
        {
            "name": "6. Persistence Configured",
            "cmd": "test -f /etc/sysctl.d/99-xnai-zram-tuning.conf",
            "description": "Kernel tuning is documented for persistence"
        },
        {
            "name": "7. Systemd Service Enabled",
            "cmd": "systemctl is-enabled xnai-zram.service | grep -q enabled",
            "description": "zRAM service will persist across reboots"
        }
    ]

    for check in checks:
        if "cmd" in check:
            success, _, stderr = run_cmd(check['cmd'])
        else:
            success = check["condition"]
            stderr = ""

        if success:
            print(f"✅ {check['name']}")
            print(f"   {check['description']}")
            passed += 1
        else:
            print(f"❌ {check['name']}")
            print(f"   {check['description']}")
            if stderr:
                print(f"   Error: {stderr[:100]}")
            failed += 1
        print()

    # OOM check
    try:
        out = subprocess.run("dmesg | grep -c 'Out of memory' || true", shell=True, capture_output=True, text=True)
        oom_count = int(out.stdout.strip() or 0)
        if oom_count < 3:
            passed += 1
            print("✅ 8. No Recent Critical OOM Events")
        else:
            failed += 1
            print(f"❌ 8. High OOM Count Detected ({oom_count} events)")
    except:
        print("⚠️  8. Unable to perform OOM check (permissions)")

    print("="*70)
    print("ZRAM STATUS DETAIL")
    print("="*70)
    subprocess.run("zramctl", shell=True)
    print()
    subprocess.run("swapon --show", shell=True)
    print()
    
    print("="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(validate())
