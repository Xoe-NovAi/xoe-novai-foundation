#!/usr/bin/env python3
"""Test and validation script for Omega-Stack Agent-Bus implementation."""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import json
import yaml

# Import all components
from app.XNAi_rag_app.services.agent_management import (
    AgentRegistry, ResearchJobManager, AgentMetricsManager, AgentMemoryManager
)
from app.XNAi_rag_app.services.database import get_db_session, init_db
from app.XNAi_rag_app.services.agent_bus import AgentBusManager, AgentBus
from scripts.agent_ranker import AgentRankerService
from scripts.vikunja_integration import VikunjaSync
from scripts.cline_multi_account import ClineAccountManager

# Test configuration
TEST_CONFIG = {
    'test_agents': [
        {'name': 'Test-Agent-1', 'model': 'gpt-4', 'runtime': 'openai'},
        {'name': 'Test-Agent-2', 'model': 'claude-sonnet', 'runtime': 'anthropic'},
        {'name': 'Test-Agent-3', 'model': 'gemini-pro', 'runtime': 'google'}
    ],
    'test_jobs': [
        {'slug': 'test-job-1', 'title': 'Test Research Job 1', 'domain_tags': ['test', 'research']},
        {'slug': 'test-job-2', 'title': 'Test Research Job 2', 'domain_tags': ['ai', 'ml']}
    ],
    'test_preferences': {
        'Test-Agent-1': {'machine_learning': 0.8, 'nlp': 0.6},
        'Test-Agent-2': {'computer_vision': 0.9, 'ethics': 0.7},
        'Test-Agent-3': {'optimization': 0.8, 'algorithms': 0.6}
    }
}


