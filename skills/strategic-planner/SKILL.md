---
name: strategic-planner
description: Elite software planning skill for reducing mistakes and maximizing effectiveness. Use when starting ANY non-trivial implementation, refactoring, migration, or feature development. Triggers include "plan", "implement", "add feature", "refactor", "migrate", "architecture", "design", "how should I", "best approach", or when tasks involve multiple files or steps. ALWAYS use before writing significant code.
---

# Strategic Planner

Transform vague requirements into bulletproof implementation plans using industry best practices, risk mitigation, and systematic decomposition.

## Core Philosophy

**PLAN BEFORE CODE.** 80% of bugs come from poor planning. Every hour of planning saves 10 hours of debugging.

## The SPACE Framework

Use this 5-phase framework for ALL planning:

### 1. **S**cope - Define Boundaries

```
[ ] What EXACTLY needs to be built?
[ ] What is explicitly OUT of scope?
[ ] What are the acceptance criteria?
[ ] Who is the user/stakeholder?
[ ] What does "done" look like?
```

**Anti-pattern:** Starting without clear boundaries leads to scope creep and gold-plating.

### 2. **P**robe - Investigate Context

```
[ ] Explore existing codebase patterns
[ ] Find similar implementations to reference
[ ] Identify dependencies and integrations
[ ] Check for breaking change risks
[ ] Review recent changes in affected areas
```

**Tool usage:**
- Use `Explore` agent for codebase investigation
- Use `Grep` for pattern matching
- Use `LSP` for call hierarchy analysis

### 3. **A**nalyze - Assess Risks & Tradeoffs

```
[ ] What could go wrong? (Risk matrix)
[ ] What are the technical tradeoffs?
[ ] What are the dependencies?
[ ] What assumptions are we making?
[ ] What's the rollback strategy?
```

**Risk Categories:**
- **Technical**: Complexity, performance, security
- **Integration**: Breaking changes, API contracts
- **Timeline**: Blocking dependencies, unknowns
- **Quality**: Test coverage, edge cases

### 4. **C**onstruct - Build the Plan

```
[ ] Break into atomic, testable steps
[ ] Order by dependencies (topological sort)
[ ] Identify parallelization opportunities
[ ] Define checkpoints for validation
[ ] Estimate complexity (not time!)
```

**Step Decomposition Rules:**
- Each step should be completable in one focused session
- Each step should have a clear verification method
- Steps should be independent when possible
- Failure of one step shouldn't cascade to others

### 5. **E**xecute - Implement with Checkpoints

```
[ ] Use TodoWrite to track progress
[ ] Validate after EACH step
[ ] Run tests incrementally
[ ] Commit at stable checkpoints
[ ] Document decisions and rationale
```

## Planning Intensity Levels

### Level 1: Quick Plan (5-10 min)
**Use for:** Simple features, bug fixes, small refactors

```markdown
## Quick Plan: [Feature Name]
**Goal:** [One sentence]
**Steps:**
1. [ ] Step 1 - [verification]
2. [ ] Step 2 - [verification]
3. [ ] Step 3 - [verification]
**Risks:** [Top 1-2 risks]
```

### Level 2: Standard Plan (15-30 min)
**Use for:** Multi-file features, integrations, moderate complexity

```markdown
## Standard Plan: [Feature Name]

### Scope
- **Goal:** [Clear objective]
- **Out of scope:** [Explicit exclusions]
- **Acceptance:** [Measurable criteria]

### Investigation
- **Patterns found:** [Existing code patterns]
- **Dependencies:** [What this touches]
- **Reference impl:** [Similar code to follow]

### Risk Analysis
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | High/Med/Low | [Strategy] |

### Implementation Steps
1. [ ] [Step] - **Verify:** [How to confirm]
2. [ ] [Step] - **Verify:** [How to confirm]
...

### Checkpoints
- [ ] After step 2: Run tests
- [ ] After step 4: Manual verification
- [ ] Final: Lint + typecheck + full test suite
```

### Level 3: Comprehensive Plan (1+ hour)
**Use for:** Architecture changes, migrations, large features

See `references/comprehensive-plan-template.md`

## Decision Framework

When facing choices, use this matrix:

```
               | Simple | Complex
---------------|--------|----------
Low Risk       | JFDI   | Quick Plan
High Risk      | Standard | Comprehensive
```

**JFDI** = Just Do It (no formal plan needed)

## Best Practices Checklist

### Before Planning
- [ ] Requirements are clear (ask if not!)
- [ ] You understand the "why" not just "what"
- [ ] Stakeholder expectations are aligned
- [ ] Timeline constraints are known

### During Planning
- [ ] Use existing patterns (don't reinvent)
- [ ] Consider edge cases explicitly
- [ ] Identify the "happy path" first
- [ ] Plan for failure modes
- [ ] Include rollback strategy

### After Planning (Before Implementation)
- [ ] Plan reviewed for completeness
- [ ] Steps are atomic and verifiable
- [ ] TodoWrite populated with tasks
- [ ] Tests outlined or written first (TDD)

## Anti-Patterns to Avoid

1. **Analysis Paralysis**: Planning forever without starting
2. **Premature Optimization**: Planning for scale before MVP
3. **Big Bang**: Giant plans with no checkpoints
4. **Wishful Thinking**: Ignoring risks because "it'll be fine"
5. **Gold Plating**: Adding features not in requirements
6. **Tunnel Vision**: Not exploring alternatives
7. **Copy-Pasta Planning**: Using templates without thinking

## Integration with Agents

**Delegate to specialists during planning:**

| Phase | Agent | Purpose |
|-------|-------|---------|
| Probe | `Explore` | Codebase investigation |
| Analyze | `debugger` | Risk assessment for bugs |
| Construct | `architecture-planner` | System design |
| Execute | `tdd-specialist` | Test-first implementation |

## Quick Reference Commands

```bash
# Use sequential thinking for complex decisions
mcp__sequential-thinking__sequentialthinking

# Explore codebase for patterns
Task(subagent_type="Explore", prompt="...")

# Track implementation
TodoWrite(todos=[...])
```

## References

- `references/comprehensive-plan-template.md` - Full template for large projects
- `references/risk-assessment-guide.md` - Detailed risk analysis
- `references/decomposition-patterns.md` - Breaking down complex work
- `references/industry-methodologies.md` - TDD, DDD, SOLID principles
- `assets/planning-checklist.md` - Printable checklist
- `assets/decision-matrix.md` - Decision framework templates

## Implementation Workflow

When this skill triggers:

1. **Assess Complexity** - Determine planning level needed
2. **Gather Context** - Explore codebase, understand requirements
3. **Apply SPACE Framework** - Work through each phase
4. **Create Plan Document** - Write out the plan
5. **Review with User** - Get approval before implementing
6. **Transfer to TodoWrite** - Create trackable tasks
7. **Execute with Checkpoints** - Implement systematically
