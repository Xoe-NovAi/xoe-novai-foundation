# macOS Voice Accessibility Research Package

**Complete Documentation for Implementing Blind User Voice Access to Claude Code**

---

## 📚 Documentation Overview

This research package contains **5 comprehensive documents** totaling ~100KB of implementation guidance, API references, and code examples.

### Start Here

**→ [ACCESSIBILITY_RESEARCH_SUMMARY.md](ACCESSIBILITY_RESEARCH_SUMMARY.md)** (Executive Summary)
- 5-minute overview of findings
- Key recommendations
- Implementation roadmap
- Quick start checklist
- **Read this first**

---

## 📖 Core Documentation (Read in This Order)

### 1. Research Foundation
**[macOS-voice-accessibility-research.md](macOS-voice-accessibility-research.md)** (30KB)

**What you'll learn:**
- Complete macOS Accessibility API reference (AXUIElement, NSAccessibility)
- Speech Recognition Framework (on-device STT)
- AVFoundation audio APIs
- Python library options with examples
- Existing accessibility agent projects
- Recommended architecture
- Implementation phases (Phase 1-4)

**Who should read:** Anyone implementing accessibility features, architects, decision-makers

**Key sections:**
- Mac Native Voice Control & VoiceOver Integration
- Accessibility API versions and requirements
- Python integration (PyObjC, atomacos, pyax, macapptree)
- Accessibility agent options overview
- Integration architecture diagrams

---

### 2. Implementation Guide
**[accessibility-implementation-guide.md](accessibility-implementation-guide.md)** (25KB)

**What you'll learn:**
- Ready-to-use Python code modules
- How to integrate with Claude Code
- Voice command parser (25+ commands)
- Output accessibility filter
- Testing framework
- Deployment checklist

**Who should read:** Developers implementing the feature

**How to use:**
- Copy `AccessibilityOrchestrator` class directly into your codebase
- Use `AccessibleCommandParser` for voice command handling
- Apply `AccessibleOutputFilter` to all output
- Follow integration patterns for Claude Code main loop

**Key sections:**
- Setup guide (pip install, permissions)
- Core modules (complete working code)
- Integration with Claude Code
- Voice command handler
- Testing and validation
- Deployment checklist

---

### 3. GitHub Projects Reference
**[accessibility-github-projects-reference.md](accessibility-github-projects-reference.md)** (16KB)

**What you'll learn:**
- 14 recommended GitHub projects with descriptions
- Links to accessibility frameworks
- Voice-controlled project examples
- Testing tools and resources
- Development environment setup

**Who should read:** Researchers, project leads, those evaluating existing solutions

**Projects covered:**
1. AccessKit - Cross-platform accessibility infrastructure
2. PyObjC - Python-Objective-C bridge
3. Atomacos - GUI testing via accessibility
4. PyAX - Accessibility client library
5. macapptree - Accessibility tree parser
6. TDSR - Terminal screen reader
7. Plus 8 voice-controlled accessibility projects

---

### 4. Detailed API Reference
**[macOS-accessibility-apis-detailed.md](macOS-accessibility-apis-detailed.md)** (26KB)

**What you'll learn:**
- Complete AXUIElement C API reference with Python examples
- NSAccessibility Protocol (Swift/Objective-C code)
- Speech Recognition Framework setup
- AVFoundation audio I/O
- Accessibility notifications
- Permission management (TCC database)
- Best practices and error handling

**Who should read:** Developers implementing specific features, API-level integration

**When to reference:** During implementation when you need specific API details

**Key sections:**
- Core Accessibility API (AXUIElement) - 6 function categories
- NSAccessibility Protocol - Swift/ObjC examples
- Speech Recognition Framework - Complete setup
- AVFoundation audio APIs - Audio capture/synthesis
- Version requirements table
- Error handling guide

---

## 🚀 Quick Reference

### For Quick Setup (15 minutes)
```
1. Read: ACCESSIBILITY_RESEARCH_SUMMARY.md
2. Install: pip install pyobjc-framework-Accessibility
3. Check: System Settings > Privacy & Security > Accessibility
4. Copy: AccessibilityOrchestrator class from implementation-guide.md
5. Test: Run provided example code
```

### For Architecture Planning (1 hour)
```
1. Read: ACCESSIBILITY_RESEARCH_SUMMARY.md
2. Read: Integration Architecture section of macOS-voice-accessibility-research.md
3. Review: Implementation phases in research document
4. Decide: Which tier (Minimal, Standard, Advanced) fits your timeline
```

### For Full Development (8 weeks)
```
Week 1-2: Read all documentation, understand architecture
Week 2-3: Integrate core modules into Claude Code
Week 3-4: Add VoiceOver integration
Week 4-5: Implement output filtering
Week 5-6: Testing and refinement
Week 6-7: Documentation and user guide
Week 7-8: Release and community feedback
```

