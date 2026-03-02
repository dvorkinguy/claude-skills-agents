# Export Arena Stack

Expert guidance for the Export Arena monorepo architecture, patterns, and conventions.

## Triggers

Use when:
- Working on Export Arena codebase
- Questions about project structure, conventions, patterns
- Creating new components, pages, or features
- Understanding the monorepo architecture

## Tech Stack

| Component | Technology | Location |
|-----------|------------|----------|
| Framework | Next.js 15+ (App Router + Pages Router) | apps/* |
| Build | Turborepo + pnpm | root |
| Auth | Clerk | apps/www, apps/studio |
| Database | Neon PostgreSQL | packages/database |
| ORM | Drizzle ORM | packages/database |
| Vector DB | Neon pgvector | packages/database |
| UI | Radix UI + TailwindCSS + shadcn/ui | packages/ui |
| CMS | Payload CMS | apps/cms |
| Testing | Playwright (E2E), Vitest (unit) | */e2e, */tests |

## Monorepo Structure

```
exportarena-supabase-v2/
├── apps/
│   ├── www/          # Marketing site (localhost:3000)
│   ├── studio/       # User dashboard (localhost:54323)
│   └── cms/          # Payload CMS (localhost:3030)
├── packages/
│   ├── database/     # Drizzle ORM + Neon
│   ├── ui/           # Component library
│   ├── ui-patterns/  # UI patterns
│   ├── icons/        # Icon components
│   └── common/       # Shared utilities
```

## Dark Theme (MANDATORY)

Export Arena uses dark theme ONLY. No light mode.

```tsx
// Correct - dark theme classes
<div className="bg-background text-foreground">
<div className="bg-surface-100 border-default">

// NEVER add light mode variants
// NEVER use: "dark:bg-x" pattern (already dark)
```

## Component Patterns

### Creating New Components

```tsx
// packages/ui/src/components/NewComponent.tsx
import { cn } from '../lib/utils'

interface NewComponentProps {
  className?: string
  children: React.ReactNode
}

export function NewComponent({ className, children }: NewComponentProps) {
  return (
    <div className={cn('base-styles', className)}>
      {children}
    </div>
  )
}
```

### Using Shared UI

```tsx
import { Button, Input, Card } from 'ui'
import { IconArrowRight } from 'icons'
```

## Database Patterns

```typescript
import { db, users, eq } from 'database'

// Query
const user = await db.query.users.findFirst({
  where: eq(users.id, clerkUserId),
})

// Insert
await db.insert(users).values({ ... })

// Update
await db.update(users).set({ ... }).where(eq(users.id, id))
```

## API Routes (Next.js)

```typescript
// apps/www/pages/api/example.ts (Pages Router)
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  // Handle request
  res.status(200).json({ success: true })
}
```

## Environment Variables

```bash
# Auth (Clerk)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
CLERK_WEBHOOK_SECRET=whsec_...

# Database (Neon)
DATABASE_URL=postgresql://...@neon.tech/neondb

# CMS (Payload)
PAYLOAD_SECRET=...
CMS_SITE_ORIGIN=http://localhost:3030
```

## Git Workflow (GitFlow)

```bash
# Feature development
git checkout develop
git checkout -b feature/phase-X-description
# Work...
git commit -m "feat: Description"
git push -u origin feature/phase-X-description
# PR to develop -> merge

# Tags for releases
git tag -a v0.X.Y-description -m "Description"
```

## Key Commands

```bash
# Development
pnpm dev --filter www      # Marketing site
pnpm dev --filter cms      # CMS admin
pnpm dev --filter studio   # Dashboard

# Database
cd packages/database
pnpm db:push               # Push schema to Neon
pnpm db:studio             # Drizzle Studio

# Testing
pnpm test:e2e              # Playwright
```

## SEO Keywords

Target keywords for content:
- Global Trade AI, Export Automation, Import Automation
- AI for SMBs, Trade Documentation AI
- Customs Compliance AI, HS Code Automation
- AI Workforce, Digital Employees
