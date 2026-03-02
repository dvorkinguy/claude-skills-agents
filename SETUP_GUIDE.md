# Claude Code Global Setup Guide

**Last Updated:** 2025-12-01

This guide documents your global Claude Code setup with skills and agents available across all projects.

---

## Directory Structure

```
~/.claude/
├── agents/              # 20 global agents
├── skills/              # 5 global skills
├── commands/            # Global slash commands
├── CLAUDE.md           # Global instructions
└── SETUP_GUIDE.md      # This file
```

---

## Global Skills (5)

Skills are **tool-based** capabilities with scripts, templates, and documentation.
Located in: `~/.claude/skills/`

### 1. n8n-workflow-builder
**When to use:** Creating n8n automation workflows, webhook integrations
**Contains:**
- SKILL.md - Workflow structure, node types, best practices
- scripts/validate_workflow.py - Validates workflow JSON
- templates/workflow_template.json - Starter template

**Example usage:** "Create an n8n workflow that triggers on webhook and sends data to Slack"

### 2. stripe-integration
**When to use:** Implementing Stripe payments, subscriptions, webhooks
**Contains:**
- SKILL.md - Setup guide, checkout sessions, webhook handling
- scripts/verify_webhook.py - Webhook signature verification
- templates/webhook_handler.ts - Complete Next.js webhook handler

**Example usage:** "Add Stripe subscription checkout to my SaaS"

### 3. supabase-rls
**When to use:** Creating Row Level Security policies, securing Supabase tables
**Contains:**
- SKILL.md - RLS patterns (user-owned, team-based, role-based)
- templates/policies.sql - Multi-tenant RLS policy examples

**Example usage:** "Create RLS policies for a team-based project management app"

### 4. rtl-css
**When to use:** Building RTL layouts for Hebrew/Arabic, fixing RTL issues
**Contains:**
- SKILL.md - Logical properties guide, Next.js RTL setup
- scripts/audit_rtl.sh - Scans codebase for RTL violations

**Example usage:** "Audit my codebase for RTL compliance"

### 5. drizzle-migrations
**When to use:** Creating Drizzle schemas, running migrations
**Contains:**
- SKILL.md - Schema patterns, migration workflow, troubleshooting
- templates/schema_template.ts - Multi-tenant SaaS schema template

**Example usage:** "Create a Drizzle schema for users and teams"

---

## Global Agents (20)

Agents are **specialized AI assistants** for specific tasks.
Located in: `~/.claude/agents/`

### Generic Programming Agents (11)
| Agent | Use Case |
|-------|----------|
| **accessibility-checker** | WCAG compliance, a11y audits |
| **agent-organizer** | Meta-agent for coordinating multiple agents |
| **api-documentation** | OpenAPI specs, SDK generation |
| **architecture-planner** | System design, folder structure |
| **debugger** | Error diagnosis, troubleshooting |
| **llm-engineer** | RAG systems, prompt engineering, AI integrations |
| **nextjs-pro** | Next.js 15 App Router, RSC, Server Actions |
| **react-pro** | React 19, hooks, performance optimization |
| **sql-expert** | PostgreSQL queries, database design |
| **typescript-pro** | TypeScript patterns, type safety |
| **ux-researcher** | User research, journey maps |

### Stack-Specific Agents (9)
| Agent | Use Case |
|-------|----------|
| **automation-architect** | n8n, Make.com integrations |
| **drizzle-specialist** | Drizzle ORM for Neon PostgreSQL |
| **i18n-rtl** | RTL/i18n for Hebrew and Arabic |
| **mobile-first** | Responsive design, mobile-first CSS |
| **payment-integration** | Stripe subscriptions, webhooks |
| **performance-auditor** | Core Web Vitals, bundle optimization |
| **supabase-specialist** | Supabase Auth, Storage, RLS, Realtime |
| **tdd-specialist** | Test-Driven Development workflows |
| **ui-designer** | shadcn/ui, Tailwind design systems |

---

## Skills vs Agents: When to Use What

### Use a SKILL when:
- You need executable scripts or templates
- Working with specific tools (n8n, Stripe, Drizzle)
- You want validation/audit capabilities
- The task involves file generation from templates

