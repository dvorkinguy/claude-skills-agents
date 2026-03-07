#!/usr/bin/env bash
# audio-doctor.sh — Diagnose and fix all audio input issues
# Usage: bash audio-doctor.sh [diagnose|fix|switch <device>|status]
set -uo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

log_ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err()  { echo -e "${RED}[ERR]${NC} $*"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }

# ─── Status ───────────────────────────────────────────────────────────────
cmd_status() {
    echo -e "\n${BLUE}=== Audio Input Status ===${NC}"

    # PipeWire
    if systemctl --user is-active pipewire &>/dev/null; then
        log_ok "PipeWire running"
    else
        log_err "PipeWire not running"
    fi

    # Default source
    local src
    src=$(pactl get-default-source 2>/dev/null || echo "none")
    log_info "Default source: $src"

    # Source volume
    local vol
    vol=$(pactl get-source-volume "$src" 2>/dev/null | grep -oP '\d+%' | head -1 || echo "?")
    local muted
    muted=$(pactl get-source-mute "$src" 2>/dev/null | grep -oP '(yes|no)' || echo "?")
    if [[ "$muted" == "yes" ]]; then
        log_err "Mic is MUTED"
    fi
    if [[ "$vol" =~ ^([0-9]+)% ]] && (( ${BASH_REMATCH[1]} < 50 )); then
        log_warn "Mic volume low: $vol (should be 80-100%)"
    else
        log_ok "Mic volume: $vol"
    fi

    # List all input sources
    echo -e "\n${BLUE}Available input sources:${NC}"
    pactl list sources short 2>/dev/null | grep -v '\.monitor' | while read -r idx name _ _ _; do
        local marker=""
        [[ "$name" == "$src" ]] && marker=" <-- DEFAULT"
        echo "  $idx  $name$marker"
    done

    # Bluetooth devices
    echo -e "\n${BLUE}Bluetooth audio devices:${NC}"
    local bt_cards
    bt_cards=$(pactl list cards short 2>/dev/null | grep bluez || true)
    if [[ -z "$bt_cards" ]]; then
        log_info "No Bluetooth audio devices connected"
    else
        while read -r idx name _; do
            local profile
            profile=$(pactl list cards 2>/dev/null | grep -A30 "Name: $name" | grep "Active Profile:" | head -1 | sed 's/.*: //')
            echo "  $name  (profile: $profile)"
            if [[ "$profile" == "a2dp-sink"* ]]; then
                log_warn "  ^ A2DP mode = output only. Use 'switch bt-mic' to enable mic"
            fi
        done <<< "$bt_cards"
    fi

    # STT daemon
    echo -e "\n${BLUE}Claude STT daemon:${NC}"
    if pgrep -f 'claude_stt.daemon' &>/dev/null; then
        local count
        count=$(pgrep -fc 'claude_stt.daemon' || true)
        if (( count > 1 )); then
            log_warn "Multiple STT daemon instances running ($count)"
        else
            log_ok "STT daemon running (1 instance)"
        fi
    else
        log_info "STT daemon not running"
    fi

    # Quick recording test
    echo -e "\n${BLUE}Mic test (1 sec):${NC}"
    local tmpwav="/tmp/audio_doctor_test_$$.wav"
    if timeout 3 arecord -d 1 -f S16_LE -r 16000 -c 1 "$tmpwav" &>/dev/null; then
        local db
        db=$(python3 -c "
import numpy as np, wave
with wave.open('$tmpwav', 'r') as w:
    data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
    rms = np.sqrt(np.mean(data**2)) if len(data) > 0 else 0
    db = 20 * np.log10(rms / 32768) if rms > 0 else -100
    print(f'{db:.1f}')
" 2>/dev/null || echo "-999")
        rm -f "$tmpwav"
        if (( $(echo "$db < -50" | bc -l 2>/dev/null || echo 1) )); then
            log_err "Mic level very low: ${db} dB (speak into mic and try again)"
        elif (( $(echo "$db < -35" | bc -l 2>/dev/null || echo 0) )); then
            log_warn "Mic level low: ${db} dB (consider boosting volume)"
        else
            log_ok "Mic level good: ${db} dB"
        fi
    else
        log_err "Could not record from mic"
        rm -f "$tmpwav"
    fi
}

# ─── Fix ──────────────────────────────────────────────────────────────────
cmd_fix() {
    echo -e "\n${BLUE}=== Fixing Audio Input ===${NC}"

    # 1. Ensure PipeWire is running
    if ! systemctl --user is-active pipewire &>/dev/null; then
        log_info "Starting PipeWire..."
        systemctl --user start pipewire pipewire-pulse wireplumber
    fi
    log_ok "PipeWire running"

    # 2. Kill duplicate STT daemons
    local stt_count
    stt_count=$(pgrep -fc 'claude_stt.daemon' || true)
    if (( stt_count > 1 )); then
        log_info "Killing duplicate STT daemon instances..."
        pkill -f 'claude_stt.daemon' || true
        sleep 1
        log_ok "Cleared duplicate daemons"
    fi

    # 3. Pick best available input source
    local best_source=""
    local bt_headset_source=""
    local wired_source=""
    local internal_source=""

    # Check for bluetooth headset with mic
    local bt_card
    bt_card=$(pactl list cards short 2>/dev/null | grep bluez | head -1 | awk '{print $2}')
    if [[ -n "$bt_card" ]]; then
        # Check if headset-head-unit profile is available (has mic)
        local has_hfp
        has_hfp=$(pactl list cards 2>/dev/null | grep -A100 "Name: $bt_card" | grep -c 'headset-head-unit' || true)
        if (( has_hfp > 0 )); then
            bt_headset_source="bt"
        fi
    fi

    # Check for USB/wired headset mic
    wired_source=$(pactl list sources short 2>/dev/null | grep -v '\.monitor' | grep -i 'usb\|headset\|headphone' | grep -v 'Camera' | head -1 | awk '{print $2}')

    # Internal mic is always available
    internal_source=$(pactl list sources short 2>/dev/null | grep -v '\.monitor' | grep -iE 'analog.*stereo|internal' | head -1 | awk '{print $2}')

    # Use internal mic as default (most reliable)
    if [[ -n "$internal_source" ]]; then
        best_source="$internal_source"
    fi

    if [[ -n "$best_source" ]]; then
        pactl set-default-source "$best_source"
        log_ok "Default source: $best_source"
    fi

    # 4. Unmute and set optimal volume
    local current_src
    current_src=$(pactl get-default-source 2>/dev/null)
    if [[ -n "$current_src" ]]; then
        pactl set-source-mute "$current_src" 0
        pactl set-source-volume "$current_src" 45%
        log_ok "Mic unmuted, volume set to 45%"
    fi

    # 5. Fix ALSA internal mic boost if available
    if amixer -c PCH sget 'Internal Mic Boost' &>/dev/null; then
        amixer -c PCH sset 'Internal Mic Boost' 0% &>/dev/null
        log_ok "Internal Mic Boost set to 0%"
    elif amixer sget 'Mic Boost' &>/dev/null; then
        amixer sset 'Mic Boost' 0% &>/dev/null
        log_ok "Mic Boost set to 0%"
    fi

    # 6. Verify with a recording test
    echo ""
    cmd_status
}

# ─── Switch audio input device ────────────────────────────────────────────
cmd_switch() {
    local target="${1:-}"
    if [[ -z "$target" ]]; then
        echo "Usage: audio-doctor.sh switch <laptop|bt-mic|bt-audio|wired|list>"
        echo ""
        echo "  laptop   - Internal laptop microphone"
        echo "  bt-mic   - Bluetooth headset mic (switches to HFP profile)"
        echo "  bt-audio - Bluetooth A2DP (high quality output, no mic)"
        echo "  wired    - Wired/USB headset microphone"
        echo "  list     - Show all available sources"
        return 1
    fi

    case "$target" in
        laptop|internal)
            local src
            src=$(pactl list sources short 2>/dev/null | grep -v '\.monitor' | grep -iE 'analog.*stereo' | head -1 | awk '{print $2}')
            if [[ -n "$src" ]]; then
                pactl set-default-source "$src"
                pactl set-source-mute "$src" 0
                pactl set-source-volume "$src" 45%
                log_ok "Switched to laptop mic: $src (45%)"
            else
                log_err "Internal mic not found"
            fi
            ;;

        bt-mic|bt-headset)
            local bt_card
            bt_card=$(pactl list cards short 2>/dev/null | grep bluez | head -1 | awk '{print $2}')
            if [[ -z "$bt_card" ]]; then
                log_err "No Bluetooth audio device connected"
                return 1
            fi

            # Switch to headset profile (HFP/HSP) which enables mic
            log_info "Switching $bt_card to headset profile..."
            if pactl set-card-profile "$bt_card" headset-head-unit-msbc 2>/dev/null; then
                log_ok "Switched to mSBC headset profile (16kHz mic)"
            elif pactl set-card-profile "$bt_card" headset-head-unit 2>/dev/null; then
                log_ok "Switched to headset profile (8kHz mic)"
            else
                log_err "Failed to switch Bluetooth profile. Available profiles:"
                pactl list cards 2>/dev/null | grep -A50 "Name: $bt_card" | grep 'Part of profile' | sort -u
                return 1
            fi

            # Wait for source to appear
            sleep 1

            # Find and set the bluetooth source
            local bt_src
            bt_src=$(pactl list sources short 2>/dev/null | grep bluez | grep -v '\.monitor' | head -1 | awk '{print $2}')
            if [[ -n "$bt_src" ]]; then
                pactl set-default-source "$bt_src"
                pactl set-source-mute "$bt_src" 0
                pactl set-source-volume "$bt_src" 100%
                log_ok "Bluetooth mic active: $bt_src"
            else
                log_warn "Bluetooth source not yet available. Try again in a moment."
            fi
            ;;

        bt-audio|bt-a2dp)
            local bt_card
            bt_card=$(pactl list cards short 2>/dev/null | grep bluez | head -1 | awk '{print $2}')
            if [[ -z "$bt_card" ]]; then
                log_err "No Bluetooth audio device connected"
                return 1
            fi
            # Switch back to A2DP (high quality audio, no mic)
            pactl set-card-profile "$bt_card" a2dp-sink 2>/dev/null || \
            pactl set-card-profile "$bt_card" a2dp-sink-sbc 2>/dev/null || \
            pactl set-card-profile "$bt_card" a2dp-sink-sbc_xq 2>/dev/null
            log_ok "Switched to A2DP (high quality output, laptop mic for input)"

            # Fall back to internal mic
            cmd_switch laptop
            ;;

        wired|usb)
            local src
            src=$(pactl list sources short 2>/dev/null | grep -v '\.monitor' | grep -iE 'usb|headset|headphone' | grep -iv 'Camera' | head -1 | awk '{print $2}')
            if [[ -n "$src" ]]; then
                pactl set-default-source "$src"
                pactl set-source-mute "$src" 0
                pactl set-source-volume "$src" 80%
                log_ok "Switched to wired/USB mic: $src (80%)"
            else
                log_err "No wired/USB headset mic found. Connected devices:"
                pactl list sources short 2>/dev/null | grep -v '\.monitor'
            fi
            ;;

        list)
            echo -e "${BLUE}Available audio input sources:${NC}"
            local default_src
            default_src=$(pactl get-default-source 2>/dev/null)
            pactl list sources short 2>/dev/null | grep -v '\.monitor' | while read -r idx name _ _ _; do
                local marker=""
                [[ "$name" == "$default_src" ]] && marker=" ${GREEN}<-- DEFAULT${NC}"
                echo -e "  $idx  $name$marker"
            done
            echo ""
            echo -e "${BLUE}Bluetooth cards:${NC}"
            pactl list cards short 2>/dev/null | grep bluez || echo "  (none connected)"
            ;;

        *)
            log_err "Unknown target: $target"
            echo "Use: laptop, bt-mic, bt-audio, wired, or list"
            return 1
            ;;
    esac
}

