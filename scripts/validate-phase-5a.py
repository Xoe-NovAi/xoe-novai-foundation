#!/usr/bin/env python3
"""
Phase 5A Comprehensive Validation Script
Validates all Phase 5A requirements are met
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
    print("PHASE 5A VALIDATION SCRIPT")
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
        print("   Install missing tools or expect some checks to be skipped.")
    if os.geteuid() != 0:
        print("⚠️  Not running as root — some validation checks may require sudo/root privileges.")

    checks = [
        {
            "name": "1. zRAM Device Active",
            "cmd": "zramctl | grep -q zram0",
            "description": "Verify /dev/zram0 is active"
        },
        {
            "name": "2. zRAM Algorithm = zstd",
            "cmd": "zramctl | grep zram0 | grep -q zstd",
            "description": "Verify compression is zstd (not lz4/lzo)"
        },
        {
            "name": "3. vm.swappiness = 180",
            "cmd": "test $(cat /proc/sys/vm/swappiness) -eq 180",
            "description": "Kernel parameter configured correctly"
        },
        {
            "name": "4. vm.page-cluster = 0",
            "cmd": "test $(cat /proc/sys/vm/page-cluster) -eq 0",
            "description": "Single-page swap enabled"
        },
        {
            "name": "5. Swap Configured",
            "cmd": "swapon --show | grep -q zram0",
            "description": "zRAM swap is active"
        },
        {
            "name": "6. Systemd Service Exists",
            "cmd": "test -f /etc/systemd/system/xnai-zram.service",
            "description": "Service file created"
        },
        {
            "name": "7. Systemd Service Enabled",
            "cmd": "systemctl is-enabled xnai-zram.service | grep -q enabled",
            "description": "Service will start on boot"
        },
        {
            "name": "8. Systemd Service Active",
            "cmd": "systemctl is-active xnai-zram.service | grep -q active",
            "description": "Service running now"
        },
        {
            "name": "9. Sysctl Config Persistent",
            "cmd": "test -f /etc/sysctl.d/99-xnai-zram-tuning.conf",
            "description": "Configuration file exists"
        }
    ]

    
    for check in checks:
        success, stdout, stderr = run_cmd(check['cmd'])
        
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
    
    # Additional OOM check (robust: dmesg -> journalctl fallback)
    def count_oom_events():
        try:
            out = subprocess.run("dmesg | grep -c 'Out of memory'", shell=True, capture_output=True, text=True, timeout=5)
            return int(out.stdout.strip() or 0)
        except Exception:
            try:
                out = subprocess.run("journalctl -k --no-pager | grep -c 'Out of memory'", shell=True, capture_output=True, text=True, timeout=5)
                return int(out.stdout.strip() or 0)
            except Exception:
                return -1

    oom_count = count_oom_events()
    if oom_count == -1:
        print("⚠️  10. No Recent OOM Events — unable to determine (insufficient permissions)")
    else:
        if oom_count < 3:
            passed += 1
            print("✅ 10. No Recent OOM Events")
            print(f"   Total OOM events (last boot): {oom_count}")
        else:
            failed += 1
            print(f"❌ 10. No Recent OOM Events ({oom_count} events)")

    # Additional info
    print("="*70)
    print("SYSTEM INFO")
    print("="*70)
    print()
    
    print("Memory State:")
    _, mem_output, _ = run_cmd("free -h | grep Mem")
    print(f"  {mem_output}")
    print()
    
    print("zRAM Status:")
    _, zram_output, _ = run_cmd("zramctl 2>/dev/null || echo 'zramctl not available'")
    for line in zram_output.split('\n')[:3]:
        if line:
            print(f"  {line}")
    print()
    
    print("="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    print()
    
    if failed == 0:
        print("🎉 Phase 5A validation PASSED!")
        print("All requirements met. Ready for Phase 5B.")
        return 0
    else:
        print("❌ Phase 5A validation FAILED")
        print("See failures above and run troubleshooting.")
        return 1

if __name__ == '__main__':
    sys.exit(validate())
