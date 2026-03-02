# 🚨 STOP - READ THIS FIRST

## Pre-Action Checklist (MANDATORY)

Before EVERY response, run through this:

```
[ ] MCP tool available? → USE IT (instant, no context cost)
[ ] Specialized agent fits? → DELEGATE (parallel, expert knowledge)
[ ] Skill exists? → INVOKE IT (workflows, templates)
[ ] Simple edit? → DO IT, DON'T OVER-VERIFY
```

## Tool Priority (HIGHEST → LOWEST)

| Priority | Tool Type | When to Use | Example |
|----------|-----------|-------------|---------|
| 1 | **MCP Tools** | Direct integrations | playwright, stripe, github, context7 |
| 2 | **Agents** | Domain expertise | drizzle-specialist, nextjs-pro, debugger |
| 3 | **Skills** | Workflows/templates | webapp-testing, n8n-workflow-builder |
| 4 | **Manual** | Only when no tool exists | Last resort |

## Speed Rules

- **Simple edits** (imports, config, component additions) → Trust it, move on
- **Only screenshot** for complex layout/styling changes
- **Parallel tool calls** always - don't sequence independent operations
- **Don't over-verify** - once done, confirm and proceed

---

## 🧠 Agent Configuration

**ALL agents MUST use:** `model: "opus"` (no exceptions)

### Auto-Delegation Rules

| Trigger | Action | Priority |
|---------|--------|----------|
| Error, bug, broken, fails | → `debugger` agent | 1 |
| How, where, what, explain | → `Explore` agent | 2 |
| Implement, add feature, refactor | → `EnterPlanMode` | 3 |
| Domain-specific (see below) | → Specialized agent | 4 |
| After code changes | → Quality agents | 5 |

### Domain Triggers → Agents

| Keywords | Agent |
|----------|-------|
| schema, migration, SQL, Drizzle | `drizzle-specialist` |
| hooks, useState, component | `react-pro` |
| App Router, RSC, Server Action | `nextjs-pro` |
| Hebrew, Arabic, RTL | `i18n-rtl` |
| slow, optimize, bundle | `performance-auditor` |
| WCAG, a11y, screen reader | `accessibility-checker` |
| vulnerability, XSS, OWASP | `security-auditor` |
| dashboard, prometheus, loki | `grafana-specialist` |

---

## 🔧 MCP Servers Available

| Server | Purpose | Trigger |
|--------|---------|---------|
| playwright | Browser automation, screenshots | UI testing |
| stripe | Payment operations | Billing, subscriptions |
| github | Repo operations, PRs | Git workflows |
| context7 | Any library docs | Next.js, React, Clerk, etc. |
| postgres | Database queries | Direct SQL |
| n8n | Workflow automation | Automation flows |
| filesystem | File operations | Bulk file ops |
| memory | Persistent memory | Cross-session data |

---

## 🎭 Playwright Guidelines

**Use for:** Visual verification, E2E tests, user flow testing

**DON'T use for:** Simple edits, config changes, non-UI work

**Quick verification pattern:**
```python
# Only when complex layout work requires it
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:3000/route')
    page.screenshot(path='/tmp/verify.png')
    browser.close()
```

---

## 📋 Post-Implementation Checklist

After completing features:

| Check | Action |
|-------|--------|
| Code quality | DRY? Follows patterns? |
| Security | Input validation? No secrets? |
| Testing | Tests added? |
| Learnings | Document patterns for future |

---

## Language

- ALWAYS respond in English (never Hebrew unless explicitly requested)
