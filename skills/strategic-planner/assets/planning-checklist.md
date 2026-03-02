# Planning Checklist

Quick reference checklist for software planning.

---

## Pre-Planning Checklist

### Requirements
- [ ] Problem statement is clear
- [ ] Success criteria defined
- [ ] Scope boundaries established
- [ ] Out-of-scope items documented
- [ ] Stakeholders identified
- [ ] Constraints known (tech, timeline, budget)

### Context Gathering
- [ ] Codebase explored
- [ ] Existing patterns identified
- [ ] Dependencies mapped
- [ ] Similar implementations found
- [ ] Breaking change risks assessed

---

## SPACE Framework Checklist

### S - Scope
- [ ] WHAT exactly needs to be built?
- [ ] What is OUT of scope?
- [ ] Acceptance criteria defined?
- [ ] Who is the end user?
- [ ] What does "done" look like?

### P - Probe
- [ ] Existing code patterns found?
- [ ] Reference implementations identified?
- [ ] Dependencies documented?
- [ ] Recent changes reviewed?
- [ ] Integration points mapped?

### A - Analyze
- [ ] Risks identified?
- [ ] Risk mitigations planned?
- [ ] Tradeoffs documented?
- [ ] Assumptions listed?
- [ ] Rollback strategy defined?

### C - Construct
- [ ] Tasks atomic and testable?
- [ ] Dependencies ordered correctly?
- [ ] Parallel work identified?
- [ ] Checkpoints defined?
- [ ] Verification methods clear?

### E - Execute
- [ ] TodoWrite populated?
- [ ] Test strategy defined?
- [ ] Commit strategy planned?
- [ ] Documentation needs identified?

---

## Risk Assessment Checklist

### Risk Categories
- [ ] Complexity risks identified?
- [ ] Dependency risks identified?
- [ ] Quality risks identified?
- [ ] Knowledge risks identified?
- [ ] Security risks identified?
- [ ] Performance risks identified?

### Risk Response
- [ ] Critical risks have mitigation?
- [ ] High risks have mitigation?
- [ ] Risks assigned owners?
- [ ] Rollback plan exists?

---

## Task Decomposition Checklist

### Task Quality
- [ ] Each task has single responsibility?
- [ ] Each task has clear verification?
- [ ] Tasks are appropriately sized?
- [ ] Dependencies explicitly listed?
- [ ] No implicit assumptions?

### Task Organization
- [ ] Phases defined?
- [ ] Checkpoints placed?
- [ ] Parallelization opportunities identified?
- [ ] Critical path understood?

---

## Implementation Readiness Checklist

### Technical
- [ ] Architecture approach decided?
- [ ] Data structures designed?
- [ ] API contracts defined?
- [ ] Error handling planned?
- [ ] Logging strategy defined?

### Quality
- [ ] Test cases outlined?
- [ ] Edge cases identified?
- [ ] Performance requirements known?
- [ ] Security considerations addressed?

### Process
- [ ] Plan reviewed?
- [ ] Questions resolved?
- [ ] TodoWrite ready?
- [ ] First task clear?

---

## Post-Implementation Checklist

### Verification
- [ ] All tests pass?
- [ ] Lint/typecheck clean?
- [ ] Manual testing complete?
- [ ] Edge cases tested?
- [ ] Performance acceptable?

### Documentation
- [ ] Code commented where needed?
- [ ] API documentation updated?
- [ ] Architecture docs updated?
- [ ] README updated if needed?

### Cleanup
- [ ] Dead code removed?
- [ ] Debug code removed?
- [ ] TODOs addressed or ticketed?
- [ ] Dependencies cleaned?

---

## Quick Decision Matrix

```
Task Type → Planning Level

Simple bug fix     → No formal plan
Small feature      → Quick plan (5 min)
Multi-file change  → Standard plan (15-30 min)
Large feature      → Comprehensive plan (1+ hr)
Architecture       → Full planning process
Migration          → Full planning process
```

---

## Warning Signs

### Plan Needs More Work
- [ ] "It depends" appears often
- [ ] Can't explain in simple terms
- [ ] Too many unknowns
- [ ] No clear verification method
- [ ] Missing rollback strategy

### Over-Planning
- [ ] Spending more time planning than doing
- [ ] Planning for hypothetical futures
- [ ] Excessive documentation
- [ ] Analysis paralysis

### Under-Planning
- [ ] Starting without clear goal
- [ ] "I'll figure it out as I go"
- [ ] No risk consideration
- [ ] No verification defined
