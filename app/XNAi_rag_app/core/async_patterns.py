"""
AnyIO Structured Concurrency Patterns
======================================

Enterprise-grade structured concurrency replacing fragile asyncio.gather patterns.
Provides zero-leak async operations with graceful cancellation and timeout handling.

Week 2 Implementation - January 15-16, 2026
"""

import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable, Awaitable
from contextlib import asynccontextmanager
import time

import anyio
from anyio import create_task_group, move_on_after, sleep, create_memory_object_stream
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

logger = logging.getLogger(__name__)

class StructuredConcurrencyManager:
    """
    Enterprise structured concurrency manager with timeout and cancellation support.

    Replaces asyncio.gather with anyio.create_task_group for better error handling
    and resource cleanup.
    """

    def __init__(self, default_timeout: float = 30.0):
        self.default_timeout = default_timeout
        self.active_tasks: Dict[str, anyio.CancelScope] = {}

    @asynccontextmanager
    async def managed_task_group(self, name: str = "task_group"):
        """Context manager for structured task groups with automatic cleanup."""
        async with create_task_group() as tg:
            task_id = f"{name}_{id(tg)}"
            logger.debug(f"Starting structured task group: {task_id}")

            try:
                yield tg
            finally:
                logger.debug(f"Completed structured task group: {task_id}")

    async def run_with_timeout(
        self,
        coro: Awaitable[Any],
        timeout: Optional[float] = None,
        name: str = "operation"
    ) -> Any:
        """
        Run coroutine with timeout protection.

        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds (uses default if None)
            name: Operation name for logging

        Returns:
            Coroutine result

        Raises:
            TimeoutError: If operation times out
        """
        timeout = timeout or self.default_timeout

        with move_on_after(timeout) as cancel_scope:
            start_time = time.time()
            try:
                result = await coro
                duration = time.time() - start_time
                logger.debug(f"Operation '{name}' completed in {duration:.2f}s")
                return result
            except BaseException:
                if cancel_scope.cancelled_caught:
                    duration = time.time() - start_time
                    logger.warning(f"Operation '{name}' timed out after {duration:.2f}s (limit: {timeout}s)")
                    raise TimeoutError(f"Operation '{name}' timed out after {timeout}s")
                raise

    async def gather_concurrent(
        self,
        operations: Dict[str, Awaitable[Any]],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Structured concurrent execution replacing asyncio.gather.

        Args:
            operations: Dict of operation_name -> coroutine
            timeout: Overall timeout for all operations

        Returns:
            Dict of operation_name -> result

        Raises:
            Exception: If any operation fails (others are cancelled)
        """
        results = {}
        errors = {}

        async def run_operation(name: str, coro: Awaitable[Any]):
            """Run single operation with error capture."""
            try:
                result = await coro
                results[name] = result
                logger.debug(f"Concurrent operation '{name}' completed successfully")
            except Exception as e:
                errors[name] = e
                logger.error(f"Concurrent operation '{name}' failed: {e}")
                raise  # Cancel other operations

        timeout = timeout or self.default_timeout

        with move_on_after(timeout) as cancel_scope:
            async with create_task_group() as tg:
                # Start all operations concurrently
                for name, coro in operations.items():
                    tg.start_soon(run_operation, name, coro)

        if cancel_scope.cancelled_caught:
            failed_ops = list(operations.keys())
            logger.error(f"Concurrent operations timed out after {timeout}s: {failed_ops}")
            raise TimeoutError(f"Concurrent operations timed out: {failed_ops}")

        if errors:
            failed_ops = list(errors.keys())
            logger.error(f"Concurrent operations failed: {failed_ops}")
            # Re-raise first error
            first_error = next(iter(errors.values()))
            raise first_error

        return results

    async def pipeline_operations(
        self,
        operations: List[Callable[[Any], Awaitable[Any]]],
        initial_input: Any = None,
        timeout_per_step: Optional[float] = None
    ) -> Any:
        """
        Execute operations in pipeline with structured concurrency.

        Args:
            operations: List of functions that take previous result and return coroutine
            initial_input: Initial input for first operation
            timeout_per_step: Timeout per pipeline step

        Returns:
            Final pipeline result
        """
        current_result = initial_input

        for i, operation in enumerate(operations):
            step_name = f"pipeline_step_{i}"
            coro = operation(current_result)

            current_result = await self.run_with_timeout(
                coro,
                timeout=timeout_per_step,
                name=step_name
            )

        return current_result

class VoiceProcessingPipeline:
    """
    Structured concurrency pipeline for voice RAG processing.

    Replaces asyncio.gather patterns in voice processing with
    anyio task groups for better error handling and cancellation.
    """

    def __init__(self, concurrency_manager: StructuredConcurrencyManager):
        self.manager = concurrency_manager

    async def process_voice_rag_pipeline(
        self,
        audio_data: bytes,
        user_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process voice through RAG pipeline with structured concurrency.

        Args:
            audio_data: Raw audio bytes
            user_query: Optional pre-transcribed query

        Returns:
            Dict containing transcription, context, response, audio
        """
        results = {}

        # Step 1: Concurrent transcription and context preparation
        logger.info("Starting voice RAG pipeline with structured concurrency")

        concurrent_ops = {}

        # Transcription (if not provided)
        if user_query is None:
            concurrent_ops["transcription"] = self._transcribe_audio(audio_data)
        else:
            results["transcription"] = user_query

        # Initial context retrieval (if we have query)
        if user_query:
            concurrent_ops["initial_context"] = self._get_initial_context(user_query)

        # Execute concurrent operations
        if concurrent_ops:
            concurrent_results = await self.manager.gather_concurrent(
                concurrent_ops,
                timeout=15.0  # 15 second timeout for STT
            )
            results.update(concurrent_results)

        # Step 2: Sequential RAG processing
        transcription = results.get("transcription") or user_query
        if not transcription:
            raise ValueError("No transcription available")

        # Pipeline: RAG retrieval -> AI generation -> TTS
        pipeline_ops = [
            lambda ctx: self._refine_context(transcription, ctx),
            lambda refined_ctx: self._generate_ai_response(transcription, refined_ctx),
            lambda ai_response: self._generate_voice_response(ai_response)
        ]

        # Execute pipeline with timeout per step
        final_result = await self.manager.pipeline_operations(
            pipeline_ops,
            initial_input=results.get("initial_context"),
            timeout_per_step=30.0  # 30 seconds per pipeline step
        )

        results["final_audio"] = final_result
        logger.info("Voice RAG pipeline completed successfully")

        return results

    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio to text."""
        # Placeholder - integrate with actual STT
        await sleep(0.1)  # Simulate processing time
        return "Transcribed text from audio"

    async def _get_initial_context(self, query: str) -> Dict[str, Any]:
        """Get initial context for query."""
        # Placeholder - integrate with retrievers
        await sleep(0.05)  # Simulate processing time
        return {"sources": [], "content": ""}

    async def _refine_context(self, query: str, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refine context based on transcription."""
        # Placeholder - integrate with hybrid retrievers
        await sleep(0.1)  # Simulate processing time
        return {
            "query": query,
            "context": initial_context.get("content", ""),
            "sources": initial_context.get("sources", [])
        }

    async def _generate_ai_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate AI response."""
        # Placeholder - integrate with LLM
        await sleep(0.2)  # Simulate processing time
        return f"AI response to: {query}"

    async def _generate_voice_response(self, text: str) -> bytes:
        """Generate voice audio from text."""
        # Placeholder - integrate with TTS
        await sleep(0.1)  # Simulate processing time
        return b"audio_data_placeholder"

class StreamingResponseHandler:
    """
    Structured streaming with backpressure handling.

    Provides memory-efficient streaming with anyio streams.
    """

    def __init__(self, buffer_size: int = 10):
        self.buffer_size = buffer_size

    @asynccontextmanager
    async def create_stream_pair(self):
        """Create send/receive stream pair for structured streaming."""
        sender, receiver = create_memory_object_stream(self.buffer_size)
        try:
            yield sender, receiver
        finally:
            await sender.aclose()
            await receiver.aclose()

    async def stream_with_backpressure(
        self,
        items: AsyncGenerator[Any, None],
        sender: MemoryObjectSendStream[Any]
    ):
        """Stream items with backpressure handling."""
        try:
            async for item in items:
                await sender.send(item)
                # Small delay to prevent overwhelming receiver
                await sleep(0.01)
        except anyio.get_cancelled_exc_class():
            logger.info("Streaming cancelled gracefully")
        except Exception as e:
            logger.error(f"Streaming error: {e}")
        finally:
            await sender.aclose()

    async def consume_stream(
        self,
        receiver: MemoryObjectReceiveStream[Any],
        processor: Callable[[Any], Awaitable[None]]
    ):
        """Consume stream items with processing function."""
        try:
            async for item in receiver:
                await processor(item)
        except anyio.get_cancelled_exc_class():
            logger.info("Stream consumption cancelled gracefully")
        except Exception as e:
            logger.error(f"Stream consumption error: {e}")

# Global instances
concurrency_manager = StructuredConcurrencyManager(default_timeout=30.0)
voice_pipeline = VoiceProcessingPipeline(concurrency_manager)
streaming_handler = StreamingResponseHandler()

# Convenience functions for application use
async def run_voice_pipeline(audio_data: bytes, user_query: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for voice processing pipeline."""
    return await voice_pipeline.process_voice_rag_pipeline(audio_data, user_query)

async def run_with_timeout(coro: Awaitable[Any], timeout: float = 30.0, name: str = "operation") -> Any:
    """Convenience function for timeout-protected operations."""
    return await concurrency_manager.run_with_timeout(coro, timeout, name)

async def gather_concurrent(operations: Dict[str, Awaitable[Any]], timeout: float = 30.0) -> Dict[str, Any]:
    """Convenience function for structured concurrent execution."""
    return await concurrency_manager.gather_concurrent(operations, timeout)

# Migration helpers for existing asyncio.gather usage
async def migrate_from_asyncio_gather(*coros: Awaitable[Any], timeout: float = 30.0) -> List[Any]:
    """
    Migration helper to replace asyncio.gather calls.

    Usage:
        # Old: results = await asyncio.gather(coro1, coro2, coro3)
        # New: results = await migrate_from_asyncio_gather(coro1, coro2, coro3)
    """
    operations = {f"coro_{i}": coro for i, coro in enumerate(coros)}
    results = await concurrency_manager.gather_concurrent(operations, timeout)
    return [results[f"coro_{i}"] for i in range(len(coros))]
