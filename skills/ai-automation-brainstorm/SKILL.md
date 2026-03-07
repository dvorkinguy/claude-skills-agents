---
name: ai-automation-brainstorm
description: Brainstorm and rank buildable AI automation ideas by scanning the web, n8n templates, Claude Code changelogs, and Apify actors. Cross-references against existing skills and tools. Use when user says "brainstorm automations", "automation ideas", "what should I build", "scan for AI solutions", "find new automations", or needs structured AI solution discovery for a specific industry or problem.
---

# AI Automation Brainstorm

Scan the web for proven AI automations, cross-reference with existing skills/tools, and output ranked, buildable automation ideas with revenue models.

## Quick Actions

| Need | Action |
|------|--------|
| Full brainstorm | -> Run all 3 phases below |
| Discovery only | -> Phase 1 only |
| Feasibility check | -> Phase 2 only |
| Score existing ideas | -> Phase 3 with manual input |

## Cost Estimates

| Run Type | Cost | Notes |
|----------|------|-------|
| Full run (all phases) | $0.00-0.08 | WebSearch free, Apify optional |
| Discovery only (Phase 1) | $0.00 | WebSearch + MCP tools only |
| With YouTube scan | ~$0.08 | Apify YouTube scraper |

---

## Before Starting

**Always ask for:**
1. **Domain/Industry** - e.g., "logistics", "legal", "e-commerce" (no default scan)
2. **Problem area** (optional) - e.g., "lead qualification", "invoice processing"
3. **Target client** (optional) - e.g., "mid-size freight forwarders in Europe"

Cross-reference the industry against `vertical-playbooks` for existing coverage.

---

## Phase 1: Solution Discovery

**Goal:** Find 15-20 proven AI automations from multiple sources, all related to the specified domain.

### Step 1A: Web Search -- AI News & Product Launches (5 parallel calls)

Run these `WebSearch` queries in parallel:

1. `"AI automation" OR "AI agent" [DOMAIN] [current year]` (last 30 days)
2. `"AI tool" [DOMAIN] launch OR new site:producthunt.com OR site:news.ycombinator.com` (last 30 days)
3. `"AI workflow" OR "AI automation" [DOMAIN] site:zapier.com OR site:make.com OR site:n8n.io` (last 30 days)
4. `"AI solution" [DOMAIN] business automation [current year]` (last 30 days)
5. `"AI agent" [DOMAIN] use case OR case study [current year]` (last 30 days)

### Step 1B: Automation Platform Templates (3 parallel calls)

1. `mcp__n8n__search_templates` with `searchMode: "by_task"` and relevant task type for the domain
2. `mcp__n8n__search_templates` with `query: "[DOMAIN] automation"`
3. `WebSearch`: `"[DOMAIN] automation template" site:community.n8n.io OR site:community.make.com`

### Step 1C: AI Tool Directories (2 parallel calls)

1. `WebSearch`: `"[DOMAIN]" AI tool directory site:theresanaiforthat.com OR site:futuretools.io`
2. `WebSearch`: `"[DOMAIN]" AI automation tool OR platform [current year]`

### Step 1D: Claude Code Capabilities (2 parallel calls)

Fetch via `WebFetch`:
1. `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` -- extract new features, hooks, MCP changes
2. `https://github.com/anthropics/skills/tree/main/skills` -- official Anthropic skill patterns

**Extract:** New CLI features, new skills, new MCP capabilities, deprecations. Cross-reference against Guy's current skill ecosystem for upgrade/adoption opportunities.

### Step 1E: Apify Actor Discovery (optional, 1-2 calls)

If relevant to the domain:
- `mcp__apify__search-actors` with `query: "[DOMAIN]"` -- find scrapers and automation actors
- `mcp__apify__search-actors` with `query: "[DOMAIN] data"` -- find data extraction actors

### Step 1F: YouTube AI Channels (optional)

If user requests broader scan:
- `WebSearch`: `"AI automation [DOMAIN]" site:youtube.com [current year]`

### Phase 1 Output

Compile a raw list:

| # | Automation / Solution | Source | Target Problem | Proven? |
|---|----------------------|--------|---------------|---------|
| 1 | [Name/Description] | [Source URL/Platform] | [What it solves] | Yes/No |
| ... | ... | ... | ... | ... |
| 20 | ... | ... | ... | ... |

**Proven** = has live users, case studies, or template downloads. Mark unproven ideas accordingly.

---

## Phase 2: Cross-Reference & Feasibility

**Goal:** Map each discovery against Guy's existing capabilities and determine build feasibility.

### Step 2A: Check Existing Skills

Cross-reference each discovery against:
- `n8n-workflow-builder` -- can this be built as an n8n workflow?
- `vertical-playbooks` -- is this vertical already covered?
- `ai-worker-creator` -- can this become a productized AI worker?
- `lead-enrichment` -- does this overlap with lead enrichment flows?
- `existing-solutions-finder` -- is there already a tool/package for this?

### Step 2B: Check Tool Availability

For each promising automation:
- `mcp__n8n__search_nodes` with relevant node types (e.g., `search_nodes({query: "slack"})`)
- Check if required integrations exist in Guy's stack: n8n, Apify, OpenRouter, Attio, WhatsApp, Slack, Vercel, Cloudflare

### Step 2C: Check n8n Template Availability

