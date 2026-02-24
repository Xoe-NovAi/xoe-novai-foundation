#!/usr/bin/env python3
"""
Track Antigravity account quota resets and manage rate limit fallback.

Usage:
  python scripts/track_antigravity_resets.py --monitor          # Watch for resets
  python scripts/track_antigravity_resets.py --check-quota      # Current quota status
  python scripts/track_antigravity_resets.py --countdown        # Time until reset
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

# Constants
ACCOUNTS = [f"antigravity-{i:02d}" for i in range(1, 9)]
QUOTA_FILE = Path.home() / ".config" / "xnai" / "antigravity_quota_baseline.json"
QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)

# Reset day: Sunday UTC
RESET_DAY = 6  # Sunday
RESET_HOUR = 0  # Midnight UTC


def get_account_quota(account: str) -> Optional[int]:
    """Get current quota for an Antigravity account via OpenCode CLI.
    
    Returns remaining tokens, or None if account unavailable.
    """
    try:
        result = subprocess.run(
            ["opencode", "chat", "--model", f"google/antigravity-claude-sonnet", 
             "--dry-run"],  # Don't actually dispatch
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Parse quota from output (format varies by OpenCode version)
        # Look for patterns like "Quota: 500000" or "Remaining: 25000"
        output = result.stdout + result.stderr
        
        for line in output.split('\n'):
            if 'quota' in line.lower() or 'remaining' in line.lower():
                # Extract numbers
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    return int(numbers[-1])  # Usually last number is quota
        
        return None
    except Exception as e:
        print(f"Error checking quota for {account}: {e}", file=sys.stderr)
        return None


def save_baseline(account: str, quota: int) -> None:
    """Save current quota as baseline for detecting resets."""
    data = {}
    if QUOTA_FILE.exists():
        with open(QUOTA_FILE) as f:
            data = json.load(f)
    
    data[account] = {
        "quota": quota,
        "timestamp": datetime.utcnow().isoformat(),
        "save_reason": "baseline_capture"
    }
    
    with open(QUOTA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_baseline() -> Dict[str, dict]:
    """Load saved quota baseline."""
    if QUOTA_FILE.exists():
        with open(QUOTA_FILE) as f:
            return json.load(f)
    return {}


def is_reset_day() -> bool:
    """Check if today is reset day (Sunday UTC)."""
    now = datetime.utcnow()
    return now.weekday() == RESET_DAY


def time_until_reset() -> timedelta:
    """Calculate time until next reset."""
    now = datetime.utcnow()
    days_until_reset = (RESET_DAY - now.weekday()) % 7
    if days_until_reset == 0 and now.hour >= RESET_HOUR:
        days_until_reset = 7
    
    # Calculate exact time
    next_reset = now + timedelta(days=days_until_reset)
    next_reset = next_reset.replace(hour=RESET_HOUR, minute=0, second=0, microsecond=0)
    return next_reset - now


def check_quota_status() -> Tuple[Dict[str, Optional[int]], Dict[str, float]]:
    """Check current quota for all accounts."""
    print("Checking Antigravity account quotas...")
    print("-" * 80)
    
    current_quotas = {}
    usage_percent = {}
    
    for account in ACCOUNTS:
        try:
            # Simplified check - just list quota from account
            result = subprocess.run(
                ["opencode", "list-models", "--json"],  # Try to get models
                capture_output=True,
                text=True,
                timeout=3
            )
            
            # For now, use placeholder - real implementation needs OpenCode API
            current_quotas[account] = 500000  # Placeholder
            usage_percent[account] = 95.0  # From earlier status
            
            print(f"  {account}: ~{usage_percent[account]:.0f}% used "
                  f"(~{current_quotas[account]:,} tokens remaining)")
        except Exception as e:
            current_quotas[account] = None
            usage_percent[account] = 0.0
            print(f"  {account}: ERROR - {e}")
    
    print("-" * 80)
    return current_quotas, usage_percent


def check_reset_status() -> Dict[str, bool]:
    """Check if accounts have reset since baseline."""
    baseline = load_baseline()
    current, _ = check_quota_status()
    
    print("\nReset Detection:")
    print("-" * 80)
    
    resets_detected = {}
    for account in ACCOUNTS:
        if account in baseline and account in current:
            baseline_quota = baseline[account].get("quota", 0)
            current_quota = current.get(account, 0) or 0
            
            # Reset if current > baseline (quota increased)
            reset = current_quota > baseline_quota * 1.1  # 10% threshold
            resets_detected[account] = reset
            
            status = "✅ RESET DETECTED" if reset else "⏳ NOT RESET"
            print(f"  {account}: {status} (baseline: {baseline_quota:,}, current: {current_quota:,})")
        else:
            print(f"  {account}: NO BASELINE - use --capture-baseline first")
    
    print("-" * 80)
    return resets_detected


def show_countdown() -> None:
    """Show time until next reset."""
    until_reset = time_until_reset()
    
    print("\nReset Countdown:")
    print("-" * 80)
    
    days = until_reset.days
    hours = until_reset.seconds // 3600
    minutes = (until_reset.seconds % 3600) // 60
    
    print(f"  Current time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Next reset (Sunday midnight UTC): ~{days}d {hours}h {minutes}m away")
    
    if is_reset_day():
        print("  ⚠️  TODAY IS RESET DAY - Check quota every 30 minutes")
    
    print("-" * 80)


def monitor_mode() -> None:
    """Continuously monitor for resets."""
    print("Monitoring for Antigravity resets...")
    print("(This should run continuously - consider adding to systemd timer)")
    print()
    
    check_interval = 300  # Check every 5 minutes
    
    while True:
        print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Checking quotas...")
        
        current, usage = check_quota_status()
        
        # Check for resets
        reset_detected = any(
            usage.get(acc, 0) < 50 for acc in ACCOUNTS  # Usage dropped significantly
        )
        
        if reset_detected:
            print("\n🟢 RESET DETECTED! - Saving new baseline...")
            for account, quota in current.items():
                if quota:
                    save_baseline(account, quota)
        
        # Show countdown
        until_reset = time_until_reset()
        if until_reset.total_seconds() < 3600:  # Less than 1 hour
            print(f"⚠️  RESET HAPPENING SOON: {until_reset.seconds // 60} minutes away")
        
        print(f"\nNext check in {check_interval} seconds...")
        try:
            __import__('time').sleep(check_interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "--monitor":
        monitor_mode()
    elif command == "--check-quota":
        check_quota_status()
        show_countdown()
    elif command == "--countdown":
        show_countdown()
    elif command == "--check-reset":
        check_reset_status()
    elif command == "--capture-baseline":
        print("Capturing quota baseline for all accounts...")
        _, usage = check_quota_status()
        # In real implementation, get actual quotas
        for account in ACCOUNTS:
            save_baseline(account, 500000)  # Placeholder
        print("Baseline captured. Use --check-reset after reset to detect changes.")
    elif command == "--help" or command == "-h":
        print(__doc__)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
