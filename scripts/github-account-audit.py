#!/usr/bin/env python3
"""
XNAi GitHub Multi-Account Audit Script - ENHANCED VERSION

Enhanced with:
- Copilot message/completion tracking
- Account rotation recommendations
- Multi-provider integration
- Split test coordination

Usage:
    python3 scripts/github-account-audit.py
    python3 scripts/github-account-audit.py --copilot
    python3 scripts/github-account-audit.py --recommend

Author: XNAi Foundation
Date: 2026-02-26
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


class GitHubAccount:
    """Represents a GitHub account with full usage tracking."""

    def __init__(self, email: str, gh_host: str = "github.com"):
        self.email: str = email
        self.gh_host: str = gh_host
        self.username: Optional[str] = None
        self.rate_limit: Optional[Dict[str, Any]] = None
        self.copilot_usage: Optional[Dict[str, Any]] = None
        self.reset_date: Optional[str] = None
        self.remaining: int = 0
        self.limit: int = 0
        self.used: int = 0
        self.authenticated: bool = False
        self.last_check: Optional[str] = None
        self.daily_driver: bool = False
        self.role: str = "contributor"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "gh_host": self.gh_host,
            "username": self.username,
            "authenticated": self.authenticated,
            "rate_limit": self.rate_limit,
            "remaining": self.remaining,
            "limit": self.limit,
            "used": self.used,
            "reset_date": self.reset_date,
            "copilot_usage": self.copilot_usage,
            "last_check": self.last_check,
            "daily_driver": self.daily_driver,
            "role": self.role,
        }


class GitHubAccountAuditor:
    """Enhanced auditor with Copilot and rotation support."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "memory_bank/usage/github-accounts.yaml"
        self.accounts: List[GitHubAccount] = []
        self.results: Dict[str, Any] = {}

    def load_accounts(self) -> List[GitHubAccount]:
        """Load accounts from YAML config."""
        accounts = []

        # Try to load from YAML config
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                import yaml

                with open(config_file) as f:
                    config = yaml.safe_load(f)
                    for acc in config.get("accounts", []):
                        email = acc.get("email", "")
                        if email:
                            gh_acc = GitHubAccount(email=email)
                            gh_acc.role = acc.get("role", "contributor")
                            gh_acc.daily_driver = acc.get("daily_driver", False)

                            # Load Copilot usage if available
                            copilot = acc.get("copilot", {})
                            gh_acc.copilot_usage = {
                                "messages_used": copilot.get("messages_used", 0),
                                "messages_limit": copilot.get("messages_limit", 50),
                                "messages_remaining": copilot.get("messages_remaining", 50),
                                "completions_used": copilot.get("completions_used", 0),
                                "completions_limit": copilot.get("completions_limit", 2000),
                                "reset_date": copilot.get("reset_date", "2026-03-01"),
                            }
                            accounts.append(gh_acc)
            except ImportError:
                pass

        return accounts

    def check_authenticated_accounts(self) -> List[GitHubAccount]:
        """Get currently authenticated accounts via gh CLI."""
        accounts = []

        try:
            # Get authenticated users
            result = subprocess.run(["gh", "api", "user"], capture_output=True, text=True)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                gh_acc = GitHubAccount(email=f"{data.get('login')}@github.com")
                gh_acc.username = data.get("login")
                gh_acc.authenticated = True
                accounts.append(gh_acc)

        except Exception:
            pass

        return accounts

    async def check_rate_limit(self, account: GitHubAccount) -> Dict[str, Any]:
        """Check API rate limit."""
        try:
            result = subprocess.run(["gh", "api", "rate_limit"], capture_output=True, text=True)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                resources = data.get("resources", {})
                core = resources.get("core", {})

                account.limit = core.get("limit", 5000)
                account.remaining = core.get("remaining", 5000)
                account.used = account.limit - account.remaining

                reset_timestamp = core.get("reset", 0)
                if reset_timestamp:
                    account.reset_date = datetime.fromtimestamp(reset_timestamp, tz=timezone.utc).isoformat()

                return {
                    "limit": account.limit,
                    "remaining": account.remaining,
                    "used": account.used,
                    "reset": account.reset_date,
                }
        except Exception:
            pass

        return {"error": "Could not check rate limit"}

    def audit_all(self) -> Dict[str, Any]:
        """Run full audit on all accounts."""
        self.accounts = self.load_accounts()

        results = {
            "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_accounts": len(self.accounts),
            "accounts": [],
            "recommendations": [],
        }

        for account in self.accounts:
            checked = self.check_account(account)
            results["accounts"].append(checked.to_dict())

        # Generate recommendations
        results["recommendations"] = self.generate_recommendations()

        # Summary
        total_copilot_remaining = sum(a.copilot_usage.get("messages_remaining", 0) for a in self.accounts if a.copilot_usage)

        results["summary"] = {
            "total_copilot_remaining": total_copilot_remaining,
            "total_api_remaining": sum(a.remaining for a in self.accounts),
            "ready_for_split_test": total_copilot_remaining >= 25,
        }

        self.results = results
        return results

    def check_account(self, account: GitHubAccount) -> GitHubAccount:
        """Check a single account."""
        account.last_check = datetime.now(timezone.utc).isoformat()

        # Check authentication
        try:
            result = subprocess.run(["gh", "api", "user"], capture_output=True, text=True)
            if result.returncode == 0:
                user_data = json.loads(result.stdout)
                account.username = user_data.get("login")
                account.authenticated = True
        except Exception:
            pass

        return account

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate account usage recommendations."""
        recommendations = []

        # Check for accounts with low quota
        for account in self.accounts:
            if account.copilot_usage:
                remaining = account.copilot_usage.get("messages_remaining", 0)
                limit = account.copilot_usage.get("messages_limit", 50)
                percent = (remaining / limit * 100) if limit > 0 else 0

                if percent < 20:
                    recommendations.append(
                        {
                            "type": "warning",
                            "account": account.email,
                            "message": f"Low quota: {remaining}/{limit} ({percent:.0f}%)",
                            "action": "Switch to account with more quota",
                        }
                    )

        # Recommend split test account
        best_account = self.get_best_account_for_split_test()
        if best_account:
            recommendations.append(
                {
                    "type": "info",
                    "account": best_account.email,
                    "message": "Best account for split test",
                    "action": f"Use: gh auth switch --user {best_account.username or best_account.email}",
                }
            )

        return recommendations

    def get_best_account_for_split_test(self) -> Optional[GitHubAccount]:
        """Get best account for split test."""
        available = [a for a in self.accounts if a.copilot_usage and a.copilot_usage.get("messages_remaining", 0) >= 25]

        if not available:
            return None

        # Prefer non-daily-driver for testing
        non_driver = [a for a in available if not a.daily_driver]
        if non_driver:
            return max(non_driver, key=lambda a: a.copilot_usage.get("messages_remaining", 0) if a.copilot_usage else 0)

        return max(available, key=lambda a: a.copilot_usage.get("messages_remaining", 0) if a.copilot_usage else 0)

    def print_report(self, verbose: bool = False):
        """Print audit report."""
        print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════{RESET}")
        print(f"{BOLD}{CYAN}     XNAi GitHub Multi-Account Audit Report (Enhanced){RESET}")
        print(f"{BOLD}{CYAN}     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
        print(f"{BOLD}{CYAN}═══════════════════════════════════════════════════════{RESET}\n")

        # Ensure audit has run
        if not self.accounts:
            self.accounts = self.load_accounts()
            self.audit_all()

        # Calculate summary from loaded accounts
        total_copilot = sum(a.copilot_usage.get("messages_remaining", 0) for a in self.accounts if a.copilot_usage)

        # Summary
        print(f"{BOLD}📊 SUMMARY{RESET}")
        print(f"   Total accounts: {len(self.accounts)}")
        print(f"   Copilot remaining: {total_copilot} messages")
        print(f"   Split test ready: {'✅ YES' if total_copilot >= 25 else '❌ NO'}")
        print()

        # Account details
        print(f"{BOLD}📋 ACCOUNT DETAILS{RESET}")
        for acc in self.accounts:
            if acc.copilot_usage:
                remaining = acc.copilot_usage.get("messages_remaining", 0)
                limit = acc.copilot_usage.get("messages_limit", 50)
                percent = (remaining / limit * 100) if limit > 0 else 0

                status_icon = "🟢" if percent > 50 else "🟡" if percent > 20 else "🔴"

                print(f"\n   {status_icon} {acc.email}")
                print(f"      Copilot: {remaining}/{limit} ({percent:.0f}%)")
                print(f"      Role: {acc.role}")
                print(f"      Daily Driver: {'Yes' if acc.daily_driver else 'No'}")

        # Recommendations
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            print(f"\n{BOLD}💡 RECOMMENDATIONS{RESET}")
            for rec in recommendations:
                icon = "⚠️" if rec.get("type") == "warning" else "ℹ️"
                print(f"   {icon} {rec.get('message', '')}")
                print(f"      → {rec.get('action', '')}")

        print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════{RESET}\n")

    def save_results(self, output_path: str = "memory_bank/usage/github-audit.json"):
        """Save audit results to JSON."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(description="XNAi GitHub Multi-Account Audit Tool (Enhanced)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose")
    parser.add_argument("--copilot", action="store_true", help="Show Copilot details")
    parser.add_argument("--recommend", action="store_true", help="Show recommendations")
    parser.add_argument("--save", action="store_true", help="Save results")
    parser.add_argument("--output", default="memory_bank/usage/github-audit.json")
    parser.add_argument("--config")

    args = parser.parse_args()

    auditor = GitHubAccountAuditor(config_path=args.config)

    try:
        results = auditor.audit_all()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            auditor.print_report(verbose=args.verbose)

        if args.save or args.recommend:
            auditor.save_results(args.output)

    except KeyboardInterrupt:
        print("\nAudit cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main()) if False else main()