### For API Implementation (ongoing reference)
```
- Keep macOS-accessibility-apis-detailed.md open while coding
- Reference specific functions and error codes as needed
- Check version requirements before using new APIs
- Follow best practices from implementation guide
```

---

## 🎯 Key Technologies

### macOS Native APIs
- **AXUIElement** - System-wide UI element access (macOS 10.2+)
- **Speech Recognition Framework** - On-device STT (macOS 10.15+)
- **AVFoundation** - Professional audio I/O (macOS 10.14+)
- **Voice Control** - Built-in voice commands (macOS 14.1+)
- **NSAccessibility** - AppKit protocol-based accessibility (macOS 10.10+)

### Python Libraries
- **PyObjC** - Bridge to Objective-C frameworks
- **atomacos** - High-level UI automation
- **macapptree** - Accessibility tree inspection
- **speech_recognition** - STT fallback

### Already Deployed Infrastructure
- **Whisper STT** - localhost:2022 (CoreML+Metal)
- **Kokoro TTS** - localhost:8880 (MPS, 67 voices)
- **Voice Mode MCP** - HTTP server for voice orchestration

---

## 📋 File Locations

```
/Users/buck/Documents/
├── README-ACCESSIBILITY.md                  # This file
├── ACCESSIBILITY_RESEARCH_SUMMARY.md        # START HERE
├── macOS-voice-accessibility-research.md    # Comprehensive reference
├── accessibility-implementation-guide.md    # Code templates & patterns
├── accessibility-github-projects-reference.md # Project links & examples
└── macOS-accessibility-apis-detailed.md     # Detailed API reference
```

All files are in **Markdown format** and can be read in any text editor or Markdown viewer.

---

## ✅ Implementation Checklist

### Initial Setup
- [ ] Read ACCESSIBILITY_RESEARCH_SUMMARY.md
- [ ] Read macOS-voice-accessibility-research.md (sections 1-3)
- [ ] Install dependencies: `pip install pyobjc-framework-Accessibility`
- [ ] Verify VoiceOver access: `Command-F5` to toggle
- [ ] Add Claude Code to Accessibility permissions

### Core Implementation
- [ ] Copy AccessibilityOrchestrator class
- [ ] Copy AccessibleCommandParser class
- [ ] Copy AccessibleOutputFilter class
- [ ] Create voice_accessibility.py module
- [ ] Integrate into Claude Code main loop
- [ ] Add `--accessible` CLI flag

### Testing
- [ ] Unit tests pass (provided in implementation guide)
- [ ] Integration tests pass
- [ ] Test with VoiceOver enabled
- [ ] Test 20+ voice commands
- [ ] Test speech recognition accuracy
- [ ] Test with blind user (if possible)

### Documentation
- [ ] User guide written
- [ ] Troubleshooting guide included
- [ ] Command vocabulary documented
- [ ] Permission requirements clearly stated
- [ ] Known limitations documented

---

## 🔧 Configuration Reference

### Installation
```bash
# Core dependencies
pip install pyobjc-framework-Accessibility

# Optional enhancements
pip install atomacos
pip install macapptree
```

### Environment Variables (for STT vocabulary)
```bash
# ~/.voicemode/voicemode.env
VOICEMODE_STT_PROMPT="You are transcribing programming commands. Common terms: git, Python, function, class, variable, compile, debug, terminal"
```

### System Settings Required
1. System Settings > Privacy & Security > Accessibility
2. Add Claude Code to allowed applications
3. System Settings > Accessibility > Voice Control (optional)
4. Enable VoiceOver: Command-F5

---

## 📞 Support & Troubleshooting

### Common Issues

**"Accessibility API not available"**
- Fix: Add Claude Code to System Settings > Privacy & Security > Accessibility
- Restart Claude Code after granting permissions

**"PyObjC not installed"**
- Fix: `pip install pyobjc-framework-Accessibility`

**"Announcements don't appear in VoiceOver"**
- Fix: Verify VoiceOver is running (Command-F5)
- Check VoiceOver utility notification settings

**"Speech recognition too many errors"**
- Fix: Configure vocabulary bias in ~/.voicemode/voicemode.env
- Adjust speech rate or microphone placement

**See detailed troubleshooting** in accessibility-implementation-guide.md

---

## 🌐 Resources

