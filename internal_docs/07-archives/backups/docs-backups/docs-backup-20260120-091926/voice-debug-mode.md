# Voice Debug Mode Documentation
## Recording and Analysis System for Voice Conversations

**Date:** January 17, 2026
**Version:** v0.1.0
**Status:** Production Ready

---

## 📋 Overview

Xoe-NovAi now includes a comprehensive voice debug mode that records both human and AI voice interactions for later review and learning. This feature enables detailed analysis of voice conversations, performance monitoring, and continuous improvement of the voice interface.

**Key Features:**
- ✅ **Dual Recording**: Records both human input and AI responses
- ✅ **Session-Based Storage**: Organized recordings by conversation sessions
- ✅ **Metadata Tracking**: Comprehensive metadata for each recording
- ✅ **Export Capabilities**: Archive and share debug sessions
- ✅ **Performance Analysis**: Latency, quality, and accuracy metrics
- ✅ **Learning Insights**: Data for continuous voice interface improvement

---

## 🚀 Quick Start

### Enable Voice Debug Mode

**Option 1: Environment Variable**
```bash
export XOE_VOICE_DEBUG=true
export XOE_VOICE_DEBUG_DIR=/tmp/xoe_voice_debug
# Start your voice interface
```

**Option 2: Makefile Target**
```bash
make voice-debug-enable
# Follow prompts to enable recording
```

### Basic Usage

1. **Enable debug mode** using one of the methods above
2. **Start voice conversations** as normal
3. **View recordings** with `make voice-debug-stats`
4. **Export session data** with `make voice-debug-export`

---

## 📁 Recording Structure

### Directory Structure
```
/tmp/xoe_voice_debug/
├── session_abc123def/           # Session directory
│   ├── metadata.json           # Session metadata
│   ├── human_20260117_143052_123456.wav  # Human voice recordings
│   ├── ai_20260117_143055_789012.wav     # AI voice recordings
│   └── ...                     # Additional recordings
└── session_def456ghi/          # Another session
    └── ...
```

### File Naming Convention
```
{type}_{timestamp}_{microseconds}.wav
```

- **type**: `human` or `ai`
- **timestamp**: `YYYYMMDD_HHMMSS` format
- **microseconds**: High-precision timestamp for uniqueness

### Metadata Structure

**Session Metadata (`metadata.json`):**
```json
{
  "session_id": "abc123def",
  "start_time": "2026-01-17T14:30:45.123456",
  "recordings": [
    {
      "type": "human_voice",
      "filename": "human_20260117_143052_123456.wav",
      "timestamp": "2026-01-17T14:30:52.123456",
      "audio_size_bytes": 245760,
      "transcription": "Hello, how are you today?",
      "metadata": {
        "confidence": 0.95,
        "latency_ms": 245.67,
        "provider": "faster_whisper",
        "audio_size_bytes": 245760
      },
      "filepath": "/tmp/xoe_voice_debug/session_abc123def/human_20260117_143052_123456.wav"
    },
    {
      "type": "ai_voice",
      "filename": "ai_20260117_143055_789012.wav",
      "timestamp": "2026-01-17T14:30:55.789012",
      "audio_size_bytes": 189440,
      "text": "I'm doing well, thank you for asking! How can I help you today?",
      "metadata": {
        "latency_ms": 156.23,
        "provider": "piper_onnx",
        "audio_size_bytes": 189440
      },
      "filepath": "/tmp/xoe_voice_debug/session_abc123def/ai_20260117_143055_789012.wav"
    }
  ],
  "stats": {
    "human_voice_recordings": 1,
    "ai_voice_recordings": 1,
    "total_audio_mb": 0.41
  }
}
```

---

## 🎯 Makefile Targets

### Enable/Disable Debug Mode

**`make voice-debug-enable`**
- Enables voice debug recording mode
- Sets environment variables
- Creates recording directory structure
- Provides user confirmation prompts

**`make voice-debug-disable`**
- Disables voice debug recording
- Cleans up environment variables
- Preserves existing recordings

### Monitoring & Statistics

