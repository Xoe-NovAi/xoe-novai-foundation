"""
Comprehensive test suite for the multi-account system.

Tests account management, CLI integration, agent integration,
and end-to-end workflows.

Author: XNAi Foundation
Version: 1.0.0
"""

import asyncio
import tempfile
import os
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from app.XNAi_rag_app.core.account_manager import (
    AccountManager, AccountInfo, AccountStatus, AccountType,
    get_account_manager
)
from app.XNAi_rag_app.core.account_cli import (
    list_accounts, show_status, switch_account, create_account,
    recommend_account, suspend_account, activate_account,
    generate_report, cleanup_accounts, set_api_key, update_quota
)
from app.XNAi_rag_app.core.agent_account_integration import (
    AgentAccountManager, AgentAccountContext, AccountAwareAgent,
    get_agent_account_manager
)


class TestAccountManager:
    """Test the core account manager functionality"""
    
    @pytest.fixture
    async def account_manager(self):
        """Create a test account manager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            # Create test accounts
            test_accounts = {
                "accounts": [
                    {
                        "id": "test_github_01",
                        "name": "Test GitHub Account",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "test@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5", "sonnet-4.5"],
                        "priority": 1,
                        "api_key": "test_key_123",
                        "usage_stats": {
                            "total_requests": 0,
                            "successful_requests": 0,
                            "failed_requests": 0,
                            "avg_response_time": 0.0
                        }
                    },
                    {
                        "id": "test_gemini_01",
                        "name": "Test Gemini Account",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "test2@example.com",
                        "provider": "gemini",
                        "quota_remaining": 500,
                        "quota_limit": 1000,
                        "models_preferred": ["gemini-3-pro"],
                        "priority": 2,
                        "api_key": "test_key_456",
                        "usage_stats": {
                            "total_requests": 0,
                            "successful_requests": 0,
                            "failed_requests": 0,
                            "avg_response_time": 0.0
                        }
                    }
                ],
                "rotation_strategy": "quota_aware",
                "auto_switch": True,
                "validation_enabled": True
            }
            
            # Write test config
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            # Create account manager
            manager = AccountManager(config_path)
            await manager.initialize()
            
            yield manager
    
    async def test_account_loading(self, account_manager):
        """Test that accounts are loaded correctly"""
        assert len(account_manager.accounts) == 2
        
        github_account = account_manager.accounts["test_github_01"]
        assert github_account.name == "Test GitHub Account"
        assert github_account.provider == "github"
        assert github_account.quota_remaining == 1000
        assert github_account.quota_limit == 1000
        assert github_account.status == AccountStatus.ACTIVE
    
    async def test_get_current_account(self, account_manager):
        """Test getting current account"""
        current = account_manager.get_current_account()
        assert current is not None
        assert current.account_id in account_manager.accounts
    
    async def test_switch_account(self, account_manager):
        """Test account switching"""
        # Switch to gemini account
        success = await account_manager.switch_account("test_gemini_01")
        assert success is True
        
        current = account_manager.get_current_account()
        assert current.account_id == "test_gemini_01"
        assert current.last_used is not None
    
    async def test_switch_to_nonexistent_account(self, account_manager):
        """Test switching to non-existent account"""
        success = await account_manager.switch_account("nonexistent")
        assert success is False
    
    async def test_switch_to_inactive_account(self, account_manager):
        """Test switching to inactive account"""
        # Make account inactive
        account_manager.accounts["test_github_01"].status = AccountStatus.INACTIVE
        
        success = await account_manager.switch_account("test_github_01")
        assert success is False
    
    async def test_switch_to_account_with_no_quota(self, account_manager):
        """Test switching to account with no quota"""
        # Set quota to 0
        account_manager.accounts["test_github_01"].quota_remaining = 0
        
        success = await account_manager.switch_account("test_github_01")
        assert success is False
    
    async def test_create_account(self, account_manager):
        """Test creating a new account"""
        account_id = await account_manager.create_account(
            name="New Test Account",
            account_type=AccountType.USER,
            email="new@example.com",
            provider="opencode",
            quota_limit=2000,
            models_preferred=["raptor-mini"],
            priority=3
        )
        
        assert account_id in account_manager.accounts
        new_account = account_manager.accounts[account_id]
        assert new_account.name == "New Test Account"
        assert new_account.provider == "opencode"
        assert new_account.quota_limit == 2000
        assert new_account.quota_remaining == 2000
    
    async def test_get_recommended_account(self, account_manager):
        """Test getting recommended account"""
        # Test with reasoning task
        recommended = await account_manager.get_recommended_account("reasoning")
        assert recommended is not None
        assert recommended.account_id in account_manager.accounts
        
        # Test with code task
        recommended = await account_manager.get_recommended_account("code")
        assert recommended is not None
        assert recommended.account_id in account_manager.accounts
    
    async def test_get_recommended_account_no_available(self, account_manager):
        """Test getting recommended account when none available"""
        # Set all accounts to inactive
        for account in account_manager.accounts.values():
            account.status = AccountStatus.INACTIVE
        
        recommended = await account_manager.get_recommended_account("general")
        assert recommended is None
    
    async def test_update_usage_stats(self, account_manager):
        """Test updating usage statistics"""
        account_id = "test_github_01"
        
        # Update with successful request
        await account_manager.update_usage_stats(account_id, True, 1.5)
        
        account = account_manager.accounts[account_id]
        assert account.usage_stats["total_requests"] == 1
        assert account.usage_stats["successful_requests"] == 1
        assert account.usage_stats["failed_requests"] == 0
        assert account.usage_stats["avg_response_time"] == 1.5
    
    async def test_suspend_and_activate_account(self, account_manager):
        """Test suspending and activating accounts"""
        account_id = "test_github_01"
        
        # Suspend account
        success = await account_manager.suspend_account(account_id, "Testing suspension")
        assert success is True
        assert account_manager.accounts[account_id].status == AccountStatus.SUSPENDED
        
        # Activate account
        success = await account_manager.activate_account(account_id)
        assert success is True
        assert account_manager.accounts[account_id].status == AccountStatus.ACTIVE
    
    async def test_get_usage_report(self, account_manager):
        """Test generating usage report"""
        report = await account_manager.get_usage_report()
        
        assert "total_accounts" in report
        assert "active_accounts" in report
        assert "account_details" in report
        assert len(report["account_details"]) == 2
        
        # Check account details structure
        account_detail = report["account_details"][0]
        assert "account_id" in account_detail
        assert "quota_percent" in account_detail
        assert "success_rate" in account_detail
    
    async def test_cleanup_expired_accounts(self, account_manager):
        """Test cleaning up expired accounts"""
        # Create an expired account
        expired_account = AccountInfo(
            account_id="expired_test",
            name="Expired Test",
            account_type=AccountType.USER,
            status=AccountStatus.ACTIVE,
            created_at=datetime.now(),
            last_used=datetime.now() - timedelta(days=100),  # 100 days ago
            email="expired@example.com",
            provider="test",
            quota_remaining=100,
            quota_limit=100,
            models_preferred=[],
            priority=1,
            api_key=None,
            usage_stats={}
        )
        
        account_manager.accounts["expired_test"] = expired_account
        
        # Clean up expired accounts
        deleted_count = await account_manager.cleanup_expired_accounts(days_old=90)
        
        assert deleted_count == 1
        assert "expired_test" not in account_manager.accounts


class TestAgentAccountIntegration:
    """Test agent account integration"""
    
    @pytest.fixture
    async def agent_account_manager(self):
        """Create a test agent account manager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            # Create test accounts
            test_accounts = {
                "accounts": [
                    {
                        "id": "agent_test_01",
                        "name": "Agent Test Account",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "agent@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5"],
                        "priority": 1,
                        "api_key": "test_key",
                        "usage_stats": {
                            "total_requests": 0,
                            "successful_requests": 0,
                            "failed_requests": 0,
                            "avg_response_time": 0.0
                        }
                    }
                ]
            }
            
            # Write test config
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            # Create agent account manager
            manager = AgentAccountManager()
            manager.account_manager = AccountManager(config_path)
            await manager.account_manager.initialize()
            
            yield manager
    
    async def test_get_current_account_for_agent(self, agent_account_manager):
        """Test getting current account for agent"""
        account = await agent_account_manager.get_current_account_for_agent("test_agent")
        assert account is not None
        assert account.account_id == "agent_test_01"
    
    async def test_switch_account_for_agent(self, agent_account_manager):
        """Test switching account for agent"""
        success = await agent_account_manager.switch_account_for_agent(
            "test_agent", "agent_test_01"
        )
        assert success is True
    
    async def test_execute_with_account(self, agent_account_manager):
        """Test executing task with specific account"""
        async def test_task():
            return {"result": "success", "account_used": "agent_test_01"}
        
        result = await agent_account_manager.execute_with_account(
            "test_agent", "agent_test_01", test_task
        )
        
        assert result["result"] == "success"
        assert result["account_used"] == "agent_test_01"
    
    async def test_execute_with_recommended_account(self, agent_account_manager):
        """Test executing task with recommended account"""
        async def test_task():
            return {"result": "success"}
        
        result = await agent_account_manager.execute_with_recommended_account(
            "test_agent", test_task, "general"
        )
        
        assert result["result"] == "success"
    
    async def test_validate_agent_account_access(self, agent_account_manager):
        """Test validating agent account access"""
        # Valid access
        valid = await agent_account_manager.validate_agent_account_access(
            "test_agent", "agent_test_01", "execute_task"
        )
        assert valid is True
        
        # Invalid account
        invalid = await agent_account_manager.validate_agent_account_access(
            "test_agent", "nonexistent", "execute_task"
        )
        assert invalid is False