**Example:** "Create an n8n workflow" → Uses `n8n-workflow-builder` skill

### Use an AGENT when:
- You need specialized expertise and reasoning
- Working with a technology stack (React, Next.js, Supabase)
- Complex problem-solving or architecture decisions
- Code review, debugging, or refactoring

**Example:** "Debug this React performance issue" → Uses `react-pro` agent

---

## Project-Specific Setup

Your current project (DrillMD) has these **project-specific** agents in `.claude/agents/`:

| Agent | Why Project-Specific |
|-------|---------------------|
| **code-reviewer** | Knows your project's code style and patterns |
| **security-auditor** | Familiar with your security requirements |
| **security-scanner** | Configured for your project structure |
| **test-runner** | Knows your test setup and paths |
| **docs-writer** | Understands your documentation structure |

**Decision:** Keep these in `.claude/agents/` because they're customized for this specific project.

---

## How Claude Uses Skills and Agents

### Automatic Discovery
Claude automatically:
1. Reads skill names and descriptions at startup
2. Loads relevant skills when you ask matching questions
3. Invokes agents when tasks match their expertise

### Example Flow

**You ask:** "Add Stripe subscriptions to my Next.js app"

**Claude:**
1. ✅ Detects `stripe-integration` skill (payment flows)
2. ✅ Detects `nextjs-pro` agent (Next.js expertise)
3. ✅ Loads skill templates and agent knowledge
4. ✅ Generates implementation using both

---

## Adding New Skills/Agents

### Add a New Global Skill
```bash
mkdir -p ~/.claude/skills/my-new-skill/{scripts,templates}
```

Create `~/.claude/skills/my-new-skill/SKILL.md`:
```markdown
---
name: my-new-skill
description: Brief description of when to use this skill
---

# Skill Content
...
```

### Add a New Global Agent
Create `~/.claude/agents/my-new-agent.md`:
```markdown
You are an expert in [DOMAIN].

Use when: [SCENARIOS]

Your responsibilities:
- [TASK 1]
- [TASK 2]

Guidelines:
- [GUIDELINE 1]
- [GUIDELINE 2]
```

---

## Maintenance

### Update Skills
Skills can be updated by editing files in `~/.claude/skills/`:
- Update SKILL.md for documentation changes
- Modify scripts for improved validation
- Add new templates as needed

### Update Agents
Agents can be updated by editing files in `~/.claude/agents/`:
- Refine expertise areas
- Add new guidelines
- Update for new versions of technologies

### Sync Across Machines
To use this setup on another machine:
```bash
# Backup
tar -czf claude-global-setup.tar.gz ~/.claude/skills ~/.claude/agents

# Restore on new machine
tar -xzf claude-global-setup.tar.gz -C ~/
```

---

## Testing Your Setup

### Test Skills
```bash
# Test n8n workflow validation
python3 ~/.claude/skills/n8n-workflow-builder/scripts/validate_workflow.py test.json

# Test RTL audit (in a project)
bash ~/.claude/skills/rtl-css/scripts/audit_rtl.sh
```

### Test Agents
Just ask Claude:
- "Use the drizzle-specialist to create a users table"
- "Use the stripe-integration skill to add webhook handling"

---

## Next Steps

1. **Install Official Skills** (optional):
   ```bash
   /plugin marketplace add anthropics/skills
   /plugin install document-skills@anthropic-agent-skills
   /plugin install example-skills@anthropic-agent-skills
   ```

2. **Customize for Your Stack:**
   - Add skills for your specific tools (Vercel, Railway, etc.)
   - Create agents for your company's internal tools

3. **Share with Your Team:**
   - Export `~/.claude/skills/` and `~/.claude/agents/`
   - Add to your team's onboarding docs

---

## Quick Reference

**Skills Location:** `~/.claude/skills/`
**Agents Location:** `~/.claude/agents/`
**Project Agents:** `.claude/agents/` (current project only)

**5 Skills:**
1. n8n-workflow-builder
2. stripe-integration
3. supabase-rls
4. rtl-css
5. drizzle-migrations

**20 Global Agents:**
11 generic + 9 stack-specific

**Status:** ✅ All set up and ready to use across all projects!
