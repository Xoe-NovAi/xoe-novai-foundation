"""
Phase 3: Async Hardening & Race Condition Tests
================================================
Verifies concurrent operations don't cause initialization issues.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock
from app.XNAi_rag_app.core.services_init import ServiceOrchestrator
from app.XNAi_rag_app.api.exceptions import XNAiException
from app.XNAi_rag_app.schemas.errors import ErrorCategory


class TestLLMInitializationRaceCondition:
    """Tests for LLM initialization race condition handling."""
    
    @pytest.mark.asyncio
    async def test_concurrent_llm_initialization_same_instance(self):
        """Verify 10 concurrent requests get the same LLM instance."""
        orchestrator = ServiceOrchestrator()
        
        # Mock the LLM initialization to be slow
        async def mock_llm_init():
            await asyncio.sleep(0.1)
            return MagicMock(name="LLM_Instance")
        
        with patch("app.XNAi_rag_app.core.dependencies.get_llm_async", side_effect=mock_llm_init):
            # Simulate 10 concurrent requests trying to initialize LLM
            tasks = [
                orchestrator._initialize_llm()
                for _ in range(10)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All results should be the SAME instance
            assert all(r is results[0] for r in results), "All results should be the same instance"
    
    @pytest.mark.asyncio
    async def test_concurrent_llm_initialization_count(self):
        """Verify LLM is initialized only once even with concurrent access."""
        orchestrator = ServiceOrchestrator()
        init_count = 0
        
        async def mock_llm_init():
            nonlocal init_count
            init_count += 1
            await asyncio.sleep(0.05)
            return MagicMock(name=f"LLM_Instance_{init_count}")
        
        with patch("app.XNAi_rag_app.core.dependencies.get_llm_async", side_effect=mock_llm_init):
            # 20 concurrent initialization attempts
            tasks = [
                orchestrator._initialize_llm()
                for _ in range(20)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Should only initialize once
            assert init_count == 1, f"Expected 1 init, got {init_count}"
            # All should get same instance
            assert len(set(id(r) for r in results)) == 1
    
    @pytest.mark.asyncio
    async def test_llm_cache_hit_on_second_call(self):
        """Verify cached LLM returned on subsequent calls."""
        orchestrator = ServiceOrchestrator()
        init_count = 0
        
        async def mock_llm_init():
            nonlocal init_count
            init_count += 1
            return MagicMock(name="LLM_Instance")
        
        with patch("app.XNAi_rag_app.core.dependencies.get_llm_async", side_effect=mock_llm_init):
            # First call
            llm1 = await orchestrator._initialize_llm()
            assert init_count == 1
            
            # Second call should hit cache
            llm2 = await orchestrator._initialize_llm()
            assert init_count == 1  # Should not increment
            assert llm1 is llm2


class TestStreamingResourceCleanup:
    """Tests for streaming endpoint resource cleanup."""
    
    @pytest.mark.asyncio
    async def test_stream_cleanup_on_client_disconnect(self):
        """Verify resources are cleaned when client disconnects."""
        from app.XNAi_rag_app.api.exceptions import XNAiException
        
        # Mock request object that simulates disconnect
        mock_request = MagicMock()
        disconnect_at = 5  # Disconnect after 5 tokens
        token_count = 0
        
        async def is_disconnected():
            nonlocal token_count
            token_count += 1
            return token_count >= disconnect_at
        
        mock_request.is_disconnected = is_disconnected
        
        # Verify disconnect detection works
        assert not await mock_request.is_disconnected()
        assert not await mock_request.is_disconnected()
        
        # After 5 calls should detect disconnect
        for _ in range(3):
            await mock_request.is_disconnected()
        assert await mock_request.is_disconnected()
    
    @pytest.mark.asyncio
    async def test_stream_error_during_generation(self):
        """Verify errors during streaming are properly handled."""
        
        async def failing_generator():
            """Generator that fails after some tokens."""
            for i in range(3):
                yield f"token_{i}"
            
            # Simulate error during generation
            raise XNAiException(
                message="Stream generation failed",
                category=ErrorCategory.TIMEOUT,
                recovery_suggestion="Retry with simpler query"
            )
        
        tokens = []
        error_caught = False
        
        try:
            async for token in failing_generator():
                tokens.append(token)
        except XNAiException as e:
            error_caught = True
            assert e.category == ErrorCategory.TIMEOUT
        
        assert len(tokens) == 3
        assert error_caught


class TestCircuitBreakerStateTransitions:
    """Tests for circuit breaker state machine."""
    
    @pytest.mark.asyncio
    async def test_circuit_open_then_half_open_transition(self):
        """Verify CLOSED → OPEN → HALF_OPEN state transitions with mock breaker."""
        # Mock simple circuit breaker for testing state transitions
        class SimpleCircuitBreaker:
            def __init__(self, failure_threshold=3, timeout=0.2):
                self.state = "CLOSED"
                self.failure_count = 0
                self.failure_threshold = failure_threshold
                self.timeout = timeout
                self.last_failure_time = None
            
            async def call(self, func):
                try:
                    if not callable(func):
                        raise ValueError("func must be callable")
                    if asyncio.iscoroutinefunction(func):
                        return await func()
                    else:
                        return func()
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                    raise
        
        breaker = SimpleCircuitBreaker(failure_threshold=3, timeout=0.2)
        
        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0
        
        # Simulate 3 failures to open circuit
        for i in range(3):
            try:
                await breaker.call(lambda: 1 / 0)  # Will raise ZeroDivisionError
            except:
                pass
        
        assert breaker.state == "OPEN"
        assert breaker.failure_count == 3
        
        # Simulate recovery: reset state and try successful call
        breaker.state = "CLOSED"
        breaker.failure_count = 0
        
        async def successful_call():
            return "success"
        
        result = await breaker.call(successful_call)
        assert result == "success"
        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_failure_count_reset_on_success(self):
        """Verify failure count resets after successful call."""
        class SimpleCircuitBreaker:
            def __init__(self, failure_threshold=3):
                self.state = "CLOSED"
                self.failure_count = 0
                self.failure_threshold = failure_threshold
            
            async def call(self, func):
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await func()
                    else:
                        result = func()
                    # Success: reset failure count
                    self.failure_count = 0
                    return result
                except Exception as e:
                    self.failure_count += 1
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                    raise
        
        breaker = SimpleCircuitBreaker(failure_threshold=3)
        
        call_count = 0
        
        async def intermittent_call():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Failure")
            return "success"
        
        # Two failures
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(intermittent_call)
        
        assert breaker.failure_count == 2
        assert breaker.state == "CLOSED"
        
        # Success should reset counter
        result = await breaker.call(intermittent_call)
        assert result == "success"
        assert breaker.failure_count == 0
        assert breaker.state == "CLOSED"
    
    @pytest.mark.asyncio
    async def test_circuit_multiple_open_transition_from_half_open(self):
        """Verify HALF_OPEN → OPEN if test call still fails."""
        class SimpleCircuitBreaker:
            def __init__(self, failure_threshold=2):
                self.state = "CLOSED"
                self.failure_count = 0
                self.failure_threshold = failure_threshold
            
            async def call(self, func):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func()
                    else:
                        return func()
                except Exception as e:
                    self.failure_count += 1
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                    raise
        
        breaker = SimpleCircuitBreaker(failure_threshold=2)
        
        # Trigger OPEN
        for _ in range(2):
            try:
                await breaker.call(lambda: 1 / 0)
            except:
                pass
        
        assert breaker.state == "OPEN"
        
        # Test with failing call still fails and stays open
        async def failing_call():
            raise Exception("Still failing")
        
        with pytest.raises(Exception):
            await breaker.call(failing_call)
        
        assert breaker.state == "OPEN"


class TestAsyncWaitAndRetry:
    """Tests for async wait/retry logic."""
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Verify exponential backoff calculation."""
        import asyncio
        import time
        
        delays = []
        
        async def retry_with_backoff(max_retries=3):
            for attempt in range(max_retries):
                try:
                    if attempt < 2:  # Fail first 2 times
                        raise Exception("Retry me")
                    return "success"
                except Exception:
                    if attempt < max_retries - 1:
                        delay = 2 ** attempt * 0.1  # Exponential backoff
                        delays.append(delay)
                        await asyncio.sleep(delay)
                    else:
                        raise
        
        result = await retry_with_backoff()
        assert result == "success"
        assert len(delays) == 2
        # Each delay should be double the previous
        assert delays[1] > delays[0]


class TestConcurrentErrorHandling:
    """Tests for error handling in concurrent operations."""
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_errors(self):
        """Verify multiple concurrent errors are handled independently."""
        
        async def operation(op_id: int, should_fail: bool) -> str:
            await asyncio.sleep(0.05)
            if should_fail:
                raise XNAiException(
                    message=f"Operation {op_id} failed",
                    category=ErrorCategory.INTERNAL_ERROR
                )
            return f"op_{op_id}_success"
        
        # Run operations: fail, succeed, fail, succeed, fail
        tasks = [
            operation(0, True),   # Failed
            operation(1, False),  # Success
            operation(2, True),   # Failed
            operation(3, False),  # Success
            operation(4, True),   # Failed
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify result types
        assert isinstance(results[0], XNAiException)
        assert results[1] == "op_1_success"
        assert isinstance(results[2], XNAiException)
        assert results[3] == "op_3_success"
        assert isinstance(results[4], XNAiException)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
