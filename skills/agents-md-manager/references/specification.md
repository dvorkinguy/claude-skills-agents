# AGENTS.md Specification Reference

> Official specification from [agents.md](https://agents.md)

## Overview

AGENTS.md is a simple, open format for guiding coding agents. It's a dedicated, predictable place to provide the context and instructions to help AI coding agents work on your project.

## Key Principles

1. **Complementary to README** - README is for humans, AGENTS.md is for AI agents
2. **Inheritance** - Agents use the nearest AGENTS.md (like .gitignore)
3. **Actionable** - Focus on executable commands and specific patterns
4. **Portable** - Works across AI tools (OpenAI Codex, Google Jules, Cursor, etc.)

## Adoption

- 60,000+ open-source repositories
- Supported by: OpenAI, Google, Cursor, Factory, GitHub Copilot
- MIT licensed

## File Placement

```
project/
├── AGENTS.md           # Project root (required)
├── apps/
│   ├── api/
│   │   └── AGENTS.md   # API-specific (optional)
│   └── web/
│       └── AGENTS.md   # Frontend-specific (optional)
└── packages/
    └── shared/
        └── AGENTS.md   # Package-specific (optional)
```

## Recommended Sections

### 1. Header with Metadata (Optional)
```yaml
---
name: api-agent
description: Backend API development agent
---
```

### 2. Your Role
```markdown
## Your Role
You are working on [specific app/package description].
Your expertise includes [relevant technologies].
```

### 3. Tech Stack
```markdown
## Tech Stack
| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Node.js | 20.x |
| Framework | Express | 4.x |
```

### 4. Commands
```markdown
## Commands You Can Use
\`\`\`bash
npm run dev       # Start dev server
npm run build     # Production build
npm run test      # Run tests
npm run lint      # Lint code
\`\`\`
```

### 5. Project Structure
```markdown
## Project Structure
\`\`\`
src/
├── routes/       # API endpoints
├── services/     # Business logic
├── models/       # Data models
└── utils/        # Helpers
\`\`\`
```

### 6. Code Standards
```markdown
## Code Standards

### Naming
- Files: kebab-case (user-service.ts)
- Classes: PascalCase (UserService)
- Functions: camelCase (getUser)

### Patterns
\`\`\`typescript
// ✅ Good: Explicit types, error handling
async function getUser(id: string): Promise<User | null> {
  try {
    return await db.users.findUnique({ where: { id } })
  } catch (error) {
    logger.error('Failed to get user', { id, error })
    return null
  }
}

// ❌ Bad: No types, no error handling
async function getUser(id) {
  return db.users.findUnique({ where: { id } })
}
\`\`\`
```

### 7. Boundaries
```markdown
## Boundaries

### ✅ Always Do
- Validate all user input
- Use parameterized queries
- Write tests for new features
- Follow existing patterns

### ⚠️ Ask First
- Database schema changes
- Adding new dependencies
- Modifying authentication
- API breaking changes

### 🚫 Never Do
- Hardcode credentials
- Skip error handling
- Remove existing tests
- Use `any` type without comment
```

### 8. Key Files
```markdown
## Key Files
| Purpose | File |
|---------|------|
| Entry point | src/index.ts |
| Config | src/config.ts |
| Routes | src/routes/index.ts |
| Database | src/db/client.ts |
```

## Anti-Patterns to Avoid

### Vague Instructions
```markdown
<!-- ❌ Bad -->
Be a helpful coding assistant.

<!-- ✅ Good -->
You are working on a Node.js REST API using Express 4.x with PostgreSQL.
Focus on type safety, error handling, and test coverage.
```

### Missing Commands
```markdown
<!-- ❌ Bad -->
Run the tests before committing.

<!-- ✅ Good -->
npm run test -- --coverage --watch
```

### Abstract Explanations
```markdown
<!-- ❌ Bad -->
Use proper error handling.

<!-- ✅ Good -->
try {
  const result = await operation()
  return { success: true, data: result }
} catch (error) {
  logger.error('Operation failed', error)
  return { success: false, error: error.message }
}
```

### Unclear Boundaries
```markdown
<!-- ❌ Bad -->
Be careful with database changes.

<!-- ✅ Good -->
### ⚠️ Ask First
- Adding/removing columns
- Modifying indexes
- Changing foreign keys
```

## Specialized Agents (GitHub Copilot)

GitHub Copilot supports multiple agents in one file:

```markdown
---
name: docs-agent
description: Technical documentation specialist
---

## Your Role
Generate and update technical documentation.
Read source code but never modify it.

---
name: test-agent
description: Quality assurance specialist
---

## Your Role
Write and maintain tests.
Never remove failing tests without fixing.

---
name: security-agent
description: Security analysis specialist
---

## Your Role
Review code for vulnerabilities.
Flag issues but ask before fixing.
```

## Sources

- [Official Site](https://agents.md)
- [GitHub Repository](https://github.com/agentsmd/agents.md)
- [OpenAI Codex Guide](https://developers.openai.com/codex/guides/agents-md/)
- [GitHub Blog](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)
- [InfoQ Article](https://www.infoq.com/news/2025/08/agents-md/)
