# GitHub Projects & Resources for macOS Accessibility

**Curated Collection of Relevant Projects and References**

---

## Core Accessibility Frameworks

### 1. AccessKit - Accessibility Infrastructure

**Repository:** https://github.com/AccessKit/accesskit

**Primary Language:** Rust

**Purpose:** Cross-platform accessibility infrastructure for UI toolkits and applications

**Key Features:**
- Data schema for representing accessible UI
- Platform adapters (macOS, Windows, Linux, web)
- Language bindings (Rust, C, C++, Python via bindings)
- Screen reader support

**Relevance to Claude Code:**
- Could be foundation for accessible Claude Code UI layer
- Provides abstraction over platform-specific accessibility APIs
- Active development and maintenance

**macOS-Specific Components:**
- NSAccessibility protocol implementation
- AppKit accessibility adapter
- VoiceOver compatibility layer

**Installation & Integration:**
```bash
# Rust project - add to Cargo.toml or use via FFI
[dependencies]
accesskit = "0.15"

# Or use Python bindings (if available)
pip install accesskit-python  # Check if published
```

---

### 2. PyObjC - Python to Objective-C Bridge

**Repository:** https://github.com/ronaldoussoren/pyobjc

**Documentation:** https://pyobjc.readthedocs.io/

**Status:** Actively Maintained

**Purpose:** Full Python bindings to macOS frameworks

**Accessibility-Specific:**
- `pyobjc-framework-Accessibility` package
- Full AXUIElement bindings
- NSAccessibility protocol access
- All Cocoa accessibility features

**Installation:**
```bash
pip install pyobjc-framework-Accessibility
```

**Core Modules Available:**
- `Accessibility.AXUIElement*` - System-wide element access
- `AppKit.NSAccessibility` - Cocoa accessibility protocols
- `Foundation.NSNotification` - Accessibility event posting

**Code Example:**
```python
from Accessibility import (
    AXUIElementCreateSystemWide,
    AXUIElementCopyAttributeValue,
    AXUIElementCopyActionNames,
    AXUIElementPerformAction
)

# Create system element
system = AXUIElementCreateSystemWide()

# Get focused element
error, focused = AXUIElementCopyAttributeValue(system, "AXFocusedUIElement", None)

# Get available actions
error, actions = AXUIElementCopyActionNames(focused, None)
for action in actions:
    print(f"Available action: {action}")

# Perform action
AXUIElementPerformAction(focused, actions[0])
```

**API Reference:** https://pyobjc.readthedocs.io/en/latest/apinotes/Accessibility.html

---

### 3. Atomacos - GUI Testing via Accessibility

**Repository:** https://daveenguyen.github.io/atomacos/readme.html

**Installation:**
```bash
pip install atomacos
```

**Purpose:** High-level automation of macOS applications via Accessibility API

**Features:**
- Application discovery and control
- UI element querying and interaction
- Window management
- Built on PyObjC (can be extended)

**Example Usage:**
```python
from atomacos import AXClipboard
from atomacos.api import AXUIElementFactory

# Get Mail application
app = AXUIElementFactory.AppWithBundleIdentifier('com.apple.mail')

# Get and iterate windows
for window in app.windows():
    print(f"Window: {window.title()}")

# Get buttons in window
buttons = window.buttons()
for button in buttons:
    if button.title() == "Send":
        button.click()
```

**Relevance:** Can serve as foundation for Claude Code UI automation in accessibility mode

---

## Python Accessibility Libraries

### 4. PyAX - Accessibility Client Library

**Repository:** https://github.com/eeejay/pyax

**Purpose:** Simplified Python client for macOS accessibility

**Features:**
- Accessibility tree dumping
- Attribute inspection
- JSON-formatted tree output

**Key Tools:**
```bash
# Tree command - dump accessibility tree
pyax tree [app-or-window] [--attributes all]
```

**Relevance:** Good for debugging and understanding accessibility tree structure

---

### 5. macapptree - Accessibility Tree Parser

