---
name: payload-cms-expert
description: Expert Payload CMS 3.x toolkit for Export Arena. Use when creating/modifying collections, building blocks, configuring hooks, debugging content sync, testing CMS functionality, or integrating frontend. Triggers: CMS, Payload, collection, block, hook, content, preview, revalidate, pages, posts.
---

# Payload CMS Expert

Expert knowledge for Payload CMS 3.x with PostgreSQL, S3 storage, and Next.js frontend integration.

## Quick Reference

| Item | Value |
|------|-------|
| CMS Location | `apps/cms/` |
| CMS URL | http://localhost:3030 |
| WWW URL | http://localhost:3000 |
| Database | PostgreSQL (schema: `cms`) |
| Config | `apps/cms/src/payload.config.ts` |

### Environment Variables

| Variable | App | Purpose |
|----------|-----|---------|
| `DATABASE_URI` | CMS | PostgreSQL connection string |
| `PAYLOAD_SECRET` | CMS | Authentication secret |
| `PREVIEW_SECRET` | CMS | Preview URL generation |
| `CMS_PREVIEW_SECRET` | WWW | Preview validation (must match) |
| `CMS_SITE_ORIGIN` | WWW | CMS URL for API calls |
| `S3_BUCKET` | CMS | Optional S3 media storage |

## Decision Tree

| Task | Action |
|------|--------|
| **Add new content type** | Create collection in `collections/`, add to config |
| **Add block to pages** | Create block in `blocks/`, register in Pages collection |
| **Debug preview not working** | Run `scripts/check-preview.sh` |
| **Content not syncing** | Run `scripts/diagnose-sync.py` |
| **Test CMS functionality** | Run `npx playwright test e2e/cms/` |
| **Check CMS is running** | Run `scripts/check-connectivity.sh` |
| **Create new block component** | Use `templates/block-component.tsx` |
| **Create new collection** | Use `templates/collection.ts` |

## Collections (9 Total)

| Collection | Slug | Purpose | Location |
|------------|------|---------|----------|
| Pages | `pages` | Marketing pages (home, pricing, features) | `collections/Pages/` |
| Posts | `posts` | Blog articles | `collections/Posts/` |
| Events | `events` | Webinars, tradeshows | `collections/Events/` |
| Customers | `customers` | Customer logos/testimonials | `collections/Customers/` |
| Authors | `authors` | Blog post authors | `collections/Authors.ts` |
| Categories | `categories` | Content categorization | `collections/Categories.ts` |
| Tags | `tags` | Content tagging | `collections/Tags.ts` |
| Media | `media` | Images, files | `collections/Media.ts` |
| Users | `users` | CMS admin users | `collections/Users.ts` |

## Content Blocks (14 Total)

### Marketing Page Blocks (in Pages collection)

| Block | Slug | Styles | Purpose |
|-------|------|--------|---------|
| Hero | `hero` | default, centered, split | Main hero sections |
| Features | `features` | grid, list, cards | Feature grids/lists |
| Pricing | `pricing` | cards, table | Pricing tables |
| Testimonials | `testimonials` | carousel, grid | Customer quotes |
| CTA | `cta` | default, minimal, gradient | Call-to-action sections |
| Stats | `stats` | default, cards | Statistics display |
| FAQ | `faq` | accordion, list | FAQ sections |
| RichText | `richText` | - | Rich text content |
| Comparison | `comparison` | table | Feature comparisons |

### Blog Blocks (in Posts collection)

| Block | Slug | Purpose |
|-------|------|---------|
| Banner | `banner` | Announcement banners |
| Code | `code` | Code snippets |
| MediaBlock | `mediaBlock` | Media embeds |
| Quote | `quote` | Block quotes |
| YouTube | `youtube` | YouTube embeds |

## Common Commands

```bash
# Development
pnpm dev --filter cms              # Start CMS (localhost:3030)
pnpm dev --filter www              # Start WWW (localhost:3000)

# Types & Migrations
cd apps/cms
pnpm payload generate:types        # Generate TypeScript types
pnpm payload migrate:create        # Create new migration
pnpm payload migrate               # Run pending migrations

# Testing
npx playwright test e2e/cms/       # Run CMS tests
```

## Workflow: Add New Block

1. **Create block config** at `apps/cms/src/blocks/NewBlock/config.ts`
   ```typescript
   import type { Block } from 'payload'

   export const NewBlock: Block = {
     slug: 'newBlock',
     interfaceName: 'NewBlockBlock',
     fields: [
       { name: 'title', type: 'text', required: true },
       // Add fields
     ],
   }
   ```

2. **Register in Pages collection** at `apps/cms/src/collections/Pages/index.ts`
   ```typescript
   import { NewBlock } from '../../blocks/NewBlock/config'
   // Add to blocks array:
   blocks: [Hero, Features, ..., NewBlock]
   ```

3. **Create frontend component** at `apps/www/components/cms/blocks/NewBlockSection.tsx`

4. **Add to BlockRenderer** at `apps/www/components/cms/BlockRenderer.tsx`
   ```typescript
   case 'newBlock':
     return <NewBlockSection key={index} block={block} />
   ```

