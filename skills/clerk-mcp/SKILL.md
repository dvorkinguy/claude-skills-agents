# Clerk MCP Integration

Reference for Clerk authentication with Export Arena.

## Dashboard

- **Clerk Dashboard:** https://dashboard.clerk.com
- **Application:** Export Arena

## Environment Variables

```bash
# Required
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Webhook (for user sync)
CLERK_WEBHOOK_SECRET=whsec_...

# Route configuration
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

## Webhook Configuration

### Setup in Clerk Dashboard

1. Go to Webhooks → Add Endpoint
2. URL: `https://exportarena.com/api/webhooks/clerk`
3. Events:
   - `user.created`
   - `user.updated`
   - `user.deleted`
4. Copy signing secret to `CLERK_WEBHOOK_SECRET`

### Webhook Handler

```typescript
// apps/www/pages/api/webhooks/clerk.ts
import { Webhook } from 'svix'
import { db, users, eq } from 'database'

export default async function handler(req, res) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET!

  // Verify signature
  const wh = new Webhook(WEBHOOK_SECRET)
  const payload = wh.verify(
    JSON.stringify(req.body),
    req.headers as Record<string, string>
  )

  const { type, data } = payload

  switch (type) {
    case 'user.created':
      await db.insert(users).values({
        id: data.id,
        email: data.email_addresses[0]?.email_address,
        // ...
      })
      break
    // Handle other events
  }

  return res.status(200).json({ success: true })
}
```

## SDK Usage

### Server-Side (Pages Router)

```typescript
import { getAuth } from '@clerk/nextjs/server'

export default async function handler(req, res) {
  const { userId } = getAuth(req)

  if (!userId) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  // Proceed with authenticated request
}
```

### Server-Side (App Router)

```typescript
import { auth } from '@clerk/nextjs/server'

export default async function Page() {
  const { userId } = await auth()

  if (!userId) {
    redirect('/sign-in')
  }

  // Render authenticated content
}
```

### Client-Side Components

```tsx
import { SignedIn, SignedOut, UserButton, SignInButton } from '@clerk/nextjs'

export function Header() {
  return (
    <header>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
      <SignedOut>
        <SignInButton mode="modal">
          <button>Sign In</button>
        </SignInButton>
      </SignedOut>
    </header>
  )
}
```

### Hooks

```tsx
'use client'

import { useAuth, useUser } from '@clerk/nextjs'

export function Profile() {
  const { isSignedIn, userId } = useAuth()
  const { user } = useUser()

  if (!isSignedIn) return null

  return (
    <div>
      <p>Hello, {user?.firstName}</p>
    </div>
  )
}
```

## Middleware

```typescript
// apps/www/middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks/(.*)',
  '/blog(.*)',
  '/pricing',
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

## Organizations (Optional)

Enable organizations for team features:

```tsx
import { useOrganization } from '@clerk/nextjs'

export function TeamDashboard() {
  const { organization, isLoaded } = useOrganization()

  if (!isLoaded) return <Loading />

  if (!organization) {
    return <CreateOrganizationPrompt />
  }

  return <Dashboard org={organization} />
}
```

## Custom Sign In/Up Pages

```tsx
// apps/www/app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignIn
        appearance={{
          elements: {
            rootBox: 'mx-auto',
            card: 'bg-surface-100 border-default',
          },
        }}
      />
    </div>
  )
}
```

## Testing

For local development with webhooks:

```bash
# Use Clerk dev webhook URL
# Or use ngrok for local testing
ngrok http 3000

# Set webhook URL in Clerk Dashboard
# https://xxx.ngrok.io/api/webhooks/clerk
```

## Metadata

Store additional user data:

```typescript
import { clerkClient } from '@clerk/nextjs/server'

// Update public metadata
await clerkClient.users.updateUserMetadata(userId, {
  publicMetadata: {
    plan: 'pro',
    role: 'admin',
  },
})
```

## Rate Limits

Clerk has rate limits on API calls:
- 500 requests/minute (Development)
- 2000 requests/minute (Production)

Cache user data when possible.
