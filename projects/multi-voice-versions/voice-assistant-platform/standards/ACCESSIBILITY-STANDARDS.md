# Accessibility Standards

**Project**: VoiceOS — Voice Assistant Platform
**Scope**: All features, all phases
**Last Updated**: 2026-02-23

> "Accessibility is not a feature. It is the product."

---

## 1. Core Accessibility Requirements

### 1.1 Zero-Screen Guarantee

Every feature in VoiceOS MUST be fully functional without a display. This means:

- All state is communicated by voice
- All interactions can be triggered by voice command
- No feature requires mouse clicks, trackpad gestures, or visual selection
- Visual UI elements (menus, dialogs, code windows) are read aloud on demand

**Testing method**: Close your eyes and complete the task from start to finish. If you can't, it fails.

### 1.2 Keyboard-Optional

All features must be operable with zero keyboard input after the system is started. The "Start VoiceOS" launcher app is the one-time keyboard-or-click action.

### 1.3 Predictable Behavior

A blind user cannot scan a UI to understand state. Therefore:
- All actions must have predictable, consistent results
- Commands must always work the same way regardless of app focus
- Error recovery must be guided by voice, never visual

---

## 2. macOS Accessibility APIs

### 2.1 VoiceOver Integration

VoiceOver is the primary screen reader on macOS. VoiceOS integrates with it via the Accessibility API.

**Rules for VoiceOver integration:**
- Use `AXUIElement` to post announcements via `NSAccessibilityPostNotification`
- Priority responses should interrupt VoiceOver's current speech
- Low-priority messages queue behind VoiceOver
- Do not override VoiceOver cursor position without explicit user request

**Announcement levels:**

| Priority | VoiceOver Behavior | Use Case |
|----------|-------------------|----------|
| 0 — Low | Queued after VoiceOver finishes | Status updates |
| 1 — Normal | Queued, plays when VoiceOver idle | Normal responses |
| 2 — High | Interrupts VoiceOver queue | Warnings, new responses |
| 3 — Interrupt | Immediately interrupts all speech | Errors, wake word |

### 2.2 AXUIElement Navigation

When navigating macOS apps on behalf of the user:
- Always announce the focused element before activating it
- Read element labels using `kAXTitleAttribute` or `kAXDescriptionAttribute`
- Read element role (button, text field, menu item) before value
- Announce confirmation before performing destructive actions

**Example announcement pattern:**
```
"Navigating to: Terminal application"
"Current focus: New Terminal button"
"Activating: New Terminal"
"Terminal window opened"
```

### 2.3 Permission Requirements

The system requires the following macOS permissions (must be granted at first run):
- **Accessibility Access** — System Settings > Privacy & Security > Accessibility
- **Microphone Access** — System Settings > Privacy & Security > Microphone
- **Speech Recognition** — System Settings > Privacy & Security > Speech Recognition (if using native macOS STT)
- **Automation** — For controlling specific apps (Terminal, Xcode, etc.)

The `voiceos check-permissions` command must verify all permissions at startup and guide the user through granting any that are missing — entirely by voice.

---

## 3. Voice Interaction Design

### 3.1 Response Length Guidelines

| Context | Max Length | Rationale |
|---------|-----------|-----------|
| Confirmation | 5 words | "Done." / "Okay, opening Terminal." |
| Normal response | 30 words | Short enough to hold in working memory |
| Explanation | 60 words | For complex concepts |
| Detailed output | 150 words | Only when explicitly asked |
| Code summary | 20 words | Describe, don't read code |

For anything longer than 150 words, VoiceOS MUST ask: "That's a long answer. Want me to summarize or read it all?"

### 3.2 Confirmation Before Destructive Actions

Any action that cannot be undone MUST require verbal confirmation:
- Deleting files: "Are you sure you want to delete main.py? Say 'yes' to confirm."
- Running scripts: "About to run install.sh as root. Say 'confirm' to proceed."
- Closing unsaved work: "You have unsaved changes. Say 'save and close' or 'discard'."

### 3.3 Interruptibility

The user MUST be able to interrupt any ongoing speech with a voice command or wake word at any time. Long responses are never spoken to completion if interrupted.

Implementation: Use VAD (voice activity detection) during TTS playback. Detected voice interrupts TTS immediately.

### 3.4 Progressive Disclosure of Commands

New users should not need to memorize commands. The system should:
- Offer natural language understanding for common intents
- Suggest next possible commands when uncertain: "I can open it, run it, or delete it. What would you like?"
- Provide a "what can I say?" command at any time
- Never say "invalid command" — always suggest the closest valid interpretation

