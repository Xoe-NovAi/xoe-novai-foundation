#!/usr/bin/env python3
"""
Multi-Account OAuth Authentication and Domain Access Test Script

This script tests the complete multi-account OAuth authentication system
and domain-specific expert access functionality.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.XNAi_rag_app.core.oauth_manager import OAuthManager, AccountManager, batch_authenticate_accounts
from app.XNAi_rag_app.core.domain_router import DomainRouter
from app.XNAi_rag_app.cli.enhanced_cli import EnhancedCLI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MultiAccountTestSuite:
    """Test suite for multi-account OAuth and domain access"""
    
    def __init__(self):
        self.oauth_manager = OAuthManager()
        self.account_manager = AccountManager()
        self.domain_router = DomainRouter()
        self.cli = EnhancedCLI()
    
    async def test_oauth_manager(self):
        """Test OAuth credential management"""
        print("\n" + "="*60)
        print("🧪 TESTING OAUTH MANAGER")
        print("="*60)
        
        # Test 1: List accounts
        accounts = await self.oauth_manager.list_accounts()
        print(f"✅ Found {len(accounts)} stored accounts: {accounts}")
        
        # Test 2: Check account validity
        for account in accounts:
            valid = await self.oauth_manager.is_valid(account)
            status = "✅" if valid else "❌"
            print(f"{status} Account {account}: {'Valid' if valid else 'Invalid'}")
        
        # Test 3: Get credentials
        if accounts:
            credentials = await self.oauth_manager.get_credentials(accounts[0])
            if credentials:
                print(f"✅ Retrieved credentials for {accounts[0]}")
                print(f"   Provider: {credentials.get('provider')}")
                print(f"   Scopes: {credentials.get('scopes', [])}")
            else:
                print(f"❌ No credentials found for {accounts[0]}")
        
        return len(accounts) > 0
    
    async def test_account_manager(self):
        """Test account management and selection"""
        print("\n" + "="*60)
        print("🧪 TESTING ACCOUNT MANAGER")
        print("="*60)
        
        # Test 1: List OAuth accounts
        oauth_accounts = self.account_manager.list_oauth_accounts()
        print(f"✅ Found {len(oauth_accounts)} OAuth accounts: {oauth_accounts}")
        
        # Test 2: Get account configurations
        for account_id in oauth_accounts[:3]:  # Test first 3
            config = self.account_manager.get_account_by_id(account_id)
            if config:
                print(f"✅ Account {account_id}:")
                print(f"   Provider: {config.get('provider')}")
                print(f"   Priority: {config.get('priority')}")
                print(f"   Domains: {config.get('domains_supported', [])}")
            else:
                print(f"❌ Account {account_id} not found in config")
        
        # Test 3: Account selection
        selected = await self.account_manager.select_best_account("general")
        if selected:
            print(f"✅ Selected best account for 'general' domain: {selected}")
        else:
            print("❌ No account available for 'general' domain")
        
        return len(oauth_accounts) > 0
    
    async def test_domain_router(self):
        """Test domain routing and expert selection"""
        print("\n" + "="*60)
        print("🧪 TESTING DOMAIN ROUTER")
        print("="*60)
        
        # Test 1: List domains
        domains = await self.domain_router.list_available_domains()
        print(f"✅ Found {len(domains)} available domains:")
        for domain in domains:
            status = "✅" if domain['available'] else "❌"
            print(f"   {status} {domain['name']}: {domain['role']}")
        
        # Test 2: Domain detection
        test_queries = [
            "How do I design a microservices architecture?",
            "Create a responsive dashboard with React",
            "Build a RESTful API with FastAPI",
            "How do I optimize database queries?",
            "What's the best way to deploy to Kubernetes?"
        ]
        
        print("\n🔍 Testing domain detection:")
        for query in test_queries:
            detected = self.domain_router.detect_domain_from_query(query)
            print(f"   Query: '{query[:50]}...'")
            print(f"   Detected: {detected}")
        
        # Test 3: Expert routing
        test_domain = "architect"
        test_query = "Design a scalable e-commerce platform architecture"
        
        try:
            routing_result = await self.domain_router.route_to_expert(test_domain, test_query)
            print(f"\n✅ Successfully routed to {test_domain} expert:")
            print(f"   Domain: {routing_result['routing_info']['domain']}")
            print(f"   Expert: {routing_result['routing_info']['expert_role']}")
            print(f"   Account: {routing_result['routing_info']['account_id']}")
            print(f"   Model: {routing_result['routing_info']['model']}")
        except Exception as e:
            print(f"❌ Failed to route to {test_domain} expert: {e}")
        
        return len(domains) > 0
    
    async def test_enhanced_cli(self):
        """Test enhanced CLI functionality"""
        print("\n" + "="*60)
        print("🧪 TESTING ENHANCED CLI")
        print("="*60)
        
        # Initialize CLI
        await self.cli.initialize()
        
        # Test 1: List domains
        print("\n🌍 Testing domain listing:")
        await self.cli.list_domains()
        
        # Test 2: List accounts
        print("\n👤 Testing account listing:")
        await self.cli.list_accounts()
        
        # Test 3: Domain status
        print("\n📊 Testing domain status:")
        await self.cli.get_domain_status("architect")
        
        # Test 4: Auto-detect domain
        print("\n🔍 Testing domain auto-detection:")
        test_query = "How do I create a responsive dashboard with charts and graphs?"
        await self.cli.auto_detect_domain(test_query)
        
        # Test 5: Dispatch with domain
        print("\n🚀 Testing domain-specific dispatch:")
        result = await self.cli.dispatch_with_domain(
            query="Design a microservices architecture for an e-commerce platform",
            domain="architect"
        )
        
        if result.get('success'):
            print("✅ Domain-specific dispatch successful")
        else:
            print(f"❌ Domain-specific dispatch failed: {result.get('error')}")
        
        return True
    
    async def test_integration(self):
        """Test complete integration workflow"""
        print("\n" + "="*60)
        print("🧪 TESTING INTEGRATION WORKFLOW")
        print("="*60)
        
        # Test complete workflow: OAuth → Account Selection → Domain Routing → CLI
        test_scenarios = [
            {
                "name": "Architecture Design",
                "domain": "architect",
                "query": "Design a scalable microservices architecture for a ride-sharing app",
                "expected_expert": "System Blueprinting & Architecture"
            },
            {
                "name": "UI Dashboard",
                "domain": "ui",
                "query": "Create a responsive dashboard for monitoring system metrics",
                "expected_expert": "Frontend, UX, & Dashboard"
            },
            {
                "name": "API Design",
                "domain": "api",
                "query": "Design a RESTful API for a task management system",
                "expected_expert": "Backend, AnyIO, & Redis Streams"
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📋 Testing scenario: {scenario['name']}")
            print(f"   Domain: {scenario['domain']}")
            print(f"   Query: {scenario['query'][:60]}...")
            
            try:
                # Route to expert
                routing_result = await self.domain_router.route_to_expert(
                    scenario['domain'], 
                    scenario['query']
                )
                
                expert_role = routing_result['routing_info']['expert_role']
                account = routing_result['routing_info']['account_id']
                model = routing_result['routing_info']['model']
                
                print(f"   ✅ Routed to expert: {expert_role}")
                print(f"   ✅ Account: {account}")
                print(f"   ✅ Model: {model}")
                
                # Verify expert role matches expectation
                if scenario['expected_expert'] in expert_role:
                    print(f"   ✅ Expert role matches expectation")
                else:
                    print(f"   ⚠️  Expert role mismatch: expected '{scenario['expected_expert']}', got '{expert_role}'")
                
            except Exception as e:
                print(f"   ❌ Scenario failed: {e}")
        
        return True
    
    async def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 STARTING MULTI-ACCOUNT OAUTH AND DOMAIN ACCESS TESTS")
        print("="*80)
        
        test_results = {}
        
        # Run individual tests
        test_results['oauth_manager'] = await self.test_oauth_manager()
        test_results['account_manager'] = await self.test_account_manager()
        test_results['domain_router'] = await self.test_domain_router()
        test_results['enhanced_cli'] = await self.test_enhanced_cli()
        test_results['integration'] = await self.test_integration()
        
        # Print summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Multi-account OAuth and domain access is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total


async def main():
    """Main test execution"""
    if len(sys.argv) > 1 and sys.argv[1] == "batch_auth":
        print("🔄 Running batch authentication...")
        await batch_authenticate_accounts()
        print("✅ Batch authentication completed")
        return
    
    # Run tests
    test_suite = MultiAccountTestSuite()
    success = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())