---
name: skill-manager
description: Meta-skill for managing the entire skills ecosystem. Inventory all skills/agents/plugins, detect duplicates, recommend the right tool for a task, identify gaps, discover new skills from the web, and run health checks.
user_invocable: true
---

# Skill Manager

Manage Guy's skills ecosystem across all 4 layers: global agents, global skills, installed plugins, and project-level skills.

## Trigger Keywords

manage skills, skill audit, what skills do I have, missing skills, skill gaps, organize skills, skill health, skill inventory, duplicate skills, find skills

## Commands

When invoked, ask the user which operation to run (or auto-detect from their message):

### 1. Inventory

Scan all layers and produce a categorized summary with counts.

```
Locations to scan:
- ~/.claude/agents/*.md           → Global agents
- ~/.claude/skills/*/SKILL.md     → Global skills
- ~/.claude/plugins/cache/        → Installed plugins (each has skills/)
- <project>/.claude/skills/       → Project-level skills (current project)
```

**Tools:** `Glob`, `Bash(ls)`, `Read` (for SKILL.md frontmatter)

Output format: table grouped by category with name, layer, one-line description.

### 2. Duplicate Detection

Compare skill names, descriptions, and trigger keywords across all layers. Flag:
- **Exact duplicates**: same skill name in multiple locations
- **Near-duplicates**: overlapping trigger keywords or descriptions (>70% overlap)
- **Layer conflicts**: agent + skill with same name or purpose

**Tools:** `Glob`, `Grep`, `Read`

### 3. Usage Advisor

Given a user task description, recommend the best skill/agent/plugin:
1. Check `~/.claude/skills/README.md` registry first
2. Match against trigger keywords
3. Explain why this tool is the best fit
4. Note alternatives if multiple options exist

**Tools:** `Read` (README.md), `Grep` (trigger keywords)

### 4. Gap Analysis

Compare current capabilities against Guy's business domains:
- AI agents & automation
- Sales & lead management
- Global trade & Export Arena
- SaaS development (Next.js, React, Drizzle, Vercel)
- Content & marketing
- Compliance & risk

Identify what's missing or underserved.

**Tools:** `Read` (README.md, context files), reasoning

### 5. Web Discovery

Search for new skills, plugins, or agents that could fill identified gaps:
- Apify Store (via `search-actors` MCP tool)
- GitHub (via `WebSearch`)
- Claude Code community plugins

**Tools:** `WebSearch`, `mcp__apify__search-actors`, `Agent(Explore)` for deep research

### 6. Health Check

Validate the ecosystem:
- Every skill directory has a valid `SKILL.md` with frontmatter (name, description)
- No orphaned directories (empty skill folders)
- `README.md` registry matches actual skills on disk
- Disabled plugins in `settings.json` are intentional (cross-reference with README.md)
- No broken agent references

**Tools:** `Glob`, `Read`, `Bash(ls)`, `Grep`

Output: pass/fail per check with actionable fix suggestions.

## Quick Reference

| Operation | Command |
|-----------|---------|
| Full inventory | `/skill-manager` → "inventory" |
| Find duplicates | `/skill-manager` → "duplicates" |
| What should I use for X? | `/skill-manager` → "advisor: <task>" |
| What am I missing? | `/skill-manager` → "gaps" |
| Find new skills | `/skill-manager` → "discover" |
| Validate everything | `/skill-manager` → "health" |

## Important Paths

| Path | Content |
|------|---------|
| `~/.claude/skills/README.md` | Skills registry (source of truth) |
| `~/.claude/settings.json` | Plugin enable/disable state |
| `~/.claude/agents/` | Global agent definitions |
| `~/.claude/skills/` | Global skill definitions |
| `~/.claude/plugins/cache/` | Installed plugin cache |
