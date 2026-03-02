# Practical Tips for Skill Development

Actionable best practices from heavy skill usage. Use this as a quick reference when building, debugging, or optimizing skills.

Source: Nate Herk's skill-building workflow insights.

---

## When to Build a Skill

- You've told Claude the same instruction in different ways across sessions
- You've done something manually that could be automated
- You find yourself copy-pasting the same prompt or workflow

If any of these apply, it's time to make a skill.

---

## Start Simple, Iterate Ruthlessly

- **50 lines is fine** for a first version. Don't over-engineer upfront.
- Watch the first 5-10 runs closely. Observe what Claude gets right and wrong.
- Don't set-and-forget. Skills need tuning based on real usage.
- Progressive refinement: ship v1 fast, then tighten based on observations.

---

## Context Window Management

Your biggest enemy is context bloat. Every token in context costs money and reduces quality.

**Pre-load static data in SKILL.md instead of API calls:**
- If data doesn't change (IDs, endpoints, config values), hardcode it in the skill or a reference file
- Don't make Claude fetch something every run that you could embed once

**Delegate to sub-agents to keep context lean:**
- Pattern: "Delegate to [agent] with [query] to [task] so you don't blow your context window"
- Use `context: fork` for self-contained research or analysis tasks
- The sub-agent's verbose output stays out of your main conversation

**Use markdown reference files instead of repeated API/web searches:**
- If Claude keeps looking up the same docs, save them as a reference file
- One-time cost to create, zero ongoing token cost

---

## Token Optimization Checklist

- [ ] Hardcode static IDs, URLs, and config values (don't fetch what doesn't change)
- [ ] Move lengthy reference material to `references/` files (loaded on-demand, not every invocation)
- [ ] Use `context: fork` for tasks that produce verbose output
- [ ] Delegate research to sub-agents instead of doing it in the main context
- [ ] Keep SKILL.md under 500 lines

---

## Testing Workflow

1. Run the skill 5-10 times with varied inputs
2. Watch for: wrong steps, missing tone, repeated mistakes, tool struggles
3. After each observation, make ONE targeted fix
4. Re-run and verify the fix didn't break something else
5. Once stable, run edge cases (empty input, unusual input, missing args)

---

## Symptom → Fix Table

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Wrong steps or sequence | Instructions unclear or ambiguous | Edit the step-by-step instructions in SKILL.md |
| Missing tone or style | No style reference provided | Add or fix a reference file with tone/style examples |
| Repeated mistakes | No explicit rule against the mistake | Add a rule in the Notes section: "Do NOT [mistake]" |
| Tool struggles (wrong tool, bad args) | Claude doesn't know the tool well enough | Create a tool reference doc with examples |
| Skill not triggering | Description doesn't match user's words | Update `description` with natural trigger keywords |
| Skill triggers too often | Description too broad | Narrow the description or add `disable-model-invocation: true` |
| Sub-agent returns nothing useful | Skill has guidelines but no concrete task | Add explicit instructions: "Do X, then return Y" |
| Output in wrong format | No output template specified | Add an Output Template section with exact format |

---

## Sub-Agent Delegation Pattern

When a skill step involves research, analysis, or any self-contained task:

```
Delegate to [agent-type] agent:
"[Exact prompt for the sub-agent including what to search, analyze, and return]"
```

**Why:** Keeps the main context clean. The sub-agent does the heavy lifting and returns only the summary.

**Example:**
```
Delegate to Explore agent:
"Find all API route handlers in this project. List each route, its HTTP method, and the file path. Return as a markdown table."
```

---

## Scope: Where to Put Skills

| Scope | Path | Use When |
|-------|------|----------|
| **Project** | `.claude/skills/<name>/SKILL.md` | Skill is specific to one codebase |
| **Global** | `~/.claude/skills/<name>/SKILL.md` | Skill is useful across all your projects |

Rule of thumb: Start project-level. Promote to global only after you've confirmed it works across multiple projects.

---

## Common Anti-Patterns

- **Over-engineering v1**: Don't add hooks, scripts, and 5 reference files before the skill has run once
- **Vague instructions**: "Make it good" → Claude guesses. "Format as H2 headings with bullet points" → Claude delivers
- **Fetching static data**: Making API calls for data that hasn't changed in months
- **Giant SKILL.md**: 800+ lines means Claude loses focus. Split into references.
- **No guardrails**: Always add a "Do NOT" section for known failure modes
