# PHASE 1: Foundation & Isolation
## Hands-Free OpenClaw on Mac mini: Secure Base Setup

**Status**: Foundation (Days 1-2) | **Prerequisites**: None | **Outputs**: Ready Mac mini, Burner identity, Accessibility baseline | **Test Gate**: VO accessibility audit + voice-enabled approval simulation

---

## Executive Summary

This phase establishes a secure, accessible foundation for running OpenClaw with hands-free operation. You are building an "agent bunker"—a dedicated Mac mini that runs an autonomous AI agent without sending data to external services. All work is local. All interaction is voice-first. All approvals are audible.

**Key Outcomes**:
- ✓ Mac mini physically isolated with accessibility enabled
- ✓ VoiceOver (screen reader) speaking all setup steps
- ✓ Burner identity (no personal data leakage)
- ✓ Approval mechanisms that announce decisions
- ✓ Hands-free accessibility validated end-to-end

---

## Part A: Hardware Preparation

### Hardware Checklist

**Mac mini Requirements**:
- Apple Silicon (M1, M2, M3, M4—ideally M3/M4 for 2026)
- 64GB unified memory (fits Q4 quantized 70B models)
- 500GB+ SSD (model cache + logs + safety margin)
- Network: USB-C Ethernet adapter (optional; WiFi works)

**Accessibility Kit**:
- External microphone (USB or 3.5mm adapter): Essential for hands-free dictation
  - Recommended: Blue Yeti Nano or equivalent (standalone, USB plug-and-play)
  - Budget option: Mac's built-in mic (tested; acceptable quality for dictation)
- Braille display (optional but powerful): Focus 40 5th Gen, Humanware BrailleNote or equivalent
  - USB or Bluetooth connection; macOS recognizes automatically
- Headphones/speakers: For TTS feedback and VoiceOver audio
- USB-C hub: For expanding ports (Ethernet, USB, power)

**Operational Setup**:
- **HDMI dummy plug**: Critical for headless stability on M-series Macs
  - Symptoms without: Graphics resets, kernel panics under load
  - Cost: ~$5; insert into HDMI port, leave in place
  - Why: Apple Silicon's unified memory controller behaves differently without display connection

### Initial Mac mini Configuration

#### Step 1: Enable VoiceOver (Voice-First Setup)

**Why first**: Everything that follows relies on spoken feedback. You're building for hands-free from day one.

1. **Power on the Mac mini** and connect power, Ethernet (if available), and microphone.
2. **Insert HDMI dummy plug** into HDMI port.
3. **At login screen**: Press **Cmd + F5** (or **Fn + Cmd + F5** on newer keyboards).
   - Listen for: "Welcome to VoiceOver" spoken announcement.
   - If no sound: Check System Settings > Sound > Output volume.
4. **VoiceOver cursor is now active**. Navigate using:
   - **VO (Control + Option) + Right Arrow**: Move to next item
   - **VO + Left Arrow**: Previous item
   - **VO + Space**: Activate button/toggle
   - **VO + Down Arrow**: Read more (for longer text)

#### Step 2: Initial System Settings via VoiceOver

Use VoiceOver to navigate. All actions are spoken.

1. **Open System Settings** (press VO + Space on Apple menu, search "Settings").
2. **Navigate to Accessibility** (VO + Right Arrow through menu).
3. **Enable these accessibility features**:
   - ✓ **VoiceOver**: Already on (from Step 1)
   - ✓ **Voice Control**: System Settings > Accessibility > Motor > Voice Control
     - This enables hands-free app launching and system commands
     - Download English language files when prompted (required for offline use)
   - ✓ **Dictation**: System Settings > Keyboard > Dictation
     - Toggle ON
     - Set shortcut to **Fn + Fn** (double-tap Function key)
     - Enable "Use Enhanced Dictation" for offline transcription
   - ✓ **Speech**: System Settings > Accessibility > Spoken Content
     - Enable "Speak Selection" (for announcements)
     - Set voice: Select your preferred voice (System voice works; "Samantha" or "Alex" are common)
     - Speaking rate: Adjust to comfortable speed (try 40-50%)

#### Step 3: Audio Input & Output Validation

