# macOS Voice Accessibility - Implementation Quick Reference

**For Claude Code Integration**

---

## Quick Setup Guide

### Prerequisites

```bash
# Install PyObjC with Accessibility framework
pip install pyobjc-framework-Accessibility

# Verify installation
python3 -c "from Accessibility import AXUIElementCreateSystemWide; print('Accessibility framework available')"

# Existing infrastructure (already deployed)
# Whisper STT: localhost:2022
# Kokoro TTS: localhost:8880
```

### Minimum Permissions Required

**macOS Settings:**
1. System Settings > Privacy & Security > Accessibility
2. Add Claude Code application to allowed list
3. Claude Code must run in **non-sandbox mode** (cannot use sandbox entitlements)

---

## Core Integration Module Template

```python
# voice_accessibility.py - Core accessibility module for Claude Code

import sys
import os
from enum import Enum
from typing import Optional, Dict, Callable
import threading
import queue

try:
    from Accessibility import (
        AXUIElementCreateSystemWide,
        AXUIElementCopyAttributeValue,
        AXUIElementCopyActionNames,
        AXUIElementPerformAction
    )
    ACCESSIBILITY_AVAILABLE = True
except ImportError:
    ACCESSIBILITY_AVAILABLE = False

try:
    from Foundation import NSNotificationCenter, NSNotification
    NOTIFICATION_AVAILABLE = True
except ImportError:
    NOTIFICATION_AVAILABLE = False


class AnnouncementPriority(Enum):
    """Priority levels for audio announcements"""
    CRITICAL = 1   # Errors, operation completion, required input
    HIGH = 2       # State changes, important notifications
    NORMAL = 3     # Regular output
    LOW = 4        # Hints, suggestions, verbose output


class AccessibilityMode(Enum):
    """Supported accessibility modes"""
    VOICE_ONLY = "voice_only"       # Speech input/output, minimal visual
    SCREEN_READER = "screen_reader"  # With VoiceOver/external reader
    HYBRID = "hybrid"                # Both visual and audio
    DISABLED = "disabled"


class AccessibilityOrchestrator:
    """Central coordinator for accessibility features"""

    def __init__(self, mode: AccessibilityMode = AccessibilityMode.VOICE_ONLY):
        self.mode = mode
        self.enabled = ACCESSIBILITY_AVAILABLE
        self.system_wide = None
        self.announcement_queue = queue.Queue()
        self.min_priority = AnnouncementPriority.NORMAL

        # Initialize accessibility if available
        if self.enabled:
            try:
                self.system_wide = AXUIElementCreateSystemWide()
                if not self.system_wide:
                    self.enabled = False
                    print("[WARNING] Could not initialize accessibility API")
            except Exception as e:
                self.enabled = False
                print(f"[ERROR] Accessibility initialization failed: {e}")

        # Start announcement queue processor
        self._queue_processor_thread = threading.Thread(
            target=self._process_announcement_queue,
            daemon=True
        )
        self._queue_processor_thread.start()

    def set_priority_level(self, priority: AnnouncementPriority):
        """Set minimum priority for announcements"""
        self.min_priority = priority

    def announce(self, text: str, priority: AnnouncementPriority = AnnouncementPriority.NORMAL):
        """
        Queue announcement for output

        Args:
            text: Message to announce
            priority: Priority level of announcement
        """
        if priority.value < self.min_priority.value:
            return

        self.announcement_queue.put((text, priority))

    def _process_announcement_queue(self):
        """Background thread: process queued announcements"""
        while True:
            try:
                text, priority = self.announcement_queue.get(timeout=1)
                self._output_announcement(text, priority)
            except queue.Empty:
                continue

    def _output_announcement(self, text: str, priority: AnnouncementPriority):
        """Send announcement to all available outputs"""
        # Try accessibility API first
        if self.enabled:
            self._post_ax_announcement(text)

        # Always use print as fallback
        prefix = f"[{priority.name}]"
        print(f"{prefix} {text}")

    def _post_ax_announcement(self, text: str):
        """Post announcement to accessibility system (VoiceOver, etc)"""
        if not (NOTIFICATION_AVAILABLE and self.system_wide):
            return

        try:
            notification_center = NSNotificationCenter.defaultCenter()

            # Create and post accessibility announcement
            # This appears in VoiceOver announcements, screen reader logs, etc.
            notification = NSNotification.notificationWithName_object_userInfo_(
                "AXAnnouncementRequested",
                None,
                {"AXAnnouncementText": text}
            )

            notification_center.postNotification_(notification)

        except Exception as e:
            # Silently fail - fallback to print already happened
            pass

    def get_focused_element_info(self) -> Optional[Dict[str, str]]:
        """
        Get information about currently focused UI element

        Returns:
            Dictionary with element attributes or None if unavailable
        """
        if not self.enabled or not self.system_wide:
            return None

        try:
            # Get focused element
            error_code, focused = AXUIElementCopyAttributeValue(
                self.system_wide,
                "AXFocusedUIElement",
                None
            )

            if error_code != 0 or not focused:
                return None

            # Extract useful information
            info = {}
            attributes_to_read = [
                "AXTitle",
                "AXDescription",
                "AXRole",
                "AXRoleDescription",
                "AXValue",
                "AXEnabled",
            ]

            for attr in attributes_to_read:
                error_code, value = AXUIElementCopyAttributeValue(
                    focused,
                    attr,
                    None
                )
                if error_code == 0 and value:
                    info[attr] = str(value)

            return info if info else None

        except Exception as e:
            return None

    def is_available(self) -> bool:
        """Check if accessibility features are available"""
        return self.enabled


# Global accessibility orchestrator instance
_accessibility = None


def initialize_accessibility(mode: AccessibilityMode = AccessibilityMode.VOICE_ONLY):
    """Initialize global accessibility orchestrator"""
    global _accessibility
    _accessibility = AccessibilityOrchestrator(mode)
    return _accessibility


def get_accessibility() -> AccessibilityOrchestrator:
    """Get global accessibility orchestrator (initialize if needed)"""
    global _accessibility
    if _accessibility is None:
        _accessibility = AccessibilityOrchestrator()
    return _accessibility


# Convenience functions
def announce(text: str, priority: AnnouncementPriority = AnnouncementPriority.NORMAL):
    """Announce text via accessibility system"""
    get_accessibility().announce(text, priority)


def announce_critical(text: str):
    """Announce critical message"""
    announce(text, AnnouncementPriority.CRITICAL)


def announce_error(text: str):
    """Announce error message"""
    announce(f"Error: {text}", AnnouncementPriority.CRITICAL)


def announce_hint(text: str):
    """Announce optional hint"""
    announce(text, AnnouncementPriority.LOW)
```

