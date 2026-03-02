# Frontend Integration Guide

## Overview

The `apps/www` Next.js application fetches content from Payload CMS via REST API.

## API Client

### Location
`apps/www/lib/get-cms-pages.ts`

### Page Fetching

```typescript
import { CMS_SITE_ORIGIN } from './constants'

const PAYLOAD_URL = CMS_SITE_ORIGIN || 'http://localhost:3030'

export async function getCMSPageBySlug(
  slug: string,
  preview = false
): Promise<CMSPage | null> {
  const statusFilter = preview ? '' : '&where[_status][equals]=published'
  const url = `${PAYLOAD_URL}/api/pages?where[slug][equals]=${slug}&depth=2${statusFilter}`

  const res = await fetch(url, {
    next: { revalidate: 60 }, // ISR: 60 seconds
  })

  if (!res.ok) return null

  const data = await res.json()
  return data.docs[0] || null
}
```

### Get All Pages

```typescript
export async function getAllCMSPages(): Promise<CMSPage[]> {
  const url = `${PAYLOAD_URL}/api/pages?where[_status][equals]=published&limit=100&depth=2`

  const res = await fetch(url, {
    next: { revalidate: 60 },
  })

  const data = await res.json()
  return data.docs
}
```

### Get Page Slugs (for static generation)

```typescript
export async function getAllCMSPageSlugs(): Promise<string[]> {
  const url = `${PAYLOAD_URL}/api/pages?where[_status][equals]=published&limit=100`

  const res = await fetch(url, {
    next: { revalidate: 60 },
  })

  const data = await res.json()
  return data.docs.map((page: CMSPage) => page.slug)
}
```

### Check Page Exists

```typescript
export async function cmsPageExists(slug: string): Promise<boolean> {
  const url = `${PAYLOAD_URL}/api/pages?where[slug][equals]=${slug}&where[_status][equals]=published&limit=1`

  const res = await fetch(url)
  const data = await res.json()
  return data.docs.length > 0
}
```

---

## Type Definitions

### Page Types

```typescript
export interface CMSPage {
  id: string
  title: string
  slug: string
  template: 'home' | 'landing' | 'feature' | 'solution' | 'legal' | 'about'
  content: ContentBlock[]
  showHeader: boolean
  showFooter: boolean
  customCSS?: string
  meta?: {
    title?: string
    description?: string
    image?: CMSMedia
  }
  _status: 'draft' | 'published'
  createdAt: string
  updatedAt: string
}
```

### Block Types

```typescript
export type ContentBlock =
  | HeroBlock
  | FeaturesBlock
  | PricingBlock
  | TestimonialsBlock
  | CTABlock
  | StatsBlock
  | FAQBlock
  | RichTextBlock
  | ComparisonBlock

export interface HeroBlock {
  blockType: 'hero'
  style?: 'default' | 'centered' | 'split'
  headline: string
  subheadline?: string
  media?: CMSMedia
  primaryCTA?: CTALink
  secondaryCTA?: CTALink
  badge?: string
}

export interface FeaturesBlock {
  blockType: 'features'
  style?: 'grid' | 'list' | 'cards'
  headline?: string
  subheadline?: string
  features: {
    title: string
    description?: string
    icon?: string
    media?: CMSMedia
  }[]
}

// ... other block types
```

### Media Type

```typescript
export interface CMSMedia {
  id: string
  url: string
  alt: string
  width?: number
  height?: number
  sizes?: {
    thumbnail?: { url: string; width: number; height: number }
    card?: { url: string; width: number; height: number }
    large?: { url: string; width: number; height: number }
  }
}
```

---

## Block Renderer

### Location
`apps/www/components/cms/BlockRenderer.tsx`

### Implementation

```typescript
import { ContentBlock } from '@/lib/get-cms-pages'
import { HeroSection } from './blocks/HeroSection'
import { FeaturesSection } from './blocks/FeaturesSection'
import { PricingSection } from './blocks/PricingSection'
import { TestimonialsSection } from './blocks/TestimonialsSection'
import { CTASection } from './blocks/CTASection'
import { StatsSection } from './blocks/StatsSection'
import { FAQSection } from './blocks/FAQSection'
import { RichTextSection } from './blocks/RichTextSection'
import { ComparisonSection } from './blocks/ComparisonSection'

interface Props {
  blocks: ContentBlock[]
}

export function BlockRenderer({ blocks }: Props) {
  if (!blocks || blocks.length === 0) return null

  return (
    <>
      {blocks.map((block, index) => {
        switch (block.blockType) {
          case 'hero':
            return <HeroSection key={index} block={block} />
          case 'features':
            return <FeaturesSection key={index} block={block} />
          case 'pricing':
            return <PricingSection key={index} block={block} />
          case 'testimonials':
            return <TestimonialsSection key={index} block={block} />
          case 'cta':
            return <CTASection key={index} block={block} />
          case 'stats':
            return <StatsSection key={index} block={block} />
          case 'faq':
            return <FAQSection key={index} block={block} />
          case 'richText':
            return <RichTextSection key={index} block={block} />
          case 'comparison':
            return <ComparisonSection key={index} block={block} />
          default:
            console.warn('Unknown block type:', (block as any).blockType)
            return null
        }
      })}
    </>
  )
}
```