class TestAccountAwareAgent:
    """Test account-aware agent functionality"""
    
    @pytest.fixture
    async def account_aware_agent(self):
        """Create a test account-aware agent"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            # Create test accounts
            test_accounts = {
                "accounts": [
                    {
                        "id": "agent_test_01",
                        "name": "Agent Test Account",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "agent@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5"],
                        "priority": 1,
                        "api_key": "test_key",
                        "usage_stats": {
                            "total_requests": 0,
                            "successful_requests": 0,
                            "failed_requests": 0,
                            "avg_response_time": 0.0
                        }
                    }
                ]
            }
            
            # Write test config
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            # Create agent
            agent = AccountAwareAgent("test_agent")
            agent.account_manager.account_manager = AccountManager(config_path)
            await agent.account_manager.account_manager.initialize()
            
            yield agent
    
    async def test_agent_initialization(self, account_aware_agent):
        """Test agent initialization"""
        await account_aware_agent.initialize()
        assert account_aware_agent.agent_id == "test_agent"
    
    async def test_agent_get_current_account(self, account_aware_agent):
        """Test agent getting current account"""
        account = await account_aware_agent.get_current_account()
        assert account is not None
        assert account.account_id == "agent_test_01"
    
    async def test_agent_switch_account(self, account_aware_agent):
        """Test agent switching account"""
        success = await account_aware_agent.switch_account("agent_test_01")
        assert success is True
    
    async def test_agent_execute_with_account(self, account_aware_agent):
        """Test agent executing with specific account"""
        async def test_task():
            return {"result": "success"}
        
        result = await account_aware_agent.execute_with_account(
            "agent_test_01", test_task
        )
        
        assert result["result"] == "success"
    
    async def test_agent_perform_task(self, account_aware_agent):
        """Test agent performing task with intelligent account selection"""
        async def test_task():
            return {"result": "success"}
        
        result = await account_aware_agent.perform_task(test_task, "general")
        assert result["result"] == "success"


class TestAccountContext:
    """Test account context management"""
    
    @pytest.fixture
    async def account_manager(self):
        """Create a test account manager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            # Create test accounts
            test_accounts = {
                "accounts": [
                    {
                        "id": "context_test_01",
                        "name": "Context Test Account 1",
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
                        "api_key": "test_key_1",
                        "usage_stats": {}
                    },
                    {
                        "id": "context_test_02",
                        "name": "Context Test Account 2",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "context2@example.com",
                        "provider": "gemini",
                        "quota_remaining": 500,
                        "quota_limit": 1000,
                        "models_preferred": ["gemini-3-pro"],
                        "priority": 2,
                        "api_key": "test_key_2",
                        "usage_stats": {}
                    }
                ]
            }
            
            # Write test config
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            # Create account manager
            manager = AccountManager(config_path)
            await manager.initialize()
            
            yield manager
    
    async def test_account_context_preservation(self, account_manager):
        """Test that account context is preserved and restored"""
        original_account = account_manager.get_current_account()
        
        async with AgentAccountContext("test_agent", account_manager):
            # Switch to different account
            await account_manager.switch_account("context_test_02")
            current_account = account_manager.get_current_account()
            assert current_account.account_id == "context_test_02"
        
        # Should be restored to original
        restored_account = account_manager.get_current_account()
        assert restored_account.account_id == original_account.account_id


