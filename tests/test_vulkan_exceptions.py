"""
Vulkan Acceleration Exception Tests
==================================
Verifies Vulkan exception hierarchy.
"""

import pytest
import sys
import os
from pathlib import Path

# Add app root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from XNAi_rag_app.core.vulkan_acceleration import (
    VulkanAccelerationError,
    VulkanInitializationError,
    VulkanOperationError,
)
from XNAi_rag_app.schemas.errors import ErrorCategory


class TestVulkanAccelerationError:
    """Test VulkanAccelerationError base class."""
    
    def test_vulkan_error_creation(self):
        """Test creating a VulkanAccelerationError."""
        exc = VulkanAccelerationError(
            message="Vulkan acceleration failed"
        )
        assert exc.message == "Vulkan acceleration failed"
        assert exc.category == ErrorCategory.VULKAN_ACCELERATION
        assert exc.http_status == 500
        assert "cpu" in exc.recovery_suggestion.lower() or "disable" in exc.recovery_suggestion.lower()
    
    def test_vulkan_error_with_details(self):
        """Test VulkanAccelerationError with details."""
        details = {"device": "GPU0"}
        exc = VulkanAccelerationError(
            message="Error",
            details=details
        )
        assert exc.details["device"] == "GPU0"
    
    def test_vulkan_error_with_cause(self):
        """Test VulkanAccelerationError with underlying cause."""
        original = RuntimeError("GPU error")
        exc = VulkanAccelerationError(
            message="Vulkan error",
            cause=original
        )
        assert exc.__cause__ is original


class TestVulkanInitializationError:
    """Test VulkanInitializationError."""
    
    def test_initialization_error_creation(self):
        """Test creating a VulkanInitializationError."""
        exc = VulkanInitializationError(
            message="Vulkan initialization failed",
            device_info={"driver_version": "unknown"}
        )
        assert exc.message == "Vulkan initialization failed"
        assert exc.details["device_info"]["driver_version"] == "unknown"
        assert exc.category == ErrorCategory.VULKAN_ACCELERATION
    
    def test_initialization_error_recovery(self):
        """Test VulkanInitializationError recovery suggestion."""
        exc = VulkanInitializationError(
            message="No Vulkan drivers"
        )
        assert "driver" in exc.recovery_suggestion.lower()
        assert "vulkan" in exc.recovery_suggestion.lower()
    
    def test_initialization_error_inheritance(self):
        """Test VulkanInitializationError inherits from VulkanAccelerationError."""
        exc = VulkanInitializationError(message="Test")
        assert isinstance(exc, VulkanAccelerationError)


class TestVulkanOperationError:
    """Test VulkanOperationError."""
    
    def test_operation_error_creation(self):
        """Test creating a VulkanOperationError."""
        exc = VulkanOperationError(
            message="Compute operation failed",
            operation_name="matrix_multiply"
        )
        assert exc.message == "Compute operation failed"
        assert exc.details["operation_name"] == "matrix_multiply"
    
    def test_operation_error_without_operation_name(self):
        """Test VulkanOperationError without operation name."""
        exc = VulkanOperationError(
            message="Operation failed"
        )
        assert "operation_name" not in exc.details
    
    def test_operation_error_recovery(self):
        """Test VulkanOperationError recovery suggestion."""
        exc = VulkanOperationError(
            message="Operation failed"
        )
        assert "cpu" in exc.recovery_suggestion.lower() or "fallback" in exc.recovery_suggestion.lower()
    
    def test_operation_error_inheritance(self):
        """Test VulkanOperationError inherits from VulkanAccelerationError."""
        exc = VulkanOperationError(message="Test", operation_name="test_op")
        assert isinstance(exc, VulkanAccelerationError)


class TestVulkanErrorInheritance:
    """Test Vulkan error inheritance chain."""
    
    def test_initialization_is_vulkan_error(self):
        """Test VulkanInitializationError is VulkanAccelerationError."""
        exc = VulkanInitializationError(message="Test")
        assert isinstance(exc, VulkanAccelerationError)
    
    def test_operation_is_vulkan_error(self):
        """Test VulkanOperationError is VulkanAccelerationError."""
        exc = VulkanOperationError(message="Test")
        assert isinstance(exc, VulkanAccelerationError)
    
    def test_vulkan_errors_are_xnai_exceptions(self):
        """Test all Vulkan errors are XNAiException."""
        from XNAi_rag_app.api.exceptions import XNAiException
        
        errors = [
            VulkanAccelerationError(message="Test"),
            VulkanInitializationError(message="Test"),
            VulkanOperationError(message="Test"),
        ]
        
        for exc in errors:
            assert isinstance(exc, XNAiException), f"{exc.__class__.__name__} not an XNAiException"


class TestVulkanErrorCategory:
    """Test Vulkan error category mapping."""
    
    def test_all_vulkan_errors_have_correct_category(self):
        """Test all Vulkan errors map to VULKAN_ACCELERATION category."""
        errors = [
            VulkanAccelerationError(message="Test"),
            VulkanInitializationError(message="Test"),
            VulkanOperationError(message="Test"),
        ]
        
        for exc in errors:
            assert exc.category == ErrorCategory.VULKAN_ACCELERATION, \
                f"{exc.__class__.__name__} has wrong category: {exc.category}"
            assert exc.http_status == 500, \
                f"{exc.__class__.__name__} should return HTTP 500"
