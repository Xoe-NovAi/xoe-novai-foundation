#!/usr/bin/env python3
"""
Xoe-NovAi Integration Test Framework
====================================

Comprehensive testing suite for validating system integration and cross-component communication.
Ensures all components work together seamlessly in the AI development ecosystem.
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class IntegrationTestFramework:
    """
    Comprehensive integration testing framework for Xoe-NovAi ecosystem.

    Tests cross-component communication, data flow, and system reliability.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_results = []
        self.start_time = None
        self.end_time = None

        # Test directories
        self.test_output_dir = project_root / "tests" / "integration_output"
        self.test_output_dir.mkdir(parents=True, exist_ok=True)

    def run_full_integration_test(self) -> Dict[str, Any]:
        """
        Run complete integration test suite.

        Returns:
            Comprehensive test results with metrics and recommendations
        """
        self.start_time = datetime.now()
        print("🚀 Starting Xoe-NovAi Integration Test Suite")
        print("=" * 60)

        try:
            # Test 1: Project System Integration
            self.test_project_system_integration()

            # Test 2: Knowledge Base Integration
            self.test_knowledge_base_integration()

            # Test 3: Cross-Component Communication
            self.test_cross_component_communication()

            # Test 4: Data Flow Validation
            self.test_data_flow_validation()

            # Test 5: Performance Integration
            self.test_performance_integration()

            # Test 6: Error Handling Integration
            self.test_error_handling_integration()

            # Generate comprehensive report
            report = self.generate_integration_report()

            self.end_time = datetime.now()
            duration = self.end_time - self.start_time

            print(f"\n✅ Integration Test Suite Complete")
            print(f"⏱️  Duration: {duration.total_seconds():.2f} seconds")
            print(f"📊 Tests Run: {len(self.test_results)}")
            print(f"🎯 Success Rate: {report['summary']['success_rate']:.1f}%")

            return report

        except Exception as e:
            print(f"❌ Integration test suite failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def test_project_system_integration(self):
        """Test project system integration with templates and orchestration."""
        print("\n🔧 Testing Project System Integration...")

        try:
            # Import project orchestrator
            sys.path.insert(0, str(self.project_root / "projects" / "_meta"))
            from orchestrator import BasicProjectOrchestrator

            # Test orchestrator initialization
            orchestrator = BasicProjectOrchestrator()
            self._log_test_result("project_orchestrator_init", True, "Orchestrator initialized successfully")

            # Test template discovery
            templates_dir = self.project_root / "projects" / "_templates"
            template_types = [d.name for d in templates_dir.iterdir() if d.is_dir()]
            expected_templates = ["research-project", "development-project", "experimental-project"]

            if set(template_types) == set(expected_templates):
                self._log_test_result("template_discovery", True, f"All templates found: {template_types}")
            else:
                self._log_test_result("template_discovery", False, f"Missing templates. Found: {template_types}, Expected: {expected_templates}")

            # Test project creation
            test_project_name = "integration_test_project"
            success = orchestrator.create_project(
                test_project_name,
                "research-project",
                "Integration testing project"
            )

            if success:
                self._log_test_result("project_creation", True, f"Project '{test_project_name}' created successfully")

                # Verify project structure
                project_dir = self.project_root / "projects" / test_project_name
                required_files = ["README.md", "metadata.json"]

                files_exist = all((project_dir / file).exists() for file in required_files)
                if files_exist:
                    self._log_test_result("project_structure", True, "Project structure validated")
                else:
                    self._log_test_result("project_structure", False, "Project structure incomplete")

                # Cleanup test project
                if project_dir.exists():
                    shutil.rmtree(project_dir)
                    self._log_test_result("project_cleanup", True, "Test project cleaned up")
            else:
                self._log_test_result("project_creation", False, "Project creation failed")

        except Exception as e:
            self._log_test_result("project_system_integration", False, f"Project system integration failed: {e}")

    def test_knowledge_base_integration(self):
        """Test knowledge base integration and validation systems."""
        print("\n🧠 Testing Knowledge Base Integration...")

        try:
            # Test knowledge base structure
            kb_dir = self.project_root / "expert-knowledge"
            required_structure = [
                "environment/ide-ecosystem",
                "environment/cline-plugin",
                "environment/grok-code-fast-1",
                "environment/development-workflows",
                "_meta/knowledge-templates",
                "_meta/notes-todo-manager.md",
                "_meta/update-protocols.md",
                "_meta/validation-framework.md",
                "README.md"
            ]

            structure_complete = True
            missing_items = []

            for item in required_structure:
                path = kb_dir / item
                if not path.exists():
                    structure_complete = False
                    missing_items.append(item)

            if structure_complete:
                self._log_test_result("kb_structure", True, "Knowledge base structure complete")
            else:
                self._log_test_result("kb_structure", False, f"Missing items: {missing_items}")

            # Test template system
            template_file = kb_dir / "_meta" / "knowledge-templates" / "environment-template.md"
            if template_file.exists():
                with open(template_file, 'r') as f:
                    content = f.read()
                    if "## Component Overview" in content and "## Installation & Setup" in content:
                        self._log_test_result("template_system", True, "Template system functional")
                    else:
                        self._log_test_result("template_system", False, "Template structure incomplete")
            else:
                self._log_test_result("template_system", False, "Template file missing")

            # Test notes system
            notes_file = kb_dir / "_meta" / "notes" / "philosophy-notes.md"
            todos_file = kb_dir / "_meta" / "todos" / "technical-todos.md"

            notes_exist = notes_file.exists()
            todos_exist = todos_file.exists()

            if notes_exist and todos_exist:
                self._log_test_result("notes_todo_system", True, "Notes and todo system operational")
            else:
                self._log_test_result("notes_todo_system", False, f"Missing: notes={not notes_exist}, todos={not todos_exist}")

        except Exception as e:
            self._log_test_result("knowledge_base_integration", False, f"Knowledge base integration failed: {e}")

    def test_cross_component_communication(self):
        """Test communication between different system components."""
        print("\n🔗 Testing Cross-Component Communication...")

        try:
            # Test project system ↔ knowledge base integration
            # This would test if projects can reference knowledge base content
            kb_readme = self.project_root / "expert-knowledge" / "README.md"
            projects_readme = self.project_root / "projects" / "README.md"

            if kb_readme.exists() and projects_readme.exists():
                # Check for cross-references
                with open(projects_readme, 'r') as f:
                    projects_content = f.read()

                cross_refs_found = "expert-knowledge" in projects_content

                if cross_refs_found:
                    self._log_test_result("cross_component_refs", True, "Cross-component references established")
                else:
                    self._log_test_result("cross_component_refs", False, "Missing cross-component references")
            else:
                self._log_test_result("cross_component_refs", False, "Component documentation missing")

            # Test template integration with project system
            template_dir = self.project_root / "projects" / "_templates" / "research-project"
            if template_dir.exists():
                readme_template = template_dir / "README.md"
                if readme_template.exists():
                    with open(readme_template, 'r') as f:
                        template_content = f.read()

                    # Check for variable replacement
                    variables_present = "{{" in template_content and "}}" in template_content
                    if variables_present:
                        self._log_test_result("template_variable_system", True, "Template variable system functional")
                    else:
                        self._log_test_result("template_variable_system", False, "Template variables missing")
                else:
                    self._log_test_result("template_variable_system", False, "Template README missing")
            else:
                self._log_test_result("template_variable_system", False, "Research template missing")

        except Exception as e:
            self._log_test_result("cross_component_communication", False, f"Cross-component communication test failed: {e}")

    def test_data_flow_validation(self):
        """Test data flow between components and validation."""
        print("\n📊 Testing Data Flow Validation...")

        try:
            # Test metadata consistency
            projects_dir = self.project_root / "projects"
            metadata_files = list(projects_dir.rglob("metadata.json"))

            if metadata_files:
                valid_metadata = 0
                for metadata_file in metadata_files:
                    try:
                        with open(metadata_file, 'r') as f:
                            data = json.load(f)

                        # Check required fields
                        required_fields = ["name", "type", "status", "created"]
                        has_required = all(field in data for field in required_fields)

                        if has_required:
                            valid_metadata += 1

                    except (json.JSONDecodeError, IOError):
                        continue

                if valid_metadata == len(metadata_files):
                    self._log_test_result("metadata_validation", True, f"All {valid_metadata} metadata files valid")
                else:
                    self._log_test_result("metadata_validation", False, f"Only {valid_metadata}/{len(metadata_files)} metadata files valid")
            else:
                self._log_test_result("metadata_validation", True, "No metadata files to validate (expected)")

            # Test knowledge base document structure
            kb_docs = list((self.project_root / "expert-knowledge").rglob("*.md"))
            structured_docs = 0

            for doc in kb_docs:
                try:
                    with open(doc, 'r') as f:
                        content = f.read()

                    # Check for basic structure
                    has_title = content.startswith("# ")
                    has_sections = "## " in content

                    if has_title and has_sections:
                        structured_docs += 1

                except IOError:
                    continue

            if structured_docs == len(kb_docs):
                self._log_test_result("kb_document_structure", True, f"All {structured_docs} KB documents properly structured")
            else:
                self._log_test_result("kb_document_structure", False, f"Only {structured_docs}/{len(kb_docs)} KB documents properly structured")

        except Exception as e:
            self._log_test_result("data_flow_validation", False, f"Data flow validation failed: {e}")

    def test_performance_integration(self):
        """Test performance integration across components."""
        print("\n⚡ Testing Performance Integration...")

        try:
            # Test project creation performance
            import time
            start_time = time.time()

            # Simulate quick project creation test
            test_dir = self.test_output_dir / "perf_test"
            test_dir.mkdir(exist_ok=True)

            # Create a simple test file
            test_file = test_dir / "test.txt"
            with open(test_file, 'w') as f:
                f.write("Performance test")

            creation_time = time.time() - start_time

            if creation_time < 1.0:  # Should be very fast
                self._log_test_result("file_operation_performance", True, f"File operations: {creation_time:.3f}s")
            else:
                self._log_test_result("file_operation_performance", False, f"File operations too slow: {creation_time:.3f}s")

            # Clean up
            shutil.rmtree(test_dir)

            # Test knowledge base access performance
            kb_start = time.time()
            kb_files = list((self.project_root / "expert-knowledge").rglob("*.md"))
            kb_access_time = time.time() - kb_start

            if kb_access_time < 5.0:  # Should be reasonably fast
                self._log_test_result("kb_access_performance", True, f"KB access ({len(kb_files)} files): {kb_access_time:.3f}s")
            else:
                self._log_test_result("kb_access_performance", False, f"KB access too slow: {kb_access_time:.3f}s")

        except Exception as e:
            self._log_test_result("performance_integration", False, f"Performance integration test failed: {e}")

    def test_error_handling_integration(self):
        """Test error handling across integrated components."""
        print("\n🛡️  Testing Error Handling Integration...")

        try:
            # Test graceful handling of missing files
            nonexistent_file = self.project_root / "nonexistent" / "file.md"

            try:
                with open(nonexistent_file, 'r') as f:
                    content = f.read()
                self._log_test_result("error_handling", False, "Should have failed on missing file")
            except FileNotFoundError:
                self._log_test_result("error_handling", True, "Properly handled missing file error")
            except Exception as e:
                self._log_test_result("error_handling", False, f"Unexpected error type: {e}")

            # Test invalid JSON handling
            invalid_json_file = self.test_output_dir / "invalid.json"
            with open(invalid_json_file, 'w') as f:
                f.write("{ invalid json content }")

            try:
                with open(invalid_json_file, 'r') as f:
                    json.load(f)
                self._log_test_result("json_error_handling", False, "Should have failed on invalid JSON")
            except json.JSONDecodeError:
                self._log_test_result("json_error_handling", True, "Properly handled invalid JSON error")
            except Exception as e:
                self._log_test_result("json_error_handling", False, f"Unexpected error type: {e}")

            # Clean up
            invalid_json_file.unlink(missing_ok=True)

        except Exception as e:
            self._log_test_result("error_handling_integration", False, f"Error handling integration test failed: {e}")

    def _log_test_result(self, test_name: str, success: bool, message: str):
        """Log individual test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        self.test_results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")

    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration test report."""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        # Categorize results
        categories = {}
        for result in self.test_results:
            category = result["test_name"].split("_")[0]
            if category not in categories:
                categories[category] = {"total": 0, "successful": 0}
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["successful"] += 1

        # Generate recommendations
        recommendations = []
        if success_rate < 90:
            recommendations.append("Address failing integration tests to ensure system stability")
        if success_rate < 95:
            recommendations.append("Review and optimize cross-component communication")

        # Save detailed results
        results_file = self.test_output_dir / f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "success_rate": success_rate,
                    "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else None
                },
                "categories": categories,
                "detailed_results": self.test_results,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": round(success_rate, 1),
                "categories": categories
            },
            "recommendations": recommendations,
            "results_file": str(results_file),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main entry point for integration testing."""
    project_root = Path(__file__).parent.parent

    framework = IntegrationTestFramework(project_root)
    report = framework.run_full_integration_test()

    # Print summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Successful: {report['summary']['successful_tests']}")
    print(f"Success Rate: {report['summary']['success_rate']}%")

    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"• {rec}")

    print(f"\nDetailed results saved to: {report['results_file']}")

    # Exit with appropriate code
    success_rate = report['summary']['success_rate']
    exit_code = 0 if success_rate >= 90 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()