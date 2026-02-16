"""
Consul registration helper (skeleton).

Uses Consul HTTP API to register/deregister services and perform simple checks.
This is a lightweight helper; production code should use TLS, ACLs, and retries.
"""

import os
import requests


class ConsulRegistrar:
    def __init__(self, address: str = None):
        self.address = address or os.getenv("CONSUL_HTTP_ADDR", "http://127.0.0.1:8500")

    def register_service(self, name: str, service_id: str = None, port: int = None, tags: list = None, check: dict = None) -> bool:
        payload = {
            "Name": name,
            "ID": service_id or name,
        }
        if port:
            payload["Port"] = port
        if tags:
            payload["Tags"] = tags
        if check:
            payload["Check"] = check
        url = f"{self.address}/v1/agent/service/register"
        resp = requests.put(url, json=payload)
        resp.raise_for_status()
        return resp.ok

    def deregister_service(self, service_id: str) -> bool:
        url = f"{self.address}/v1/agent/service/deregister/{service_id}"
        resp = requests.put(url)
        resp.raise_for_status()
        return resp.ok

    def list_services(self) -> dict:
        url = f"{self.address}/v1/agent/services"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
