"""
Domain Router for Expert System

Routes requests to appropriate domain experts based on query content,
domain selection, and account preferences. Integrates with OAuth Manager
and Account Manager for seamless multi-account, multi-domain operation.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import asyncio

from app.XNAi_rag_app.core.oauth_manager import OAuthManager, AccountManager

logger = logging.getLogger(__name__)


class DomainRouter:
    """Routes requests to appropriate domain experts"""
    
    def __init__(self, config_path: str = "config/domain-routing.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.experts = {}
        self.oauth_manager = OAuthManager()
        self.account_manager = AccountManager()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load domain routing configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded domain routing config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load domain routing config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default domain configuration"""
        return {
            'domains': {
                'general': {
                    'id': 0,
                    'role': 'General Purpose Assistant',
                    'expert_config': 'expert-knowledge/general-expert.yaml',
                    'preferred_models': ['google/antigravity-claude-sonnet-4-6']
                }
            }
        }
    
    def get_domain_list(self) -> List[Dict[str, Any]]:
        """Get list of all available domains"""
        domains = []
        for domain_id, config in self.config['domains'].items():
            domains.append({
                'id': config['id'],
                'name': domain_id,
                'role': config['role'],
                'description': config.get('description', ''),
                'expert_config': config['expert_config'],
                'preferred_models': config['preferred_models']
            })
        return sorted(domains, key=lambda x: x['id'])
    
    def get_expert_for_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get expert configuration for a domain"""
        domain_config = self.config['domains'].get(domain)
        if not domain_config:
            logger.warning(f"Domain '{domain}' not found, using general domain")
            domain_config = self.config['domains'].get('general')
        
        return {
            'domain': domain,
            'role': domain_config['role'],
            'expert_config': domain_config['expert_config'],
            'preferred_models': domain_config['preferred_models'],
            'description': domain_config.get('description', ''),
            'id': domain_config['id']
        }
    
    def detect_domain_from_query(self, query: str) -> str:
        """Auto-detect domain from query content"""
        query_lower = query.lower()
        
        # Domain detection rules
        domain_keywords = {
            'architect': ['architecture', 'design', 'system', 'scalability', 'pattern', 'blueprint'],
            'api': ['api', 'backend', 'endpoint', 'rest', 'graphql', 'async', 'redis'],
            'ui': ['ui', 'ux', 'frontend', 'interface', 'dashboard', 'responsive', 'accessibility'],
            'voice': ['voice', 'audio', 'stt', 'tts', 'speech', 'transcribe'],
            'data': ['data', 'rag', 'qdrant', 'gnosis', 'database', 'retrieval'],
            'ops': ['infrastructure', 'podman', 'caddy', 'deployment', 'container', 'docker'],
            'research': ['research', 'scholarly', 'metadata', 'academic', 'paper', 'study'],
            'test': ['test', 'pytest', 'qa', 'validation', 'testing', 'quality']
        }
        
        # Count keyword matches
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                domain_scores[domain] = score
        
        # Return domain with highest score, or general if no match
        if domain_scores:
            detected_domain = max(domain_scores, key=domain_scores.get)
            logger.info(f"Auto-detected domain: {detected_domain} (score: {domain_scores[detected_domain]})")
            return detected_domain
        
        return 'general'
    
    async def select_best_account(self, domain: str, preferred_account: Optional[str] = None) -> Optional[str]:
        """Select the best account for a given domain"""
        
        # If preferred account is specified, use it if available
        if preferred_account:
            credentials = await self.oauth_manager.get_credentials(preferred_account)
            if credentials and await self.oauth_manager.is_valid(preferred_account):
                return preferred_account
            else:
                logger.warning(f"Preferred account {preferred_account} not available or invalid")
        
        # Get all OAuth accounts
        oauth_accounts = self.account_manager.list_oauth_accounts()
        if not oauth_accounts:
            logger.error("No OAuth accounts available")
            return None
        
        # Filter accounts that are valid
        valid_accounts = []
        for account in oauth_accounts:
            if await self.oauth_manager.is_valid(account):
                valid_accounts.append(account)
        
        if not valid_accounts:
            logger.error("No valid OAuth accounts available")
            return None
        
        # Simple selection: return first valid account
        # Could be enhanced with load balancing, priority, etc.
        return valid_accounts[0]
    
    def select_best_model(self, expert_config: Dict[str, Any], account_id: str) -> Optional[str]:
        """Select the best model for the expert and account"""
        preferred_models = expert_config['preferred_models']
        
        # For now, return the first preferred model
        # Could be enhanced with model availability checking, performance metrics, etc.
        if preferred_models:
            return preferred_models[0]
        
        return None
    
    async def load_expert_context(self, expert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load expert context from configuration file"""
        expert_file = Path(expert_config['expert_config'])
        
        if not expert_file.exists():
            logger.warning(f"Expert config file not found: {expert_file}")
            return self._get_default_expert_context(expert_config)
        
        try:
            with open(expert_file, 'r') as f:
                expert_data = yaml.safe_load(f)
            
            return {
                'prompt_template': expert_data.get('prompt_template', ''),
                'knowledge_base': expert_data.get('knowledge_base', []),
                'specializations': expert_data.get('specializations', []),
                'examples': expert_data.get('examples', []),
                'constraints': expert_data.get('constraints', [])
            }
        except Exception as e:
            logger.error(f"Failed to load expert context: {e}")
            return self._get_default_expert_context(expert_config)
    
    def _get_default_expert_context(self, expert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get default expert context"""
        return {
            'prompt_template': f"You are an expert in {expert_config['role']}. Provide helpful and accurate responses.",
            'knowledge_base': [],
            'specializations': [],
            'examples': [],
            'constraints': []
        }
    
    async def route_to_expert(self, domain: str, query: str, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Route query to appropriate expert"""
        
        # Auto-detect domain if not specified
        if not domain or domain == 'auto':
            domain = self.detect_domain_from_query(query)
        
        # Get expert configuration
        expert_config = self.get_expert_for_domain(domain)
        if not expert_config:
            raise ValueError(f"No expert configuration found for domain: {domain}")
        
        # Select account
        selected_account = await self.select_best_account(domain, account_id)
        if not selected_account:
            raise ValueError("No valid account available for routing")
        
        # Get OAuth credentials
        credentials = await self.oauth_manager.get_credentials(selected_account)
        if not credentials:
            raise ValueError(f"No OAuth credentials found for account: {selected_account}")
        
        # Select model
        model = self.select_best_model(expert_config, selected_account)
        if not model:
            raise ValueError(f"No suitable model found for expert: {expert_config['role']}")
        
        # Load expert context
        expert_context = await self.load_expert_context(expert_config)
        
        # Build routing result
        routing_result = {
            'routing_info': {
                'domain': domain,
                'expert_role': expert_config['role'],
                'account_id': selected_account,
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'query_length': len(query)
            },
            'expert_config': expert_config,
            'expert_context': expert_context,
            'oauth_credentials': {
                'account_id': selected_account,
                'provider': credentials.get('provider'),
                'scopes': credentials.get('scopes', []),
                'expires_at': credentials.get('expires_at')
            },
            'model_selection': {
                'preferred_models': expert_config['preferred_models'],
                'selected_model': model,
                'selection_reason': 'First preferred model available'
            }
        }
        
        logger.info(f"Routed query to {domain} expert via {selected_account} account using {model}")
        return routing_result
    
    async def execute_with_expert(self, query: str, routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query with expert context"""
        
        # This would integrate with the actual LLM execution
        # For now, return a mock response structure
        return {
            'success': True,
            'query': query,
            'routing_info': routing_result['routing_info'],
            'response': {
                'content': f"Response from {routing_result['routing_info']['expert_role']} expert",
                'model_used': routing_result['routing_info']['model'],
                'account_used': routing_result['routing_info']['account_id'],
                'domain': routing_result['routing_info']['domain']
            },
            'metadata': {
                'execution_time': 0.0,
                'tokens_used': 0,
                'expert_context_loaded': bool(routing_result['expert_context'])
            }
        }
    
    async def list_available_domains(self) -> List[Dict[str, Any]]:
        """List all available domains with their details"""
        domains = self.get_domain_list()
        
        # Add availability status
        for domain in domains:
            # Check if any OAuth account is available for this domain
            account = await self.select_best_account(domain['name'])
            domain['available'] = account is not None
            domain['preferred_account'] = account
        
        return domains
    
    async def get_domain_status(self, domain: str) -> Dict[str, Any]:
        """Get status information for a specific domain"""
        expert_config = self.get_expert_for_domain(domain)
        if not expert_config:
            return {'domain': domain, 'available': False, 'error': 'Domain not found'}
        
        # Check account availability
        account = await self.select_best_account(domain)
        
        # Check expert context availability
        expert_context = await self.load_expert_context(expert_config)
        
        return {
            'domain': domain,
            'role': expert_config['role'],
            'available': account is not None,
            'account': account,
            'expert_config_file': expert_config['expert_config'],
            'expert_context_loaded': bool(expert_context['prompt_template']),
            'preferred_models': expert_config['preferred_models']
        }


# CLI Interface for Domain Router
async def domain_router_cli():
    """Domain router CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python domain_router.py <command>")
        print("Commands:")
        print("  list                    - List all available domains")
        print("  status <domain>         - Get status for specific domain")
        print("  route <query> [domain]  - Route query to expert")
        print("  detect <query>          - Auto-detect domain from query")
        return
    
    command = sys.argv[1]
    router = DomainRouter()
    
    if command == "list":
        domains = await router.list_available_domains()
        print("Available domains:")
        for domain in domains:
            status = "✅" if domain['available'] else "❌"
            account = f" (account: {domain['preferred_account']})" if domain['preferred_account'] else ""
            print(f"  {status} {domain['name']}: {domain['role']}{account}")
    
    elif command == "status" and len(sys.argv) > 2:
        domain = sys.argv[2]
        status = await router.get_domain_status(domain)
        print(f"Domain: {status['domain']}")
        print(f"Role: {status['role']}")
        print(f"Available: {'✅' if status['available'] else '❌'}")
        if status['available']:
            print(f"Account: {status['account']}")
            print(f"Expert config: {status['expert_config_file']}")
            print(f"Models: {', '.join(status['preferred_models'])}")
    
    elif command == "route" and len(sys.argv) > 2:
        query = sys.argv[2]
        domain = sys.argv[3] if len(sys.argv) > 3 else 'auto'
        
        try:
            routing_result = await router.route_to_expert(domain, query)
            print(f"Query: {query}")
            print(f"Domain: {routing_result['routing_info']['domain']}")
            print(f"Expert: {routing_result['routing_info']['expert_role']}")
            print(f"Account: {routing_result['routing_info']['account_id']}")
            print(f"Model: {routing_result['routing_info']['model']}")
        except Exception as e:
            print(f"❌ Routing failed: {e}")
    
    elif command == "detect" and len(sys.argv) > 2:
        query = sys.argv[2]
        detected_domain = router.detect_domain_from_query(query)
        print(f"Query: {query}")
        print(f"Detected domain: {detected_domain}")
    
    else:
        print("❌ Unknown command or missing arguments")


if __name__ == "__main__":
    asyncio.run(domain_router_cli())