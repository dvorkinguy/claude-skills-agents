# Payload CMS Architecture

## Directory Structure

```
apps/cms/
├── src/
│   ├── access/               # Access control functions
│   │   ├── isAdmin.ts
│   │   ├── isAdminOrSelf.ts
│   │   ├── isAnyone.ts
│   │   └── isAuthenticated.ts
│   ├── app/                  # Next.js app router
│   │   └── (payload)/        # Payload admin routes
│   ├── blocks/               # Content blocks
│   │   ├── Banner/
│   │   ├── Code/
│   │   ├── Comparison/
│   │   ├── CTA/
│   │   ├── FAQ/
│   │   ├── Features/
│   │   ├── Hero/
│   │   ├── MediaBlock/
│   │   ├── Pricing/
│   │   ├── Quote/
│   │   ├── RichText/
│   │   ├── Stats/
│   │   ├── Testimonials/
│   │   └── YouTube/
│   ├── collections/          # Data collections
│   │   ├── Authors.ts
│   │   ├── Categories.ts
│   │   ├── Customers/
│   │   ├── Events/
│   │   ├── Media.ts
│   │   ├── Pages/
│   │   ├── Posts/
│   │   ├── Tags.ts
│   │   └── Users.ts
│   ├── fields/               # Reusable fields
│   │   ├── defaultLexical.ts
│   │   ├── link.ts
│   │   ├── linkGroup.ts
│   │   └── slug/
│   ├── hooks/                # Global hooks
│   │   ├── formatSlug.ts
│   │   ├── populatePublishedAt.ts
│   │   └── revalidateRedirects.ts
│   ├── migrations/           # Database migrations
│   ├── providers/            # React providers
│   ├── utilities/            # Utility functions
│   │   ├── constants.ts      # URL constants
│   │   ├── generateMeta.ts
│   │   ├── generatePreviewPath.ts
│   │   └── getURL.ts
│   ├── payload.config.ts     # Main configuration
│   └── payload-types.ts      # Generated types
├── public/                   # Static assets
├── package.json
├── tsconfig.json
└── next.config.mjs
```

## Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   CMS Admin     │     │   Payload API   │     │   PostgreSQL    │
│  localhost:3030 │────▶│   /api/*        │────▶│   (cms schema)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               │ REST API
                               ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   WWW Frontend  │◀────│   Fetch Utils   │     │   ISR Cache     │
│  localhost:3000 │     │  get-cms-*.ts   │────▶│   60s revalidate│
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Component Relationships

### Collections → Blocks

```
Pages Collection
├── Hero Block
├── Features Block
├── Pricing Block
├── Testimonials Block
├── CTA Block
├── Stats Block
├── FAQ Block
├── RichText Block
└── Comparison Block

Posts Collection
├── Banner Block
├── Code Block
├── MediaBlock
├── Quote Block
└── YouTube Block
```

### CMS → Frontend Mapping

| CMS Component | Frontend Component |
|---------------|-------------------|
| `apps/cms/src/blocks/Hero/config.ts` | `apps/www/components/cms/blocks/HeroSection.tsx` |
| `apps/cms/src/blocks/Features/config.ts` | `apps/www/components/cms/blocks/FeaturesSection.tsx` |
| `apps/cms/src/blocks/Pricing/config.ts` | `apps/www/components/cms/blocks/PricingSection.tsx` |
| `apps/cms/src/collections/Pages/` | `apps/www/pages/[[...slug]].tsx` |
| `apps/cms/src/collections/Posts/` | `apps/www/app/blog/[slug]/page.tsx` |

## Configuration Files

### payload.config.ts (Main Config)

```typescript
export default buildConfig({
  admin: {
    user: Users.slug,
    importMap: { baseDir: path.resolve(dirname) },
  },
  collections: [
    Authors, Categories, Customers, Events,
    Media, Pages, Posts, Tags, Users
  ],
  editor: defaultLexical,
  secret: process.env.PAYLOAD_SECRET,
  cors: [getServerSideURL(), WWW_SITE_ORIGIN].filter(Boolean),
  db: postgresAdapter({
    pool: { connectionString: process.env.DATABASE_URI },
    schemaName: 'cms',
    push: process.env.NODE_ENV !== 'production',
  }),
  graphQL: { disable: true },
  telemetry: false,
  plugins: [nestedDocsPlugin, seoPlugin, payloadCloudPlugin, s3Storage],
})
```

### Database Schema

All CMS tables are in the `cms` PostgreSQL schema, separate from the main app tables:

- `cms.pages` - Marketing pages
- `cms.posts` - Blog posts
- `cms.media` - Media files
- `cms.users` - CMS admin users
- `cms.authors` - Blog authors
- `cms.categories` - Content categories
- `cms.tags` - Content tags
- `cms.customers` - Customer testimonials
- `cms.events` - Events/webinars

## Plugin Configuration

### SEO Plugin
```typescript
seoPlugin({
  generateTitle: ({ doc }) => `${doc.title} | Export Arena`,
  generateURL: ({ doc }) => `https://exportarena.com/${doc.slug}`,
})
```

### Nested Docs Plugin
```typescript
nestedDocsPlugin({ collections: ['categories'] })
```

### S3 Storage (Conditional)
```typescript
...(process.env.S3_BUCKET ? [s3Storage({
  collections: { media: { prefix: 'media' } },
  bucket: process.env.S3_BUCKET,
  config: {
    credentials: {
      accessKeyId: process.env.S3_ACCESS_KEY_ID,
      secretAccessKey: process.env.S3_SECRET_ACCESS_KEY,
    },
    region: process.env.S3_REGION,
    endpoint: process.env.S3_ENDPOINT,
  },
})] : [])
```

## Revalidation Flow

```
Page Updated in CMS
        │
        ▼
afterChange Hook Triggered
        │
        ▼
revalidatePath('/' + slug)
        │
        ▼
Next.js ISR Cache Invalidated
        │
        ▼
Next Request → Fresh Content
```

## Preview Flow

```
Click "Preview" in CMS Admin
        │
        ▼
Generate Preview URL
(baseUrl/api-v2/cms/preview?slug=X&secret=Y)
        │
        ▼
WWW Preview Route Handler
        │
        ▼
Validate Secret
        │
        ▼
Enable Draft Mode (draftMode().enable())
        │
        ▼
Redirect to Page (/${slug})
        │
        ▼
Page Fetches Draft Content
```
