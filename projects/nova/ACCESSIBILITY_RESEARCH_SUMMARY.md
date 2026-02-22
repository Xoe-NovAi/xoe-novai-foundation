# macOS Voice Accessibility for Claude Code - Research Summary

**Executive Summary & Implementation Roadmap**

---

## Overview

This research package documents how to implement comprehensive voice-only accessibility for Claude Code on macOS, enabling blind users to control the application entirely through voice input and audio feedback.

**Date:** February 2026
**Total Documentation:** 4 detailed guides (97KB)

---

## Key Findings

### 1. macOS Native APIs are Mature & Accessible

✅ **Accessibility API (AXUIElement)** available since macOS 10.2
- Full system-wide UI element access
- Can read, query, and manipulate any macOS application
- Python access via PyObjC library

✅ **Speech Recognition Framework** (macOS 10.15+)
- On-device, privacy-first speech recognition
- No data sent to Apple servers
- Integrates with existing Whisper/Kokoro infrastructure

✅ **Voice Control** (macOS 14.1+)
- Built-in voice command system
- Custom command creation
- Fully accessible from accessibility APIs

✅ **AVFoundation Audio APIs** (macOS 10.14+)
- Professional audio input/output
- Speech synthesis with customization
- Integrates with VoiceOver settings

### 2. Existing Infrastructure Enables Quick Implementation

- **Whisper STT** (localhost:2022) ✓ Already deployed
- **Kokoro TTS** (localhost:8880) ✓ Already deployed
- **Voice Mode MCP** - Ready for accessibility hooks
- **Mac mini with CoreML+Metal** - Optimal for blind user setup

**Result:** Can build accessibility layer on top of existing voice infrastructure with minimal new dependencies.

### 3. VoiceOver Integration is Achievable

**VoiceOver** (built-in screen reader):
- Fully programmable via Accessibility API
- Can announce custom messages
- Works in parallel with applications
- No conflicts with custom voice output

**Accessibility Notifications:**
- Post announcements that VoiceOver announces
- Monitor VoiceOver events
- Integrate with system accessibility settings

---

## Quick Reference: Three Implementation Tiers

### Tier 1: Minimal (1-2 weeks)

**What:** Basic voice input/output, no VoiceOver integration

**Requires:**
- PyObjC library (50KB)
- Voice command parser
- TTS routing to Kokoro

**Features:**
- Voice commands: "next", "previous", "run", "help"
- Text output to Kokoro TTS
- Error announcements

**Platforms:** Any macOS + Whisper/Kokoro

---

### Tier 2: Standard (3-4 weeks)

**What:** Full accessibility orchestration with VoiceOver compatibility

**Requires:**
- Tier 1 + Accessibility framework bindings
- Priority-based announcement system
- Output simplification filters

**Features:**
- All Tier 1 features
- VoiceOver integration (announcements appear in rotor)
- Context-aware hints
- Error message simplification

**Platforms:** macOS with Accessibility permissions

---

### Tier 3: Advanced (4-6 weeks)

**What:** Fully accessible IDE-like interface

**Requires:**
- Tier 2 + advanced UI automation
- Real-time focus tracking
- Command confirmation system

**Features:**
- All Tier 2 features
- Voice-driven file/git operations
- Code navigation by voice
- Real-time error feedback
- Undo/redo voice support

**Platforms:** macOS with TCC accessibility + microphone permissions

---

## Recommended Tech Stack

### Core Dependencies

```
Python 3.9+
├── pyobjc-framework-Accessibility (macOS APIs)
├── atomacos (High-level automation)
├── macapptree (Accessibility tree inspection)
└── speech_recognition (STT fallback)

Infrastructure (Already Deployed)
├── Whisper (STT, port 2022)
├── Kokoro (TTS, port 8880)
└── Voice Mode MCP (HTTP server)
```

### Optional Enhancement

```
Swift/Objective-C (for native app)
├── Speech.framework (on-device speech recognition)
├── AVFoundation (audio I/O)
└── AppKit (NSAccessibility protocol)
```

---

## File Structure & Documentation

### Document 1: Core Research
**File:** `/Users/buck/Documents/macOS-voice-accessibility-research.md` (30KB)

**Contents:**
- Complete API reference (AXUIElement, NSAccessibility, Speech Framework, AVFoundation)
- macOS version requirements
- Python library options (PyObjC, atomacos, pyax, macapptree)
- Accessibility agent overview (AccessKit, AXSwift, AXorcist, TDSR)
- Recommended architecture for blind user implementation
- Code examples for all major APIs
- Implementation phases (Phase 1-4)

**Use This For:** Understanding the full landscape of available APIs and frameworks

---

