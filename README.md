# Claude Code Configuration Backup

This folder contains a backup of Claude Code configuration for restoration on another machine.

## Contents

| Folder | Description | Count |
|--------|-------------|-------|
| `skills/` | Custom skills with scripts, templates, references | 13 skills |
| `agents/` | Agent definitions (specialized AI personas) | 26 agents |
| `commands/` | Custom slash commands | 1 command |
| `plugins/` | Plugin registry (not cache) | 3 files |
| `mcp/` | MCP server configurations | 3 files |
| `settings/` | Global settings and instructions | 3 files |

## Restoration Instructions

### Prerequisites
1. Install Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
2. Authenticate: `claude login`

### Step 1: Restore Skills
```bash
cp -r skills/* ~/.claude/skills/
```

### Step 2: Restore Agents
```bash
cp -r agents/* ~/.claude/agents/
```

### Step 3: Restore Commands
```bash
mkdir -p ~/.claude/commands/
cp -r commands/* ~/.claude/commands/
```

### Step 4: Restore Settings
```bash
cp settings/CLAUDE.md ~/.claude/
cp settings/settings.json ~/.claude/
cp settings/settings.local.json ~/.claude/
```

### Step 5: Restore Plugin Configuration
```bash
mkdir -p ~/.claude/plugins/
cp plugins/* ~/.claude/plugins/
```

Then reinstall plugins:
```bash
claude plugins install
```

### Step 6: Restore MCP Configurations

**For Claude Code CLI:**
```bash
mkdir -p ~/.config/claude-code/
cp mcp/claude-code-mcp.json ~/.config/claude-code/mcp.json
```

**For Claude Desktop (if using):**
```bash
mkdir -p ~/.config/claude-desktop/
cp mcp/claude_desktop_config.json ~/.config/claude-desktop/
```

**For VS Code Extension (if using):**
```bash
mkdir -p ~/.config/Code/User/
cp mcp/vscode-mcp.json ~/.config/Code/User/mcp.json
```

### Step 7: Update MCP Server Paths

After restoring, edit the MCP config files to update any absolute paths that reference the old machine's directory structure.

## What's NOT Included

- **API Keys** (`~/.claude/config.json`) - Re-authenticate with `claude login`
- **OAuth Credentials** (`~/.claude/.credentials.json`) - Re-authenticate
- **Plugin Cache** - Plugins will be re-downloaded from marketplaces
- **Session Data** - Regenerates automatically
- **Debug Logs** - Not needed

## Quick Restore Script

Create a script `restore-claude.sh`:
```bash
#!/bin/bash
BACKUP_DIR="$(dirname "$0")"

# Create directories
mkdir -p ~/.claude/{skills,agents,commands,plugins}
mkdir -p ~/.config/{claude-code,claude-desktop}
mkdir -p ~/.config/Code/User

# Copy configuration
cp -r "$BACKUP_DIR/skills/"* ~/.claude/skills/
cp -r "$BACKUP_DIR/agents/"* ~/.claude/agents/
cp -r "$BACKUP_DIR/commands/"* ~/.claude/commands/ 2>/dev/null
cp "$BACKUP_DIR/settings/CLAUDE.md" ~/.claude/
cp "$BACKUP_DIR/settings/settings.json" ~/.claude/ 2>/dev/null
cp "$BACKUP_DIR/settings/settings.local.json" ~/.claude/ 2>/dev/null
cp "$BACKUP_DIR/plugins/"* ~/.claude/plugins/ 2>/dev/null
cp "$BACKUP_DIR/mcp/claude-code-mcp.json" ~/.config/claude-code/mcp.json 2>/dev/null
cp "$BACKUP_DIR/mcp/claude_desktop_config.json" ~/.config/claude-desktop/ 2>/dev/null
cp "$BACKUP_DIR/mcp/vscode-mcp.json" ~/.config/Code/User/mcp.json 2>/dev/null

echo "Claude Code configuration restored!"
echo "Next steps:"
echo "  1. Run 'claude login' to authenticate"
echo "  2. Update paths in MCP configs if needed"
echo "  3. Run 'claude plugins install' to restore plugins"
```

## Backup Date
Created: $(date +%Y-%m-%d)
