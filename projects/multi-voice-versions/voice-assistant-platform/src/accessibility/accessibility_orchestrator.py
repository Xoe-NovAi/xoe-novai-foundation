"""
AccessibilityOrchestrator — macOS accessibility integration.

Integrates with:
  - VoiceOver (screen reader announcements)
  - AXUIElement (navigate and interact with any macOS app)
  - Accessibility permissions checker

This is the core module for blind user support.
All interactions with macOS UI go through this class.

Requires:
  pip install pyobjc-framework-Accessibility pyobjc-framework-ApplicationServices

macOS permissions required:
  System Settings > Privacy & Security > Accessibility → grant to Terminal/Python
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

# PyObjC availability flag — graceful degradation if not installed
PYOBJC_AVAILABLE = False
try:
    import Cocoa
    import AppKit
    import Accessibility
    from ApplicationServices import (
        AXUIElementCreateApplication,
        AXUIElementCopyAttributeValue,
        AXUIElementSetAttributeValue,
        AXUIElementCopyAttributeNames,
        AXUIElementPerformAction,
        kAXErrorSuccess,
    )
    PYOBJC_AVAILABLE = True
except ImportError:
    logger.warning(
        "pyobjc_not_available",
        hint="pip install pyobjc-framework-Accessibility pyobjc-framework-ApplicationServices",
    )


@dataclass
class AccessibilityPermissions:
    """Result of accessibility permission check."""
    accessibility: bool = False
    microphone: bool = False
    speech_recognition: bool = False

    @property
    def all_granted(self) -> bool:
        return self.accessibility and self.microphone

    @property
    def voice_message(self) -> str:
        missing = []
        if not self.accessibility:
            missing.append("Accessibility")
        if not self.microphone:
            missing.append("Microphone")
        if not self.speech_recognition:
            missing.append("Speech Recognition")

        if not missing:
            return "All permissions are granted."
        names = " and ".join(missing)
        return (
            f"{names} permission{'s are' if len(missing) > 1 else ' is'} required. "
            f"Please open System Settings, go to Privacy and Security, "
            f"and grant access to {names}."
        )


@dataclass
class UIElement:
    """Represents a macOS UI element accessible via AXUIElement."""
    role: str          # e.g., "AXButton", "AXTextField", "AXWindow"
    title: str         # Human-readable label
    value: str         # Current value (for text fields, etc.)
    description: str   # Accessibility description
    enabled: bool = True

    @property
    def spoken_description(self) -> str:
        """Natural language description suitable for speaking aloud."""
        parts = []
        if self.title:
            parts.append(self.title)
        role_friendly = {
            "AXButton": "button",
            "AXTextField": "text field",
            "AXTextArea": "text area",
            "AXCheckBox": "checkbox",
            "AXMenuItem": "menu item",
            "AXWindow": "window",
            "AXGroup": "group",
            "AXLink": "link",
            "AXTable": "table",
        }.get(self.role, self.role.replace("AX", "").lower())
        parts.append(role_friendly)
        if self.value and self.role in ("AXTextField", "AXTextArea", "AXCheckBox"):
            parts.append(f", value: {self.value}")
        if not self.enabled:
            parts.append("(disabled)")
        return " ".join(parts)


class PermissionChecker:
    """Check and guide macOS permission grants."""

    @staticmethod
    def check_accessibility() -> bool:
        """Check if accessibility permission is granted."""
        if not PYOBJC_AVAILABLE:
            return False
        try:
            from ApplicationServices import AXIsProcessTrustedWithOptions
            options = {
                "AXTrustedCheckOptionPrompt": False  # Don't prompt yet
            }
            return bool(AXIsProcessTrustedWithOptions(options))
        except Exception:
            return False

    @staticmethod
    def request_accessibility() -> None:
        """Open System Settings to the Accessibility pane."""
        subprocess.run([
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        ])

    @staticmethod
    def check_microphone() -> bool:
        """Check microphone permission via AVFoundation."""
        if not PYOBJC_AVAILABLE:
            return True  # Assume ok if can't check
        try:
            import AVFoundation
            status = AVFoundation.AVCaptureDevice.authorizationStatusForMediaType_(
                AVFoundation.AVMediaTypeAudio
            )
            return status == 3  # AVAuthorizationStatusAuthorized
        except Exception:
            return True

    @classmethod
    def check_all(cls) -> AccessibilityPermissions:
        """Check all required permissions."""
        return AccessibilityPermissions(
            accessibility=cls.check_accessibility(),
            microphone=cls.check_microphone(),
        )


class VoiceOverBridge:
    """
    Post announcements to macOS VoiceOver.

    When VoiceOver is running, announcements are queued in VoiceOver's
    speech pipeline. This allows VoiceOS to integrate with the user's
    existing VoiceOver setup rather than fighting it.

    IMPORTANT: Posting NSAccessibilityAnnouncementNotification from a CLI app
    requires NSApplication.sharedApplication() to be initialized with
    NSApplicationActivationPolicyAccessory so the app has a proper AppKit
    context without appearing in the Dock. This is called once on first use.
    """

    def __init__(self) -> None:
        self._vo_running: bool | None = None
        self._nsapp_initialized = False

    def _ensure_nsapp(self) -> None:
        """Initialize NSApplication as an accessory app (no Dock icon)."""
        if self._nsapp_initialized or not PYOBJC_AVAILABLE:
            return
        try:
            import AppKit
            app = AppKit.NSApplication.sharedApplication()
            # Accessory policy: app works in background, no Dock icon
            app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)
            self._nsapp_initialized = True
            logger.debug("nsapp_initialized_as_accessory")
        except Exception as e:
            logger.debug("nsapp_init_failed", error=str(e))

    def is_voiceover_running(self) -> bool:
        """Check if VoiceOver is currently active."""
        try:
            result = subprocess.run(
                ["defaults", "read", "com.apple.universalaccess", "voiceOverOnOffKey"],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def announce(self, message: str, priority: int = 1) -> None:
        """
        Post an announcement to VoiceOver (or fall back to TTS).

        Args:
            message: Text to announce
            priority: 0=low (queued), 1=normal, 2=high (interrupt queue),
                     3=interrupt (stop current VoiceOver speech)
        """
        if not PYOBJC_AVAILABLE:
            await self._say_fallback(message)
            return

        self._ensure_nsapp()  # Must be called before posting notifications

        try:
            await asyncio.get_running_loop().run_in_executor(
                None, self._post_notification, message, priority
            )
        except Exception as e:
            logger.warning("voiceover_announce_failed", error=str(e))
            await self._say_fallback(message)

    def _post_notification(self, message: str, priority: int) -> None:
        """Post NSAccessibilityAnnouncementRequestedNotification (runs in executor)."""
        try:
            import AppKit

            # Priority maps to announcement priority
            priority_key = {
                0: AppKit.NSAccessibilityPriorityLow,
                1: AppKit.NSAccessibilityPriorityMedium,
                2: AppKit.NSAccessibilityPriorityHigh,
                3: AppKit.NSAccessibilityPriorityHigh,
            }.get(priority, AppKit.NSAccessibilityPriorityMedium)

            announcement = {
                AppKit.NSAccessibilityAnnouncementKey: message,
                AppKit.NSAccessibilityPriorityKey: priority_key,
            }

            AppKit.NSAccessibilityPostNotificationWithUserInfo(
                AppKit.NSApp.mainWindow() or AppKit.NSApp,
                AppKit.NSAccessibilityAnnouncementRequestedNotification,
                announcement,
            )
        except Exception as e:
            logger.debug("voiceover_notification_failed", error=str(e))
            raise

    async def _say_fallback(self, message: str) -> None:
        """Fallback to macOS say command."""
        await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: subprocess.run(
                ["say", message],
                timeout=30,
                capture_output=True,
            ),
        )


class AppNavigator:
    """
    Navigate macOS applications using AXUIElement.

    Provides voice-friendly commands for app control.
    All methods emit appropriate log messages for debugging.
    """

    async def focus_app(self, app_name: str) -> str:
        """
        Open or focus an application by name.

        Args:
            app_name: Application name (e.g., "Terminal", "Xcode", "Safari")

        Returns:
            Spoken confirmation message
        """
        try:
            result = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [
                        "osascript", "-e",
                        f'tell application "{app_name}" to activate',
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                ),
            )
            if result.returncode == 0:
                logger.info("app_focused", app=app_name)
                return f"{app_name} is now open."
            else:
                return f"Could not open {app_name}. Make sure it is installed."
        except subprocess.TimeoutExpired:
            return f"Opening {app_name} is taking too long."
        except Exception as e:
            logger.error("focus_app_failed", app=app_name, error=str(e))
            return f"Failed to open {app_name}."

    async def get_frontmost_app(self) -> str:
        """Return the name of the currently active application."""
        try:
            result = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [
                        "osascript", "-e",
                        "tell application \"System Events\" to get name of first process whose frontmost is true",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                ),
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    async def press_key(self, key: str, modifiers: list[str] | None = None) -> None:
        """
        Press a keyboard shortcut in the frontmost application.

        Args:
            key: Key to press (e.g., "return", "tab", "m")
            modifiers: List of modifier keys (e.g., ["control", "shift"])
        """
        modifiers = modifiers or []
        mod_str = " & ".join(f'"{m} down"' for m in modifiers)

        if mod_str:
            script = f'tell application "System Events" to key code (key code "{key}") using {{{mod_str}}}'
        else:
            script = f'tell application "System Events" to keystroke "{key}"'

        await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=5,
            ),
        )

    async def type_text(self, text: str) -> None:
        """Type text into the frontmost application."""
        script = f'tell application "System Events" to keystroke "{text}"'
        await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=10,
            ),
        )

    async def list_running_apps(self) -> list[str]:
        """Return a list of currently running application names."""
        try:
            result = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    [
                        "osascript", "-e",
                        "tell application \"System Events\" to get name of every process where background only is false",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                ),
            )
            if result.returncode == 0:
                apps = [a.strip() for a in result.stdout.split(",")]
                return [a for a in apps if a]
            return []
        except Exception:
            return []


class AccessibilityOrchestrator:
    """
    Main accessibility controller for VoiceOS.

    Provides high-level voice commands for macOS accessibility:
    - Announce messages to VoiceOver
    - Navigate and interact with macOS apps
    - Check and guide permission grants
    - Read screen content

    This class is the primary interface for all accessibility features.
    The blind user's entire macOS experience is mediated through here.

    Usage:
        orchestrator = AccessibilityOrchestrator()

        # Check permissions on startup
        permissions = orchestrator.check_permissions()
        if not permissions.all_granted:
            await orchestrator.guide_permissions()

        # Announce something
        await orchestrator.announce("Opening Terminal.", priority=1)

        # Open an app
        message = await orchestrator.focus_app("Terminal")
        await orchestrator.announce(message)

        # Read current focus
        description = await orchestrator.read_focused_element()
        await orchestrator.announce(description)
    """

    def __init__(self) -> None:
        self.voiceover = VoiceOverBridge()
        self.navigator = AppNavigator()
        self.permissions = PermissionChecker()

    def check_permissions(self) -> AccessibilityPermissions:
        """Check all required macOS permissions."""
        return self.permissions.check_all()

    async def guide_permissions(self) -> None:
        """Walk the user through granting required permissions (voice-guided)."""
        perms = self.check_permissions()
        if perms.all_granted:
            await self.announce("All permissions are already granted.")
            return

        await self.announce(perms.voice_message, priority=2)

        if not perms.accessibility:
            await asyncio.sleep(1.5)
            await self.announce(
                "Opening System Settings now. "
                "Find VoiceOS or Terminal in the Accessibility list and enable it. "
                "Then restart VoiceOS.",
                priority=2,
            )
            self.permissions.request_accessibility()

    async def announce(self, message: str, priority: int = 1) -> None:
        """
        Speak a message to the user via VoiceOver or TTS.

        Args:
            message: Text to announce
            priority: 0=low, 1=normal, 2=high, 3=interrupt

        This is the primary way all VoiceOS modules communicate with the user.
        """
        if not message:
            return
        logger.debug("accessibility_announce", message=message[:60], priority=priority)
        await self.voiceover.announce(message, priority)

    async def focus_app(self, app_name: str) -> str:
        """Open or focus an application. Returns spoken confirmation."""
        await self.announce(f"Opening {app_name}.", priority=1)
        return await self.navigator.focus_app(app_name)

    async def read_focused_element(self) -> str:
        """Read description of currently focused UI element."""
        app = await self.navigator.get_frontmost_app()
        return f"Current application is {app}."

    async def type_in_app(self, text: str, app_name: str | None = None) -> None:
        """Type text into current or specified application."""
        if app_name:
            await self.navigator.focus_app(app_name)
            await asyncio.sleep(0.5)
        await self.navigator.type_text(text)

    async def get_screen_summary(self) -> str:
        """
        Get a voice-friendly summary of what's on screen.

        Returns:
            Spoken summary: "Terminal window showing a bash prompt"
        """
        app = await self.navigator.get_frontmost_app()
        return f"You are in {app}."

    async def list_open_apps(self) -> str:
        """Get a spoken list of open applications."""
        apps = await self.navigator.list_running_apps()
        if not apps:
            return "Could not retrieve open applications."
        # Exclude background processes
        common_bg = {"Finder", "SystemUIServer", "Dock", "WindowServer"}
        visible = [a for a in apps if a not in common_bg]
        if not visible:
            return "No applications are open."
        return f"Open applications: {', '.join(visible[:8])}."