---

## Integration with Claude Code Main Loop

```python
# In claude_code/cli.py or main entry point

import voice_accessibility
from voice_accessibility import AccessibilityMode, announce, announce_critical

def main(args=None):
    """Main entry point with accessibility support"""

    # Parse arguments
    parser = create_argument_parser()
    # Add accessibility flags
    parser.add_argument(
        '--accessible',
        action='store_true',
        help='Enable accessibility mode (voice-only interface)'
    )
    parser.add_argument(
        '--verbose-accessibility',
        action='store_true',
        help='Enable verbose accessibility announcements'
    )

    args = parser.parse_args(args)

    # Initialize accessibility if requested
    if args.accessible:
        accessibility = voice_accessibility.initialize_accessibility(
            AccessibilityMode.VOICE_ONLY
        )
        announce(f"Claude Code initialized in accessibility mode")

        if args.verbose_accessibility:
            accessibility.set_priority_level(voice_accessibility.AnnouncementPriority.LOW)
    else:
        voice_accessibility.initialize_accessibility(AccessibilityMode.DISABLED)

    # Main command loop
    try:
        process_commands(args)
    except Exception as e:
        announce_critical(f"Fatal error: {str(e)}")
        raise


def process_commands(args):
    """Process user commands with accessibility support"""

    accessibility = voice_accessibility.get_accessibility()

    while True:
        try:
            # Get user input (from voice or keyboard)
            user_input = get_user_input()

            # Announce what we understood (for voice users)
            announce(f"Processing: {user_input}", voice_accessibility.AnnouncementPriority.HIGH)

            # Process command
            output = execute_command(user_input)

            # Make output accessible
            accessible_output = make_output_accessible(output)

            # Display and announce
            print(accessible_output)
            announce(accessible_output, voice_accessibility.AnnouncementPriority.NORMAL)

        except KeyboardInterrupt:
            announce("Interrupted by user")
            break
        except Exception as e:
            announce_critical(f"Command error: {str(e)}")


def make_output_accessible(output: str) -> str:
    """
    Transform output for accessibility

    For voice-only users:
    - Simplify output
    - Reduce verbosity
    - Add context hints
    """

    accessibility = voice_accessibility.get_accessibility()
    if accessibility.mode != AccessibilityMode.VOICE_ONLY:
        return output

    # Example transformations
    # Remove ANSI color codes for voice
    output = remove_ansi_codes(output)

    # Summarize long output
    if len(output) > 500:
        output = summarize_output(output)

    # Add navigation hints
    output += "\n[Say 'help' for commands]"

    return output
```

