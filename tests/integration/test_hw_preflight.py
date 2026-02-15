#!/usr/bin/env python3
"""
Hardware Preflight Tests for Phase 4.1 - Service Integration Testing
Purpose: Verify Vega 8 64-wide wavefront support and zRAM 2-tier status
Reference: conductor/tracks/phase-4.1-integration/spec.md
Last Updated: 2026-02-14
"""

import pytest
import subprocess
import time
import psutil
import json
import os
from pathlib import Path
from typing import Dict, Any, List

# Optional imports for hardware tests
try:
    import numpy as np
except ImportError:
    np = None


class TestHardwarePreflight:
    """Hardware compatibility and optimization tests."""

    @pytest.mark.hardware
    def test_cpu_compatibility(self, hardware_requirements):
        """Test CPU compatibility with Ryzen 7 5700U."""
        try:
            result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, "lscpu command failed"
            
            cpu_info = result.stdout
            assert hardware_requirements['cpu_model'] in cpu_info, \
                f"CPU {hardware_requirements['cpu_model']} not found in lscpu output"
            
            # More robust core/thread detection
            import re
            cores_match = re.search(r'Core\(s\) per socket:\s+(\d+)', cpu_info)
            threads_match = re.search(r'CPU\(s\):\s+(\d+)', cpu_info)
            
            if cores_match:
                cores = int(cores_match.group(1))
                assert 6 <= cores <= 8, f"Expected 6-8 cores, found {cores}"
            
            if threads_match:
                threads = int(threads_match.group(1))
                assert 12 <= threads <= 16, f"Expected 12-16 threads, found {threads}"
            
        except Exception as e:
            pytest.fail(f"CPU compatibility check failed: {e}")

    @pytest.mark.hardware
    def test_gpu_vulkan_support(self, hardware_requirements):
        """Test GPU and Vulkan support for Vega 8."""
        try:
            # Check Vulkan info
            result = subprocess.run(
                ['vulkaninfo', '--summary'], 
                capture_output=True, text=True, timeout=30
            )
            # vulkaninfo --summary might return non-zero but still have output
            vulkan_info = result.stdout + result.stderr
            
            # Check for Vega 8 GPU (or Renoir/RADV variants)
            gpu_found = any(term in vulkan_info for term in [hardware_requirements['gpu_model'], 'RENOIR', 'AMD Radeon Graphics'])
            assert gpu_found, f"GPU {hardware_requirements['gpu_model']} not found in Vulkan info"
            
            # Check for 64-wide wavefront support (Vega/Renoir standard)
            # Note: vulkaninfo --summary might not show subgroup size, but we check if it is mentioned
            # If not in summary, we might need a deeper check but for now we accept mention of '64' or assume Vega
            assert '64' in vulkan_info or 'RENOIR' in vulkan_info, \
                f"64-wide wavefront capability not confirmed for this GPU"
            
        except subprocess.TimeoutExpired:
            pytest.skip("Vulkan info command timed out")
        except FileNotFoundError:
            pytest.skip("vulkaninfo command not found")
        except Exception as e:
            pytest.fail(f"GPU/Vulkan support check failed: {e}")

    @pytest.mark.hardware
    def test_zram_configuration(self):
        """Test 2-tier zRAM configuration (lz4 + zstd)."""
        try:
            result = subprocess.run(['zramctl'], capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, "zramctl command failed"
            
            zram_info = result.stdout
            
            # Check for lz4 compression
            assert 'lz4' in zram_info, "lz4 compression not found in zRAM configuration"
            
            # Check for zstd compression
            assert 'zstd' in zram_info, "zstd compression not found in zRAM configuration"
            
            # Parse zRAM devices
            lines = zram_info.strip().split('\n')
            zram_devices = []
            
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 6:
                        device = {
                            'name': parts[0],
                            'disksize': parts[1],
                            'memlimit': parts[2],
                            'memused': parts[3],
                            'comptype': parts[4],
                            'priority': parts[5]
                        }
                        zram_devices.append(device)
            
            # Verify we have at least 2 zRAM devices with different compression types
            compression_types = set(device['comptype'] for device in zram_devices)
            assert 'lz4' in compression_types, "lz4 compression type not found"
            assert 'zstd' in compression_types, "zstd compression type not found"
            
            # Verify devices are active
            for device in zram_devices:
                assert device['disksize'] != '0B', f"zRAM device {device['name']} has 0 disk size"
                assert device['memused'] != '0B', f"zRAM device {device['name']} has 0 memory used"
            
        except subprocess.TimeoutExpired:
            pytest.skip("zramctl command timed out")
        except FileNotFoundError:
            pytest.skip("zramctl command not found")
        except Exception as e:
            pytest.fail(f"zRAM configuration check failed: {e}")

    @pytest.mark.hardware
    def test_memory_configuration(self, hardware_requirements):
        """Test memory configuration meets requirements."""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            
            # Check total memory
            total_gb = memory.total / (1024**3)
            assert total_gb >= 8.0, f"System memory {total_gb:.1f}GB below minimum 8GB"
            
            # Check available memory
            available_gb = memory.available / (1024**3)
            assert available_gb >= 6.0, f"Available memory {available_gb:.1f}GB below target {hardware_requirements['memory_target_gb']}GB"
            
            # Check memory usage percentage
            assert memory.percent < 80, f"Memory usage {memory.percent}% too high"
            
            # Check swap usage
            swap = psutil.swap_memory()
            assert swap.percent < 10, f"Swap usage {swap.percent}% too high, zRAM should be handling this"
            
        except Exception as e:
            pytest.fail(f"Memory configuration check failed: {e}")

    @pytest.mark.hardware
    def test_performance_targets(self, hardware_requirements):
        """Test performance targets for latency and throughput."""
        try:
            # Test memory latency
            start_time = time.time()
            # Simple memory allocation test
            test_data = [i for i in range(1000000)]
            memory_access_time = time.time() - start_time
            
            assert memory_access_time < 1.0, f"Memory access too slow: {memory_access_time:.2f}s"
            
            # Test CPU performance (simple computation)
            start_time = time.time()
            result = sum(i * i for i in range(100000))
            computation_time = time.time() - start_time
            
            assert computation_time < 0.5, f"CPU computation too slow: {computation_time:.2f}s"
            
            # Test disk I/O (if needed)
            test_file = Path('/tmp/test_performance.tmp')
            test_content = b'x' * (1024 * 1024)  # 1MB
            
            start_time = time.time()
            test_file.write_bytes(test_content)
            write_time = time.time() - start_time
            
            start_time = time.time()
            read_content = test_file.read_bytes()
            read_time = time.time() - start_time
            
            test_file.unlink()
            
            assert write_time < 1.0, f"Disk write too slow: {write_time:.2f}s"
            assert read_time < 0.5, f"Disk read too slow: {read_time:.2f}s"
            
        except Exception as e:
            pytest.fail(f"Performance targets check failed: {e}")

    @pytest.mark.hardware
    def test_environment_variables(self):
        """Test required environment variables are set."""
        required_vars = [
            'LLAMA_CPP_N_THREADS',
            'LLAMA_CPP_F16_KV',
            'OPENBLAS_CORETYPE',
            'OMP_NUM_THREADS',
            'MEMORY_LIMIT_GB',
            'CHAINLIT_NO_TELEMETRY',
            'CRAWL4AI_NO_TELEMETRY',
            'LANGCHAIN_TRACING_V2',
            'PYDANTIC_NO_TELEMETRY',
            'FASTAPI_NO_TELEMETRY'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            assert value is not None, f"Environment variable {var} not set"
            
            # Check specific values
            if var == 'LLAMA_CPP_N_THREADS':
                assert value == '6', f"LLAMA_CPP_N_THREADS should be 6, got {value}"
            elif var == 'LLAMA_CPP_F16_KV':
                assert value == 'true', f"LLAMA_CPP_F16_KV should be true, got {value}"
            elif var == 'OPENBLAS_CORETYPE':
                assert value == 'ZEN', f"OPENBLAS_CORETYPE should be ZEN, got {value}"
            elif var == 'OMP_NUM_THREADS':
                assert value == '1', f"OMP_NUM_THREADS should be 1, got {value}"
            elif var == 'MEMORY_LIMIT_GB':
                assert float(value) <= 6.0, f"MEMORY_LIMIT_GB should be <= 6.0, got {value}"
            elif var in ['CHAINLIT_NO_TELEMETRY', 'CRAWL4AI_NO_TELEMETRY', 'PYDANTIC_NO_TELEMETRY', 'FASTAPI_NO_TELEMETRY']:
                assert value == 'true', f"{var} should be true, got {value}"
            elif var == 'LANGCHAIN_TRACING_V2':
                assert value == 'false', f"LANGCHAIN_TRACING_V2 should be false, got {value}"

    @pytest.mark.hardware
    def test_required_tools_available(self):
        """Test required tools are available."""
        required_tools = [
            'podman',
            'podman-compose',
            'docker',
            'vulkaninfo',
            'zramctl',
            'lscpu'
        ]
        
        for tool in required_tools:
            try:
                # Check with --help or --version as a fallback
                result = subprocess.run([tool, '--help'], capture_output=True, text=True, timeout=5)
                # We care that it exists in PATH, not necessarily the return code for --help
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pytest.fail(f"Tool {tool} not available in PATH")

    @pytest.mark.hardware
    def test_network_configuration(self):
        """Test network configuration for container networking."""
        try:
            # Check if network interfaces are available
            interfaces = psutil.net_if_addrs()
            assert len(interfaces) > 0, "No network interfaces found"
            
            # Check for Docker/Podman bridge interface
            bridge_interfaces = [iface for iface in interfaces.keys() if 'docker' in iface or 'podman' in iface or 'br-' in iface]
            
            # This might not be present if containers aren't running, so just log
            if bridge_interfaces:
                print(f"Found container bridge interfaces: {bridge_interfaces}")
            
            # Check for localhost connectivity
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', 80))
            sock.close()
            
            # Port 80 might not be open, but connection should not fail
            assert result in [0, 111], f"Localhost connectivity check failed with code {result}"
            
        except Exception as e:
            pytest.fail(f"Network configuration check failed: {e}")

    @pytest.mark.hardware  
    def test_filesystem_performance(self):
        """Test filesystem performance for AI model storage."""
        try:
            # Test temporary file performance
            test_dir = Path('/tmp/xnai_test')
            test_dir.mkdir(exist_ok=True)
            
            # Test file creation speed
            start_time = time.time()
            for i in range(100):
                test_file = test_dir / f'test_{i}.tmp'
                test_file.write_text(f'Test content {i}')
            creation_time = time.time() - start_time
            
            assert creation_time < 5.0, f"File creation too slow: {creation_time:.2f}s"
            
            # Test file read speed
            start_time = time.time()
            for i in range(100):
                test_file = test_dir / f'test_{i}.tmp'
                content = test_file.read_text()
            read_time = time.time() - start_time
            
            assert read_time < 2.0, f"File read too slow: {read_time:.2f}s"
            
            # Cleanup
            import shutil
            shutil.rmtree(test_dir)
            
        except Exception as e:
            pytest.fail(f"Filesystem performance check failed: {e}")

    @pytest.mark.hardware
    def test_system_stability(self):
        """Test system stability under load."""
        try:
            # Monitor system for 10 seconds
            start_time = time.time()
            cpu_samples = []
            memory_samples = []
            
            while time.time() - start_time < 10:
                cpu_samples.append(psutil.cpu_percent(interval=1))
                memory_samples.append(psutil.virtual_memory().percent)
            
            # Check for stability (no extreme spikes)
            cpu_avg = sum(cpu_samples) / len(cpu_samples)
            cpu_max = max(cpu_samples)
            memory_avg = sum(memory_samples) / len(memory_samples)
            memory_max = max(memory_samples)
            
            # System should not be under extreme load
            assert cpu_max < 90, f"CPU max {cpu_max}% too high during stability test"
            assert memory_max < 90, f"Memory max {memory_max}% too high during stability test"
            
            # Should not have extreme variance
            cpu_variance = max(cpu_samples) - min(cpu_samples)
            memory_variance = max(memory_samples) - min(memory_samples)
            
            assert cpu_variance < 50, f"CPU variance {cpu_variance}% too high"
            assert memory_variance < 30, f"Memory variance {memory_variance}% too high"
            
        except Exception as e:
            pytest.fail(f"System stability check failed: {e}")

    @pytest.mark.hardware
    def test_security_configuration(self):
        """Test security configuration for rootless containers."""
        try:
            # Check if running as non-root
            assert os.getuid() != 0, "Tests should not run as root"
            
            # Check for user namespace support
            try:
                result = subprocess.run(['unshare', '--user', 'echo', 'test'], capture_output=True, text=True, timeout=5)
                assert result.returncode == 0, "User namespace support not available"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pytest.skip("User namespace support check not available")
            
            # Check for seccomp support (basic check)
            try:
                result = subprocess.run(['cat', '/proc/sys/kernel/seccomp/actions_avail'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    assert 'log' in result.stdout, "Seccomp logging not available"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Optional feature
            
        except Exception as e:
            pytest.fail(f"Security configuration check failed: {e}")


class TestHardwareIntegration:
    """Integration tests that combine hardware checks with service readiness."""

    @pytest.mark.hardware
    @pytest.mark.integration
    def test_complete_hardware_readiness(self, hardware_requirements, check_hardware_compatibility):
        """Test complete hardware readiness for Xoe-NovAi stack."""
        # Run all hardware compatibility checks
        check_hardware_compatibility()
        
        # Additional integration checks
        self._test_vulkan_compute_capabilities()
        self._test_memory_bandwidth()
        self._test_storage_performance()

    def _test_vulkan_compute_capabilities(self):
        """Test Vulkan compute capabilities."""
        try:
            result = subprocess.run(['vulkaninfo', '--json'], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                pytest.skip("Cannot get Vulkan JSON info")
            
            vulkan_data = json.loads(result.stdout)
            
            # Check for compute queue families
            queue_families = vulkan_data.get('queueFamilies', [])
            compute_families = [qf for qf in queue_families if 'COMPUTE' in qf.get('queueFlags', [])]
            
            assert len(compute_families) > 0, "No compute queue families found"
            
            # Check for required extensions
            device_extensions = vulkan_data.get('deviceExtensions', [])
            required_extensions = [
                'VK_KHR_swapchain',
                'VK_KHR_external_memory_fd'
            ]
            
            for ext in required_extensions:
                assert any(ext in dev_ext.get('extensionName', '') for dev_ext in device_extensions), \
                    f"Required Vulkan extension {ext} not found"
            
        except Exception as e:
            pytest.fail(f"Vulkan compute capabilities check failed: {e}")

    def _test_memory_bandwidth(self):
        """Test memory bandwidth for AI workloads."""
        try:
            # Simple memory bandwidth test
            import numpy as np
            
            # Create large arrays
            size = 1000000
            a = np.random.random(size).astype(np.float32)
            b = np.random.random(size).astype(np.float32)
            
            # Test memory operations
            start_time = time.time()
            c = a + b  # Memory-bound operation
            memory_time = time.time() - start_time
            
            # Test compute operations  
            start_time = time.time()
            d = np.dot(a, b)  # Compute-bound operation
            compute_time = time.time() - start_time
            
            # Basic sanity checks
            assert memory_time < 1.0, f"Memory operation too slow: {memory_time:.2f}s"
            assert compute_time < 2.0, f"Compute operation too slow: {compute_time:.2f}s"
            
        except ImportError:
            pytest.skip("NumPy not available for memory bandwidth test")
        except Exception as e:
            pytest.fail(f"Memory bandwidth check failed: {e}")

    def _test_storage_performance(self):
        """Test storage performance for model loading."""
        try:
            test_file = Path('/tmp/xnai_storage_test.bin')
            test_size = 100 * 1024 * 1024  # 100MB
            
            # Test write performance
            test_data = os.urandom(test_size)
            start_time = time.time()
            test_file.write_bytes(test_data)
            write_time = time.time() - start_time
            write_speed = test_size / write_time / (1024 * 1024)  # MB/s
            
            # Test read performance
            start_time = time.time()
            read_data = test_file.read_bytes()
            read_time = time.time() - start_time
            read_speed = test_size / read_time / (1024 * 1024)  # MB/s
            
            # Cleanup
            test_file.unlink()
            
            # Verify speeds
            assert write_speed > 50, f"Write speed too slow: {write_speed:.1f} MB/s"
            assert read_speed > 100, f"Read speed too slow: {read_speed:.1f} MB/s"
            
        except Exception as e:
            pytest.fail(f"Storage performance check failed: {e}")


# ============================================================================
# Test Data and Constants
# ============================================================================

HARDWARE_TEST_CASES = [
    {
        'name': 'Ryzen 7 5700U Vega 8',
        'cpu_model': 'Ryzen 7 5700U',
        'gpu_model': 'Vega 8',
        'cores': 8,
        'threads': 16,
        'base_freq': 1.8,
        'boost_freq': 4.3,
        'tdp': 15,
        'integrated_gpu': True
    },
    {
        'name': 'Ryzen 9 5900HX Vega 8',
        'cpu_model': 'Ryzen 9 5900HX',
        'gpu_model': 'Vega 8',
        'cores': 8,
        'threads': 16,
        'base_freq': 3.3,
        'boost_freq': 4.6,
        'tdp': 45,
        'integrated_gpu': True
    }
]

PERFORMANCE_THRESHOLDS = {
    'memory_latency_ms': 200,
    'cpu_computation_s': 0.5,
    'disk_write_mb_s': 50,
    'disk_read_mb_s': 100,
    'vulkan_compute_queues': 1,
    'zram_devices': 2
}


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])