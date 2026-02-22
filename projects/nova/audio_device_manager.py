#!/usr/bin/env python3
"""
Audio Device Manager - Handle Bluetooth AirPods input + Mac mini speakers output
Prevents Bluetooth mode-switching latency by keeping separate input/output devices.
Based on original setup: AirPods Pro (mic input) + Mac mini Speakers (audio output)
"""

import subprocess
import logging
import asyncio
import json
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AudioDevice:
    """Represents an audio input or output device"""
    name: str
    device_id: str
    is_input: bool  # True for input, False for output
    is_builtin: bool
    is_airpods: bool
    device_uid: Optional[str] = None


class AudioDeviceManager:
    """
    Manages audio devices on macOS.
    
    Key insight from original setup:
    - Use AirPods Pro as MICROPHONE INPUT (Bluetooth)
    - Use Mac mini Speakers as AUDIO OUTPUT (wired/built-in)
    - This avoids HFP/A2DP mode-switching latency
    """

    def __init__(self):
        """Initialize audio device manager"""
        self.logger = logging.getLogger(__name__)
        self.input_devices: Dict[str, AudioDevice] = {}
        self.output_devices: Dict[str, AudioDevice] = {}
        self._refresh_devices()

    def _refresh_devices(self) -> None:
        """Refresh list of available audio devices using `system_profiler`"""
        try:
            # Get audio input devices
            result = subprocess.run(
                ["system_profiler", "SPAudioDataType", "-json"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                self._parse_audio_devices(data)
                self.logger.info(f"Found {len(self.input_devices)} input, {len(self.output_devices)} output devices")
            else:
                self.logger.warning("Failed to get audio device list")

        except Exception as e:
            self.logger.error(f"Error refreshing audio devices: {e}")

    def _parse_audio_devices(self, profile_data: dict) -> None:
        """Parse audio devices from system_profiler output"""
        try:
            audio_data = profile_data.get("SPAudioDataType", [])

            for device in audio_data:
                name = device.get("_name", "")
                device_id = device.get("_name", "")

                # Check if it's input or output (or both)
                input_channels = device.get("coreaudio_input_channel_count", 0)
                output_channels = device.get("coreaudio_output_channel_count", 0)

                is_builtin = "internal" in name.lower() or "built-in" in name.lower()
                is_airpods = "airpod" in name.lower()

                # Register as input device
                if input_channels > 0:
                    dev = AudioDevice(
                        name=name,
                        device_id=device_id,
                        is_input=True,
                        is_builtin=is_builtin,
                        is_airpods=is_airpods,
                        device_uid=device.get("coreaudio_device_uid")
                    )
                    self.input_devices[device_id] = dev

                # Register as output device
                if output_channels > 0:
                    dev = AudioDevice(
                        name=name,
                        device_id=device_id,
                        is_input=False,
                        is_builtin=is_builtin,
                        is_airpods=is_airpods,
                        device_uid=device.get("coreaudio_device_uid")
                    )
                    self.output_devices[device_id] = dev

        except Exception as e:
            self.logger.error(f"Error parsing audio devices: {e}")

    def list_input_devices(self) -> List[AudioDevice]:
        """Get list of available input devices"""
        return list(self.input_devices.values())

    def list_output_devices(self) -> List[AudioDevice]:
        """Get list of available output devices"""
        return list(self.output_devices.values())

    def get_airpods_device(self) -> Optional[AudioDevice]:
        """Find AirPods Pro/Air/Max device if connected"""
        for device in self.input_devices.values():
            if device.is_airpods:
                return device
        return None

    def get_speakers_device(self) -> Optional[AudioDevice]:
        """Find Mac mini Speakers or built-in output device"""
        # Prefer "Mac mini Speakers" but fallback to any built-in speaker
        for device in self.output_devices.values():
            if "mac mini" in device.name.lower() and "speaker" in device.name.lower():
                return device

        # Fallback to any built-in speaker
        for device in self.output_devices.values():
            if device.is_builtin and ("speaker" in device.name.lower() or "internal" in device.name.lower()):
                return device

        return None

    def set_input_device(self, device: AudioDevice) -> bool:
        """Set audio input device
        
        Args:
            device: AudioDevice to set as input
            
        Returns:
            True if successful
        """
        if not device.is_input:
            self.logger.error(f"Device {device.name} is not an input device")
            return False

        try:
            # Use SwitchAudioSource if available (brew install switchaudio-osxor our custom solution
            result = subprocess.run(
                ["bash", "-c", f"defaults write com.apple.coreaudio.avr.stdinDeviceUID {device.device_uid or device.device_id}"],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                self.logger.info(f"Set input device to: {device.name}")
                return True
            else:
                self.logger.warning(f"Failed to set input device: {result.stderr.decode()}")
                return False

        except Exception as e:
            self.logger.error(f"Error setting input device: {e}")
            return False

    def set_output_device(self, device: AudioDevice) -> bool:
        """Set audio output device
        
        Args:
            device: AudioDevice to set as output
            
        Returns:
            True if successful
        """
        if device.is_input:
            self.logger.error(f"Device {device.name} is not an output device")
            return False

        try:
            # Method 1: Try SwitchAudioSource (if installed via brew)
            result = subprocess.run(
                ["bash", "-c", "which SwitchAudioSource && SwitchAudioSource -s '{}'].format(device.name)"],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                self.logger.info(f"Set output device to: {device.name}")
                return True

            # Method 2: Use CoreAudio defaults
            result = subprocess.run(
                ["bash", "-c", f"defaults write com.apple.coreaudio.avr.stdinDeviceUID {device.device_uid  or device.device_id}"],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                self.logger.info(f"Set output device to: {device.name}")
                return True

            self.logger.warning(f"Failed to set output device: {result.stderr.decode()}")
            return False

        except Exception as e:
            self.logger.error(f"Error setting output device: {e}")
            return False

    def configure_optimal_audio(self) -> Tuple[bool, str]:
        """
        Configure optimal audio setup for blind-accessible voice assistant.
        
        Ideal: AirPods Pro for input, Mac mini Speakers for output
        Benefit: Avoids Bluetooth HFP/A2DP mode-switching latency
        
        Returns:
            (success: bool, message: str)
        """
        results = []

        # Find and set input device (AirPods)
        airpods = self.get_airpods_device()
        if airpods:
            if self.set_input_device(airpods):
                msg = f"✅ Input: {airpods.name}"
                results.append(msg)
                self.logger.info(msg)
            else:
                msg = f"⚠️  Input device set failed, using default"
                results.append(msg)
        else:
            msg = "⚠️  AirPods not found, will use default microphone"
            results.append(msg)
            self.logger.warning(msg)

        # Find and set output device (Mac mini Speakers)
        speakers = self.get_speakers_device()
        if speakers:
            if self.set_output_device(speakers):
                msg = f"✅ Output: {speakers.name}"
                results.append(msg)
                self.logger.info(msg)
            else:
                msg = f"⚠️  Output device set failed, using default"
                results.append(msg)
        else:
            msg = "⚠️  Mac mini Speakers not found, will use default output"
            results.append(msg)
            self.logger.warning(msg)

        success = len([r for r in results if r.startswith("✅")]) == 2
        message = "\n".join(results)

        return success, message

    def print_device_list(self) -> None:
        """Print available input and output devices"""
        print("\n=== Audio Input Devices ===")
        for i, device in enumerate(self.list_input_devices(), 1):
            airpods_badge = "🎧" if device.is_airpods else " "
            builtin_badge = "🔘" if device.is_builtin else " "
            print(f"{i}. {airpods_badge} {builtin_badge} {device.name} ({device.device_id})")

        print("\n=== Audio Output Devices ===")
        for i, device in enumerate(self.list_output_devices(), 1):
            speaker_badge = "🔊" if "speaker" in device.name.lower() else " "
            builtin_badge = "🔘" if device.is_builtin else " "
            print(f"{i}. {speaker_badge} {builtin_badge} {device.name} ({device.device_id})")


class AudioGuardian:
    """
    Guardian process to keep Mac mini Speakers as output device.
    
    Problem: macOS can switch output to AirPods when they connect/disconnect,
    causing the blind user to lose audio.
    
    Solution: Run every 5 seconds, ensure speakers remain as output.
    """

    def __init__(self, check_interval: float = 5.0):
        """Initialize guardian
        
        Args:
            check_interval: How often to check/correct output (seconds)
        """
        self.check_interval = check_interval
        self.running = False
        self.logger = logging.getLogger(__name__)
        self.device_manager = AudioDeviceManager()

    async def start(self) -> None:
        """Start the audio guardian daemon"""
        self.running = True
        self.logger.info(f"🛡️  Audio Guardian started (check interval: {self.check_interval}s)")

        while self.running:
            try:
                self._ensure_speakers_output()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Guardian error: {e}")
                await asyncio.sleep(self.check_interval)

    def stop(self) -> None:
        """Stop the audio guardian"""
        self.running = False
        self.logger.info("🛡️  Audio Guardian stopped")

    def _ensure_speakers_output(self) -> None:
        """Check and correct output device if needed"""
        try:
            # Get current output device using ioreg
            result = subprocess.run(
                ["bash", "-c", "defaults read com.apple.coreaudio.avr.stdinDeviceUID"],
                capture_output=True,
                text=True,
                timeout=2
            )

            current_output = result.stdout.strip() if result.returncode == 0 else None

            # Get desired output device
            speakers = self.device_manager.get_speakers_device()

            if speakers and current_output != speakers.device_uid:
                # Output device is not speakers - correct it
                self.device_manager.set_output_device(speakers)
                self.logger.info(f"🔧 Corrected output device to: {speakers.name}")

        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout checking audio device")
        except Exception as e:
            self.logger.warning(f"Guardian check failed: {e}")


# Convenience functions for integration

def get_audio_device_manager() -> AudioDeviceManager:
    """Get or create audio device manager singleton"""
    return AudioDeviceManager()


async def start_audio_guardian(check_interval: float = 5.0) -> AudioGuardian:
    """Start audio guardian process
    
    Args:
        check_interval: How often to poll and correct output device (seconds)
        
    Returns:
        AudioGuardian instance (call .stop() to halt)
    """
    guardian = AudioGuardian(check_interval=check_interval)
    asyncio.create_task(guardian.start())
    return guardian
