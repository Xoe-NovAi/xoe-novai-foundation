"""
Account CLI Interface for XNAi RAG Stack

Provides CLI commands for managing multi-provider accounts,
including account switching, status checking, and configuration.

Author: XNAi Foundation
Version: 1.0.0
"""

import asyncio
import click
import logging
import sys
from datetime import datetime
from typing import Optional, List

from .account_manager import (
    AccountManager, AccountStatus, AccountType, AccountInfo,
    get_account_manager
)

logger = logging.getLogger(__name__)


@click.group(name="account", help="Account management commands")
def account_cli():
    """Account management CLI commands"""
    pass


@account_cli.command(name="list", help="List all accounts")
@click.option("--type", "-t", type=click.Choice(["primary", "service", "user"]), 
              help="Filter by account type")
@click.option("--status", "-s", type=click.Choice(["active", "inactive", "suspended", "expired"]),
              help="Filter by account status")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def list_accounts(type: Optional[str], status: Optional[str], verbose: bool):
    """List all accounts with optional filtering"""
    try:
        manager = asyncio.run(get_account_manager())
        accounts = asyncio.run(manager.list_accounts(
            AccountType(type) if type else None
        ))
        
        if status:
            accounts = [acc for acc in accounts if acc.status.value == status]
        
        if not accounts:
            click.echo("No accounts found")
            return
        
        click.echo(f"\nFound {len(accounts)} accounts:\n")
        
        for account in accounts:
            if verbose:
                click.echo(f"Account ID: {account.account_id}")
                click.echo(f"  Name: {account.name}")
                click.echo(f"  Type: {account.account_type.value}")
                click.echo(f"  Status: {account.status.value}")
                click.echo(f"  Provider: {account.provider}")
                click.echo(f"  Email: {account.email}")
                click.echo(f"  Priority: {account.priority}")
                click.echo(f"  Models: {', '.join(account.models_preferred)}")
                click.echo(f"  Quota: {account.quota_remaining}/{account.quota_limit} ({account.quota_percent:.1f}%)")
                click.echo(f"  Created: {account.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                click.echo(f"  Last Used: {account.last_used.strftime('%Y-%m-%d %H:%M:%S') if account.last_used else 'Never'}")
                click.echo(f"  Stats: {account.usage_stats['total_requests']} requests, {account.usage_stats['success_rate']:.1f}% success")
            else:
                quota_pct = account.quota_percent
                status_emoji = "🟢" if account.status == AccountStatus.ACTIVE else "🟡" if account.status == AccountStatus.INACTIVE else "🔴"
                click.echo(f"{status_emoji} {account.account_id:<20} {account.name:<20} {account.provider:<12} {quota_pct:>6.1f}%")
            
            click.echo()
    
    except Exception as e:
        click.echo(f"Error listing accounts: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="status", help="Show current account status")
@click.option("--account", "-a", help="Show status for specific account")
def show_status(account: Optional[str]):
    """Show current account status or status for specific account"""
    try:
        manager = asyncio.run(get_account_manager())
        
        if account:
            account_info = asyncio.run(manager.get_account_status(account))
            if not account_info:
                click.echo(f"Account not found: {account}", err=True)
                sys.exit(1)
            
            click.echo(f"\nAccount Status: {account}\n")
            click.echo(f"Name: {account_info.name}")
            click.echo(f"Type: {account_info.account_type.value}")
            click.echo(f"Status: {account_info.status.value}")
            click.echo(f"Provider: {account_info.provider}")
            click.echo(f"Email: {account_info.email}")
            click.echo(f"Priority: {account_info.priority}")
            click.echo(f"Models: {', '.join(account_info.models_preferred)}")
            click.echo(f"Quota: {account_info.quota_remaining}/{account_info.quota_limit} ({account_info.quota_percent:.1f}%)")
            click.echo(f"Created: {account_info.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"Last Used: {account_info.last_used.strftime('%Y-%m-%d %H:%M:%S') if account_info.last_used else 'Never'}")
            click.echo(f"Total Requests: {account_info.usage_stats['total_requests']}")
            click.echo(f"Success Rate: {account_info.usage_stats['success_rate']:.1f}%")
            click.echo(f"Avg Response Time: {account_info.usage_stats['avg_response_time']:.2f}s")
        else:
            current = manager.get_current_account()
            if current:
                click.echo(f"Current Account: {current.account_id}")
                click.echo(f"Name: {current.name}")
                click.echo(f"Provider: {current.provider}")
                click.echo(f"Quota: {current.quota_remaining}/{current.quota_limit} ({current.quota_percent:.1f}%)")
            else:
                click.echo("No current account set")
    
    except Exception as e:
        click.echo(f"Error showing status: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="switch", help="Switch to a different account")
@click.argument("account_id")
def switch_account(account_id: str):
    """Switch to a different account"""
    try:
        manager = asyncio.run(get_account_manager())
        success = asyncio.run(manager.switch_account(account_id))
        
        if success:
            click.echo(f"Successfully switched to account: {account_id}")
        else:
            click.echo(f"Failed to switch to account: {account_id}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error switching account: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="create", help="Create a new account")
@click.argument("name")
@click.option("--type", "-t", type=click.Choice(["primary", "service", "user"]), 
              default="user", help="Account type (default: user)")
@click.option("--email", "-e", required=True, help="Account email")
@click.option("--provider", "-p", required=True, help="Provider name")
@click.option("--quota-limit", "-q", type=int, default=500000, help="Quota limit (default: 500000)")
@click.option("--models", "-m", multiple=True, help="Preferred models")
@click.option("--priority", "-r", type=int, default=1, help="Account priority (lower = higher priority)")
def create_account(name: str, type: str, email: str, provider: str, 
                  quota_limit: int, models: List[str], priority: int):
    """Create a new account"""
    try:
        manager = asyncio.run(get_account_manager())
        account_id = asyncio.run(manager.create_account(
            name=name,
            account_type=AccountType(type),
            email=email,
            provider=provider,
            quota_limit=quota_limit,
            models_preferred=list(models),
            priority=priority
        ))
        
        click.echo(f"Successfully created account: {account_id}")
    
    except Exception as e:
        click.echo(f"Error creating account: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="recommend", help="Get recommended account for task")
@click.option("--task", "-t", type=click.Choice(["reasoning", "code", "quick", "research"]), 
              default="general", help="Task type (default: general)")
def recommend_account(task: str):
    """Get recommended account for specific task type"""
    try:
        manager = asyncio.run(get_account_manager())
        recommended = asyncio.run(manager.get_recommended_account(task))
        
        if recommended:
            click.echo(f"Recommended account for {task} tasks:")
            click.echo(f"  Account: {recommended.account_id}")
            click.echo(f"  Name: {recommended.name}")
            click.echo(f"  Provider: {recommended.provider}")
            click.echo(f"  Models: {', '.join(recommended.models_preferred)}")
            click.echo(f"  Quota: {recommended.quota_remaining}/{recommended.quota_limit} ({recommended.quota_percent:.1f}%)")
            click.echo(f"  Priority: {recommended.priority}")
        else:
            click.echo("No suitable accounts available", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error getting recommendation: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="suspend", help="Suspend an account")
@click.argument("account_id")
@click.option("--reason", "-r", help="Reason for suspension")
def suspend_account(account_id: str, reason: Optional[str]):
    """Suspend an account"""
    try:
        manager = asyncio.run(get_account_manager())
        success = asyncio.run(manager.suspend_account(account_id, reason or ""))
        
        if success:
            click.echo(f"Successfully suspended account: {account_id}")
        else:
            click.echo(f"Failed to suspend account: {account_id}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error suspending account: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="activate", help="Activate a suspended account")
@click.argument("account_id")
def activate_account(account_id: str):
    """Activate a suspended account"""
    try:
        manager = asyncio.run(get_account_manager())
        success = asyncio.run(manager.activate_account(account_id))
        
        if success:
            click.echo(f"Successfully activated account: {account_id}")
        else:
            click.echo(f"Failed to activate account: {account_id}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error activating account: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="report", help="Generate usage report")
@click.option("--format", "-f", type=click.Choice(["json", "text"]), default="text", help="Output format")
def generate_report(format: str):
    """Generate usage report for all accounts"""
    try:
        manager = asyncio.run(get_account_manager())
        report = asyncio.run(manager.get_usage_report())
        
        if format == "json":
            import json
            click.echo(json.dumps(report, indent=2, default=str))
        else:
            click.echo(f"\nAccount Usage Report\n")
            click.echo(f"Total Accounts: {report['total_accounts']}")
            click.echo(f"Active Accounts: {report['active_accounts']}")
            click.echo(f"Inactive Accounts: {report['inactive_accounts']}")
            click.echo(f"Suspended Accounts: {report['suspended_accounts']}")
            click.echo(f"Expired Accounts: {report['expired_accounts']}")
            click.echo(f"\nAccount Details:\n")
            
            for account in report['account_details']:
                quota_pct = account['quota_percent']
                click.echo(f"{account['account_id']:<20} {account['name']:<20} {account['provider']:<12} {quota_pct:>6.1f}% {account['success_rate']:>6.1f}%")
    
    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="cleanup", help="Clean up expired accounts")
@click.option("--days", "-d", type=int, default=90, help="Days old to consider expired (default: 90)")
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without actually deleting")
def cleanup_accounts(days: int, dry_run: bool):
    """Clean up accounts that haven't been used for specified days"""
    try:
        manager = asyncio.run(get_account_manager())
        
        if dry_run:
            cutoff_date = datetime.now() - timedelta(days=days)
            expired_accounts = []
            
            for account_id, account_info in manager.accounts.items():
                if account_info.last_used and account_info.last_used < cutoff_date:
                    expired_accounts.append(account_id)
            
            if expired_accounts:
                click.echo(f"Would delete {len(expired_accounts)} expired accounts:")
                for account_id in expired_accounts:
                    click.echo(f"  - {account_id}")
            else:
                click.echo("No expired accounts found")
        else:
            deleted_count = asyncio.run(manager.cleanup_expired_accounts(days))
            click.echo(f"Cleaned up {deleted_count} expired accounts")
    
    except Exception as e:
        click.echo(f"Error cleaning up accounts: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="set-api-key", help="Set API key for an account")
@click.argument("account_id")
@click.argument("api_key")
def set_api_key(account_id: str, api_key: str):
    """Set API key for an account"""
    try:
        manager = asyncio.run(get_account_manager())
        success = asyncio.run(manager.set_api_key(account_id, api_key))
        
        if success:
            click.echo(f"Successfully set API key for account: {account_id}")
        else:
            click.echo(f"Failed to set API key for account: {account_id}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error setting API key: {e}", err=True)
        sys.exit(1)


@account_cli.command(name="update-quota", help="Update quota for an account")
@click.argument("account_id")
@click.option("--remaining", "-r", type=int, required=True, help="Remaining quota")
@click.option("--limit", "-l", type=int, required=True, help="Quota limit")
def update_quota(account_id: str, remaining: int, limit: int):
    """Update quota information for an account"""
    try:
        manager = asyncio.run(get_account_manager())
        
        if account_id not in manager.accounts:
            click.echo(f"Account not found: {account_id}", err=True)
            sys.exit(1)
        
        account_info = manager.accounts[account_id]
        account_info.quota_remaining = remaining
        account_info.quota_limit = limit
        
        asyncio.run(manager._save_registry())
        
        click.echo(f"Updated quota for {account_id}: {remaining}/{limit}")
    
    except Exception as e:
        click.echo(f"Error updating quota: {e}", err=True)
        sys.exit(1)


# Add the account CLI group to the main CLI
def add_account_commands(cli):
    """Add account commands to main CLI"""
    cli.add_command(account_cli)


if __name__ == "__main__":
    account_cli()