**Repository:** https://github.com/MacPaw/macapptree

**Installation:**
```bash
pip install macapptree
```

**Purpose:** Extract macOS application accessibility tree to JSON

**Features:**
- JSON accessibility tree export
- Screenshot capture with labeled bounding boxes
- Element type classification
- Positional metadata

**Usage Example:**
```python
import macapptree
import json

# Extract tree for Finder application
tree = macapptree.extract_tree_for_app('com.apple.finder')

# Save as JSON
with open('finder_tree.json', 'w') as f:
    json.dump(tree, f, indent=2)

# Tree structure:
# {
#   "accessibility_tree": {
#     "elements": [
#       {
#         "id": "...",
#         "role": "Window",
#         "label": "...",
#         "position": {"x": 100, "y": 100},
#         "size": {"width": 800, "height": 600},
#         "children": [...]
#       }
#     ]
#   }
# }
```

---

### 6. Acacia - Advanced Accessibility API Wrapper

**Repository:** https://github.com/Igalia/acacia

**Language:** C++ with Python bindings

**Purpose:** Thin wrapper around NSAccessibility Protocol with cross-platform support

**Features:**
- Platform-agnostic accessibility API
- Python C++ extension module
- macOS, Windows, Linux support (where applicable)

**Relevance:** Provides abstraction for accessibility across platforms (future expansion)

---

### 7. AXSwift - Swift Accessibility Wrapper

**Repository:** https://github.com/tmandry/AXSwift

**Language:** Swift

**Purpose:** Type-safe Swift interface to AXUIElement

**Features:**
- Swift-native API
- Strongly typed element access
- Error handling improvements

**Note:** If Claude Code is ported to Swift in future

---

### 8. AXorcist - Advanced Swift Accessibility Queries

**Repository:** https://github.com/steipete/AXorcist

**Language:** Swift

**Purpose:** Advanced Swift wrapper with chainable queries and fuzzy matching

**Features:**
- Chainable query builder
- Fuzzy element matching
- State inspection and interaction
- UI modification capabilities

**Philosophy:** "The power of Swift compels your UI to obey!"

```swift
let app = try AXUIElement(application: NSRunningApplication.current)

let buttons = app.descendants
    .filter { $0.role == .button }
    .filter { $0.title?.contains("OK") ?? false }

for button in buttons {
    try button.performAction(.press)
}
```

---

## Screen Reader & Console Accessibility

### 9. TDSR - Terminal Screen Reader

**Repository:** https://github.com/tspivey/tdsr

**Purpose:** Console-based screen reader for macOS and Linux

**Features:**
- Terminal accessibility for command-line applications
- Integration with NVDA on other platforms
- Python extensibility

**Relevance for Claude Code:**
- Could enhance terminal output accessibility
- Particularly useful for complex data display
- Community-maintained

---

## Voice-Controlled Accessibility Projects

### 10. Voice-Guided Navigation for Visually Impaired

**Repository:** https://github.com/ShivamGaurUQ/Voice-Guided-Navigation-for-visually-impaired

**Purpose:** Voice-operated navigation system

**Relevant Patterns:**
- Voice command parsing
- Real-time audio feedback
- Navigation context tracking

---

### 11. BlindSpot - Voice-Controlled Indoor Navigation

**Repository:** https://github.com/praskee/BlindSpot

**Purpose:** Voice-controlled indoor navigation for blind and visually impaired users

**Relevant Patterns:**
- Voice command interface design
- Spatial navigation via voice
- Real-time environment feedback

**Potential Reference:** Patterns for navigating Claude Code codebase via voice

---

### 12. VISION-THE-BLIND - Comprehensive Accessibility Solution

**Repository:** https://github.com/priyanshpsalian/VISION-THE-BLIND

**Purpose:** All-in-one safety and security solution for blind users

**Features:**
- Google Maps navigation by voice
- Currency detection and announcement
- Voice assistance for daily tasks
- Environment description
- Home automation control with face recognition

