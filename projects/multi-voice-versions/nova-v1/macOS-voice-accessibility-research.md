# macOS Voice Accessibility Research & Integration Guide

**Date:** February 2026
**Purpose:** Comprehensive guide for implementing blind user accessibility in Claude Code through macOS native voice control and VoiceOver integration.

---

## Table of Contents

1. [Mac Native Voice Control & VoiceOver Integration](#mac-native-voice-control--voiceover-integration)
2. [Accessibility Agent Options](#accessibility-agent-options)
3. [Integration Architecture](#integration-architecture)
4. [Implementation Recommendations](#implementation-recommendations)

---

## Mac Native Voice Control & VoiceOver Integration

### macOS APIs Available

#### 1. **Accessibility API (ApplicationServices Framework)**

**Version Requirements:** macOS 10.2+

The core accessibility framework for programmatic interaction with macOS UI:

- **AXUIElement**: Primary C-based API for accessing UI elements system-wide
- **NSAccessibility Protocol**: Objective-C/Swift-based accessibility protocol for AppKit applications
- **Available in macOS 10.10+**: Modern method-based API replacing legacy key-based API

**Key Functions:**
```
AXUIElementCreateSystemWide()              // Get system-wide accessibility element
AXUIElementCreateApplication()             // Create element for specific app
AXUIElementCopyAttributeValue()            // Retrieve element attributes
AXUIElementSetAttributeValue()             // Set element values
AXUIElementPerformAction()                 // Execute element actions
AXUIElementCopyActionNames()               // Get available actions
AXUIElementCopyAttributeNames()            // List attributes
```

**Limitations:**
- Requires app to be in **non-sandbox mode** (cannot be distributed via Mac App Store)
- Accessibility permission prompt only appears for non-sandboxed apps
- Access to `kAXFocusedUIElementAttribute` enables reading currently focused element
- VoiceOver must have access enabled in System Preferences

**Privacy Requirements:**
- macOS requests accessibility permission explicitly
- User must grant permission in: **System Settings > Privacy & Security > Accessibility**
- TCC (Transparent User Consent) database governs permissions

#### 2. **Voice Control (macOS 14.1+)**

**Built-in spoken command system** providing hands-free control:

**Core Capabilities:**
- Spoken commands: "Open Mail", "Scroll down", "Click Done"
- Numeric overlay system for UI element identification
- Custom command creation and configuration
- Dictation with voice text editing
- Available through: **System Settings > Accessibility > Voice Control**

**Programmatic Access:**
- Voice Control generates accessibility events that can be intercepted
- Works through standard Accessibility API
- No direct Swift/Objective-C API for Voice Control configuration
- Voice commands trigger AXAction notifications

#### 3. **Speech Framework (macOS 10.15+)**

**On-device speech recognition for apps:**

```swift
import Speech

// Request microphone permission
SFSpeechRecognizer.requestAuthorization { authStatus in
    // Handle authorization
}

// Create recognizer
let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))

// Recognize audio
let request = SFSpeechAudioBufferRecognitionRequest()
let task = recognizer?.recognitionTask(with: request) { result, error in
    if let result = result {
        let transcript = result.bestTranscription.formattedString
    }
}
```

**Key Features:**
- On-device recognition (data not sent to Apple servers)
- Requires: `NSMicrophoneUsageDescription` in Info.plist
- Requires Siri to be enabled
- `requiresOnDeviceRecognition` property for privacy-first operation
- Available via: `SFSpeechRecognizer` class

**Requirements:**
- macOS 10.15 (Catalina) or later
- Microphone permissions granted
- Siri enabled on device

#### 4. **AVFoundation Audio Frameworks**

**For custom audio input/output handling:**

```swift
import AVFoundation

// Audio input
let audioEngine = AVAudioEngine()
let inputNode = audioEngine.inputNode
let inputFormat = inputNode.outputFormat(forBus: 0)

// Configure voice processing
inputNode.setVoiceProcessingEnabled(true)

// Audio output
let speechSynthesizer = AVSpeechSynthesizer()
let utterance = AVSpeechUtterance(string: "Accessible feedback")
utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
speechSynthesizer.speak(utterance)
```

**macOS-Specific Notes:**
- AVAudioInputNode is fixed to system's default input on macOS
- Cannot programmatically change input device
- Respects VoiceOver settings via `prefersAssistiveTechnologySettings` API
- AVSpeechSynthesizer automatically uses Accessibility Spoken Content settings

**Version Requirements:** macOS 10.14+

#### 5. **VoiceOver Programmatic Control**

**Limited direct API, but can be monitored and augmented:**

**What's Available:**
- Monitor VoiceOver events through Accessibility notifications
- Read focused element via AXUIElement
- Announce custom text through `AXPostNotification` API
- Cannot directly control VoiceOver cursor position
- Cannot inject VoiceOver rotor commands

**Workaround Pattern:**
```objc
// Announce text to assistive technologies
NSAccessibilityPostNotification(element, NSAccessibilityAnnouncementRequestedNotification);

// Monitor VoiceOver focus changes
[[NSNotificationCenter defaultCenter] addObserver:self
    selector:@selector(voiceOverFocusChanged:)
    name:NSAccessibilityUIElementsCreatedNotification
    object:nil];
```

---

### Python Integration Libraries

#### 1. **PyObjC** (Primary Option)

**GitHub:** https://github.com/ronaldoussoren/pyobjc

**Installation:**
```bash
pip install pyobjc
pip install pyobjc-framework-Accessibility
```

**Basic Usage:**
```python
from Accessibility import AXUIElementCreateSystemWide, AXUIElementCopyAttributeValue
from Foundation import kCFNull

# Get system-wide element
system_wide = AXUIElementCreateSystemWide()

# Get focused element
_, focused_element = AXUIElementCopyAttributeValue(
    system_wide,
    "AXFocusedUIElement",
    None
)

# Get focused element title
_, title = AXUIElementCopyAttributeValue(
    focused_element,
    "AXTitle",
    None
)
print(f"Focused element: {title}")
```

**Accessibility Framework Bindings:**
- Full support for ApplicationServices Accessibility API
- Bindings for all AX* functions
- Support for NSAccessibility protocol
- Latest version: See https://pypi.org/project/pyobjc/

#### 2. **atomacos** (Higher-Level Library)

**GitHub:** https://daveenguyen.github.io/atomacos/readme.html

**Purpose:** GUI automation and testing via Accessibility API

**Installation:**
```bash
pip install atomacos
```

**Usage Example:**
```python
from atomacos import AXClipboard
from atomacos.api import AXUIElementFactory

# Get application
app = AXUIElementFactory.AppWithBundleIdentifier('com.apple.mail')

# Get UI elements
windows = app.windows()
for window in windows:
    print(f"Window: {window.title()}")
    buttons = window.buttons()
    for button in buttons:
        print(f"  Button: {button.title()}")
```

#### 3. **pyax** (Lightweight Client Library)

**GitHub:** https://github.com/eeejay/pyax

**Purpose:** Simplified client library for macOS accessibility

**Features:**
- Tree command to dump accessibility hierarchy
- JSON-formatted output
- Attribute filtering
- Screenshot capture with labeled bounding boxes

#### 4. **macapptree** (Accessibility Parser)

**GitHub:** https://github.com/MacPaw/macapptree

**Purpose:** Extract accessibility tree to JSON format

**Installation:**
```bash
pip install macapptree
```

**Usage:**
```python
import macapptree

# Get accessibility tree for application
tree = macapptree.extract_tree('com.apple.mail')
# Returns JSON representation with element types, positions, etc.
```

#### 5. **SpeechRecognition Library**

**For Speech-to-Text:**
```bash
pip install SpeechRecognition
```

```python
import speech_recognition as sr

recognizer = sr.Recognizer()
with sr.Microphone() as source:
    audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
    except sr.UnknownValueError:
        print("Could not understand audio")
```

**Note:** Requires Google Speech Recognition (internet) or offline services

---

## Accessibility Agent Options

### Established Projects & Frameworks

#### 1. **OpenClaw** - Personal AI Assistant

**GitHub:** https://github.com/openclaw/openclaw
**Documentation:** https://docs.openclaw.ai/
**Status:** Active Development (v2026.2.19+)

**Relevant Features for Accessibility:**
- macOS app with TCC (Transparency, Consent, Control) accessibility permissions built-in
- Voice wake and talk mode (always-on speech)
- Multi-platform support (macOS/iOS/Android)
- Headless Mac mini support discussed in community

**Limitations:**
- Designed as general AI assistant, not specialized for blind navigation
- Would require significant customization for accessibility-focused features

**Repository Discussion:**
- Issue #7700: Discussion on running OpenClaw on headless Mac mini (sleep prevention, virtual display, audio capture)

#### 2. **AccessKit** - Accessibility Infrastructure

**GitHub:** https://github.com/AccessKit/accesskit
**Status:** Production-ready framework

**Features:**
- Cross-platform accessibility infrastructure for UI toolkits
- macOS adapter implementing NSAccessibility protocols
- Data schema for rendering accessible UI
- Language bindings (Rust, C)

**Architecture:**
- Tree-based structure where each node represents UI element or element cluster
- Platform-agnostic data schema
- Platform adapters for macOS (AppKit), other platforms

**Relevance:**
- More suitable for toolkit developers than end-user applications
- Could be used as foundation for building accessible UI layer

#### 3. **AXSwift** - Swift Wrapper for Accessibility

**GitHub:** https://github.com/tmandry/AXSwift
**Purpose:** Simplified Swift interface to Accessibility API

**Features:**
- Chainable Swift API wrapping AXUIElement
- Fuzzy element matching
- Query builders for finding elements

#### 4. **AXorcist** - Accessibility Query Builder

**GitHub:** https://github.com/steipete/AXorcist
**Purpose:** Advanced Swift wrapper with fuzzy-matched queries

**Capabilities:**
- Read UI state
- Click and interact with elements
- Inspect any UI
- Chainable query interface

#### 5. **TDSR** - Console Screen Reader

**GitHub:** https://github.com/tspivey/tdsr
**Purpose:** Console-based screen reader for macOS and Linux

**Relevant for:**
- Terminal-based accessibility
- Command-line applications
- Could be integrated with Claude Code CLI

#### 6. **Acacia** - Accessibility API Wrapper

**GitHub:** https://github.com/Igalia/acacia
**Purpose:** Thin C++ wrapper around NSAccessibility Protocol

**Features:**
- Cross-platform accessibility API inspection
- Python C++ extension module support
- Can expose accessibility trees to Python

---

### Voice-Controlled Accessibility Projects (GitHub)

#### 1. **Voice-Guided-Navigation-for-visually-impaired**

**GitHub:** https://github.com/ShivamGaurUQ/Voice-Guided-Navigation-for-visually-impaired

**Features:**
- Voice-operated navigation for visually impaired
- May provide architectural patterns for voice control

#### 2. **BlindSpot** - Voice-Controlled Indoor Navigation

**GitHub:** https://github.com/praskee/BlindSpot

**Description:** Voice-controlled indoor navigation system designed for blind and visually impaired users

**Relevant Patterns:**
- Voice command parsing
- Real-time audio feedback
- Navigation metaphors for blind users

#### 3. **VISION-THE-BLIND** - Comprehensive Solution

**GitHub:** https://github.com/priyanshpsalian/VISION-THE-BLIND

**Features:**
- Google Maps navigation by voice
- Currency detection
- Voice assistance for daily tasks
- Environment description
- Home appliances control with face recognition

#### 4. **Voice-Based Email for Blind**

**GitHub:** https://github.com/hacky1997/voice-based-email-for-blind

**Relevant for:**
- Voice-only email interface patterns
- Command vocabulary for accessibility
- Text-to-speech integration

---

### GitHub Topics & Curated Lists

- **GitHub Topic: blind-people** - https://github.com/topics/blind-people
- **GitHub Topic: visually-impaired** - https://github.com/topics/visually-impaired
- **Awesome Accessibility List** - https://github.com/lukeslp/awesome-accessibility
- **Mac Accessibility Hub** - https://aaron-gh.github.io/Mac-Accessibility-Hub/

---

## Integration Architecture

### Recommended Architecture for Blind User Access

#### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code CLI                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Python Application Layer                             │  │
│  │ - Command processing                                 │  │
│  │ - Output generation                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Voice      │  │ Accessibility│  │ Screen       │
    │ Input      │  │ Feedback     │  │ Reader       │
    │ (STT)      │  │ Orchestrator │  │ Integration  │
    └────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────────────────────────────────────────────────┐
    │        Voice Mode + Kokoro TTS                     │
    │        (Whisper STT + Kokoro on ports 2022/8880)  │
    └────────────────────────────────────────────────────┘
        │
        ▼
    ┌────────────────────────────────────────────────────┐
    │   macOS Native Voice + VoiceOver                   │
    │   - Speech Recognition Framework                  │
    │   - Accessibility API (AXUIElement)               │
    │   - AVFoundation audio                            │
    └────────────────────────────────────────────────────┘
```

#### Components Breakdown

**1. Voice Input Layer**
- Input: Kokoro TTS (port 8880) or Whisper STT (port 2022)
- Alternative: Speech Recognition Framework for on-device recognition
- Process user voice commands and convert to text

**2. Accessibility Feedback Orchestrator** (New Module)
- Receives text output from Claude Code
- Filters for accessibility-relevant information
- Routes to multiple output channels:
  - TTS synthesis
  - VoiceOver announcements
  - Screen reader notifications

**3. VoiceOver Integration Layer**
```python
# pseudo-code architecture
class AccessibilityOrchestrator:
    def __init__(self):
        self.ax_element = AXUIElementCreateSystemWide()
        self.speech_synthesizer = AVSpeechSynthesizer()

    def announce(self, text: str, priority: str = "normal"):
        """
        Announce text via multiple channels:
        - VoiceOver (if running)
        - Direct TTS (if not)
        - Accessibility notifications
        """
        # Post accessibility notification
        self.post_ax_announcement(text)

        # Fallback to direct TTS
        self.synthesize_speech(text)

    def post_ax_announcement(self, text: str):
        """Post to accessibility API"""
        # Uses NSAccessibilityPostNotification
        pass

    def get_screen_state(self) -> dict:
        """Get current VoiceOver context"""
        # Read focused element
        # Get window information
        # Return accessibility tree subset
        pass
```

#### Architecture for Claude Code Integration

**Modifications to Claude Code:**

1. **New Module:** `voice_accessibility.py`
   - Handles all accessibility-specific logic
   - Separate from core CLI functionality
   - Lazy-loaded only when accessibility mode active

2. **Output Hooks:**
   - Intercept all text output before display
   - Filter for accessibility context
   - Route through Accessibility Orchestrator

3. **Command Processing:**
   ```python
   # Pseudocode
   class AccessibleCommandProcessor:
       def process_output(self, output: str, context: OutputContext):
           # Summarize for blind user
           summary = self.create_accessibility_summary(output)

           # Announce key information
           self.orchestrator.announce(summary)

           # Provide navigation hints
           hints = self.generate_context_hints(context)
           if hints:
               self.orchestrator.announce(hints, priority="low")
   ```

---

### Best Practices for Blind User Accessibility

#### 1. **Output Simplification**

For blind users, reduce information verbosity:

```python
# Example: File listing
# Normal output: 26 files, 1.2GB total, last modified...
# Accessible: "26 Python files in src directory"
```

#### 2. **Structured Navigation**

Provide navigation context instead of visual cues:

```
Instead of: "▶ expand folder"
Use: "Press 'e' to expand src folder, contains 12 files"
```

#### 3. **Audio Feedback Priority Levels**

```python
PRIORITY_CRITICAL = 1    # Commands executed, errors
PRIORITY_HIGH = 2        # Important state changes
PRIORITY_NORMAL = 3      # Regular output
PRIORITY_LOW = 4         # Hints, suggestions

# Only announce based on user preference
if priority >= user_attention_threshold:
    orchestrator.announce(message)
```

#### 4. **VoiceOver Compatibility**

- Always use standard macOS accessibility attributes
- Post notifications to accessibility system
- Don't duplicate information that VoiceOver already provides
- Use standard element role descriptions

#### 5. **Speech Input Vocabulary**

Configure Whisper/speech recognition for coding terms:

```yaml
# ~/.voicemode/voicemode.env
VOICEMODE_STT_PROMPT: "You are transcribing programming commands. Common terms: git, Python, function, class, variable, compile, debug, terminal"
```

#### 6. **Context-Aware Announcements**

```python
class ContextAwareAnnouncer:
    def announce_file_operation(self, op: str, filename: str):
        """Example: announce_file_operation('read', 'main.py')"""

        # Announce based on context
        if op == "read":
            message = f"Reading {filename}"
        elif op == "modified":
            message = f"Modified {filename}, unsaved"

        # Add navigation hint
        message += ". Press 'n' for next, 'p' for previous file"

        self.orchestrator.announce(message)
```

---

## Implementation Recommendations

### Phase 1: Foundation (2-3 weeks)

**Objective:** Build core accessibility orchestration layer

**Tasks:**
1. Create `accessibility_module.py` with PyObjC integration
   - Initialize accessibility framework
   - Set up VoiceOver event monitoring
   - Implement announcement system

2. Implement `AccessibilityOrchestrator` class
   - Hook into Voice Mode infrastructure (Whisper + Kokoro)
   - Route outputs through accessibility APIs
   - Handle priority levels

3. Add configuration options
   ```ini
   [accessibility]
   mode = voice_only
   verbosity = minimal
   announcement_priority = critical,high
   voiceover_enabled = auto  # auto-detect
   ```

4. Test with VoiceOver
   - Verify announcements appear in VoiceOver rotor
   - Test priority filtering
   - Validate with actual VoiceOver users

**Technologies:**
- PyObjC + Accessibility framework bindings
- Current: Whisper + Kokoro infrastructure
- Optional: Speech Recognition Framework for future enhancement

### Phase 2: Command Enhancement (2 weeks)

**Objective:** Optimize voice commands for accessibility

**Tasks:**
1. Create accessible command vocabulary
   - Standard commands: "next", "previous", "help", "read"
   - Context-specific: "expand", "collapse", "show errors"

2. Implement context awareness
   - Track current operation (editing, browsing, running)
   - Adjust announcements based on context

3. Add feedback validation
   - Ask user to confirm critical operations
   - Provide undo hints

**Deliverable:**
- Documented command set for blind users
- Voice-optimized output format examples

### Phase 3: Integration & Testing (2 weeks)

**Objective:** Full Claude Code + accessibility integration

**Tasks:**
1. Integrate accessibility orchestrator into Claude Code main loop
2. Add `--accessible` / `--voice-only` flags
3. Create accessibility mode documentation
4. Conduct user testing with blind developers/testers

**Success Metrics:**
- User can perform core operations via voice only
- Less than 2% speech recognition error rate with codebase vocabulary
- All critical feedback reaches user audibly

### Phase 4: Enhancement (Ongoing)

**Future considerations:**
- Integration with OpenAI API for higher-quality TTS (when available)
- Support for custom screen readers (TDSR integration)
- Accessibility API for third-party screen readers
- Real-time code error narration
- Voice-driven debugging assistant

---

## Specific macOS APIs Summary

| API/Framework | Version | Purpose | Python Support | Sandbox-Safe |
|---|---|---|---|---|
| **Accessibility (AXUIElement)** | macOS 10.2+ | UI element access | PyObjC | No |
| **NSAccessibility Protocol** | macOS 10.10+ | AppKit accessibility | PyObjC | No |
| **Speech Recognition** | macOS 10.15+ | On-device STT | Limited | Yes |
| **AVFoundation** | macOS 10.14+ | Audio I/O | PyObjC | Yes |
| **Voice Control** | macOS 14.1+ | Voice commands | Indirect | Yes |
| **AVSpeechSynthesizer** | macOS 10.14+ | TTS | PyObjC | Yes |

---

## Code Examples

### Python: Reading Focused Element

```python
#!/usr/bin/env python3
import PyObjC
from Accessibility import (
    AXUIElementCreateSystemWide,
    AXUIElementCopyAttributeValue
)

def get_focused_element_info():
    """Get information about currently focused UI element"""

    # Create system-wide element
    system_wide = AXUIElementCreateSystemWide()

    if not system_wide:
        print("Accessibility API not available")
        return None

    # Get focused element
    error_code, focused = AXUIElementCopyAttributeValue(
        system_wide,
        "AXFocusedUIElement",
        None
    )

    if error_code != 0 or not focused:
        print(f"Could not get focused element (error: {error_code})")
        return None

    # Extract useful information
    info = {}

    attributes_to_read = [
        "AXTitle",
        "AXDescription",
        "AXRole",
        "AXRoleDescription",
        "AXValue"
    ]

    for attr in attributes_to_read:
        error_code, value = AXUIElementCopyAttributeValue(
            focused,
            attr,
            None
        )
        if error_code == 0 and value:
            info[attr] = value

    return info

if __name__ == "__main__":
    info = get_focused_element_info()
    if info:
        print("Focused element info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
```

### Python: Announce Text via Accessibility

```python
#!/usr/bin/env python3
from Foundation import NSNotificationCenter, NSNotification
from Accessibility import AXUIElementCreateSystemWide

def announce_to_accessibility(text: str):
    """
    Announce text to accessibility APIs (VoiceOver, etc)
    """
    try:
        # Post accessibility announcement notification
        notification_center = NSNotificationCenter.defaultCenter()

        # Create notification with text as userInfo
        notification = NSNotification.notificationWithName_object_userInfo_(
            "AXAnnouncementRequested",
            None,
            {"AXAnnouncementText": text}
        )

        notification_center.postNotification_(notification)

        print(f"Announced: {text}")

    except Exception as e:
        print(f"Could not post announcement: {e}")
        # Fallback to print
        print(f"[Accessibility]: {text}")

if __name__ == "__main__":
    announce_to_accessibility("Hello from Claude Code")
    announce_to_accessibility("Python environment initialized")
```

### Python: Voice Command Parser

```python
#!/usr/bin/env python3
import re
from enum import Enum
from typing import Optional, Tuple

class CommandType(Enum):
    NAVIGATE = "navigate"
    EDIT = "edit"
    EXECUTE = "execute"
    HELP = "help"
    UNDO = "undo"
    UNKNOWN = "unknown"

class AccessibleCommandParser:
    """Parse voice commands for accessibility mode"""

    # Command patterns (regex)
    PATTERNS = {
        CommandType.NAVIGATE: [
            r"(next|move to next)",
            r"(previous|move to previous|go back)",
            r"(first|go to start)",
            r"(last|go to end)",
        ],
        CommandType.EDIT: [
            r"delete (this|line|word)",
            r"change (this|line|text) to (.+)",
            r"insert (.+) (here|before this|after this)",
        ],
        CommandType.EXECUTE: [
            r"run( this)?( command)?",
            r"execute",
            r"go( ahead)?",
        ],
        CommandType.HELP: [
            r"help( me)?",
            r"what can i do",
            r"(what|show) (commands|options)",
        ],
        CommandType.UNDO: [
            r"(undo|take back|revert)",
        ],
    }

    def parse(self, voice_text: str) -> Tuple[CommandType, Optional[str]]:
        """
        Parse voice command and return (command_type, extracted_data)
        """
        voice_text = voice_text.lower().strip()

        # Try each command type
        for cmd_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, voice_text)
                if match:
                    # Extract any captured groups
                    data = match.groups()[-1] if match.groups() else None
                    return (cmd_type, data)

        return (CommandType.UNKNOWN, voice_text)

    def handle_command(self, voice_text: str) -> str:
        """Handle voice command and return response"""
        cmd_type, data = self.parse(voice_text)

        responses = {
            CommandType.NAVIGATE: f"Navigating to {data or 'next item'}",
            CommandType.EDIT: f"Editing: {data}",
            CommandType.EXECUTE: "Executing command",
            CommandType.HELP: "Available commands: next, previous, delete, run, help",
            CommandType.UNDO: "Last action undone",
            CommandType.UNKNOWN: f"Did not understand: {data}",
        }

        return responses.get(cmd_type, "Command processed")

if __name__ == "__main__":
    parser = AccessibleCommandParser()

    test_commands = [
        "next",
        "delete this line",
        "show commands",
        "change this to hello",
        "run this",
    ]

    for cmd in test_commands:
        cmd_type, data = parser.parse(cmd)
        response = parser.handle_command(cmd)
        print(f"Input: '{cmd}'")
        print(f"  Type: {cmd_type.value}, Data: {data}")
        print(f"  Response: {response}\n")
```

---

## Recommended Libraries & Frameworks Summary

### Essential
- **PyObjC**: Primary bridge to macOS Accessibility API
- **Whisper + Kokoro**: Already deployed STT/TTS infrastructure
- **Speech Recognition Framework**: Built-in macOS API (macOS 10.15+)

### Optional Enhancement
- **atomacos**: Higher-level automation framework
- **AccessKit**: For building accessible UI components
- **AXorcist/AXSwift**: Swift alternatives (if porting to Swift)

### Reference/Community
- **TDSR**: Console screen reader (for terminal augmentation)
- **Voice-Guided-Navigation projects**: Pattern inspiration
- **Acacia**: Advanced accessibility tree inspection

---

## Testing Checklist for Blind User Implementation

- [ ] VoiceOver announces all critical state changes
- [ ] Voice commands recognized with <5% error rate
- [ ] Announcements use consistent, predictable language
- [ ] Navigation possible via voice only (no visual reference needed)
- [ ] Error messages clear and actionable via audio alone
- [ ] Command confirmation provided for destructive operations
- [ ] Interrupt capability for long announcements
- [ ] Context switching clear to blind user
- [ ] No reliance on position/coordinates in announcements
- [ ] File/symbol names pronounced clearly by TTS

---

## References & Resources

**Apple Developer Documentation:**
- [Accessibility API](https://developer.apple.com/documentation/accessibility/accessibility-api)
- [NSAccessibility Protocol](https://developer.apple.com/documentation/appkit/nsaccessibility)
- [Speech Framework](https://developer.apple.com/documentation/speech)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [Accessibility Programming Guide](https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/)

**Community Resources:**
- [AppleVis Forums](https://www.applevis.com) - Blind and low vision user community
- [Mac Accessibility Hub](https://aaron-gh.github.io/Mac-Accessibility-Hub/)

**Video Resources (WWDC):**
- [Build Accessible Apps with SwiftUI and UIKit - WWDC23](https://developer.apple.com/videos/play/wwdc2023/10036/)
- [Create a Seamless Speech Experience - WWDC20](https://developer.apple.com/videos/play/wwdc2020/10022/)
- [Advances in Speech Recognition - WWDC19](https://developer.apple.com/videos/play/wwdc2019/256/)

---

**Document Version:** 1.0
**Last Updated:** February 2026
**Author:** Claude Code Research
