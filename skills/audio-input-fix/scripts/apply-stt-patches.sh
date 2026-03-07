#!/usr/bin/env bash
# Apply STT plugin patches to the cache directory.
# Survives plugin updates and cache clears.
#
# Usage:
#   bash apply-stt-patches.sh          # verbose output
#   bash apply-stt-patches.sh --quiet  # only warnings/errors (for hooks)

set -euo pipefail

QUIET=false
[[ "${1:-}" == "--quiet" ]] && QUIET=true

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PATCHES_DIR="$SKILL_DIR/patches"
FALLBACK_DIR="$SKILL_DIR/patched-files"

log()  { $QUIET || echo "[INFO] $*"; }
warn() { echo "[WARN] $*" >&2; }
err()  { echo "[ERROR] $*" >&2; }

# --- Locate cache directory (handles version changes) ---
CACHE_BASE="$HOME/.claude/plugins/cache/jarrodwatts-claude-stt"
if [[ ! -d "$CACHE_BASE" ]]; then
    log "Cache dir not found ($CACHE_BASE). Nothing to patch."
    exit 0
fi

# Find the claude_stt package dir inside any version folder
STT_PKG=$(find "$CACHE_BASE" -type d -name claude_stt -path "*/src/claude_stt" | head -1)
if [[ -z "$STT_PKG" ]]; then
    warn "Could not find src/claude_stt inside $CACHE_BASE"
    exit 0
fi

CACHE_SRC="$(dirname "$STT_PKG")"  # .../src
log "Cache source: $CACHE_SRC"

# --- Patch definitions: patch_file  target_relative_path  fallback_file ---
declare -a PATCH_DEFS=(
    "sounds.py.patch          claude_stt/sounds.py            sounds.py"
    "keyboard.py.patch        claude_stt/keyboard.py          keyboard.py"
    "whisper.py.patch         claude_stt/engines/whisper.py    whisper.py"
    "daemon_service.py.patch  claude_stt/daemon_service.py     daemon_service.py"
)

PATCHED=0
SKIPPED=0
FAILED=0

for def in "${PATCH_DEFS[@]}"; do
    read -r patch_file rel_path fallback_file <<< "$def"
    target="$CACHE_SRC/$rel_path"
    patch_path="$PATCHES_DIR/$patch_file"
    fallback_path="$FALLBACK_DIR/$fallback_file"

    if [[ ! -f "$target" ]]; then
        warn "$rel_path not found in cache, skipping"
        ((FAILED++)) || true
        continue
    fi

    # Check if already patched by diffing against fallback
    if [[ -f "$fallback_path" ]] && diff -q "$target" "$fallback_path" >/dev/null 2>&1; then
        log "[SKIP] $rel_path — already patched"
        ((SKIPPED++)) || true
        continue
    fi

    # Try unified patch (dry-run first)
    if [[ -f "$patch_path" ]] && patch --dry-run -s -p1 -d "$CACHE_SRC" < "$patch_path" >/dev/null 2>&1; then
        patch -s -p1 -d "$CACHE_SRC" < "$patch_path"
        log "[OK] Patched $rel_path via diff"
        ((PATCHED++)) || true
    elif [[ -f "$fallback_path" ]]; then
        # Patch doesn't apply cleanly — copy full fallback file
        cp "$fallback_path" "$target"
        warn "[OK] Copied fallback for $rel_path (patch didn't apply cleanly — upstream may have changed)"
        ((PATCHED++)) || true
    else
        err "No patch or fallback available for $rel_path"
        ((FAILED++)) || true
    fi
done

# Clear __pycache__ so Python picks up changes
find "$CACHE_SRC" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

log "Done: $PATCHED patched, $SKIPPED already applied, $FAILED failed"
exit 0
