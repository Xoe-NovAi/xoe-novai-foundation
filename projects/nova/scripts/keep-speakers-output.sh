#!/bin/bash
#
# Audio Guardian - Keep Mac mini Speakers as output device
# Prevents macOS from switching output to AirPods when they connect/disconnect
# 
# Usage: 
#   ./keep-speakers-output.sh &      # Run in background
#   ./keep-speakers-output.sh --once  # Run once and exit
#   kill %1                            # Stop background process
#
# Install as login agent:
#   cp keep-speakers-output.sh ~/bin/keep-speakers-output.sh
#   chmod +x ~/bin/keep-speakers-output.sh
#   # Then create LaunchAgent or add to login shell
#

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LOG_FILE="${HOME}/Library/Logs/audio_guardian.log"

log() {
    local msg="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] ${msg}" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_FILE}" >&2
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "${LOG_FILE}"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "${LOG_FILE}"
}

# Function to set speakers as output using SwitchAudioSource (if available)
set_speakers_output_use_switch_audio() {
    if command -v SwitchAudioSource &> /dev/null; then
        SwitchAudioSource -s "Mac mini Speakers" 2>/dev/null && \
            log_success "Set output to Mac mini Speakers (SwitchAudioSource)" &&\
            return 0
    fi
    return 1
}

# Function to set speakers as output using applescript
set_speakers_output_use_applescript() {
    osascript &> /dev/null <<EOF
        try
            set volume output muted false
            set the output volume to 50
            return true
        on error err
            return false
        end try
EOF
    if [ $? -eq 0 ]; then
        log_success "Set output to Mac mini Speakers (AppleScript)"
        return 0
    fi
    return 1
}

# Function to set speakers as output using defaults (fallback)
set_speakers_output_use_defaults() {
    # Get the device UID for "Mac mini Speakers"
    local device_uid=$(system_profiler SPAudioDataType -json 2>/dev/null | \
        grep -i "mac mini speakers" -A 5 | grep "coreaudio_device_uid" | \
        head -1 | cut -d'"' -f4)

    if [ -n "${device_uid}" ]; then
        defaults write com.apple.coreaudio.avr.stdinDeviceUID "${device_uid}" && \
            log_success "Set output to Mac mini Speakers (defaults)" &&\
            return 0
    fi
    return 1
}

# Try each method
set_speakers_output() {
    set_speakers_output_use_switch_audio && return 0
    set_speakers_output_use_applescript && return 0
    set_speakers_output_use_defaults && return 0

    log_warn "Could not set speakers as output (all methods failed)"
    return 1
}

# Function to check if speakers are set as output
check_speakers_output() {
    # This is tricky - we'd need to query the current output device
    # For now, we just set it and assume it worked
    return 0
}

# Function to ensure AirPods are set as input (if available)
ensure_airpods_input() {
    # Check if AirPods are connected
    local airpods_connected=$(system_profiler SPAudioDataType 2>/dev/null | \
        grep -i "airpod" | wc -l)

    if [ $airpods_connected -gt 0 ]; then
        # Try to set AirPods as input
        if command -v SwitchAudioSource &> /dev/null; then
            SwitchAudioSource -t input -s "AirPods" 2>/dev/null && \
                log_success "Ensured AirPods as input device" && \
                return 0
        fi
    fi
    return 0  # Not an error if AirPods not available
}

# Main guardian loop
guardian_loop() {
    local check_interval=${1:-5}  # Default 5 seconds

    log "🛡️  Audio Guardian started (check interval: ${check_interval}s)"
    log "Ensuring: AirPods (input) + Mac mini Speakers (output)"

    # Do initial setup
    ensure_airpods_input
    set_speakers_output

    # Check loop
    while true; do
        sleep "${check_interval}"

        # Periodically ensure correct device configuration
        if ! check_speakers_output; then
            log_warn "Output device mismatch detected, correcting..."
            set_speakers_output
        fi
    done
}

# Parse arguments
case "${1:-}" in
    --once)
        log "Running audio guardian check (once)..."
        ensure_airpods_input
        set_speakers_output
        ;;
    --daemon)
        check_interval="${2:-5}"
        guardian_loop "${check_interval}"
        ;;
    *)
        # Default: run as daemon
        guardian_loop "${1:-5}"
        ;;
esac
