# Security Hardened

Security patterns and checklists for Export Arena. Use before any production deployment.

## Triggers

Use when:
- Building authentication flows
- Creating API endpoints
- Handling user input
- Processing payments
- Before production deployment

## OWASP Top 10 Checklist

### 1. Injection Prevention

```typescript
// GOOD: Parameterized queries (Drizzle)
await db.query.users.findFirst({
  where: eq(users.id, userId), // Safe - parameterized
})

// BAD: String interpolation
const result = await db.execute(`SELECT * FROM users WHERE id = '${userId}'`) // VULNERABLE
```

### 2. Broken Authentication

```typescript
// Clerk handles auth - use their patterns
import { getAuth } from '@clerk/nextjs/server'

export default async function handler(req, res) {
  const { userId, sessionId } = getAuth(req)

  if (!userId || !sessionId) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  // Proceed with authenticated request
}
```

### 3. Sensitive Data Exposure

```typescript
// NEVER log sensitive data
console.log('User:', { id: user.id, email: '***' }) // GOOD
console.log('User:', user) // BAD - may include sensitive fields

// NEVER return sensitive data in API
return res.json({
  id: user.id,
  email: user.email,
  // password: user.passwordHash, // NEVER
  // apiKey: user.apiKey, // NEVER
})
```

### 4. XXE Prevention

```typescript
// Disable XML external entities if using XML
import { XMLParser } from 'fast-xml-parser'

const parser = new XMLParser({
  allowBooleanAttributes: true,
  // Disable external entities
  processEntities: false,
})
```

### 5. Broken Access Control

```typescript
// Always verify ownership
async function updatePost(postId: string, userId: string, data: PostData) {
  const post = await db.query.posts.findFirst({
    where: eq(posts.id, postId),
  })

  // Verify ownership
  if (post?.authorId !== userId) {
    throw new Error('Not authorized to update this post')
  }

  await db.update(posts).set(data).where(eq(posts.id, postId))
}
```

### 6. Security Misconfiguration

```typescript
// next.config.js
module.exports = {
  headers: async () => [
    {
      source: '/(.*)',
      headers: [
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-XSS-Protection', value: '1; mode=block' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        {
          key: 'Content-Security-Policy',
          value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
        },
      ],
    },
  ],
}
```

### 7. XSS Prevention

```tsx
// React escapes by default - GOOD
<div>{userInput}</div>

// AVOID dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userInput }} /> // VULNERABLE

// If HTML is needed, sanitize first
import DOMPurify from 'dompurify'
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(htmlContent) }} />
```

### 8. Insecure Deserialization

```typescript
// Validate input with Zod
import { z } from 'zod'

const UserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150).optional(),
})

export default async function handler(req, res) {
  const result = UserSchema.safeParse(req.body)

  if (!result.success) {
    return res.status(400).json({ error: result.error.issues })
  }

  const validData = result.data
  // Proceed with validated data
}
```

### 9. Vulnerable Components

```bash
# Audit dependencies regularly
pnpm audit

# Update dependencies
pnpm update

# Check for known vulnerabilities
npx snyk test
```

### 10. Insufficient Logging

```typescript
// Log security events
import { logger } from '@/lib/logger'

// Authentication
logger.info('User logged in', { userId, ip: req.ip })
logger.warn('Failed login attempt', { email, ip: req.ip })

// Authorization
logger.warn('Unauthorized access attempt', { userId, resource })

// Data changes
logger.info('User updated profile', { userId, fields: Object.keys(data) })
```

## API Security Checklist

```typescript
export default async function handler(req, res) {
  // 1. Method validation
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  // 2. Authentication
  const { userId } = getAuth(req)
  if (!userId) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  // 3. Rate limiting
  const rateLimitResult = await rateLimit.check(req, userId)
  if (!rateLimitResult.success) {
    return res.status(429).json({ error: 'Too many requests' })
  }

  // 4. Input validation
  const result = InputSchema.safeParse(req.body)
  if (!result.success) {
    return res.status(400).json({ error: 'Invalid input' })
  }

  // 5. Authorization (resource-level)
  const resource = await getResource(result.data.id)
  if (resource.ownerId !== userId) {
    return res.status(403).json({ error: 'Forbidden' })
  }

  // 6. Process request
  try {
    const data = await processRequest(result.data)
    return res.status(200).json({ data })
  } catch (error) {
    logger.error('API Error', { error, userId })
    return res.status(500).json({ error: 'Internal error' })
  }
}
```

## Environment Variables

```bash
# NEVER commit secrets
# Add to .gitignore: .env.local, .env.*.local

# Required secrets (must be set in production)
CLERK_SECRET_KEY=sk_live_...
DATABASE_URL=postgresql://...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
CLERK_WEBHOOK_SECRET=whsec_...
```

## Rate Limiting

```typescript
// Using Upstash Rate Limit
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
  analytics: true,
})

export async function middleware(req) {
  const ip = req.ip ?? 'anonymous'
  const { success, limit, remaining } = await ratelimit.limit(ip)

  if (!success) {
    return new Response('Too Many Requests', { status: 429 })
  }
}
```

## Webhook Verification

```typescript
// Clerk webhook verification
import { Webhook } from 'svix'

export default async function handler(req, res) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET!

  const svix_id = req.headers['svix-id']
  const svix_timestamp = req.headers['svix-timestamp']
  const svix_signature = req.headers['svix-signature']

  const wh = new Webhook(WEBHOOK_SECRET)

  try {
    const evt = wh.verify(JSON.stringify(req.body), {
      'svix-id': svix_id,
      'svix-timestamp': svix_timestamp,
      'svix-signature': svix_signature,
    })

    // Process verified webhook
  } catch (err) {
    return res.status(401).json({ error: 'Invalid signature' })
  }
}
```

## Pre-Deployment Checklist

- [ ] All API routes authenticated
- [ ] Input validation on all endpoints (Zod)
- [ ] No sensitive data in logs
- [ ] Rate limiting enabled
- [ ] CORS configured correctly
- [ ] Security headers set
- [ ] Dependencies audited (`pnpm audit`)
- [ ] Secrets in environment variables only
- [ ] Webhook signatures verified
- [ ] Error messages don't leak info
- [ ] HTTPS enforced
- [ ] Database connections use SSL