**`make voice-debug-stats`**
- Shows current recording statistics
- Displays session information
- Lists recent recordings
- Shows storage usage

Example output:
```
📊 Voice Debug Recording Statistics
=====================================
debug_mode: true
session_id: abc123def
recording_dir: /tmp/xoe_voice_debug/session_abc123def
stats:
  human_voice_recordings: 3
  ai_voice_recordings: 3
  total_audio_mb: 1.23
total_recordings: 6
recordings: [last 10 recordings shown]
```

### Data Management

**`make voice-debug-export`**
- Exports current session as compressed archive
- Includes all recordings and metadata
- Creates timestamped ZIP file
- Ready for sharing or backup

**`make voice-debug-clean`**
- **WARNING: DESTRUCTIVE OPERATION**
- Permanently deletes all voice recordings
- Requires explicit user confirmation
- Cannot be undone

---

## 🔧 Technical Implementation

### Voice Recording System

**Recording Triggers:**
- **Human Voice**: Recorded after successful STT transcription
- **AI Voice**: Recorded after successful TTS synthesis
- **Metadata**: Captured for both latency and quality metrics

**Audio Format:**
- **Codec**: WAV (uncompressed)
- **Sample Rate**: 22,050 Hz (common for TTS)
- **Channels**: Mono
- **Bit Depth**: 16-bit PCM

**Fallback Handling:**
- If WAV conversion fails, saves as raw binary (.raw)
- Continues operation even if recording fails
- Logs errors without interrupting voice flow

### Session Management

**Session Creation:**
- Automatic session ID generation (8-character unique ID)
- Timestamp-based session directories
- Isolated storage per conversation session

**Metadata Tracking:**
- Real-time JSON metadata updates
- Comprehensive recording statistics
- Error handling and recovery

### Performance Considerations

**Storage Impact:**
- Typical WAV file: ~20-50KB per utterance
- Session with 10 exchanges: ~400KB total
- Compression available via export feature

**Performance Overhead:**
- Minimal latency impact (<1ms per recording)
- Asynchronous file operations
- Non-blocking metadata updates

---

## 📊 Analysis & Learning

### Recorded Data Types

1. **Audio Files**: Raw voice recordings for quality analysis
2. **Transcriptions**: STT results with confidence scores
3. **Synthesis Text**: Original text sent to TTS
4. **Performance Metrics**: Latency, file sizes, provider info
5. **Error Tracking**: Failed recordings and recovery attempts

### Learning Applications

**Voice Quality Improvement:**
- Analyze TTS output quality vs input text
- Identify pronunciation issues
- Optimize voice model selection

**STT Accuracy Enhancement:**
- Review transcription accuracy
- Identify common error patterns
- Improve wake word detection

**Performance Optimization:**
- Monitor latency trends
- Identify bottleneck operations
- Optimize resource usage

**User Experience Insights:**
- Conversation flow analysis
- Response time expectations
- Error recovery patterns

---

## 🔒 Security & Privacy

### Data Protection

**Local Storage Only:**
- All recordings stored locally on user system
- No automatic cloud uploads
- User-controlled data retention

**Access Controls:**
- Directory permissions follow system defaults
- Session isolation prevents cross-contamination
- Export requires explicit user action

**Privacy Considerations:**
- Contains actual voice recordings and conversations
- May include sensitive information
- User responsible for secure storage and deletion

### Best Practices

**Data Retention:**
```bash
# Regular cleanup (example cron job)
0 2 * * * find /tmp/xoe_voice_debug -type f -mtime +30 -delete
```

**Secure Storage:**
```bash
# Encrypt sensitive sessions
openssl enc -aes-256-cbc -salt -in session_data.zip -out session_data.enc
```

**Access Logging:**
- Monitor access to debug directories
- Audit export operations
- Track cleanup activities

---

## 🐛 Troubleshooting

### Common Issues

**"Debug mode not enabled"**
```bash
# Check environment variables
echo $XOE_VOICE_DEBUG
echo $XOE_VOICE_DEBUG_DIR

# Enable debug mode
make voice-debug-enable
```

