# Claude Code Configuration Backup

Last synced: **2026-03-02**

## Contents

| Folder | Description | Count |
|--------|-------------|-------|
| `skills/` | Custom skills with scripts, templates, references | 58 skills |
| `agents/` | Agent definitions (specialized AI personas) | 25 agents |
| `commands/` | Custom slash commands | 1 command |
| `plugins/` | Plugin registry (not cache) | 3 files |
| `mcp/` | MCP server configurations (secrets replaced with `${VAR}`) | 1 file |
| `settings/` | Global + local settings | 2 files |
| `CLAUDE.md` | Global instructions | |
| `ENV_CHECKLIST.md` | Environment requirements | |
| `SETUP_GUIDE.md` | Setup documentation | |
| `statusline.sh` | Status line script | |

## Restoration

```bash
# Quick restore
cp -r skills/* ~/.claude/skills/
cp -r agents/* ~/.claude/agents/
cp -r commands/* ~/.claude/commands/
cp settings/* ~/.claude/
cp plugins/* ~/.claude/plugins/
cp mcp/mcp.json ~/.claude/mcp.json
cp CLAUDE.md ~/.claude/
cp ENV_CHECKLIST.md ~/.claude/ 2>/dev/null
cp SETUP_GUIDE.md ~/.claude/ 2>/dev/null
cp statusline.sh ~/.claude/ 2>/dev/null
```

Then update `~/.claude/mcp.json` with real API keys for: `N8N_API_KEY`, `ATTIO_API_KEY`, `CLERK_API_KEY`.

## What's NOT Included

- API keys / credentials — re-authenticate with `claude login`
- Plugin cache — re-downloaded automatically
- Session data, debug logs, telemetry, history