### Document 2: Implementation Guide
**File:** `/Users/buck/Documents/accessibility-implementation-guide.md` (25KB)

**Contents:**
- Quick setup guide (pip install, permissions)
- Core accessibility orchestrator module (complete Python code)
- Integration with Claude Code main loop
- Voice command parser (25+ predefined commands)
- Output accessibility filter (ANSI removal, simplification, hints)
- Testing framework
- Deployment checklist
- Troubleshooting guide

**Use This For:** Copy-paste ready Python modules and code templates

---

### Document 3: GitHub Projects Reference
**File:** `/Users/buck/Documents/accessibility-github-projects-reference.md` (16KB)

**Contents:**
- 14 recommended GitHub projects with links
  - AccessKit (cross-platform accessibility infrastructure)
  - PyObjC (Python-Objective-C bridge)
  - Atomacos (high-level UI automation)
  - TDSR (terminal screen reader)
  - Voice-controlled navigation projects
- OpenClaw (general AI assistant with voice)
- Testing tools and IDE setup
- Development environment configuration

**Use This For:** Finding existing projects, inspiration, and evaluation resources

---

### Document 4: Detailed API Reference
**File:** `/Users/buck/Documents/macOS-accessibility-apis-detailed.md` (26KB)

**Contents:**
- **Core Accessibility API (AXUIElement)** - 6 function categories with C/Python examples
  - Element creation
  - Attribute reading/writing
  - Action performance
  - Notifications
  - Error handling
- **NSAccessibility Protocol (AppKit)** - Swift/Objective-C examples
  - Protocol definition
  - Custom component implementation
  - Making views accessible
- **Speech Recognition Framework** - Complete implementation
  - Authorization flow
  - Microphone setup
  - On-device recognition configuration
  - Info.plist requirements
- **AVFoundation Audio APIs** - Audio capture and synthesis
  - Input setup
  - Audio buffer processing
  - Speech synthesis with customization
  - Device selection (macOS limitations)
- **Accessibility Notifications** - Posting custom announcements
- **Version requirements table**
- **Permission management (TCC database)**
- **Best practices & error recovery**

**Use This For:** Deep API reference when implementing features

---

## Critical Implementation Points

### 1. Sandbox Limitation ⚠️

**Issue:** Accessibility API requires non-sandbox mode
- Cannot be distributed via Mac App Store
- Requires manual Accessibility permission grant
- Must be explicit in documentation

**Solution:** Distribute as command-line tool with clear permission instructions

### 2. VoiceOver Compatibility ✓

**Solution:**
- Use Accessibility notifications API
- Check VoiceOver status
- Provide fallback TTS if VoiceOver unavailable
- Never duplicate information VoiceOver already announces

### 3. Microphone Privacy ✓

**Solution:**
- Requires `NSMicrophoneUsageDescription` in Info.plist
- Must explain why microphone access is needed
- Users can revoke in System Settings
- Gracefully handle permission denials

### 4. Speech Recognition Accuracy

