#!/usr/bin/env python3
"""
Test script for rate limit handling and context preservation.

This script tests the enhanced multi-account system's ability to:
1. Detect rate limits automatically
2. Rotate accounts when hitting limits
3. Preserve context across account switches
4. Recover from context loss

Author: XNAi Foundation
Version: 1.0.0
"""

import asyncio
import json
import tempfile
import os
import yaml
from datetime import datetime
from pathlib import Path

from app.XNAi_rag_app.core.rate_limit_handler import (
    RateLimitDetector,
    ContextManager,
    AccountRotator,
    SmartDispatcher
)


class MockCLI:
    """Mock CLI for testing rate limit scenarios"""
    
    def __init__(self, account_id: str, provider: str):
        self.account_id = account_id
        self.provider = provider
        self.rate_limit_count = 0
        self.context_preserved = True
    
    async def chat(self, task: str, timeout_sec: float = 30.0) -> dict:
        """Simulate CLI chat with rate limit scenarios"""
        self.rate_limit_count += 1
        
        # Simulate rate limit on 3rd call
        if self.rate_limit_count >= 3:
            return {
                "success": False,
                "error": f"Rate limit exceeded for {self.account_id}. Too many requests. Retry after 60 seconds.",
                "account_id": self.account_id
            }
        
        # Simulate context loss on 2nd call
        if self.rate_limit_count == 2:
            self.context_preserved = False
            return {
                "success": False,
                "error": f"Session lost for {self.account_id}. Starting new session.",
                "account_id": self.account_id
            }
        
        # Success case
        return {
            "success": True,
            "output": f"Response from {self.account_id}: {task[:50]}...",
            "account_id": self.account_id
        }


