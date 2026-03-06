"""
AWQ Quantizer Exception Tests
============================
Verifies AWQ exception hierarchy (experimental/optional feature).
"""

import pytest
import sys
import os
from pathlib import Path

# Add app root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from XNAi_rag_app.core.awq_quantizer import (
    AWQQuantizationError,
    CalibrationError,
    QuantizationError,
    PrecisionSwitchError,
)
from XNAi_rag_app.schemas.errors import ErrorCategory


class TestAWQQuantizationError:
    """Test AWQQuantizationError base class."""
    
    def test_awq_error_creation(self):
        """Test creating an AWQQuantizationError."""
        exc = AWQQuantizationError(
            message="AWQ quantization failed"
        )
        assert exc.message == "AWQ quantization failed"
        assert exc.category == ErrorCategory.AWQ_QUANTIZATION
        assert exc.http_status == 500
        assert "experimental" in exc.recovery_suggestion.lower() or "AWQ" in exc.recovery_suggestion
    
    def test_awq_error_with_details(self):
        """Test AWQQuantizationError with details."""
        details = {"error_type": "calibration"}
        exc = AWQQuantizationError(
            message="Error",
            details=details
        )
        assert exc.details["error_type"] == "calibration"
    
    def test_awq_error_with_cause(self):
        """Test AWQQuantizationError with underlying cause."""
        original = ValueError("Bad value")
        exc = AWQQuantizationError(
            message="AWQ error",
            cause=original
        )
        assert exc.__cause__ is original


class TestCalibrationError:
    """Test CalibrationError."""
    
    def test_calibration_error_creation(self):
        """Test creating a CalibrationError."""
        exc = CalibrationError(
            message="Calibration failed",
            samples_count=50
        )
        assert exc.message == "Calibration failed"
        assert exc.details.get("samples_count") == 50
        assert exc.category == ErrorCategory.AWQ_QUANTIZATION
    
    def test_calibration_error_recovery(self):
        """Test CalibrationError recovery suggestion."""
        exc = CalibrationError(
            message="Insufficient data",
            samples_count=10
        )
        assert "calibration data" in exc.recovery_suggestion.lower()
    
    def test_calibration_error_inheritance(self):
        """Test CalibrationError inherits from AWQQuantizationError."""
        exc = CalibrationError(message="Test")
        assert isinstance(exc, AWQQuantizationError)


class TestQuantizationError:
    """Test QuantizationError."""
    
    def test_quantization_error_creation(self):
        """Test creating a QuantizationError."""
        exc = QuantizationError(
            message="Weight quantization failed",
            layer_index=5
        )
        assert exc.message == "Weight quantization failed"
        assert exc.details.get("layer_index") == 5
    
    def test_quantization_error_without_layer(self):
        """Test QuantizationError without layer index."""
        exc = QuantizationError(
            message="Quantization failed"
        )
        assert "layer_index" not in exc.details
    
    def test_quantization_error_inheritance(self):
        """Test QuantizationError inherits from AWQQuantizationError."""
        exc = QuantizationError(message="Test", layer_index=1)
        assert isinstance(exc, AWQQuantizationError)


class TestPrecisionSwitchError:
    """Test PrecisionSwitchError."""
    
    def test_precision_switch_error_creation(self):
        """Test creating a PrecisionSwitchError."""
        exc = PrecisionSwitchError(
            message="Precision switch failed",
            from_precision="FP32",
            to_precision="INT8"
        )
        assert exc.message == "Precision switch failed"
        assert exc.details["from_precision"] == "FP32"
        assert exc.details["to_precision"] == "INT8"
    
    def test_precision_switch_error_partial(self):
        """Test PrecisionSwitchError with partial precision info."""
        exc = PrecisionSwitchError(
            message="Switch failed",
            to_precision="INT8"
        )
        assert "from_precision" not in exc.details
        assert exc.details["to_precision"] == "INT8"
    
    def test_precision_switch_error_recovery(self):
        """Test PrecisionSwitchError recovery suggestion."""
        exc = PrecisionSwitchError(
            message="Switch failed"
        )
        assert "precision" in exc.recovery_suggestion.lower()
    
    def test_precision_switch_error_inheritance(self):
        """Test PrecisionSwitchError inherits from AWQQuantizationError."""
        exc = PrecisionSwitchError(message="Test")
        assert isinstance(exc, AWQQuantizationError)


class TestAWQErrorInheritance:
    """Test AWQ error inheritance chain."""
    
    def test_calibration_is_awq_error(self):
        """Test CalibrationError is AWQQuantizationError."""
        exc = CalibrationError(message="Test")
        assert isinstance(exc, AWQQuantizationError)
    
    def test_quantization_is_awq_error(self):
        """Test QuantizationError is AWQQuantizationError."""
        exc = QuantizationError(message="Test")
        assert isinstance(exc, AWQQuantizationError)
    
    def test_precision_switch_is_awq_error(self):
        """Test PrecisionSwitchError is AWQQuantizationError."""
        exc = PrecisionSwitchError(message="Test")
        assert isinstance(exc, AWQQuantizationError)
    
    def test_awq_errors_are_xnai_exceptions(self):
        """Test all AWQ errors are XNAiException."""
        from XNAi_rag_app.api.exceptions import XNAiException
        
        errors = [
            AWQQuantizationError(message="Test"),
            CalibrationError(message="Test"),
            QuantizationError(message="Test"),
            PrecisionSwitchError(message="Test"),
        ]
        
        for exc in errors:
            assert isinstance(exc, XNAiException), f"{exc.__class__.__name__} not an XNAiException"


class TestAWQExperimentalMarking:
    """Test that AWQ errors properly indicate experimental status."""
    
    def test_awq_all_mention_experimental_or_bow_out(self):
        """Test AWQ errors mention they are experimental."""
        errors = [
            AWQQuantizationError(message="Test"),
            CalibrationError(message="Test"),
            QuantizationError(message="Test"),
            PrecisionSwitchError(message="Test"),
        ]
        
        for exc in errors:
            # Either recovery mentions disabling AWQ or it's clear it's optional
            recovery = exc.recovery_suggestion.lower()
            assert ("awq" in recovery or "disable" in recovery or "experimental" in recovery), \
                f"{exc.__class__.__name__} doesn't clearly indicate it's experimental/optional"
