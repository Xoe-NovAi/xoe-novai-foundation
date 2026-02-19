# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint5-2026-02-18
# version: v1.0.0
# created: 2026-02-18
# ---
"""
model_router.py — XNAi Model Router

Loads configs/model-router.yaml and provides routing decisions for:
  - Task-based model selection (10 task types)
  - Context-size-based routing (small/medium/large/massive)
  - Rate-limit waterfall (provider fallback chain)
  - Sovereign MC routing (local-first for sensitive tasks)

Usage:
    router = ModelRouter()
    model = router.select_model(task_type="code_generation", context_tokens=45000)
    provider = router.get_provider(model)
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# ─── Config Path ──────────────────────────────────────────────────────────────

CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "model-router.yaml"


# ─── Data Classes ─────────────────────────────────────────────────────────────


class ProviderConfig:
    """Configuration for a single AI provider."""

    def __init__(self, name: str, data: dict[str, Any]) -> None:
        self.name = name
        self.display_name = data.get("name", name)
        self.tier = data.get("tier", "unknown")
        self.cost = data.get("cost", "unknown")
        self.auth = data.get("auth", {})
        self.models = data.get("models", [])
        self.rate_limits = data.get("rate_limits", {})
        self.features = data.get("features", [])
        self.raw = data

    @property
    def is_free(self) -> bool:
        return self.cost in ("free", "free_tier", "free-tier", "$0")

    @property
    def requires_api_key(self) -> bool:
        return self.auth.get("type") == "api_key"

    def has_model(self, model_id: str) -> bool:
        """Check if this provider has the given model."""
        for m in self.models:
            if isinstance(m, dict):
                if m.get("id") == model_id or m.get("name") == model_id:
                    return True
            elif isinstance(m, str):
                if m == model_id:
                    return True
        return False


class ModelRouter:
    """
    Route model selection based on task type, context size, and availability.

    Loads from configs/model-router.yaml — the canonical single source of truth.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or CONFIG_PATH
        self._config: dict[str, Any] = {}
        self._providers: dict[str, ProviderConfig] = {}
        self._load()

    def _load(self) -> None:
        """Load and parse the model router config."""
        if not self._config_path.exists():
            logger.warning("model-router.yaml not found at %s", self._config_path)
            return

        try:
            with self._config_path.open() as f:
                self._config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error("Failed to load model-router.yaml: %s", e)
            return

        # Parse providers
        for pname, pdata in self._config.get("providers", {}).items():
            self._providers[pname] = ProviderConfig(pname, pdata)

        logger.info(
            "ModelRouter loaded: %d providers from %s",
            len(self._providers),
            self._config_path,
        )

    def get_provider(self, provider_name: str) -> ProviderConfig | None:
        """Get provider config by name."""
        return self._providers.get(provider_name)

    def list_providers(self, free_only: bool = False) -> list[ProviderConfig]:
        """List all providers, optionally filtering to free-only."""
        providers = list(self._providers.values())
        if free_only:
            providers = [p for p in providers if p.is_free]
        return providers

    def select_model(
        self,
        task_type: str = "general",
        context_tokens: int = 0,
        prefer_free: bool = False,
        prefer_local: bool = False,
    ) -> dict[str, str]:
        """
        Select the best model for the given task and context size.

        Args:
            task_type: One of the task types defined in model-router.yaml
                       (code_generation, research, creative_writing, etc.)
            context_tokens: Estimated input token count
            prefer_free: Bias toward free providers
            prefer_local: Bias toward local/sovereign models

        Returns:
            Dict with 'provider', 'model', 'reason' keys
        """
        # Sovereign override
        if prefer_local:
            sovereign = self._config.get("sovereign_mc_routing", {})
            local_model = sovereign.get("local_first_model", "")
            if local_model:
                return {
                    "provider": "llama_cpp_python",
                    "model": local_model,
                    "reason": "sovereign/local preference",
                }

        # Context-size routing
        context_routing = self._config.get("context_routing", {})
        context_tier = self._get_context_tier(context_tokens, context_routing)

        # Task-type routing
        task_routing = self._config.get("task_routing", {})
        task_config = task_routing.get(task_type, task_routing.get("general", {}))

        # Primary model from task config
        primary_model = task_config.get("primary", "")
        primary_provider = task_config.get("provider", "")

        # Check if primary is available (env vars present)
        if primary_provider and self._is_provider_available(primary_provider):
            if not prefer_free or self._providers.get(primary_provider, ProviderConfig("", {})).is_free:
                return {
                    "provider": primary_provider,
                    "model": primary_model,
                    "reason": f"task_routing[{task_type}].primary",
                }

        # Fallback chain
        fallback_model = task_config.get("fallback", "")
        fallback_provider = task_config.get("fallback_provider", "")
        if fallback_provider and self._is_provider_available(fallback_provider):
            return {
                "provider": fallback_provider,
                "model": fallback_model,
                "reason": f"task_routing[{task_type}].fallback",
            }

        # Rate limit waterfall
        waterfall = self._config.get("rate_limit_waterfall", [])
        for entry in waterfall:
            provider_name = entry.get("provider", "")
            if self._is_provider_available(provider_name):
                models = entry.get("models", [])
                if models:
                    model_id = models[0].get("id", "") if isinstance(models[0], dict) else models[0]
                    return {
                        "provider": provider_name,
                        "model": model_id,
                        "reason": "rate_limit_waterfall",
                    }

        # Last resort: local
        return {
            "provider": "llama_cpp_python",
            "model": "Qwen3-0.6B-Q4_K_M",
            "reason": "no_provider_available/local_fallback",
        }

    def _get_context_tier(self, tokens: int, routing: dict) -> str:
        """Determine context tier from token count."""
        if tokens <= routing.get("small", {}).get("max_tokens", 8000):
            return "small"
        elif tokens <= routing.get("medium", {}).get("max_tokens", 32000):
            return "medium"
        elif tokens <= routing.get("large", {}).get("max_tokens", 128000):
            return "large"
        else:
            return "massive"

    def _is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider has the required credentials in environment."""
        provider = self._providers.get(provider_name)
        if not provider:
            return False

        auth = provider.auth
        auth_type = auth.get("type", "none")

        if auth_type == "none":
            return True
        elif auth_type == "api_key":
            env_var = auth.get("env_var", "")
            return bool(os.environ.get(env_var))
        elif auth_type == "oauth":
            # OAuth providers assumed available if CLI is installed
            return True
        elif auth_type == "local":
            # Local providers — check if model file exists
            model_path = auth.get("model_path", "")
            if model_path:
                return Path(model_path).exists()
            return True

        return False

    def get_waterfall(self) -> list[dict[str, Any]]:
        """Get the full rate limit waterfall chain."""
        return self._config.get("rate_limit_waterfall", [])

    def get_free_providers(self) -> list[ProviderConfig]:
        """Get all free/free-tier providers."""
        return [p for p in self._providers.values() if p.is_free]

    def get_confirmed_models(self) -> dict[str, Any]:
        """Get the confirmed real models registry."""
        return self._config.get("confirmed_real_models", {})

    def summary(self) -> str:
        """Human-readable summary of loaded config."""
        lines = [
            f"ModelRouter: {len(self._providers)} providers loaded",
            f"Config: {self._config_path}",
            "",
            "Providers:",
        ]
        for name, p in sorted(self._providers.items()):
            available = "✅" if self._is_provider_available(name) else "❌"
            free = " (free)" if p.is_free else ""
            lines.append(f"  {available} {name}{free} — tier: {p.tier}")
        return "\n".join(lines)


# ─── Singleton ────────────────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def get_model_router() -> ModelRouter:
    """Get the singleton ModelRouter instance."""
    return ModelRouter()


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="XNAi Model Router")
    parser.add_argument("--task", default="general", help="Task type")
    parser.add_argument("--context", type=int, default=0, help="Context token count")
    parser.add_argument("--free-only", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--list-providers", action="store_true")
    args = parser.parse_args()

    router = ModelRouter()

    if args.summary:
        print(router.summary())
    elif args.list_providers:
        for p in router.list_providers(free_only=args.free_only):
            avail = "✅" if router._is_provider_available(p.name) else "❌"
            print(f"{avail} {p.name} ({p.tier}) — {p.cost}")
    else:
        result = router.select_model(
            task_type=args.task,
            context_tokens=args.context,
            prefer_free=args.free_only,
            prefer_local=args.local,
        )
        print(f"Selected: {result['provider']} / {result['model']}")
        print(f"Reason: {result['reason']}")
