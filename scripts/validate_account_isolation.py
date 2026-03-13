#!/usr/bin/env python3
"""
Account Isolation Validation Script

Validates that the multi-account system properly isolates accounts
and prevents cross-contamination between different providers and users.

Author: XNAi Foundation
Version: 1.0.0
"""

import asyncio
import tempfile
import os
import yaml
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from app.XNAi_rag_app.core.account_manager import AccountManager, AccountInfo, AccountStatus, AccountType
from app.XNAi_rag_app.core.agent_account_integration import AgentAccountManager, AccountAwareAgent


class AccountIsolationValidator:
    """Validates account isolation and security"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.validation_results = []
    
    def _setup_logger(self):
        """Setup validation logger"""
        import logging
        logger = logging.getLogger("AccountIsolationValidator")
        logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log validation result"""
        status = "PASS" if passed else "FAIL"
        self.logger.info(f"[{status}] {test_name}: {details}")
        self.validation_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def validate_account_isolation(self) -> Dict[str, Any]:
        """Run comprehensive account isolation validation"""
        self.logger.info("Starting account isolation validation...")
        
        # Test 1: Configuration Isolation
        await self._test_configuration_isolation()
        
        # Test 2: Quota Isolation
        await self._test_quota_isolation()
        
        # Test 3: Context Isolation
        await self._test_context_isolation()
        
        # Test 4: Agent Isolation
        await self._test_agent_isolation()
        
        # Test 5: Security Isolation
        await self._test_security_isolation()
        
        # Generate report
        return self._generate_validation_report()
    
    async def _test_configuration_isolation(self):
        """Test that account configurations are properly isolated"""
        self.logger.info("Testing configuration isolation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create separate config files for different providers
            github_config = os.path.join(temp_dir, "github_accounts.yaml")
            gemini_config = os.path.join(temp_dir, "gemini_accounts.yaml")
            
            github_accounts = {
                "accounts": [
                    {
                        "id": "github_user_01",
                        "name": "GitHub User 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "github_user@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5"],
                        "priority": 1,
                        "api_key": "github_key_123",
                        "usage_stats": {}
                    }
                ]
            }
            
            gemini_accounts = {
                "accounts": [
                    {
                        "id": "gemini_user_01",
                        "name": "Gemini User 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "gemini_user@example.com",
                        "provider": "gemini",
                        "quota_remaining": 800,
                        "quota_limit": 1000,
                        "models_preferred": ["gemini-3-pro"],
                        "priority": 1,
                        "api_key": "gemini_key_456",
                        "usage_stats": {}
                    }
                ]
            }
            
            # Write separate configs
            with open(github_config, 'w') as f:
                yaml.dump(github_accounts, f)
            
            with open(gemini_config, 'w') as f:
                yaml.dump(gemini_accounts, f)
            
            # Load managers with different configs
            github_manager = AccountManager(github_config)
            await github_manager.initialize()
            
            gemini_manager = AccountManager(gemini_config)
            await gemini_manager.initialize()
            
            # Verify isolation
            github_accounts_loaded = len(github_manager.accounts)
            gemini_accounts_loaded = len(gemini_manager.accounts)
            
            self.log_result(
                "Configuration Isolation",
                github_accounts_loaded == 1 and gemini_accounts_loaded == 1,
                f"GitHub: {github_accounts_loaded} accounts, Gemini: {gemini_accounts_loaded} accounts"
            )
            
            # Verify no cross-contamination
            github_has_gemini = "gemini_user_01" in github_manager.accounts
            gemini_has_github = "github_user_01" in gemini_manager.accounts
            
            self.log_result(
                "No Cross-Contamination",
                not github_has_gemini and not gemini_has_github,
                f"GitHub has Gemini accounts: {github_has_gemini}, Gemini has GitHub accounts: {gemini_has_github}"
            )
    
    async def _test_quota_isolation(self):
        """Test that quota tracking is properly isolated"""
        self.logger.info("Testing quota isolation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            test_accounts = {
                "accounts": [
                    {
                        "id": "quota_test_01",
                        "name": "Quota Test 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "quota1@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5"],
                        "priority": 1,
                        "api_key": "quota_key_1",
                        "usage_stats": {"total_requests": 0, "successful_requests": 0, "failed_requests": 0, "avg_response_time": 0.0}
                    },
                    {
                        "id": "quota_test_02",
                        "name": "Quota Test 2",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "quota2@example.com",
                        "provider": "gemini",
                        "quota_remaining": 800,
                        "quota_limit": 1000,
                        "models_preferred": ["gemini-3-pro"],
                        "priority": 2,
                        "api_key": "quota_key_2",
                        "usage_stats": {"total_requests": 0, "successful_requests": 0, "failed_requests": 0, "avg_response_time": 0.0}
                    }
                ]
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            manager = AccountManager(config_path)
            await manager.initialize()
            
            # Test quota updates are isolated
            initial_quota_1 = manager.accounts["quota_test_01"].quota_remaining
            initial_quota_2 = manager.accounts["quota_test_02"].quota_remaining
            
            # Update usage for account 1
            await manager.update_usage_stats("quota_test_01", True, 1.0)
            
            # Check that only account 1 was affected
            final_quota_1 = manager.accounts["quota_test_01"].quota_remaining
            final_quota_2 = manager.accounts["quota_test_02"].quota_remaining
            
            quota_1_unchanged = initial_quota_1 == final_quota_1
            quota_2_unchanged = initial_quota_2 == final_quota_2
            
            self.log_result(
                "Quota Update Isolation",
                quota_1_unchanged and quota_2_unchanged,
                f"Account 1 quota unchanged: {quota_1_unchanged}, Account 2 quota unchanged: {quota_2_unchanged}"
            )
    
    async def _test_context_isolation(self):
        """Test that agent contexts are properly isolated"""
        self.logger.info("Testing context isolation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            test_accounts = {
                "accounts": [
                    {
                        "id": "context_test_01",
                        "name": "Context Test 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "context1@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5"],
                        "priority": 1,
                        "api_key": "context_key_1",
                        "usage_stats": {}
                    },
                    {
                        "id": "context_test_02",
                        "name": "Context Test 2",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "context2@example.com",
                        "provider": "gemini",
                        "quota_remaining": 800,
                        "quota_limit": 1000,
                        "models_preferred": ["gemini-3-pro"],
                        "priority": 2,
                        "api_key": "context_key_2",
                        "usage_stats": {}
                    }
                ]
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            manager = AccountManager(config_path)
            await manager.initialize()
            
            # Test context preservation for different agents
            async with AgentAccountContext("agent_1", manager):
                await manager.switch_account("context_test_01")
                agent_1_account = manager.get_current_account()
                
                async with AgentAccountContext("agent_2", manager):
                    await manager.switch_account("context_test_02")
                    agent_2_account = manager.get_current_account()
                    
                    # Agent 2 should have different account
                    self.log_result(
                        "Agent Context Isolation",
                        agent_1_account.account_id != agent_2_account.account_id,
                        f"Agent 1: {agent_1_account.account_id}, Agent 2: {agent_2_account.account_id}"
                    )
                
                # Agent 1 should still have original account
                agent_1_final_account = manager.get_current_account()
                self.log_result(
                    "Agent Context Restoration",
                    agent_1_account.account_id == agent_1_final_account.account_id,
                    f"Agent 1 original: {agent_1_account.account_id}, final: {agent_1_final_account.account_id}"
                )
    
    async def _test_agent_isolation(self):
        """Test that agents are properly isolated"""
        self.logger.info("Testing agent isolation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            test_accounts = {
                "accounts": [
                    {
                        "id": "agent_isolation_01",
                        "name": "Agent Isolation 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "agent1@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5"],
                        "priority": 1,
                        "api_key": "agent_key_1",
                        "usage_stats": {}
                    },
                    {
                        "id": "agent_isolation_02",
                        "name": "Agent Isolation 2",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "agent2@example.com",
                        "provider": "gemini",
                        "quota_remaining": 800,
                        "quota_limit": 1000,
                        "models_preferred": ["gemini-3-pro"],
                        "priority": 2,
                        "api_key": "agent_key_2",
                        "usage_stats": {}
                    }
                ]
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            # Create multiple agents
            agent1 = AccountAwareAgent("test_agent_1")
            agent1.account_manager.account_manager = AccountManager(config_path)
            await agent1.account_manager.account_manager.initialize()
            
            agent2 = AccountAwareAgent("test_agent_2")
            agent2.account_manager.account_manager = AccountManager(config_path)
            await agent2.account_manager.account_manager.initialize()
            
            # Test that agents can have different current accounts
            await agent1.switch_account("agent_isolation_01")
            await agent2.switch_account("agent_isolation_02")
            
            agent1_current = await agent1.get_current_account()
            agent2_current = await agent2.get_current_account()
            
            self.log_result(
                "Agent Account Isolation",
                agent1_current.account_id != agent2_current.account_id,
                f"Agent 1: {agent1_current.account_id}, Agent 2: {agent2_current.account_id}"
            )
    
    async def _test_security_isolation(self):
        """Test security isolation measures"""
        self.logger.info("Testing security isolation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            test_accounts = {
                "accounts": [
                    {
                        "id": "security_test_01",
                        "name": "Security Test 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "security1@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5"],
                        "priority": 1,
                        "api_key": "security_key_123",
                        "usage_stats": {}
                    },
                    {
                        "id": "security_test_02",
                        "name": "Security Test 2",
                        "type": "user",
                        "status": "suspended",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "security2@example.com",
                        "provider": "gemini",
                        "quota_remaining": 800,
                        "quota_limit": 1000,
                        "models_preferred": ["gemini-3-pro"],
                        "priority": 2,
                        "api_key": "security_key_456",
                        "usage_stats": {}
                    }
                ]
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            manager = AccountManager(config_path)
            await manager.initialize()
            
            # Test that suspended accounts cannot be switched to
            success = await manager.switch_account("security_test_02")
            self.log_result(
                "Suspended Account Access Prevention",
                not success,
                f"Switch to suspended account succeeded: {success}"
            )
            
            # Test that accounts with no quota cannot be switched to
            manager.accounts["security_test_01"].quota_remaining = 0
            success = await manager.switch_account("security_test_01")
            self.log_result(
                "Zero Quota Account Access Prevention",
                not success,
                f"Switch to zero-quota account succeeded: {success}"
            )
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        report = {
            "validation_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.validation_results,
            "isolation_status": "PASS" if failed_tests == 0 else "FAIL"
        }
        
        # Log summary
        self.logger.info(f"Validation Summary: {passed_tests}/{total_tests} tests passed ({report['validation_summary']['success_rate']:.1f}%)")
        
        if failed_tests > 0:
            self.logger.warning("Some isolation tests failed. Review the results above.")
        else:
            self.logger.info("All isolation tests passed. Account isolation is properly implemented.")
        
        return report


async def main():
    """Main validation function"""
    validator = AccountIsolationValidator()
    report = await validator.validate_account_isolation()
    
    # Save report
    report_path = "account_isolation_validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nValidation report saved to: {report_path}")
    
    # Print summary
    summary = report["validation_summary"]
    print(f"\nAccount Isolation Validation Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {report['isolation_status']}")


if __name__ == "__main__":
    asyncio.run(main())