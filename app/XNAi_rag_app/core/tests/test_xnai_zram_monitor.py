"""
Tests for zRAM Monitor (SESS-26)
Validates all 4 required test scenarios:
  1. Normal operation (zRAM <50%) → returns True
  2. High zRAM (>90%) → triggers backoff, pauses 30s, returns False
  3. Logging captures all backoff events
  4. zramctl command works and parses correctly
"""

import unittest
import logging
import time
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the app directory to path
app_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(app_path))

from xnai_zram_monitor import (
    check_and_backoff,
    _parse_zramctl_output,
    _parse_size_to_gb,
    ZRAM_USAGE_THRESHOLD_PERCENT,
    DEFAULT_BACKOFF_DURATION_SECONDS,
)

# Setup logging to capture messages
logging.basicConfig(level=logging.DEBUG)


def _execute_real_zramctl():
    """Helper: Check if zramctl is actually available"""
    try:
        import subprocess
        result = subprocess.run(
            ["zramctl"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


class TestZramSizeParser(unittest.TestCase):
    """Test size string parsing (K, M, G, T units)"""
    
    def test_kilobytes_to_gb(self):
        self.assertAlmostEqual(_parse_size_to_gb("1000K"), 0.001, places=6)
    
    def test_megabytes_to_gb(self):
        self.assertAlmostEqual(_parse_size_to_gb("500M"), 0.5, places=6)
    
    def test_gigabytes_to_gb(self):
        self.assertAlmostEqual(_parse_size_to_gb("4G"), 4.0, places=6)
    
    def test_terabytes_to_gb(self):
        self.assertAlmostEqual(_parse_size_to_gb("1T"), 1000.0, places=6)
    
    def test_decimal_values(self):
        self.assertAlmostEqual(_parse_size_to_gb("1.3G"), 1.3, places=6)
        self.assertAlmostEqual(_parse_size_to_gb("460.2M"), 0.4602, places=6)
    
    def test_lowercase_units(self):
        self.assertAlmostEqual(_parse_size_to_gb("4g"), 4.0, places=6)
    
    def test_invalid_format(self):
        self.assertEqual(_parse_size_to_gb("invalid"), 0.0)


class TestZramctlParser(unittest.TestCase):
    """Test zramctl output parsing"""
    
    def test_parse_real_zramctl_output(self):
        """Test parsing actual zramctl output"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE  DATA  COMPR  TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram1 zstd            8G    4K    59B    20K         [SWAP]\n"
            "/dev/zram0 lz4             4G  1.3G 460.2M 479.5M         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            result = _parse_zramctl_output()
            
            self.assertIsNotNone(result)
            disksize_gb, total_gb, usage_percent = result
            
            # Check values: disksize=4G, total=479.5M
            self.assertAlmostEqual(disksize_gb, 4.0, places=1)
            self.assertAlmostEqual(total_gb, 0.4795, places=3)
            # Usage percent: 0.4795 / 4.0 * 100 ≈ 11.99%
            self.assertAlmostEqual(usage_percent, 11.99, places=1)
    
    def test_parse_low_usage(self):
        """Test parsing low zRAM usage (< 50%)"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE  DATA  COMPR TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G    1G   200M 1.2G         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            result = _parse_zramctl_output()
            disksize_gb, total_gb, usage_percent = result
            
            # 1.2G / 4G = 30%
            self.assertAlmostEqual(usage_percent, 30.0, places=1)
    
    def test_parse_high_usage(self):
        """Test parsing high zRAM usage (> 90%)"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE  DATA   COMPR   TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G  3.5G    900M   3.8G         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            result = _parse_zramctl_output()
            disksize_gb, total_gb, usage_percent = result
            
            # 3.8G / 4G = 95%
            self.assertAlmostEqual(usage_percent, 95.0, places=1)
    
    def test_parse_error_handling(self):
        """Test error handling when zramctl fails"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            
            result = _parse_zramctl_output()
            self.assertIsNone(result)
    
    def test_parse_timeout_handling(self):
        """Test timeout handling"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = TimeoutError()
            
            result = _parse_zramctl_output()
            self.assertIsNone(result)


class TestCheckAndBackoffNormal(unittest.TestCase):
    """Test 1: Normal operation (zRAM <50%) → returns True"""
    
    def test_normal_low_usage_returns_true(self):
        """Low zRAM usage should return True immediately"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE DATA COMPR TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G   1G  200M 1.2G         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            start_time = time.time()
            result = check_and_backoff(backoff_duration=30)
            elapsed = time.time() - start_time
            
            # Should return True
            self.assertTrue(result)
            # Should NOT sleep
            self.assertLess(elapsed, 5.0)
    
    def test_multiple_calls_normal(self):
        """Multiple normal checks should all return True"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE DATA COMPR TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G  500M  100M 600M         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            for _ in range(5):
                result = check_and_backoff()
                self.assertTrue(result)


class TestCheckAndBackoffHighUsage(unittest.TestCase):
    """Test 2: High zRAM (>90%) → triggers backoff, pauses 30s, returns False"""
    
    def test_high_usage_triggers_backoff(self):
        """High zRAM usage should trigger backoff and return False"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE DATA   COMPR   TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G  3.5G    900M   3.8G         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            # Use short backoff duration for testing
            start_time = time.time()
            result = check_and_backoff(backoff_duration=1)
            elapsed = time.time() - start_time
            
            # Should return False
            self.assertFalse(result)
            # Should have slept ~1 second
            self.assertGreaterEqual(elapsed, 0.9)
    
    def test_backoff_duration_honored(self):
        """Backoff should sleep for specified duration"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE DATA   COMPR   TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G  3.8G    950M   3.9G         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            # Test with 2-second backoff
            start_time = time.time()
            result = check_and_backoff(backoff_duration=2)
            elapsed = time.time() - start_time
            
            self.assertFalse(result)
            # Should sleep ~2 seconds
            self.assertGreaterEqual(elapsed, 1.8)


class TestCheckAndBackoffLogging(unittest.TestCase):
    """Test 3: Verify logging captures all backoff events"""
    
    def test_logging_on_backoff(self):
        """Backoff should log warning with proper format"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE DATA   COMPR   TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G  3.8G    950M   3.9G         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            with patch('xnai_zram_monitor.logger') as mock_logger:
                result = check_and_backoff(backoff_duration=1)
                
                # Should have logged a warning
                self.assertTrue(mock_logger.warning.called)
                
                # Get the log message
                call_args = mock_logger.warning.call_args[0][0]
                
                # Verify log contains required information
                self.assertIn("zRAM0 backoff triggered", call_args)
                self.assertIn("97.5%", call_args)  # 3.9G / 4G
                self.assertIn("90%", call_args)
                self.assertIn("1s", call_args)  # backoff duration
                self.assertIn("used:", call_args)
                self.assertIn("remaining:", call_args)
    
    def test_no_logging_on_normal(self):
        """Normal operation should not log backoff warning"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE DATA COMPR TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G   1G  200M 1.2G         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            with patch('xnai_zram_monitor.logger') as mock_logger:
                result = check_and_backoff()
                
                # Should NOT log a backoff warning
                # (may log other things, but not the backoff message)
                for call in mock_logger.warning.call_args_list:
                    self.assertNotIn("backoff triggered", str(call))


class TestZramctlCommand(unittest.TestCase):
    """Test 4: Verify zramctl command works and parses correctly"""
    
    @unittest.skipUnless(
        _execute_real_zramctl(),
        "zramctl not available in test environment"
    )
    def test_real_zramctl_execution(self):
        """Test with actual zramctl command (if available)"""
        result = _parse_zramctl_output()
        
        if result is not None:
            disksize_gb, total_gb, usage_percent = result
            
            # Verify reasonable values
            self.assertGreater(disksize_gb, 0)
            self.assertGreaterEqual(total_gb, 0)
            self.assertGreater(usage_percent, 0)
            self.assertLess(usage_percent, 200)  # Should be less than 200%
            
            # Usage should not exceed disksize
            self.assertLessEqual(total_gb, disksize_gb * 1.1)


class TestIntegrationExample(unittest.TestCase):
    """Test integration pattern from requirements"""
    
    def test_integration_pattern(self):
        """Test the integration pattern from requirements"""
        mock_output = (
            "NAME       ALGORITHM DISKSIZE DATA COMPR TOTAL STREAMS MOUNTPOINT\n"
            "/dev/zram0 lz4             4G   1G  200M 1.2G         [SWAP]\n"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
            
            # Simulate integration pattern from requirements:
            # for document in documents:
            #     if not check_and_backoff():
            #         continue  # Back off, skip this iteration
            #     process_document(document)
            
            documents = ["doc1", "doc2", "doc3"]
            processed = []
            
            for document in documents:
                if not check_and_backoff():
                    continue
                processed.append(document)
            
            # All should be processed in normal conditions
            self.assertEqual(len(processed), 3)


if __name__ == "__main__":
    unittest.main()
