#!/usr/bin/env python3
"""
Voice Activation Module - Wake word detection and continuous listening for blind accessibility

Features:
- Wake word detection (customizable)
- Continuous audio streaming
- Real-time voice activity detection
- Accessible audio feedback patterns
- Session management for always-on listening
"""

import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from collections import deque
import numpy as np
import soundfile as sf
import threading
import time

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logging.warning("PyAudio not available - voice activation will be limited")

try:
    from audio_device_manager import AudioDeviceManager, start_audio_guardian
    AUDIO_DEVICE_MANAGER_AVAILABLE = True
except ImportError:
    AUDIO_DEVICE_MANAGER_AVAILABLE = False
    logging.debug("Audio device manager not available - using system defaults")

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Simple wake word detector using audio pattern matching
    Detects specific phrases using voice activity patterns
    
    For blind users: Simple, reliable, no special hardware needed
    Common wake words: "Hey Voice", "Voice", "Listen"
    """
    
    def __init__(self, wake_words: Optional[list] = None, config: Optional[Dict] = None):
        """
        Initialize wake word detector
        
        Args:
            wake_words: List of wake word strings (default: ["hey voice", "voice"])
            config: Configuration dict with settings
        """
        self.wake_words = wake_words or ["hey voice", "voice"]
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 16000)
        self.sensitivity = self.config.get('sensitivity', 0.8)  # 0-1, higher = more sensitive
        self.vad_threshold = self.config.get('vad_threshold', 0.3)
        self.min_audio_length = self.config.get('min_audio_length', 0.5)  # seconds
        
        logger.info(f"Wake word detector initialized with words: {self.wake_words}")
    
    def detect_wake_word_from_text(self, text: str) -> bool:
        """
        Detect if text contains wake word
        
        Args:
            text: Transcribed text to check
            
        Returns:
            True if wake word detected
        """
        text_lower = text.lower().strip()
        
        # Check exact matches and partial phrases
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                logger.info(f"Wake word detected: '{wake_word}' in '{text_lower}'")
                return True
        
        return False
    
    def detect_wake_word_from_audio(self, audio_array: np.ndarray) -> bool:
        """
        Detect wake word from audio using energy patterns
        
        For blind users: Quick response to indicate listening started
        
        Args:
            audio_array: Audio data as numpy array
            
        Returns:
            True if likely speech detected (used with feedback)
        """
        # Calculate audio energy
        rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
        normalized_rms = rms / 32768.0 if audio_array.dtype == np.int16 else rms
        
        # Detect if above threshold (indicates speech)
        return normalized_rms > self.vad_threshold


class ContinuousAudioListener:
    """
    Continuous audio listening for voice-first experience
    
    Keeps microphone open, detects voice activity, passes to STT
    For blind users: Natural conversation flow without repeated "listening" prompts
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize continuous audio listener"""
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 16000)
        self.chunk_size = self.config.get('chunk_size', 2048)
        self.channels = self.config.get('channels', 1)
        
        self.pyaudio_instance = None
        self.stream = None
        self.is_listening = False
        self.audio_buffer = deque(maxlen=100)  # Rolling buffer
        
        self._initialize_audio()
        logger.info("ContinuousAudioListener initialized")
    
    def _initialize_audio(self):
        """Initialize PyAudio"""
        if not PYAUDIO_AVAILABLE:
            logger.warning("PyAudio not available")
            return
        
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            logger.info("PyAudio initialized for continuous listening")
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
    
    async def start_listening(self) -> bool:
        """
        Start continuous audio listening
        
        For blind users: Non-blocking, returns immediately
        
        Returns:
            True if listening started successfully
        """
        if not self.pyaudio_instance:
            logger.error("Cannot start listening - PyAudio not available")
            return False
        
        try:
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                exception_on_overflow=False
            )
            self.is_listening = True
            logger.info("Audio listening started")
            return True
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            return False
    
    async def stop_listening(self):
        """Stop continuous audio listening"""
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        logger.info("Audio listening stopped")
    
    async def get_audio_chunk(self) -> Optional[bytes]:
        """
        Get next audio chunk without blocking
        
        Returns:
            Audio bytes or None if not listening
        """
        if not self.is_listening or not self.stream:
            return None
        
        try:
            # Use exception_on_overflow=False to handle late buffers gracefully
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            self.audio_buffer.append(data)
            return data
        except Exception as e:
            logger.warning(f"Error reading audio chunk: {e}")
            return None
    
    async def get_continuous_audio(self, timeout: float = 5.0) -> Optional[bytes]:
        """
        Get audio as user is speaking
        
        Uses Voice Activity Detection (VAD) to know when speech starts/stops
        For blind users: Automatic, no button press needed
        
        Args:
            timeout: Max time to wait for speech
            
        Returns:
            Combined audio bytes from user input
        """
        frames = []
        silence_frames = 0
        vad_threshold = 0.2
        silence_threshold = int(1.0 * self.sample_rate / self.chunk_size)  # 1 second
        max_frames = int(timeout * self.sample_rate / self.chunk_size)
        
        start_time = time.time()
        
        while len(frames) < max_frames:
            chunk = await self.get_audio_chunk()
            if chunk is None:
                await asyncio.sleep(0.05)
                continue
            
            # VAD: Check if chunk has speech
            audio_array = np.frombuffer(chunk, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            normalized_rms = rms / 32768.0
            
            if normalized_rms > vad_threshold:
                silence_frames = 0
                frames.append(chunk)
            else:
                silence_frames += 1
                if silence_frames > silence_threshold and len(frames) > silence_threshold:
                    # User finished speaking
                    break
                elif len(frames) > 0:
                    # Still recording silence during speech
                    frames.append(chunk)
            
            # Check timeout
            if time.time() - start_time > timeout:
                break
        
        if frames:
            return b''.join(frames)
        return None
    
    def cleanup(self):
        """Cleanup audio resources"""
        asyncio.run(self.stop_listening())
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            logger.info("Audio resources cleaned up")


class AccessibleAudioFeedback:
    """
    Audio feedback system for blind users
    
    Provides non-intrusive audio cues instead of visual feedback:
    - Status changes (tone patterns)
    - Notifications (unique beeps)
    - Recognition (cheerful ding)
    - Errors (warning tone)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize audio feedback system"""
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 16000)
        self.feedback_enabled = self.config.get('feedback_enabled', True)
        self.volume = self.config.get('volume', 0.5)  # 0-1
        
        # Pre-generate audio tones
        self._generate_tones()
        logger.info("AccessibleAudioFeedback initialized")
    
    def _generate_tones(self):
        """Pre-generate audio feedback tones"""
        self.tones = {}
        
        # Listening tone - short high beep (user should speak after this)
        self.tones['listening'] = self._sine_tone(1000, 0.2)
        
        # Processing tone - medium beep (system is thinking)
        self.tones['processing'] = self._sine_tone(800, 0.3)
        
        # Success tone - ascending notes (task completed)
        self.tones['success'] = self._chord_tone([523, 659, 784], 0.3)
        
        # Error tone - descending notes (something wrong)
        self.tones['error'] = self._chord_tone([784, 659, 523], 0.3)
        
        # Wake word detected tone - double beep (system ready)
        self.tones['wake_word'] = self._double_beep(1200, 0.2)
        
        # Ready tone - single clear beep (ready for input)
        self.tones['ready'] = self._sine_tone(1200, 0.15)
        
        # Stopping tone - fade out (session ending)
        self.tones['stopping'] = self._fade_out_tone(600, 0.3)
    
    def _sine_tone(self, frequency: float, duration: float) -> np.ndarray:
        """Generate simple sine wave tone"""
        t = np.arange(0, duration, 1/self.sample_rate)
        wave = np.sin(2 * np.pi * frequency * t)
        wave = (wave * 0.3 * self.volume).astype(np.int16)
        return wave
    
    def _chord_tone(self, frequencies: list, duration: float) -> np.ndarray:
        """Generate chord (multiple frequencies at once)"""
        t = np.arange(0, duration, 1/self.sample_rate)
        wave = np.zeros_like(t)
        for freq in frequencies:
            wave += np.sin(2 * np.pi * freq * t)
        wave = wave / len(frequencies)  # Normalize
        wave = (wave * 0.3 * self.volume).astype(np.int16)
        return wave
    
    def _double_beep(self, frequency: float, duration: float) -> np.ndarray:
        """Two quick beeps"""
        beep1 = self._sine_tone(frequency, duration/2)
        beep2 = self._sine_tone(frequency, duration/2)
        silence = np.zeros(int(0.1 * self.sample_rate), dtype=np.int16)
        return np.concatenate([beep1, silence, beep2])
    
    def _fade_out_tone(self, frequency: float, duration: float) -> np.ndarray:
        """Tone that fades out"""
        t = np.arange(0, duration, 1/self.sample_rate)
        envelope = np.linspace(1, 0, len(t))  # Fade from 1 to 0
        wave = np.sin(2 * np.pi * frequency * t) * envelope
        wave = (wave * 0.3 * self.volume).astype(np.int16)
        return wave
    
    async def play_feedback(self, feedback_type: str):
        """
        Play audio feedback (non-blocking)
        
        Types: 'listening', 'processing', 'success', 'error', 'wake_word', 'ready', 'stopping'
        """
        if not self.feedback_enabled or feedback_type not in self.tones:
            return
        
        try:
            tone = self.tones[feedback_type]
            
            if not PYAUDIO_AVAILABLE:
                logger.debug(f"Feedback: {feedback_type} (audio not available)")
                return
            
            # Play asynchronously in a thread
            def play():
                try:
                    p = pyaudio.PyAudio()
                    stream = p.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        output=True
                    )
                    stream.write(tone.tobytes())
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                except Exception as e:
                    logger.warning(f"Failed to play feedback: {e}")
            
            # Run in thread pool so it doesn't block
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, play)
            
        except Exception as e:
            logger.warning(f"Error playing feedback '{feedback_type}': {e}")


class VoiceSessionManager:
    """
    Manages voice-first conversation session
    
    For blind users:
    - One continuous session instead of repeated commands
    - Wake word to start, natural speech to continue
    - Audio feedback for all state changes
    - Emergency stop commands (e.g., "stop listening", "exit")
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize voice session manager"""
        self.config = config or {}
        
        self.listener = ContinuousAudioListener(config)
        self.wake_detector = WakeWordDetector(config=config)
        self.audio_feedback = AccessibleAudioFeedback(config)
        
        self.is_active = False
        self.session_start_time = None
        self.interaction_count = 0
        
        # Audio device management (for AirPods + speaker configuration)
        self.device_manager: Optional[AudioDeviceManager] = None
        self.audio_guardian = None
        if AUDIO_DEVICE_MANAGER_AVAILABLE:
            try:
                self.device_manager = AudioDeviceManager()
                logger.info("Audio device manager initialized")
            except Exception as e:
                logger.warning(f"Could not initialize audio device manager: {e}")
        
        # Callbacks for external handlers
        self.on_voice_detected: Optional[Callable] = None
        self.on_speech_ready: Optional[Callable] = None
        self.on_session_end: Optional[Callable] = None
        
        logger.info("VoiceSessionManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize session (prepare audio)"""
        success = await self.listener.start_listening()
        if success:
            await self.audio_feedback.play_feedback('ready')
            logger.info("Voice session ready")
        return success
    
    async def start_session(self):
        """
        Start voice session
        
        For blind users: System is now listening and ready to respond
        Configures optimal audio: AirPods input + Mac mini Speakers output
        """
        self.is_active = True
        self.session_start_time = time.time()
        self.interaction_count = 0
        
        # Configure optimal audio device setup (AirPods + Speakers)
        if self.device_manager:
            try:
                success, msg = self.device_manager.configure_optimal_audio()
                for line in msg.split('\n'):
                    logger.info(f"Audio config: {line}")
            except Exception as e:
                logger.warning(f"Could not configure audio devices: {e}")
            
            # Start audio guardian to keep speakers as output
            try:
                check_interval = self.config.get('audio_guardian_interval', 5.0)
                self.audio_guardian = await start_audio_guardian(check_interval=check_interval)
                logger.info("Audio guardian started - will maintain speaker output")
            except Exception as e:
                logger.warning(f"Could not start audio guardian: {e}")
        
        await self.audio_feedback.play_feedback('listening')
        logger.info("Voice session started")
    
    async def end_session(self):
        """End voice session and cleanup audio resources"""
        # Stop audio guardian
        if self.audio_guardian:
            try:
                self.audio_guardian.stop()
                logger.info("Audio guardian stopped")
            except Exception as e:
                logger.warning(f"Error stopping audio guardian: {e}")
            self.audio_guardian = None
        
        self.is_active = False
        await self.audio_feedback.play_feedback('stopping')
        await self.listener.stop_listening()
        
        if self.session_start_time:
            duration = time.time() - self.session_start_time
            logger.info(f"Voice session ended (duration: {duration:.1f}s, interactions: {self.interaction_count})")
    
    async def get_user_speech(self, timeout: float = 10.0) -> tuple[Optional[bytes], bool]:
        """
        Get user speech input
        
        For blind users:
        - Automatic detection of when to start/stop recording
        - Audio feedback when ready
        
        Args:
            timeout: Max time to wait
            
        Returns:
            (audio_bytes, is_valid) - audio data and whether it's valid input
        """
        # Play "listening" feedback
        await self.audio_feedback.play_feedback('listening')
        
        # Wait for speech
        audio = await self.listener.get_continuous_audio(timeout)
        
        if audio:
            self.interaction_count += 1
            await self.audio_feedback.play_feedback('processing')
            return audio, True
        else:
            await self.audio_feedback.play_feedback('error')
            return None, False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics for logging"""
        if not self.session_start_time:
            return {}
        
        return {
            'duration': time.time() - self.session_start_time,
            'interactions': self.interaction_count,
            'is_active': self.is_active
        }
    
    def configure_audio_device(self, input_device_name: Optional[str] = None,
                              output_device_name: Optional[str] = None) -> bool:
        """Configure specific audio devices during session
        
        Args:
            input_device_name: Name of input device (e.g., 'AirPods Pro')
            output_device_name: Name of output device (e.g., 'Mac mini Speakers')
            
        Returns:
            True if configuration successful
        """
        if not self.device_manager:
            logger.warning("Audio device manager not available")
            return False
        
        try:
            if input_device_name:
                devices = self.device_manager.list_input_devices()
                for dev in devices:
                    if input_device_name.lower() in dev.name.lower():
                        self.device_manager.set_input_device(dev)
                        logger.info(f"Set input device: {dev.name}")
                        break
            
            if output_device_name:
                devices = self.device_manager.list_output_devices()
                for dev in devices:
                    if output_device_name.lower() in dev.name.lower():
                        self.device_manager.set_output_device(dev)
                        logger.info(f"Set output device: {dev.name}")
                        break
            
            return True
        except Exception as e:
            logger.error(f"Error configuring audio devices: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup session resources"""
        await self.end_session()
        self.listener.cleanup()
        logger.info("Voice session cleaned up")