### Apple Documentation
- [Accessibility Programming Guide](https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/)
- [Accessibility API Reference](https://developer.apple.com/documentation/accessibility/accessibility-api)
- [Speech Framework](https://developer.apple.com/documentation/speech/)

### Community Resources
- [AppleVis Forums](https://www.applevis.com/) - Blind users helping blind users
- [Mac Accessibility Hub](https://aaron-gh.github.io/Mac-Accessibility-Hub/)
- [GitHub: Awesome Accessibility](https://github.com/lukeslp/awesome-accessibility)

### Testing Tools
- **VoiceOver** - Built-in screen reader (Command-F5)
- **Accessibility Inspector** - Part of Xcode Additional Tools
- **Voice Control** - System Settings > Accessibility > Voice Control

---

## 📈 Implementation Tiers

### Tier 1: Minimal (1-2 weeks)
Basic voice input/output with Whisper/Kokoro
- Voice commands: "next", "previous", "run", "help"
- TTS for output
- Error announcements
- No VoiceOver integration

### Tier 2: Standard (3-4 weeks)
Full accessibility with VoiceOver compatibility
- Tier 1 + VoiceOver integration
- Priority-based announcements
- Context-aware hints
- Output simplification

### Tier 3: Advanced (4-6 weeks)
IDE-like accessible interface
- Tier 2 + advanced features
- Voice-driven file/git operations
- Code navigation by voice
- Real-time error feedback

**Recommendation for Claude Code:** Start with Tier 1, expand to Tier 2 after successful testing.

---

## 🎓 Learning Path

### For Project Managers
1. ACCESSIBILITY_RESEARCH_SUMMARY.md - Overall vision
2. Implementation Tiers section - Timeline and scope
3. Success Metrics section - What done looks like

### For Architects
1. macOS-voice-accessibility-research.md - Technology options
2. Integration Architecture section - System design
3. accessibility-github-projects-reference.md - Existing solutions

### For Developers
1. ACCESSIBILITY_RESEARCH_SUMMARY.md - Context
2. accessibility-implementation-guide.md - Code templates
3. macOS-accessibility-apis-detailed.md - API reference

### For QA/Testers
1. ACCESSIBILITY_RESEARCH_SUMMARY.md - Overview
2. Testing section of accessibility-implementation-guide.md
3. Provided test code and validation examples

---

## 🚀 Next Steps

### Immediate (This Week)
- [ ] Read ACCESSIBILITY_RESEARCH_SUMMARY.md
- [ ] Review architecture diagrams in main research document
- [ ] Install PyObjC
- [ ] Verify existing infrastructure (Whisper + Kokoro)

### Short Term (Next 2 Weeks)
- [ ] Read implementation guide
- [ ] Set up development environment
- [ ] Copy core modules into Claude Code
- [ ] Test basic functionality

### Medium Term (Weeks 3-8)
- [ ] Implement full accessibility layer
- [ ] Integrate VoiceOver support
- [ ] Conduct user testing
- [ ] Document and release

---

## 📝 Notes for Implementation

### Key Decisions Made
1. **Use PyObjC** for Python-to-macOS bridge (most complete)
2. **Leverage existing voice infrastructure** (Whisper + Kokoro)
3. **Non-sandboxed deployment** (Accessibility API requirement)
4. **Tier 2 (Standard) recommended** for first release

### Critical Implementation Points
1. **Sandbox is not compatible** - Requires explicit non-sandbox mode
2. **VoiceOver is optional** - App works independently or integrated
3. **Permissions require explicit grant** - Users must manually enable
4. **Speech accuracy depends on vocabulary** - Configure STT prompt

### Success Criteria
- Blind user can perform 80%+ of operations via voice
- <5% speech recognition error rate
- <200ms latency from voice command to audio feedback
- 99% accessibility API uptime

---

## 📄 Document Versions

| Document | Size | Version | Updated |
|----------|------|---------|---------|
| ACCESSIBILITY_RESEARCH_SUMMARY.md | 8KB | 1.0 | Feb 2026 |
| macOS-voice-accessibility-research.md | 30KB | 1.0 | Feb 2026 |
| accessibility-implementation-guide.md | 25KB | 1.0 | Feb 2026 |
| accessibility-github-projects-reference.md | 16KB | 1.0 | Feb 2026 |
| macOS-accessibility-apis-detailed.md | 26KB | 1.0 | Feb 2026 |
| README-ACCESSIBILITY.md | 10KB | 1.0 | Feb 2026 |
| **Total** | **~115KB** | | |

---

## 🎯 Success Indicators

After implementation, you should have:

✅ Blind user can use Claude Code entirely via voice
✅ <5% speech recognition error rate
✅ VoiceOver announcements for all important state changes
✅ Clear, audible error messages
✅ 10+ hour continuous usage without fatigue
✅ Documentation for blind users
✅ Community feedback incorporated

---

## 📞 Questions?

Refer to the appropriate document:
- **"What should we build?"** → ACCESSIBILITY_RESEARCH_SUMMARY.md
- **"How do the APIs work?"** → macOS-voice-accessibility-research.md
- **"Show me code"** → accessibility-implementation-guide.md
- **"What projects exist?"** → accessibility-github-projects-reference.md
- **"What's the API signature?"** → macOS-accessibility-apis-detailed.md

---

**Package Contents Version 1.0**
**Generated:** February 2026
**For:** Claude Code Accessibility Implementation
**Status:** Ready for Development

