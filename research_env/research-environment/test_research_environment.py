#!/usr/bin/env python3
"""
Test script for the XNAi Foundation Research Environment

This script validates the complete research environment setup including:
- JupyterLab integration
- Vikunja task management
- Model router functionality
- Research queue processing
"""

import asyncio
import os
import sys
import logging
import requests
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchEnvironmentTester:
    """Test suite for the research environment."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.vikunja_url = os.getenv('VIKUNJA_URL', 'http://localhost:3456/api/v1')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.jupyterlab_url = 'http://localhost:8888'
        
        self.test_results = []
        
        logger.info("Initialized Research Environment Tester")
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        logger.info(f"{status}: {test_name} - {message}")
    
    async def test_vikunja_connection(self) -> bool:
        """Test connection to Vikunja API."""
        try:
            response = requests.get(f"{self.vikunja_url}/health", timeout=10)
            success = response.status_code == 200
            self.log_test("Vikunja Connection", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Vikunja Connection", False, f"Error: {e}")
            return False
    
    async def test_jupyterlab_connection(self) -> bool:
        """Test connection to JupyterLab."""
        try:
            response = requests.get(f"{self.jupyterlab_url}/api", timeout=10)
            success = response.status_code == 200
            self.log_test("JupyterLab Connection", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("JupyterLab Connection", False, f"Error: {e}")
            return False
    
    async def test_redis_connection(self) -> bool:
        """Test connection to Redis."""
        try:
            import redis.asyncio as aioredis
            
            redis_client = aioredis.from_url(self.redis_url)
            await redis_client.ping()
            await redis_client.close()
            
            self.log_test("Redis Connection", True, "Connected successfully")
            return True
        except Exception as e:
            self.log_test("Redis Connection", False, f"Error: {e}")
            return False
    
    async def test_model_router_import(self) -> bool:
        """Test model router module import."""
        try:
            sys.path.append('scripts')
            from model_router import ModelRouter
            
            router = ModelRouter('config/model-router.yaml')
            self.log_test("Model Router Import", True, "Module imported successfully")
            return True
        except Exception as e:
            self.log_test("Model Router Import", False, f"Error: {e}")
            return False
    
    async def test_vikunja_integration_import(self) -> bool:
        """Test Vikunja integration module import."""
        try:
            sys.path.append('scripts')
            from jupyter_vikunja_integration import VikunjaIntegration
            
            integration = VikunjaIntegration(self.vikunja_url)
            self.log_test("Vikunja Integration Import", True, "Module imported successfully")
            return True
        except Exception as e:
            self.log_test("Vikunja Integration Import", False, f"Error: {e}")
            return False
    
    async def test_create_research_task(self) -> bool:
        """Test creating a research task."""
        try:
            sys.path.append('scripts')
            from jupyter_vikunja_integration import create_task_from_notebook
            from enum import Enum
            
            # Create a test task
            test_task = create_task_from_notebook(
                title="Test Research Task",
                description="This is a test task for validation",
                project="Development",
                job_type="analysis",
                content="This is test content for the research task.",
                priority=3,
                labels=["test", "validation"]
            )
            
            success = test_task is not None
            message = f"Task created: {test_task['id']}" if success else "Task creation failed"
            self.log_test("Create Research Task", success, message)
            return success
        except Exception as e:
            self.log_test("Create Research Task", False, f"Error: {e}")
            return False
    
    async def test_model_selection(self) -> bool:
        """Test model selection functionality."""
        try:
            sys.path.append('scripts')
            from model_router import ModelRouter
            
            router = ModelRouter('config/model-router.yaml')
            
            # Test model selection
            model_info = await router.select_model('analysis', 'This is test content')
            
            success = 'model' in model_info and 'reasoning' in model_info
            message = f"Selected model: {model_info.get('model', 'Unknown')}" if success else "Model selection failed"
            self.log_test("Model Selection", success, message)
            return success
        except Exception as e:
            self.log_test("Model Selection", False, f"Error: {e}")
            return False
    
    async def test_research_queue(self) -> bool:
        """Test research queue functionality."""
        try:
            import redis.asyncio as aioredis
            
            redis_client = aioredis.from_url(self.redis_url)
            
            # Test queue operations
            test_data = {
                'task_id': 999,
                'content': 'Test content',
                'job_type': 'test',
                'priority': 1
            }
            
            # Add to queue
            await redis_client.rpush('test_queue', json.dumps(test_data))
            
            # Get from queue
            result = await redis_client.lpop('test_queue')
            
            # Clean up
            await redis_client.delete('test_queue')
            await redis_client.close()
            
            success = result is not None
            message = "Queue operations successful" if success else "Queue operations failed"
            self.log_test("Research Queue", success, message)
            return success
        except Exception as e:
            self.log_test("Research Queue", False, f"Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests and generate report."""
        logger.info("Starting Research Environment Tests...")
        
        # Run individual tests
        tests = [
            ("Vikunja Connection", self.test_vikunja_connection()),
            ("JupyterLab Connection", self.test_jupyterlab_connection()),
            ("Redis Connection", self.test_redis_connection()),
            ("Model Router Import", self.test_model_router_import()),
            ("Vikunja Integration Import", self.test_vikunja_integration_import()),
            ("Create Research Task", self.test_create_research_task()),
            ("Model Selection", self.test_model_selection()),
            ("Research Queue", self.test_research_queue())
        ]
        
        results = []
        for test_name, test_coro in tests:
            logger.info(f"Running test: {test_name}")
            result = await test_coro
            results.append((test_name, result))
        
        # Generate report
        self.generate_report()
        
        # Return overall success
        return all(result for _, result in results)
    
    def generate_report(self):
        """Generate test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("RESEARCH ENVIRONMENT TEST REPORT")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("\nDetailed Results:")
        print("-"*60)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
        
        print("="*60)
        
        if failed_tests == 0:
            print("🎉 All tests passed! Research environment is ready.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Please check the issues above.")
        
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'results': self.test_results
            }, f, indent=2)
        
        logger.info(f"Test report saved to: {report_file}")


async def main():
    """Main entry point for testing."""
    tester = ResearchEnvironmentTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            logger.info("🎉 All tests passed! Research environment is ready.")
            sys.exit(0)
        else:
            logger.error("⚠️ Some tests failed. Please check the issues above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())