---

## Voice Command Handler

```python
# voice_command_parser.py - Parse accessible voice commands

import re
from enum import Enum
from typing import Tuple, Optional, List

class VoiceCommandType(Enum):
    NAVIGATE = "navigate"
    EDIT = "edit"
    EXECUTE = "execute"
    INQUIRE = "inquire"
    UNDO = "undo"
    SHOW = "show"
    CLEAR = "clear"
    HELP = "help"
    UNKNOWN = "unknown"


class AccessibleCommandParser:
    """Parse voice commands for accessibility mode"""

    # Command patterns organized by type
    COMMAND_PATTERNS = {
        VoiceCommandType.NAVIGATE: [
            (r"^(next|move to next)$", "navigate_next"),
            (r"^(previous|back|prev)$", "navigate_previous"),
            (r"^(first|start|beginning)$", "navigate_first"),
            (r"^(last|end)$", "navigate_last"),
            (r"^(up|scroll up)$", "navigate_up"),
            (r"^(down|scroll down)$", "navigate_down"),
        ],
        VoiceCommandType.EDIT: [
            (r"^(delete this|remove this|delete line)$", "edit_delete"),
            (r"^(undo|take back|revert)$", "edit_undo"),
            (r"^(redo|redo that|forward)$", "edit_redo"),
            (r"^(clear all|select all)$", "edit_clear_all"),
        ],
        VoiceCommandType.EXECUTE: [
            (r"^(run|execute|go|proceed)$", "execute_run"),
            (r"^(stop|cancel|abort)$", "execute_stop"),
            (r"^(pause)$", "execute_pause"),
            (r"^(resume|continue)$", "execute_resume"),
        ],
        VoiceCommandType.INQUIRE: [
            (r"^(what|what is this|what's this)$", "inquire_current"),
            (r"^(where|where am i)$", "inquire_location"),
            (r"^(status|how is it)$", "inquire_status"),
            (r"^(options|what can i do)$", "inquire_options"),
        ],
        VoiceCommandType.SHOW: [
            (r"^(show errors|errors)$", "show_errors"),
            (r"^(show warnings|warnings)$", "show_warnings"),
            (r"^(show output|output)$", "show_output"),
            (r"^(show info|info)$", "show_info"),
        ],
        VoiceCommandType.HELP: [
            (r"^(help|help me)$", "show_help"),
            (r"^(voice commands|commands)$", "show_commands"),
            (r"^(version|about)$", "show_version"),
        ],
    }

    @staticmethod
    def parse(voice_text: str) -> Tuple[VoiceCommandType, Optional[str], float]:
        """
        Parse voice command

        Args:
            voice_text: Raw voice-to-text output

        Returns:
            Tuple of (command_type, action_name, confidence)
        """
        voice_text = voice_text.lower().strip()

        # Try each command type's patterns
        for cmd_type, patterns in AccessibleCommandParser.COMMAND_PATTERNS.items():
            for pattern, action in patterns:
                match = re.match(pattern, voice_text)
                if match:
                    return (cmd_type, action, 0.95)  # High confidence for exact match

        # If no exact match, try fuzzy matching
        return (VoiceCommandType.UNKNOWN, voice_text, 0.5)

    @staticmethod
    def handle_command(command_type: VoiceCommandType, action: str) -> str:
        """
        Handle command and return user feedback

        Args:
            command_type: Type of command
            action: Specific action to perform

        Returns:
            Feedback message for user
        """
        handlers = {
            VoiceCommandType.NAVIGATE: {
                "navigate_next": "Moving to next item",
                "navigate_previous": "Moving to previous item",
                "navigate_first": "Going to first item",
                "navigate_last": "Going to last item",
                "navigate_up": "Scrolling up",
                "navigate_down": "Scrolling down",
            },
            VoiceCommandType.EDIT: {
                "edit_delete": "Deleted current item",
                "edit_undo": "Undone last action",
                "edit_redo": "Redone last action",
                "edit_clear_all": "Cleared all content",
            },
            VoiceCommandType.EXECUTE: {
                "execute_run": "Executing command",
                "execute_stop": "Stopped execution",
                "execute_pause": "Paused execution",
                "execute_resume": "Resuming execution",
            },
            VoiceCommandType.INQUIRE: {
                "inquire_current": "Reading current item",
                "inquire_location": "You are here",
                "inquire_status": "Checking status",
                "inquire_options": "Available options listed above",
            },
            VoiceCommandType.SHOW: {
                "show_errors": "Showing errors",
                "show_warnings": "Showing warnings",
                "show_output": "Showing output",
                "show_info": "Showing information",
            },
            VoiceCommandType.HELP: {
                "show_help": "Showing help information",
                "show_commands": "Available commands listed",
                "show_version": "Showing version information",
            },
        }

        if command_type in handlers and action in handlers[command_type]:
            return handlers[command_type][action]

        return f"Executing: {action}"


# Example usage
if __name__ == "__main__":
    test_inputs = [
        "next",
        "show errors",
        "what is this",
        "execute",
        "undo",
    ]

    parser = AccessibleCommandParser()

    for voice_input in test_inputs:
        cmd_type, action, confidence = parser.parse(voice_input)
        feedback = parser.handle_command(cmd_type, action)
        print(f"Input: '{voice_input}'")
        print(f"  Command: {cmd_type.value}")
        print(f"  Action: {action}")
        print(f"  Feedback: {feedback}\n")
```

