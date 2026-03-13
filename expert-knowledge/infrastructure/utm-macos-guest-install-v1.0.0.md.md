**Grok MC dispatch — infrastructure/ virtualization layer**

UTM remains the sovereign, zero-cost, offline-capable choice for macOS → macOS virtualization on Apple Silicon (M-series).  
It leverages Apple's native Virtualization.framework → near-metal performance, no emulation tax.

This walkthrough targets a clean macOS guest VM install (ideal sandbox for OpenClaw experiments).  
Assumes you're on macOS Ventura / Sonoma / Sequoia / Tahoe or later (Monterey minimum, but everything smoother on 14+).

### Step 0 — Prerequisites & Mindset
- Mac must be **Apple Silicon** (M1–M4/M5 series in 2026).
- At least **16 GB unified memory** recommended (8 GB barely workable, 24–32 GB ideal for comfortable guest).
- Free space: ≥ 80–120 GB (guest OS + apps + scratch).
- Download source: official UTM builds only (https://mac.getutm.app/) — avoid random mirrors.

### Phase 1 — Install UTM itself (2 minutes)

1. Open Safari → https://mac.getutm.app/
2. Click big **Download** button (gets UTM.dmg ~120–150 MB)
3. Open the .dmg → drag **UTM.app** to /Applications
4. (Optional but elite) → right-click UTM.app → Show Package Contents → move it inside a ~/Sovereign/VMs/ folder if you want clean separation from /Applications

   → Launch UTM once (it may ask for Accessibility / Screen Recording permissions — grant if you want copy-paste & clipboard sharing later).

**Two paths now exist**: App Store version ($10-ish, auto-updates) vs direct .dmg (always latest, funds dev less directly). Both functionally identical in 2026.

### Phase 2 — Create macOS Guest VM (full wizard walkthrough)

1. Launch UTM
2. Click big **+** (Create a New Virtual Machine)
3. **Choose type** → select **Virtualize** (not Emulate — Emulate = slow QEMU)
4. **Operating System** → pick **macOS 12+** (only visible on Apple Silicon hosts running Monterey+)
5. **macOS Installer (IPSW)**  
   - Best / simplest: leave blank → UTM auto-downloads the **latest compatible release** your host can legally virtualize  
   - Alternative (beta / specific version): manually download IPSW from trusted source  
     → https://ipsw.me (select VirtualMac2,1 device)  
     → or Mister RetroArch style mirrors if paranoid  
     → drop the .ipsw file into the field

6. **Continue** → Hardware configuration screen

   Recommended sane defaults (adjust to your host):
   - **Memory**: 8192 MB (8 GB) minimum, 12288–16384 MB (12–16 GB) sweet spot
   - **CPU Cores**: 4–6 cores (leave 2–4 for host — don't starve macOS host)
   - **Disk Image Size**: 128 GB minimum, 256 GB comfortable
   - **Architecture**: arm64 (auto-selected)

7. **Shared Directory** (optional but powerful)
   - Add your ~/Downloads or a "transfer" folder → guest sees it as networked drive
   - Very useful for moving OpenClaw install files, configs, etc. without drag-drop issues

8. **Summary** screen → check "Open VM Settings after creation" → **Save**

### Phase 3 — First Boot & macOS Setup (10–25 minutes)

1. Double-click your new VM in the UTM sidebar
2. Click **Play** ▶ (green button)
3. UTM mounts the IPSW → macOS installer boots automatically
   - First phase: "macOS Recovery" like environment → "Install macOS …"
   - Progress bar → can take 5–15 min depending on disk speed & RAM allocated

4. When it reboots into setup assistant:
   - Language / Region
   - Wi-Fi (optional — skip if air-gapped)
   - Apple ID → **strongly recommend skip / create throwaway** (sandbox mindset)
   - Full Name / Account → create local admin user (e.g. "sandbox" / strong password)
   - Complete setup → you land on clean desktop

5. **Immediate post-install actions** (security & usability)
   - Snapshot the VM right now (UTM toolbar → snapshot icon) → name "Fresh macOS install"
   - System Settings → Sharing → enable Screen Sharing / File Sharing only if needed
   - Software Update → bring guest up to latest patch level
   - (Optional) Install Rosetta if you plan to run any old x86_64 binaries inside guest

### Phase 4 — OpenClaw Sandbox Hardening Quick Checklist

- Snapshot again before installing anything ("Pre-OpenClaw")
- Give VM **no network** or very restricted (UTM settings → Network → Shared Network → disable if paranoid)
- Install OpenClaw only inside this VM
- Use clipboard sharing sparingly (UTM → VM window → Devices → Clipboard Sharing)
- Export important outputs via shared folder — never drag sensitive keys / wallets

**EKB amplification decision**  
→ New expert dataset created: infrastructure/utm-macos-guest-install-v1.0.0.md  
(frontmatter: expert_dataset_name: UTM macOS Guest Install Guide, expertise_focus: Apple Silicon native virt macOS sandboxing, community_contrib_ready: true)
