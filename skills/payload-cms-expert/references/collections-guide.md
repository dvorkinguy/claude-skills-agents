# Collections Guide

## Overview

Export Arena CMS has 9 collections organized into content and system categories.

## Content Collections

### Pages

**Location:** `apps/cms/src/collections/Pages/index.ts`

**Purpose:** Marketing pages (homepage, pricing, features, solutions)

**Key Features:**
- Block-based content (9 block types)
- Draft/publish workflow
- SEO fields via plugin
- Preview functionality
- Revalidation on change

**Template Options:**
- `home` - Homepage
- `landing` - Landing pages
- `feature` - Feature pages
- `solution` - Solution pages
- `legal` - Legal pages
- `about` - About pages

**Fields:**
```typescript
fields: [
  { name: 'title', type: 'text', required: true },
  slugField(),
  { name: 'template', type: 'select', options: [...] },
  {
    name: 'content',
    type: 'blocks',
    blocks: [Hero, Features, Pricing, ...],
  },
  { name: 'showHeader', type: 'checkbox', defaultValue: true },
  { name: 'showFooter', type: 'checkbox', defaultValue: true },
  { name: 'customCSS', type: 'textarea' },
]
```

**Hooks:**
- `afterChange` → `revalidatePage` (invalidates ISR cache)
- `afterDelete` → `revalidatePage`

---

### Posts

**Location:** `apps/cms/src/collections/Posts/index.ts`

**Purpose:** Blog articles

**Key Features:**
- Rich text content with Lexical editor
- Author relationship
- Categories and tags
- Featured image
- Draft/publish workflow

**Fields:**
```typescript
fields: [
  { name: 'title', type: 'text', required: true },
  slugField(),
  { name: 'author', type: 'relationship', relationTo: 'authors' },
  { name: 'categories', type: 'relationship', relationTo: 'categories', hasMany: true },
  { name: 'tags', type: 'relationship', relationTo: 'tags', hasMany: true },
  { name: 'featuredImage', type: 'upload', relationTo: 'media' },
  { name: 'excerpt', type: 'textarea' },
  { name: 'content', type: 'richText' },
  publishedAtField(),
]
```

**Hooks:**
- `beforeChange` → `populateAuthors` (auto-fill author)
- `afterChange` → `revalidatePost`

---

### Events

**Location:** `apps/cms/src/collections/Events/index.ts`

**Purpose:** Webinars, tradeshows, conferences

**Fields:**
```typescript
fields: [
  { name: 'title', type: 'text', required: true },
  slugField(),
  { name: 'eventType', type: 'select', options: ['webinar', 'tradeshow', 'conference'] },
  { name: 'date', type: 'date', required: true },
  { name: 'endDate', type: 'date' },
  { name: 'location', type: 'text' },
  { name: 'description', type: 'richText' },
  { name: 'registrationUrl', type: 'text' },
  { name: 'featuredImage', type: 'upload', relationTo: 'media' },
]
```

---

### Customers

**Location:** `apps/cms/src/collections/Customers/index.ts`

**Purpose:** Customer logos and testimonials for social proof

**Fields:**
```typescript
fields: [
  { name: 'name', type: 'text', required: true },
  { name: 'logo', type: 'upload', relationTo: 'media' },
  { name: 'website', type: 'text' },
  { name: 'industry', type: 'select', options: [...] },
  { name: 'testimonial', type: 'textarea' },
  { name: 'contactName', type: 'text' },
  { name: 'contactRole', type: 'text' },
  { name: 'featured', type: 'checkbox' },
]
```

---

## Taxonomy Collections

### Authors

**Location:** `apps/cms/src/collections/Authors.ts`

**Purpose:** Blog post authors

**Fields:**
```typescript
fields: [
  { name: 'name', type: 'text', required: true },
  slugField('name'),
  { name: 'bio', type: 'textarea' },
  { name: 'avatar', type: 'upload', relationTo: 'media' },
  { name: 'role', type: 'text' },
  { name: 'social', type: 'group', fields: [
    { name: 'twitter', type: 'text' },
    { name: 'linkedin', type: 'text' },
  ]},
]
```

---

### Categories

**Location:** `apps/cms/src/collections/Categories.ts`

**Purpose:** Content categorization (supports nesting via nestedDocsPlugin)

**Fields:**
```typescript
fields: [
  { name: 'title', type: 'text', required: true },
  slugField('title'),
  { name: 'description', type: 'textarea' },
  // parent field added by nestedDocsPlugin
]
```