**Test microphone with VoiceOver**:
1. Open **System Settings > Sound > Input**.
2. VoiceOver reads available microphones. Use VO + Right Arrow to select external mic (if connected).
3. Open **Notes app** (VO + Space, search "Notes").
4. Press **Fn + Fn** to activate Dictation.
5. **Speak clearly**: "Testing dictation. One, two, three."
6. Listen for VoiceOver to announce the transcribed text.
7. If errors: Speak slower, enunciate. (Enhanced Dictation improves accuracy over time.)

**Test audio output**:
1. In Notes, select some text.
2. **VO + Space** on the text to open context menu.
3. Select "Speak" (or press key binding if set).
4. Listen: VoiceOver should speak the text aloud.

**If issues**:
- No microphone detected: Check System Settings > Privacy & Security > Microphone; grant access.
- Dictation fails: Ensure internet connected (first use downloads language model). Offline dictation requires "Enhanced Dictation" download (~600MB).
- Audio cuts out: Restart VoiceOver (Cmd + F5 twice).

---

## Part B: Burner Identity Setup

### Why Burner Identity Matters

A burner identity isolates your friend's personal data from the agent. If the agent runs a task incorrectly, it doesn't touch their real email, files, or calendar. It's a sandbox at the OS level.

### Create Burner Apple ID

1. **On the Mac mini**, use VoiceOver to navigate to **System Settings > General > Software Update**.
   - (This ensures latest security patches before identity setup.)
2. Once up-to-date, sign out of any existing Apple ID (if logged in).
3. **Create a new Apple ID**:
   - Go to **System Settings > [Your Name]** (top of sidebar).
   - Select "Sign in with a different account".
   - Choose "Don't have an Apple ID?" and follow the wizard.
   - **Email**: Create a burner Gmail or ProtonMail specifically for this: `agent-sandbox-[random]@gmail.com`
   - **Password**: Strong, unique, stored encrypted in a physical notebook (air-gapped from this system).
   - **Recovery email**: Leave blank or use another burner account.
   - **Phone**: Optional; skip if possible.

**Why Gmail/ProtonMail for email**?
- Gmail: Free, no phone required (use app password for OpenClaw later).
- ProtonMail: Free, privacy-first (E2E encryption); slightly slower but highly secure.

### Create Burner System User (Optional but Recommended)

Create a second macOS user account for the agent runtime:

1. **System Settings > General > Users & Groups**.
2. **VoiceOver navigation**: VO + Right Arrow to "Users & Groups".
3. **Add user**: Click the "+" button (announce with VO + Space).
4. **Name**: `openclaw-agent` | **Account type**: Standard (not Admin).
5. **Password**: Random, 20+ chars, stored securely.
6. **Login items**: Leave empty (agent runs via daemon).

**Rationale**: Even if an OpenClaw task is misconfigured and runs shell commands, it's confined to this limited account. It can't delete system files, modify other users' data, or access sensitive accounts.

---

## Part C: Accessibility Baseline

### VoiceOver Customization for Agent Approval

Since your friend will approve OpenClaw actions via voice, VoiceOver must be clear and immediate.

#### Configure VoiceOver Voice & Speed

1. **System Settings > Accessibility > VoiceOver > VoiceOver Utility** (VO + Space).
2. **Navigation > Interaction**:
   - **Cursor focus**: Enable "Speak on focus" (announces items as you navigate).
   - **Verbosity**: Set to "Verbose" (more details about buttons, menus).
3. **Voices**:
   - Set system voice to a clear voice (e.g., "Samantha" or high-quality voice like "Victoria").
   - **Speaking rate**: Adjust to 50-60% (clear and steady for agent approvals).
