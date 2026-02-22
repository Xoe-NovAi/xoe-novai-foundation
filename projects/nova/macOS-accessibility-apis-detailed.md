# macOS Native Accessibility APIs - Detailed Reference

**Complete API Documentation with Code Examples**

---

## Table of Contents

1. [Core Accessibility API (AXUIElement)](#core-accessibility-api-axuielement)
2. [NSAccessibility Protocol (AppKit)](#nsaccessibility-protocol-appkit)
3. [Speech Recognition Framework](#speech-recognition-framework)
4. [AVFoundation Audio APIs](#avfoundation-audio-apis)
5. [Accessibility Notifications](#accessibility-notifications)
6. [Version Requirements & Compatibility](#version-requirements--compatibility)

---

## Core Accessibility API (AXUIElement)

### Framework
- **Framework:** ApplicationServices.framework
- **Header:** `<ApplicationServices/ApplicationServices.h>`
- **Language:** C/Objective-C
- **Minimum macOS:** 10.2+
- **Sandbox:** Not compatible (requires disabled sandbox)

### Primary Types

```c
// Opaque types
typedef struct __AXUIElement *AXUIElementRef;

// Errors
typedef UInt32 AXError;

// Attributes (strings)
#define kAXRoleAttribute "AXRole"
#define kAXFocusedUIElementAttribute "AXFocusedUIElement"
#define kAXTitleAttribute "AXTitle"
#define kAXDescriptionAttribute "AXDescription"
#define kAXValueAttribute "AXValue"
#define kAXEnabledAttribute "AXEnabled"
#define kAXRoleDescriptionAttribute "AXRoleDescription"
#define kAXParentAttribute "AXParent"
#define kAXChildrenAttribute "AXChildren"
#define kAXVisibleChildrenAttribute "AXVisibleChildren"
#define kAXWindowAttribute "AXWindow"
```

### Core Functions

#### 1. Create Elements

```c
// Create system-wide element (for global focus access)
AXUIElementRef AXUIElementCreateSystemWide(void);

// Create element for specific application
AXUIElementRef AXUIElementCreateApplication(pid_t pid);

// Copy element from another element
AXError AXUIElementCopyElementAtPosition(
    AXUIElementRef application,
    float x,
    float y,
    AXUIElementRef *element
);
```

**Python (PyObjC) Examples:**

```python
from Accessibility import AXUIElementCreateSystemWide, AXUIElementCreateApplication
from os import getpid

# System-wide element
system_wide = AXUIElementCreateSystemWide()

# Application element for Mail
# First get Mail's PID
from subprocess import check_output
import json

pid_str = check_output(['pgrep', '-f', 'com.apple.mail']).decode()
mail_pid = int(pid_str.strip())

mail_element = AXUIElementCreateApplication(mail_pid)
```

#### 2. Read Attributes

```c
// Get attribute value
AXError AXUIElementCopyAttributeValue(
    AXUIElementRef element,
    CFStringRef attribute,
    void *value
);

// Get attribute names
AXError AXUIElementCopyAttributeNames(
    AXUIElementRef element,
    CFArrayRef *names
);

// Get attribute by name and index
AXError AXUIElementCopyAttributeValues(
    AXUIElementRef element,
    CFStringRef attribute,
    CFIndex maxValues,
    CFArrayRef *values
);

// Check if attribute is writable
AXError AXUIElementIsAttributeSettable(
    AXUIElementRef element,
    CFStringRef attribute,
    Boolean *settable
);

// Get attribute's parameter type
AXError AXUIElementCopyParameterizedAttributeNames(
    AXUIElementRef element,
    CFArrayRef *names
);
```

**Python Example: Get All Attributes**

```python
from Accessibility import (
    AXUIElementCreateSystemWide,
    AXUIElementCopyAttributeValue,
    AXUIElementCopyAttributeNames,
)

def read_element_attributes(element):
    """Read all available attributes from element"""

    # Get list of available attributes
    error_code, attr_names = AXUIElementCopyAttributeNames(element, None)

    if error_code != 0 or not attr_names:
        print(f"Error: {error_code}")
        return {}

    attributes = {}

    for attr_name in attr_names:
        error_code, value = AXUIElementCopyAttributeValue(element, attr_name, None)

        if error_code == 0 and value:
            attributes[attr_name] = value

    return attributes


# Usage
system_wide = AXUIElementCreateSystemWide()
_, focused = AXUIElementCopyAttributeValue(
    system_wide,
    "AXFocusedUIElement",
    None
)

attrs = read_element_attributes(focused)
for attr_name, value in attrs.items():
    print(f"{attr_name}: {value}")
```

#### 3. Perform Actions

```c
// Get available actions
AXError AXUIElementCopyActionNames(
    AXUIElementRef element,
    CFArrayRef *names
);

// Perform action
AXError AXUIElementPerformAction(
    AXUIElementRef element,
    CFStringRef action
);

// Get action description
AXError AXUIElementCopyActionDescription(
    AXUIElementRef element,
    CFStringRef action,
    CFStringRef *description
);
```

**Common Actions:**

```
"AXPress"           // Button click, checkbox toggle
"AXConfirm"         // Confirm dialog
"AXCancel"          // Cancel dialog
"AXRaise"           // Bring window to front
"AXShowMenu"        // Show menu
"AXShowDefaultUI"   // Show main UI
"AXIncrement"       // Increase value
"AXDecrement"       // Decrease value
"AXScrollUp"        // Scroll up
"AXScrollDown"      // Scroll down
"AXScrollLeft"      // Scroll left
"AXScrollRight"     // Scroll right
"AXScrollTopLeft"   // Scroll to top-left
"AXScrollBottomRight" // Scroll to bottom-right
```

**Python Example: Perform Action**

```python
from Accessibility import (
    AXUIElementCopyActionNames,
    AXUIElementPerformAction,
    AXUIElementCopyActionDescription
)

def perform_button_click(button_element):
    """Click a button element"""

    # Get available actions
    error, actions = AXUIElementCopyActionNames(button_element, None)

    if error != 0 or not actions:
        print("No actions available")
        return False

    # Look for Press action
    if "AXPress" in actions:
        error = AXUIElementPerformAction(button_element, "AXPress")
        return error == 0

    # Fallback: try first action
    if actions:
        error = AXUIElementPerformAction(button_element, actions[0])
        return error == 0

    return False
```

#### 4. Set Attributes (Write)

```c
// Set attribute value
AXError AXUIElementSetAttributeValue(
    AXUIElementRef element,
    CFStringRef attribute,
    void *value
);
```

**Example: Set Text Value**

```python
from Accessibility import (
    AXUIElementSetAttributeValue,
    AXUIElementCopyAttributeValue,
)

def set_text_field_value(text_field_element, text):
    """Set value of text field"""

    # First check if writable
    error, is_writable = AXUIElementIsAttributeSettable(
        text_field_element,
        "AXValue",
        None
    )

    if error != 0 or not is_writable:
        return False

    # Set value
    error = AXUIElementSetAttributeValue(
        text_field_element,
        "AXValue",
        text
    )

    return error == 0
```

#### 5. Notifications & Observation

```c
// Register for notifications
AXError AXObserverCreate(
    pid_t application,
    AXObserverCallback callback,
    AXObserverRef *outObserver
);

// Add notification
AXError AXObserverAddNotification(
    AXObserverRef observer,
    AXUIElementRef element,
    CFStringRef notification,
    void *refcon
);

// Remove notification
AXError AXObserverRemoveNotification(
    AXObserverRef observer,
    AXUIElementRef element,
    CFStringRef notification
);

// Run observer
void AXObserverGetRunLoopSource(
    AXObserverRef observer
);
```

**Common Notifications:**

```
"AXUIElementDestroyed"
"AXFocused"
"AXTitleChanged"
"AXValueChanged"
"AXWindowCreated"
"AXWindowMoved"
"AXWindowResized"
"AXMenuOpened"
"AXMenuClosed"
"AXRowCountChanged"
"AXSelectedChildrenChanged"
```

**Python Example: Observe Elements**

```python
from Accessibility import AXObserverCreate, AXObserverAddNotification
from Foundation import NSRunLoop, NSRunLoopCommonModes
import os

def setup_observer(pid, callback):
    """Set up observer for application"""

    try:
        # Create observer
        error, observer = AXObserverCreate(pid, callback, None)

        if error != 0:
            print(f"Could not create observer: {error}")
            return None

        # Get run loop source
        from Accessibility import AXObserverGetRunLoopSource

        run_loop_source = AXObserverGetRunLoopSource(observer)

        # Add to run loop
        run_loop = NSRunLoop.currentRunLoop()
        run_loop.addInput_forMode_(run_loop_source, NSRunLoopCommonModes)

        return observer

    except Exception as e:
        print(f"Error setting up observer: {e}")
        return None
```

#### 6. Error Handling

```c
// AXError return values:
#define kAXErrorSuccess           0
#define kAXErrorFailure           1
#define kAXErrorIllegalArgument   2
#define kAXErrorInvalidUIElement  3
#define kAXErrorInvalidUIElementObserver 4
#define kAXErrorCannotComplete    5
#define kAXErrorAttributeUnsupported 6
#define kAXErrorActionUnsupported 7
#define kAXErrorNotificationUnsupported 8
#define kAXErrorNotImplemented    9
#define kAXErrorNotificationAlreadyRegistered 10
#define kAXErrorNotificationNotRegistered 11
#define kAXErrorAPIDisabledForApp 12
#define kAXErrorNoValue           13
#define kAXErrorParameterizedAttributeUnsupported 14
#define kAXErrorNotificationDeliveredWithDelay 15
```

**Python Error Handler:**

```python
def check_ax_error(error_code, operation_name="Operation"):
    """Check and report accessibility API error"""

    error_map = {
        0: "Success",
        1: "Failure",
        2: "Illegal argument",
        3: "Invalid UI element",
        5: "Cannot complete",
        6: "Attribute unsupported",
        12: "API disabled for application",
        13: "No value",
    }

    error_message = error_map.get(error_code, f"Unknown error {error_code}")

    if error_code != 0:
        print(f"[ERROR] {operation_name}: {error_message}")
        return False

    return True
```

---

## NSAccessibility Protocol (AppKit)

### Framework
- **Framework:** AppKit.framework
- **Header:** `<AppKit/NSAccessibility.h>`
- **Language:** Objective-C/Swift
- **Minimum macOS:** 10.10+ (protocol-based API)
- **Sandbox:** Partial support (depends on implementation)

### Protocol Definition

```objc
@protocol NSAccessibility

// Role and role description
@property (nonatomic, readonly) NSString *accessibilityRole;
@property (nonatomic, readonly) NSString *accessibilityRoleDescription;

// Attributes
@property (nonatomic, readonly) NSString *accessibilityTitle;
@property (nonatomic, readonly) NSString *accessibilityDescription;
@property (nonatomic, readonly) id accessibilityValue;
@property (nonatomic, readonly) NSString *accessibilityLabel;

// Parent and children
@property (nonatomic, readonly, strong) id accessibilityParent;
@property (nonatomic, readonly) NSArray *accessibilityChildren;
@property (nonatomic, readonly) NSArray *accessibilityVisibleChildren;

// Frame and position
@property (nonatomic, readonly) NSRect accessibilityFrame;
@property (nonatomic, readonly) BOOL accessibilityIsIgnored;

// Custom attributes and actions
- (NSArray *)accessibilityAttributeNames;
- (id)accessibilityAttributeValue:(NSString *)attribute;
- (BOOL)accessibilityIsAttributeSettable:(NSString *)attribute;
- (void)accessibilitySetValue:(id)value forAttribute:(NSString *)attribute;

- (NSArray *)accessibilityActionNames;
- (NSString *)accessibilityActionDescription:(NSString *)action;
- (void)accessibilityPerformAction:(NSString *)action;

@end
```

### Swift Example: Custom Accessible Component

```swift
import AppKit

class AccessibleCustomButton: NSButton {

    override var accessibilityRole: NSAccessibility.Role? {
        get { .button }
        set { }
    }

    override var accessibilityRoleDescription: String? {
        get {
            let title = self.title
            return "Custom button: \(title)"
        }
        set { }
    }

    override var accessibilityTitle: String? {
        get { self.title }
        set { self.title = newValue ?? "" }
    }

    override var accessibilityLabel: String? {
        get { self.toolTip }
        set { self.toolTip = newValue }
    }

    override func accessibilityActionNames() -> [NSAccessibility.Action] {
        return [.press]
    }

    override func accessibilityActionDescription(_ action: NSAccessibility.Action) -> String? {
        if action == .press {
            return "Click the button"
        }
        return super.accessibilityActionDescription(action)
    }

    override func accessibilityPerformAction(_ action: NSAccessibility.Action) {
        if action == .press {
            self.performClick(self)
        } else {
            super.accessibilityPerformAction(action)
        }
    }
}
```

### Objective-C Example: Making View Accessible

```objc
@implementation MyCustomView

- (NSString *)accessibilityRole {
    return NSAccessibilityGroupRole;
}

- (NSString *)accessibilityRoleDescription {
    return @"Custom view with interactive content";
}

- (NSArray *)accessibilityChildren {
    // Return array of accessible child elements
    return @[self.titleLabel, self.submitButton];
}

- (void)accessibilityPerformAction:(NSString *)action {
    if ([action isEqualToString:NSAccessibilityPressAction]) {
        [self handleUserInteraction];
    }
}

- (void)postAccessibilityNotification:(NSString *)notification
                                value:(id)value {
    // Announce to VoiceOver and other accessibility clients
    NSAccessibilityPostNotification(self, notification);

    if (value) {
        NSAccessibilityPostNotificationWithUserInfo(
            self,
            notification,
            @{NSAccessibilityAnnouncementUIElementAttribute: value}
        );
    }
}

@end
```

---

## Speech Recognition Framework

### Framework
- **Framework:** Speech.framework
- **Language:** Swift / Objective-C
- **Minimum macOS:** 10.15 (Catalina)
- **Sandbox:** Supported
- **Requirements:** Microphone permission, Siri enabled

### Core Classes

#### SFSpeechRecognizer

```swift
import Speech

class SpeechRecognitionManager {

    let recognizer = SFSpeechRecognizer()
    var recognitionTask: SFSpeechRecognitionTask?

    // Request authorization
    static func requestAuthorization() {
        SFSpeechRecognizer.requestAuthorization { authStatus in
            switch authStatus {
            case .authorized:
                print("Speech recognition authorized")
            case .denied:
                print("User denied speech recognition")
            case .restricted:
                print("Speech recognition restricted")
            case .notDetermined:
                print("Speech recognition not yet authorized")
            @unknown default:
                print("Unknown authorization status")
            }
        }
    }

    // Check if speech recognition is available
    func isSpeechRecognitionAvailable() -> Bool {
        return SFSpeechRecognizer.authorizationStatus() == .authorized
    }

    // Recognize from microphone
    func startListening(onResult: @escaping (String?) -> Void) throws {
        guard let recognizer = recognizer else {
            throw SpeechRecognitionError.unavailable
        }

        guard recognizer.isAvailable else {
            throw SpeechRecognitionError.unavailable
        }

        let audioEngine = AVAudioEngine()
        let inputNode = audioEngine.inputNode
        let audioFormat = inputNode.outputFormat(forBus: 0)!

        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        request.requiresOnDeviceRecognition = true  // Privacy-first

        // Attach input to request
        inputNode.installTap(
            onBus: 0,
            bufferSize: 1024,
            format: audioFormat
        ) { buffer, _ in
            request.append(buffer)
        }

        audioEngine.prepare()
        try audioEngine.start()

        recognitionTask = recognizer.recognitionTask(
            with: request
        ) { result, error in
            var isFinal = false

            if let result = result {
                let transcription = result.bestTranscription.formattedString
                isFinal = result.isFinal
                onResult(transcription)
            }

            if error != nil || isFinal {
                audioEngine.stop()
                inputNode.removeTap(onBus: 0)
                request.endAudio()
                self.recognitionTask = nil
            }
        }
    }

    enum SpeechRecognitionError: Error {
        case unavailable
    }
}
```

### Info.plist Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Microphone usage description -->
    <key>NSMicrophoneUsageDescription</key>
    <string>Claude Code needs access to your microphone for voice input in accessibility mode</string>

    <!-- Speech recognition usage description -->
    <key>NSSpeechRecognitionUsageDescription</key>
    <string>Claude Code uses speech recognition to process your voice commands</string>

    <!-- Siri requirement -->
    <key>NSRequiresSiriForSpeechRecognition</key>
    <true/>

    <!-- Other configuration -->
    <key>CFBundleExecutable</key>
    <string>ClaudeCode</string>

</dict>
</plist>
```

---

## AVFoundation Audio APIs

### Framework
- **Framework:** AVFoundation.framework
- **Language:** Swift / Objective-C
- **Minimum macOS:** 10.14+
- **Sandbox:** Supported with permissions

### Audio Input

```swift
import AVFoundation

class AudioCaptureManager {

    let audioEngine = AVAudioEngine()

    func setupAudioInput() throws {
        let inputNode = audioEngine.inputNode
        let inputFormat = inputNode.outputFormat(forBus: 0)!

        // Configure audio session
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(
            .record,
            mode: .voice,
            options: []
        )
        try audioSession.setActive(true)

        // Prepare engine
        audioEngine.prepare()

        // Install tap to process audio
        inputNode.installTap(
            onBus: 0,
            bufferSize: 4096,
            format: inputFormat
        ) { buffer, when in
            self.processAudioBuffer(buffer)
        }

        try audioEngine.start()
    }

    func processAudioBuffer(_ buffer: AVAudioPCMBuffer) {
        // Process audio data
        guard let channelData = buffer.floatChannelData else { return }

        let frames = Int(buffer.frameLength)
        let floats = Array(UnsafeMutableBufferPointer(
            start: channelData.pointee,
            count: frames
        ))

        // Send to speech recognition or other processing
        print("Captured \(frames) audio frames")
    }

    func stopCapture() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
    }
}
```

### Audio Output (Speech Synthesis)

```swift
import AVFoundation

class AudioOutputManager {

    let speechSynthesizer = AVSpeechSynthesizer()

    func speak(text: String, language: String = "en-US") {
        let utterance = AVSpeechUtterance(string: text)

        // Configure voice
        utterance.voice = AVSpeechSynthesisVoice(language: language)
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate
        utterance.pitchMultiplier = 1.0
        utterance.volume = 1.0

        // Speak
        speechSynthesizer.speak(utterance)
    }

    func speakWithOptions(
        text: String,
        rate: Float = AVSpeechUtteranceDefaultSpeechRate,
        pitch: Float = 1.0,
        volume: Float = 1.0
    ) {
        let utterance = AVSpeechUtterance(string: text)

        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = rate
        utterance.pitchMultiplier = pitch
        utterance.volume = volume

        speechSynthesizer.speak(utterance)
    }
}
```

### Audio Device Selection

**macOS-Specific Note:**
On macOS, `AVAudioInputNode` is fixed to the system's default input and cannot be changed programmatically. This differs from iOS where you can select specific audio devices.

```swift
// Get available audio output devices (for reference)
let audioSession = AVAudioSession.sharedInstance()
let availableOutputs = audioSession.availableOutputs ?? []

for output in availableOutputs {
    print("Output: \(output.portName)")
    print("  Type: \(output.portType)")
}

// macOS system audio input uses system default
// To change: System Settings > Sound > Input
```

---

## Accessibility Notifications

### Framework
- **Framework:** Foundation.framework + Accessibility.framework
- **Header:** `<ApplicationServices/ApplicationServices.h>`

### Posting Notifications

```objc
// Announce text to accessibility system
void AXPostNotification(
    AXUIElementRef element,
    CFStringRef notification
);

// With user info (macOS 10.13+)
void AXPostNotificationWithUserInfo(
    AXUIElementRef element,
    CFStringRef notification,
    CFDictionaryRef userInfo
);
```

**Swift Example:**

```swift
import AppKit

class AccessibilityAnnouncer {

    static func announce(message: String) {
        let announcement = NSAccessibilityPostNotification(
            NSAccessibility.Notification.announcement.rawValue,
            message
        )

        NSAccessibilityPostNotification(
            NSApp.mainWindow ?? NSApp.windows.first,
            announcement
        )
    }

    static func announceWithUserInfo(
        message: String,
        userInfo: [NSAccessibility.AnnouncementRequestedKey: Any]
    ) {
        // Create notification
        let userInfo: [AnyHashable: Any] = [
            "AXAnnouncementText": message
        ]

        NSAccessibilityPostNotificationWithUserInfo(
            NSApp.mainWindow ?? NSApp.windows.first,
            NSAccessibility.Notification.announcement.rawValue,
            userInfo
        )
    }
}
```

### Common Announcements

```swift
// VoiceOver announcements
NSAccessibility.Notification.announcement
NSAccessibility.Notification.focusChanged
NSAccessibility.Notification.titleChanged
NSAccessibility.Notification.valueChanged
NSAccessibility.Notification.createdNotification
NSAccessibility.Notification.destroyedNotification
```

---

## Version Requirements & Compatibility

### Feature Availability by macOS Version

| Feature | Min Version | Notes |
|---------|-------------|-------|
| **Core Accessibility API (AXUIElement)** | 10.2 | Requires non-sandbox |
| **NSAccessibility Protocol** | 10.10 | Replaces older key-based API |
| **Speech Recognition** | 10.15 | On-device, privacy-friendly |
| **Voice Control** | 14.1 | Native voice commands |
| **AVSpeechSynthesizer** | 10.14 | TTS |
| **AVAudioEngine** | 10.10 | Audio I/O |
| **Accessibility Notifications** | 10.10+ | Modern notification API |
| **Parametrized Attributes** | 10.12 | Advanced AX API features |

### Code Example: Compatibility Check

```python
import platform
import sys

def check_accessibility_support():
    """Check if macOS accessibility features are available"""

    version = platform.mac_ver()[0]
    version_tuple = tuple(map(int, version.split('.')[:2]))

    print(f"macOS Version: {version}")

    features = {
        "Core Accessibility API": (10, 2),
        "Modern NSAccessibility": (10, 10),
        "Speech Recognition": (10, 15),
        "Voice Control": (14, 1),
        "AVFoundation Audio": (10, 10),
    }

    for feature, min_version in features.items():
        supported = version_tuple >= min_version
        status = "✓" if supported else "✗"
        print(f"  {status} {feature}: macOS {min_version[0]}.{min_version[1]}+")

if __name__ == "__main__":
    check_accessibility_support()
```

---

## Permission Management

### TCC (Transparency, Consent, Control) Database

Accessibility permissions are stored in the macOS TCC database.

**User-facing:**
- System Settings > Privacy & Security > Accessibility

**Command line (macOS 13+):**
```bash
# Grant accessibility permission to app
tccutil grant Accessibility com.anthropic.claudecode

# Revoke permission
tccutil revoke Accessibility com.anthropic.claudecode

# Check permissions
sqlite3 ~/Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.db \
    "SELECT * FROM access_control WHERE client LIKE '%claude%';"
```

**Info.plist Declaration:**

```xml
<key>NSAccessibilityUsageDescription</key>
<string>Claude Code needs accessibility access to enable voice-controlled navigation and provide audio feedback to users.</string>
```

---

## Best Practices

### 1. Always Check Authorization

```python
def verify_accessibility_available():
    """Verify accessibility APIs are accessible"""

    try:
        from Accessibility import AXUIElementCreateSystemWide

        system_wide = AXUIElementCreateSystemWide()

        if not system_wide:
            print("ERROR: Accessibility API not available")
            print("Fix: System Settings > Privacy & Security > Accessibility")
            return False

        return True

    except ImportError:
        print("ERROR: PyObjC Accessibility framework not installed")
        print("Fix: pip install pyobjc-framework-Accessibility")
        return False
```

### 2. Error Recovery

```python
def safe_perform_action(element, action_name):
    """Safely perform action with error recovery"""

    try:
        error = AXUIElementPerformAction(element, action_name)

        if error != 0:
            print(f"Action failed with error: {error}")

            # Try alternative approach
            if action_name == "AXPress":
                # Some elements respond to click but not press
                print("Attempting alternative action")
                return False

            return False

        return True

    except Exception as e:
        print(f"Exception performing action: {e}")
        return False
```

### 3. Handle VoiceOver Compatibility

```python
def announce_with_voiceover_fallback(text: str):
    """Announce text with VoiceOver and fallback"""

    # Try accessibility API first (VoiceOver)
    try:
        from Accessibility import AXUIElementCreateSystemWide
        system_wide = AXUIElementCreateSystemWide()

        if system_wide:
            # Post accessibility notification
            NSAccessibilityPostNotification(system_wide, text)
            return

    except Exception as e:
        print(f"VoiceOver announcement failed: {e}")

    # Fallback: Direct TTS output
    import subprocess
    subprocess.run(['say', text])
```

---

## References

- Apple Accessibility Programming Guide: https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/
- AXUIElement.h: https://developer.apple.com/documentation/applicationservices/axuielement_h
- NSAccessibility Protocol: https://developer.apple.com/documentation/appkit/nsaccessibility
- Speech Framework: https://developer.apple.com/documentation/speech/
- AVFoundation: https://developer.apple.com/documentation/avfoundation/

---

**Last Updated:** February 2026

