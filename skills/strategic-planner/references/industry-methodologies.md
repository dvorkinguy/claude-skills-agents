# Industry Best Practices & Methodologies

Proven software development methodologies to apply during planning.

## SOLID Principles

### Single Responsibility Principle (SRP)
**A class/module should have only one reason to change.**

**Planning Application:**
- Each task should address one concern
- Separate data, logic, and presentation
- Identify distinct responsibilities before coding

```
❌ UserService handles: auth, profile, notifications
✓ AuthService, ProfileService, NotificationService
```

### Open/Closed Principle (OCP)
**Open for extension, closed for modification.**

**Planning Application:**
- Design for extensibility from the start
- Use interfaces and abstractions
- Plan for future variations

```
❌ Adding payment method requires modifying PaymentProcessor
✓ PaymentProcessor accepts PaymentMethod interface
```

### Liskov Substitution Principle (LSP)
**Subtypes must be substitutable for base types.**

**Planning Application:**
- Verify inheritance hierarchies make sense
- Ensure derived classes honor base contracts
- Plan test cases for substitutability

### Interface Segregation Principle (ISP)
**Clients shouldn't depend on interfaces they don't use.**

**Planning Application:**
- Design focused interfaces
- Split large interfaces into smaller ones
- Plan for minimal dependencies

### Dependency Inversion Principle (DIP)
**Depend on abstractions, not concretions.**

**Planning Application:**
- Plan dependency injection
- Design interfaces before implementations
- Identify what should be abstracted

## Test-Driven Development (TDD)

### Red-Green-Refactor Cycle

```
1. RED: Write failing test
2. GREEN: Write minimal code to pass
3. REFACTOR: Improve without changing behavior
4. Repeat
```

### TDD Planning Integration

**Before Implementation:**
1. Define acceptance criteria as test scenarios
2. List test cases for each component
3. Identify edge cases upfront
4. Plan test data requirements

**Task Structure with TDD:**
```markdown
Task: Add user validation

Tests to Write First:
- [ ] Test: Rejects empty email
- [ ] Test: Rejects invalid email format
- [ ] Test: Accepts valid email
- [ ] Test: Rejects duplicate email
- [ ] Test: Handles case sensitivity

Implementation:
- [ ] Create validation function
- [ ] Integrate with form
- [ ] Add error messages
```

### Test Categories to Plan

1. **Unit Tests**: Individual functions/methods
2. **Integration Tests**: Component interactions
3. **E2E Tests**: User workflows
4. **Performance Tests**: Speed/resource usage
5. **Security Tests**: Vulnerability checks

## Domain-Driven Design (DDD)

### Strategic Design

**Bounded Contexts**
Identify distinct business domains that should be separated.

```
E-commerce Platform:
├── Catalog Context (products, categories)
├── Ordering Context (carts, orders)
├── Inventory Context (stock, warehouses)
├── Shipping Context (delivery, tracking)
└── Payment Context (transactions, refunds)
```

**Context Mapping**
Define relationships between contexts.

| Relationship | Description | Example |
|--------------|-------------|---------|
| Partnership | Mutual dependency | Ordering ↔ Inventory |
| Customer-Supplier | Upstream/downstream | Catalog → Ordering |
| Conformist | Accept upstream model | External API |
| Anti-corruption Layer | Translate external models | Legacy integration |

### Tactical Design

**Entities**: Objects with identity
```
- User (identified by ID)
- Order (identified by order number)
- Product (identified by SKU)
```

**Value Objects**: Objects without identity
```
- Money (amount + currency)
- Address (street, city, postal)
- DateRange (start, end)
```

**Aggregates**: Consistency boundaries
```
Order Aggregate:
├── Order (root)
├── OrderLine[]
├── ShippingAddress
└── PaymentInfo
```

**Domain Events**: Significant occurrences
```
- OrderPlaced
- PaymentReceived
- ItemShipped
```

### DDD Planning Checklist
- [ ] Identify bounded contexts
- [ ] Define ubiquitous language
- [ ] Map context relationships
- [ ] Identify aggregates
- [ ] Define domain events
- [ ] Plan anti-corruption layers

## Clean Architecture

### Layer Structure

```
┌─────────────────────────────────────────┐
│           Frameworks & Drivers          │ (Web, DB, External)
├─────────────────────────────────────────┤
│          Interface Adapters             │ (Controllers, Gateways)
├─────────────────────────────────────────┤
│          Application Business           │ (Use Cases)
├─────────────────────────────────────────┤
│          Enterprise Business            │ (Entities)
└─────────────────────────────────────────┘
```

