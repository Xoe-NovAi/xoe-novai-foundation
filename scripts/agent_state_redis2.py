"""
Improved Redis-backed adapter for agent state persistence with authentication handling.

This adapter will attempt to reconnect using REDIS_PASSWORD or REDIS_URL and falls back
to filesystem storage when Redis is unavailable or authentication fails.
"""

import json
import os
from typing import Optional

try:
    import redis
    from redis.exceptions import AuthenticationError, RedisError
except Exception:
    redis = None
    AuthenticationError = Exception
    RedisError = Exception


class RedisAgentStateAdapter:
    """Redis adapter that attempts auth handling and falls back to filesystem."""

    def __init__(self, url: Optional[str] = None, prefix: str = "agent:state:", ttl: Optional[int] = None):
        self.url = url or os.getenv("REDIS_URL")
        self.prefix = prefix
        self.ttl = ttl
        self.client = None
        self._init_params = None
        self._ensure_url()
        self._init_client()

    def _ensure_url(self):
        if self.url:
            return
        host = os.getenv("REDIS_HOST", "127.0.0.1")
        port = os.getenv("REDIS_PORT", "6379")
        password = os.getenv("REDIS_PASSWORD")
        username = os.getenv("REDIS_USERNAME")
        if password:
            if username:
                self.url = f"redis://{username}:{password}@{host}:{port}/0"
            else:
                self.url = f"redis://:{password}@{host}:{port}/0"
        else:
            self.url = f"redis://{host}:{port}/0"

    def _init_client(self):
        if not redis:
            self.client = None
            return
        try:
            # prefer from_url when available
            try:
                self.client = redis.from_url(self.url)
            except Exception:
                # fallback for older redis clients
                self.client = redis.StrictRedis.from_url(self.url)

            # quick ping to validate auth/connectivity
            try:
                self.client.ping()
            except Exception as e:
                msg = str(e).lower()
                if "auth" in msg or "noauth" in msg or "authentication" in msg:
                    # attempt to rebuild url from REDIS_PASSWORD if available and url lacks credentials
                    pw = os.getenv("REDIS_PASSWORD")
                    if pw and "@" not in self.url:
                        parts = self.url.split("//", 1)
                        if len(parts) == 2:
                            scheme = parts[0] + "//"
                            rest = parts[1]
                            new_url = scheme + f":{pw}@" + rest
                            try:
                                self.client = redis.from_url(new_url)
                                self.url = new_url
                                self.client.ping()
                                return
                            except Exception:
                                self.client = None
                                return
                    # cannot auth
                    self.client = None
                else:
                    # other connectivity error
                    self.client = None
        except Exception:
            self.client = None

    def _key(self, agent_name: str) -> str:
        return f"{self.prefix}{agent_name}"

    def save_state(self, agent_name: str, state: dict):
        payload = json.dumps(state)
        if self.client:
            try:
                if self.ttl:
                    self.client.setex(self._key(agent_name), self.ttl, payload)
                else:
                    self.client.set(self._key(agent_name), payload)
                return
            except Exception as e:
                msg = str(e).lower()
                if "auth" in msg or "noauth" in msg or "authentication" in msg:
                    raise RuntimeError("Redis authentication required. Set REDIS_URL or REDIS_PASSWORD env var with correct credentials.")
                # fall through to filesystem fallback

        # Filesystem fallback
        path = os.path.join("internal_docs/communication_hub/state", f"{agent_name}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(payload)

    def load_state(self, agent_name: str) -> Optional[dict]:
        if self.client:
            try:
                raw = self.client.get(self._key(agent_name))
                if raw is None:
                    return None
                try:
                    return json.loads(raw)
                except Exception:
                    return None
            except Exception as e:
                msg = str(e).lower()
                if "auth" in msg or "noauth" in msg or "authentication" in msg:
                    raise RuntimeError("Redis authentication required. Set REDIS_URL or REDIS_PASSWORD env var with correct credentials.")
                # fall through to filesystem fallback

        path = os.path.join("internal_docs/communication_hub/state", f"{agent_name}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    return json.load(f)
                except Exception:
                    return None
        return None