class VoiceInterruptHandler:
    """
    Handles user interrupts during response playback
    
    For blind users:
    - "Stop" or "Hold on" to pause response
    - "Resume" to continue
    - "Repeat" to hear again
    - "What?" to repeat last response
    """
    
    STOP_COMMANDS = ["stop", "hold on", "pause", "wait", "hold"]
    REPEAT_COMMANDS = ["repeat", "say that again", "what", "what did you say", "huh"]
    RESUME_COMMANDS = ["resume", "continue", "go on", "keep going"]
    EXIT_COMMANDS = ["exit", "quit", "goodbye", "bye", "stop listening", "turn off"]
    
    def __init__(self):
        """Initialize interrupt handler"""
        logger.info("VoiceInterruptHandler initialized")
    
    def classify_command(self, text: str) -> str:
        """
        Classify user input command
        
        Returns: 'stop', 'repeat', 'resume', 'exit', 'speech', or 'unknown'
        """
        text_lower = text.lower().strip()
        
        for cmd in self.STOP_COMMANDS:
            if cmd in text_lower:
                return 'stop'
        
        for cmd in self.REPEAT_COMMANDS:
            if cmd in text_lower:
                return 'repeat'
        
        for cmd in self.RESUME_COMMANDS:
            if cmd in text_lower:
                return 'resume'
        
        for cmd in self.EXIT_COMMANDS:
            if cmd in text_lower:
                return 'exit'
        
        # If not a command, it's regular speech
        return 'speech'
