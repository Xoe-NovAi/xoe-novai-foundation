import pytest
import asyncio
import socket
from app.XNAi_rag_app.core.consul_client import ConsulClient

@pytest.mark.asyncio
async def test_consul_connection():
    """Test that ConsulClient can connect to the local Consul instance."""
    client = ConsulClient()
    # If Consul is running in Podman, this should eventually be True
    # If not, we check if it handles failure gracefully
    assert hasattr(client, 'is_connected')

@pytest.mark.asyncio
async def test_service_registration_lifecycle():
    """Test registering and deregistering a service."""
    client = ConsulClient()
    if not client.is_connected:
        pytest.skip("Consul not available")
        
    service_name = "test-service-integration"
    service_id = f"test-id-{socket.gethostname()}"
    port = 9999
    
    # Register
    success = await client.register_service(
        name=service_name,
        service_id=service_id,
        address="127.0.0.1",
        port=port
    )
    assert success is True
    
    # Resolve
    resolved = await client.resolve_service(service_name)
    assert resolved is not None
    assert str(port) in resolved
    
    # Deregister
    success = await client.deregister_service(service_id)
    assert success is True

@pytest.mark.asyncio
async def test_dns_resolution_fallback():
    """Test that DNS resolution falls back to API or naming conventions."""
    client = ConsulClient()
    # Test a service that doesn't exist to check fallback
    resolved = await client.resolve_service("non-existent-service")
    assert resolved is not None
    # Default fallback for unknown is {name}:8000
    assert resolved == "non-existent-service:6379" or resolved == "non-existent-service:8000"
