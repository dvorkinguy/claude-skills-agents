# Output Patterns

Use these patterns when skills need consistent, high-quality output.

## Template Pattern

**Strict (APIs, data formats):**
```markdown
## Report Structure

ALWAYS use this exact template:

# [Title]
## Executive Summary
[One paragraph overview]
## Key Findings
- Finding 1 with data
- Finding 2 with data
## Recommendations
1. Action item
2. Action item
```

**Flexible (when adaptation is useful):**
```markdown
## Report Structure

Default format (adjust as needed):

# [Title]
## Summary
[Overview]
## Findings
[Adapt based on what you discover]
## Recommendations
[Tailor to context]
```

## Examples Pattern

For output quality that depends on seeing examples:

```markdown
## Commit Message Format

**Example 1:**
Input: Added user authentication with JWT
Output:
feat(auth): implement JWT authentication

Add login endpoint and token validation

**Example 2:**
Input: Fixed date display bug in reports
Output:
fix(reports): correct date timezone conversion

Use UTC timestamps consistently
```

Examples show desired style better than descriptions.

## Checklist Pattern

For multi-step verification:

```markdown
## Before Submitting

- [ ] All tests pass
- [ ] Documentation updated
- [ ] No console.log statements
- [ ] Error handling in place
```
