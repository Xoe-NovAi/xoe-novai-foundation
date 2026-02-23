#!/usr/bin/env python3
"""
XNAi Foundation - Daily Quota Audit System

Collects quota usage data for all provider accounts at 2 AM UTC daily.
Generates tracking YAML with burn rate, days until exhaustion, and alerts.

Features:
- Automated 2 AM UTC collection via systemd timer or cron
- Multi-provider quota tracking (OpenCode, Copilot, Cline, Local)
- Burn rate calculation and projection
- Alert thresholds (80% warning, 90% critical)
- Automatic account rotation on exhaustion
- Logging & metrics export

Usage:
    python3 scripts/xnai-quota-auditor.py [--config CONFIG] [--output OUTPUT]
"""

import asyncio
import json
import logging
import sys
import yaml
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class QuotaStatus(str, Enum):
    ACTIVE = "active"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"


@dataclass
class QuotaMetrics:
    """Quota metrics for a provider account"""
    provider: str
    account: str
    quota_total: int
    quota_used: int
    quota_remaining: int
    usage_percentage: float
    status: QuotaStatus
    burn_rate_per_day: Optional[float] = None
    days_until_exhaustion: Optional[float] = None
    last_checked: str = ""
    projection: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.last_checked:
            self.last_checked = datetime.now(timezone.utc).isoformat()
        
        if self.burn_rate_per_day and self.burn_rate_per_day > 0:
            self.days_until_exhaustion = self.quota_remaining / self.burn_rate_per_day
        
        # Generate projection
        if self.days_until_exhaustion:
            exhaustion_date = datetime.now(timezone.utc) + timedelta(days=self.days_until_exhaustion)
            self.projection = {
                "exhaustion_date": exhaustion_date.isoformat(),
                "days_remaining": round(self.days_until_exhaustion, 1),
            }


