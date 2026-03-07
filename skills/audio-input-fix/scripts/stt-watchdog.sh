#!/usr/bin/env bash
# stt-watchdog.sh — Monitor and auto-restart STT daemon, fix audio issues
# Intended to run as a systemd user service or from cron
set -euo pipefail

LOGFILE="$HOME/.claude/plugins/claude-stt/watchdog.log"
PIDFILE="$HOME/.claude/plugins/claude-stt/daemon.pid"
CHECK_INTERVAL="${1:-30}"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOGFILE"; }

fix_duplicate_daemons() {
    local count
    count=$(pgrep -fc 'claude_stt.daemon' 2>/dev/null || echo 0)
    if (( count > 1 )); then
        log "WARN: $count daemon instances found, killing all"
        pkill -f 'claude_stt.daemon' 2>/dev/null || true
        sleep 2
        rm -f "$PIDFILE"
        return 1
    fi
    return 0
}

ensure_mic_volume() {
    local src
    src=$(pactl get-default-source 2>/dev/null || echo "")
    [[ -z "$src" ]] && return

    local vol
    vol=$(pactl get-source-volume "$src" 2>/dev/null | grep -oP '\d+' | head -1 || echo 0)
    local muted
    muted=$(pactl get-source-mute "$src" 2>/dev/null | grep -oP '(yes|no)' || echo "no")

    if [[ "$muted" == "yes" ]]; then
        log "WARN: Mic was muted, unmuting"
        pactl set-source-mute "$src" 0
    fi

    if (( vol < 50 )); then
        log "WARN: Mic volume was ${vol}%, setting to 85%"
        pactl set-source-volume "$src" 85%
    fi
}

# Main watchdog loop
log "Watchdog started (interval: ${CHECK_INTERVAL}s)"

while true; do
    fix_duplicate_daemons || true
    ensure_mic_volume
    sleep "$CHECK_INTERVAL"
done
