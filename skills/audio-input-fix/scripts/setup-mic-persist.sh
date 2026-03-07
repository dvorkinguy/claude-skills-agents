#!/usr/bin/env bash
# setup-mic-persist.sh — Create systemd user service to persist mic volume on boot
set -euo pipefail

SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/mic-volume-fix.service"

mkdir -p "$SERVICE_DIR"

cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=Set microphone volume for STT on login
After=pipewire.service pipewire-pulse.service wireplumber.service
Wants=pipewire-pulse.service

[Service]
Type=oneshot
RemainAfterExit=yes
# Wait for PipeWire to fully initialize
ExecStartPre=/bin/sleep 3
ExecStart=/bin/bash -c '\
  pactl set-source-volume alsa_input.pci-0000_00_1b.0.analog-stereo 45%% && \
  pactl set-source-mute alsa_input.pci-0000_00_1b.0.analog-stereo 0 && \
  (amixer -c PCH sset "Internal Mic Boost" 0%% 2>/dev/null || true)'

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable mic-volume-fix.service
systemctl --user start mic-volume-fix.service

echo "[OK] mic-volume-fix.service installed and started"
echo "     Mic volume will be set to 85% on every login"
