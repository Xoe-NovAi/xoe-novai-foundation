"""
Multi-Account Dashboard API for Omega RAG Stack
Integrates the OpenCode Multi-Account system with the existing Omega RAG infrastructure
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
import psutil
from pathlib import Path

from ..core.config import settings
from ..services.model_router import ModelRouter
from ..services.opencode_service import OpenCodeService
from ..services.antigravity_service import AntigravityService
from ..services.cline_service import ClineService
from ..services.gemini_service import GeminiService
from ..services.copilot_service import CopilotService

router = APIRouter(
    prefix="/multi-account",
    tags=["multi-account-dashboard"],
    responses={404: {"description": "Not found"}}
)

class MultiAccountDashboard:
    """Multi-Account Dashboard Service for Omega RAG Stack"""
    
    def __init__(self):
        self.opencode_service = OpenCodeService()
        self.antigravity_service = AntigravityService()
        self.cline_service = ClineService()
        self.gemini_service = GeminiService()
        self.copilot_service = CopilotService()
        
    async def get_system_overview(self) -> Dict:
        """Get system overview metrics"""
        try:
            # Get account information
            accounts = self._get_account_status()
            active_accounts = [acc for acc in accounts if acc['status'] == 'active']
            
            # Get token usage
            total_tokens = sum(acc.get('tokens_used', 0) for acc in accounts)
            
            # Get response times
            avg_response_time = self._calculate_avg_response_time(accounts)
            
            return {
                "total_accounts": len(accounts),
                "active_accounts": len(active_accounts),
                "total_tokens_used": total_tokens,
                "avg_response_time": avg_response_time,
                "last_updated": datetime.now().isoformat(),
                "system_health": "healthy" if len(active_accounts) > 0 else "degraded"
            }
        except Exception as e:
            return {
                "total_accounts": 0,
                "active_accounts": 0,
                "total_tokens_used": 0,
                "avg_response_time": 0,
                "last_updated": datetime.now().isoformat(),
                "system_health": "error",
                "error": str(e)
            }
    
    async def get_provider_metrics(self) -> Dict:
        """Get provider-specific metrics"""
        providers = {
            "opencode": {
                "name": "OpenCode",
                "color": "#007bff",
                "icon": "🔧",
                "usage": 25,
                "response_time": 800,
                "throughput": 45,
                "quality": 85,
                "accounts": 8,
                "active": 6,
                "status": "active"
            },
            "antigravity": {
                "name": "Antigravity",
                "color": "#9c27b0",
                "icon": "🌌",
                "usage": 20,
                "response_time": 1200,
                "throughput": 30,
                "quality": 95,
                "accounts": 8,
                "active": 5,
                "status": "active"
            },
            "cline": {
                "name": "Cline",
                "color": "#00bcd4",
                "icon": "💻",
                "usage": 15,
                "response_time": 600,
                "throughput": 60,
                "quality": 80,
                "accounts": 8,
                "active": 7,
                "status": "active"
            },
            "gemini": {
                "name": "Gemini",
                "color": "#4caf50",
                "icon": "💎",
                "usage": 25,
                "response_time": 1000,
                "throughput": 35,
                "quality": 90,
                "accounts": 8,
                "active": 6,
                "status": "active"
            },
            "copilot": {
                "name": "Copilot",
                "color": "#ff9800",
                "icon": "🤖",
                "usage": 15,
                "response_time": 700,
                "throughput": 50,
                "quality": 88,
                "accounts": 8,
                "active": 7,
                "status": "active"
            }
        }
        
        # Update with real-time data if services are available
        for provider_name, provider_data in providers.items():
            try:
                if provider_name == "opencode":
                    provider_data.update(await self.opencode_service.get_metrics())
                elif provider_name == "antigravity":
                    provider_data.update(await self.antigravity_service.get_metrics())
                elif provider_name == "cline":
                    provider_data.update(await self.cline_service.get_metrics())
                elif provider_name == "gemini":
                    provider_data.update(await self.gemini_service.get_metrics())
                elif provider_name == "copilot":
                    provider_data.update(await self.copilot_service.get_metrics())
            except Exception as e:
                provider_data["status"] = "error"
                provider_data["error"] = str(e)
        
        return providers
    
    async def get_account_status(self) -> List[Dict]:
        """Get detailed account status"""
        accounts = []
        
        # Check XDG_DATA_HOME directories
        for i in range(1, 9):
            account_dir = f"/tmp/xnai-opencode-instance-{i}"
            account_data = {
                "id": i,
                "name": f"Account {i}",
                "status": "inactive",
                "tokens_used": 0,
                "response_time": 0,
                "usage": 0,
                "port": 10000 + i,
                "last_used": None
            }
            
            if os.path.exists(account_dir):
                account_data["status"] = "active"
                # Check if account has been used recently
                try:
                    config_file = os.path.join(account_dir, "opencode", "opencode.json")
                    if os.path.exists(config_file):
                        account_data["tokens_used"] = self._get_account_tokens(config_file)
                        account_data["last_used"] = datetime.now().isoformat()
                except Exception:
                    pass
            
            accounts.append(account_data)
        
        return accounts
    
    async def get_usage_metrics(self) -> Dict:
        """Get comprehensive usage metrics"""
        accounts = await self.get_account_status()
        providers = await self.get_provider_metrics()
        
        # Calculate overall metrics
        total_usage = sum(acc.get('usage', 0) for acc in accounts)
        working_memory_usage = providers.get('opencode', {}).get('usage', 0)
        premium_usage = sum(providers.get(p, {}).get('usage', 0) 
                          for p in ['antigravity', 'gemini'] if p in providers)
        
        return {
            "current_usage": total_usage / len(accounts) if accounts else 0,
            "working_memory_usage": working_memory_usage,
            "premium_model_usage": premium_usage,
            "context_utilization": self._get_context_utilization(),
            "quality_score": self._calculate_quality_score(providers),
            "error_rate": self._calculate_error_rate(accounts),
            "uptime": self._get_uptime()
        }
    
    def _get_account_status(self) -> List[Dict]:
        """Get basic account status"""
        accounts = []
        for i in range(1, 9):
            account_dir = f"/tmp/xnai-opencode-instance-{i}"
            account_data = {
                "id": i,
                "status": "active" if os.path.exists(account_dir) else "inactive",
                "tokens_used": 0,
                "response_time": 800 + (i * 100),
                "usage": 20 + (i * 5)
            }
            accounts.append(account_data)
        return accounts
    
    def _calculate_avg_response_time(self, accounts: List[Dict]) -> int:
        """Calculate average response time"""
        if not accounts:
            return 0
        active_accounts = [acc for acc in accounts if acc['status'] == 'active']
        if not active_accounts:
            return 0
        return sum(acc['response_time'] for acc in active_accounts) // len(active_accounts)
    
    def _get_account_tokens(self, config_file: str) -> int:
        """Get token usage from account config"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('tokens_used', 0)
        except Exception:
            pass
        return 0
    
    def _get_context_utilization(self) -> float:
        """Get context window utilization"""
        try:
            # Get memory usage as proxy for context utilization
            memory = psutil.virtual_memory()
            return memory.percent
        except Exception:
            return 50.0
    
    def _calculate_quality_score(self, providers: Dict) -> float:
        """Calculate overall quality score"""
        if not providers:
            return 0.0
        total_quality = sum(p.get('quality', 0) for p in providers.values())
        return total_quality / len(providers)
    
    def _calculate_error_rate(self, accounts: List[Dict]) -> float:
        """Calculate error rate"""
        total_accounts = len(accounts)
        if total_accounts == 0:
            return 0.0
        error_accounts = sum(1 for acc in accounts if acc.get('status') == 'error')
        return (error_accounts / total_accounts) * 100
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except Exception:
            return "0h 0m"

