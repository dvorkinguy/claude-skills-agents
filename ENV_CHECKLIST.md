# Required Environment Variables for MCP Servers

This document lists environment variables needed for MCP servers configured in `~/.claude/mcp.json`.

## MCP Server Requirements

| Server | Variable | Required | Description |
|--------|----------|----------|-------------|
| postgres | `DATABASE_URL` | Yes | PostgreSQL connection string |
| brave-search | `BRAVE_API_KEY` | Yes | Brave Search API key |
| slack | `SLACK_BOT_TOKEN` | Optional | Slack bot OAuth token |
| github | `GITHUB_TOKEN` | Recommended | GitHub personal access token |

## Setup Instructions

Add these to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
# PostgreSQL (Neon)
export DATABASE_URL="postgresql://user:password@host/database?sslmode=require"

# Brave Search API
export BRAVE_API_KEY="BSA..."

# Slack Bot (optional)
export SLACK_BOT_TOKEN="xoxb-..."

# GitHub (recommended)
export GITHUB_TOKEN="ghp_..."
```

## Getting API Keys

### Brave Search
1. Go to https://brave.com/search/api/
2. Sign up for API access
3. Copy your API key

### GitHub Token
1. Go to https://github.com/settings/tokens
2. Generate new token (classic) with `repo` scope
3. Copy the token

### Slack Bot Token
1. Go to https://api.slack.com/apps
2. Create or select your app
3. Go to OAuth & Permissions
4. Copy the Bot User OAuth Token

### PostgreSQL (Neon)
1. Go to https://console.neon.tech
2. Select your project
3. Copy the connection string from Dashboard

## Verification

After setting environment variables, restart your terminal and verify:

```bash
echo $DATABASE_URL
echo $BRAVE_API_KEY
echo $GITHUB_TOKEN
```

Then restart Claude Code to apply the changes to MCP servers.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MCP server won't connect | Check if env var is set: `echo $VAR_NAME` |
| Permission denied | Regenerate token with correct scopes |
| Connection timeout | Check network/firewall settings |

## HTTP-Based MCP Servers (No Env Vars Needed)

These servers authenticate via their web interface:

| Server | URL | Auth Method |
|--------|-----|-------------|
| stripe | https://mcp.stripe.com | Stripe account login |
| apify | https://mcp.apify.com | Apify account login |
