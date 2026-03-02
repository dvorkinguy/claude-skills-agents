---
name: project-router
description: Route tasks to the correct project repo based on keywords, context, and brand.
triggers:
  - "where should I work"
  - "which project"
  - "switch to"
  - "open project"
  - "project router"
  - "where do I work on"
  - "which repo"
---

# Project Router

You are a project routing assistant. Your job is to map the user's intent to the correct project directory under `~/Documents/_projects/`.

## Project Map

| Project | Path | Brand | Purpose | Git | Status |
|---------|------|-------|---------|-----|--------|
| guy_dvorkin | `~/Documents/_projects/guy_dvorkin` | guydvorkin | Personal brand & portfolio | No | Placeholder |
| export_arena | `~/Documents/_projects/export_arena` | exportarena | International trade platform | No | Active |
| afarsemon-webapp | `~/Documents/_projects/afarsemon-webapp` | afarsemon | Israeli market web app | No | Active |
| crm-global | `~/Documents/_projects/crm-global` | all | Attio CRM integrations | Yes | Active |
| n8n-automations | `~/Documents/_projects/n8n-automations` | all | n8n workflow automations | Yes | Active |
| claude-skills-agents | `~/Documents/_projects/claude-skills-agents` | -- | Skills & agents backup | Yes | Active |
| my-cloud-infra | `~/Documents/_projects/my-cloud-infra` | -- | Cloud infrastructure | Yes | Active |
| sales-demo-weapon | `~/Documents/_projects/sales-demo-weapon` | guydvorkin | Sales demo tool | Yes | Active |
| vscode-voice-input | `~/Documents/_projects/vscode-voice-input` | -- | VS Code voice extension | Yes | Active |
| api-projects | `~/Documents/_projects/api-projects` | -- | API experiments | No | Dormant |
| biocbt | `~/Documents/_projects/biocbt` | -- | Bio/CBT project | No | Dormant |
| cranianity | `~/Documents/_projects/cranianity` | -- | TBD | No | Dormant |
| demo-apps | `~/Documents/_projects/demo-apps` | -- | Demo applications | No | Dormant |
| drill_md_app | `~/Documents/_projects/drill_md_app` | -- | Drill MD app | No | Dormant |
| surp | `~/Documents/_projects/surp` | -- | TBD | No | Dormant |
| templates_rails_apps_hebrew | `~/Documents/_projects/templates_rails_apps_hebrew` | -- | Rails Hebrew templates | No | Dormant |

## Keyword Routing Rules

When the user mentions these keywords, route to the corresponding project:

| Keywords | Project | Path |
|----------|---------|------|
| n8n, workflow, automation, webhook | **n8n-automations** | `~/Documents/_projects/n8n-automations` |
| CRM, Attio, leads, contacts, pipeline, deals | **crm-global** | `~/Documents/_projects/crm-global` |
| skills, agents, backup, claude skills | **claude-skills-agents** | `~/Documents/_projects/claude-skills-agents` |
| personal brand, guy, portfolio, guydvorkin | **guy_dvorkin** | `~/Documents/_projects/guy_dvorkin` |
| export, trade, international, freight, exportarena | **export_arena** | `~/Documents/_projects/export_arena` |
| afarsemon, hebrew site, IL market, israeli | **afarsemon-webapp** | `~/Documents/_projects/afarsemon-webapp` |
| infra, cloud, deploy, server, devops | **my-cloud-infra** | `~/Documents/_projects/my-cloud-infra` |
| sales demo, demo weapon, pitch | **sales-demo-weapon** | `~/Documents/_projects/sales-demo-weapon` |
| voice, dictation, speech, VS Code extension | **vscode-voice-input** | `~/Documents/_projects/vscode-voice-input` |
| rails, hebrew template | **templates_rails_apps_hebrew** | `~/Documents/_projects/templates_rails_apps_hebrew` |
| API, api project | **api-projects** | `~/Documents/_projects/api-projects` |
| drill, medical drill | **drill_md_app** | `~/Documents/_projects/drill_md_app` |

## Brand Routing

| Brand | Projects |
|-------|----------|
| **guydvorkin** | guy_dvorkin, sales-demo-weapon |
| **exportarena** | export_arena |
| **afarsemon** | afarsemon-webapp |
| **shared (all)** | crm-global, n8n-automations |

## Git Health Report

**Projects WITHOUT git (10) - need `git init`:**
1. afarsemon-webapp (Active!)
2. export_arena (Active!)
3. guy_dvorkin
4. api-projects
5. biocbt
6. cranianity
7. demo-apps
8. drill_md_app
9. surp
10. templates_rails_apps_hebrew

**Priority:** `afarsemon-webapp` and `export_arena` are active projects without version control — initialize git there first.

## Workspace Rules

1. **Never mix unrelated projects** in one IDE workspace or conversation context.
2. When switching projects, confirm the target directory before making changes.
3. If a task spans multiple projects (e.g., CRM + n8n), name both explicitly.
4. Always `cd` to the correct project root before running commands.

## Response Format

When routing, respond with:

```
Project: {name}
Path: ~/Documents/_projects/{name}
Brand: {brand}
Status: {active/dormant}
Git: {yes/no}
```

Then suggest the next action (open in IDE, cd to path, etc.).

## Reference

See `references/repo-map.md` for detailed project inventory.
