---
name: plan-interview
description: Interview the user about their plan before implementation. Use when user says "interview me", "ask me questions about the plan", "clarify the plan", "review my plan", "question my plan", or "challenge my approach". Systematically asks about technical implementation, UI/UX, concerns, tradeoffs, dependencies, testing, security, and edge cases.
---

# Plan Interview

Systematically interview the user about their plan to ensure clarity, catch edge cases, and validate assumptions before implementation begins.

## When to Use

- User explicitly requests an interview: "interview me", "ask me questions"
- User wants plan validation: "review my plan", "challenge my approach"
- Before starting implementation of a complex feature
- When the plan seems to have gaps or ambiguities
- When assumptions need validation

## Interview Process

### Step 1: Load the Plan

First, read the active plan file to understand what's being proposed:

1. Check for plan file in `~/.claude/plans/` (most recent or specified)
2. Parse the plan structure: goals, steps, files to modify, approach
3. Identify areas that need clarification

### Step 2: Conduct Systematic Interview

Use the AskUserQuestion tool to interview the user across these categories. Ask 1-4 questions at a time, grouped by category.

#### Category 1: Technical Implementation

Ask about:
- Architecture decisions (why this approach vs alternatives?)
- Data flow (where does data come from/go to?)
- State management (how is state handled?)
- API contracts (what are the inputs/outputs?)
- Error handling (what can go wrong? how to handle it?)
- Performance implications (any N+1 queries? expensive operations?)

Example questions:
```
Question: "How should we handle errors in the API call?"
Options:
- A. Silent fail with fallback data
- B. Show error toast and retry button
- C. Redirect to error page
- D. Other
```

#### Category 2: UI/UX Decisions

Ask about:
- User flow (what's the happy path? what about edge cases?)
- Visual design (any specific design requirements?)
- Responsive behavior (mobile/tablet/desktop differences?)
- Loading states (what to show while loading?)
- Empty states (what if there's no data?)
- Accessibility (keyboard nav? screen readers?)

#### Category 3: Concerns & Edge Cases

Ask about:
- What happens if the user is offline?
- What happens with invalid input?
- What about concurrent users/requests?
- What about partial failures?
- What about really large datasets?
- What about really small screens?

#### Category 4: Tradeoffs

Ask about:
- Speed vs completeness (MVP or full feature?)
- Consistency vs availability (stale data OK?)
- Simplicity vs flexibility (hardcode or configure?)
- Build vs buy (custom or library?)
- Now vs later (optimize now or defer?)

#### Category 5: Dependencies & Integration

Ask about:
- External services (which APIs? what if they're down?)
- Internal dependencies (what other code/features does this touch?)
- Database changes (new tables? migrations?)
- Environment variables (new config needed?)
- Third-party libraries (any new dependencies?)

#### Category 6: Testing Strategy

Ask about:
- Unit tests (what's worth testing?)
- Integration tests (what flows to test?)
- E2E tests (what user journeys to verify?)
- Edge case tests (what unusual scenarios?)
- Performance tests (any benchmarks needed?)

#### Category 7: Security

Ask about:
- Authentication (who can access this?)
- Authorization (what can they do?)
- Input validation (what to sanitize?)
- Data exposure (what not to leak?)
- OWASP top 10 (any vulnerabilities?)

### Step 3: Document Findings

After the interview:
1. Update the plan file with clarified decisions
2. Note any unresolved questions for later
3. Highlight any risks or concerns identified

## Question Format Guidelines

When using AskUserQuestion:

1. **Be specific** - Don't ask vague questions
   - Bad: "How should we handle errors?"
   - Good: "When the HS code lookup API fails, should we: A) Show cached results, B) Display error message, C) Fallback to manual entry?"

2. **Provide options** - Give concrete choices when possible
   - Include 2-4 options
   - Always include "Other" for custom responses
   - Put recommended option first with "(Recommended)"

3. **Group related questions** - Ask up to 4 questions per round

4. **Use clear headers** - Help user understand the category

## Example Interview Session

```
[After reading plan for "Add HS Code Lookup Feature"]

Round 1 - Technical Implementation:
Q1: "Where should the HS code lookup data come from?"
    A. External API (real-time lookup)
    B. Local database (pre-loaded codes)
    C. Hybrid (cache API results locally)
    D. Other

Q2: "How often should we refresh the HS code data?"
    A. Never (static dataset)
    B. Daily background sync
    C. On-demand when user searches
    D. Other

Round 2 - UI/UX:
Q1: "What should happen while searching for HS codes?"
    A. Show loading spinner in input
    B. Show skeleton results
    C. Disable input until ready
    D. Other

Q2: "How many search results should we show?"
    A. Top 5 matches
    B. Top 10 matches
    C. Paginated results (10 per page)
    D. Other

[Continue through all categories as needed]
```

## Anti-Patterns

- Don't ask questions you can answer yourself by reading the code
- Don't ask about things already specified in the plan
- Don't ask hypothetical questions that won't affect implementation
- Don't overwhelm with too many questions at once (max 4 per round)
- Don't ask leading questions that push a particular answer

## Integration with Plan Mode

This skill works best when:
1. A plan file already exists (from plan mode)
2. The plan has been drafted but not approved
3. User wants validation before ExitPlanMode

After interview completes:
1. Update plan file with decisions
2. Call ExitPlanMode with the refined plan
3. Include any caveats or risks identified

## Quick Reference

| Phase | Questions to Ask |
|-------|-----------------|
| Technical | Architecture, data flow, APIs, errors, performance |
| UI/UX | User flow, design, responsive, loading/empty states |
| Edge Cases | Offline, invalid input, concurrency, scale |
| Tradeoffs | MVP vs full, build vs buy, now vs later |
| Dependencies | External APIs, internal code, DB, config |
| Testing | Unit, integration, E2E, edge cases |
| Security | Auth, authz, validation, data exposure |
