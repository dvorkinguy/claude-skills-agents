#!/bin/bash
# Show sync status between local ~/.claude and GitHub backup repo
REPO_DIR="$HOME/Documents/_projects/claude-skills-agents"
CLAUDE_DIR="$HOME/.claude"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "Backup repo not found at $REPO_DIR"
  echo "Run: git clone https://github.com/dvorkinguy/claude-skills-agents.git $REPO_DIR"
  exit 1
fi

echo "=== Config Sync Status ==="
echo "Local:  $CLAUDE_DIR"
echo "Repo:   $REPO_DIR"
echo ""

# Check repo git status
cd "$REPO_DIR"
REMOTE_STATUS=$(git fetch origin main --dry-run 2>&1)
LOCAL_BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "?")
LOCAL_AHEAD=$(git rev-list origin/main..HEAD --count 2>/dev/null || echo "?")

echo "Git: ahead=$LOCAL_AHEAD behind=$LOCAL_BEHIND"
echo ""

# Compare each sync target
compare() {
  local src="$1" dst="$2" label="$3"
  if [ -d "$src" ] && [ -d "$dst" ]; then
    local count
    count=$(diff -rq "$src" "$dst" 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
      echo "  CHANGED  $label ($count differences)"
    else
      echo "  OK       $label"
    fi
  elif [ -f "$src" ] && [ -f "$dst" ]; then
    if ! diff -q "$src" "$dst" >/dev/null 2>&1; then
      echo "  CHANGED  $label"
    else
      echo "  OK       $label"
    fi
  elif [ -e "$src" ] && [ ! -e "$dst" ]; then
    echo "  MISSING  $label (not in local)"
  elif [ ! -e "$src" ] && [ -e "$dst" ]; then
    echo "  NEW      $label (not in repo)"
  fi
}

echo "Local vs Repo:"
compare "$CLAUDE_DIR/skills" "$REPO_DIR/skills" "skills/"
compare "$CLAUDE_DIR/agents" "$REPO_DIR/agents" "agents/"
compare "$CLAUDE_DIR/commands" "$REPO_DIR/commands" "commands/"
compare "$CLAUDE_DIR/settings.json" "$REPO_DIR/settings/settings.json" "settings.json"
compare "$CLAUDE_DIR/settings.local.json" "$REPO_DIR/settings/settings.local.json" "settings.local.json"
compare "$CLAUDE_DIR/CLAUDE.md" "$REPO_DIR/CLAUDE.md" "CLAUDE.md"
compare "$CLAUDE_DIR/statusline.sh" "$REPO_DIR/statusline.sh" "statusline.sh"

echo ""
echo "Run 'backup-to-github.sh' to push local → repo"
echo "Run 'restore-from-github.sh --dry-run' to preview repo → local"