**Solution:**
- Configure STT vocabulary bias for code terms
- Pre-loaded in `~/.voicemode/voicemode.env`
- Already configured in your setup (Mark's Mac mini)

---

## Command Vocabulary Recommendation

### Essential Commands

**Navigation:**
- "next" → Move to next item
- "previous" → Go to previous item
- "first" → Jump to beginning
- "last" → Jump to end

**Execution:**
- "run" → Execute command
- "go" → Proceed/confirm
- "stop" → Abort operation

**Help:**
- "help" → Show available commands
- "status" → Report current state
- "what is this" → Describe current item

**Editing:**
- "delete" → Remove current item
- "undo" → Revert last action
- "clear all" → Remove all content

---

## Testing Roadmap

### Phase 1: Unit Testing
```bash
# Test accessibility module
pytest tests/accessibility/ -v
pytest tests/voice_commands/ -v
```

### Phase 2: Integration Testing
```bash
# Test with VoiceOver
# 1. Enable VoiceOver: Command-F5
# 2. Run Claude Code in accessibility mode
# 3. Verify announcements appear in VoiceOver rotor
```

### Phase 3: User Testing
```
# Conduct testing with blind developers
# - Measure speech recognition accuracy
# - Validate command vocabulary
# - Gather feedback on output clarity
# - Identify pain points
```

---

## Architecture Recommendation

### Recommended Approach for Claude Code

**Layer 1: Voice Input**
- Whisper STT (already running on port 2022)
- Speech Recognition Framework (optional fallback)

**Layer 2: Command Processing**
- Voice command parser (25+ recognized commands)
- Context awareness (current operation tracking)

**Layer 3: Accessibility Orchestrator**
- Priority-based announcement system
- VoiceOver integration
- Multiple output channels (TTS, accessibility API, print)

**Layer 4: Output Processing**
- ANSI code removal (for TTS)
- Output simplification for voice
- Context hints generation

**Layer 5: Voice Output**
- Kokoro TTS (already running on port 8880)
- AVSpeechSynthesizer (optional for higher quality)

```
Whisper STT (2022)
        ↓
Command Parser → Accessibility Orchestrator → Output Filter
        ↓                    ↓
    Execute Command    Kokoro TTS (8880)
        ↓                    ↓
    Results ──────────→ Speak to User
```

---

## Success Metrics

By end of implementation, these metrics should be achievable:

✅ **Functionality:**
- User can perform 80%+ of Claude Code operations via voice
- No visual reference required for blind user
- Command confirmation for destructive operations

✅ **Performance:**
- <100ms latency from voice input to command execution
- <200ms latency from command output to audio announcement

✅ **Reliability:**
- <5% speech recognition error rate with configured vocabulary
- 99% accessibility API uptime
- Zero crashes due to accessibility operations

✅ **Usability:**
- 10+ hour hands-free usage without fatigue
- Clear, understandable announcements
- Consistent command vocabulary

---

## Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Research & Setup** | 1 week | Environment setup, dependency verification |
| **Core Module** | 2 weeks | Accessibility orchestrator, voice command parser |
| **VoiceOver Integration** | 1 week | Notification posting, event monitoring |
| **Output Filtering** | 1 week | Simplification, context hints, error formatting |
| **Testing & Refinement** | 2 weeks | Unit tests, integration tests, bug fixes |
| **Documentation & Release** | 1 week | User guide, troubleshooting, release notes |
| **Total** | **8 weeks** | Production-ready accessibility mode |

---

## Quick Start Checklist

### Setup Phase (Day 1-2)

- [ ] Read `macOS-voice-accessibility-research.md` (understand APIs)
- [ ] Install PyObjC: `pip install pyobjc-framework-Accessibility`
- [ ] Add Claude Code to Accessibility permissions (System Settings)
- [ ] Verify existing voice infrastructure (Whisper + Kokoro running)
- [ ] Test basic PyObjC functionality with provided examples

### Development Phase (Week 1)

- [ ] Copy `AccessibilityOrchestrator` class from implementation guide
- [ ] Copy `AccessibleCommandParser` class
- [ ] Copy `AccessibleOutputFilter` class
- [ ] Integrate into Claude Code main loop
- [ ] Test with VoiceOver enabled

### Testing Phase (Week 2)

- [ ] Run unit tests (provided in guide)
- [ ] Test 20+ voice commands
- [ ] Verify VoiceOver announcements
- [ ] Test with actual blind user if possible
- [ ] Measure speech recognition accuracy

### Release Phase (Week 3)

- [ ] Create `--accessible` CLI flag
- [ ] Write user guide
- [ ] Document troubleshooting
- [ ] Release with clear installation instructions

---

## Support Resources

### Documentation
- Apple Accessibility Programming Guide: https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/
- PyObjC Documentation: https://pyobjc.readthedocs.io/
- Speech Framework: https://developer.apple.com/documentation/speech/

### Community
- AppleVis (blind users helping blind users): https://www.applevis.com/
- Mac Accessibility Hub: https://aaron-gh.github.io/Mac-Accessibility-Hub/
- GitHub Topics: blind-people, visually-impaired, accessibility

### Testing
- VoiceOver: Built-in, Command-F5 to toggle
- Accessibility Inspector: In Xcode Additional Tools
- Voice Control: System Settings > Accessibility > Voice Control

---

## Conclusion

The research demonstrates that **implementing blind user voice accessibility for Claude Code is absolutely feasible** using:

1. **Mature macOS APIs** (AXUIElement, Speech Framework)
2. **Existing voice infrastructure** (Whisper + Kokoro already deployed)
3. **Python accessibility libraries** (PyObjC with full API bindings)
4. **Established patterns** (14+ reference GitHub projects)

The estimated implementation time is **8 weeks** for a production-ready solution, with the first functional prototype achievable in **2-3 weeks**.

---

## Next Steps

1. **Review the four documentation files** in `/Users/buck/Documents/`
2. **Choose implementation tier** (Minimal, Standard, or Advanced)
3. **Begin with Phase 1 setup** (dependencies, permissions, testing)
4. **Copy provided code templates** from the implementation guide
5. **Integrate into Claude Code** main loop
6. **Test with VoiceOver** and gather feedback

---

**Generated:** February 2026
**Prepared for:** Mark (Computer Owner) & Blind User Testing
**Project Status:** Ready for Implementation

