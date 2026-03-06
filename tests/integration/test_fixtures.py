#!/usr/bin/env python3
"""
Test data fixtures and mock services for integration tests.
Provides test data, mock services, and test utilities for Phase 4.1 integration testing.
"""

import asyncio
import json
import pytest
import time
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import redis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from tests.integration.conftest import (
    get_redis_client,
    get_postgres_client,
    gateway_client,
    streaming_client
)


class TestDataFixtures:
    """Test data fixtures for integration tests."""

    @pytest.fixture
    def test_rag_data(self):
        """Test data for RAG functionality."""
        return {
            "question": "What is the capital of France?",
            "context": "Paris is the capital and largest city of France. It has been one of Europe's major centers of finance, diplomacy, commerce, culture, fashion, and the arts since the 17th century.",
            "expected_answer": "Paris",
            "test_payload": {
                "question": "What is the capital of France?",
                "context": "Paris is the capital and largest city of France. It has been one of Europe's major centers of finance, diplomacy, commerce, culture, fashion, and the arts since the 17th century.",
                "model": "llama2",
                "temperature": 0.7
            }
        }

    @pytest.fixture
    def test_vikunja_data(self):
        """Test data for Vikunja task management."""
        return {
            "user": {
                "username": "test_user",
                "email": "test@example.com",
                "password": "test_password_123"
            },
            "project": {
                "title": "Integration Test Project",
                "description": "Project for testing Vikunja integration"
            },
            "task": {
                "title": "Test Task",
                "description": "Task for testing task creation and management",
                "priority": 1,
                "status": "pending"
            }
        }

    @pytest.fixture
    def test_mkdocs_data(self):
        """Test data for MkDocs documentation."""
        return {
            "documentation": {
                "title": "Integration Test Documentation",
                "content": "# Integration Test\n\nThis is test documentation for MkDocs integration.",
                "path": "integration-test.md"
            },
            "config": {
                "site_name": "Test Documentation",
                "theme": "material",
                "nav": [
                    {"Home": "index.md"},
                    {"Integration": "integration-test.md"}
                ]
            }
        }

    @pytest.fixture
    def test_redis_data(self):
        """Test data for Redis cache operations."""
        return {
            "string_data": {
                "key": "test:string:key",
                "value": "test_string_value",
                "ttl": 60
            },
            "list_data": {
                "key": "test:list:key",
                "values": ["item1", "item2", "item3"],
                "ttl": 120
            },
            "hash_data": {
                "key": "test:hash:key",
                "fields": {
                    "field1": "value1",
                    "field2": "value2",
                    "field3": "value3"
                },
                "ttl": 180
            },
            "set_data": {
                "key": "test:set:key",
                "members": {"member1", "member2", "member3"},
                "ttl": 240
            }
        }

    @pytest.fixture
    def test_postgres_data(self):
        """Test data for PostgreSQL operations."""
        return {
            "test_table": {
                "name": "integration_test_table",
                "columns": [
                    "id SERIAL PRIMARY KEY",
                    "name VARCHAR(100) NOT NULL",
                    "description TEXT",
                    "created_at TIMESTAMP DEFAULT NOW()"
                ],
                "test_records": [
                    {"name": "Test Record 1", "description": "First test record"},
                    {"name": "Test Record 2", "description": "Second test record"},
                    {"name": "Test Record 3", "description": "Third test record"}
                ]
            }
        }


