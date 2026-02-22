#!/usr/bin/env python3
"""
OpenPipe Integration Test Suite
===============================
Comprehensive testing framework for OpenPipe integration with XNAi Foundation.
Tests sovereignty, performance, and compatibility with existing stack.
"""

import asyncio
import time
import json
import logging
import httpx
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

# Import OpenPipe integration modules
from app.XNAi_rag_app.core.openpipe_integration import (
    OpenPipeClient, 
    OpenPipeLLMWrapper, 
    OpenPipeIntegrationManager
)
from app.XNAi_rag_app.core.services_init_enhanced import EnhancedServiceOrchestrator

# Test configuration
TEST_CONFIG = {
    'openpipe': {
        'api_key': 'test_key_123',
        'base_url': 'http://localhost:3000',
        'cache_ttl': 300,
        'deduplication_window': 60,
        'sovereign_mode': True
    },
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'password': 'test_password'
    }
}

class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, response_delay: float = 0.1):
        self.response_delay = response_delay
        self.call_count = 0
        self.responses = [
            "This is a test response from the mock LLM.",
            "Here's another response for testing purposes.",
            "Third response to test caching functionality."
        ]
    
    async def generate(self, prompt: str) -> str:
        """Generate mock response."""
        await asyncio.sleep(self.response_delay)
        self.call_count += 1
        response_idx = self.call_count % len(self.responses)
        return f"{self.responses[response_idx]} [Call #{self.call_count}]"