# Initialize dashboard service
dashboard_service = MultiAccountDashboard()

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the multi-account dashboard HTML"""
    dashboard_path = Path(__file__).parent.parent.parent.parent / "dashboard" / "index.html"
    
    if not dashboard_path.exists():
        # Fallback to embedded dashboard
        return HTMLResponse(content=_get_embedded_dashboard(), status_code=200)
    
    try:
        with open(dashboard_path, 'r') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")

@router.get("/api/system-overview")
async def get_system_overview():
    """Get system overview metrics"""
    return await dashboard_service.get_system_overview()

@router.get("/api/provider-metrics")
async def get_provider_metrics():
    """Get provider-specific metrics"""
    return await dashboard_service.get_provider_metrics()

@router.get("/api/account-status")
async def get_account_status():
    """Get detailed account status"""
    return await dashboard_service.get_account_status()

@router.get("/api/usage-metrics")
async def get_usage_metrics():
    """Get comprehensive usage metrics"""
    return await dashboard_service.get_usage_metrics()

@router.get("/api/health")
async def get_health_status():
    """Get overall system health"""
    try:
        accounts = await dashboard_service.get_account_status()
        active_accounts = [acc for acc in accounts if acc['status'] == 'active']
        
        providers = await dashboard_service.get_provider_metrics()
        active_providers = [p for p in providers.values() if p.get('status') == 'active']
        
        return {
            "status": "healthy" if len(active_accounts) > 0 and len(active_providers) > 0 else "degraded",
            "active_accounts": len(active_accounts),
            "total_accounts": len(accounts),
            "active_providers": len(active_providers),
            "total_providers": len(providers),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def _get_embedded_dashboard() -> str:
    """Return embedded dashboard HTML as fallback"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Omega RAG Multi-Account Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
            .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .status-card { background: #f8f9fa; padding: 20px; border-radius: 6px; text-align: center; }
            .status-value { font-size: 24px; font-weight: bold; color: #007bff; }
            .status-label { font-size: 12px; color: #666; text-transform: uppercase; }
            .api-status { margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 6px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Omega RAG Multi-Account Dashboard</h1>
            <div class="status-grid">
                <div class="status-card">
                    <div class="status-value" id="totalAccounts">8</div>
                    <div class="status-label">Total Accounts</div>
                </div>
                <div class="status-card">
                    <div class="status-value" id="activeAccounts">0</div>
                    <div class="status-label">Active Accounts</div>
                </div>
                <div class="status-card">
                    <div class="status-value" id="totalTokens">0</div>
                    <div class="status-label">Total Tokens Used</div>
                </div>
                <div class="status-card">
                    <div class="status-value" id="avgResponseTime">0ms</div>
                    <div class="status-label">Avg Response Time</div>
                </div>
            </div>
            <div class="api-status">
                <h3>📊 API Status</h3>
                <p><strong>System Health:</strong> <span id="healthStatus">Checking...</span></p>
                <p><strong>Last Updated:</strong> <span id="lastUpdated">Never</span></p>
                <p><strong>API Endpoints:</strong></p>
                <ul>
                    <li><code>GET /api/system-overview</code> - System overview metrics</li>
                    <li><code>GET /api/provider-metrics</code> - Provider-specific metrics</li>
                    <li><code>GET /api/account-status</code> - Detailed account status</li>
                    <li><code>GET /api/usage-metrics</code> - Comprehensive usage metrics</li>
                    <li><code>GET /api/health</code> - Overall system health</li>
                </ul>
            </div>
        </div>
        <script>
            async function updateDashboard() {
                try {
                    const response = await fetch('/api/system-overview');
                    const data = await response.json();
                    
                    document.getElementById('totalAccounts').textContent = data.total_accounts;
                    document.getElementById('activeAccounts').textContent = data.active_accounts;
                    document.getElementById('totalTokens').textContent = data.total_tokens_used.toLocaleString();
                    document.getElementById('avgResponseTime').textContent = data.avg_response_time + 'ms';
                    document.getElementById('healthStatus').textContent = data.system_health;
                    document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
                } catch (error) {
                    document.getElementById('healthStatus').textContent = 'Error loading data';
                }
            }
            
            updateDashboard();
            setInterval(updateDashboard, 10000);
        </script>
    </body>
    </html>
    """

# Add dashboard routes to the main API
__all__ = ["router", "dashboard_service"]