class MockServices:
    """Mock services for testing when real services are not available."""

    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service for testing."""
        app = FastAPI()

        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "mock-rag"}

        @app.post("/api/query")
        async def query_endpoint(payload: Dict[str, Any]):
            return {
                "answer": "This is a mock response",
                "source": "mock_service",
                "confidence": 0.8,
                "timestamp": time.time()
            }

        @app.get("/api/stream")
        async def stream_endpoint():
            # Mock streaming response
            async def generate():
                for i in range(5):
                    yield f"data: {{'chunk': 'Chunk {i}', 'progress': {i*20}}}\n\n"
                    await asyncio.sleep(0.1)
                yield "data: {'complete': true}\n\n"

            return httpx.Response(200, content=generate(), headers={"Content-Type": "text/event-stream"})

        return TestClient(app)

    @pytest.fixture
    def mock_vikunja_service(self):
        """Mock Vikunja service for testing."""
        app = FastAPI()

        @app.get("/api/health")
        async def health_check():
            return {"status": "healthy", "service": "mock-vikunja"}

        @app.post("/api/v1/users")
        async def create_user(payload: Dict[str, Any]):
            return {
                "id": 1,
                "username": payload.get("username"),
                "email": payload.get("email"),
                "created_at": time.time()
            }

        @app.get("/api/v1/projects")
        async def get_projects():
            return [
                {
                    "id": 1,
                    "title": "Test Project",
                    "description": "Test project for integration",
                    "created_at": time.time()
                }
            ]

        @app.post("/api/v1/tasks")
        async def create_task(payload: Dict[str, Any]):
            return {
                "id": 1,
                "title": payload.get("title"),
                "description": payload.get("description"),
                "status": payload.get("status", "pending"),
                "priority": payload.get("priority", 1),
                "created_at": time.time()
            }

        return TestClient(app)

    @pytest.fixture
    def mock_mkdocs_service(self):
        """Mock MkDocs service for testing."""
        app = FastAPI()

        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "mock-mkdocs"}

        @app.get("/docs/")
        async def docs_home():
            return {"message": "Mock MkDocs documentation"}

        @app.get("/docs/integration-test.md")
        async def docs_page():
            return {"content": "# Integration Test\n\nThis is mock documentation."}

        return TestClient(app)

    @pytest.fixture
    def mock_redis_service(self):
        """Mock Redis service for testing."""
        mock_client = MagicMock()
        
        # Mock Redis operations
        mock_client.get.return_value = "test_value"
        mock_client.set.return_value = True
        mock_client.delete.return_value = 1
        mock_client.exists.return_value = 1
        mock_client.ping.return_value = True
        mock_client.lpush.return_value = 1
        mock_client.lrange.return_value = ["item1", "item2", "item3"]
        mock_client.hset.return_value = 1
        mock_client.hgetall.return_value = {"field1": "value1", "field2": "value2"}
        mock_client.sadd.return_value = 1
        mock_client.smembers.return_value = {"member1", "member2", "member3"}
        mock_client.publish.return_value = 1
        
        return mock_client

    @pytest.fixture
    def mock_postgres_service(self):
        """Mock PostgreSQL service for testing."""
        mock_conn = MagicMock()
        
        # Mock database operations
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (1,)
        mock_result.fetchall.return_value = [(1, "test", "description")]
        
        mock_conn.execute.return_value = mock_result
        mock_conn.begin.return_value.__enter__ = MagicMock()
        mock_conn.begin.return_value.__exit__ = MagicMock()
        
        return mock_conn


class TestUtilities:
    """Utility functions for integration tests."""

    @staticmethod
    async def setup_test_data(redis_client=None, postgres_client=None):
        """Set up test data in Redis and PostgreSQL."""
        test_data = {
            "redis": {
                "string": {"key": "test:string", "value": "test_value"},
                "list": {"key": "test:list", "values": ["item1", "item2", "item3"]},
                "hash": {"key": "test:hash", "fields": {"field1": "value1", "field2": "value2"}},
                "set": {"key": "test:set", "members": {"member1", "member2", "member3"}}
            },
            "postgres": {
                "table": "test_table",
                "records": [
                    {"name": "Test 1", "description": "First test record"},
                    {"name": "Test 2", "description": "Second test record"}
                ]
            }
        }

        # Setup Redis data
        if redis_client:
            try:
                # String data
                await redis_client.set(test_data["redis"]["string"]["key"], 
                                     test_data["redis"]["string"]["value"], ex=300)
                
                # List data
                await redis_client.delete(test_data["redis"]["list"]["key"])
                for item in test_data["redis"]["list"]["values"]:
                    await redis_client.lpush(test_data["redis"]["list"]["key"], item)
                
                # Hash data
                await redis_client.hset(test_data["redis"]["hash"]["key"], 
                                      mapping=test_data["redis"]["hash"]["fields"])
                
                # Set data
                await redis_client.sadd(test_data["redis"]["set"]["key"], 
                                      *test_data["redis"]["set"]["members"])
                
            except Exception as e:
                print(f"Warning: Could not setup Redis test data: {e}")

        # Setup PostgreSQL data
        if postgres_client:
            try:
                # Create test table
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """
                
                async with postgres_client.connect() as conn:
                    await conn.execute(text(create_table_sql))
                    await conn.commit()
                    
                    # Insert test records
                    for record in test_data["postgres"]["records"]:
                        insert_sql = """
                            INSERT INTO test_table (name, description) 
                            VALUES (:name, :description)
                        """
                        await conn.execute(text(insert_sql), record)
                    await conn.commit()
                    
            except Exception as e:
                print(f"Warning: Could not setup PostgreSQL test data: {e}")

    @staticmethod
    async def cleanup_test_data(redis_client=None, postgres_client=None):
        """Clean up test data from Redis and PostgreSQL."""
        try:
            # Cleanup Redis
            if redis_client:
                await redis_client.delete("test:string", "test:list", "test:hash", "test:set")
            
            # Cleanup PostgreSQL
            if postgres_client:
                async with postgres_client.connect() as conn:
                    await conn.execute(text("DROP TABLE IF EXISTS test_table"))
                    await conn.commit()
                    
        except Exception as e:
            print(f"Warning: Could not cleanup test data: {e}")

    @staticmethod
    async def wait_for_service_health(service_url: str, timeout: int = 60):
        """Wait for a service to be healthy."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(service_url, timeout=5)
                    if response.status_code == 200:
                        return True
            except Exception:
                pass
            await asyncio.sleep(1)
        return False

    @staticmethod
    def assert_response_structure(response, expected_fields: List[str]):
        """Assert that response contains expected fields."""
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        for field in expected_fields:
            assert field in data, f"Missing field '{field}' in response"

    @staticmethod
    def assert_error_response(response, expected_status: int, expected_error_fields: List[str]):
        """Assert that response is an error response with expected fields."""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        data = response.json()
        for field in expected_error_fields:
            assert field in data, f"Missing error field '{field}' in response"


# Test data for specific scenarios
TEST_SCENARIOS = {
    "rag_query": {
        "valid": {
            "question": "What is AI?",
            "context": "Artificial Intelligence is a field of computer science...",
            "model": "llama2",
            "temperature": 0.7
        },
        "invalid": {
            "question": "",
            "context": "",
            "model": "invalid_model"
        }
    },
    "vikunja_task": {
        "valid": {
            "title": "Test Task",
            "description": "Test task description",
            "priority": 1,
            "status": "pending"
        },
        "invalid": {
            "title": "",
            "description": "",
            "priority": 999
        }
    },
    "streaming": {
        "sse": {
            "endpoint": "/api/stream",
            "expected_events": 5
        },
        "websocket": {
            "endpoint": "/ws/stream",
            "expected_messages": 3
        }
    }
}


if __name__ == "__main__":
    # Run basic fixture tests
    pytest.main([__file__, "-v"])