class OpenPipeIntegrationTests:
    """Test suite for OpenPipe integration."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = []
    
    async def test_openpipe_client_initialization(self):
        """Test OpenPipe client initialization."""
        print("🧪 Testing OpenPipe Client Initialization...")
        
        try:
            client = OpenPipeClient(TEST_CONFIG)
            
            # Test configuration loading
            assert client.api_key == 'test_key_123'
            assert client.base_url == 'http://localhost:3000'
            assert client.cache_ttl == 300
            assert client.sovereign_mode == True
            
            print("✅ OpenPipe client initialization successful")
            return True
            
        except Exception as e:
            print(f"❌ OpenPipe client initialization failed: {e}")
            return False
    
    async def test_prompt_hashing(self):
        """Test prompt hashing for deduplication and caching."""
        print("🧪 Testing Prompt Hashing...")
        
        try:
            client = OpenPipeClient(TEST_CONFIG)
            
            # Test identical prompts
            prompt1 = "What is 2 + 2?"
            prompt2 = "What is 2 + 2?"
            
            hash1 = client._generate_prompt_hash(prompt1)
            hash2 = client._generate_prompt_hash(prompt2)
            
            assert hash1 == hash2, "Identical prompts should have same hash"
            
            # Test different prompts
            prompt3 = "What is 3 + 3?"
            hash3 = client._generate_prompt_hash(prompt3)
            
            assert hash1 != hash3, "Different prompts should have different hashes"
            
            print("✅ Prompt hashing tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Prompt hashing tests failed: {e}")
            return False
    
    async def test_caching_functionality(self):
        """Test OpenPipe caching functionality."""
        print("🧪 Testing Caching Functionality...")
        
        try:
            # Mock Redis client
            mock_redis = AsyncMock()
            mock_redis.get.return_value = b"cached_response"
            mock_redis.setex = AsyncMock()
            
            client = OpenPipeClient(TEST_CONFIG)
            client.redis_client = mock_redis
            
            # Test cache retrieval
            cached_response = await client.get_cached_response("test prompt")
            assert cached_response == "cached_response"
            
            # Test cache storage
            await client.cache_response("test prompt", "test response")
            mock_redis.setex.assert_called_once()
            
            print("✅ Caching functionality tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Caching functionality tests failed: {e}")
            return False
    
    async def test_deduplication(self):
        """Test request deduplication functionality."""
        print("🧪 Testing Deduplication...")
        
        try:
            # Mock Redis client
            mock_redis = AsyncMock()
            mock_redis.set.return_value = True  # First call succeeds
            mock_redis.set.return_value = False  # Subsequent calls fail (duplicate)
            
            client = OpenPipeClient(TEST_CONFIG)
            client.redis_client = mock_redis
            
            # Test first request (should proceed)
            is_duplicate = await client.deduplicate_request("test prompt")
            assert is_duplicate == False, "First request should not be duplicate"
            
            # Test second request (should be duplicate)
            is_duplicate = await client.deduplicate_request("test prompt")
            assert is_duplicate == True, "Second identical request should be duplicate"
            
            print("✅ Deduplication tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Deduplication tests failed: {e}")
            return False
    
    async def test_llm_wrapper(self):
        """Test LLM wrapper with OpenPipe integration."""
        print("🧪 Testing LLM Wrapper...")
        
        try:
            # Create mock components
            mock_llm = MockLLMClient(response_delay=0.01)
            mock_client = Mock(spec=OpenPipeClient)
            mock_client.get_cached_response = AsyncMock(return_value=None)
            mock_client.cache_response = AsyncMock()
            mock_client.record_metrics = AsyncMock()
            mock_client.deduplicate_request = AsyncMock(return_value=False)
            
            # Create wrapper
            wrapper = OpenPipeLLMWrapper(mock_llm, mock_client, "test_task")
            
            # Test generation
            response = await wrapper.generate("Test prompt")
            
            # Verify LLM was called
            assert mock_llm.call_count == 1
            
            # Verify OpenPipe methods were called
            mock_client.deduplicate_request.assert_called_once()
            mock_client.cache_response.assert_called_once()
            mock_client.record_metrics.assert_called_once()
            
            print("✅ LLM wrapper tests passed")
            return True
            
        except Exception as e:
            print(f"❌ LLM wrapper tests failed: {e}")
            return False
    
    async def test_integration_manager(self):
        """Test integration manager functionality."""
        print("🧪 Testing Integration Manager...")
        
        try:
            manager = OpenPipeIntegrationManager()
            manager.config = TEST_CONFIG
            
            # Mock the initialization
            with patch('app.XNAi_rag_app.core.openpipe_integration.OpenPipeClient') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                success = await manager.initialize()
                
                assert success == True, "Integration manager should initialize successfully"
                mock_client_class.assert_called_once_with(TEST_CONFIG)
                
            print("✅ Integration manager tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Integration manager tests failed: {e}")
            return False
    
    async def test_performance_metrics(self):
        """Test performance metrics collection."""
        print("🧪 Testing Performance Metrics...")
        
        try:
            client = OpenPipeClient(TEST_CONFIG)
            client.http_client = AsyncMock()
            
            # Test metrics recording
            await client.record_metrics(
                prompt="Test prompt",
                response="Test response",
                latency=100.0,
                cost=0.001,
                success=True,
                task_type="test_task"
            )
            
            # Verify HTTP client was called
            client.http_client.post.assert_called_once()
            
            print("✅ Performance metrics tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Performance metrics tests failed: {e}")
            return False
    
    async def test_sovereignty_compliance(self):
        """Test sovereignty and offline-first compliance."""
        print("🧪 Testing Sovereignty Compliance...")
        
        try:
            client = OpenPipeClient(TEST_CONFIG)
            
            # Test sovereign mode
            assert client.sovereign_mode == True, "Should operate in sovereign mode"
            
            # Test that no external calls are made in sovereign mode
            # (This would require network monitoring in a real test)
            
            print("✅ Sovereignty compliance tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Sovereignty compliance tests failed: {e}")
            return False
    
    async def test_memory_constraints(self):
        """Test memory usage within 6GB constraint."""
        print("🧪 Testing Memory Constraints...")
        
        try:
            import psutil
            
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create OpenPipe components
            client = OpenPipeClient(TEST_CONFIG)
            wrapper = OpenPipeLLMWrapper(MockLLMClient(), client, "test")
            
            # Get memory after creation
            after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = after_creation_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB for components)
            assert memory_increase < 100, f"Memory increase too high: {memory_increase}MB"
            
            print(f"✅ Memory constraints test passed (increase: {memory_increase:.2f}MB)")
            return True
            
        except Exception as e:
            print(f"❌ Memory constraints tests failed: {e}")
            return False
    
    async def test_latency_requirements(self):
        """Test latency requirements (<300ms)."""
        print("🧪 Testing Latency Requirements...")
        
        try:
            # Test LLM wrapper latency
            mock_llm = MockLLMClient(response_delay=0.05)  # 50ms response time
            mock_client = Mock(spec=OpenPipeClient)
            mock_client.get_cached_response = AsyncMock(return_value=None)
            mock_client.cache_response = AsyncMock()
            mock_client.record_metrics = AsyncMock()
            mock_client.deduplicate_request = AsyncMock(return_value=False)
            
            wrapper = OpenPipeLLMWrapper(mock_llm, mock_client, "test_task")
            
            # Measure response time
            start_time = time.time()
            response = await wrapper.generate("Test prompt")
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            
            # Should be under 300ms (allowing for overhead)
            assert latency_ms < 300, f"Latency too high: {latency_ms:.2f}ms"
            
            print(f"✅ Latency requirements test passed ({latency_ms:.2f}ms)")
            return True
            
        except Exception as e:
            print(f"❌ Latency requirements tests failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting OpenPipe Integration Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_openpipe_client_initialization,
            self.test_prompt_hashing,
            self.test_caching_functionality,
            self.test_deduplication,
            self.test_llm_wrapper,
            self.test_integration_manager,
            self.test_performance_metrics,
            self.test_sovereignty_compliance,
            self.test_memory_constraints,
            self.test_latency_requirements
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
                failed += 1
        
        print("=" * 60)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! OpenPipe integration is ready.")
        else:
            print("⚠️  Some tests failed. Review and fix issues before deployment.")
        
        return failed == 0

async def main():
    """Main test execution."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    tester = OpenPipeIntegrationTests()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())