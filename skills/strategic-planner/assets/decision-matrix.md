# Decision Matrix Templates

Templates for making structured technical decisions.

---

## Technology Selection Matrix

### Template

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| [Criterion 1] | [1-5] | [1-5] | [1-5] | [1-5] |
| [Criterion 2] | [1-5] | [1-5] | [1-5] | [1-5] |
| **Weighted Total** | - | **[Sum]** | **[Sum]** | **[Sum]** |

**Calculation:** Score = (Weight × Rating) for each criterion, sum all.

### Common Criteria

**For Libraries/Frameworks:**
- Documentation quality
- Community support
- Maintenance status
- Performance
- Learning curve
- Bundle size
- Security track record
- Integration ease

**For Architecture:**
- Scalability
- Maintainability
- Performance
- Complexity
- Team familiarity
- Future flexibility
- Cost

### Example: Database Selection

| Criterion | Weight | PostgreSQL | MongoDB | SQLite |
|-----------|--------|------------|---------|--------|
| Performance | 4 | 4 | 4 | 3 |
| Scalability | 3 | 5 | 5 | 2 |
| Simplicity | 4 | 3 | 3 | 5 |
| Team Experience | 5 | 5 | 3 | 4 |
| Cost | 2 | 4 | 4 | 5 |
| **Weighted Total** | - | **76** | **67** | **69** |

**Decision:** PostgreSQL wins with highest weighted score.

---

## Build vs Buy Decision

### Evaluation Framework

| Factor | Build In-House | Buy/Use Existing |
|--------|----------------|------------------|
| **Time to Market** | [Longer/Shorter] | [Longer/Shorter] |
| **Initial Cost** | [Higher/Lower] | [Higher/Lower] |
| **Long-term Cost** | [Higher/Lower] | [Higher/Lower] |
| **Customization** | [Full/Limited] | [Limited/Full] |
| **Maintenance** | [Internal] | [External/Shared] |
| **Risk** | [Higher/Lower] | [Higher/Lower] |
| **Learning** | [Steep/None] | [Documentation] |
| **Integration** | [Perfect Fit] | [Adaptation Needed] |

### Decision Rules

**Build when:**
- Core differentiator for business
- Unique requirements
- Long-term strategic value
- Team has capacity and expertise
- Existing solutions don't fit

**Buy when:**
- Commodity functionality
- Standard requirements
- Time is critical
- Team lacks expertise
- Proven solution exists

---

## Risk-Based Decision Matrix

### Framework

| Option | Expected Value | Risk Level | Reversibility |
|--------|---------------|------------|---------------|
| [Option A] | [High/Med/Low] | [High/Med/Low] | [Easy/Hard] |
| [Option B] | [High/Med/Low] | [High/Med/Low] | [Easy/Hard] |

### Decision Rules

```
High Value + Low Risk + Easy Reversibility = GO
High Value + High Risk + Easy Reversibility = TRY
High Value + High Risk + Hard Reversibility = CAREFUL PLAN
Low Value + Any Risk = SKIP
```

---

## RAPID Decision Framework

For decisions involving multiple stakeholders.

| Role | Person | Responsibility |
|------|--------|---------------|
| **R**ecommend | [Who] | Proposes solution |
| **A**gree | [Who] | Must agree to proceed |
| **P**erform | [Who] | Implements decision |
| **I**nput | [Who] | Provides information |
| **D**ecide | [Who] | Final authority |

---

## Tradeoff Analysis

### Template

```markdown
## Decision: [What are we deciding?]

### Options

**Option A: [Name]**
- Pros: [List]
- Cons: [List]
- Cost: [Effort/Resources]
- Risk: [Level]

**Option B: [Name]**
- Pros: [List]
- Cons: [List]
- Cost: [Effort/Resources]
- Risk: [Level]

### Analysis

| Factor | Option A | Option B | Winner |
|--------|----------|----------|--------|
| [Factor 1] | [Rating] | [Rating] | [A/B] |
| [Factor 2] | [Rating] | [Rating] | [A/B] |

### Recommendation
[Which option and why]

### Reversibility
[Can we change our mind? At what cost?]
```

---

## Architecture Decision Record (ADR)

### Template

```markdown
# ADR-[NUMBER]: [TITLE]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[What is the issue that we're seeing that is motivating this decision?]

## Decision
[What is the change that we're proposing and/or doing?]

## Consequences
[What becomes easier or more difficult to do because of this change?]

## Alternatives Considered

### Alternative 1: [Name]
[Description and why rejected]

### Alternative 2: [Name]
[Description and why rejected]

## References
[Links to relevant resources, discussions, etc.]
```

---

## Quick Decision Heuristics

### Two-Way Door Decisions (Reversible)
- Move fast
- Don't over-analyze
- Learn by doing
- Accept "good enough"

### One-Way Door Decisions (Irreversible)
- Take time
- Gather data
- Get multiple perspectives
- Plan for contingencies

### Time-Boxed Decisions
When stuck on a decision:
1. Set a timer (15-30 min)
2. List pros/cons
3. Score options
4. Decide when timer ends
5. Move forward with chosen option

### Default to Action
When in doubt:
- Choose the simpler option
- Choose the more reversible option
- Choose what you can ship sooner
- Choose what has better error handling

---

## Decision Anti-Patterns

### Analysis Paralysis
- **Symptom:** Can't decide, need more data
- **Fix:** Time-box, accept uncertainty

### HiPPO (Highest Paid Person's Opinion)
- **Symptom:** Defer to authority regardless of merit
- **Fix:** Use structured evaluation

### Anchoring
- **Symptom:** Over-weight first option
- **Fix:** Evaluate all options equally

### Sunk Cost Fallacy
- **Symptom:** Continue because of past investment
- **Fix:** Evaluate based on future value only

### Groupthink
- **Symptom:** Consensus without critical evaluation
- **Fix:** Assign devil's advocate role
