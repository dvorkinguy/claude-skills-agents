# Dev Environment Doctor

Diagnoses and fixes common development environment issues in the Export Arena monorepo.

## When to Use This Skill

Use `/dev-env-doctor` when encountering:
- "dev not working", "localhost not loading", "pnpm dev errors"
- "500 error", "connection refused", "Invalid host"
- "Turbopack error", "esmExternals"
- CMS or www failing to start
- Database connection issues

## Diagnostic Checklist

### 1. Environment Variables

**Check all .env files:**

```bash
# Root .env (source of truth)
cat .env | grep -E "CLERK|DATABASE|NEON"

# www app
cat apps/www/.env | grep -E "CLERK|SUPABASE"

# CMS app
cat apps/cms/.env | grep -E "DATABASE_URI|S3"
```

**Expected values:**
- `apps/www/.env`: Should have `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY`
- `apps/cms/.env`: Should have `DATABASE_URI` pointing to Neon (NOT localhost:34322)

### 2. Database Connection

**CMS should use Neon:**
```
DATABASE_URI=postgresql://neondb_owner:...@ep-raspy-sun-a2of88b3-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

**NOT local Supabase:**
```
DATABASE_URI=postgresql://postgres:postgres@127.0.0.1:34322/postgres  # WRONG
```

### 3. Auth Configuration (Clerk)

**Check middleware.ts:**
- Development mode should skip Clerk for public routes
- If "Invalid host" error: localhost not configured in Clerk dashboard

**Quick fix for development:**
```typescript
// In apps/www/middleware.ts
if (isDevelopment && isPublicRoute(req)) {
  return NextResponse.next()
}
```

### 4. Turbopack Compatibility

**Known incompatibilities:**
- `esmExternals: "loose"` - NOT supported by Turbopack

**Solution:**
Replace `esmExternals` with `serverExternalPackages`:
```javascript
// next.config.mjs
serverExternalPackages: [
  '@octokit/core',
  '@octokit/rest',
  '@octokit/graphql',
  '@octokit/plugin-paginate-graphql',
  '@octokit/auth-app',
],
```

### 5. CMS Import Map

**If S3 handler error:**
```
PayloadComponent not found in importMap: @payloadcms/storage-s3/client#S3ClientUploadHandler
```

**Fix:** Edit `apps/cms/src/app/(payload)/admin/importMap.js`:
```javascript
import { S3ClientUploadHandler as S3ClientUploadHandler_storage_s3 } from '@payloadcms/storage-s3/client'

export const importMap = {
  // ...existing entries...
  "@payloadcms/storage-s3/client#S3ClientUploadHandler": S3ClientUploadHandler_storage_s3,
}
```

## Quick Fixes Reference

### Clerk "Invalid host" Error
```typescript
// apps/www/middleware.ts
const isDevelopment = process.env.NODE_ENV === 'development'

export default async function middleware(req: NextRequest) {
  if (isDevelopment && isPublicRoute(req)) {
    return NextResponse.next()
  }
  return clerkHandler(req, {} as any)
}
```

### CMS Connection Refused
```bash
# apps/cms/.env - Update to Neon URL
DATABASE_URI=postgresql://neondb_owner:npg_Ts5wy4CoiNbD@ep-raspy-sun-a2of88b3-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

### Turbopack esmExternals Error
Remove from next.config.mjs:
```javascript
experimental: {
  esmExternals: 'loose',  // DELETE THIS
},
```

Add instead:
```javascript
serverExternalPackages: ['@octokit/core', '@octokit/rest', ...],
```

## Playwright Smoke Test

Run quick validation:
```python
# /tmp/quick_test.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Test www
    response = page.goto('http://localhost:3000', timeout=30000)
    print(f"WWW: {response.status}")

    # Test cms
    response = page.goto('http://localhost:3030/admin', timeout=30000)
    print(f"CMS: {response.status}")

    browser.close()
```

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `@clerk/clerk-react: Missing publishableKey` | Clerk env vars not in www/.env | Add CLERK keys to apps/www/.env |
| `ECONNREFUSED 127.0.0.1:34322` | CMS using local Supabase URL | Update DATABASE_URI to Neon |
| `Invalid host` | Clerk doesn't recognize localhost | Skip Clerk for public routes in dev |
| `esmExternals = "loose" is not supported` | Turbopack incompatibility | Use serverExternalPackages instead |
| `PayloadComponent not found in importMap` | Missing S3 handler | Add to importMap.js |

## Prevention Tips

1. **Always check .env files** after cloning or switching branches
2. **Don't commit sensitive values** - use .env.local for secrets
3. **Test both apps** after config changes: `pnpm dev --filter www --filter cms`
4. **Clear caches** if issues persist: `rm -rf apps/www/.next apps/cms/.next`
