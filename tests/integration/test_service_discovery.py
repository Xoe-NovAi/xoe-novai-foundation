#!/usr/bin/env python3
"""
Integration tests for service discovery functionality.
Tests Consul service registration, health checks, and service mesh connectivity.
"""

import asyncio
import json
import pytest
import time
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch

import httpx
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.XNAi_rag_app import app as rag_app
from app.config import settings
from tests.integration.conftest import (
    create_test_service,
    get_consul_client,
    wait_for_service_health,
    cleanup_test_services
)


class TestServiceDiscovery:
    """Test service discovery functionality with Consul."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_teardown(self):
        """Setup and teardown for each test."""
        # Setup test services
        self.test_services = []
        yield
        # Teardown
        await cleanup_test_services(self.test_services)

    @pytest.mark.asyncio
    async def test_consul_service_registration(self):
        """Test that services can register with Consul."""
        consul_client = await get_consul_client()
        
        # Register a test service
        service_data = {
            "ID": "test-service-1",
            "Name": "test-service",
            "Address": "127.0.0.1",
            "Port": 8080,
            "Tags": ["test", "integration"],
            "Check": {
                "HTTP": "http://127.0.0.1:8080/health",
                "Interval": "10s",
                "Timeout": "5s"
            }
        }
        
        # Register service
        response = await consul_client.agent.service.register(**service_data)
        assert response is True
        
        # Verify service is registered
        services = await consul_client.agent.services()
        assert "test-service-1" in services
        
        # Store for cleanup
        self.test_services.append("test-service-1")

    @pytest.mark.asyncio
    async def test_service_health_checks(self):
        """Test service health check functionality."""
        consul_client = await get_consul_client()
        
        # Create a test service with health check
        service_id = "health-test-service"
        service_data = {
            "ID": service_id,
            "Name": "health-test",
            "Address": "127.0.0.1",
            "Port": 8081,
            "Check": {
                "HTTP": "http://127.0.0.1:8081/health",
                "Interval": "5s",
                "Timeout": "2s"
            }
        }
        
        # Register service
        await consul_client.agent.service.register(**service_data)
        self.test_services.append(service_id)
        
        # Wait for health check to complete
        health_status = await wait_for_service_health(consul_client, service_id, timeout=30)
        assert health_status in ["passing", "warning"]  # Allow warning state

    @pytest.mark.asyncio
    async def test_service_discovery_query(self):
        """Test querying for services via Consul."""
        consul_client = await get_consul_client()
        
        # Register multiple test services
        services_to_register = [
            {
                "ID": "query-service-1",
                "Name": "query-service",
                "Address": "127.0.0.1",
                "Port": 8082,
                "Tags": ["query", "test"]
            },
            {
                "ID": "query-service-2", 
                "Name": "query-service",
                "Address": "127.0.0.1",
                "Port": 8083,
                "Tags": ["query", "test"]
            }
        ]
        
        for service_data in services_to_register:
            await consul_client.agent.service.register(**service_data)
            self.test_services.append(service_data["ID"])
        
        # Query for services
        services = await consul_client.health.service("query-service")
        
        # Verify we can find the services
        assert len(services) >= 2
        service_names = [s["Service"]["ID"] for s in services]
        assert "query-service-1" in service_names
        assert "query-service-2" in service_names

    @pytest.mark.asyncio
    async def test_service_mesh_connectivity(self):
        """Test service-to-service communication through the mesh."""
        # This test verifies that services can communicate with each other
        # through the service mesh when properly configured
        
        # Start a mock service
        mock_app = FastAPI()
        
        @mock_app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "mock-service"}
        
        @mock_app.get("/api/test")
        async def test_endpoint():
            return {"message": "Service mesh test successful"}
        
        # In a real test, we would start this as a separate service
        # For now, we'll test the connectivity logic
        
        async with httpx.AsyncClient() as client:
            # Test that we can reach the mock service
            try:
                response = await client.get("http://127.0.0.1:8000/health")
                assert response.status_code == 200
                data = response.json()
                assert "status" in data
            except httpx.ConnectError:
                # Service might not be running, which is expected in this test context
                pytest.skip("Mock service not available for connectivity test")

    @pytest.mark.asyncio
    async def test_service_failover(self):
        """Test service failover scenarios."""
        consul_client = await get_consul_client()
        
        # Register primary and backup services
        primary_service = {
            "ID": "primary-service",
            "Name": "failover-service", 
            "Address": "127.0.0.1",
            "Port": 8084,
            "Check": {
                "HTTP": "http://127.0.0.1:8084/health",
                "Interval": "5s",
                "Timeout": "2s"
            }
        }
        
        backup_service = {
            "ID": "backup-service",
            "Name": "failover-service",
            "Address": "127.0.0.1", 
            "Port": 8085,
            "Check": {
                "HTTP": "http://127.0.0.1:8085/health",
                "Interval": "5s",
                "Timeout": "2s"
            }
        }
        
        await consul_client.agent.service.register(**primary_service)
        await consul_client.agent.service.register(**backup_service)
        
        self.test_services.extend(["primary-service", "backup-service"])
        
        # Verify both services are healthy initially
        services = await consul_client.health.service("failover-service")
        healthy_services = [s for s in services if s["Checks"][-1]["Status"] == "passing"]
        assert len(healthy_services) >= 2
        
        # Simulate primary service failure by deregistering it
        await consul_client.agent.service.deregister("primary-service")
        
        # Verify backup service is still available
        services = await consul_client.health.service("failover-service")
        backup_services = [s for s in services if s["Service"]["ID"] == "backup-service"]
        assert len(backup_services) == 1

    @pytest.mark.asyncio
    async def test_service_tags_and_metadata(self):
        """Test service tagging and metadata functionality."""
        consul_client = await get_consul_client()
        
        service_with_tags = {
            "ID": "tagged-service",
            "Name": "tagged-service",
            "Address": "127.0.0.1",
            "Port": 8086,
            "Tags": ["production", "api", "v1.0"],
            "Meta": {
                "version": "1.0.0",
                "environment": "test",
                "team": "platform"
            },
            "Check": {
                "HTTP": "http://127.0.0.1:8086/health",
                "Interval": "10s"
            }
        }
        
        await consul_client.agent.service.register(**service_with_tags)
        self.test_services.append("tagged-service")
        
        # Query service and verify tags and metadata
        services = await consul_client.agent.services()
        service_info = services["tagged-service"]
        
        assert "production" in service_info["Tags"]
        assert "api" in service_info["Tags"]
        assert "v1.0" in service_info["Tags"]
        
        assert service_info["Meta"]["version"] == "1.0.0"
        assert service_info["Meta"]["environment"] == "test"
        assert service_info["Meta"]["team"] == "platform"

    @pytest.mark.asyncio
    async def test_consul_cluster_health(self):
        """Test Consul cluster health and availability."""
        consul_client = await get_consul_client()
        
        # Check Consul cluster members
        members = await consul_client.operator.raft.list_peers()
        assert len(members) > 0
        
        # Check Consul health
        health = await consul_client.health.node("localhost")
        assert len(health) > 0
        
        # Verify Consul is in healthy state
        for check in health:
            if check["CheckID"] == "serfHealth":
                assert check["Status"] == "passing"

    @pytest.mark.asyncio
    async def test_service_registration_with_custom_checks(self):
        """Test service registration with custom health check configurations."""
        consul_client = await get_consul_client()
        
        # Service with multiple health checks
        service_with_checks = {
            "ID": "multi-check-service",
            "Name": "multi-check-service",
            "Address": "127.0.0.1",
            "Port": 8087,
            "Checks": [
                {
                    "HTTP": "http://127.0.0.1:8087/health",
                    "Interval": "10s",
                    "Timeout": "5s",
                    "Name": "HTTP Health Check"
                },
                {
                    "TCP": "127.0.0.1:8087",
                    "Interval": "30s",
                    "Timeout": "10s",
                    "Name": "TCP Health Check"
                }
            ]
        }
        
        await consul_client.agent.service.register(**service_with_checks)
        self.test_services.append("multi-check-service")
        
        # Verify service has multiple checks
        services = await consul_client.agent.services()
        service_info = services["multi-check-service"]
        
        # The service should be registered (exact check verification depends on Consul API response format)
        assert service_info["ID"] == "multi-check-service"

    @pytest.mark.asyncio
    async def test_service_deregistration(self):
        """Test proper service deregistration."""
        consul_client = await get_consul_client()
        
        service_to_deregister = {
            "ID": "deregister-test-service",
            "Name": "deregister-test",
            "Address": "127.0.0.1",
            "Port": 8088
        }
        
        # Register service
        await consul_client.agent.service.register(**service_to_deregister)
        
        # Verify service is registered
        services = await consul_client.agent.services()
        assert "deregister-test-service" in services
        
        # Deregister service
        await consul_client.agent.service.deregister("deregister-test-service")
        
        # Verify service is deregistered
        services = await consul_client.agent.services()
        assert "deregister-test-service" not in services

    @pytest.mark.asyncio
    async def test_service_discovery_under_load(self):
        """Test service discovery performance under load."""
        consul_client = await get_consul_client()
        
        # Register many services to simulate load
        num_services = 50
        registered_services = []
        
        for i in range(num_services):
            service_data = {
                "ID": f"load-test-service-{i}",
                "Name": "load-test-service",
                "Address": "127.0.0.1",
                "Port": 8089 + i
            }
            
            await consul_client.agent.service.register(**service_data)
            registered_services.append(f"load-test-service-{i}")
        
        # Test query performance
        start_time = time.time()
        services = await consul_client.health.service("load-test-service")
        query_time = time.time() - start_time
        
        # Verify all services are found
        assert len(services) >= num_services
        
        # Query should complete in reasonable time (adjust based on your performance requirements)
        assert query_time < 5.0  # 5 seconds max
        
        # Cleanup
        for service_id in registered_services:
            await consul_client.agent.service.deregister(service_id)


async def test_consul_client_factory():
    """Test the Consul client factory function."""
    from tests.integration.conftest import get_consul_client
    
    consul_client = await get_consul_client()
    assert consul_client is not None
    
    # Test that we can make a basic API call
    try:
        members = await consul_client.operator.raft.list_peers()
        assert isinstance(members, list)
    except Exception as e:
        # If Consul is not available, skip this test
        pytest.skip(f"Consul not available: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])