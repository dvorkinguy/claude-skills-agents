/**
 * Frontend Block Component Template
 *
 * Usage:
 * 1. Copy to apps/www/components/cms/blocks/{{BlockName}}Section.tsx
 * 2. Replace {{BlockName}}, {{blockName}} placeholders
 * 3. Add to BlockRenderer.tsx switch statement
 * 4. Add type to get-cms-pages.ts
 */

import { cn } from '@/lib/utils'
import { getMediaUrl } from '@/lib/get-cms-pages'
import type { {{BlockName}}Block } from '@/lib/get-cms-pages'

interface Props {
  block: {{BlockName}}Block
}

export function {{BlockName}}Section({ block }: Props) {
  const { style = 'default', headline, subheadline } = block

  return (
    <section
      className={cn(
        'relative py-16 lg:py-24',
        style === 'default' && 'bg-background',
        style === 'alternate' && 'bg-muted'
      )}
    >
      <div className="container mx-auto px-4">
        {/* Header */}
        {(headline || subheadline) && (
          <div className="mx-auto max-w-3xl text-center mb-12">
            {headline && (
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
                {headline}
              </h2>
            )}
            {subheadline && (
              <p className="mt-4 text-lg text-muted-foreground">
                {subheadline}
              </p>
            )}
          </div>
        )}

        {/* Content */}
        <div className="mt-8">
          {/* Add block-specific content here */}

          {/* Example: Items grid */}
          {/* {block.items && block.items.length > 0 && (
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {block.items.map((item, index) => (
                <div key={index} className="rounded-lg border p-6">
                  {item.media && (
                    <img
                      src={getMediaUrl(item.media, 'card')}
                      alt={item.media.alt || ''}
                      className="mb-4 rounded"
                    />
                  )}
                  <h3 className="text-xl font-semibold">{item.title}</h3>
                  {item.description && (
                    <p className="mt-2 text-muted-foreground">
                      {item.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )} */}

          {/* Example: CTA buttons */}
          {/* {(block.primaryCTA || block.secondaryCTA) && (
            <div className="mt-8 flex flex-wrap gap-4 justify-center">
              {block.primaryCTA && (
                <a
                  href={block.primaryCTA.url}
                  className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90"
                >
                  {block.primaryCTA.text}
                </a>
              )}
              {block.secondaryCTA && (
                <a
                  href={block.secondaryCTA.url}
                  className="inline-flex items-center justify-center rounded-md border border-input bg-background px-6 py-3 text-sm font-medium hover:bg-accent"
                >
                  {block.secondaryCTA.text}
                </a>
              )}
            </div>
          )} */}
        </div>
      </div>
    </section>
  )
}

// ============================================
// Type Definition (add to get-cms-pages.ts)
// ============================================

/*
export interface {{BlockName}}Block {
  blockType: '{{blockName}}'
  style?: 'default' | 'alternate'
  headline?: string
  subheadline?: string
  // Add more fields as needed:
  // media?: CMSMedia
  // primaryCTA?: { text: string; url: string }
  // items?: Array<{
  //   title: string
  //   description?: string
  //   icon?: string
  //   media?: CMSMedia
  // }>
}

// Add to ContentBlock union:
export type ContentBlock =
  | HeroBlock
  | FeaturesBlock
  // ... other blocks
  | {{BlockName}}Block
*/

// ============================================
// BlockRenderer Case (add to BlockRenderer.tsx)
// ============================================

/*
case '{{blockName}}':
  return <{{BlockName}}Section key={index} block={block as {{BlockName}}Block} />
*/
