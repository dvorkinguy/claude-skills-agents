# Risk Assessment Guide

Systematic approach to identifying, analyzing, and mitigating risks in software projects.

## Risk Identification

### Categories of Technical Risk

#### 1. Complexity Risks
- **Algorithm Complexity**: Novel algorithms, edge cases, performance requirements
- **Integration Complexity**: Multiple systems, APIs, data synchronization
- **Domain Complexity**: Business rules, compliance, specialized knowledge
- **Scale Complexity**: Data volume, concurrent users, geographic distribution

#### 2. Dependency Risks
- **External APIs**: Third-party availability, rate limits, breaking changes
- **Libraries**: Version conflicts, security vulnerabilities, maintenance status
- **Infrastructure**: Cloud services, database, caching layers
- **Team Dependencies**: Blocking on other teams, shared resources

#### 3. Quality Risks
- **Technical Debt**: Legacy code, poor test coverage, architectural issues
- **Performance**: Bottlenecks, resource constraints, scalability limits
- **Security**: Vulnerabilities, data exposure, compliance gaps
- **Reliability**: Error handling, failover, data consistency

#### 4. Knowledge Risks
- **Unfamiliar Technology**: New frameworks, languages, patterns
- **Undocumented Code**: Missing context, tribal knowledge
- **Complex Domain**: Specialized business logic, regulatory requirements

### Risk Discovery Questions

**For each major component, ask:**

1. **What could fail?**
   - Network failures
   - Invalid input
   - Resource exhaustion
   - Concurrent access conflicts
   - Timeout scenarios

2. **What assumptions are we making?**
   - Data format consistency
   - System availability
   - User behavior
   - Environment configuration

3. **What external factors could impact us?**
   - API changes
   - Infrastructure issues
   - Third-party outages
   - Security threats

4. **What don't we know?**
   - Performance under load
   - Edge case behavior
   - Long-term maintainability

## Risk Analysis

### Probability Assessment

| Level | Description | Indicators |
|-------|-------------|------------|
| **High** | Very likely to occur | New technology, complex integration, tight timeline |
| **Medium** | Possible but not certain | Some unknowns, moderate complexity |
| **Low** | Unlikely but possible | Well-understood domain, proven approach |

### Impact Assessment

| Level | Description | Consequences |
|-------|-------------|--------------|
| **High** | Severe impact | Project failure, security breach, data loss |
| **Medium** | Significant impact | Major delays, degraded functionality |
| **Low** | Minor impact | Small delays, cosmetic issues |

### Risk Matrix

```
         Impact
         Low    Med    High
     +------+------+------+
High |  Med | High | Crit |  Probability
     +------+------+------+
Med  |  Low |  Med | High |
     +------+------+------+
Low  |  Low |  Low |  Med |
     +------+------+------+
```

### Severity Responses

| Severity | Response |
|----------|----------|
| **Critical** | STOP. Address before proceeding. Escalate if needed. |
| **High** | Must have mitigation plan. Monitor closely. |
| **Medium** | Should have mitigation. Accept with monitoring. |
| **Low** | Document and accept. Revisit if changes. |

## Mitigation Strategies

### Strategy Types

#### 1. Avoid
Eliminate the risk by changing approach.
- Choose proven technology over cutting-edge
- Reduce scope to avoid complex features
- Use existing solutions instead of building

#### 2. Mitigate
Reduce probability or impact.
- Add validation to prevent bad input
- Implement caching to reduce API dependency
- Create comprehensive test coverage

#### 3. Transfer
Shift risk to another party.
- Use managed services instead of self-hosted
- Rely on framework security instead of custom
- Delegate to specialist teams

#### 4. Accept
Acknowledge and monitor.
- Document known limitations
- Create monitoring/alerting
- Plan contingency response

### Mitigation Patterns

#### For Complexity Risks
```
Pattern: Incremental Delivery
- Break into small, testable pieces
- Validate assumptions early
- Build simplest version first
- Iterate based on feedback
```

#### For Dependency Risks
```
Pattern: Defensive Integration
- Add timeouts and circuit breakers
- Implement fallback mechanisms
- Cache critical data
- Monitor external service health
```

#### For Quality Risks
```
Pattern: Shift Left
- Write tests before code
- Review early and often
- Automate quality checks
- Address issues immediately
```

#### For Knowledge Risks
```
Pattern: Spike and Learn
- Create proof-of-concept first
- Time-box exploration
- Document findings
- Share knowledge across team
```

## Common Software Risks & Mitigations

### Database Risks

| Risk | Mitigation |
|------|------------|
| Schema migration failure | Test migrations on production copy |
| Performance degradation | Add indexes, query optimization |
| Data corruption | Implement validation, backups |
| Connection pool exhaustion | Configure limits, add monitoring |

### API Integration Risks

| Risk | Mitigation |
|------|------------|
| Breaking changes | Version pinning, contract tests |
| Rate limiting | Implement backoff, caching |
| Availability | Circuit breaker, fallback |
| Security exposure | API keys rotation, least privilege |

### Authentication/Authorization Risks

| Risk | Mitigation |
|------|------------|
| Session hijacking | Secure cookies, HTTPS only |
| Privilege escalation | Server-side validation |
| Credential exposure | Environment variables, secrets manager |
| Token expiry issues | Refresh token flow, graceful handling |

### Frontend Risks

| Risk | Mitigation |
|------|------------|
| XSS vulnerabilities | Output encoding, CSP headers |
| State management bugs | Immutable state, strict typing |
| Bundle size bloat | Code splitting, tree shaking |
| Browser compatibility | Feature detection, polyfills |

### Performance Risks

| Risk | Mitigation |
|------|------------|
| N+1 queries | Eager loading, query optimization |
| Memory leaks | Profiling, cleanup handlers |
| Blocking operations | Async patterns, background jobs |
| Slow renders | Memoization, virtualization |

## Risk Register Template

```markdown
## Risk Register: [Project Name]

### Active Risks

| ID | Risk | Prob | Impact | Severity | Mitigation | Owner | Status |
|----|------|------|--------|----------|------------|-------|--------|
| R-001 | [Description] | H/M/L | H/M/L | Crit/High/Med/Low | [Strategy] | [Who] | Open/Mitigated |

### Resolved Risks

| ID | Risk | Resolution | Date |
|----|------|------------|------|
| R-xxx | [Description] | [How resolved] | [Date] |

### Risk Metrics
- Total Open Risks: X
- Critical: X
- High: X
- Medium: X
- Low: X
```

## Pre-Implementation Risk Checklist

### Technical
- [ ] All dependencies identified and verified
- [ ] Performance requirements defined and achievable
- [ ] Security threats identified and mitigated
- [ ] Error scenarios handled gracefully
- [ ] Rollback strategy defined

### Integration
- [ ] API contracts understood and stable
- [ ] Data formats validated
- [ ] Authentication/authorization verified
- [ ] Rate limits accounted for
- [ ] Timeout handling implemented

### Quality
- [ ] Test strategy defined
- [ ] Critical paths covered
- [ ] Edge cases identified
- [ ] Monitoring/alerting planned
- [ ] Documentation updated

### Knowledge
- [ ] Team has necessary skills
- [ ] Unknowns time-boxed for investigation
- [ ] External dependencies understood
- [ ] Historical context gathered

## Risk Review Triggers

Re-assess risks when:
- Requirements change
- New dependencies added
- Timeline changes
- Team composition changes
- External factors change
- Previous assumptions invalidated
- New issues discovered during implementation