For automations that map to n8n:
- `mcp__n8n__search_templates` with `searchMode: "by_nodes"` using the required node types
- `mcp__n8n__get_template` for promising templates (use `mode: "full"`)

### Phase 2 Output

**Feasibility Matrix:**

| # | Automation | Existing Skill? | n8n Nodes Available? | Tool Stack Fit | Build Effort | Feasibility |
|---|-----------|----------------|---------------------|---------------|-------------|-------------|
| 1 | [Name] | Yes/No (which) | Yes/Partial/No | High/Med/Low | Hours est. | Ready/Needs Work/Blocked |
| ... | ... | ... | ... | ... | ... | ... |

**Legend:**
- **Ready** = Can build today with existing skills + tools
- **Needs Work** = Missing 1-2 components, buildable with effort
- **Blocked** = Missing critical integration or capability

---

## Phase 3: Score, Rank & Synthesize

**Goal:** Score each viable automation and output ranked Automation Spec Cards.

### Scoring Framework (/50)

| Criterion | /10 | What to Evaluate |
|-----------|-----|-----------------|
| Revenue Potential | How much can Guy charge? ($297-$5,000+/mo) |
| Business Impact | How much pain does it solve for the client? |
| Build Feasibility | Can it be built with existing skills/tools? |
| Market Demand | How many businesses need this? |
| Differentiation | Is there a moat or competitive edge? |

### Category Thresholds

| Category | Score | Action |
|----------|-------|--------|
| **Quick Wins** | 40+ | Build in <8 hours, ship this week |
| **High Value** | 35-39 | Worth 1-2 day investment |
| **Strategic** | 30-34 | Builds future capability, plan for it |
| **Experimental** | 25-29 | Unproven but interesting, backlog |

### Automation Spec Card Template

For each of the top 5-10 ideas, produce:

```
## [#X] [Automation Name] -- Score: XX/50

**Category:** Quick Win / High Value / Strategic / Experimental

**Business Outcome:**
[1-2 sentences: what changes for the client after deployment]

**Architecture:**
[How it works: trigger -> process -> output]
- Trigger: [webhook, schedule, event]
- Process: [AI model, data transform, API calls]
- Output: [notification, document, CRM update]

**Tech Stack:**
- n8n nodes: [list required nodes]
- AI model: [OpenRouter/Claude/GPT]
- Integrations: [Slack, WhatsApp, Attio, etc.]
- Existing skills to reuse: [list any]

**n8n Template:** [template ID if found, or "Build from scratch"]

**Build Time:** X hours

**Revenue Model:**
- Setup fee: $X
- Monthly retainer: $Y/mo
- Usage-based: $Z per task (if applicable)
- Target pricing tier: Starter / Growth / Scale

**Implementation Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Score Breakdown:**
| Revenue | Impact | Feasibility | Demand | Differentiation | Total |
|---------|--------|-------------|--------|-----------------|-------|
| X/10 | X/10 | X/10 | X/10 | X/10 | XX/50 |
```

### Phase 3 Output

Group all spec cards by category:

```
QUICK WINS (Build This Week)
------------------------------
#1. [Name] -- Score: XX/50
#2. ...

HIGH VALUE (Worth Investment)
-------------------------------
#3. [Name] -- Score: XX/50
#4. ...

STRATEGIC (Plan For)
---------------------
#5. [Name] -- Score: XX/50

EXPERIMENTAL (Backlog)
-----------------------
#6. [Name] -- Score: XX/50
```

---

## Phase 4: Handoff (Optional)

After presenting results, offer to route to:

| Destination | When | Skill |
|-------------|------|-------|
| Build the workflow | User picks an idea to build | `n8n-workflow-builder` |
| Productize as AI Worker | For Export Arena / Afarsemon | `ai-worker-creator` |
| Price for a client | Creating a proposal | `ai-agent-pricing` |
| Expand vertical coverage | Industry-specific playbook | `vertical-playbooks` |
| Find existing solutions | Before building from scratch | `existing-solutions-finder` |

---

## PDF Output

After completing all phases, generate a styled PDF report using `generate_pdf.py` in this skill's directory.

- **Output path:** `tmp/automation-brainstorm-[date].pdf`
- **Run command:** `python /home/gi/.claude/skills/ai-automation-brainstorm/generate_pdf.py`
- **The script expects a JSON file** at `tmp/automation-brainstorm-data.json` with the structured output from all 3 phases

If PDF generation fails, fall back to markdown at `tmp/automation-brainstorm-[date].md`.

---

## Error Handling

| Issue | Fallback |
|-------|----------|
| WebSearch returns few results | Broaden date range to 60 days, try alternate keywords |
| n8n template search empty | Use `WebSearch` for community templates instead |
| Claude Code changelog fetch fails | Skip Step 1D, note in output |
| Apify actor search fails | Skip Step 1E, note in output |
| No viable automations found | Pivot domain, broaden problem area, or report "market is saturated" |
| PDF generation fails | Fall back to markdown output |

---

## Tips

- Run monthly or when exploring a new vertical
- Focus on automations with **proven demand** (existing templates, case studies, paying customers)
- Quick Wins should generate revenue within 2 weeks of building
- Cross-reference against `vertical-playbooks` to avoid rebuilding existing coverage
- Use `ai-agent-pricing` output for accurate pricing in spec cards
- Save promising but unbuilt ideas to a backlog for future sprints
