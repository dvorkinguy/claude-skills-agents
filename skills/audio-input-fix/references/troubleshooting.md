# Audio Input Troubleshooting Reference

## System: Pop!_OS 22.04, PipeWire 1.0.3, X11, Intel i5-5200U

## Known Hardware

| Device | ALSA Card | Source Name | Notes |
|--------|-----------|-------------|-------|
| Laptop mic | PCH (card 2) | `alsa_input.pci-0000_00_1b.0.analog-stereo` | ALC255, always available |
| USB camera mic | Camera (card 1) | `alsa_input.usb-BC-FAY-250426_USB_2.0_Camera-02.mono-fallback` | Low quality, avoid |
| Sony WH-CH520 | bluez | `bluez_input.*` (only in HFP mode) | A2DP=no mic, HFP=mic |
| OnePlus Nord Buds 3 | bluez | `bluez_input.*` (only in HFP mode) | Same as above |

## Common Issues & Fixes

### 1. "No speech detected" / Very quiet mic (-40dB to -55dB)
**Cause**: PulseAudio source volume defaults to 19% on boot
**Fix**:
```bash
pactl set-source-volume @DEFAULT_SOURCE@ 85%
pactl set-source-mute @DEFAULT_SOURCE@ 0
# Also try ALSA boost:
amixer -c PCH sset 'Internal Mic Boost' 50%
```

### 2. Bluetooth headphones connected but no mic
**Cause**: Bluetooth defaults to A2DP profile (high quality stereo output, no mic input)
**Fix**: Switch to HFP/HSP headset profile:
```bash
# Find bluetooth card
CARD=$(pactl list cards short | grep bluez | awk '{print $2}')
# Switch to headset profile (enables mic, reduces audio quality)
pactl set-card-profile "$CARD" headset-head-unit-msbc  # mSBC = 16kHz
# or fallback:
pactl set-card-profile "$CARD" headset-head-unit       # CVSD = 8kHz
```
**Note**: HFP mode reduces audio output quality to mono 8/16kHz. Switch back to A2DP when done dictating.

### 3. Duplicate STT daemon instances
**Cause**: `/claude-stt:start` called multiple times without stopping
**Fix**:
```bash
pkill -f 'claude_stt.daemon'
rm -f ~/.claude/plugins/claude-stt/daemon.pid
# Then restart with /claude-stt:start
```

### 4. Xlib BrokenPipeError crash
**Cause**: pynput uses X11 Record extension which breaks when display connection drops (screen lock, suspend)
**Symptoms**: `Xlib.error.ConnectionClosedError: Display connection closed by server`
**Fix**: This is a known pynput bug on X11. The daemon must be restarted after screen lock/unlock.
**Workaround**: Use `stt-watchdog.sh` to auto-monitor and restart.

### 5. Moonshine >64s assertion error
**Cause**: Moonshine ONNX model only supports 0.1-64s audio segments
**Symptoms**: `AssertionError: Moonshine models support audio segments that are between 0.1s and 64s`
**Fix**: Don't leave recording running >60s. Use toggle mode and stop promptly.
Alternative: Switch to whisper engine which handles longer recordings.

### 6. Mic volume resets on reboot
**Cause**: PipeWire/WirePlumber may not persist source volume
**Fix**: Create a systemd user service or login script:
```bash
# Add to ~/.profile or create systemd service
pactl set-source-volume alsa_input.pci-0000_00_1b.0.analog-stereo 85%
pactl set-source-mute alsa_input.pci-0000_00_1b.0.analog-stereo 0
```

### 7. Wrong mic selected after plugging/unplugging devices
**Cause**: PipeWire auto-switches default source when USB devices connect
**Fix**: Explicitly set default source:
```bash
pactl set-default-source alsa_input.pci-0000_00_1b.0.analog-stereo
```

## Optimal STT Config

For `~/.claude/plugins/claude-stt/config.toml`:
```toml
[claude-stt]
hotkey = "ctrl+shift+space"
mode = "toggle"
engine = "whisper"             # Better accuracy than moonshine
moonshine_model = "moonshine/base"
whisper_model = "base"         # Good balance of speed/quality on i5 CPU
sample_rate = 16000
max_recording_seconds = 60     # Keep under 64 for moonshine
output_mode = "auto"
sound_effects = true
```

## Volume Levels Guide

| Scenario | PulseAudio Volume | ALSA Boost | Expected dB |
|----------|-------------------|------------|-------------|
| Laptop mic, quiet room | 65% | 30% | -25 to -15 dB |
| Laptop mic, noisy | 50% | 20% | -20 to -10 dB |
| BT headset mic | 100% | N/A | -20 to -10 dB |
| Wired headset | 70% | N/A | -25 to -15 dB |

Ideal for STT: -30 dB to -10 dB. Below -35 dB = "no speech detected".
