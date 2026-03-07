# Config Sync

Manage Claude Code config backup and restore across machines.

## Trigger

Use when user says: "sync my config", "restore my claude config", "config status", "config diff", "pull my config", "push my config"

## Operations

### Status / Diff
Show what's different between local ~/.claude and the GitHub backup repo.

```bash
~/.claude/skills/config-sync/scripts/sync-status.sh
```

### Backup (Push)
Run the backup script manually (normally auto-runs on session end via hook).

```bash
~/.claude/backup-to-github.sh
```

### Restore (Pull)
Pull latest config from GitHub and apply to local machine.

```bash
# Preview changes first
~/.claude/restore-from-github.sh --dry-run

# Apply with confirmation prompt
~/.claude/restore-from-github.sh

# Apply without confirmation
~/.claude/restore-from-github.sh --force
```

## How It Works

- **Auto-backup**: A SessionEnd hook runs `backup-to-github.sh` after every session
- **Manual restore**: Run `restore-from-github.sh` to pull config to a new/different machine
- **Secrets**: All API keys, tokens, passwords are sanitized before pushing to GitHub
- **Self-contained**: Both scripts are backed up into the repo under `scripts/`

## Backed Up Items

| Item | Location in Repo |
|------|-----------------|
| skills/ | skills/ |
| agents/ | agents/ |
| commands/ | commands/ |
| settings.json | settings/settings.json |
| settings.local.json | settings/settings.local.json |
| config.json (sanitized) | settings/config.json |
| mcp.json (sanitized) | mcp/mcp.json |
| CLAUDE.md | CLAUDE.md |
| plugins metadata | plugins/ |
| statusline.sh | statusline.sh |
| backup script | scripts/backup-to-github.sh |
| restore script | scripts/restore-from-github.sh |

## Secret Handling

The backup script sanitizes any env var key matching: `*_KEY`, `*_TOKEN`, `*_SECRET`, `*_PASSWORD`, `*_AUTH`. Values are replaced with `${VAR_NAME}` placeholders. After restore, users must manually re-add their API keys.