**"Permission denied"**
```bash
# Fix directory permissions
sudo chown -R $USER:$USER /tmp/xoe_voice_debug
chmod -R 755 /tmp/xoe_voice_debug
```

**"No recordings found"**
```bash
# Check if voice interface is running
make status

# Verify debug mode is active
make voice-debug-stats

# Check directory exists
ls -la /tmp/xoe_voice_debug/
```

**"Disk space full"**
```bash
# Check disk usage
df -h /tmp

# Clean old recordings
make voice-debug-clean

# Move to different location
export XOE_VOICE_DEBUG_DIR=/path/to/larger/disk/xoe_voice_debug
```

### Performance Issues

**High latency during recording:**
- Check disk I/O performance
- Consider moving to faster storage
- Reduce recording frequency if needed

**Large file sizes:**
- Monitor with `make voice-debug-stats`
- Clean regularly with `make voice-debug-clean`
- Compress exports with `make voice-debug-export`

---

## 📈 Advanced Usage

### Custom Recording Directories

```bash
# Use custom directory
export XOE_VOICE_DEBUG_DIR=/custom/path/voice_debug

# Verify
make voice-debug-enable
```

### Automated Analysis Scripts

Create custom analysis scripts:

```python
import json
import os
from pathlib import Path

def analyze_session(session_dir):
    """Analyze a voice debug session."""
    metadata_file = Path(session_dir) / "metadata.json"

    if not metadata_file.exists():
        return None

    with open(metadata_file) as f:
        metadata = json.load(f)

    # Analyze recordings
    stats = metadata['stats']
    recordings = metadata['recordings']

    # Custom analysis logic here
    avg_human_size = sum(r['audio_size_bytes'] for r in recordings if r['type'] == 'human_voice') / stats['human_voice_recordings']
    avg_ai_size = sum(r['audio_size_bytes'] for r in recordings if r['type'] == 'ai_voice') / stats['ai_voice_recordings']

    return {
        'session_id': metadata['session_id'],
        'total_recordings': len(recordings),
        'avg_human_size_kb': avg_human_size / 1024,
        'avg_ai_size_kb': avg_ai_size / 1024,
        'total_size_mb': stats['total_audio_mb']
    }
```

### Integration with Monitoring

Export data for external monitoring:

```bash
# Export and send to monitoring system
make voice-debug-export
curl -X POST -H "Content-Type: application/zip" \
     --data-binary @debug_export.zip \
     http://monitoring.example.com/api/voice-analytics
```

---

## 🎯 Future Enhancements

### Planned Features

**Real-time Analysis:**
- Live quality scoring during conversations
- Automatic issue detection and alerts
- Performance trend monitoring

**Advanced Export:**
- Multiple format support (MP3, OGG)
- Selective export by criteria
- Automated backup to cloud storage

**Integration APIs:**
- REST API for external analysis tools
- Webhook notifications for events
- Database integration for long-term storage

**Machine Learning Integration:**
- Automated quality assessment
- Anomaly detection in recordings
- Predictive maintenance alerts

---

## 📞 Support & Resources

### Getting Help

**Documentation:**
- This document: `docs/voice-debug-mode.md`
- Voice interface docs: `docs/voice-interface.md`
- Makefile reference: `make help`

**Community Support:**
- GitHub Issues: Report bugs and request features
- Discussion Forums: Share analysis techniques
- Wiki: Advanced usage examples

### Contributing

**Bug Reports:**
- Include debug session exports
- Provide system information
- Describe expected vs actual behavior

**Feature Requests:**
- Detail use case and benefits
- Provide implementation suggestions
- Include sample data if applicable

---

## 📝 Changelog

### v0.1.0 (January 17, 2026)
- ✅ Initial implementation of voice debug recording
- ✅ Dual recording (human + AI voice)
- ✅ Session-based organization
- ✅ Comprehensive metadata tracking
- ✅ Export and cleanup functionality
- ✅ Makefile integration
- ✅ Documentation and examples

---

**Voice Debug Mode provides powerful tools for analyzing and improving voice conversations. Use responsibly and ensure proper data handling practices are followed.**

**For questions or issues, please refer to the troubleshooting section or create a GitHub issue.**