# ─── Boost mic for STT ────────────────────────────────────────────────────
cmd_boost() {
    local src
    src=$(pactl get-default-source 2>/dev/null)
    if [[ -z "$src" ]]; then
        log_err "No default source"
        return 1
    fi

    pactl set-source-mute "$src" 0
    pactl set-source-volume "$src" 100%
    log_ok "Mic boosted to 100%: $src"

    # Also try ALSA boost
    if amixer -c PCH sget 'Internal Mic Boost' &>/dev/null; then
        amixer -c PCH sset 'Internal Mic Boost' 80% &>/dev/null
        log_ok "ALSA Internal Mic Boost: 80%"
    fi
}

# ─── Restart STT daemon cleanly ──────────────────────────────────────────
cmd_restart_stt() {
    log_info "Stopping all STT daemon instances..."
    pkill -f 'claude_stt.daemon' 2>/dev/null || true
    sleep 1

    # Verify killed
    if pgrep -f 'claude_stt.daemon' &>/dev/null; then
        pkill -9 -f 'claude_stt.daemon' 2>/dev/null || true
        sleep 1
    fi

    # Clear stale PID
    rm -f ~/.claude/plugins/claude-stt/daemon.pid

    log_ok "STT daemon stopped. Use /claude-stt:start to restart."
}

# ─── Main ─────────────────────────────────────────────────────────────────
main() {
    local cmd="${1:-status}"
    shift || true

    case "$cmd" in
        status|s)       cmd_status ;;
        fix|f)          cmd_fix ;;
        switch|sw)      cmd_switch "$@" ;;
        boost|b)        cmd_boost ;;
        restart-stt|rs) cmd_restart_stt ;;
        diagnose|d)     cmd_status ;; # alias
        help|h|-h|--help)
            echo "audio-doctor.sh — Fix audio input for voice dictation"
            echo ""
            echo "Commands:"
            echo "  status       Show current audio input state"
            echo "  fix          Auto-fix common audio issues"
            echo "  switch <dev> Switch input (laptop|bt-mic|bt-audio|wired|list)"
            echo "  boost        Max out mic volume for STT"
            echo "  restart-stt  Kill and clean up STT daemon"
            echo "  help         Show this help"
            ;;
        *)
            log_err "Unknown command: $cmd"
            main help
            return 1
            ;;
    esac
}

main "$@"