### 3.5 Acknowledgment Chimes

Chimes provide instant non-verbal feedback:
- **Listen chime** (rising tone): System is now listening
- **Think chime** (two tones): Processing your request
- **Done chime** (falling tone): Action completed
- **Error chime** (descending tones): Something went wrong

Chimes are especially important for blind users who cannot see visual indicators.

---

## 4. Code Accessibility

### 4.1 Reading Code Aloud

Code is not naturally speakable. When reading code to a blind user:
- Never read punctuation literally unless requested ("open paren" → implied)
- Use natural language: "define function named parse_audio that takes audio as bytes"
- Indentation communicated as structure: "inside the if block:" → "inside that block:"
- Error locations: "line 42, column 8: missing colon after if statement"

### 4.2 Code Navigation Commands

Users must be able to navigate code by voice:
- "Jump to function [name]"
- "Read the current function"
- "What are the parameters of [function]?"
- "Show me all errors"
- "Go to line [number]"
- "Read from line [X] to line [Y]"

### 4.3 Diff and Change Descriptions

When code changes are made:
- Always describe the change in natural language before showing code
- "I added a try-except block around the audio capture. The function now catches connection errors and retries up to 3 times."
- Offer to read the changed lines or skip to reviewing the result

---

## 5. Audio Quality Requirements

### 5.1 TTS Voice Quality

For a blind user, TTS voice is the primary interface. Standards:
- Default voice: natural, not robotic (Kokoro or OpenAI TTS)
- Speaking rate: 150–170 WPM (normal conversation pace), user-adjustable
- Pitch: mid-range, neutral, non-fatiguing for long sessions
- Silence between responses: 0.3s minimum pause for comprehension
- No clipping, distortion, or audio artifacts

### 5.2 Audio Device Reliability

- Audio output device MUST be pinned to the configured device (e.g., Mac mini Speakers)
- An audio watcher daemon monitors and corrects device switching every 2 seconds
- If audio device changes, VoiceOS announces via system speaker: "Audio output restored"
- Input device (microphone) must remain stable for the duration of a session

### 5.3 Silence Detection Sensitivity

For blind users who may pause longer when thinking:
- Minimum silence duration before cutoff: 2.5 seconds (not 1.5s default)
- VAD aggressiveness: 2 (balanced — not overly strict)
- After silence cutoff, always confirm: "Got it. Working on that."

---

## 6. Session Reliability

### 6.1 Session State is Always Known

At any time, the user can say "where are we?" and receive:
- Current task/context
- Last successful action
- Any pending confirmations

### 6.2 Graceful Degradation Script

When services fail, there is a defined fallback speech path:

| Failure | Fallback | Speech |
|---------|---------|--------|
| STT timeout | Wait 3s, retry once | "Having trouble hearing you. Please try again." |
| LLM unavailable | Try next provider | "Using backup AI. One moment." |
| TTS silent | System beep + log | *(no speech possible — use system bell)* |
| All services down | Emergency shell mode | Fallback to macOS built-in `say` command |

### 6.3 Emergency Fallback

If VoiceOS core crashes, a separate watchdog process uses macOS `say` command to speak: "VoiceOS has stopped. Please check the terminal window."

---

## 7. Testing for Accessibility

### 7.1 Eyes-Closed Test

Every new feature must be tested with eyes closed:
1. Close your eyes
2. Complete the task using only voice
3. If you open your eyes at any point, that's a bug

### 7.2 VoiceOver Compatibility Test

Run VoiceOver (Cmd+F5) and verify:
- All VoiceOS announcements are read correctly
- There is no conflicting speech between VoiceOver and VoiceOS TTS
- Navigation commands work while VoiceOver is active

### 7.3 New User Test

An unfamiliar blind user should be able to:
- Start VoiceOS from scratch using only voice
- Complete one development task (create a file, write a function, run it)
- Understand every response without prior training

---

## 8. Internationalization (Future)

Not in scope for Phase 0–2, but designed for:
- All voice prompts use string constants (no hardcoded English strings in logic)
- SSML markup for non-English pronunciation
- STT language configurable per session
- RTL text handled correctly in code reading

---

## References

- [macOS Accessibility Programming Guide](https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/)
- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/) — adapted for voice interfaces
- [W3C ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [Apple VoiceOver User Guide](https://support.apple.com/guide/voiceover/)
- [PyObjC Accessibility Framework](https://pyobjc.readthedocs.io/en/latest/apinotes/Accessibility.html)
