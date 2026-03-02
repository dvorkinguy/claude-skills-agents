# JTBD Feature Builder

Build features using Jobs To Be Done framework. Focus on customer outcomes, not features.

## Triggers

Use when:
- Planning new features
- Writing user stories
- Prioritizing backlog
- Defining acceptance criteria
- Understanding customer needs

## JTBD Framework

### Core Concept

Customers don't buy products - they "hire" them to get a job done.

```
When [situation], I want to [motivation], so I can [outcome].
```

### Example for Export Arena

```
When I receive a new shipment, I want to classify it quickly,
so I can file my customs entry before the deadline.
```

## Job Mapping Template

### 1. Identify the Main Job

```markdown
## Main Job
**Functional:** [What they're trying to accomplish]
**Emotional:** [How they want to feel]
**Social:** [How they want to be perceived]

## Context
**When:** [Situation trigger]
**Where:** [Environment/location]
**Who:** [Role/persona]
```

### 2. Break Down Job Steps

```markdown
## Job Steps (Job Map)

1. **Define** - What triggers the job?
   - When a shipment arrives
   - When customs filing is due

2. **Locate** - What inputs are needed?
   - Product descriptions
   - Country of origin
   - Commercial invoices

3. **Prepare** - How do they get ready?
   - Gather documentation
   - Review product specs

4. **Confirm** - How do they verify readiness?
   - Check all required fields
   - Validate quantities

5. **Execute** - How do they perform the job?
   - Classify products
   - Submit to customs

6. **Monitor** - How do they track progress?
   - Check classification status
   - Track filing acceptance

7. **Modify** - How do they make adjustments?
   - Correct errors
   - Update classifications

8. **Conclude** - How do they finish?
   - Archive documentation
   - Update records
```

## Opportunity Score

Rate each job step:

```
Opportunity Score = Importance + (Importance - Satisfaction)
```

| Step | Importance (1-10) | Satisfaction (1-10) | Score |
|------|-------------------|---------------------|-------|
| Classify products | 9 | 4 | 14 |
| Track filing status | 7 | 6 | 8 |
| Correct errors | 8 | 5 | 11 |

**High Score = High Opportunity**

## Feature Definition Template

```markdown
# Feature: [Name]

## Job to be Done
When [situation], I want to [motivation], so I can [outcome].

## Job Step Addressed
[Which step from the job map this addresses]

## Opportunity Score
Importance: [1-10]
Satisfaction: [1-10]
Score: [calculated]

## User Story
As a [persona],
I want [capability],
So that [benefit].

## Acceptance Criteria
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [action], then [result]

## Success Metrics
- [Measurable outcome 1]
- [Measurable outcome 2]

## Anti-Goals (What we're NOT solving)
- [Explicitly out of scope]
```

## Export Arena JTBD Examples

### HS Classification Agent

```markdown
# Feature: AI HS Classification

## Job to be Done
When I need to classify a new product, I want accurate HS codes
with documentation, so I can file customs entries confidently.

## Pain Points
- Manual classification takes 15-30 minutes per SKU
- Fear of misclassification penalties
- Lack of audit trail for compliance

## Opportunity
Importance: 9
Satisfaction: 3
Score: 15 (HIGH)

## Solution
AI classifies products in seconds with:
- Confidence score
- Defense Memo (audit documentation)
- Historical classification data
```

### Port Monitor Agent

```markdown
# Feature: D&D Prevention Monitor

## Job to be Done
When containers arrive at port, I want proactive alerts about
free time expiration, so I can avoid demurrage and detention fees.

## Pain Points
- $300-500 per container per day fees
- Manual tracking across multiple ports
- Missed deadlines due to visibility gaps

## Opportunity
Importance: 8
Satisfaction: 2
Score: 14 (HIGH)

## Solution
Real-time monitoring with:
- Free time countdown
- Proactive alerts (3 days, 1 day, same day)
- Cost-saving analytics
```

## Interview Questions

Use these to uncover jobs:

1. **Situation:** "Walk me through the last time you had to [do job]"
2. **Struggle:** "What's the hardest part about [job step]?"
3. **Workaround:** "How do you handle that today?"
4. **Success:** "What does a great outcome look like?"
5. **Failure:** "What happens when it goes wrong?"

## Prioritization Matrix

```
                 High Importance
                      │
    Quick Wins        │     Big Bets
    (Do First)        │    (Plan Well)
                      │
    ──────────────────┼──────────────────
                      │
    Maybe Later       │     Don't Do
    (Low Priority)    │    (Waste)
                      │
                 Low Importance

    Low Effort ←──────┼──────→ High Effort
```

## Outcome Statements

Format: [Direction] + [Unit] + [Object] + [Context]

Examples:
- Minimize the time to classify a product
- Reduce the likelihood of misclassification penalties
- Increase the accuracy of HS code assignments
- Minimize the number of manual corrections needed

## Anti-Patterns to Avoid

1. **Feature-first thinking**: "We should add AI" → "What job does AI help complete?"
2. **Solution assumptions**: "Users need a dashboard" → "What outcome do they need?"
3. **Persona-only focus**: "SMB owners want X" → "When doing Y, what struggle exists?"
4. **Feature bloat**: Adding capabilities no one hired the product for
