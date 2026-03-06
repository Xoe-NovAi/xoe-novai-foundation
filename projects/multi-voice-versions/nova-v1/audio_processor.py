#!/usr/bin/env python3
"""
Audio Processor - Advanced audio processing with noise reduction, echo cancellation, and enhancement
"""

import asyncio
import numpy as np
import soundfile as sf
import tempfile
import wave
import os
from typing import Tuple, Optional, Union, Dict, Any
import logging

# Try to import pyaudio for recording
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logging.warning("PyAudio not available - audio recording will be simulated")

class AudioProcessor:
    """Advanced audio processing with noise reduction, echo cancellation, and enhancement"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, 
                 config: Optional[Dict[str, Any]] = None):
        """Initialize audio processor"""
        self.sample_rate = sample_rate
        self.channels = channels
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Audio recording settings
        self.chunk_size = self.config.get('buffer_size', 1024)
        self.vad_threshold = self.config.get('vad_threshold', 0.5)
        self.silence_timeout = self.config.get('silence_timeout', 2.0)
        self.max_record_time = self.config.get('max_audio_duration', 30.0)
        
        # Initialize PyAudio if available
        self.pyaudio_instance = None
        if PYAUDIO_AVAILABLE:
            try:
                self.pyaudio_instance = pyaudio.PyAudio()
                self.logger.info("PyAudio initialized successfully")
            except Exception as e:
                self.logger.warning(f"PyAudio initialization failed: {e}")
        
        # Initialize processing components
        self.noise_reduction = NoiseReduction()
        self.echo_cancellation = EchoCancellation()
        self.audio_enhancement = AudioEnhancement()
        self.format_converter = FormatConverter()

    async def record_audio_with_vad(self) -> Optional[bytes]:
        """Record audio with Voice Activity Detection
        
        Returns:
            Audio data as bytes, or None if recording failed
        """
        if self.pyaudio_instance is None:
            self.logger.warning("PyAudio not available - returning simulated audio")
            return await self._simulate_audio_recording()
        
        try:
            self.logger.info("Starting audio recording with VAD...")
            
            # Open audio stream
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            silence_frames = 0
            total_frames = 0
            max_frames = int(self.max_record_time * self.sample_rate / self.chunk_size)
            silence_threshold_frames = int(self.silence_timeout * self.sample_rate / self.chunk_size)
            
            self.logger.info("Listening for speech... (press Ctrl+C to stop)")
            
            while total_frames < max_frames:
                try:
                    # Read audio chunk
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                    total_frames += 1
                    
                    # Simple VAD: check if audio level is above threshold
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
                    normalized_rms = rms / 32768.0  # Normalize to 0-1 range
                    
                    if normalized_rms > self.vad_threshold:
                        silence_frames = 0  # Reset silence counter
                    else:
                        silence_frames += 1
                    
                    # Stop if silence detected for too long
                    if silence_frames >= silence_threshold_frames and len(frames) > silence_threshold_frames:
                        self.logger.info("Silence detected, stopping recording")
                        break
                        
                except IOError as e:
                    self.logger.warning(f"Audio input error: {e}")
                    continue
            
            # Close stream
            stream.stop_stream()
            stream.close()
            
            # Convert frames to WAV bytes
            audio_bytes = self._frames_to_wav_bytes(frames)
            self.logger.info(f"Recorded {len(audio_bytes)} bytes of audio")
            
            return audio_bytes
            
        except Exception as e:
            self.logger.error(f"Audio recording failed: {e}")
            return None

    async def _simulate_audio_recording(self) -> Optional[bytes]:
        """Simulate audio recording for testing without microphone"""
        self.logger.info("Simulating audio recording (no microphone available)")
        
        # Generate a short silent audio file for testing
        duration = 2.0  # seconds
        samples = int(duration * self.sample_rate)
        
        # Create a simple test audio (silence with slight noise)
        audio_array = np.random.randn(samples).astype(np.float32) * 0.01
        
        # Convert to WAV bytes
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        sf.write(temp_path, audio_array, self.sample_rate)
        
        with open(temp_path, 'rb') as f:
            audio_bytes = f.read()
        
        os.unlink(temp_path)
        
        return audio_bytes

    def _frames_to_wav_bytes(self, frames: list) -> bytes:
        """Convert audio frames to WAV bytes"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(b''.join(frames))
        
        with open(temp_path, 'rb') as f:
            audio_bytes = f.read()
        
        os.unlink(temp_path)
        
        return audio_bytes

    def preprocess_audio(self, audio_data: bytes) -> bytes:
        """Preprocess audio for STT (synchronous wrapper)"""
        # For now, just return the audio as-is
        # In production, would apply noise reduction, normalization, etc.
        return audio_data

    def cleanup(self):
        """Cleanup audio resources"""
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.logger.info("PyAudio resources cleaned up")
        
    async def process_audio(self, audio_data: Union[bytes, np.ndarray], 
                          format: str = 'wav') -> bytes:
        """Process audio with advanced features"""
        try:
            # Convert to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_data = self._bytes_to_array(audio_data, format)
            
            # Noise reduction
            audio_data = await self.noise_reduction.reduce(audio_data)
            
            # Echo cancellation
            audio_data = await self.echo_cancellation.cancel(audio_data)
            
            # Audio enhancement
            audio_data = await self.audio_enhancement.enhance(audio_data)
            
            # Convert back to bytes
            return self._array_to_bytes(audio_data, format)
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {e}")
            raise
            
    def _bytes_to_array(self, audio_bytes: bytes, format: str) -> np.ndarray:
        """Convert audio bytes to numpy array"""
        try:
            audio_data, sample_rate = sf.read(
                audio_bytes, 
                format=format, 
                samplerate=self.sample_rate
            )
            return audio_data
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {e}")
            raise
            
    def _array_to_bytes(self, audio_array: np.ndarray, format: str) -> bytes:
        """Convert numpy array to audio bytes"""
        try:
            audio_bytes = sf.write(
                audio_array.tobytes(), 
                audio_array, 
                self.sample_rate, 
                format=format
            )
            return audio_bytes
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {e}")
            raise
            
    async def enhance_voice(self, audio_data: Union[bytes, np.ndarray]) -> bytes:
        """Enhance voice quality with advanced processing"""
        try:
            # Convert to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_data = self._bytes_to_array(audio_data, 'wav')
            
            # Apply voice enhancement
            enhanced_audio = await self.audio_enhancement.enhance_voice(audio_data)
            
            # Convert back to bytes
            return self._array_to_bytes(enhanced_audio, 'wav')
            
        except Exception as e:
            self.logger.error(f"Voice enhancement failed: {e}")
            raise
            
    async def reduce_noise(self, audio_data: Union[bytes, np.ndarray]) -> bytes:
        """Reduce background noise"""
        try:
            # Convert to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_data = self._bytes_to_array(audio_data, 'wav')
            
            # Apply noise reduction
            cleaned_audio = await self.noise_reduction.reduce(audio_data)
            
            # Convert back to bytes
            return self._array_to_bytes(cleaned_audio, 'wav')
            
        except Exception as e:
            self.logger.error(f"Noise reduction failed: {e}")
            raise
            
    async def cancel_echo(self, audio_data: Union[bytes, np.ndarray]) -> bytes:
        """Cancel echo and reverberation"""
        try:
            # Convert to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_data = self._bytes_to_array(audio_data, 'wav')
            
            # Apply echo cancellation
            cleaned_audio = await self.echo_cancellation.cancel(audio_data)
            
            # Convert back to bytes
            return self._array_to_bytes(cleaned_audio, 'wav')
            
        except Exception as e:
            self.logger.error(f"Echo cancellation failed: {e}")
            raise
            
    async def convert_format(self, audio_data: Union[bytes, np.ndarray], 
                           target_format: str) -> bytes:
        """Convert audio format"""
        try:
            # Convert to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_data = self._bytes_to_array(audio_data, 'wav')
            
            # Convert format
            converted_audio = await self.format_converter.convert(audio_data, target_format)
            
            # Convert back to bytes
            return self._array_to_bytes(converted_audio, target_format)
            
        except Exception as e:
            self.logger.error(f"Format conversion failed: {e}")
            raise
            
    def get_audio_info(self, audio_data: Union[bytes, np.ndarray]) -> Dict[str, Any]:
        """Get audio information"""
        try:
            if isinstance(audio_data, bytes):
                audio_data, sample_rate = sf.read(audio_data)
            else:
                sample_rate = self.sample_rate
                
            return {
                'duration': len(audio_data) / sample_rate,
                'sample_rate': sample_rate,
                'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                'format': 'wav'
            }
        except Exception as e:
            self.logger.error(f"Audio info extraction failed: {e}")
            return {}
            