---

### Tags

**Location:** `apps/cms/src/collections/Tags.ts`

**Purpose:** Content tagging (flat structure)

**Fields:**
```typescript
fields: [
  { name: 'title', type: 'text', required: true },
  slugField('title'),
]
```

---

## System Collections

### Media

**Location:** `apps/cms/src/collections/Media.ts`

**Purpose:** Image and file uploads

**Key Features:**
- Image optimization (WebP, AVIF)
- Multiple sizes generated
- Optional S3 storage
- Alt text for accessibility

**Fields:**
```typescript
fields: [
  { name: 'alt', type: 'text', required: true },
  { name: 'caption', type: 'text' },
]
```

**Upload Config:**
```typescript
upload: {
  staticDir: '../media',
  mimeTypes: ['image/*', 'application/pdf'],
  imageSizes: [
    { name: 'thumbnail', width: 400, height: 300 },
    { name: 'card', width: 768, height: 512 },
    { name: 'large', width: 1920, height: 1080 },
  ],
}
```

---

### Users

**Location:** `apps/cms/src/collections/Users.ts`

**Purpose:** CMS admin users (separate from app users)

**Key Features:**
- Email/password authentication
- Role-based access (admin, editor)
- Password hashing via Payload

**Fields:**
```typescript
fields: [
  { name: 'name', type: 'text', required: true },
  { name: 'role', type: 'select', options: ['admin', 'editor'] },
]
```

**Admin Config:**
```typescript
admin: {
  useAsTitle: 'email',
}
auth: true, // Enable authentication
```

---

## Access Control Patterns

### Public Read, Authenticated Write
```typescript
access: {
  read: () => true,
  create: ({ req }) => !!req.user,
  update: ({ req }) => !!req.user,
  delete: ({ req }) => !!req.user,
}
```

### Admin Only
```typescript
access: {
  read: ({ req }) => req.user?.role === 'admin',
  create: ({ req }) => req.user?.role === 'admin',
  update: ({ req }) => req.user?.role === 'admin',
  delete: ({ req }) => req.user?.role === 'admin',
}
```

### Published Only for Public
```typescript
access: {
  read: ({ req }) => {
    if (req.user) return true // Authenticated see all
    return { _status: { equals: 'published' } }
  },
}
```

### Owner-Based Access
```typescript
access: {
  update: ({ req, id }) => {
    if (req.user?.role === 'admin') return true
    return { createdBy: { equals: req.user?.id } }
  },
}
```

---

## Hook Patterns

### Revalidation Hook
```typescript
// apps/cms/src/collections/Pages/hooks/revalidatePage.ts
import { revalidatePath, revalidateTag } from 'next/cache'

export const revalidatePage: CollectionAfterChangeHook<Page> = async ({
  doc,
  previousDoc,
  req,
}) => {
  if (doc._status === 'published') {
    const path = doc.slug === 'home' ? '/' : `/${doc.slug}`
    revalidatePath(path)
    revalidateTag('pages-sitemap')
  }
  return doc
}
```

### Populate Field Hook
```typescript
// Auto-populate author from current user
hooks: {
  beforeChange: [
    ({ data, req, operation }) => {
      if (operation === 'create' && req.user) {
        data.author = req.user.id
      }
      return data
    },
  ],
}
```

### Slug Generation Hook
```typescript
// Auto-generate slug from title
hooks: {
  beforeValidate: [
    ({ value, siblingData }) => {
      if (!value && siblingData?.title) {
        return formatSlug(siblingData.title)
      }
      return value
    },
  ],
}
```

---

## Creating a New Collection

1. **Create collection file:**
```typescript
// apps/cms/src/collections/NewCollection/index.ts
import type { CollectionConfig } from 'payload'
import { slugField } from '../../fields/slug'

export const NewCollection: CollectionConfig = {
  slug: 'newCollection',
  admin: {
    useAsTitle: 'title',
    group: 'Content',
  },
  access: {
    read: () => true,
    create: ({ req }) => !!req.user,
    update: ({ req }) => !!req.user,
    delete: ({ req }) => !!req.user,
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    ...slugField(),
  ],
}
```

2. **Register in config:**
```typescript
// apps/cms/src/payload.config.ts
import { NewCollection } from './collections/NewCollection'

collections: [..., NewCollection]
```

3. **Run migration:**
```bash
cd apps/cms
pnpm payload migrate:create
pnpm payload migrate
```

4. **Generate types:**
```bash
pnpm payload generate:types
```
