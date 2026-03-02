---
name: skill-suggestion
description: Scan project dependencies and suggest relevant Claude Code skills. Use when starting a new project or checking for missing skills.
---

# Skill Suggestion

Scans the project's package.json files and suggests relevant Claude Code skills and MCP tools.

## Usage

Run the project's suggest-skills script:

```bash
./scripts/suggest-skills.sh
```

If the script doesn't exist, create it by copying from a template or inform the user to run:

```bash
# Quick inline version
echo "📦 Scanning for skills..."
DEPS=$(find . -name "package.json" -not -path "*/node_modules/*" -exec cat {} \; 2>/dev/null)

echo "$DEPS" | grep -q '"next"' && echo "✅ nextjs-pro"
echo "$DEPS" | grep -q '"react"' && echo "✅ react-pro"
echo "$DEPS" | grep -q '"drizzle' && echo "✅ drizzle-migrations"
echo "$DEPS" | grep -q '"playwright' && echo "✅ webapp-testing"
echo "$DEPS" | grep -q '"tailwind' && echo "✅ ui-designer"
echo "$DEPS" | grep -q '"stripe' && echo "✅ stripe-integration"
echo "$DEPS" | grep -q '"@supabase' && echo "✅ supabase-specialist"
echo "$DEPS" | grep -q '"@clerk' && echo "💡 Use context7 MCP for Clerk docs"

echo ""
echo "Add missing skills to CLAUDE.md '🎯 Project Skills' table"
```

## Output

The script outputs:
- ✅ Detected skills based on dependencies
- 🔧 Recommended MCP servers
- Instructions to update CLAUDE.md
