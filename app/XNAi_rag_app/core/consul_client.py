import os
import logging
import asyncio
from typing import Optional, List, Dict, Any
import httpx
import dns.resolver
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ServiceCheck(BaseModel):
    """Pydantic model for Consul health check configuration."""
    http: str
    interval: str = "10s"
    timeout: str = "5s"
    deregister_critical_service_after: str = "30s"


class ServiceRegistration(BaseModel):
    """Pydantic model for service registration."""
    ID: str
    Name: str
    Address: str
    Port: int
    Tags: List[str] = []
    Check: Optional[Dict[str, Any]] = None


class ConsulClient:
    """Consul client for service discovery and health monitoring using httpx."""
    
    def __init__(self):
        self.host = os.getenv("CONSUL_HOST", "consul")
        self.port = int(os.getenv("CONSUL_PORT", "8500"))
        self.base_url = f"http://{self.host}:{self.port}"
        self.dns_host = os.getenv("CONSUL_DNS_HOST", "localhost")
        self.dns_port = int(os.getenv("CONSUL_DNS_PORT", "8600"))
        self.is_connected = False
        self._init_client()

    def _init_client(self):
        """Initialize the Consul client by testing connectivity."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/v1/agent/self")
                if response.status_code == 200:
                    self.is_connected = True
                    logger.info(f"✅ Connected to Consul at {self.host}:{self.port}")
                else:
                    self.is_connected = False
                    logger.warning(f"⚠️ Consul returned status {response.status_code}")
        except Exception as e:
            self.is_connected = False
            logger.warning(f"⚠️ Consul unavailable at {self.host}:{self.port}. Service discovery disabled. Error: {e}")

    async def register_service(
        self, 
        name: str, 
        service_id: str, 
        address: str, 
        port: int, 
        tags: List[str] = None,
        check_url: str = None
    ) -> bool:
        """Register a service with Consul."""
        if not self.is_connected:
            logger.warning(f"⚠️ Consul not connected, skipping registration of {name}")
            return False

        tags = tags or ["v1"]
        
        registration_data = {
            "ID": service_id,
            "Name": name,
            "Address": address,
            "Port": port,
            "Tags": tags,
        }
        
        if check_url:
            registration_data["Check"] = {
                "HTTP": check_url,
                "Interval": "10s",
                "Timeout": "5s",
                "DeregisterCriticalServiceAfter": "30s",
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.put(
                    f"{self.base_url}/v1/agent/service/register",
                    json=registration_data
                )
                if response.status_code == 200:
                    logger.info(f"✅ Registered service {name} ({service_id}) with Consul")
                    return True
                else:
                    logger.error(f"❌ Failed to register service {name}: HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Failed to register service {name}: {e}")
            return False

    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service from Consul."""
        if not self.is_connected:
            logger.warning(f"⚠️ Consul not connected, skipping deregistration of {service_id}")
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.put(
                    f"{self.base_url}/v1/agent/service/deregister/{service_id}"
                )
                if response.status_code == 200:
                    logger.info(f"✅ Deregistered service {service_id} from Consul")
                    return True
                else:
                    logger.error(f"❌ Failed to deregister service {service_id}: HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Failed to deregister service {service_id}: {e}")
            return False

    async def resolve_service(self, name: str) -> Optional[str]:
        """Resolve a service name to an address:port string using DNS first, then API fallback."""
        # Try DNS resolution first
        dns_result = await self._resolve_via_dns(name)
        if dns_result:
            return dns_result
        
        # Fallback to Consul API
        if self.is_connected:
            api_result = await self._resolve_via_api(name)
            if api_result:
                return api_result
        
        # Final fallback to container name conventions
        logger.warning(f"⚠️ No healthy instances of {name} found, using fallback naming")
        return f"{name}:8000" if name == "rag" else f"{name}:6379"

    async def _resolve_via_dns(self, name: str) -> Optional[str]:
        """Resolve service using Consul DNS on port 8600."""
        try:
            loop = asyncio.get_event_loop()
            
            def dns_lookup():
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [self.dns_host]
                resolver.port = self.dns_port
                answers = resolver.resolve(f"{name}.service.consul", "A")
                if answers:
                    # Return first address with default port
                    return f"{answers[0]}:8000"
                return None
            
            result = await loop.run_in_executor(None, dns_lookup)
            if result:
                logger.debug(f"✅ Resolved {name} via DNS: {result}")
                return result
        except Exception as e:
            logger.debug(f"⚠️ DNS resolution failed for {name}: {e}")
        
        return None

    async def _resolve_via_api(self, name: str) -> Optional[str]:
        """Resolve service using Consul API health checks."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/health/service/{name}",
                    params={"passing": True}
                )
                
                if response.status_code == 200:
                    services = response.json()
                    if services:
                        service = services[0]["Service"]
                        address = service.get("Address")
                        port = service.get("Port")
                        result = f"{address}:{port}"
                        logger.debug(f"✅ Resolved {name} via API: {result}")
                        return result
                    else:
                        logger.warning(f"⚠️ No healthy instances of {name} found in Consul")
                else:
                    logger.debug(f"⚠️ Consul API returned status {response.status_code} for {name}")
        except Exception as e:
            logger.warning(f"❌ Error resolving service {name} via API: {e}")
        
        return None


# Global singleton
consul_client = ConsulClient()
