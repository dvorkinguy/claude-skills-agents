# AGENTS.md Manager Skill

Manage AGENTS.md files following the open standard for AI coding agent context.

**Triggers:** `agents.md`, `create agents`, `update agents`, `agent context`, `ai agent instructions`

## What is AGENTS.md?

AGENTS.md is a simple, open format for guiding AI coding agents. It provides:
- Directory-specific context (like .gitignore inheritance)
- Executable commands and examples
- Clear boundaries (Always/Ask First/Never)
- Tech stack and project structure

**Standard:** [agents.md](https://agents.md) | [GitHub](https://github.com/agentsmd/agents.md)

## When to Create AGENTS.md Files

1. **Root level** - Project-wide context
2. **App directories** - App-specific instructions (apps/www, apps/api)
3. **Package directories** - Shared package context
4. **Complex subdirectories** - When context differs from parent

## Required Sections

Every AGENTS.md should include:

```markdown
# [Directory Name] - Agent Instructions

## Your Role
[Specific persona and expertise for this directory]

## Tech Stack
[Technologies with versions]

## Commands You Can Use
[Executable commands with flags]

## Project Structure
[Directory layout with purposes]

## Code Standards
[Examples with ✅ good / ❌ bad patterns]

## Boundaries
### ✅ Always Do
### ⚠️ Ask First
### 🚫 Never Do
```

## Best Practices

### Be Specific
```markdown
<!-- ✅ Good -->
pnpm test --coverage --watch

<!-- ❌ Bad -->
Run the tests
```

### Use Code Examples
```markdown
<!-- ✅ Good -->
// ✅ Correct pattern
export function getUser(id: string): Promise<User> { ... }

// ❌ Avoid this
export default function(id) { ... }

<!-- ❌ Bad -->
Use proper typing and named exports.
```

### Set Clear Boundaries
```markdown
### ✅ Always Do
- Run `pnpm typecheck` before committing
- Write tests for new features

### ⚠️ Ask First
- Database schema changes
- Adding new dependencies

### 🚫 Never Do
- Commit directly to main
- Delete migration files
```

## Workflow: Create AGENTS.md

1. **Analyze directory** - Understand purpose and tech stack
2. **Identify commands** - List executable commands
3. **Document patterns** - Show code examples
4. **Set boundaries** - Define always/ask/never rules
5. **Add structure** - Include file layout

## Workflow: Update AGENTS.md

1. **Read existing file** - Understand current context
2. **Identify gaps** - What's missing or outdated?
3. **Validate commands** - Ensure they still work
4. **Update examples** - Reflect current patterns
5. **Review boundaries** - Adjust as project evolves

## Integration with CLAUDE.md

| File | Purpose | Scope |
|------|---------|-------|
| `CLAUDE.md` | Claude Code specific instructions | Per-project |
| `AGENTS.md` | Universal AI agent context | Per-directory |

CLAUDE.md can reference AGENTS.md files and vice versa. They complement each other.

## Template: Root AGENTS.md

```markdown
# [Project Name] - AI Agent Instructions

## Project Overview
[Brief description and purpose]

## Tech Stack
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Next.js | 15.x |
| Database | PostgreSQL | 16 |

## Commands You Can Use
\`\`\`bash
pnpm dev          # Start development
pnpm build        # Production build
pnpm test         # Run tests
\`\`\`

## Project Structure
\`\`\`
project/
├── apps/           # Applications
├── packages/       # Shared packages
└── AGENTS.md       # This file
\`\`\`

## Boundaries
### ✅ Always Do
- Follow existing patterns
- Write tests for changes

### ⚠️ Ask First
- Adding dependencies
- Schema changes

### 🚫 Never Do
- Commit to main directly
- Hardcode secrets

## Directory-Specific Agents
- `apps/api/AGENTS.md` - API specifics
- `apps/web/AGENTS.md` - Frontend specifics
```

## Template: App AGENTS.md

```markdown
# [App Name] - Agent Instructions

## Your Role
You are working on [app description].

## Tech Stack
| Component | Technology |
|-----------|------------|
| Framework | Next.js |
| Styling | TailwindCSS |

## Commands
\`\`\`bash
pnpm dev    # Start app
pnpm build  # Build app
pnpm test   # Run tests
\`\`\`

## Code Standards
\`\`\`typescript
// ✅ Good
export function Component({ prop }: Props) { ... }

// ❌ Bad
export default function({ prop }) { ... }
\`\`\`

## Boundaries
### ✅ Always
### ⚠️ Ask First
### 🚫 Never
```

## Validation Checklist

Before finalizing an AGENTS.md:

- [ ] Commands are executable and tested
- [ ] Tech stack includes versions
- [ ] Code examples are copy-pasteable
- [ ] Boundaries are specific, not vague
- [ ] Structure matches actual directory
- [ ] No sensitive information included
