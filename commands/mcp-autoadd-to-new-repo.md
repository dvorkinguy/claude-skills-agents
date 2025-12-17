#!/bin/bash
# Add standard MCP servers to this repository by creating or updating .mcp.json with context7, playwright, airtable, github, and sentry servers.
# Create or update .mcp.json with standard MCP servers
if [ -f .mcp.json ]; then
  echo "Updating existing .mcp.json..."
  # Backup existing file
  cp .mcp.json .mcp.json.backup
else
  echo "Creating new .mcp.json..."
fi

# Create the MCP configuration
cat > .mcp.json << 'EOF'
{
  "mcp": {
    "context7": "npx -y @upstash/context7-mcp",
    "playwright": "npx @playwright/mcp@latest",
    "airtable": "npx -y airtable-mcp-server",
    "github": "https://api.githubcopilot.com/mcp/",
    "sentry": "https://mcp.sentry.dev/mcp"
  }
}
EOF

echo "✅ Added standard MCP servers to .mcp.json"
echo "Servers added: context7, playwright, airtable, github, sentry"