4. **Audio**:
   - **Audio ducking**: Disable (so agent TTS doesn't fade out system sounds).

#### Test VoiceOver Navigation Flow

Simulate an agent approval request:

1. Open **Notes** (VO + Space, search "Notes").
2. **VO + U** (open rotor) to access the rotor menu.
3. Navigate rotor to "Headings" (VO + Down Arrow).
4. **VO + Down Arrow** through headings to simulate scanning a task list.
5. **VO + Space** to "activate" (approve) an item.
6. **Expectation**: VoiceOver announces each action clearly; no stumbling.

**Accessibility Checklist**:
- ✓ All system notifications are announced by VoiceOver
- ✓ Dictation activates with Fn + Fn and announces "Dictation listening"
- ✓ Text entered via Dictation is read back by VoiceOver
- ✓ Buttons/menus are navigable without sight (VO + Right/Left, Space to activate)

### Braille Display (Optional)

If your friend uses Braille:

1. **Connect Braille display via Bluetooth** (or USB).
2. **macOS detects automatically**; may prompt for driver installation.
3. **System Settings > Accessibility > VoiceOver > Braille**:
   - Enable "Braille support" (toggle ON).
   - Select connected display in "Braille Display" dropdown.
   - **Braille table**: US English or your language (affects translation).
4. **Test**: Open Notes, type text, confirm it appears on Braille display.

---

## Part D: Approval Mechanisms

### Approval Philosophy

OpenClaw is an autonomous agent that can execute tasks (send emails, modify files, run scripts). Without approval gates, it might do something unintended. Your friend needs:
1. **Audible notification** when a task is pending approval.
2. **Clear description** of what the agent wants to do.
3. **Voice-activated approval** or **explicit deny**.

### ApprovalConfig Skeleton

Create a file `~/.openclaw/approval-config.yaml`:

```yaml
# Approval gate config for hands-free operation
approval:
  enabled: true
  
  # Audible announcement before waiting for decision
  notification:
    method: "voiceover-speak"  # Use macOS VoiceOver to announce
    voice: "System"             # Matches system voice
    text_template: |
      Agent requests approval for: {action}
      Details: {details}
      Say 'approve' to proceed. Say 'deny' to reject.
      Timeout: 60 seconds.
  
  # Dictation-based approval (voice)
  approval_method: "voice"
  voice_keywords:
    approve: ["approve", "yes", "ok", "proceed"]
    deny: ["deny", "no", "stop", "cancel"]
  
  # Fallback (if voice fails): use keyboard
  fallback: "keyboard"
  fallback_keys:
    approve: "Return"
    deny: "Escape"
  
  # Timeout: if no response after 60s, deny by default (safe)
  timeout_seconds: 60
  timeout_action: "deny"
  
  # Log all approvals for audit trail
  audit_log: "~/.openclaw/audit.log"
```

### Integration with OpenClaw (Phase 4)

In Phase 4, you'll integrate this config into OpenClaw's core setup. For now, save it as a placeholder.

---

## Part E: Knowledge Gaps Filled

### Gap 1: zram Compression on macOS

**Problem**: Older documentation recommends zram (in-memory compression) for M-series Macs. macOS doesn't support zram natively.

**Solution**: 
- macOS uses **memory compression** automatically (no config needed).
- When RAM pressure rises, the OS compresses inactive pages.
- Monitor compression with: `vm_stat | grep "Pages compressed"` (in Terminal).
- If compression exceeds 10% of physical RAM, you're swapping; close background apps.

### Gap 2: Burner Identity Isolation

**Problem**: If a burner account runs the agent and a task goes rogue, can it escape to the admin account?

**Solution**:
- Run OpenClaw daemon under the `openclaw-agent` user (limited privileges).
- Use **sandboxd** (macOS sandbox) to further restrict file/network access.
- (Detailed in Phase 4; here we just create the account and test permissions.)

### Gap 3: Thermal Management in Headless Mode

**Problem**: Mac mini with HDMI dummy plug sometimes throttles GPU if it thinks there's no display.

**Solution**:
- Monitor thermal state: `pmset -g thermlog` (shows temp zones).
- If throttling occurs: Create a cron job to log thermal state every 5 minutes.
- (Detailed in Phase 6; for now, note that HDMI dummy plug solves 99% of cases.)

---

## Part F: Testing & Validation Gate

Before proceeding to Phase 2, validate the foundation:

### Accessibility Validation Checklist

Run the **OpenClaw Doctor** (once installed in Phase 4). For now, manually test:

1. **VoiceOver Test**:
   - [ ] Cmd + F5 toggles VoiceOver on/off; announcement is clear.
   - [ ] Navigate System Settings with VO + Right/Left; all items announced.
   - [ ] Open 3+ apps (Notes, Mail, Safari) using VoiceOver search (VO + Space).

2. **Dictation Test**:
   - [ ] Fn + Fn activates dictation; "Listening" is announced.
   - [ ] Dictate a sentence: "Hello, this is a test of hands-free dictation."
   - [ ] Accuracy: ≥90% (for English; will improve with Enhanced Dictation).

3. **Voice Control Test** (if using):
   - [ ] Say "Open Safari"; Safari launches without touching keyboard.
   - [ ] Say "Show grid"; grid overlays appear (for clicking via voice).

4. **Approval Simulation**:
   - [ ] Create a shell script that runs: `echo "Test approval request" | say` (uses macOS `say` to announce).
   - [ ] Script should wait for voice input ("approve" or "deny").
   - [ ] Confirm input is captured and logged.

### Manual Test Script

Create `~/test-accessibility.sh`:

```bash
#!/bin/bash
# Test accessibility baseline

echo "=== VoiceOver & Dictation Test ==="
# Announce test start
say "Testing VoiceOver and Dictation. Please follow prompts."

echo "Test 1: Open Notes"
open -a Notes

# Wait for human to confirm Notes is open
sleep 5

echo "Test 2: Activate Dictation (Fn + Fn) and say 'Test dictation'."
say "Press Function twice to start dictation. Say: Test dictation phrase."

# Simulate approval request
echo "Test 3: Approval simulation"
say "Agent requests approval to create a test file. Say approve or deny."

# (In Phase 4, this will be replaced with actual OpenClaw approval flow.)

echo "=== Test Complete ==="
say "Accessibility tests complete. Check ~/test-results.txt for details."
```

**Run it**:
```bash
chmod +x ~/test-accessibility.sh
./test-accessibility.sh
```

### Success Criteria

- ✓ All VoiceOver navigation works without touching keyboard
- ✓ Dictation transcribes English with >85% accuracy
- ✓ System announcements (via `say` command) are clear and immediate
- ✓ Approval simulation captures voice input and responds appropriately
- ✓ No errors in system logs (`log show --predicate 'process == "kernel"' | head -20`)

---

## Part G: Extension Points

Document where future customizations will hook in:

### `customAccessibility` Object (Phase 4+)

```json
{
  "customAccessibility": {
    "tts_provider": "system",  // macOS `say`; swap to external TTS if needed
    "tts_voice": "Samantha",
    "tts_rate": 0.5,
    "braille_enabled": false,  // Set to true if Braille display connected
    "braille_display_model": "focus40_5th_gen",  // For future Braille integrations
    "voiceover_customizations": {
      "verbosity": "verbose",
      "audio_ducking": false
    }
  }
}
```

---

## Troubleshooting Matrix

| **Issue** | **Symptom** | **Fix** |
|-----------|-----------|--------|
| VoiceOver won't start | Cmd + F5 produces no sound | Restart Mac; check System Settings > Sound > Output; restart VoiceOver with Cmd + F5 twice |
| Dictation fails | "Dictation failed" error after pressing Fn + Fn | Check internet (first run downloads language files); download Enhanced Dictation offline (~600MB) |
| Microphone not detected | VoiceOver doesn't announce microphone input | System Settings > Privacy & Security > Microphone; grant access to required app |
| HDMI dummy plug doesn't work | GPU still throttles | Reseat dummy plug; try different HDMI cable; check `pmset -g thermlog` |
| Braille display not recognized | Braille display connects but not paired | Restart VoiceOver; check Bluetooth settings; update Braille display firmware |

---

## Summary & Handoff to Phase 2

**What you've built**:
- ✓ Secure, accessible Mac mini with VoiceOver enabled
- ✓ Burner identity isolated from personal data
- ✓ Hands-free approval mechanisms in place
- ✓ Accessibility validated end-to-end
- ✓ Foundation for all subsequent phases

**Next**: Phase 2 adds Podman (container runtime) for isolation. The accessibility tools you've set up here will speak all of Phase 2's configuration steps.

**Estimated time**: 2-4 hours (including testing and troubleshooting).