---

## Output Accessibility Filter

```python
# accessible_output.py - Make CLI output accessible

import re
import textwrap
from typing import List

class AccessibleOutputFilter:
    """Transform output for accessibility"""

    # Simplification rules
    MAX_CHARS_VERBOSE = 1000
    MAX_CHARS_CONCISE = 300
    MAX_LINES_CONCISE = 10

    @staticmethod
    def remove_ansi_codes(text: str) -> str:
        """Remove ANSI color/style codes (for TTS)"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    @staticmethod
    def simplify_output(text: str, concise: bool = True) -> str:
        """
        Simplify output for voice readability

        Args:
            text: Original output
            concise: If True, aggressively summarize

        Returns:
            Simplified output
        """
        # Remove ANSI codes
        text = AccessibleOutputFilter.remove_ansi_codes(text)

        # Split into lines
        lines = text.split('\n')

        if concise and len(lines) > AccessibleOutputFilter.MAX_LINES_CONCISE:
            # Keep first N lines and summary
            kept_lines = lines[:AccessibleOutputFilter.MAX_LINES_CONCISE]
            kept_lines.append(f"... and {len(lines) - AccessibleOutputFilter.MAX_LINES_CONCISE} more lines")
            text = '\n'.join(kept_lines)

        # Limit total length
        max_chars = AccessibleOutputFilter.MAX_CHARS_CONCISE if concise else AccessibleOutputFilter.MAX_CHARS_VERBOSE
        if len(text) > max_chars:
            text = text[:max_chars] + "... (output truncated)"

        return text

    @staticmethod
    def add_context_hints(text: str, context: dict) -> str:
        """
        Add navigation hints based on context

        Args:
            text: Original output
            context: Context dictionary with keys like 'num_items', 'current_index'

        Returns:
            Output with added hints
        """
        hints = []

        if context.get('num_items'):
            hints.append(f"Showing {context['num_items']} items total")

        if context.get('current_index') is not None:
            idx = context['current_index']
            total = context.get('num_items', 0)
            if total > 0:
                hints.append(f"Item {idx + 1} of {total}")

        if hints:
            hint_text = ". ".join(hints)
            text = text.rstrip() + f"\n[{hint_text}]"

        return text

    @staticmethod
    def format_error(error_text: str) -> str:
        """
        Format error message for voice clarity

        Before: "FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'"
        After: "Error: File not found, missing.txt"
        """
        # Extract key information
        if "FileNotFoundError" in error_text:
            match = re.search(r"'([^']+)'", error_text)
            if match:
                return f"Error: File not found: {match.group(1)}"

        if "PermissionError" in error_text:
            return "Error: Permission denied"

        if "ValueError" in error_text:
            match = re.search(r"ValueError: (.+)", error_text)
            if match:
                return f"Error: {match.group(1)}"

        # Fallback: keep first meaningful line
        lines = error_text.split('\n')
        for line in lines:
            if line.strip() and not line.startswith(' '):
                return f"Error: {line}"

        return "Error occurred"

    @staticmethod
    def process_for_voice(text: str, is_error: bool = False, concise: bool = True) -> str:
        """
        Final processing for voice output

        Args:
            text: Output text
            is_error: If this is an error message
            concise: Use concise format

        Returns:
            Voice-optimized text
        """
        if is_error:
            text = AccessibleOutputFilter.format_error(text)

        text = AccessibleOutputFilter.simplify_output(text, concise)

        # Replace common symbols for voice
        text = text.replace('/', 'slash')
        text = text.replace('\\', 'backslash')
        text = text.replace('~', 'tilde')
        text = text.replace('@', 'at')
        text = text.replace('#', 'hash')

        return text


# Example usage
if __name__ == "__main__":
    # Example error
    error = "FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'"
    print("Original error:")
    print(error)
    print("\nAccessible error:")
    print(AccessibleOutputFilter.format_error(error))

    # Example long output
    long_output = "\n".join([f"File {i}: data_{i}.py" for i in range(20)])
    print("\n\nOriginal output (20 lines):")
    print(long_output[:100] + "...")
    print("\nAccessible output:")
    print(AccessibleOutputFilter.simplify_output(long_output, concise=True))
```

