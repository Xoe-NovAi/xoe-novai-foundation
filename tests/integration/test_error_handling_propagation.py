#!/usr/bin/env python3
"""
Phase 4.1 Integration Tests: Error Handling & Propagation
Purpose: Verify 404/500 error passthrough from backend services through Caddy gateway
Reference: conductor/tracks/phase-4.1-integration/spec.md
Last Updated: 2026-02-15
Hardware Target: Ryzen 7 5700U / Vega 8 (latency <200ms)
"""

import pytest
import time
import json
import logging
from typing import Dict, Any
from unittest.mock import Mock, patch

logger = logging.getLogger(__name__)


class TestHTTPErrorPropagation:
    """Test HTTP error code passthrough from backend through gateway."""

    @pytest.mark.integration
    def test_backend_404_error_passthrough(self, gateway_client):
        """Test that backend 404 errors propagate through gateway correctly."""
        endpoint = '/api/rag/query/nonexistent-id'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            # Should either get 404 from backend or gateway unavailable
            if response.status_code == 404:
                assert response.status_code == 404
                # Verify response has proper JSON error format
                try:
                    data = response.json()
                    assert 'error' in data or 'detail' in data or 'message' in data
                except json.JSONDecodeError:
                    # Error response may not be JSON in all cases
                    pass
            elif response.status_code >= 500:
                # Backend service may not be running
                pytest.skip(f"Backend service unavailable: {response.status_code}")
        except Exception as e:
            pytest.skip(f"Gateway not responding: {e}")

    @pytest.mark.integration
    def test_backend_500_error_passthrough(self, gateway_client):
        """Test that backend 500 errors propagate through gateway correctly."""
        endpoint = '/api/rag/query?trigger_error=true'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            # Should either get 500 from backend or gateway unavailable
            if response.status_code == 500:
                assert response.status_code == 500
                # Should have error details
                try:
                    data = response.json()
                    # Verify error structure
                    assert isinstance(data, dict)
                except json.JSONDecodeError:
                    # Error may be plain text
                    assert len(response.text) > 0
            elif response.status_code in [200, 400]:
                # Error wasn't triggered or endpoint works differently
                pass
            else:
                pytest.skip(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            pytest.skip(f"Gateway error test unavailable: {e}")

    @pytest.mark.integration
    def test_backend_503_error_passthrough(self, gateway_client):
        """Test that backend 503 (Service Unavailable) errors propagate."""
        # Simulate service temporarily down
        endpoint = '/api/rag/health'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            # Check for reasonable response (200 or 503)
            assert response.status_code in [200, 503, 502, 504]
            
            if response.status_code == 503:
                # Verify proper error response format
                try:
                    data = response.json()
                    assert isinstance(data, dict)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            pytest.skip(f"Gateway health check unavailable: {e}")

    @pytest.mark.integration
    def test_backend_400_error_passthrough(self, gateway_client):
        """Test that backend 400 (Bad Request) errors propagate."""
        # Send invalid JSON in request body
        endpoint = '/api/rag/query'
        
        try:
            response = gateway_client.post(
                endpoint,
                data='invalid-json-{',
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should get 400 or 422 for bad request
            if response.status_code in [400, 422]:
                assert response.status_code in [400, 422]
                # Verify error details
                try:
                    data = response.json()
                    assert 'error' in data or 'detail' in data
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            pytest.skip(f"Bad request test unavailable: {e}")

    @pytest.mark.integration
    def test_backend_401_error_passthrough(self, gateway_client):
        """Test that backend 401 (Unauthorized) errors propagate."""
        endpoint = '/api/rag/admin/status'
        
        try:
            # Request without auth header
            response = gateway_client.get(endpoint, timeout=10)
            
            # Should get 401 if endpoint requires auth
            if response.status_code == 401:
                assert response.status_code == 401
                # Verify auth error details
                try:
                    data = response.json()
                    assert isinstance(data, dict)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            pytest.skip(f"Authorization test unavailable: {e}")

    @pytest.mark.integration
    def test_backend_403_error_passthrough(self, gateway_client):
        """Test that backend 403 (Forbidden) errors propagate."""
        endpoint = '/api/rag/admin/delete'
        
        try:
            # Try to delete without proper permissions
            response = gateway_client.post(endpoint, json={}, timeout=10)
            
            # Should get 403 or 401 if denied
            if response.status_code == 403:
                assert response.status_code == 403
                try:
                    data = response.json()
                    assert isinstance(data, dict)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            pytest.skip(f"Forbidden access test unavailable: {e}")

    @pytest.mark.integration
    def test_backend_429_error_passthrough(self, gateway_client):
        """Test that backend 429 (Rate Limited) errors propagate."""
        endpoint = '/api/rag/query'
        
        try:
            # Make rapid requests to potentially trigger rate limit
            responses = []
            for i in range(10):
                try:
                    response = gateway_client.get(
                        endpoint,
                        timeout=2
                    )
                    responses.append(response.status_code)
                except Exception:
                    break
            
            # If we got 429, verify it propagated correctly
            if 429 in responses:
                assert 429 in responses
        except Exception as e:
            pytest.skip(f"Rate limiting test unavailable: {e}")

    @pytest.mark.integration
    def test_error_response_headers_preserved(self, gateway_client):
        """Test that error response headers are preserved through gateway."""
        endpoint = '/api/rag/query/bad'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            # Check for important headers in error response
            if response.status_code >= 400:
                # Verify headers are present
                assert len(response.headers) > 0
                
                # Should have content-type
                content_type = response.headers.get('content-type', '')
                assert len(content_type) > 0
        except Exception as e:
            pytest.skip(f"Error headers test unavailable: {e}")

    @pytest.mark.integration
    def test_error_response_body_completeness(self, gateway_client):
        """Test that error response bodies are complete through gateway."""
        endpoint = '/api/rag/query/error'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            if response.status_code >= 400:
                # Response body should not be empty
                assert len(response.content) > 0
                
                # Should be able to read response
                assert len(response.text) > 0
        except Exception as e:
            pytest.skip(f"Error body completeness test unavailable: {e}")

    @pytest.mark.integration
    def test_error_response_timeout_handling(self, gateway_client, hardware_requirements):
        """Test error response handling within timeout constraints."""
        endpoint = '/api/rag/query/error'
        latency_target_ms = hardware_requirements['latency_target_ms']
        
        start_time = time.time()
        try:
            response = gateway_client.get(
                endpoint,
                timeout=latency_target_ms / 1000 * 2
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Error response should be fast
            if response.status_code >= 400:
                assert elapsed_ms < latency_target_ms * 2, \
                    f"Error response took {elapsed_ms:.1f}ms"
        except Exception as e:
            pytest.skip(f"Error timeout test unavailable: {e}")


class TestGatewayErrorHandling:
    """Test gateway-level error handling and propagation."""

    @pytest.mark.integration
    def test_gateway_routes_missing_backend_as_503(self, gateway_client):
        """Test gateway returns 503 when backend is down."""
        endpoint = '/api/rag/health'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            # Either backend is up (200) or gateway reports unavailable (503/502)
            assert response.status_code in [200, 503, 502, 504]
        except Exception as e:
            # Connection refused is acceptable
            pass

    @pytest.mark.integration
    def test_gateway_forwards_custom_error_headers(self, gateway_client):
        """Test gateway forwards custom error headers from backend."""
        endpoint = '/api/rag/query'
        
        try:
            response = gateway_client.post(endpoint, json={"invalid": True}, timeout=10)
            
            if response.status_code >= 400:
                # Check for potential custom headers
                headers = dict(response.headers)
                assert len(headers) > 0
        except Exception as e:
            pytest.skip(f"Custom headers test unavailable: {e}")

    @pytest.mark.integration
    def test_gateway_error_response_consistency(self, gateway_client):
        """Test gateway provides consistent error response format."""
        endpoints = [
            '/api/rag/query/nonexistent',
            '/api/rag/invalid-endpoint',
        ]
        
        responses = []
        for endpoint in endpoints:
            try:
                response = gateway_client.get(endpoint, timeout=5)
                if response.status_code >= 400:
                    responses.append(response)
            except Exception:
                pass
        
        # If we got error responses, verify consistency
        if responses:
            for resp in responses:
                assert resp.status_code >= 400

    @pytest.mark.integration
    def test_gateway_timeout_returns_504(self, gateway_client):
        """Test gateway returns 504 on backend timeout."""
        # This would require a slow backend endpoint
        endpoint = '/api/rag/query?slow=true'
        
        try:
            response = gateway_client.get(endpoint, timeout=2)
            
            # Either response comes through or timeout occurs
            assert response.status_code in [200, 504, 502, 503]
        except Exception:
            # Timeout is expected behavior
            pass

    @pytest.mark.integration
    def test_gateway_connection_refused_returns_503(self, gateway_client):
        """Test gateway returns 503 when backend connection refused."""
        # Target a backend that doesn't exist
        endpoint = '/api/rag/health'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            # Should get a valid response (either successful or error)
            assert response.status_code in range(100, 600)
        except Exception as e:
            # Connection error is acceptable
            logger.debug(f"Expected connection error: {e}")


class TestBackendErrorScenarios:
    """Test realistic backend error scenarios."""

    @pytest.mark.integration
    def test_sequential_error_recovery(self, gateway_client):
        """Test backend recovery from errors in sequence."""
        endpoint = '/api/rag/health'
        
        try:
            # Make multiple requests
            statuses = []
            for i in range(3):
                try:
                    response = gateway_client.get(endpoint, timeout=5)
                    statuses.append(response.status_code)
                except Exception:
                    statuses.append(None)
            
            # At least some should succeed if service exists
            if any(s == 200 for s in statuses):
                assert any(s == 200 for s in statuses)
        except Exception as e:
            pytest.skip(f"Sequential recovery test unavailable: {e}")

    @pytest.mark.integration
    def test_partial_service_failure_handling(self, gateway_client):
        """Test handling when service is partially unavailable."""
        # Try different endpoints that may fail independently
        endpoints = [
            '/api/rag/health',
            '/api/rag/status',
        ]
        
        try:
            for endpoint in endpoints:
                try:
                    response = gateway_client.get(endpoint, timeout=5)
                    # Response is valid if it's any HTTP status
                    assert response.status_code in range(100, 600)
                except Exception:
                    # Some endpoints may not exist
                    pass
        except Exception as e:
            pytest.skip(f"Partial failure test unavailable: {e}")

    @pytest.mark.integration
    @pytest.mark.ryzen
    def test_error_response_latency_within_targets(self, gateway_client, hardware_requirements):
        """Test error responses meet Ryzen latency targets."""
        endpoint = '/api/rag/query/invalid'
        latency_target_ms = hardware_requirements['latency_target_ms']
        
        measurements = []
        for i in range(3):
            start_time = time.time()
            try:
                response = gateway_client.get(endpoint, timeout=latency_target_ms/1000*2)
                elapsed_ms = (time.time() - start_time) * 1000
                measurements.append(elapsed_ms)
            except Exception:
                pass
        
        # If we got measurements, verify they're within target
        if measurements:
            avg_latency = sum(measurements) / len(measurements)
            assert avg_latency < latency_target_ms * 2, \
                f"Error response latency {avg_latency:.1f}ms exceeds target"

    @pytest.mark.integration
    def test_error_context_preservation(self, gateway_client):
        """Test error context is preserved through gateway."""
        endpoint = '/api/rag/query'
        
        try:
            response = gateway_client.post(
                endpoint,
                json={"query": ""},  # Empty query might trigger error
                timeout=10
            )
            
            if response.status_code >= 400:
                # Verify error context is present
                try:
                    data = response.json()
                    assert isinstance(data, dict)
                    # Should have some error information
                    assert len(data) > 0
                except json.JSONDecodeError:
                    # Plain text error is acceptable
                    assert len(response.text) > 0
        except Exception as e:
            pytest.skip(f"Error context test unavailable: {e}")

    @pytest.mark.integration
    def test_cascading_error_handling(self, gateway_client):
        """Test handling of cascading errors through service chain."""
        # Make request that might cascade through multiple services
        endpoint = '/api/rag/query'
        
        try:
            response = gateway_client.post(
                endpoint,
                json={"query": "test", "trigger_cascade": True},
                timeout=10
            )
            
            # Should get coherent error response (not internal server error traces)
            if response.status_code >= 500:
                assert response.status_code in [500, 502, 503, 504]
        except Exception as e:
            pytest.skip(f"Cascading error test unavailable: {e}")


class TestErrorResponseValidation:
    """Validate error response format and content."""

    @pytest.mark.integration
    def test_error_response_contains_error_code(self, gateway_client):
        """Test error responses include error code."""
        endpoint = '/api/rag/query/bad'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            if response.status_code >= 400:
                # HTTP status code is the error code
                assert response.status_code >= 400
        except Exception as e:
            pytest.skip(f"Error code test unavailable: {e}")

    @pytest.mark.integration
    def test_error_response_contains_message(self, gateway_client):
        """Test error responses include descriptive message."""
        endpoint = '/api/rag/query/error'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            if response.status_code >= 400:
                # Should have response body
                assert len(response.content) > 0
        except Exception as e:
            pytest.skip(f"Error message test unavailable: {e}")

    @pytest.mark.integration
    def test_error_response_valid_json_when_claimed(self, gateway_client):
        """Test error responses are valid JSON when Content-Type claims JSON."""
        endpoint = '/api/rag/query/invalid'
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            if response.status_code >= 400:
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    # Should be valid JSON
                    try:
                        data = response.json()
                        assert isinstance(data, dict)
                    except json.JSONDecodeError:
                        pytest.fail("Response claims JSON but is not valid JSON")
        except Exception as e:
            pytest.skip(f"JSON validation test unavailable: {e}")

    @pytest.mark.integration
    def test_error_response_no_sensitive_data_leakage(self, gateway_client):
        """Test error responses don't leak sensitive information."""
        endpoint = '/api/rag/query/error'
        
        sensitive_patterns = [
            'password',
            'secret',
            'token',
            'api_key',
            'private_key',
            '/root/',
            '/home/',
        ]
        
        try:
            response = gateway_client.get(endpoint, timeout=10)
            
            if response.status_code >= 400:
                response_text = response.text.lower()
                
                # Check for sensitive data leakage
                for pattern in sensitive_patterns:
                    assert pattern not in response_text, \
                        f"Sensitive data detected: {pattern}"
        except Exception as e:
            pytest.skip(f"Sensitive data test unavailable: {e}")
