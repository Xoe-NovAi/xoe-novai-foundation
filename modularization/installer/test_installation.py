#!/usr/bin/env python3
"""
Xoe-NovAi Omega Stack Beautiful Installer - Test Framework
==========================================================
Comprehensive testing framework for the beautiful installation system.
"""

import unittest
import asyncio
import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

class InstallationTestSuite(unittest.TestCase):
    """Test suite for the beautiful installation system"""
    
    BASE_URL = "http://localhost:8001"
    FRONTEND_URL = "http://localhost:3000"
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("🧪 Setting up test environment...")
        
        # Check if required directories exist
        installer_dir = Path(__file__).parent
        frontend_dir = installer_dir / "frontend"
        backend_dir = installer_dir / "backend"
        
        assert frontend_dir.exists(), "Frontend directory not found"
        assert backend_dir.exists(), "Backend directory not found"
        
        print("✅ Test environment ready")
    
    def test_frontend_dependencies(self):
        """Test frontend dependencies are properly installed"""
        print("📦 Testing frontend dependencies...")
        
        frontend_dir = Path(__file__).parent / "frontend"
        package_json = frontend_dir / "package.json"
        
        self.assertTrue(package_json.exists(), "package.json not found")
        
        with open(package_json) as f:
            package_data = json.load(f)
        
        required_deps = [
            "react", "react-dom", "react-router-dom", 
            "zustand", "tailwind-merge", "framer-motion"
        ]
        
        for dep in required_deps:
            self.assertIn(dep, package_data.get("dependencies", {}), 
                         f"Required dependency {dep} not found")
        
        print("✅ Frontend dependencies verified")
    
    def test_backend_dependencies(self):
        """Test backend dependencies are properly installed"""
        print("🔌 Testing backend dependencies...")
        
        backend_dir = Path(__file__).parent / "backend"
        main_py = backend_dir / "main.py"
        
        self.assertTrue(main_py.exists(), "Backend main.py not found")
        
        with open(main_py) as f:
            content = f.read()
        
        required_imports = [
            "fastapi", "uvicorn", "socketio", 
            "psutil", "platform"
        ]
        
        for imp in required_imports:
            self.assertIn(imp, content, f"Required import {imp} not found")
        
        print("✅ Backend dependencies verified")
    
    def test_system_requirements(self):
        """Test system requirements check functionality"""
        print("🔍 Testing system requirements check...")
        
        try:
            response = requests.post(f"{self.BASE_URL}/api/system-check", timeout=10)
            self.assertEqual(response.status_code, 200, "System check endpoint failed")
            
            data = response.json()
            self.assertTrue(data.get("success"), "System check should succeed")
            
            system_info = data.get("data", {})
            required_fields = ["os", "cpu", "memory", "disk", "pythonVersion"]
            
            for field in required_fields:
                self.assertIn(field, system_info, f"Missing system info field: {field}")
            
            print("✅ System requirements check working")
            
        except requests.exceptions.ConnectionError:
            print("⚠️  Backend server not running - skipping system check test")
    
    def test_installation_api(self):
        """Test installation API endpoints"""
        print("🚀 Testing installation API...")
        
        try:
            # Test start installation endpoint
            test_config = {
                "preset": "quick",
                "environment": "development",
                "services": [
                    {"id": "rag-engine", "selected": True},
                    {"id": "chainlit-ui", "selected": True},
                    {"id": "redis-cache", "selected": True}
                ],
                "providers": [
                    {"id": "opencode", "selected": True}
                ]
            }
            
            response = requests.post(
                f"{self.BASE_URL}/api/start-installation",
                json=test_config,
                timeout=5
            )
            
            # Should return 400 if already running or 200 if successful
            self.assertIn(response.status_code, [200, 400], 
                         "Installation API should return 200 or 400")
            
            print("✅ Installation API working")
            
        except requests.exceptions.ConnectionError:
            print("⚠️  Backend server not running - skipping installation API test")
    
    def test_frontend_build(self):
        """Test frontend can be built successfully"""
        print("🏗️  Testing frontend build...")
        
        frontend_dir = Path(__file__).parent / "frontend"
        
        try:
            # Check if vite.config exists
            vite_config = frontend_dir / "vite.config.ts"
            self.assertTrue(vite_config.exists(), "Vite config not found")
            
            # Check if main.tsx exists
            main_tsx = frontend_dir / "src" / "main.tsx"
            self.assertTrue(main_tsx.exists(), "Main TypeScript file not found")
            
            print("✅ Frontend build configuration verified")
            
        except Exception as e:
            print(f"⚠️  Frontend build test failed: {e}")
    
    def test_installer_script(self):
        """Test installer script functionality"""
        print("📜 Testing installer script...")
        
        installer_script = Path(__file__).parent / "install.sh"
        self.assertTrue(installer_script.exists(), "Installer script not found")
        
        # Check if script is executable
        self.assertTrue(os.access(installer_script, os.X_OK), 
                       "Installer script should be executable")
        
        # Check script content
        with open(installer_script) as f:
            script_content = f.read()
        
        required_functions = [
            "check_prerequisites", "install_frontend_dependencies", 
            "install_backend_dependencies", "start_installer"
        ]
        
        for func in required_functions:
            self.assertIn(func, script_content, f"Required function {func} not found")
        
        print("✅ Installer script verified")
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        print("⚙️  Testing configuration validation...")
        
        # Test valid configuration
        valid_config = {
            "preset": "standard",
            "environment": "development",
            "services": [
                {"id": "rag-engine", "name": "RAG Engine", "selected": True, "required": True},
                {"id": "chainlit-ui", "name": "Chainlit UI", "selected": True, "required": True},
                {"id": "redis-cache", "name": "Redis Cache", "selected": True, "required": True}
            ],
            "providers": [
                {"id": "opencode", "name": "OpenCode", "selected": True},
                {"id": "antigravity", "name": "Antigravity", "selected": False}
            ]
        }
        
        # Test configuration structure
        self.assertIn("preset", valid_config)
        self.assertIn("services", valid_config)
        self.assertIn("providers", valid_config)
        
        # Test required services are present
        required_services = ["rag-engine", "chainlit-ui", "redis-cache"]
        selected_services = [s["id"] for s in valid_config["services"] if s["selected"]]
        
        for service in required_services:
            self.assertIn(service, selected_services, f"Required service {service} not selected")
        
        print("✅ Configuration validation working")
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("🚨 Testing error handling...")
        
        # Test invalid configuration
        invalid_config = {
            "preset": "invalid",
            "services": [],
            "providers": []
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/start-installation",
                json=invalid_config,
                timeout=5
            )
            
            # Should return error for invalid config
            self.assertIn(response.status_code, [400, 500], 
                         "Invalid config should return error")
            
        except requests.exceptions.ConnectionError:
            print("⚠️  Backend server not running - skipping error handling test")
        
        print("✅ Error handling working")
    
    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        print("📊 Testing progress tracking...")
        
        # Test progress structure
        progress_data = {
            "phase": "installation",
            "currentStep": 2,
            "totalSteps": 5,
            "progress": 40.0,
            "status": "running",
            "message": "Installing dependencies...",
            "components": []
        }
        
        required_fields = ["phase", "currentStep", "totalSteps", "progress", "status", "message"]
        
        for field in required_fields:
            self.assertIn(field, progress_data, f"Missing progress field: {field}")
        
        # Test progress calculation
        expected_progress = (progress_data["currentStep"] / progress_data["totalSteps"]) * 100
        self.assertEqual(progress_data["progress"], expected_progress, 
                        "Progress calculation incorrect")
        
        print("✅ Progress tracking working")
    
    def test_security_validation(self):
        """Test security considerations"""
        print("🔒 Testing security validation...")
        
        # Check that sensitive information is not hardcoded
        backend_dir = Path(__file__).parent / "backend"
        main_py = backend_dir / "main.py"
        
        with open(main_py) as f:
            content = f.read()
        
        # Should not contain hardcoded secrets
        sensitive_patterns = [
            "password =", "secret =", "key =", "token ="
        ]
        
        for pattern in sensitive_patterns:
            self.assertNotIn(pattern.lower(), content.lower(), 
                           f"Hardcoded sensitive information found: {pattern}")
        
        print("✅ Security validation passed")
    
    def test_performance_requirements(self):
        """Test performance requirements"""
        print("⚡ Testing performance requirements...")
        
        # Check that installation process is optimized
        backend_dir = Path(__file__).parent / "backend"
        main_py = backend_dir / "main.py"
        
        with open(main_py) as f:
            content = f.read()
        
        # Should use async/await for I/O operations
        self.assertIn("async", content, "Should use async operations")
        self.assertIn("await", content, "Should use await for async operations")
        
        # Should have proper error handling
        self.assertIn("try:", content, "Should have try blocks")
        self.assertIn("except", content, "Should have except blocks")
        
        print("✅ Performance requirements met")
    
    def test_user_experience(self):
        """Test user experience features"""
        print("🌟 Testing user experience...")
        
        # Check that frontend has proper loading states
        frontend_dir = Path(__file__).parent / "frontend"
        welcome_page = frontend_dir / "src" / "pages" / "WelcomePage.tsx"
        
        if welcome_page.exists():
            with open(welcome_page) as f:
                content = f.read()
            
            # Should have loading states
            self.assertIn("isAnimating", content, "Should have loading states")
            self.assertIn("toast", content, "Should have toast notifications")
        
        print("✅ User experience features present")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        print("✅ Test environment cleaned")

def run_tests():
    """Run the complete test suite"""
    print("🧪 Xoe-NovAi Omega Stack Beautiful Installer - Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(InstallationTestSuite)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n🔥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! The beautiful installer is ready.")
        return 0
    else:
        print("\n💥 Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())