# Clerk + Neon Auth Patterns

Integration patterns for Clerk authentication with Neon PostgreSQL and Drizzle ORM.

## Triggers

Use when:
- Implementing authentication flows
- Setting up Clerk webhooks for user sync
- Querying user data from database
- Protecting API routes or pages

## Architecture

```
Clerk (Auth Provider)
    │
    ├─── Frontend SDK ──→ Sign In/Up UI
    │
    └─── Webhooks ──────→ /api/webhooks/clerk
                              │
                              ▼
                         Neon PostgreSQL
                         (users table synced)
```

## User Sync Webhook

```typescript
// apps/www/pages/api/webhooks/clerk.ts
import { Webhook } from 'svix'
import { db, users, eq } from 'database'
import type { WebhookEvent } from '@clerk/nextjs/server'

export default async function handler(req, res) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET

  // Verify webhook signature
  const wh = new Webhook(WEBHOOK_SECRET)
  const payload = await wh.verify(
    JSON.stringify(req.body),
    req.headers as Record<string, string>
  )

  const evt = payload as WebhookEvent

  switch (evt.type) {
    case 'user.created':
      await db.insert(users).values({
        id: evt.data.id,
        email: evt.data.email_addresses[0]?.email_address,
        firstName: evt.data.first_name,
        lastName: evt.data.last_name,
        imageUrl: evt.data.image_url,
        createdAt: new Date(),
        updatedAt: new Date(),
      })
      break

    case 'user.updated':
      await db.update(users)
        .set({
          email: evt.data.email_addresses[0]?.email_address,
          firstName: evt.data.first_name,
          lastName: evt.data.last_name,
          imageUrl: evt.data.image_url,
          updatedAt: new Date(),
        })
        .where(eq(users.id, evt.data.id))
      break

    case 'user.deleted':
      await db.delete(users).where(eq(users.id, evt.data.id))
      break
  }

  res.status(200).json({ success: true })
}
```

## Frontend Protection

### Middleware (All Routes)

```typescript
// apps/www/middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks/(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect()
  }
})

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
}
```

### Page-Level Protection

```tsx
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function ProtectedPage() {
  const { userId } = await auth()

  if (!userId) {
    redirect('/sign-in')
  }

  return <div>Protected content</div>
}
```

### Component-Level

```tsx
import { SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

export function Header() {
  return (
    <header>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
      <SignedOut>
        <a href="/sign-in">Sign In</a>
      </SignedOut>
    </header>
  )
}
```

## API Route Protection

```typescript
// Pages Router
import { getAuth } from '@clerk/nextjs/server'

export default async function handler(req, res) {
  const { userId } = getAuth(req)

  if (!userId) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  // Fetch user from database
  const user = await db.query.users.findFirst({
    where: eq(users.id, userId),
  })

  res.status(200).json({ user })
}
```

## Database Schema

```typescript
// packages/database/schema/users.ts
import { pgTable, text, timestamp } from 'drizzle-orm/pg-core'

export const users = pgTable('users', {
  id: text('id').primaryKey(), // Clerk user ID
  email: text('email').notNull().unique(),
  firstName: text('first_name'),
  lastName: text('last_name'),
  imageUrl: text('image_url'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})
```

## Environment Setup

```bash
# .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...

NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

## Testing Auth Flows

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test('sign in flow', async ({ page }) => {
  await page.goto('/sign-in')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password')
  await page.click('button[type="submit"]')
  await page.waitForURL('/dashboard')
  expect(page.url()).toContain('/dashboard')
})
```

## Common Patterns

### Get Current User with DB Data

```typescript
import { auth } from '@clerk/nextjs/server'
import { db, users, eq } from 'database'

export async function getCurrentUser() {
  const { userId } = await auth()
  if (!userId) return null

  return db.query.users.findFirst({
    where: eq(users.id, userId),
  })
}
```

### Organization-Based Access

```typescript
const { userId, orgId } = await auth()

// User must be in an organization
if (!orgId) {
  redirect('/select-organization')
}

// Check org membership
const member = await db.query.organizationMembers.findFirst({
  where: and(
    eq(organizationMembers.userId, userId),
    eq(organizationMembers.organizationId, orgId)
  ),
})
```
