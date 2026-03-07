#!/bin/bash
# Auto-sync Claude Code config to GitHub backup repo
REPO_DIR="$HOME/Documents/_projects/claude-skills-agents"

# Ensure repo exists locally
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone https://github.com/dvorkinguy/claude-skills-agents.git "$REPO_DIR" 2>/dev/null || exit 0
fi

# Sync content
rsync -a --delete ~/.claude/skills/ "$REPO_DIR/skills/"
rsync -a --delete ~/.claude/agents/ "$REPO_DIR/agents/"
rsync -a --delete ~/.claude/commands/ "$REPO_DIR/commands/"
mkdir -p "$REPO_DIR"/{settings,mcp,plugins,scripts}
cp ~/.claude/settings.json "$REPO_DIR/settings/settings.json" 2>/dev/null
cp ~/.claude/settings.local.json "$REPO_DIR/settings/settings.local.json" 2>/dev/null
cp ~/.claude/CLAUDE.md "$REPO_DIR/CLAUDE.md" 2>/dev/null
cp ~/.claude/ENV_CHECKLIST.md "$REPO_DIR/ENV_CHECKLIST.md" 2>/dev/null
cp ~/.claude/SETUP_GUIDE.md "$REPO_DIR/SETUP_GUIDE.md" 2>/dev/null
cp ~/.claude/statusline.sh "$REPO_DIR/statusline.sh" 2>/dev/null
cp ~/.claude/plugins/installed_plugins.json "$REPO_DIR/plugins/installed_plugins.json" 2>/dev/null
cp ~/.claude/plugins/known_marketplaces.json "$REPO_DIR/plugins/known_marketplaces.json" 2>/dev/null
cp ~/.claude/plugins/config.json "$REPO_DIR/plugins/config.json" 2>/dev/null

# Copy and sanitize mcp.json (generic pattern: any KEY, TOKEN, SECRET, PASSWORD)
cp ~/.claude/mcp.json "$REPO_DIR/mcp/mcp.json" 2>/dev/null
if [ -f "$REPO_DIR/mcp/mcp.json" ]; then
  sed -i -E 's/"([^"]*(_KEY|_TOKEN|_SECRET|_PASSWORD|_AUTH))": "[^"]*"/"\1": "${\1}"/g' "$REPO_DIR/mcp/mcp.json"
fi

# Copy and sanitize config.json (API key structure without actual keys)
cp ~/.claude/config.json "$REPO_DIR/settings/config.json" 2>/dev/null
if [ -f "$REPO_DIR/settings/config.json" ]; then
  python3 -c "
import json, sys
try:
    with open('$REPO_DIR/settings/config.json') as f:
        d = json.load(f)
    if 'primaryApiKey' in d:
        d['primaryApiKey'] = '\${ANTHROPIC_API_KEY}'
    d.pop('customApiKeyResponses', None)
    with open('$REPO_DIR/settings/config.json', 'w') as f:
        json.dump(d, f, indent=2)
except Exception:
    pass
" 2>/dev/null
fi

# Self-backup: copy this script and restore script into the repo
cp ~/.claude/backup-to-github.sh "$REPO_DIR/scripts/backup-to-github.sh" 2>/dev/null
cp ~/.claude/restore-from-github.sh "$REPO_DIR/scripts/restore-from-github.sh" 2>/dev/null

# Commit and push if changes exist
cd "$REPO_DIR"
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "auto-sync $(date +%Y-%m-%d_%H:%M)" --quiet
  git push origin main --quiet 2>/dev/null
fi
