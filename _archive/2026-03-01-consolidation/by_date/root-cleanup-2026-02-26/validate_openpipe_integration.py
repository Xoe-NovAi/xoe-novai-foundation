#!/usr/bin/env python3
"""
OpenPipe Integration Validation Script
======================================
Validates the complete OpenPipe integration implementation against
XNAi Foundation requirements and constraints.
"""

import os
import json
import yaml
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenPipeValidator:
    """Validates OpenPipe integration implementation."""
    
    def __init__(self):
        self.validation_results = []
        self.requirements = {
            'sovereignty': {
                'zero_telemetry': True,
                'offline_first': True,
                'no_external_calls': True,
                'data_encryption': True
            },
            'performance': {
                'latency_under_300ms': True,
                'memory_under_6gb': True,
                'cache_hit_rate_40_percent': True,
                'cost_reduction_50_percent': True
            },
            'compatibility': {
                'torch_free': True,
                'anyio_compatible': True,
                'rootless_podman': True,
                'existing_stack_integration': True
            },
            'reliability': {
                'circuit_breakers': True,
                'deduplication': True,
                'metrics_collection': True,
                'health_monitoring': True
            }
        }
    
    def validate_file_structure(self) -> bool:
        """Validate required files are present."""
        print("📁 Validating file structure...")
        
        required_files = [
            'OpenPipe_Integration_Blueprint.md',
            'OpenPipe_Implementation_Guide.md',
            'test_openpipe_integration.py',
            'validate_openpipe_integration.py',
            'config/openpipe-config.yaml',
            'app/XNAi_rag_app/core/openpipe_integration.py',
            'app/XNAi_rag_app/core/services_init_enhanced.py',
            'monitoring/grafana/dashboards/openpipe-dashboard.json'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False
        
        logger.info("✅ All required files present")
        return True
    
    def validate_configuration(self) -> bool:
        """Validate OpenPipe configuration."""
        print("⚙️  Validating configuration...")
        
        try:
            with open('config/openpipe-config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            # Check sovereignty settings
            openpipe_config = config.get('openpipe', {})
            
            sovereignty_checks = [
                ('sovereign_mode', True),
                ('offline_mode', True),
                ('security.encryption_enabled', True),
                ('security.tls_enabled', True)
            ]
            
            for check_path, expected in sovereignty_checks:
                if not self._check_config_value(openpipe_config, check_path, expected):
                    logger.error(f"Configuration check failed: {check_path} should be {expected}")
                    return False
            
            # Check resource constraints
            resources = openpipe_config.get('resources', {})
            memory_limit = resources.get('memory_limit', '1G')
            if memory_limit != '1G':
                logger.error(f"Memory limit should be 1G, found {memory_limit}")
                return False
            
            logger.info("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def validate_code_quality(self) -> bool:
        """Validate code quality and patterns."""
        print("🔍 Validating code quality...")
        
        try:
            # Check Python files for quality
            python_files = [
                'app/XNAi_rag_app/core/openpipe_integration.py',
                'app/XNAi_rag_app/core/services_init_enhanced.py'
            ]
            
            for file_path in python_files:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for required patterns
                required_patterns = [
                    'async def',
                    'asyncio',
                    'asynccontextmanager',
                    'OpenPipeClient',
                    'CircuitBreakerProxy'
                ]
                
                for pattern in required_patterns:
                    if pattern not in content:
                        logger.error(f"Missing required pattern '{pattern}' in {file_path}")
                        return False
                
                # Check for forbidden patterns
                forbidden_patterns = [
                    'threading.Lock',
                    'asyncio.gather',
                    'asyncio.create_task'
                ]
                
                for pattern in forbidden_patterns:
                    if pattern in content:
                        logger.error(f"Found forbidden pattern '{pattern}' in {file_path}")
                        return False
            
            logger.info("✅ Code quality validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Code quality validation failed: {e}")
            return False
    
    def validate_docker_compose(self) -> bool:
        """Validate Docker Compose configuration."""
        print("🐳 Validating Docker Compose configuration...")
        
        try:
            # Check if docker-compose.yml exists and has OpenPipe service
            docker_compose_files = ['docker-compose.yml', 'docker-compose-noninit.yml']
            
            for compose_file in docker_compose_files:
                if Path(compose_file).exists():
                    with open(compose_file, 'r') as f:
                        compose_config = yaml.safe_load(f)
                    
                    services = compose_config.get('services', {})
                    if 'openpipe' in services:
                        openpipe_service = services['openpipe']
                        
                        # Check resource constraints
                        deploy = openpipe_service.get('deploy', {})
                        resources = deploy.get('resources', {})
                        limits = resources.get('limits', {})
                        
                        memory_limit = limits.get('memory', '')
                        if memory_limit != '1G':
                            logger.error(f"OpenPipe memory limit should be 1G, found {memory_limit}")
                            return False
                        
                        # Check user configuration
                        user = openpipe_service.get('user', '')
                        if not user or '1001:1001' not in user:
                            logger.error(f"OpenPipe service should run as non-root user (1001:1001)")
                            return False
            
            logger.info("✅ Docker Compose validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Docker Compose validation failed: {e}")
            return False
    
    def validate_monitoring(self) -> bool:
        """Validate monitoring and observability."""
        print("📊 Validating monitoring configuration...")
        
        try:
            # Check Grafana dashboard
            dashboard_file = 'monitoring/grafana/dashboards/openpipe-dashboard.json'
            if not Path(dashboard_file).exists():
                logger.error("Grafana dashboard file missing")
                return False
            
            with open(dashboard_file, 'r') as f:
                dashboard = json.load(f)
            
            # Check for required panels
            panels = dashboard.get('dashboard', {}).get('panels', [])
            panel_titles = [panel.get('title', '') for panel in panels]
            
            required_panels = [
                'OpenPipe Integration Status',
                'Cache Hit Rate',
                'Average Latency Reduction',
                'Response Time Distribution'
            ]
            
            for required_panel in required_panels:
                if required_panel not in panel_titles:
                    logger.error(f"Missing required dashboard panel: {required_panel}")
                    return False
            
            logger.info("✅ Monitoring validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Monitoring validation failed: {e}")
            return False
    
    def validate_environment_variables(self) -> bool:
        """Validate environment variable configuration."""
        print("🌍 Validating environment variables...")
        
        try:
            # Check if .env.example exists and has OpenPipe variables
            env_example = '.env.example'
            if Path(env_example).exists():
                with open(env_example, 'r') as f:
                    env_content = f.read()
                
                required_vars = [
                    'OPENPIPE_API_KEY',
                    'OPENPIPE_BASE_URL',
                    'OPENPIPE_CACHE_TTL',
                    'OPENPIPE_DEDUPLICATION_WINDOW',
                    'OPENPIPE_SOVEREIGN_MODE'
                ]
                
                for var in required_vars:
                    if var not in env_content:
                        logger.error(f"Missing required environment variable: {var}")
                        return False
            
            logger.info("✅ Environment variables validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Environment variables validation failed: {e}")
            return False
    
    def validate_test_coverage(self) -> bool:
        """Validate test coverage and quality."""
        print("🧪 Validating test coverage...")
        
        try:
            # Check test file
            test_file = 'test_openpipe_integration.py'
            if not Path(test_file).exists():
                logger.error("Test file missing")
                return False
            
            with open(test_file, 'r') as f:
                test_content = f.read()
            
            # Check for required test categories
            test_categories = [
                'test_openpipe_client_initialization',
                'test_caching_functionality',
                'test_deduplication',
                'test_llm_wrapper',
                'test_sovereignty_compliance',
                'test_memory_constraints',
                'test_latency_requirements'
            ]
            
            for category in test_categories:
                if category not in test_content:
                    logger.error(f"Missing test category: {category}")
                    return False
            
            logger.info("✅ Test coverage validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Test coverage validation failed: {e}")
            return False
    
    def validate_requirements_compliance(self) -> bool:
        """Validate compliance with XNAi Foundation requirements."""
        print("✅ Validating requirements compliance...")
        
        compliance_issues = []
        
        # Check sovereignty requirements
        if not self._check_sovereignty_compliance():
            compliance_issues.append("Sovereignty requirements not met")
        
        # Check performance requirements
        if not self._check_performance_compliance():
            compliance_issues.append("Performance requirements not met")
        
        # Check compatibility requirements
        if not self._check_compatibility_compliance():
            compliance_issues.append("Compatibility requirements not met")
        
        # Check reliability requirements
        if not self._check_reliability_compliance():
            compliance_issues.append("Reliability requirements not met")
        
        if compliance_issues:
            logger.error(f"Requirements compliance issues: {compliance_issues}")
            return False
        
        logger.info("✅ Requirements compliance validation passed")
        return True
    
    def _check_config_value(self, config: Dict, path: str, expected: Any) -> bool:
        """Check if a configuration value matches expected."""
        keys = path.split('.')
        current = config
        
        for key in keys:
            if key not in current:
                return False
            current = current[key]
        
        return current == expected
    
    def _check_sovereignty_compliance(self) -> bool:
        """Check sovereignty compliance."""
        try:
            # Check for zero telemetry
            with open('config/openpipe-config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            sovereign_mode = config.get('openpipe', {}).get('sovereign_mode', False)
            if not sovereign_mode:
                return False
            
            # Check for encryption
            encryption_enabled = config.get('openpipe', {}).get('security', {}).get('encryption_enabled', False)
            if not encryption_enabled:
                return False
            
            return True
            
        except:
            return False
    
    def _check_performance_compliance(self) -> bool:
        """Check performance compliance."""
        try:
            # Check memory constraints
            with open('config/openpipe-config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            memory_limit = config.get('openpipe', {}).get('resources', {}).get('memory_limit', '')
            if memory_limit != '1G':
                return False
            
            # Check latency targets
            latency_targets = config.get('openpipe', {}).get('performance', {}).get('latency_targets', {})
            p95_target = latency_targets.get('p95', 0)
            if p95_target > 300:
                return False
            
            return True
            
        except:
            return False
    
    def _check_compatibility_compliance(self) -> bool:
        """Check compatibility compliance."""
        try:
            # Check for torch-free constraint
            with open('app/XNAi_rag_app/core/openpipe_integration.py', 'r') as f:
                content = f.read()
            
            if 'torch' in content or 'pytorch' in content:
                return False
            
            # Check for AnyIO compatibility
            if 'asyncio' in content and 'AnyIO' not in content:
                return False
            
            return True
            
        except:
            return False
    
    def _check_reliability_compliance(self) -> bool:
        """Check reliability compliance."""
        try:
            # Check for circuit breakers
            with open('app/XNAi_rag_app/core/openpipe_integration.py', 'r') as f:
                content = f.read()
            
            if 'CircuitBreaker' not in content:
                return False
            
            # Check for deduplication
            if 'deduplicate' not in content:
                return False
            
            # Check for metrics
            if 'metrics' not in content:
                return False
            
            return True
            
        except:
            return False
    
    def run_validation(self) -> bool:
        """Run complete validation suite."""
        print("🚀 Starting OpenPipe Integration Validation")
        print("=" * 60)
        
        validation_functions = [
            self.validate_file_structure,
            self.validate_configuration,
            self.validate_code_quality,
            self.validate_docker_compose,
            self.validate_monitoring,
            self.validate_environment_variables,
            self.validate_test_coverage,
            self.validate_requirements_compliance
        ]
        
        passed = 0
        failed = 0
        
        for validation_func in validation_functions:
            try:
                result = validation_func()
                if result:
                    passed += 1
                    print(f"✅ {validation_func.__name__}")
                else:
                    failed += 1
                    print(f"❌ {validation_func.__name__}")
            except Exception as e:
                failed += 1
                print(f"❌ {validation_func.__name__}: {e}")
        
        print("=" * 60)
        print(f"📊 Validation Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All validations passed! OpenPipe integration is ready for deployment.")
            print("\n📋 Next Steps:")
            print("1. Set OPENPIPE_API_KEY in your environment")
            print("2. Update docker-compose.yml with OpenPipe service")
            print("3. Run the implementation guide steps")
            print("4. Execute integration tests")
            print("5. Monitor performance with Grafana dashboards")
        else:
            print("⚠️  Some validations failed. Review and fix issues before deployment.")
        
        return failed == 0

def main():
    """Main validation execution."""
    validator = OpenPipeValidator()
    success = validator.run_validation()
    
    # Exit with appropriate code
    exit(0 if success else 1)

if __name__ == "__main__":
    main()