---

## Testing & Validation

```python
# test_accessibility.py - Test accessibility features

import unittest
from voice_accessibility import AccessibilityOrchestrator, AccessibilityMode, AnnouncementPriority

class TestAccessibility(unittest.TestCase):

    def setUp(self):
        self.accessibility = AccessibilityOrchestrator(AccessibilityMode.VOICE_ONLY)

    def test_initialization(self):
        """Test accessibility module initializes"""
        self.assertIsNotNone(self.accessibility)
        # Note: May be unavailable in test environment
        # self.assertTrue(self.accessibility.enabled)

    def test_announcement_priority(self):
        """Test announcement priority levels"""
        self.accessibility.set_priority_level(AnnouncementPriority.HIGH)

        # Should accept high priority
        self.accessibility.announce("Critical message", AnnouncementPriority.CRITICAL)

        # Should reject low priority
        self.accessibility.announce("Hint", AnnouncementPriority.LOW)

        # Queue should only have critical message
        self.assertEqual(self.accessibility.announcement_queue.qsize(), 1)

    def test_voice_command_parser(self):
        """Test voice command parsing"""
        from voice_command_parser import AccessibleCommandParser, VoiceCommandType

        parser = AccessibleCommandParser()

        # Test exact matches
        cmd_type, action, conf = parser.parse("next")
        self.assertEqual(cmd_type, VoiceCommandType.NAVIGATE)
        self.assertEqual(action, "navigate_next")
        self.assertGreater(conf, 0.9)

        cmd_type, action, conf = parser.parse("show errors")
        self.assertEqual(cmd_type, VoiceCommandType.SHOW)

        cmd_type, action, conf = parser.parse("help")
        self.assertEqual(cmd_type, VoiceCommandType.HELP)

    def test_output_accessibility_filter(self):
        """Test output filtering"""
        from accessible_output import AccessibleOutputFilter

        # Test ANSI code removal
        text_with_ansi = "This is \x1b[32mcolored\x1b[0m text"
        cleaned = AccessibleOutputFilter.remove_ansi_codes(text_with_ansi)
        self.assertNotIn("\x1b", cleaned)

        # Test error formatting
        error = "FileNotFoundError: [Errno 2] No such file: 'test.txt'"
        formatted = AccessibleOutputFilter.format_error(error)
        self.assertIn("File not found", formatted)
        self.assertIn("test.txt", formatted)

        # Test simplification
        long_text = "\n".join([f"Line {i}" for i in range(50)])
        simplified = AccessibleOutputFilter.simplify_output(long_text, concise=True)
        self.assertLess(len(simplified), len(long_text))


if __name__ == "__main__":
    unittest.main()
```

