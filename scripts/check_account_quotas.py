#!/usr/bin/env python3
"""
Multi-Account Quota Monitoring Script
=====================================

This script integrates with Omega-Stack's multi-account infrastructure
to monitor and validate account quotas for CI/CD pipeline usage.

Usage:
    python scripts/check_account_quotas.py --provider antigravity --accounts 01-08
    python scripts/check_account_quotas.py --provider copilot --accounts 01-08
    python scripts/check_account_quotas.py --all
"""

import argparse
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class AccountQuotaChecker:
    """Monitor and validate account quotas across multiple providers."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "xnai"
        self.quota_files = {
            "antigravity": self.config_dir / "antigravity-quota.yaml",
            "copilot": self.config_dir / "copilot-usage.json"
        }
        
    def check_antigravity_quotas(self, accounts: List[str]) -> Dict[str, Dict]:
        """Check Antigravity account quotas."""
        print("🔍 Checking Antigravity account quotas...")
        
        results = {}
        
        # Load quota data
        quota_file = self.quota_files["antigravity"]
        if not quota_file.exists():
            print(f"⚠️  Antigravity quota file not found: {quota_file}")
            return results
            
        try:
            import yaml
            with open(quota_file, 'r') as f:
                quota_data = yaml.safe_load(f)
        except ImportError:
            print("⚠️  PyYAML not installed, cannot read YAML quota file")
            return results
        except Exception as e:
            print(f"⚠️  Error reading Antigravity quota file: {e}")
            return results
        
        # Check each account
        for account in accounts:
            account_id = f"antigravity-{account.zfill(2)}"
            
            if account_id in quota_data.get("accounts", {}):
                account_data = quota_data["accounts"][account_id]
                tokens_used = account_data.get("tokens_used", 0)
                tokens_available = 500000 - tokens_used  # 500K weekly limit
                
                status = "🟢 OK" if tokens_available > 50000 else "🟡 LOW" if tokens_available > 10000 else "🔴 CRITICAL"
                
                results[account_id] = {
                    "status": status,
                    "tokens_used": tokens_used,
                    "tokens_available": tokens_available,
                    "usage_percent": round((tokens_used / 500000) * 100, 1),
                    "reset_time": self._calculate_reset_time(account_id)
                }
                
                print(f"  {account_id}: {status} - {tokens_available:,}/{500000:,} tokens available ({results[account_id]['usage_percent']}% used)")
            else:
                results[account_id] = {
                    "status": "⚪ UNKNOWN",
                    "tokens_used": 0,
                    "tokens_available": 500000,
                    "usage_percent": 0,
                    "reset_time": self._calculate_reset_time(account_id)
                }
                print(f"  {account_id}: ⚪ UNKNOWN - No data available")
        
        return results
    
    def check_copilot_quotas(self, accounts: List[str]) -> Dict[str, Dict]:
        """Check Copilot account quotas."""
        print("🔍 Checking Copilot account quotas...")
        
        results = {}
        
        # Load usage data
        usage_file = self.quota_files["copilot"]
        if not usage_file.exists():
            print(f"⚠️  Copilot usage file not found: {usage_file}")
            return results
            
        try:
            with open(usage_file, 'r') as f:
                usage_data = json.load(f)
        except Exception as e:
            print(f"⚠️  Error reading Copilot usage file: {e}")
            return results
        
        # Check each account
        for account in accounts:
            account_id = f"copilot-{account.zfill(2)}"
            
            if account_id in usage_data.get("accounts", {}):
                account_data = usage_data["accounts"][account_id]
                messages_used = account_data.get("messages", {}).get("used", 0)
                messages_available = 50 - messages_used  # 50 messages per account
                
                status = "🟢 OK" if messages_available > 10 else "🟡 LOW" if messages_available > 5 else "🔴 CRITICAL"
                
                results[account_id] = {
                    "status": status,
                    "messages_used": messages_used,
                    "messages_available": messages_available,
                    "usage_percent": round((messages_used / 50) * 100, 1),
                    "reset_time": "2026-03-01 (Monthly)"
                }
                
                print(f"  {account_id}: {status} - {messages_available}/{50} messages available ({results[account_id]['usage_percent']}% used)")
            else:
                results[account_id] = {
                    "status": "⚪ UNKNOWN",
                    "messages_used": 0,
                    "messages_available": 50,
                    "usage_percent": 0,
                    "reset_time": "2026-03-01 (Monthly)"
                }
                print(f"  {account_id}: ⚪ UNKNOWN - No data available")
        
        return results
    
    def _calculate_reset_time(self, account_id: str) -> str:
        """Calculate next reset time for Antigravity account."""
        # Antigravity resets on Sunday
        now = datetime.now()
        days_until_sunday = (6 - now.weekday()) % 7
        if days_until_sunday == 0 and now.hour >= 0:  # After Sunday 00:00 UTC
            days_until_sunday = 7
            
        reset_date = now + timedelta(days=days_until_sunday)
        return f"{reset_date.strftime('%Y-%m-%d')} (Sunday)"
    
    def validate_quotas_for_ci(self, provider: str, accounts: List[str]) -> bool:
        """Validate that accounts have sufficient quota for CI pipeline."""
        print(f"\n✅ Validating quotas for {provider.upper()} CI usage...")
        
        if provider == "antigravity":
            results = self.check_antigravity_quotas(accounts)
        elif provider == "copilot":
            results = self.check_copilot_quotas(accounts)
        else:
            print(f"❌ Unknown provider: {provider}")
            return False
        
        # Check for critical accounts
        critical_accounts = [acc for acc, data in results.items() 
                           if data["status"] == "🔴 CRITICAL"]
        
        if critical_accounts:
            print(f"\n⚠️  CRITICAL: {len(critical_accounts)} account(s) have critically low quota:")
            for acc in critical_accounts:
                print(f"   - {acc}: {results[acc]['status']}")
            return False
        
        # Check for low accounts
        low_accounts = [acc for acc, data in results.items() 
                       if data["status"] == "🟡 LOW"]
        
        if low_accounts:
            print(f"\n⚠️  WARNING: {len(low_accounts)} account(s) have low quota:")
            for acc in low_accounts:
                print(f"   - {acc}: {results[acc]['status']}")
        
        # Check for available accounts
        available_accounts = [acc for acc, data in results.items() 
                            if data["status"] in ["🟢 OK", "⚪ UNKNOWN"]]
        
        if available_accounts:
            print(f"\n✅ SUCCESS: {len(available_accounts)} account(s) available for CI:")
            for acc in available_accounts[:3]:  # Show first 3
                print(f"   - {acc}: {results[acc]['status']}")
            if len(available_accounts) > 3:
                print(f"   ... and {len(available_accounts) - 3} more")
        
        return len(available_accounts) > 0
    
    def generate_summary_report(self) -> Dict:
        """Generate a summary report of all account quotas."""
        print("\n📊 Generating comprehensive quota summary...")
        
        all_results = {}
        
        # Check all providers
        for provider in ["antigravity", "copilot"]:
            if provider == "antigravity":
                accounts = [f"{i:02d}" for i in range(1, 9)]  # 01-08
                results = self.check_antigravity_quotas(accounts)
            else:
                accounts = [f"{i:02d}" for i in range(1, 9)]  # 01-08
                results = self.check_copilot_quotas(accounts)
            
            all_results[provider] = results
        
        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "providers": {}
        }
        
        for provider, results in all_results.items():
            total_accounts = len(results)
            ok_accounts = len([r for r in results.values() if r["status"] == "🟢 OK"])
            low_accounts = len([r for r in results.values() if r["status"] == "🟡 LOW"])
            critical_accounts = len([r for r in results.values() if r["status"] == "🔴 CRITICAL"])
            unknown_accounts = len([r for r in results.values() if r["status"] == "⚪ UNKNOWN"])
            
            summary["providers"][provider] = {
                "total_accounts": total_accounts,
                "ok_accounts": ok_accounts,
                "low_accounts": low_accounts,
                "critical_accounts": critical_accounts,
                "unknown_accounts": unknown_accounts,
                "health_status": "HEALTHY" if critical_accounts == 0 else "WARNING" if low_accounts > 0 else "CRITICAL"
            }
        
        return summary

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check account quotas for CI/CD pipeline")
    parser.add_argument("--provider", choices=["antigravity", "copilot"], 
                       help="Provider to check quotas for")
    parser.add_argument("--accounts", 
                       help="Account range (e.g., 01-08) or comma-separated list")
    parser.add_argument("--all", action="store_true", 
                       help="Check all providers and accounts")
    parser.add_argument("--ci-validation", action="store_true",
                       help="Validate quotas for CI pipeline usage")
    parser.add_argument("--json", action="store_true",
                       help="Output results in JSON format")
    
    args = parser.parse_args()
    
    checker = AccountQuotaChecker()
    
    if args.all:
        # Generate comprehensive summary
        summary = checker.generate_summary_report()
        
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n📈 Quota Summary Report ({summary['timestamp']})")
            print("=" * 60)
            
            for provider, data in summary["providers"].items():
                print(f"\n{provider.upper()} Accounts:")
                print(f"  Total: {data['total_accounts']}")
                print(f"  OK: {data['ok_accounts']} 🟢")
                print(f"  Low: {data['low_accounts']} 🟡")
                print(f"  Critical: {data['critical_accounts']} 🔴")
                print(f"  Unknown: {data['unknown_accounts']} ⚪")
                print(f"  Status: {data['health_status']}")
        
        # Exit with appropriate code
        critical_total = sum(data['critical_accounts'] for data in summary["providers"].values())
        if critical_total > 0:
            sys.exit(1)  # Critical accounts found
        else:
            sys.exit(0)
    
    elif args.provider and args.accounts:
        # Parse account list
        if '-' in args.accounts:
            start, end = args.accounts.split('-')
            accounts = [f"{i:02d}" for i in range(int(start), int(end) + 1)]
        else:
            accounts = args.accounts.split(',')
        
        # Validate for CI or check specific accounts
        if args.ci_validation:
            success = checker.validate_quotas_for_ci(args.provider, accounts)
            sys.exit(0 if success else 1)
        else:
            if args.provider == "antigravity":
                results = checker.check_antigravity_quotas(accounts)
            else:
                results = checker.check_copilot_quotas(accounts)
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"\n✅ Quota check completed for {args.provider} accounts: {', '.join(accounts)}")
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()