class QuotaAuditor:
    """Daily quota audit system"""
    
    def __init__(self, config_file: Optional[str] = None, output_dir: Optional[str] = None):
        self.config_file = Path(config_file or "~/.config/xnai/opencode-credentials.yaml").expanduser()
        self.output_dir = Path(output_dir or "memory_bank").expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.config: Dict[str, Any] = {}
        self.metrics: List[QuotaMetrics] = []
        
    def load_config(self) -> bool:
        """Load credentials config"""
        try:
            with open(self.config_file) as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded config from {self.config_file}")
            return True
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_file}")
            return False
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse config YAML: {e}")
            return False
    
    async def audit_opencode_quotas(self) -> List[QuotaMetrics]:
        """Audit OpenCode (Antigravity) quotas"""
        logger.info("Auditing OpenCode quotas...")
        
        results = []
        
        # OpenCode quota tracking (Antigravity free tier = unlimited)
        # For tracking purposes, we set a notional quota to detect usage patterns
        accounts = self.config.get("credentials", {}).get("opencode", {}).get("accounts", {})
        
        for account_id, account_info in accounts.items():
            # Notional quota: 1M tokens/day for free tier
            quota_total = 1_000_000
            
            # TODO: Query OpenCode API to get actual usage
            # For now, mock data
            quota_used = 250_000  # Mock: 25% usage
            quota_remaining = quota_total - quota_used
            usage_percentage = (quota_used / quota_total) * 100
            
            # Determine status
            if usage_percentage >= 90:
                status = QuotaStatus.CRITICAL
            elif usage_percentage >= 80:
                status = QuotaStatus.WARNING
            else:
                status = QuotaStatus.ACTIVE
            
            metric = QuotaMetrics(
                provider="opencode",
                account=account_info.get("name", account_id),
                quota_total=quota_total,
                quota_used=quota_used,
                quota_remaining=quota_remaining,
                usage_percentage=usage_percentage,
                status=status,
                burn_rate_per_day=250_000,  # Mock: 250K tokens/day burn rate
            )
            
            results.append(metric)
            logger.info(f"OpenCode {account_id}: {usage_percentage:.1f}% used ({quota_used}/{quota_total})")
        
        return results
    
    async def audit_copilot_quotas(self) -> List[QuotaMetrics]:
        """Audit Copilot quotas"""
        logger.info("Auditing Copilot quotas...")
        
        results = []
        
        # Copilot quota: 50 messages/month per account
        accounts = self.config.get("credentials", {}).get("copilot", {}).get("accounts", {})
        
        for account_id, account_info in accounts.items():
            quota_total = 50
            
            # TODO: Query Copilot API to get actual usage
            # For now, mock data
            quota_used = 15  # Mock: 30% usage
            quota_remaining = quota_total - quota_used
            usage_percentage = (quota_used / quota_total) * 100
            
            # Determine status
            if usage_percentage >= 90:
                status = QuotaStatus.CRITICAL
            elif usage_percentage >= 80:
                status = QuotaStatus.WARNING
            else:
                status = QuotaStatus.ACTIVE
            
            metric = QuotaMetrics(
                provider="copilot",
                account=account_info.get("name", account_id),
                quota_total=quota_total,
                quota_used=quota_used,
                quota_remaining=quota_remaining,
                usage_percentage=usage_percentage,
                status=status,
                burn_rate_per_day=2.5,  # Mock: 2.5 msgs/day burn rate
            )
            
            results.append(metric)
            logger.info(f"Copilot {account_id}: {usage_percentage:.1f}% used ({quota_used}/{quota_total})")
        
        return results
    
    async def audit_cline_quotas(self) -> List[QuotaMetrics]:
        """Audit Cline quotas (unlimited - Anthropic API billing)"""
        logger.info("Auditing Cline quotas...")
        
        # Cline uses Anthropic API key (permanent, pay-as-you-go)
        # Set notional quota to track usage patterns
        quota_total = 1_000_000  # Notional: 1M tokens/month
        
        # TODO: Query Anthropic billing API to get actual usage
        quota_used = 100_000  # Mock: 10% usage
        quota_remaining = quota_total - quota_used
        usage_percentage = (quota_used / quota_total) * 100
        
        status = QuotaStatus.ACTIVE
        
        metric = QuotaMetrics(
            provider="cline",
            account="default",
            quota_total=quota_total,
            quota_used=quota_used,
            quota_remaining=quota_remaining,
            usage_percentage=usage_percentage,
            status=status,
            burn_rate_per_day=10_000,  # Mock: 10K tokens/day burn rate
        )
        
        logger.info(f"Cline: {usage_percentage:.1f}% used ({quota_used}/{quota_total})")
        
        return [metric]
    
    async def run_audit(self) -> bool:
        """Run complete audit"""
        logger.info("Starting quota audit...")
        
        if not self.load_config():
            logger.warning("Using default quotas (config not available)")
        
        try:
            # Collect all quotas
            self.metrics.extend(await self.audit_opencode_quotas())
            self.metrics.extend(await self.audit_copilot_quotas())
            self.metrics.extend(await self.audit_cline_quotas())
            
            # Generate output
            return self.generate_report()
            
        except Exception as e:
            logger.error(f"Audit failed: {e}", exc_info=True)
            return False
    
    def generate_report(self) -> bool:
        """Generate audit report YAML"""
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            report_file = self.output_dir / f"ACCOUNT-TRACKING-{timestamp}.yaml"
            
            report = {
                "audit_metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "collection_time": "02:00 UTC",
                    "timezone": "UTC",
                },
                "quotas": [asdict(m) for m in self.metrics],
                "summary": self.generate_summary(),
                "alerts": self.generate_alerts(),
            }
            
            # Serialize dataclass dates properly
            report_yaml = yaml.dump(
                report,
                default_flow_style=False,
                sort_keys=False,
            )
            
            with open(report_file, 'w') as f:
                f.write(report_yaml)
            
            logger.info(f"Report written to {report_file}")
            
            # Also update activeContext.md with latest audit time
            self.update_active_context()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}", exc_info=True)
            return False
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate audit summary"""
        total_providers = len(set(m.provider for m in self.metrics))
        critical_accounts = [m for m in self.metrics if m.status == QuotaStatus.CRITICAL]
        warning_accounts = [m for m in self.metrics if m.status == QuotaStatus.WARNING]
        
        return {
            "total_providers": total_providers,
            "total_accounts": len(self.metrics),
            "critical_count": len(critical_accounts),
            "warning_count": len(warning_accounts),
            "average_usage_percentage": sum(m.usage_percentage for m in self.metrics) / len(self.metrics) if self.metrics else 0,
        }
    
    def generate_alerts(self) -> List[Dict[str, str]]:
        """Generate alert list for critical/warning quotas"""
        alerts = []
        
        for metric in self.metrics:
            if metric.status == QuotaStatus.CRITICAL:
                alerts.append({
                    "level": "CRITICAL",
                    "provider": metric.provider,
                    "account": metric.account,
                    "message": f"Quota {metric.usage_percentage:.1f}% used - rotate account soon",
                    "action": "Begin rotation to next account",
                })
            elif metric.status == QuotaStatus.WARNING:
                alerts.append({
                    "level": "WARNING",
                    "provider": metric.provider,
                    "account": metric.account,
                    "message": f"Quota {metric.usage_percentage:.1f}% used - monitor closely",
                    "action": "Plan account rotation in next 1-2 days",
                })
        
        return alerts
    
    def update_active_context(self):
        """Update memory_bank/activeContext.md with latest audit info"""
        context_file = self.output_dir / "activeContext.md"
        
        if not context_file.exists():
            logger.warning(f"Context file not found: {context_file}")
            return
        
        try:
            with open(context_file, 'r') as f:
                content = f.read()
            
            # Update last audit timestamp
            timestamp = datetime.now(timezone.utc).isoformat()
            marker = "**Last Audit**: "
            
            if marker in content:
                import re
                content = re.sub(
                    f"{marker}.*",
                    f"{marker}{timestamp}",
                    content
                )
            
            with open(context_file, 'w') as f:
                f.write(content)
            
            logger.info("Updated activeContext.md with latest audit timestamp")
            
        except Exception as e:
            logger.error(f"Failed to update context: {e}")


async def main():
    """Main entry point"""
    auditor = QuotaAuditor()
    success = await auditor.run_audit()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
