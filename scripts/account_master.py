#!/usr/bin/env python3
"""
Account Master
==============
Modular multi-account rotation and observability engine.
Manages 8 Antigravity/OpenCode accounts for quota optimization.
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

CONFIG_DIR = os.path.expanduser("~/.config/xnai")
QUOTA_FILE = os.path.join(CONFIG_DIR, "account_quotas.json")

# Account definitions (01-08)
ACCOUNTS = [f"{i:02d}" for i in range(1, 9)]

def init_config():
    """Initialize configuration."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(QUOTA_FILE):
        # Initialize with default structure
        data = {acc: {"used": 0, "limit": 50000, "reset": None} for acc in ACCOUNTS}
        save_config(data)

def load_config():
    """Load quota configuration."""
    with open(QUOTA_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    """Save quota configuration."""
    with open(QUOTA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_best_account(provider="antigravity"):
    """Get the account with the most available quota."""
    data = load_config()
    best_acc = None
    max_remaining = -1
    
    for acc in ACCOUNTS:
        usage = data.get(acc, {"used": 0, "limit": 50000})
        remaining = usage["limit"] - usage["used"]
        
        if remaining > max_remaining:
            max_remaining = remaining
            best_acc = acc
            
    return best_acc, max_remaining

def update_usage(account, amount):
    """Update usage for an account."""
    data = load_config()
    if account in data:
        data[account]["used"] += amount
        data[account]["last_used"] = datetime.utcnow().isoformat()
        save_config(data)
        print(f"Account {account} usage updated: +{amount}")
    else:
        print(f"Error: Account {account} not found.")

def happy_hour_check():
    """Check if it's Happy Hour (8AM - 2PM ET)."""
    # 8AM ET = 12PM UTC (Standard) or 1PM UTC (Daylight)
    # 2PM ET = 6PM UTC or 7PM UTC
    # Approximate check
    now = datetime.utcnow()
    hour = now.hour
    if 12 <= hour < 18:
        print("Happy Hour Active! Quotas are DOUBLED.")
        return True
    return False

if __name__ == "__main__":
    init_config()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "best":
            acc, rem = get_best_account()
            print(f"Recommended Account: {acc} ({rem} tokens remaining)")
        elif cmd == "update":
            acc = sys.argv[2]
            amt = int(sys.argv[3])
            update_usage(acc, amt)
        elif cmd == "happy":
            happy_hour_check()
    else:
        # Status Report
        data = load_config()
        print("ACCOUNT STATUS REPORT")
        print("=====================")
        for acc in ACCOUNTS:
            u = data.get(acc, {})
            print(f"Account {acc}: {u.get('used', 0)}/{u.get('limit', 50000)}")