**Relevant Modules:**
- Voice command architecture
- Real-time feedback systems
- Context-aware assistance

---

### 13. Voice-Based Email for Blind

**Repository:** https://github.com/hacky1997/voice-based-email-for-blind

**Purpose:** Voice-only email interface

**Relevant for Claude Code:**
- Voice command vocabulary design
- Output simplification patterns
- Email-like interaction model (could adapt for file/git operations)

---

## OpenAI & AI-Powered Accessibility

### 14. OpenClaw - Personal AI Assistant

**Repository:** https://github.com/openclaw/openclaw

**Documentation:** https://docs.openclaw.ai/

**Status:** Active (v2026.2.19+)

**Purpose:** Personal AI assistant for macOS/iOS/Android

**Features:**
- Voice wake and talk mode
- macOS app with TCC accessibility permissions
- Headless Mac mini support
- Multi-platform operation

**Relevant Discussion:**
- GitHub Discussion #7700: Running on headless Mac mini with virtual display and audio capture

**Integration Potential:**
- Could augment Claude Code with general AI capabilities
- Reference for voice orchestration architecture
- TCC permission management patterns

**Documentation:**
- macOS Setup: https://docs.openclaw.ai/platforms/macos
- Community Discussion: https://github.com/openclaw/openclaw/discussions

---

## Community Resources & Topic Lists

### GitHub Topics

**blind-people:** https://github.com/topics/blind-people
- Projects specifically designed for blind users

**visually-impaired:** https://github.com/topics/visually-impaired
- Broader accessibility projects

**accessibility:** https://github.com/topics/accessibility
- General accessibility projects (filter by language: Swift)

---

### Curated Lists

**Awesome Accessibility List**
- Repository: https://github.com/lukeslp/awesome-accessibility
- Comprehensive curated list of accessibility resources, tools, and best practices
- Includes tools for multiple platforms

**Mac Accessibility Hub**
- Website: https://aaron-gh.github.io/Mac-Accessibility-Hub/
- Curated resources specifically for macOS accessibility developers

---

## Accessibility Testing & Validation Tools

### Built-in macOS Tools

**1. VoiceOver Utility**
- macOS built-in tool for testing VoiceOver compatibility
- Keyboard: `Command-F5` to enable/disable
- Can run with Claude Code to test accessibility output

**2. Accessibility Inspector**
- Part of Xcode (Additional Tools for Xcode)
- Provides accessibility tree visualization
- Element property inspection
- Real-time accessibility testing

**3. Voice Control**
- macOS 14.1+ feature
- System Settings > Accessibility > Voice Control
- Can test voice command integration

---

## Implementation Pattern Examples

### Pattern 1: PyObjC Accessibility Reading

**File:** Python script using PyObjC to read focused element

```python
#!/usr/bin/env python3
"""
Read information about currently focused UI element
Useful for understanding what Claude Code user is interacting with
"""

from Accessibility import (
    AXUIElementCreateSystemWide,
    AXUIElementCopyAttributeValue,
    AXUIElementCopyActionNames,
)


def get_current_focus():
    system = AXUIElementCreateSystemWide()
    if not system:
        return None

    error, focused = AXUIElementCopyAttributeValue(
        system,
        "AXFocusedUIElement",
        None
    )

    if error != 0 or not focused:
        return None

    # Extract attributes
    result = {}
    for attr in ["AXRole", "AXTitle", "AXValue", "AXDescription"]:
        err, val = AXUIElementCopyAttributeValue(focused, attr, None)
        if err == 0 and val:
            result[attr] = str(val)

    # Get available actions
    err, actions = AXUIElementCopyActionNames(focused, None)
    if err == 0 and actions:
        result["AXActions"] = [str(a) for a in actions]

    return result


if __name__ == "__main__":
    info = get_current_focus()
    if info:
        print("Focused element:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    else:
        print("Could not access focused element")
        print("Check that this script is in Accessibility permissions")
```

---

