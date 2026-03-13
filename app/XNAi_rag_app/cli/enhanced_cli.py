"""
Enhanced CLI with Domain Selection and Multi-Account Support

Provides an enhanced command-line interface that supports:
- Domain-specific expert access
- Multi-account OAuth authentication
- Account switching without re-authentication
- Integration with existing xnai CLI commands
"""

import argparse
import asyncio
import logging
import sys
from typing import Optional, Dict, Any, List
import json

from app.XNAi_rag_app.core.oauth_manager import OAuthManager, AccountManager
from app.XNAi_rag_app.core.domain_router import DomainRouter

logger = logging.getLogger(__name__)


class EnhancedCLI:
    """Enhanced CLI with domain selection and multi-account support"""
    
    def __init__(self):
        self.oauth_manager = OAuthManager()
        self.account_manager = AccountManager()
        self.domain_router = DomainRouter()
        self.current_account = None
    
    async def initialize(self):
        """Initialize the enhanced CLI"""
        # Try to load a default account
        accounts = await self.oauth_manager.list_accounts()
        if accounts:
            self.current_account = accounts[0]
            print(f"✅ Using default account: {self.current_account}")
        else:
            print("⚠️  No OAuth accounts found. Run 'xnai oauth batch' to authenticate accounts.")
    
    async def dispatch_with_domain(
        self, 
        query: str, 
        domain: str = "general", 
        account_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatch query with domain selection"""
        
        print(f"🔍 Processing query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        # Select account if not specified
        if not account_id:
            account_id = self.current_account
        
        if not account_id:
            account_id = await self.domain_router.select_best_account(domain)
            if not account_id:
                return {"error": "No valid account available"}
        
        print(f"📍 Routing to domain: {domain}")
        print(f"👤 Using account: {account_id}")
        
        try:
            # Route to domain expert
            routing_result = await self.domain_router.route_to_expert(domain, query, account_id)
            
            # Execute with expert context
            result = await self.domain_router.execute_with_expert(query, routing_result)
            
            # Display results
            self._display_routing_info(routing_result)
            self._display_response(result)
            
            return result
            
        except Exception as e:
            error_msg = f"❌ Failed to dispatch query: {e}"
            print(error_msg)
            return {"error": str(e)}
    
    def _display_routing_info(self, routing_result: Dict[str, Any]):
        """Display routing information"""
        info = routing_result['routing_info']
        expert_config = routing_result['expert_config']
        
        print("\n" + "="*60)
        print("📋 ROUTING SUMMARY")
        print("="*60)
        print(f"Domain: {info['domain']}")
        print(f"Expert: {expert_config['role']}")
        print(f"Account: {info['account_id']}")
        print(f"Model: {info['model']}")
        print(f"Timestamp: {info['timestamp']}")
        print("="*60)
    
    def _display_response(self, result: Dict[str, Any]):
        """Display response information"""
        response = result['response']
        metadata = result['metadata']
        
        print(f"\n🤖 Response from {response['model_used']}")
        print(f"📊 Tokens used: {metadata.get('tokens_used', 'N/A')}")
        print(f"⏱️  Execution time: {metadata.get('execution_time', 0):.2f}s")
        print(f"🧠 Expert context loaded: {'✅' if metadata.get('expert_context_loaded') else '❌'}")
        print("\n" + "="*60)
    
    async def list_domains(self):
        """List available domains"""
        domains = await self.domain_router.list_available_domains()
        
        print("\n" + "="*60)
        print("🌍 AVAILABLE DOMAINS")
        print("="*60)
        
        for domain in domains:
            status = "✅" if domain['available'] else "❌"
            account_info = f" (account: {domain['preferred_account']})" if domain['preferred_account'] else " (no account)"
            print(f"{status} {domain['name']}: {domain['role']}{account_info}")
            if domain['description']:
                print(f"    {domain['description']}")
            print()
        
        print("="*60)
    
    async def switch_account(self, account_id: str) -> bool:
        """Switch to different account"""
        credentials = await self.oauth_manager.get_credentials(account_id)
        if credentials:
            if await self.oauth_manager.is_valid(account_id):
                self.current_account = account_id
                print(f"✅ Switched to account: {account_id}")
                return True
            else:
                print(f"❌ Account {account_id} credentials expired")
                return False
        else:
            print(f"❌ No credentials found for {account_id}")
            print("Run 'xnai oauth authenticate <account>' to authenticate this account")
            return False
    
    async def list_accounts(self):
        """List all available accounts"""
        accounts = await self.oauth_manager.list_accounts()
        
        print("\n" + "="*60)
        print("👤 AVAILABLE ACCOUNTS")
        print("="*60)
        
        for account in accounts:
            valid = "✅" if await self.oauth_manager.is_valid(account) else "❌"
            current = " (current)" if account == self.current_account else ""
            print(f"{valid} {account}{current}")
        
        print("="*60)
    
    async def get_domain_status(self, domain: str):
        """Get status for specific domain"""
        status = await self.domain_router.get_domain_status(domain)
        
        print(f"\n" + "="*60)
        print(f"📊 DOMAIN STATUS: {domain.upper()}")
        print("="*60)
        print(f"Role: {status['role']}")
        print(f"Available: {'✅' if status['available'] else '❌'}")
        
        if status['available']:
            print(f"Account: {status['account']}")
            print(f"Expert config: {status['expert_config_file']}")
            print(f"Models: {', '.join(status['preferred_models'])}")
            print(f"Expert context loaded: {'✅' if status['expert_context_loaded'] else '❌'}")
        else:
            print(f"Error: {status.get('error', 'Unknown error')}")
        
        print("="*60)
    
    async def auto_detect_domain(self, query: str):
        """Auto-detect domain from query"""
        detected_domain = self.domain_router.detect_domain_from_query(query)
        
        print(f"\n" + "="*60)
        print("🔍 DOMAIN DETECTION")
        print("="*60)
        print(f"Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        print(f"Detected domain: {detected_domain}")
        
        # Get domain status
        status = await self.domain_router.get_domain_status(detected_domain)
        if status['available']:
            print(f"✅ Domain available with account: {status['account']}")
        else:
            print("❌ Domain not available")
        
        print("="*60)


def create_argument_parser():
    """Create argument parser for enhanced CLI"""
    parser = argparse.ArgumentParser(
        description="Enhanced CLI with domain selection and multi-account support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use domain-specific experts
  python enhanced_cli.py --domain architect --query "Design a microservices architecture"
  python enhanced_cli.py --domain ui --query "Create a responsive dashboard"
  
  # List available domains and accounts
  python enhanced_cli.py --list-domains
  python enhanced_cli.py --list-accounts
  
  # Switch accounts
  python enhanced_cli.py --switch-account gemini_oauth_02
  
  # Auto-detect domain
  python enhanced_cli.py --auto-detect "How do I optimize database queries?"
  
  # Get domain status
  python enhanced_cli.py --domain-status architect
        """
    )
    
    # Main actions
    parser.add_argument('--query', '-q', help='Query to process')
    parser.add_argument('--domain', '-d', default='general', help='Domain to use (default: general)')
    parser.add_argument('--account', '-a', help='Account to use')
    parser.add_argument('--session', '-s', help='Session ID')
    
    # Information commands
    parser.add_argument('--list-domains', action='store_true', help='List all available domains')
    parser.add_argument('--list-accounts', action='store_true', help='List all available accounts')
    parser.add_argument('--domain-status', help='Get status for specific domain')
    parser.add_argument('--auto-detect', help='Auto-detect domain from query')
    
    # Account management
    parser.add_argument('--switch-account', help='Switch to different account')
    
    # Integration with existing CLI
    parser.add_argument('--integrate', action='store_true', 
                       help='Integrate with existing xnai CLI (experimental)')
    
    return parser


