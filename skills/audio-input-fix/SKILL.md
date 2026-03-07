---
name: audio-input-fix
description: "Diagnose and fix audio input problems on Pop!_OS/PipeWire/X11 for voice dictation in Claude Code. Use when: (1) microphone not working or too quiet, (2) STT returns 'no speech detected', (3) switching between laptop mic, wired headset, or Bluetooth headphones, (4) claude-stt daemon crashes or duplicates, (5) Bluetooth headset mic not available, (6) mic volume resets on reboot, (7) any voice input or audio recording issue."
---

# Audio Input Fix

Fix audio input for voice dictation on this machine (Pop!_OS 22.04, PipeWire 1.0.3, X11, Intel i5-5200U).

## Quick Fix (90% of issues)

Run the all-in-one diagnostic and fix script:

```bash
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh fix
```

This auto-fixes: low mic volume, muted mic, duplicate STT daemons, and selects the best input source.

## Common Tasks

### Check status
```bash
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh status
```

### Switch audio input device
```bash
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh switch laptop    # Internal mic
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh switch bt-mic    # Bluetooth headset mic (switches to HFP)
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh switch bt-audio  # Back to A2DP (hi-fi, no mic)
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh switch wired     # Wired/USB headset
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh switch list      # Show all sources
```

### Boost mic volume for STT
```bash
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh boost
```

### Fix duplicate STT daemons
```bash
bash ~/.claude/skills/audio-input-fix/scripts/audio-doctor.sh restart-stt
```
Then restart with `/claude-stt:start`.

### Persist mic volume across reboots
```bash
bash ~/.claude/skills/audio-input-fix/scripts/setup-mic-persist.sh
```
Installs a systemd user service that sets mic to 85% on login.

## Key Facts

- **Internal mic source**: `alsa_input.pci-0000_00_1b.0.analog-stereo` (ALC255)
- **Bluetooth profiles**: A2DP = high quality output, no mic. HFP/HSP = mic enabled, lower audio quality.
- **Optimal PulseAudio volume**: 65% for laptop mic (85% clips!), 100% for BT mic, 70% for wired
- **STT needs**: Audio level above -35 dB. Below that = "no speech detected"
- **Moonshine limit**: Max 64 seconds per recording. Keep dictation under 60s.
- **X11 crash**: pynput breaks on screen lock. Restart daemon after unlock.

## Troubleshooting

For detailed issue-specific fixes, see [references/troubleshooting.md](references/troubleshooting.md).

## STT Plugin Patch Persistence

Custom patches to `sounds.py`, `keyboard.py`, and `whisper.py` are stored in `patches/` (unified diffs) and `patched-files/` (full fallback copies). These are auto-applied on every session start via a SessionStart hook.

### Manual re-apply after cache clear
```bash
bash ~/.claude/skills/audio-input-fix/scripts/apply-stt-patches.sh
```

### What's patched
- **sounds.py** — Custom start/stop sounds (`message-new-instant.oga`, `power-unplug.oga`) + louder start via `paplay --volume 90000`
- **keyboard.py** — Removed all `play_sound("complete")` calls (no bell after text output)
- **whisper.py** — Better transcribe params: `language="en"`, `beam_size=5`, `best_of=3`, `vad_filter=True`, `temperature=0.0`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/audio-doctor.sh` | Main diagnostic/fix tool (status, fix, switch, boost) |
| `scripts/apply-stt-patches.sh` | Re-apply STT plugin patches after cache clear/update |
| `scripts/setup-mic-persist.sh` | Install systemd service for boot-time mic volume |
| `scripts/stt-watchdog.sh` | Background monitor to auto-fix volume and duplicate daemons |