---

## Page Routes

### Catch-All Route (Pages Router)

**Location:** `apps/www/pages/[[...slug]].tsx`

```typescript
import { GetStaticPaths, GetStaticProps } from 'next'
import { getCMSPageBySlug, getAllCMSPageSlugs, CMSPage } from '@/lib/get-cms-pages'
import { BlockRenderer } from '@/components/cms/BlockRenderer'

interface Props {
  page: CMSPage
}

export default function CMSPage({ page }: Props) {
  if (!page) return <div>Loading...</div>

  return (
    <>
      {page.showHeader && <Header />}
      <main>
        <BlockRenderer blocks={page.content} />
      </main>
      {page.showFooter && <Footer />}
      {page.customCSS && <style>{page.customCSS}</style>}
    </>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  const slugs = await getAllCMSPageSlugs()

  const paths = slugs.map((slug) => ({
    params: { slug: slug === 'home' ? [] : [slug] },
  }))

  return { paths, fallback: 'blocking' }
}

export const getStaticProps: GetStaticProps<Props> = async ({ params, preview }) => {
  const slugArray = params?.slug as string[] | undefined
  const slug = slugArray?.length ? slugArray.join('/') : 'home'

  const page = await getCMSPageBySlug(slug, preview)

  if (!page) {
    return { notFound: true }
  }

  return {
    props: { page },
    revalidate: 60, // ISR: revalidate every 60 seconds
  }
}
```

---

## Media Handling

### Get Media URL Utility

```typescript
export function getMediaUrl(media: CMSMedia | undefined, size?: keyof CMSMedia['sizes']): string {
  if (!media) return ''

  // Use specific size if available
  if (size && media.sizes?.[size]?.url) {
    return normalizeUrl(media.sizes[size].url)
  }

  return normalizeUrl(media.url)
}

function normalizeUrl(url: string): string {
  // Handle relative URLs
  if (url.startsWith('/')) {
    return `${CMS_SITE_ORIGIN}${url}`
  }
  return url
}
```

### Usage in Components

```tsx
import { getMediaUrl } from '@/lib/get-cms-pages'

function HeroSection({ block }: { block: HeroBlock }) {
  const imageUrl = getMediaUrl(block.media, 'large')

  return (
    <section>
      {imageUrl && (
        <Image
          src={imageUrl}
          alt={block.media?.alt || ''}
          width={1920}
          height={1080}
        />
      )}
    </section>
  )
}
```

---

## Preview Mode

### Preview Route Handler

**Location:** `apps/www/app/api-v2/cms/preview/route.ts`

```typescript
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(request: Request) {
  const draft = await draftMode()
  const { searchParams } = new URL(request.url)

  const secret = searchParams.get('secret')
  const slug = searchParams.get('slug') || ''
  const collection = searchParams.get('collection') || 'pages'

  // Validate secret
  const expectedSecret = process.env.CMS_PREVIEW_SECRET
  if (secret !== expectedSecret) {
    return new Response('Invalid token', { status: 401 })
  }

  // Enable draft mode
  draft.enable()

  // Redirect based on collection
  if (collection === 'posts') {
    redirect(`/blog/${slug}`)
  } else {
    redirect(slug ? `/${slug}` : '/')
  }
}
```

### Disable Draft Mode

**Location:** `apps/www/app/api-v2/cms/disable-draft/route.ts`

```typescript
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(request: Request) {
  const draft = await draftMode()
  draft.disable()

  const { searchParams } = new URL(request.url)
  const slug = searchParams.get('slug') || ''

  redirect(slug ? `/${slug}` : '/')
}
```

---

## ISR Revalidation

### On-Demand Revalidation

CMS triggers revalidation via hooks when content changes:

```typescript
// apps/cms/src/collections/Pages/hooks/revalidatePage.ts
import { revalidatePath, revalidateTag } from 'next/cache'

export const revalidatePage = async ({ doc }) => {
  if (doc._status === 'published') {
    const path = doc.slug === 'home' ? '/' : `/${doc.slug}`

    // Revalidate the specific page
    revalidatePath(path)

    // Revalidate sitemap
    revalidateTag('pages-sitemap')
  }
}
```

### Manual Revalidation API

```typescript
// apps/www/app/api/revalidate/route.ts
import { revalidatePath } from 'next/cache'

export async function POST(request: Request) {
  const { path, secret } = await request.json()

  if (secret !== process.env.REVALIDATE_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 })
  }

  revalidatePath(path)

  return Response.json({ revalidated: true, path })
}
```

---

## Constants

**Location:** `apps/www/lib/constants.ts`

```typescript
export const CMS_SITE_ORIGIN =
  process.env.NEXT_PUBLIC_VERCEL_ENV === 'production'
    ? process.env.CMS_SITE_ORIGIN || 'https://cms.exportarena.com'
    : process.env.NEXT_PUBLIC_VERCEL_BRANCH_URL
      ? `https://${process.env.NEXT_PUBLIC_VERCEL_BRANCH_URL.replace('zone-www-dot-com-git-', 'cms-git-')}`
      : 'http://localhost:3030'
```
