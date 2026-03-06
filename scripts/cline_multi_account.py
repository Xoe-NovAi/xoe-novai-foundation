#!/usr/bin/env python3
"""Multi-account Cline CLI wrapper for Omega Stack Agent-Bus."""

import os
import sys
import json
import yaml
import logging
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio
import signal
from contextlib import asynccontextmanager

# Configuration
CONFIG_FILE = "configs/cline-accounts.yaml"
DEFAULT_ACCOUNT = "default"
LOCK_FILE = "/tmp/omega-cline-lock"


@dataclass
class AccountConfig:
    """Configuration for a Cline account."""
    name: str
    model: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    priority: int = 0
    enabled: bool = True
    last_used: Optional[str] = None
    usage_count: int = 0


class ClineAccountManager:
    """Manager for multiple Cline accounts with model locking."""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = Path(config_file)
        self.accounts: Dict[str, AccountConfig] = {}
        self.current_account: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self):
        """Load account configuration from YAML file."""
        if not self.config_file.exists():
            self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            for account_name, account_data in config_data.get('accounts', {}).items():
                self.accounts[account_name] = AccountConfig(
                    name=account_name,
                    model=account_data.get('model', ''),
                    provider=account_data.get('provider', ''),
                    api_key=account_data.get('api_key'),
                    base_url=account_data.get('base_url'),
                    priority=account_data.get('priority', 0),
                    enabled=account_data.get('enabled', True),
                    last_used=account_data.get('last_used'),
                    usage_count=account_data.get('usage_count', 0)
                )
            
            self.logger.info(f"Loaded {len(self.accounts)} accounts from {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise
    
    def _create_default_config(self):
        """Create a default configuration file."""
        default_config = {
            'accounts': {
                'default': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'priority': 1,
                    'enabled': True,
                    'usage_count': 0
                },
                'claude': {
                    'model': 'claude-sonnet',
                    'provider': 'anthropic',
                    'priority': 2,
                    'enabled': True,
                    'usage_count': 0
                },
                'gemini': {
                    'model': 'gemini-pro',
                    'provider': 'google',
                    'priority': 3,
                    'enabled': True,
                    'usage_count': 0
                }
            }
        }
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        self.logger.info(f"Created default config at {self.config_file}")
    
    def list_accounts(self) -> List[AccountConfig]:
        """List all configured accounts."""
        return sorted(
            self.accounts.values(),
            key=lambda x: (-x.priority, x.name)
        )
    
    def get_account(self, account_name: str) -> Optional[AccountConfig]:
        """Get account configuration by name."""
        return self.accounts.get(account_name)
    
    def set_current_account(self, account_name: str) -> bool:
        """Set the current active account."""
        if account_name not in self.accounts:
            self.logger.error(f"Account '{account_name}' not found")
            return False
        
        if not self.accounts[account_name].enabled:
            self.logger.error(f"Account '{account_name}' is disabled")
            return False
        
        self.current_account = account_name
        self._update_account_usage(account_name)
        self._save_config()
        
        self.logger.info(f"Switched to account: {account_name}")
        return True
    
    def _update_account_usage(self, account_name: str):
        """Update account usage statistics."""
        account = self.accounts[account_name]
        account.last_used = datetime.utcnow().isoformat()
        account.usage_count += 1
        self.accounts[account_name] = account
    
    def _save_config(self):
        """Save current configuration to file."""
        config_data = {
            'accounts': {
                name: asdict(account) 
                for name, account in self.accounts.items()
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
    
    def get_best_available_account(self, preferred_model: Optional[str] = None) -> Optional[str]:
        """Get the best available account, optionally filtered by model."""
        available_accounts = [
            account for account in self.accounts.values()
            if account.enabled
        ]
        
        if preferred_model:
            # Filter by preferred model
            matching_accounts = [
                account for account in available_accounts
                if preferred_model.lower() in account.model.lower()
            ]
            if matching_accounts:
                available_accounts = matching_accounts
        
        if not available_accounts:
            return None
        
        # Sort by priority, then by last used (least recently used first)
        sorted_accounts = sorted(
            available_accounts,
            key=lambda x: (-x.priority, x.last_used or '1970-01-01')
        )
        
        return sorted_accounts[0].name
    
    def lock_model(self, model: str) -> bool:
        """Lock a model to prevent concurrent usage."""
        lock_data = {
            'model': model,
            'pid': os.getpid(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            with open(LOCK_FILE, 'w') as f:
                json.dump(lock_data, f)
            self.logger.info(f"Locked model: {model}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to lock model {model}: {e}")
            return False
    
    def unlock_model(self, model: str) -> bool:
        """Unlock a model."""
        try:
            if os.path.exists(LOCK_FILE):
                with open(LOCK_FILE, 'r') as f:
                    lock_data = json.load(f)
                
                if lock_data.get('model') == model and lock_data.get('pid') == os.getpid():
                    os.remove(LOCK_FILE)
                    self.logger.info(f"Unlocked model: {model}")
                    return True
        except Exception as e:
            self.logger.error(f"Failed to unlock model {model}: {e}")
        
        return False


class ClineWrapper:
    """Wrapper for Cline CLI with multi-account support."""
    
    def __init__(self):
        self.account_manager = ClineAccountManager()
        self.logger = logging.getLogger(__name__)
        self.process = None
    
    def run_command(self, args: List[str], account: Optional[str] = None) -> int:
        """Run a Cline command with the specified account."""
        # Determine which account to use
        if account:
            target_account = account
        elif self.account_manager.current_account:
            target_account = self.account_manager.current_account
        else:
            # Auto-select best account
            target_account = self.account_manager.get_best_available_account()
        
        if not target_account:
            self.logger.error("No available accounts")
            return 1
        
        account_config = self.account_manager.get_account(target_account)
        if not account_config:
            self.logger.error(f"Account {target_account} not found")
            return 1
        
        # Lock the model
        if not self.account_manager.lock_model(account_config.model):
            self.logger.error(f"Failed to lock model {account_config.model}")
            return 1
        
        try:
            # Set environment variables for the account
            env = os.environ.copy()
            env.update(self._get_account_env(account_config))
            
            # Run the command
            self.logger.info(f"Running command with account {target_account}: {' '.join(args)}")
            result = subprocess.run(args, env=env, text=True)
            
            return result.returncode
            
        finally:
            # Always unlock the model
            self.account_manager.unlock_model(account_config.model)
    
    def _get_account_env(self, account: AccountConfig) -> Dict[str, str]:
        """Get environment variables for an account."""
        env = {}
        
        # Set provider-specific environment variables
        if account.provider.lower() == 'openai':
            if account.api_key:
                env['OPENAI_API_KEY'] = account.api_key
            if account.base_url:
                env['OPENAI_BASE_URL'] = account.base_url
        
        elif account.provider.lower() == 'anthropic':
            if account.api_key:
                env['ANTHROPIC_API_KEY'] = account.api_key
            if account.base_url:
                env['ANTHROPIC_BASE_URL'] = account.base_url
        
        elif account.provider.lower() == 'google':
            if account.api_key:
                env['GOOGLE_API_KEY'] = account.api_key
            if account.base_url:
                env['GOOGLE_BASE_URL'] = account.base_url
        
        # Set model
        env['CLINE_MODEL'] = account.model
        
        return env
    
    def interactive_mode(self, account: Optional[str] = None):
        """Start interactive mode with the specified account."""
        if account:
            if not self.account_manager.set_current_account(account):
                self.logger.error(f"Failed to set account {account}")
                return 1
        
        # Start Cline in interactive mode
        target_account = self.account_manager.current_account or self.account_manager.get_best_available_account()
        if not target_account:
            self.logger.error("No available accounts for interactive mode")
            return 1
        
        account_config = self.account_manager.get_account(target_account)
        if not account_config:
            self.logger.error(f"Account {target_account} not found")
            return 1
        
        # Lock the model
        if not self.account_manager.lock_model(account_config.model):
            self.logger.error(f"Failed to lock model {account_config.model}")
            return 1
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env.update(self._get_account_env(account_config))
            
            # Start interactive session
            self.logger.info(f"Starting interactive mode with account {target_account}")
            self.process = subprocess.Popen(['cline'], env=env)
            
            # Wait for process to complete
            return self.process.wait()
            
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
            if self.process:
                self.process.terminate()
                self.process.wait()
            return 0
        
        finally:
            # Always unlock the model
            self.account_manager.unlock_model(account_config.model)


class ClineCLI:
    """CLI interface for the multi-account Cline wrapper."""
    
    def __init__(self):
        self.wrapper = ClineWrapper()
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog='omega-cline',
            description='Multi-account Cline CLI wrapper for Omega Stack',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  omega-cline list-accounts                    # List all accounts
  omega-cline use claude                       # Switch to claude account
  omega-cline run --account gemini ls          # Run command with gemini account
  omega-cline interactive --account default    # Start interactive mode
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # List accounts
        list_parser = subparsers.add_parser('list-accounts', help='List all configured accounts')
        
        # Use account
        use_parser = subparsers.add_parser('use', help='Set current account')
        use_parser.add_argument('account', help='Account name')
        
        # Run command
        run_parser = subparsers.add_parser('run', help='Run a command with specified account')
        run_parser.add_argument('--account', help='Account to use (optional)')
        run_parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to run')
        
        # Interactive mode
        interactive_parser = subparsers.add_parser('interactive', help='Start interactive Cline session')
        interactive_parser.add_argument('--account', help='Account to use (optional)')
        
        # Account management
        account_parser = subparsers.add_parser('account', help='Account management commands')
        account_subparsers = account_parser.add_subparsers(dest='account_subcommand')
        
        # Add account
        add_parser = account_subparsers.add_parser('add', help='Add a new account')
        add_parser.add_argument('name', help='Account name')
        add_parser.add_argument('--model', required=True, help='Model name')
        add_parser.add_argument('--provider', required=True, help='Provider name')
        add_parser.add_argument('--api-key', help='API key')
        add_parser.add_argument('--base-url', help='Base URL')
        add_parser.add_argument('--priority', type=int, default=0, help='Priority (higher = more preferred)')
        
        # Remove account
        remove_parser = account_subparsers.add_parser('remove', help='Remove an account')
        remove_parser.add_argument('name', help='Account name')
        
        # Enable/disable account
        toggle_parser = account_subparsers.add_parser('toggle', help='Enable/disable an account')
        toggle_parser.add_argument('name', help='Account name')
        toggle_parser.add_argument('state', choices=['enable', 'disable'], help='State to set')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the given arguments."""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            if parsed_args.command == 'list-accounts':
                return self.list_accounts()
            elif parsed_args.command == 'use':
                return self.use_account(parsed_args.account)
            elif parsed_args.command == 'run':
                return self.run_command(parsed_args)
            elif parsed_args.command == 'interactive':
                return self.interactive_mode(parsed_args)
            elif parsed_args.command == 'account':
                return self.account_management(parsed_args)
            else:
                self.parser.print_help()
                return 1
        
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
    
    def list_accounts(self) -> int:
        """List all configured accounts."""
        accounts = self.wrapper.account_manager.list_accounts()
        
        if not accounts:
            print("No accounts configured.")
            return 0
        
        print(f"{'Name':<15} {'Model':<20} {'Provider':<15} {'Priority':<10} {'Status':<10} {'Last Used'}")
        print("-" * 80)
        
        for account in accounts:
            status = "Enabled" if account.enabled else "Disabled"
            last_used = account.last_used or "Never"
            print(f"{account.name:<15} {account.model:<20} {account.provider:<15} {account.priority:<10} {status:<10} {last_used}")
        
        return 0
    
    def use_account(self, account_name: str) -> int:
        """Set current account."""
        if self.wrapper.account_manager.set_current_account(account_name):
            print(f"Switched to account: {account_name}")
            return 0
        else:
            print(f"Failed to switch to account: {account_name}")
            return 1
    
    def run_command(self, args) -> int:
        """Run a command with specified account."""
        if not args.command:
            print("Error: No command specified")
            return 1
        
        return self.wrapper.run_command(args.command, args.account)
    
    def interactive_mode(self, args) -> int:
        """Start interactive mode."""
        return self.wrapper.interactive_mode(args.account)
    
    def account_management(self, args) -> int:
        """Handle account management commands."""
        if args.account_subcommand == 'add':
            return self.add_account(args)
        elif args.account_subcommand == 'remove':
            return self.remove_account(args)
        elif args.account_subcommand == 'toggle':
            return self.toggle_account(args)
        else:
            print("Error: Invalid account subcommand")
            return 1
    
    def add_account(self, args) -> int:
        """Add a new account."""
        account = AccountConfig(
            name=args.name,
            model=args.model,
            provider=args.provider,
            api_key=args.api_key,
            base_url=args.base_url,
            priority=args.priority
        )
        
        self.wrapper.account_manager.accounts[args.name] = account
        self.wrapper.account_manager._save_config()
        
        print(f"Added account: {args.name}")
        return 0
    
    def remove_account(self, args) -> int:
        """Remove an account."""
        if args.name not in self.wrapper.account_manager.accounts:
            print(f"Error: Account '{args.name}' not found")
            return 1
        
        del self.wrapper.account_manager.accounts[args.name]
        self.wrapper.account_manager._save_config()
        
        print(f"Removed account: {args.name}")
        return 0
    
    def toggle_account(self, args) -> int:
        """Enable/disable an account."""
        if args.name not in self.wrapper.account_manager.accounts:
            print(f"Error: Account '{args.name}' not found")
            return 1
        
        account = self.wrapper.account_manager.accounts[args.name]
        account.enabled = (args.state == 'enable')
        self.wrapper.account_manager.accounts[args.name] = account
        self.wrapper.account_manager._save_config()
        
        print(f"Account '{args.name}' {'enabled' if account.enabled else 'disabled'}")
        return 0


def main():
    """Main entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create CLI and run
    cli = ClineCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())