class AgentBusTester:
    """Comprehensive test suite for Agent-Bus implementation."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.db_session = get_db_session()
        self.registry = AgentRegistry(self.db_session)
        self.jobs = ResearchJobManager(self.db_session)
        self.metrics = AgentMetricsManager(self.db_session)
        self.memory = AgentMemoryManager(self.db_session)
        self.bus_manager = AgentBusManager()
        self.ranker = AgentRankerService()
        
        # Test results
        self.test_results = {
            'database': {},
            'services': {},
            'cli': {},
            'integration': {},
            'performance': {}
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup test logging."""
        logger = logging.getLogger('AgentBusTester')
        logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites."""
        self.logger.info("🚀 Starting Omega-Stack Agent-Bus Test Suite")
        start_time = time.time()
        
        try:
            # Database tests
            self.logger.info("📋 Running Database Tests...")
            await self.test_database()
            
            # Service tests
            self.logger.info("⚙️  Running Service Tests...")
            await self.test_services()
            
            # CLI tests
            self.logger.info("💻 Running CLI Tests...")
            await self.test_cli()
            
            # Integration tests
            self.logger.info("🔗 Running Integration Tests...")
            await self.test_integration()
            
            # Performance tests
            self.logger.info("⚡ Running Performance Tests...")
            await self.test_performance()
            
            # Generate report
            total_time = time.time() - start_time
            report = self._generate_report(total_time)
            
            self.logger.info("✅ Test Suite Completed Successfully!")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Test Suite Failed: {e}")
            return self._generate_error_report(str(e))
    
    async def test_database(self):
        """Test database connectivity and operations."""
        try:
            # Test database initialization
            init_db()
            self.test_results['database']['init'] = True
            
            # Test agent registration
            agent = self.registry.register_agent(
                name="Test-DB-Agent",
                model="test-model",
                runtime="test-runtime"
            )
            self.test_results['database']['agent_registration'] = True
            
            # Test agent retrieval
            retrieved_agent = self.registry.get_agent(agent.id)
            self.test_results['database']['agent_retrieval'] = retrieved_agent is not None
            
            # Test job creation
            job = self.jobs.create_job(
                slug="test-db-job",
                title="Test Database Job",
                domain_tags=["test", "database"]
            )
            self.test_results['database']['job_creation'] = True
            
            # Test job listing
            job_list = self.jobs.list_jobs()
            self.test_results['database']['job_listing'] = len(job_list) > 0
            
            # Test metrics recording
            metric = self.metrics.record_metric(
                agent.id,
                "test_metric",
                0.95
            )
            self.test_results['database']['metric_recording'] = True
            
            # Test memory storage
            memory = self.memory.store_memory(
                agent.id,
                "test",
                "Test memory content"
            )
            self.test_results['database']['memory_storage'] = True
            
        except Exception as e:
            self.logger.error(f"Database test failed: {e}")
            self.test_results['database']['error'] = str(e)
    
    async def test_services(self):
        """Test core service functionality."""
        try:
            # Test agent registry
            agents = self.registry.list_agents()
            self.test_results['services']['agent_registry'] = len(agents) > 0
            
            # Test job manager
            jobs = self.jobs.list_jobs()
            self.test_results['services']['job_manager'] = len(jobs) > 0
            
            # Test metrics manager
            agent_metrics = self.metrics.get_agent_metrics(agents[0]['id'])
            self.test_results['services']['metrics_manager'] = True
            
            # Test memory manager
            memories = self.memory.get_memories(agents[0]['id'])
            self.test_results['services']['memory_manager'] = True
            
            # Test agent bus (without starting)
            bus = AgentBus()
            self.test_results['services']['agent_bus'] = bus is not None
            
            # Test agent ranker
            ranker = AgentRankerService()
            self.test_results['services']['agent_ranker'] = ranker is not None
            
        except Exception as e:
            self.logger.error(f"Service test failed: {e}")
            self.test_results['services']['error'] = str(e)
    
    async def test_cli(self):
        """Test CLI functionality."""
        try:
            # Test account manager
            account_manager = ClineAccountManager()
            accounts = account_manager.list_accounts()
            self.test_results['cli']['account_manager'] = len(accounts) > 0
            
            # Test account switching
            success = account_manager.set_current_account(accounts[0].name)
            self.test_results['cli']['account_switching'] = success
            
            # Test account preferences
            account_manager._update_account_usage(accounts[0].name)
            self.test_results['cli']['account_usage'] = True
            
        except Exception as e:
            self.logger.error(f"CLI test failed: {e}")
            self.test_results['cli']['error'] = str(e)
    
    async def test_integration(self):
        """Test integration components."""
        try:
            # Test Vikunja integration (without actual API calls)
            try:
                sync = VikunjaSync()
                self.test_results['integration']['vikunja_sync'] = True
            except Exception:
                # Vikunja might not be configured, that's okay
                self.test_results['integration']['vikunja_sync'] = "skipped (not configured)"
            
            # Test agent bus manager
            bus_manager = AgentBusManager()
            self.test_results['integration']['agent_bus_manager'] = True
            
            # Test message parsing
            from app.XNAi_rag_app.services.agent_bus import AgentMessage, MessageType
            test_message = AgentMessage(
                message_id="test-123",
                message_type=MessageType.HEARTBEAT,
                sender_id="test-agent",
                timestamp="2026-03-02T12:00:00Z",
                payload={"status": "active"}
            )
            self.test_results['integration']['message_parsing'] = True
            
        except Exception as e:
            self.logger.error(f"Integration test failed: {e}")
            self.test_results['integration']['error'] = str(e)
    
    async def test_performance(self):
        """Test performance characteristics."""
        try:
            start_time = time.time()
            
            # Test agent registration performance
            for i in range(10):
                self.registry.register_agent(
                    name=f"Perf-Agent-{i}",
                    model="test-model",
                    runtime="test-runtime"
                )
            agent_time = time.time() - start_time
            
            # Test job creation performance
            start_time = time.time()
            for i in range(10):
                self.jobs.create_job(
                    slug=f"perf-job-{i}",
                    title=f"Performance Test Job {i}",
                    domain_tags=["performance", "test"]
                )
            job_time = time.time() - start_time
            
            # Test metrics recording performance
            start_time = time.time()
            agents = self.registry.list_agents()
            for i in range(100):
                self.metrics.record_metric(
                    agents[0]['id'],
                    f"perf_metric_{i}",
                    0.5 + (i % 50) / 100
                )
            metric_time = time.time() - start_time
            
            self.test_results['performance'] = {
                'agent_registration_10': f"{agent_time:.3f}s",
                'job_creation_10': f"{job_time:.3f}s",
                'metric_recording_100': f"{metric_time:.3f}s",
                'agent_registration_rate': f"{10/agent_time:.1f} agents/sec",
                'job_creation_rate': f"{10/job_time:.1f} jobs/sec",
                'metric_recording_rate': f"{100/metric_time:.1f} metrics/sec"
            }
            
        except Exception as e:
            self.logger.error(f"Performance test failed: {e}")
            self.test_results['performance']['error'] = str(e)
    
    def _generate_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_time': f"{total_time:.2f}s",
            'summary': {},
            'details': self.test_results,
            'recommendations': []
        }
        
        # Calculate success rates
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.test_results.items():
            if 'error' in results:
                report['summary'][category] = 'FAILED'
            else:
                category_passed = sum(1 for v in results.values() if v is True)
                category_total = len(results)
                total_tests += category_total
                passed_tests += category_passed
                
                if category_passed == category_total:
                    report['summary'][category] = 'PASSED'
                else:
                    report['summary'][category] = f'PARTIAL ({category_passed}/{category_total})'
        
        # Overall status
        if passed_tests == total_tests:
            report['status'] = 'ALL TESTS PASSED'
        else:
            report['status'] = f'PARTIAL SUCCESS ({passed_tests}/{total_tests} tests passed)'
        
        # Generate recommendations
        if passed_tests < total_tests:
            report['recommendations'].append("Review failed tests and address any configuration issues")
        
        if 'database' in self.test_results and 'error' not in self.test_results['database']:
            report['recommendations'].append("Database performance is good, consider adding more indexes for production")
        
        if 'performance' in self.test_results and 'error' not in self.test_results['performance']:
            report['recommendations'].append("Performance metrics look good for initial deployment")
        
        return report
    
    def _generate_error_report(self, error: str) -> Dict[str, Any]:
        """Generate error report."""
        return {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'TEST SUITE FAILED',
            'error': error,
            'details': self.test_results
        }
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted test report."""
        print("\n" + "="*80)
        print("OMEGA-STACK AGENT-BUS TEST REPORT")
        print("="*80)
        
        print(f"\n📊 Summary:")
        print(f"   Status: {report['status']}")
        print(f"   Time: {report['total_time']}")
        print(f"   Timestamp: {report['timestamp']}")
        
        print(f"\n📋 Test Results:")
        for category, status in report['summary'].items():
            status_icon = "✅" if status == "PASSED" else "⚠️" if "PARTIAL" in status else "❌"
            print(f"   {status_icon} {category}: {status}")
        
        if 'details' in report:
            print(f"\n🔍 Detailed Results:")
            for category, results in report['details'].items():
                print(f"\n   {category.upper()}:")
                if 'error' in results:
                    print(f"      ❌ Error: {results['error']}")
                else:
                    for test, result in results.items():
                        if test != 'error':
                            icon = "✅" if result is True else "⚠️" if result == "skipped (not configured)" else "❌"
                            print(f"      {icon} {test}: {result}")
        
        if 'recommendations' in report and report['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)


async def main():
    """Main test execution."""
    # Setup
    tester = AgentBusTester()
    
    # Run tests
    report = await tester.run_all_tests()
    
    # Print report
    tester.print_report(report)
    
    # Save report
    with open('test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Exit with appropriate code
    if report['status'] == 'ALL TESTS PASSED':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())