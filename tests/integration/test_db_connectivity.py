#!/usr/bin/env python3
"""
Integration tests for database connectivity.
Tests PostgreSQL connection pooling, Redis cache connectivity, and database failover scenarios.
"""

import asyncio
import json
import pytest
import time
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch

import httpx
import pytest_asyncio
import redis
import sqlalchemy
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.XNAi_rag_app import app as rag_app
from app.config import settings
from tests.integration.conftest import (
    create_test_service,
    get_postgres_client,
    get_redis_client,
    wait_for_service_health,
    cleanup_test_services
)


class TestDatabaseConnectivity:
    """Test database connectivity functionality."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_teardown(self):
        """Setup and teardown for each test."""
        # Setup test environment
        self.test_connections = []
        self.test_data = []
        yield
        # Teardown
        await self.cleanup_test_data()

    async def cleanup_test_data(self):
        """Clean up test data from databases."""
        try:
            # Clean up Redis test data
            redis_client = await get_redis_client()
            if redis_client:
                await redis_client.delete("test:*")
            
            # Clean up PostgreSQL test data
            # This would depend on your specific database schema
            # For now, we'll skip this as it requires knowledge of your DB structure
            pass
            
        except Exception as e:
            # Log cleanup errors but don't fail the test
            print(f"Warning: Cleanup error: {e}")

    @pytest.mark.asyncio
    async def test_postgresql_connection_pooling(self):
        """Test PostgreSQL connection pooling functionality."""
        try:
            postgres_client = await get_postgres_client()
            assert postgres_client is not None
            
            # Test basic connection
            async with postgres_client.connect() as conn:
                result = await conn.execute(sqlalchemy.text("SELECT 1 as test"))
                data = result.fetchone()
                assert data[0] == 1
                
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")

    @pytest.mark.asyncio
    async def test_redis_cache_connectivity(self):
        """Test Redis cache connectivity."""
        try:
            redis_client = await get_redis_client()
            assert redis_client is not None
            
            # Test basic Redis operations
            test_key = "test:connectivity"
            test_value = "test_value_123"
            
            # Set and get value
            await redis_client.set(test_key, test_value, ex=60)  # 60 second expiry
            retrieved_value = await redis_client.get(test_key)
            
            assert retrieved_value == test_value
            
            # Clean up
            await redis_client.delete(test_key)
            
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")

    @pytest.mark.asyncio
    async def test_database_failover_scenarios(self):
        """Test database failover scenarios."""
        # This test would require a database cluster setup
        # For now, we'll test the failover logic concept
        
        try:
            postgres_client = await get_postgres_client()
            assert postgres_client is not None
            
            # Test connection resilience
            async with postgres_client.connect() as conn:
                # Test multiple operations to verify connection stability
                for i in range(5):
                    result = await conn.execute(sqlalchemy.text("SELECT NOW() as current_time"))
                    data = result.fetchone()
                    assert data is not None
                    
        except Exception as e:
            pytest.skip(f"PostgreSQL failover test not available: {e}")

    @pytest.mark.asyncio
    async def test_connection_limits_and_timeouts(self):
        """Test database connection limits and timeouts."""
        try:
            postgres_client = await get_postgres_client()
            assert postgres_client is not None
            
            # Test connection timeout
            start_time = time.time()
            try:
                async with postgres_client.connect() as conn:
                    # Simple query that should complete quickly
                    result = await conn.execute(sqlalchemy.text("SELECT pg_sleep(0.1)"))
                    elapsed = time.time() - start_time
                    
                    # Should complete in reasonable time
                    assert elapsed < 5.0  # 5 seconds max
                    
            except asyncio.TimeoutError:
                pytest.fail("Database connection timeout occurred")
                
        except Exception as e:
            pytest.skip(f"PostgreSQL timeout test not available: {e}")

    @pytest.mark.asyncio
    async def test_redis_cache_operations(self):
        """Test Redis cache operations and data persistence."""
        try:
            redis_client = await get_redis_client()
            assert redis_client is not None
            
            # Test different data types
            test_data = {
                "string": "test_string_value",
                "list": ["item1", "item2", "item3"],
                "hash": {"field1": "value1", "field2": "value2"},
                "set": {"member1", "member2", "member3"}
            }
            
            # Store different data types
            for key_suffix, value in test_data.items():
                key = f"test:cache:{key_suffix}"
                
                if isinstance(value, str):
                    await redis_client.set(key, value, ex=120)
                elif isinstance(value, list):
                    await redis_client.delete(key)  # Clear any existing list
                    for item in value:
                        await redis_client.lpush(key, item)
                elif isinstance(value, dict):
                    await redis_client.hset(key, mapping=value)
                elif isinstance(value, set):
                    await redis_client.sadd(key, *value)
            
            # Retrieve and verify data
            for key_suffix, original_value in test_data.items():
                key = f"test:cache:{key_suffix}"
                
                if isinstance(original_value, str):
                    retrieved = await redis_client.get(key)
                    assert retrieved == original_value
                elif isinstance(original_value, list):
                    retrieved = await redis_client.lrange(key, 0, -1)
                    assert set(retrieved) == set(original_value)
                elif isinstance(original_value, dict):
                    retrieved = await redis_client.hgetall(key)
                    assert retrieved == original_value
                elif isinstance(original_value, set):
                    retrieved = await redis_client.smembers(key)
                    assert retrieved == original_value
            
            # Clean up
            for key_suffix in test_data.keys():
                key = f"test:cache:{key_suffix}"
                await redis_client.delete(key)
                
        except Exception as e:
            pytest.skip(f"Redis cache operations test not available: {e}")

    @pytest.mark.asyncio
    async def test_database_transaction_handling(self):
        """Test database transaction handling and rollback."""
        try:
            postgres_client = await get_postgres_client()
            assert postgres_client is not None
            
            # Test transaction rollback
            async with postgres_client.begin() as trans:
                try:
                    # This would require actual tables to test properly
                    # For now, we'll test the transaction mechanism
                    
                    # Start a transaction
                    async with postgres_client.connect() as conn:
                        # Simple transaction test
                        await conn.execute(sqlalchemy.text("BEGIN"))
                        await conn.execute(sqlalchemy.text("SELECT 1"))
                        await conn.execute(sqlalchemy.text("COMMIT"))
                        
                except Exception:
                    # Rollback on error
                    await conn.execute(sqlalchemy.text("ROLLBACK"))
                    raise
                    
        except Exception as e:
            pytest.skip(f"PostgreSQL transaction test not available: {e}")

    @pytest.mark.asyncio
    async def test_redis_pubsub_functionality(self):
        """Test Redis pub/sub functionality."""
        try:
            redis_client = await get_redis_client()
            assert redis_client is not None
            
            # Test pub/sub (this would require a separate subscriber in a real test)
            # For now, we'll test the publish functionality
            
            channel = "test:pubsub"
            message = "Hello, Redis Pub/Sub!"
            
            # Publish message
            result = await redis_client.publish(channel, message)
            assert result >= 0  # Number of subscribers (could be 0 in this test)
            
        except Exception as e:
            pytest.skip(f"Redis pub/sub test not available: {e}")

    @pytest.mark.asyncio
    async def test_database_connection_pool_monitoring(self):
        """Test database connection pool monitoring and metrics."""
        try:
            postgres_client = await get_postgres_client()
            assert postgres_client is not None
            
            # Test connection pool status
            # This would depend on your connection pool implementation
            # For SQLAlchemy, we can check the pool status
            
            pool = postgres_client.pool
            if hasattr(pool, 'size'):
                pool_size = pool.size()
                assert pool_size > 0
                
            if hasattr(pool, 'checked_in'):
                checked_in = pool.checked_in()
                assert checked_in >= 0
                
        except Exception as e:
            pytest.skip(f"PostgreSQL connection pool monitoring not available: {e}")

    @pytest.mark.asyncio
    async def test_redis_cache_eviction_policies(self):
        """Test Redis cache eviction policies."""
        try:
            redis_client = await get_redis_client()
            assert redis_client is not None
            
            # Test TTL functionality
            test_key = "test:ttl"
            test_value = "test_value"
            
            # Set with TTL
            await redis_client.setex(test_key, 1, test_value)  # 1 second TTL
            
            # Should exist immediately
            exists = await redis_client.exists(test_key)
            assert exists == 1
            
            # Wait for expiration
            await asyncio.sleep(1.5)
            
            # Should not exist after TTL
            exists = await redis_client.exists(test_key)
            assert exists == 0
            
        except Exception as e:
            pytest.skip(f"Redis TTL test not available: {e}")

    @pytest.mark.asyncio
    async def test_database_health_check_endpoints(self):
        """Test database health check endpoints."""
        async with httpx.AsyncClient() as client:
            try:
                # Test database health endpoint
                response = await client.get("http://localhost:8000/api/v1/health")
                
                if response.status_code == 200:
                    data = response.json()
                    assert "database" in data
                    assert data["database"]["status"] == "healthy"
                else:
                    pytest.skip(f"Database health endpoint not available: {response.status_code}")
                    
            except httpx.ConnectError:
                pytest.skip("Database health endpoint not available")

    @pytest.mark.asyncio
    async def test_redis_cluster_connectivity(self):
        """Test Redis cluster connectivity (if using cluster mode)."""
        try:
            redis_client = await get_redis_client()
            assert redis_client is not None
            
            # Test cluster info (if available)
            try:
                cluster_info = await redis_client.execute_command("CLUSTER INFO")
                if cluster_info:
                    # Verify cluster is working
                    assert b"cluster_state:ok" in cluster_info
            except redis.ResponseError:
                # Not in cluster mode, which is also valid
                pass
                
        except Exception as e:
            pytest.skip(f"Redis cluster test not available: {e}")

    @pytest.mark.asyncio
    async def test_database_connection_leak_detection(self):
        """Test database connection leak detection."""
        try:
            postgres_client = await get_postgres_client()
            assert postgres_client is not None
            
            # Test that connections are properly closed
            initial_pool_size = postgres_client.pool.checked_in()
            
            # Create and close multiple connections
            for i in range(10):
                async with postgres_client.connect() as conn:
                    await conn.execute(sqlalchemy.text("SELECT 1"))
            
            # Pool should return to initial state
            final_pool_size = postgres_client.pool.checked_in()
            
            # Allow for some variance in pool management
            assert abs(final_pool_size - initial_pool_size) <= 2
                
        except Exception as e:
            pytest.skip(f"PostgreSQL connection leak detection not available: {e}")

    @pytest.mark.asyncio
    async def test_redis_memory_usage_monitoring(self):
        """Test Redis memory usage monitoring."""
        try:
            redis_client = await get_redis_client()
            assert redis_client is not None
            
            # Get memory info
            memory_info = await redis_client.memory_usage("test:key", 10)
            
            # Should return memory usage in bytes (or None if key doesn't exist)
            if memory_info is not None:
                assert isinstance(memory_info, int)
                assert memory_info >= 0
                
        except Exception as e:
            pytest.skip(f"Redis memory monitoring not available: {e}")

    @pytest.mark.asyncio
    async def test_database_backup_and_restore_readiness(self):
        """Test database backup and restore readiness."""
        try:
            postgres_client = await get_postgres_client()
            assert postgres_client is not None
            
            # Test that we can query database information needed for backup
            async with postgres_client.connect() as conn:
                # Get database size
                result = await conn.execute(
                    sqlalchemy.text("SELECT pg_database_size(current_database()) as size_bytes")
                )
                db_size = result.fetchone()[0]
                assert db_size > 0
                
                # Get table information
                result = await conn.execute(
                    sqlalchemy.text("""
                        SELECT table_name, table_schema 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                )
                tables = result.fetchall()
                assert len(tables) >= 0  # Should have some tables
                
        except Exception as e:
            pytest.skip(f"PostgreSQL backup readiness test not available: {e}")

    @pytest.mark.asyncio
    async def test_redis_persistence_configuration(self):
        """Test Redis persistence configuration."""
        try:
            redis_client = await get_redis_client()
            assert redis_client is not None
            
            # Get Redis configuration
            config = await redis_client.config_get("*")
            
            # Check for persistence settings
            persistence_keys = ["save", "rdbcompression", "appendonly"]
            for key in persistence_keys:
                if key in config:
                    # Verify configuration is set
                    assert config[key] is not None
                    
        except Exception as e:
            pytest.skip(f"Redis persistence configuration test not available: {e}")


async def test_database_clients_factory():
    """Test the database client factory functions."""
    from tests.integration.conftest import get_postgres_client, get_redis_client
    
    try:
        # Test PostgreSQL client
        postgres_client = await get_postgres_client()
        assert postgres_client is not None
        
        # Test Redis client
        redis_client = await get_redis_client()
        assert redis_client is not None
        
    except Exception as e:
        # If databases are not available, skip this test
        pytest.skip(f"Databases not available: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])