async def main():
    """Main CLI entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Initialize enhanced CLI
    cli = EnhancedCLI()
    await cli.initialize()
    
    # Handle different command types
    if args.list_domains:
        await cli.list_domains()
    
    elif args.list_accounts:
        await cli.list_accounts()
    
    elif args.domain_status:
        await cli.get_domain_status(args.domain_status)
    
    elif args.auto_detect:
        await cli.auto_detect_domain(args.auto_detect)
    
    elif args.switch_account:
        await cli.switch_account(args.switch_account)
    
    elif args.query:
        result = await cli.dispatch_with_domain(
            query=args.query,
            domain=args.domain,
            account_id=args.account,
            session_id=args.session
        )
        if result.get('error'):
            sys.exit(1)
    
    elif args.integrate:
        # Experimental integration with existing CLI
        print("🔧 Experimental integration mode")
        print("This would integrate with the existing xnai CLI")
        print("Integration not yet implemented")
    
    else:
        parser.print_help()


# Integration with existing xnai CLI
def integrate_with_xnai_cli():
    """Integrate enhanced CLI functionality with existing xnai CLI"""
    
    # This function would be called from the main xnai CLI
    # to add domain and account management commands
    
    commands = {
        'domain': {
            'list': 'List available domains',
            'status': 'Get domain status',
            'detect': 'Auto-detect domain from query'
        },
        'account': {
            'list': 'List available accounts',
            'switch': 'Switch to different account',
            'status': 'Get account status'
        },
        'dispatch': {
            'domain': 'Dispatch with domain selection'
        }
    }
    
    return commands


if __name__ == "__main__":
    asyncio.run(main())