### Pattern 2: Atomacos Application Control

**File:** Using atomacos for higher-level app automation

```python
#!/usr/bin/env python3
"""
Automate Claude Code application via accessibility
Demonstrates how to navigate and interact
"""

from atomacos.api import AXUIElementFactory
from atomacos import AXClipboard


def interact_with_app(bundle_id="com.anthropic.claudecode"):
    """Interact with Claude Code app"""

    app = AXUIElementFactory.AppWithBundleIdentifier(bundle_id)

    if not app:
        print(f"Could not find app with bundle ID: {bundle_id}")
        return

    print(f"Found application: {app.title()}")

    # Get all windows
    windows = app.windows()
    print(f"Windows: {len(windows)}")

    for window in windows:
        print(f"  Window: {window.title()}")

        # Find text areas
        text_areas = window.textAreas()
        for area in text_areas:
            print(f"    Text area: {area.title()}")
            # Could read or modify text

        # Find buttons
        buttons = window.buttons()
        for button in buttons:
            print(f"    Button: {button.title()}")

    # Interact with clipboard
    text_on_clipboard = AXClipboard.get_clipboard()
    print(f"\nClipboard content: {text_on_clipboard}")

    # Could paste text, click buttons, etc.
```

---

## Development Environment Setup

### Recommended Setup for Accessibility Development

```bash
# 1. Install core dependencies
pip install pyobjc-framework-Accessibility
pip install atomacos
pip install macapptree

# 2. Enable Accessibility for development
# System Settings > Privacy & Security > Accessibility > Add your IDE/terminal

# 3. Enable VoiceOver for testing
# Command-F5 to toggle VoiceOver

# 4. Install testing tools
pip install pytest
pip install pytest-cov

# 5. Set up development environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 6. Run with accessibility testing
python -m pytest tests/accessibility/ -v

# 7. Check accessibility tree during development
python -c "import macapptree; import json; print(json.dumps(macapptree.extract_tree('com.apple.finder'), indent=2))"
```

---

## Testing Checklist Against Real Applications

- [ ] Test with VoiceOver enabled
- [ ] Test with Voice Control enabled
- [ ] Test focused element reading
- [ ] Test action performance
- [ ] Test with screen reader (TDSR or external)
- [ ] Verify announcements appear in VoiceOver rotor
- [ ] Test with real user (blind developer if possible)
- [ ] Measure speech recognition accuracy
- [ ] Check audio feedback clarity
- [ ] Validate command vocabulary

---

## Troubleshooting Guide by Project

### PyObjC Issues

**Problem:** ImportError for Accessibility framework

**Solutions:**
1. Verify installation: `pip install --upgrade pyobjc-framework-Accessibility`
2. Check Python version (3.7+ required)
3. Ensure app has Accessibility permissions

---

### Atomacos Issues

**Problem:** "Could not find application"

**Solutions:**
1. Use correct bundle ID (check: `system_profiler SPApplicationsDataType`)
2. Ensure app is running
3. Check Accessibility permissions for your script

---

### macapptree Issues

**Problem:** JSON extraction fails silently

**Solutions:**
1. Verify app is frontmost
2. Check app has standard UI (some apps use custom rendering)
3. Try simpler app first (Finder, Mail)

---

## Further Reading & Documentation

**Apple Official Documentation:**
- Accessibility API: https://developer.apple.com/documentation/accessibility/
- Speech Framework: https://developer.apple.com/documentation/speech/
- AVFoundation: https://developer.apple.com/documentation/avfoundation/

**WWDC Videos:**
- Build Accessible Apps (WWDC23): https://developer.apple.com/videos/play/wwdc2023/10036/
- Speech Experience (WWDC20): https://developer.apple.com/videos/play/wwdc2020/10022/

**Community:**
- AppleVis Forums: https://www.applevis.com/
- Mac Accessibility Hub: https://aaron-gh.github.io/Mac-Accessibility-Hub/

---

**Last Updated:** February 2026

