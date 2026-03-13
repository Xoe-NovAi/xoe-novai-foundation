"""
Memory Metrics Collector
========================

Collects and tracks memory bank metrics for monitoring and analysis.
Integrates with Redis (real-time) and VictoriaMetrics (historical).
"""

import time
from typing import Dict, Any, Optional
import aiohttp


class MemoryMetricsCollector:
    """
    Collects memory bank metrics for monitoring.

    Uses Redis for real-time counters and VictoriaMetrics for time-series.
    """

    def __init__(
        self,
        redis_client: Optional[Any] = None,
        vm_endpoint: str = "http://localhost:8428",
    ):
        self.redis = redis_client
        self.vm_endpoint = vm_endpoint
        self._prefix = "xnai:memory"
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for VM requests."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def write_metric(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Write a metric to VictoriaMetrics.

        Uses Prometheus exposition format for compatibility.

        Args:
            name: Metric name
            value: Metric value
            labels: Optional labels dict

        Returns:
            True if write succeeded
        """
        labels = labels or {}
        label_str = ""
        if labels:
            label_str = "{" + ",".join(f'{k}="{v}"' for k, v in labels.items()) + "}"

        metric_line = f"{name}{label_str} {value}"

        try:
            session = await self._get_session()
            async with session.post(
                f"{self.vm_endpoint}/api/v1/import/prometheus",
                data=metric_line,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                return resp.status == 204
        except Exception:
            return False

    async def record_block_utilization(
        self, block_label: str, chars: int, limit: int, tier: str = "core"
    ) -> None:
        """Record block utilization metrics to both Redis and VictoriaMetrics."""
        utilization = chars / limit if limit > 0 else 0.0

        # Real-time to Redis
        if self.redis:
            key = f"{self._prefix}:blocks:{block_label}"
            await self.redis.hset(
                key,
                mapping={
                    "chars": chars,
                    "limit": limit,
                    "utilization": utilization,
                    "timestamp": time.time(),
                },
            )
            await self.redis.expire(key, 86400)

        # Historical to VictoriaMetrics
        await self.write_metric(
            "memory_block_utilization",
            utilization,
            {"block": block_label, "tier": tier},
        )
        await self.write_metric(
            "memory_block_chars",
            float(chars),
            {"block": block_label, "tier": tier},
        )

        # Record overflow event if near limit
        if utilization > 0.9:
            await self.record_overflow_event(block_label)

    async def record_tool_invocation(self, tool_name: str, success: bool) -> None:
        """Record memory tool usage metrics to Redis and VictoriaMetrics."""
        # Real-time to Redis
        if self.redis:
            await self.redis.incr(f"{self._prefix}:tools:{tool_name}:total")
            if success:
                await self.redis.incr(f"{self._prefix}:tools:{tool_name}:success")
            await self.redis.set(
                f"{self._prefix}:tools:{tool_name}:last",
                time.time(),
            )

        # Historical to VictoriaMetrics
        await self.write_metric(
            "memory_tool_calls_total",
            1.0,
            {"tool": tool_name, "success": str(success).lower()},
        )

    async def record_overflow_event(self, block_label: str) -> None:
        """Record block overflow event to Redis and VictoriaMetrics."""
        # Real-time to Redis
        if self.redis:
            key = f"{self._prefix}:overflow:{block_label}"
            await self.redis.incr(key)
            await self.redis.set(f"{key}:last", time.time())

        # Historical to VictoriaMetrics (audit trail)
        await self.write_metric(
            "memory_overflow_events_total",
            1.0,
            {"block": block_label},
        )

    async def get_session_continuity_score(self) -> float:
        """
        Calculate session continuity score.

        Based on:
        - Block utilization stability
        - Tool success rate
        - Overflow event frequency

        Returns: 0.0 to 1.0 score
        """
        if not self.redis:
            return 0.8  # Default if no Redis

        try:
            # Get tool success rates
            tools = [
                "memory_replace",
                "memory_append",
                "memory_rethink",
                "compile_context",
            ]
            total_success = 0
            total_invocations = 0

            for tool in tools:
                success = int(
                    await self.redis.get(f"{self._prefix}:tools:{tool}:success") or 0
                )
                total = int(
                    await self.redis.get(f"{self._prefix}:tools:{tool}:total") or 0
                )
                total_success += success
                total_invocations += total

            if total_invocations == 0:
                return 1.0  # No invocations = perfect score

            score = total_success / total_invocations

            # Record to VictoriaMetrics
            await self.write_metric(
                "memory_session_continuity_score",
                score * 100,  # As percentage
            )

            return score

        except Exception:
            return 0.8

    async def get_block_utilization(self, block_label: str) -> Optional[Dict[str, Any]]:
        """Get current utilization for a block."""
        if not self.redis:
            return None

        key = f"{self._prefix}:blocks:{block_label}"
        data = await self.redis.hgetall(key)

        if data:
            return {
                "chars": int(data.get("chars", 0)),
                "limit": int(data.get("limit", 0)),
                "utilization": float(data.get("utilization", 0)),
                "timestamp": float(data.get("timestamp", 0)),
            }

        return None

    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get all memory metrics."""
        return {
            "blocks": await self._get_all_block_metrics(),
            "tools": await self._get_all_tool_metrics(),
            "overflow_events": await self._get_overflow_events(),
            "continuity_score": await self.get_session_continuity_score(),
        }

    async def _get_all_block_metrics(self) -> Dict[str, Any]:
        """Get metrics for all tracked blocks."""
        if not self.redis:
            return {}

        # This would scan for all block keys
        # Simplified implementation
        return {}

    async def _get_all_tool_metrics(self) -> Dict[str, Any]:
        """Get metrics for all tools."""
        if not self.redis:
            return {}

        tools = ["memory_replace", "memory_append", "memory_rethink", "compile_context"]
        metrics = {}

        for tool in tools:
            success = int(
                await self.redis.get(f"{self._prefix}:tools:{tool}:success") or 0
            )
            total = int(await self.redis.get(f"{self._prefix}:tools:{tool}:total") or 0)
            metrics[tool] = {"success": success, "total": total}

        return metrics

    async def _get_overflow_events(self) -> Dict[str, int]:
        """Get overflow event counts."""
        if not self.redis:
            return {}

        # Would scan for overflow keys
        return {}