class NoiseReduction:
    """Noise reduction component"""
    
    async def reduce(self, audio_data: np.ndarray) -> np.ndarray:
        """Reduce background noise"""
        # Simple noise reduction implementation
        # In production, use advanced algorithms like spectral subtraction
        return audio_data * 0.9  # Placeholder implementation
        
class EchoCancellation:
    """Echo cancellation component"""
    
    async def cancel(self, audio_data: np.ndarray) -> np.ndarray:
        """Cancel echo and reverberation"""
        # Simple echo cancellation implementation
        # In production, use adaptive filters
        return audio_data * 0.8  # Placeholder implementation
        
class AudioEnhancement:
    """Audio enhancement component"""
    
    async def enhance(self, audio_data: np.ndarray) -> np.ndarray:
        """Enhance overall audio quality"""
        # Simple enhancement implementation
        # In production, use advanced audio processing
        return audio_data * 1.1  # Placeholder implementation
        
    async def enhance_voice(self, audio_data: np.ndarray) -> np.ndarray:
        """Enhance voice specifically"""
        # Simple voice enhancement implementation
        return audio_data * 1.2  # Placeholder implementation
        
class FormatConverter:
    """Audio format conversion component"""
    
    async def convert(self, audio_data: np.ndarray, target_format: str) -> np.ndarray:
        """Convert audio format"""
        # Simple format conversion implementation
        # In production, use proper format conversion
        return audio_data  # Placeholder implementation