5. **Add TypeScript types** to `apps/www/lib/get-cms-pages.ts`

6. **Test with Playwright**

## Workflow: Add New Collection

1. **Create collection** at `apps/cms/src/collections/NewCollection/index.ts`
   ```typescript
   import type { CollectionConfig } from 'payload'

   export const NewCollection: CollectionConfig = {
     slug: 'newCollection',
     admin: { useAsTitle: 'title', group: 'Content' },
     access: {
       read: () => true,
       create: ({ req }) => !!req.user,
       update: ({ req }) => !!req.user,
       delete: ({ req }) => !!req.user,
     },
     fields: [
       { name: 'title', type: 'text', required: true },
     ],
   }
   ```

2. **Register in payload.config.ts**
   ```typescript
   import { NewCollection } from './collections/NewCollection'
   collections: [..., NewCollection]
   ```

3. **Run migration**
   ```bash
   cd apps/cms && pnpm payload migrate:create && pnpm payload migrate
   ```

## Frontend Integration

### Fetching Pages

```typescript
// apps/www/lib/get-cms-pages.ts
import { CMS_SITE_ORIGIN } from './constants'

export async function getCMSPageBySlug(slug: string, preview = false) {
  const statusFilter = preview ? '' : '&where[_status][equals]=published'
  const url = `${CMS_SITE_ORIGIN}/api/pages?where[slug][equals]=${slug}&depth=2${statusFilter}`
  const res = await fetch(url, { next: { revalidate: 60 } })
  const data = await res.json()
  return data.docs[0] || null
}
```

### Block Rendering

```typescript
// apps/www/components/cms/BlockRenderer.tsx
export function BlockRenderer({ blocks }: { blocks: ContentBlock[] }) {
  return blocks.map((block, index) => {
    switch (block.blockType) {
      case 'hero': return <HeroSection key={index} block={block} />
      case 'features': return <FeaturesSection key={index} block={block} />
      // ... other blocks
    }
  })
}
```

## Access Control Patterns

```typescript
// Public read, authenticated write
access: {
  read: () => true,
  create: ({ req }) => !!req.user,
  update: ({ req }) => !!req.user,
  delete: ({ req }) => !!req.user,
}

// Admin only
access: {
  read: ({ req }) => req.user?.role === 'admin',
  create: ({ req }) => req.user?.role === 'admin',
  update: ({ req }) => req.user?.role === 'admin',
  delete: ({ req }) => req.user?.role === 'admin',
}

// Published only for public, all for admin
access: {
  read: ({ req }) => {
    if (req.user?.role === 'admin') return true
    return { _status: { equals: 'published' } }
  },
}
```

## Preview Configuration

### CMS Side (generates preview URL)
```typescript
// apps/cms/src/collections/Pages/index.ts
admin: {
  preview: (data) => {
    const baseUrl = WWW_SITE_ORIGIN || 'http://localhost:3000'
    const slug = data?.slug === 'home' ? '' : data?.slug
    return `${baseUrl}/api-v2/cms/preview?slug=${slug}&collection=pages&secret=${PREVIEW_SECRET}`
  },
}
```

### WWW Side (handles preview)
```typescript
// apps/www/app/api-v2/cms/preview/route.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const secret = searchParams.get('secret')
  if (secret !== process.env.CMS_PREVIEW_SECRET) {
    return new Response('Invalid token', { status: 401 })
  }
  const draft = await draftMode()
  draft.enable()
  redirect(`/${slug}`)
}
```

## References

| File | Content |
|------|---------|
| `references/architecture.md` | Full CMS architecture overview |
| `references/blocks-guide.md` | All blocks with field schemas |
| `references/collections-guide.md` | Collection patterns and hooks |
| `references/frontend-integration.md` | WWW integration patterns |
| `references/environment-guide.md` | Environment setup |
| `references/troubleshooting.md` | Common issues and fixes |

## Templates

| Template | Purpose |
|----------|---------|
| `templates/collection.ts` | New collection boilerplate |
| `templates/block.ts` | New block config boilerplate |
| `templates/hook.ts` | Collection hook template |
| `templates/access.ts` | Access control patterns |
| `templates/block-component.tsx` | Frontend block component |
| `templates/e2e-block-test.ts` | Playwright test template |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/check-connectivity.sh` | Test CMS API health |
| `scripts/check-preview.sh` | Verify preview configuration |
| `scripts/diagnose-sync.py` | Diagnose content sync issues |
| `scripts/validate-blocks.py` | Validate block configs |
| `scripts/list-pages.sh` | List all CMS pages |

## Key Files

| File | Purpose |
|------|---------|
| `apps/cms/src/payload.config.ts` | Main CMS configuration |
| `apps/cms/src/collections/Pages/index.ts` | Pages collection with blocks |
| `apps/cms/src/utilities/constants.ts` | URL constants |
| `apps/www/lib/get-cms-pages.ts` | Frontend CMS client |
| `apps/www/components/cms/BlockRenderer.tsx` | Block rendering |
| `apps/www/app/api-v2/cms/preview/route.ts` | Preview handler |
