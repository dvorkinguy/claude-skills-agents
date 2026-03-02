# CMS Troubleshooting Guide

## Preview Not Working

### Symptoms
- Clicking "Preview" in CMS shows 401 error
- Preview page shows wrong/old content
- Preview redirects to wrong URL

### Diagnosis

1. **Check preview secrets match:**
   ```bash
   # CMS .env
   grep PREVIEW_SECRET apps/cms/.env

   # WWW .env
   grep CMS_PREVIEW_SECRET apps/www/.env.local
   ```
   These values MUST match.

2. **Check preview URL generation:**
   ```typescript
   // apps/cms/src/collections/Pages/index.ts
   admin: {
     preview: (data) => {
       console.log('Preview URL:', `${baseUrl}/api-v2/cms/preview?slug=${data.slug}`)
       // ...
     }
   }
   ```

3. **Check preview route handler:**
   ```typescript
   // apps/www/app/api-v2/cms/preview/route.ts
   // Verify it redirects to correct path:
   redirect(`/${slug}`)  // NOT `/blog/${slug}` for pages
   ```

### Solutions

**Secret mismatch:**
```bash
# Set same value in both apps
# apps/cms/.env
PREVIEW_SECRET=your-secret-here

# apps/www/.env.local
CMS_PREVIEW_SECRET=your-secret-here
```

**Wrong redirect path:**
```typescript
// apps/www/app/api-v2/cms/preview/route.ts
const collection = searchParams.get('collection')
const slug = searchParams.get('slug')

// Route based on collection
if (collection === 'posts') {
  redirect(`/blog/${slug}`)
} else {
  redirect(slug ? `/${slug}` : '/')
}
```

---

## Content Not Syncing

### Symptoms
- Changes in CMS don't appear on frontend
- Old content still showing after publish
- ISR not revalidating

### Diagnosis

1. **Check CMS is accessible:**
   ```bash
   curl http://localhost:3030/api/pages
   ```

2. **Check revalidation hook:**
   ```typescript
   // apps/cms/src/collections/Pages/hooks/revalidatePage.ts
   // Add logging:
   console.log('Revalidating path:', path)
   ```

3. **Check ISR cache:**
   ```bash
   # Delete .next cache
   rm -rf apps/www/.next/cache
   ```

### Solutions

**Revalidation not triggering:**
```typescript
// Ensure hook is registered in collection
hooks: {
  afterChange: [revalidatePage],
  afterDelete: [revalidatePage],
}
```

**Manual revalidation:**
```typescript
// Add API route for manual revalidation
// apps/www/app/api/revalidate/route.ts
export async function POST(request: Request) {
  const { path } = await request.json()
  revalidatePath(path)
  return Response.json({ revalidated: true })
}
```

**Force fresh fetch:**
```typescript
// Disable cache temporarily for debugging
const res = await fetch(url, { cache: 'no-store' })
```

---

## CMS Not Starting

### Symptoms
- `pnpm dev --filter cms` fails
- Port 3030 already in use
- Database connection error

### Diagnosis

1. **Check port availability:**
   ```bash
   lsof -i :3030
   ```

2. **Check database connection:**
   ```bash
   # Test PostgreSQL connection
   psql $DATABASE_URI -c "SELECT 1"
   ```

3. **Check environment variables:**
   ```bash
   cat apps/cms/.env
   ```

### Solutions

**Port in use:**
```bash
# Kill process on port 3030
kill $(lsof -t -i:3030)
```

**Database connection failed:**
```bash
# Verify DATABASE_URI format
# postgresql://user:password@host:port/database?sslmode=require

# Check Neon dashboard for connection status
```

**Missing env vars:**
```bash
# Required vars
DATABASE_URI=postgresql://...
PAYLOAD_SECRET=any-random-string
```

---

## Block Not Rendering

### Symptoms
- Block shows in CMS but not on frontend
- Console error about unknown block type
- Empty section on page

### Diagnosis

1. **Check block is registered in collection:**
   ```typescript
   // apps/cms/src/collections/Pages/index.ts
   blocks: [Hero, Features, ...] // Is your block here?
   ```

2. **Check BlockRenderer handles the type:**
   ```typescript
   // apps/www/components/cms/BlockRenderer.tsx
   case 'yourBlockType': // Does this case exist?
   ```

3. **Check API returns block data:**
   ```bash
   curl "http://localhost:3030/api/pages?where[slug][equals]=home" | jq '.docs[0].content'
   ```

### Solutions

**Add missing case to BlockRenderer:**
```typescript
switch (block.blockType) {
  case 'newBlock':
    return <NewBlockSection key={index} block={block} />
  default:
    console.warn('Unknown block type:', block.blockType)
    return null
}
```

**Add TypeScript types:**
```typescript
// apps/www/lib/get-cms-pages.ts
export interface NewBlockBlock {
  blockType: 'newBlock'
  // fields...
}

export type ContentBlock = ... | NewBlockBlock
```

---

## Media URLs Broken

### Symptoms
- Images show as broken
- 404 for media files
- Wrong domain in image URLs

### Diagnosis

1. **Check media URL format:**
   ```bash
   curl "http://localhost:3030/api/media" | jq '.docs[0].url'
   ```

2. **Check S3 configuration (if using):**
   ```bash
   grep S3_ apps/cms/.env
   ```

3. **Check getMediaUrl utility:**
   ```typescript
   // apps/www/lib/get-cms-pages.ts
   export function getMediaUrl(media: CMSMedia, size?: string) {
     // Check this function
   }
   ```

### Solutions

**Fix relative URLs:**
```typescript
export function getMediaUrl(media: CMSMedia, size?: string) {
  if (!media?.url) return ''

  // Handle relative URLs
  if (media.url.startsWith('/')) {
    return `${CMS_SITE_ORIGIN}${media.url}`
  }

  return media.url
}
```

**S3 not configured:**
- Media stored locally at `apps/cms/media/`
- URLs will be relative: `/media/filename.jpg`
- Must prepend CMS origin for external access

---

## Migration Errors

### Symptoms
- `payload migrate` fails
- Schema mismatch errors
- Duplicate column errors

### Diagnosis

1. **Check migration files:**
   ```bash
   ls apps/cms/src/migrations/
   ```

2. **Check payload_migrations table:**
   ```sql
   SELECT * FROM cms.payload_migrations;
   ```

### Solutions

**Reset migrations (development only):**
```bash
# Delete migration records
psql $DATABASE_URI -c "DELETE FROM cms.payload_migrations"

# Drop and recreate tables
cd apps/cms
pnpm payload migrate:fresh
```

**Fix schema mismatch:**
```bash
# Generate new migration
pnpm payload migrate:create

# Review generated SQL
cat src/migrations/TIMESTAMP.ts

# Run migration
pnpm payload migrate
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `CORS error` | WWW domain not in cors config | Add to `payload.config.ts` cors array |
| `401 Unauthorized` | Invalid preview secret | Sync PREVIEW_SECRET vars |
| `404 Not Found` | Wrong API endpoint | Check `/api/` prefix |
| `500 Internal Server Error` | Database or config error | Check CMS logs |
| `ECONNREFUSED` | CMS not running | Start with `pnpm dev --filter cms` |