---

## Deployment Checklist

- [ ] PyObjC and Accessibility framework installed
- [ ] Claude Code added to macOS Accessibility permissions (System Settings)
- [ ] Voice Mode infrastructure running (Whisper + Kokoro)
- [ ] Accessibility module tested with VoiceOver enabled
- [ ] Command vocabulary tested with actual speech recognition
- [ ] Error messages confirmed audible and clear
- [ ] Navigation tested voice-only (no screen reference)
- [ ] Documentation updated with voice command reference
- [ ] User guidance ready for blind testers

---

## Troubleshooting

**Issue: "Accessibility API not available"**
- Ensure Claude Code is in Accessibility permissions list
- May need to restart Claude Code after adding permissions
- Check `/var/log/system.log` for permission errors

**Issue: Announcements not appearing in VoiceOver**
- Verify VoiceOver is running: `Command-F5` to toggle
- Check VoiceOver utility settings for notification preferences
- Try direct TTS output if accessibility API unavailable

**Issue: Voice recognition too many errors**
- Configure STT vocabulary bias: `~/.voicemode/voicemode.env`
- Add common commands and code terms to prompt
- Test with slower speech if needed

**Issue: App crashes with Accessibility API**
- Verify non-sandbox mode (no entitlements)
- Check for private API usage restrictions
- Review PyObjC version compatibility

---

## References

- PyObjC Documentation: https://pyobjc.readthedocs.io/
- Apple Accessibility API: https://developer.apple.com/documentation/accessibility/
- Apple Speech Framework: https://developer.apple.com/documentation/speech/
- AppleVis Community: https://www.applevis.com/