class RateLimitTestSuite:
    """Test suite for rate limit handling"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.test_results = []
    
    def _setup_logger(self):
        """Setup test logger"""
        import logging
        logger = logging.getLogger("RateLimitTestSuite")
        logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        self.logger.info(f"[{status}] {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_rate_limit_detection(self):
        """Test rate limit detection from response text"""
        self.logger.info("Testing rate limit detection...")
        
        # Test cases
        test_cases = [
            ("429 Too Many Requests", True, "http_429"),
            ("Rate limit exceeded", True, "http_429"),
            ("DeepSeek rate limit exceeded", True, "deepseek"),
            ("Minimax quota exceeded", True, "minimax"),
            ("OpenCode 429 error", True, "opencode"),
            ("Session lost", False, "unknown"),  # Context loss, not rate limit
            ("Normal response", False, "unknown"),
        ]
        
        all_passed = True
        for response_text, expected_is_rate_limit, expected_type in test_cases:
            is_rate_limit, error_type = RateLimitDetector.detect_rate_limit(response_text)
            
            passed = (is_rate_limit == expected_is_rate_limit and 
                     (not expected_is_rate_limit or error_type == expected_type))
            
            self.log_result(
                f"Rate limit detection: '{response_text[:30]}...'",
                passed,
                f"Expected: {expected_is_rate_limit}, Got: {is_rate_limit}"
            )
            
            if not passed:
                all_passed = False
        
        return all_passed
    
    async def test_context_loss_detection(self):
        """Test context loss detection from response text"""
        self.logger.info("Testing context loss detection...")
        
        # Test cases
        test_cases = [
            ("Session lost", True),
            ("Context lost", True),
            ("New session started", True),
            ("Session expired", True),
            ("Normal response", False),
            ("Rate limit exceeded", False),
        ]
        
        all_passed = True
        for response_text, expected in test_cases:
            is_context_loss = RateLimitDetector.detect_context_loss(response_text)
            
            passed = is_context_loss == expected
            self.log_result(
                f"Context loss detection: '{response_text[:30]}...'",
                passed,
                f"Expected: {expected}, Got: {is_context_loss}"
            )
            
            if not passed:
                all_passed = False
        
        return all_passed
    
    async def test_retry_after_extraction(self):
        """Test retry-after time extraction"""
        self.logger.info("Testing retry-after extraction...")
        
        # Test cases
        test_cases = [
            ("Retry after 60 seconds", 60),
            ("Try again in 120 seconds", 120),
            ("Wait 30 seconds", 30),
            ("Rate limit, retry in 5 minutes", None),  # Not in seconds
            ("Normal response", None),
        ]
        
        all_passed = True
        for response_text, expected in test_cases:
            retry_after = RateLimitDetector.extract_retry_after(response_text)
            
            passed = retry_after == expected
            self.log_result(
                f"Retry-after extraction: '{response_text[:30]}...'",
                passed,
                f"Expected: {expected}, Got: {retry_after}"
            )
            
            if not passed:
                all_passed = False
        
        return all_passed
    
    async def test_context_manager(self):
        """Test context preservation and management"""
        self.logger.info("Testing context manager...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            context_manager = ContextManager(temp_dir)
            session_id = "test_session_123"
            
            # Test context saving and loading
            test_context = {
                "session_id": session_id,
                "messages": [
                    {"role": "user", "content": "Hello", "timestamp": "2026-03-05T00:00:00"},
                    {"role": "assistant", "content": "Hi there", "timestamp": "2026-03-05T00:00:01"}
                ],
                "context_window": [
                    {"role": "user", "content": "Hello", "timestamp": "2026-03-05T00:00:00"}
                ]
            }
            
            # Save context
            context_manager.save_context(session_id, test_context)
            
            # Load context
            loaded_context = context_manager.load_context(session_id)
            
            passed = loaded_context is not None and loaded_context["session_id"] == session_id
            self.log_result(
                "Context save/load",
                passed,
                f"Context saved and loaded successfully: {passed}"
            )
            
            if not passed:
                return False
            
            # Test message addition
            context_manager.add_message_to_context(session_id, "user", "New message")
            updated_context = context_manager.load_context(session_id)
            
            message_added = len(updated_context["messages"]) == 3
            self.log_result(
                "Message addition",
                message_added,
                f"Message added to context: {message_added}"
            )
            
            if not message_added:
                return False
            
            # Test context prompt generation
            context_prompt = context_manager.get_context_prompt(session_id)
            prompt_generated = len(context_prompt) > 0
            self.log_result(
                "Context prompt generation",
                prompt_generated,
                f"Context prompt generated: {prompt_generated}"
            )
            
            return prompt_generated
    
    async def test_account_rotator(self):
        """Test account rotation logic"""
        self.logger.info("Testing account rotator...")
        
        # Create test accounts
        accounts = [
            {"account_id": "account_01", "provider": "opencode"},
            {"account_id": "account_02", "provider": "opencode"},
            {"account_id": "account_03", "provider": "opencode"},
        ]
        
        rotator = AccountRotator(accounts)
        
        # Test initial availability
        account = rotator.get_next_available_account()
        initial_available = account is not None
        self.log_result(
            "Initial account availability",
            initial_available,
            f"Initial account available: {account}"
        )
        
        if not initial_available:
            return False
        
        # Test rate limit marking
        rotator.mark_rate_limit(account, 60)
        
        # Test that rate limited account is not immediately available
        account2 = rotator.get_next_available_account()
        rate_limit_respected = account2 != account
        self.log_result(
            "Rate limit respect",
            rate_limit_respected,
            f"Rate limited account not selected: {rate_limit_respected}"
        )
        
        if not rate_limit_respected:
            return False
        
        # Test stats
        stats = rotator.get_account_stats()
        stats_available = "total_accounts" in stats and stats["total_accounts"] == 3
        self.log_result(
            "Account stats",
            stats_available,
            f"Stats available with {stats['total_accounts']} accounts"
        )
        
        return stats_available
    
    async def test_smart_dispatcher(self):
        """Test smart dispatcher with mock CLI"""
        self.logger.info("Testing smart dispatcher...")
        
        # Create test accounts
        accounts = [
            {"account_id": "test_01", "provider": "opencode", "api_key": "test_key_1"},
            {"account_id": "test_02", "provider": "opencode", "api_key": "test_key_2"},
            {"account_id": "test_03", "provider": "opencode", "api_key": "test_key_3"},
        ]
        
        # Create context manager
        with tempfile.TemporaryDirectory() as temp_dir:
            context_manager = ContextManager(temp_dir)
            
            # Create smart dispatcher
            dispatcher = SmartDispatcher(accounts, context_manager)
            
            # Mock the CLI execution
            original_execute = dispatcher._execute_with_account
            
            async def mock_execute(account_id, task, session_id, timeout_sec):
                mock_cli = MockCLI(account_id, "opencode")
                return await mock_cli.chat(task, timeout_sec)
            
            dispatcher._execute_with_account = mock_execute
            
            # Test dispatch with rate limit handling
            result = await dispatcher.dispatch_with_rotation(
                task="Test task that will trigger rate limits",
                session_id="test_session",
                timeout_sec=10.0
            )
            
            # Check if fallback worked
            fallback_worked = result["success"] or result["attempt"] > 1
            self.log_result(
                "Smart dispatcher fallback",
                fallback_worked,
                f"Dispatcher attempted {result.get('attempt', 0)} times, success: {result.get('success', False)}"
            )
            
            # Check context preservation
            context_preserved = result.get("context_preserved", False)
            self.log_result(
                "Context preservation",
                context_preserved,
                f"Context preserved across account switches: {context_preserved}"
            )
            
            return fallback_worked and context_preserved
    
    async def test_end_to_end_scenario(self):
        """Test complete end-to-end scenario"""
        self.logger.info("Testing end-to-end scenario...")
        
        # Simulate the user's scenario: DeepSeek rate limit → Minimax fallback → context loss
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create accounts
            accounts = [
                {"account_id": "deepseek_01", "provider": "deepseek", "api_key": "deepseek_key"},
                {"account_id": "minimax_01", "provider": "minimax", "api_key": "minimax_key"},
                {"account_id": "opencode_01", "provider": "opencode", "api_key": "opencode_key"},
            ]
            
            context_manager = ContextManager(temp_dir)
            dispatcher = SmartDispatcher(accounts, context_manager)
            
            # Mock CLI that simulates the user's experience
            class UserScenarioCLI:
                def __init__(self):
                    self.call_count = 0
                
                async def chat(self, task, timeout_sec=10.0):
                    self.call_count += 1
                    
                    if self.call_count == 1:
                        # First call to DeepSeek - rate limit
                        return {
                            "success": False,
                            "error": "DeepSeek rate limit exceeded. Too many requests. Retry after 60 seconds.",
                            "account_id": "deepseek_01"
                        }
                    elif self.call_count == 2:
                        # Second call to Minimax - context loss
                        return {
                            "success": False,
                            "error": "Session lost. Starting new session.",
                            "account_id": "minimax_01"
                        }
                    else:
                        # Third call to OpenCode - success
                        return {
                            "success": True,
                            "output": "Task completed successfully with preserved context.",
                            "account_id": "opencode_01"
                        }
            
            user_cli = UserScenarioCLI()
            
            async def mock_execute(account_id, task, session_id, timeout_sec):
                return await user_cli.chat(task, timeout_sec)
            
            dispatcher._execute_with_account = mock_execute
            
            # Run the scenario
            result = await dispatcher.dispatch_with_rotation(
                task="Analyze the codebase architecture and provide recommendations",
                session_id="user_scenario_session",
                timeout_sec=10.0
            )
            
            # Verify the scenario worked
            scenario_success = (
                result["success"] and
                result.get("attempt", 0) >= 2 and
                result.get("account_used") == "opencode_01"
            )
            
            self.log_result(
                "End-to-end scenario",
                scenario_success,
                f"Scenario completed in {result.get('attempt', 0)} attempts using {result.get('account_used', 'unknown')}"
            )
            
            return scenario_success
    
    async def run_all_tests(self):
        """Run all tests"""
        self.logger.info("Starting Rate Limit Handling Test Suite")
        self.logger.info("=" * 60)
        
        test_methods = [
            self.test_rate_limit_detection,
            self.test_context_loss_detection,
            self.test_retry_after_extraction,
            self.test_context_manager,
            self.test_account_rotator,
            self.test_smart_dispatcher,
            self.test_end_to_end_scenario,
        ]
        
        results = []
        for test_method in test_methods:
            try:
                result = await test_method()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Test {test_method.__name__} failed with exception: {e}")
                results.append(False)
        
        # Generate summary
        total_tests = len(results)
        passed_tests = sum(results)
        failed_tests = total_tests - passed_tests
        
        self.logger.info("=" * 60)
        self.logger.info(f"Test Summary: {passed_tests}/{total_tests} tests passed")
        
        if failed_tests > 0:
            self.logger.warning(f"{failed_tests} tests failed")
        else:
            self.logger.info("All tests passed! ✅")
        
        # Save detailed results
        results_file = "rate_limit_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
                },
                "test_results": self.test_results
            }, f, indent=2)
        
        self.logger.info(f"Detailed results saved to: {results_file}")
        
        return failed_tests == 0


async def main():
    """Main test function"""
    test_suite = RateLimitTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All rate limit handling tests passed!")
        print("The enhanced multi-account system is ready to handle:")
        print("  ✅ Automatic rate limit detection")
        print("  ✅ Account rotation on rate limits")
        print("  ✅ Context preservation across switches")
        print("  ✅ Recovery from context loss")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))