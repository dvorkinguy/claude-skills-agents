# Content Blocks Guide

## Marketing Page Blocks

### Hero Block

**Location:** `apps/cms/src/blocks/Hero/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style` | select | No | default, centered, split |
| `headline` | text | Yes | Main headline |
| `subheadline` | text | No | Supporting text |
| `media` | upload | No | Hero image/video |
| `primaryCTA` | group | No | Primary button |
| `secondaryCTA` | group | No | Secondary button |
| `badge` | text | No | Small badge text |

**Frontend:** `apps/www/components/cms/blocks/HeroSection.tsx`

---

### Features Block

**Location:** `apps/cms/src/blocks/Features/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style` | select | No | grid, list, cards |
| `headline` | text | No | Section headline |
| `subheadline` | text | No | Section description |
| `features` | array | Yes | Array of feature items |
| `features.title` | text | Yes | Feature title |
| `features.description` | textarea | No | Feature description |
| `features.icon` | text | No | Icon name |
| `features.media` | upload | No | Feature image |

**Frontend:** `apps/www/components/cms/blocks/FeaturesSection.tsx`

---

### Pricing Block

**Location:** `apps/cms/src/blocks/Pricing/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style` | select | No | cards, table |
| `headline` | text | No | Section headline |
| `plans` | array | Yes | Array of pricing plans |
| `plans.name` | text | Yes | Plan name |
| `plans.price` | number | Yes | Monthly price |
| `plans.description` | textarea | No | Plan description |
| `plans.features` | array | Yes | List of features |
| `plans.highlighted` | checkbox | No | Highlight this plan |
| `plans.ctaText` | text | No | Button text |
| `plans.ctaLink` | text | No | Button URL |

**Frontend:** `apps/www/components/cms/blocks/PricingSection.tsx`

---

### Testimonials Block

**Location:** `apps/cms/src/blocks/Testimonials/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style` | select | No | carousel, grid |
| `headline` | text | No | Section headline |
| `testimonials` | array | Yes | Array of testimonials |
| `testimonials.quote` | textarea | Yes | Testimonial text |
| `testimonials.author` | text | Yes | Author name |
| `testimonials.role` | text | No | Author role |
| `testimonials.company` | text | No | Company name |
| `testimonials.avatar` | upload | No | Author photo |
| `testimonials.logo` | upload | No | Company logo |

**Frontend:** `apps/www/components/cms/blocks/TestimonialsSection.tsx`

---

### CTA Block

**Location:** `apps/cms/src/blocks/CTA/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style` | select | No | default, minimal, gradient |
| `headline` | text | Yes | CTA headline |
| `subheadline` | text | No | Supporting text |
| `primaryCTA` | group | No | Primary button |
| `secondaryCTA` | group | No | Secondary button |
| `backgroundImage` | upload | No | Background image |

**Frontend:** `apps/www/components/cms/blocks/CTASection.tsx`

---

### Stats Block

**Location:** `apps/cms/src/blocks/Stats/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style` | select | No | default, cards |
| `headline` | text | No | Section headline |
| `stats` | array | Yes | Array of stats |
| `stats.value` | text | Yes | Stat value (e.g., "500+") |
| `stats.label` | text | Yes | Stat label |
| `stats.description` | text | No | Additional context |

**Frontend:** `apps/www/components/cms/blocks/StatsSection.tsx`

---

### FAQ Block

**Location:** `apps/cms/src/blocks/FAQ/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style` | select | No | accordion, list |
| `headline` | text | No | Section headline |
| `faqs` | array | Yes | Array of FAQs |
| `faqs.question` | text | Yes | Question text |
| `faqs.answer` | richText | Yes | Answer content |

**Frontend:** `apps/www/components/cms/blocks/FAQSection.tsx`

---

### RichText Block

**Location:** `apps/cms/src/blocks/RichText/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | richText | Yes | Lexical rich text content |
| `columns` | select | No | 1, 2 columns |

**Frontend:** `apps/www/components/cms/blocks/RichTextSection.tsx`

---

### Comparison Block

**Location:** `apps/cms/src/blocks/Comparison/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headline` | text | No | Section headline |
| `competitors` | array | Yes | Competitor columns |
| `competitors.name` | text | Yes | Competitor name |
| `competitors.logo` | upload | No | Competitor logo |
| `features` | array | Yes | Feature rows |
| `features.name` | text | Yes | Feature name |
| `features.exportArena` | checkbox | Yes | Export Arena has it |
| `features.competitors` | array | Yes | Competitor values |

**Frontend:** `apps/www/components/cms/blocks/ComparisonSection.tsx`

---

## Blog Blocks

### Banner Block

**Location:** `apps/cms/src/blocks/Banner/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style` | select | No | info, warning, success |
| `content` | richText | Yes | Banner content |

---

### Code Block

**Location:** `apps/cms/src/blocks/Code/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `language` | select | Yes | Programming language |
| `code` | textarea | Yes | Code content |
| `filename` | text | No | Optional filename |

---

### MediaBlock

**Location:** `apps/cms/src/blocks/MediaBlock/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `media` | upload | Yes | Media file |
| `caption` | text | No | Image caption |
| `size` | select | No | small, medium, large, full |

---

### Quote Block

**Location:** `apps/cms/src/blocks/Quote/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `quote` | textarea | Yes | Quote text |
| `author` | text | No | Quote author |
| `role` | text | No | Author role |

---

### YouTube Block

**Location:** `apps/cms/src/blocks/YouTube/config.ts`

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `videoId` | text | Yes | YouTube video ID |
| `title` | text | No | Video title for accessibility |

---

## Adding a New Block

1. Create block config:
```typescript
// apps/cms/src/blocks/NewBlock/config.ts
import type { Block } from 'payload'

export const NewBlock: Block = {
  slug: 'newBlock',
  interfaceName: 'NewBlockBlock',
  labels: {
    singular: 'New Block',
    plural: 'New Blocks',
  },
  fields: [
    {
      name: 'style',
      type: 'select',
      defaultValue: 'default',
      options: [
        { label: 'Default', value: 'default' },
      ],
    },
    // Add fields
  ],
}
```

2. Register in Pages collection:
```typescript
// apps/cms/src/collections/Pages/index.ts
import { NewBlock } from '../../blocks/NewBlock/config'

// In fields array, add to blocks:
blocks: [Hero, Features, ..., NewBlock]
```

3. Create frontend component:
```tsx
// apps/www/components/cms/blocks/NewBlockSection.tsx
import { NewBlockBlock } from '@/lib/get-cms-pages'

interface Props {
  block: NewBlockBlock
}

export function NewBlockSection({ block }: Props) {
  return (
    <section className="py-16">
      {/* Render block content */}
    </section>
  )
}
```

4. Add to BlockRenderer:
```typescript
// apps/www/components/cms/BlockRenderer.tsx
case 'newBlock':
  return <NewBlockSection key={index} block={block as NewBlockBlock} />
```

5. Add types:
```typescript
// apps/www/lib/get-cms-pages.ts
export interface NewBlockBlock {
  blockType: 'newBlock'
  style?: 'default'
  // Add field types
}

// Add to ContentBlock union
export type ContentBlock = HeroBlock | FeaturesBlock | ... | NewBlockBlock
```