class TestEndToEndWorkflows:
    """Test end-to-end multi-account workflows"""
    
    @pytest.fixture
    async def full_system(self):
        """Create a full test system"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_accounts.yaml")
            
            # Create comprehensive test accounts
            test_accounts = {
                "accounts": [
                    {
                        "id": "e2e_github_01",
                        "name": "GitHub Account 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "github1@example.com",
                        "provider": "github",
                        "quota_remaining": 1000,
                        "quota_limit": 1000,
                        "models_preferred": ["haiku-4.5", "sonnet-4.5"],
                        "priority": 1,
                        "api_key": "github_key_1",
                        "usage_stats": {"total_requests": 0, "successful_requests": 0, "failed_requests": 0, "avg_response_time": 0.0}
                    },
                    {
                        "id": "e2e_gemini_01",
                        "name": "Gemini Account 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "gemini1@example.com",
                        "provider": "gemini",
                        "quota_remaining": 800,
                        "quota_limit": 1000,
                        "models_preferred": ["gemini-3-pro"],
                        "priority": 2,
                        "api_key": "gemini_key_1",
                        "usage_stats": {"total_requests": 0, "successful_requests": 0, "failed_requests": 0, "avg_response_time": 0.0}
                    },
                    {
                        "id": "e2e_opencode_01",
                        "name": "OpenCode Account 1",
                        "type": "user",
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "last_used": None,
                        "email": "opencode1@example.com",
                        "provider": "opencode",
                        "quota_remaining": 1200,
                        "quota_limit": 1500,
                        "models_preferred": ["raptor-mini"],
                        "priority": 3,
                        "api_key": "opencode_key_1",
                        "usage_stats": {"total_requests": 0, "successful_requests": 0, "failed_requests": 0, "avg_response_time": 0.0}
                    }
                ]
            }
            
            # Write test config
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(test_accounts, f)
            
            # Create systems
            account_manager = AccountManager(config_path)
            await account_manager.initialize()
            
            agent_account_manager = AgentAccountManager()
            agent_account_manager.account_manager = account_manager
            
            agent = AccountAwareAgent("e2e_test_agent")
            agent.account_manager = agent_account_manager
            
            yield {
                "account_manager": account_manager,
                "agent_account_manager": agent_account_manager,
                "agent": agent
            }
    
    async def test_multi_account_workflow(self, full_system):
        """Test a complete multi-account workflow"""
        account_manager = full_system["account_manager"]
        agent = full_system["agent"]
        
        # 1. Get initial state
        initial_account = account_manager.get_current_account()
        assert initial_account is not None
        
        # 2. Create a new account
        new_account_id = await account_manager.create_account(
            name="Workflow Test Account",
            account_type=AccountType.USER,
            email="workflow@example.com",
            provider="antigravity",
            quota_limit=2000,
            models_preferred=["opus-4.6-thinking"],
            priority=1
        )
        
        # 3. Switch to new account
        success = await account_manager.switch_account(new_account_id)
        assert success is True
        
        # 4. Verify switch
        current_account = account_manager.get_current_account()
        assert current_account.account_id == new_account_id
        
        # 5. Get recommended account for reasoning
        recommended = await account_manager.get_recommended_account("reasoning")
        assert recommended is not None
        
        # 6. Execute task with agent
        async def reasoning_task():
            return {"analysis": "completed", "model": "opus-4.6-thinking"}
        
        result = await agent.perform_task(reasoning_task, "reasoning")
        assert result["analysis"] == "completed"
        
        # 7. Generate usage report
        report = await account_manager.get_usage_report()
        assert report["total_accounts"] >= 4  # Original 3 + new 1
        
        # 8. Suspend an account
        success = await account_manager.suspend_account("e2e_github_01", "Testing suspension")
        assert success is True
        
        # 9. Verify suspended account is not recommended
        recommended = await account_manager.get_recommended_account("code")
        assert recommended.account_id != "e2e_github_01"
    
    async def test_account_rotation_workflow(self, full_system):
        """Test account rotation based on quota and priority"""
        account_manager = full_system["account_manager"]
        
        # Set different quota levels
        account_manager.accounts["e2e_github_01"].quota_remaining = 100
        account_manager.accounts["e2e_gemini_01"].quota_remaining = 500
        account_manager.accounts["e2e_opencode_01"].quota_remaining = 1000
        
        # Test quota-aware selection
        recommended = await account_manager.get_recommended_account("general")
        
        # Should prefer account with most quota remaining
        assert recommended.account_id == "e2e_opencode_01"
        
        # Test priority-based selection when quotas are similar
        account_manager.accounts["e2e_github_01"].quota_remaining = 800
        account_manager.accounts["e2e_gemini_01"].quota_remaining = 800
        account_manager.accounts["e2e_opencode_01"].quota_remaining = 800
        
        recommended = await account_manager.get_recommended_account("general")
        
        # Should prefer account with highest priority (lowest number)
        assert recommended.account_id == "e2e_github_01"  # priority 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])