#!/bin/bash
# Restore Claude Code config from GitHub backup repo
set -e

REPO_DIR="$HOME/Documents/_projects/claude-skills-agents"
CLAUDE_DIR="$HOME/.claude"
FORCE=false
DRY_RUN=false

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=true ;;
    --dry-run) DRY_RUN=true ;;
    --help|-h)
      echo "Usage: restore-from-github.sh [--force] [--dry-run]"
      echo ""
      echo "Restore Claude Code config from GitHub backup repo."
      echo ""
      echo "Options:"
      echo "  --dry-run   Show what would change without applying"
      echo "  --force     Skip confirmation prompt"
      echo "  --help      Show this help"
      exit 0
      ;;
  esac
done

# Ensure repo exists and is up to date
if [ ! -d "$REPO_DIR/.git" ]; then
  echo "Cloning backup repo..."
  git clone https://github.com/dvorkinguy/claude-skills-agents.git "$REPO_DIR" || exit 1
else
  echo "Pulling latest from GitHub..."
  cd "$REPO_DIR"
  git pull origin main --quiet || { echo "ERROR: git pull failed"; exit 1; }
fi

echo ""
echo "=== Restore Summary ==="
echo ""

# Show diff for each sync target
show_diff() {
  local src="$1" dst="$2" label="$3"
  if [ -d "$src" ] && [ -d "$dst" ]; then
    local changes
    changes=$(diff -rq "$src" "$dst" 2>/dev/null | head -20)
    if [ -n "$changes" ]; then
      echo "[$label] Changes detected:"
      echo "$changes" | sed 's/^/  /'
      echo ""
    fi
  elif [ -d "$src" ] && [ ! -d "$dst" ]; then
    echo "[$label] NEW - will be created"
    echo ""
  elif [ -f "$src" ] && [ -f "$dst" ]; then
    if ! diff -q "$src" "$dst" >/dev/null 2>&1; then
      echo "[$label] Modified"
      diff --color=auto "$dst" "$src" 2>/dev/null | head -10
      echo ""
    fi
  elif [ -f "$src" ] && [ ! -f "$dst" ]; then
    echo "[$label] NEW - will be created"
    echo ""
  fi
}

show_diff "$REPO_DIR/skills" "$CLAUDE_DIR/skills" "skills/"
show_diff "$REPO_DIR/agents" "$CLAUDE_DIR/agents" "agents/"
show_diff "$REPO_DIR/commands" "$CLAUDE_DIR/commands" "commands/"
show_diff "$REPO_DIR/settings/settings.json" "$CLAUDE_DIR/settings.json" "settings.json"
show_diff "$REPO_DIR/settings/settings.local.json" "$CLAUDE_DIR/settings.local.json" "settings.local.json"
show_diff "$REPO_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"
show_diff "$REPO_DIR/statusline.sh" "$CLAUDE_DIR/statusline.sh" "statusline.sh"
show_diff "$REPO_DIR/plugins" "$CLAUDE_DIR/plugins" "plugins/"

echo "=== Skipped (secrets - re-add manually) ==="
echo "  - mcp.json (contains placeholder env vars, not real keys)"
echo "  - config.json (contains placeholder API key)"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "Dry run complete. No changes applied."
  exit 0
fi

# Confirm unless --force
if [ "$FORCE" != true ]; then
  read -p "Apply restore? [y/N] " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
fi

echo "Restoring..."

# Restore directories
[ -d "$REPO_DIR/skills" ] && rsync -a --delete "$REPO_DIR/skills/" "$CLAUDE_DIR/skills/"
[ -d "$REPO_DIR/agents" ] && rsync -a --delete "$REPO_DIR/agents/" "$CLAUDE_DIR/agents/"
[ -d "$REPO_DIR/commands" ] && rsync -a --delete "$REPO_DIR/commands/" "$CLAUDE_DIR/commands/"

# Restore individual files
[ -f "$REPO_DIR/settings/settings.json" ] && cp "$REPO_DIR/settings/settings.json" "$CLAUDE_DIR/settings.json"
[ -f "$REPO_DIR/settings/settings.local.json" ] && cp "$REPO_DIR/settings/settings.local.json" "$CLAUDE_DIR/settings.local.json"
[ -f "$REPO_DIR/CLAUDE.md" ] && cp "$REPO_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
[ -f "$REPO_DIR/ENV_CHECKLIST.md" ] && cp "$REPO_DIR/ENV_CHECKLIST.md" "$CLAUDE_DIR/ENV_CHECKLIST.md"
[ -f "$REPO_DIR/SETUP_GUIDE.md" ] && cp "$REPO_DIR/SETUP_GUIDE.md" "$CLAUDE_DIR/SETUP_GUIDE.md"
[ -f "$REPO_DIR/statusline.sh" ] && cp "$REPO_DIR/statusline.sh" "$CLAUDE_DIR/statusline.sh"

# Restore plugins (metadata only, not cache)
mkdir -p "$CLAUDE_DIR/plugins"
[ -f "$REPO_DIR/plugins/installed_plugins.json" ] && cp "$REPO_DIR/plugins/installed_plugins.json" "$CLAUDE_DIR/plugins/installed_plugins.json"
[ -f "$REPO_DIR/plugins/known_marketplaces.json" ] && cp "$REPO_DIR/plugins/known_marketplaces.json" "$CLAUDE_DIR/plugins/known_marketplaces.json"
[ -f "$REPO_DIR/plugins/config.json" ] && cp "$REPO_DIR/plugins/config.json" "$CLAUDE_DIR/plugins/config.json"

# Restore scripts
[ -f "$REPO_DIR/scripts/backup-to-github.sh" ] && cp "$REPO_DIR/scripts/backup-to-github.sh" "$CLAUDE_DIR/backup-to-github.sh" && chmod +x "$CLAUDE_DIR/backup-to-github.sh"
[ -f "$REPO_DIR/scripts/restore-from-github.sh" ] && cp "$REPO_DIR/scripts/restore-from-github.sh" "$CLAUDE_DIR/restore-from-github.sh" && chmod +x "$CLAUDE_DIR/restore-from-github.sh"

echo ""
echo "Restore complete."
echo ""
echo "MANUAL STEPS REQUIRED:"
echo "  1. Add your API keys to ~/.claude/mcp.json"
echo "  2. Add your Anthropic API key to ~/.claude/config.json"
echo "  3. Restart Claude Code to pick up changes"