**Dependency Rule:** Dependencies point inward only.

### Planning with Clean Architecture
1. Start from entities (core business objects)
2. Define use cases (application logic)
3. Design interfaces for external services
4. Implement adapters last

### Layer Planning Template
```markdown
## Feature: [Name]

### Entities (Core)
- [ ] Define business entities
- [ ] Define value objects
- [ ] Define business rules

### Use Cases (Application)
- [ ] Define use case inputs/outputs
- [ ] Implement business logic
- [ ] Define repository interfaces

### Adapters (Interface)
- [ ] Implement controllers
- [ ] Implement repositories
- [ ] Define API contracts

### Frameworks (Infrastructure)
- [ ] Database implementation
- [ ] HTTP handling
- [ ] External service clients
```

## YAGNI (You Aren't Gonna Need It)

### Principle
Don't build features until they're actually needed.

### Planning Application
- Question every "nice to have"
- Build simplest solution first
- Document deferred features, don't implement

### YAGNI Checklist
- [ ] Is this required for current requirements?
- [ ] Is there a simpler alternative?
- [ ] What's the cost of adding later vs now?
- [ ] Am I solving an imaginary problem?

## DRY (Don't Repeat Yourself)

### Principle
Every piece of knowledge should have a single, unambiguous representation.

### Planning Application
- Identify reusable patterns early
- Plan shared utilities/components
- Balance DRY with readability

### DRY Considerations
```
✓ Abstract when pattern repeats 3+ times
✓ Abstract when logic changes together
✗ Don't abstract superficially similar code
✗ Don't sacrifice clarity for DRY
```

## KISS (Keep It Simple, Stupid)

### Principle
Prefer simple solutions over complex ones.

### Planning Application
- Start with simplest approach
- Add complexity only when proven necessary
- Question every abstraction layer

### Complexity Checklist
- [ ] Is this the simplest solution?
- [ ] Can I explain it in one sentence?
- [ ] Would a junior developer understand it?
- [ ] What's the maintenance burden?

## Agile/Iterative Planning

### MVP Approach
Build minimum viable product first, then iterate.

```
Iteration 1: Core functionality
Iteration 2: Essential features
Iteration 3: Nice-to-haves
Iteration 4: Polish
```

### User Story Format
```
As a [user type]
I want [functionality]
So that [business value]

Acceptance Criteria:
- Given [context], when [action], then [result]
```

### Story Point Estimation

| Points | Description |
|--------|-------------|
| 1 | Trivial, well-understood |
| 2 | Small, minimal unknowns |
| 3 | Medium, some complexity |
| 5 | Large, significant complexity |
| 8 | Very large, many unknowns |
| 13+ | Epic, needs breakdown |

## Code Review Best Practices

### Pre-Review Planning
- [ ] Self-review before requesting review
- [ ] Tests passing
- [ ] Documentation updated
- [ ] PR description complete

### Review Focus Areas
1. **Correctness**: Does it solve the problem?
2. **Design**: Is it well-structured?
3. **Readability**: Is it understandable?
4. **Performance**: Are there concerns?
5. **Security**: Any vulnerabilities?
6. **Tests**: Adequate coverage?

## Continuous Integration/Deployment

### CI/CD Planning
- [ ] Define pipeline stages
- [ ] Plan automated tests
- [ ] Configure quality gates
- [ ] Plan deployment strategy

### Quality Gates
```
Stage 1: Build
├── Compilation
└── Static analysis

Stage 2: Test
├── Unit tests
├── Integration tests
└── Code coverage threshold

Stage 3: Security
├── Dependency scanning
└── SAST analysis

Stage 4: Deploy
├── Staging deployment
├── Smoke tests
└── Production deployment
```

## Documentation Standards

### Code Documentation
- Document "why" not "what"
- API contracts and interfaces
- Complex algorithms explained
- Architecture decisions recorded (ADRs)

### ADR Format
```markdown
# ADR-001: [Title]

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
[What is the issue?]

## Decision
[What did we decide?]

## Consequences
[What are the results?]
```

## Security by Design

### OWASP Planning
- [ ] Input validation planned
- [ ] Output encoding planned
- [ ] Authentication/authorization designed
- [ ] Session management planned
- [ ] Data protection considered
- [ ] Error handling (no info leakage)
- [ ] Logging/monitoring planned

### Security Checklist
- [ ] Principle of least privilege
- [ ] Defense in depth
- [ ] Fail securely
- [ ] Don't trust services
- [ ] Separation of duties
- [ ] Avoid security by obscurity
- [ ] Keep security simple
- [ ] Fix security issues correctly
