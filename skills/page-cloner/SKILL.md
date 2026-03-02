---
name: page-cloner
description: Clone Supabase.com pages into Export Arena with pixel-perfect design fidelity. Use when cloning a page layout, replicating a Supabase page design, building a new solution/landing page from a reference URL, or when user says "clone page", "copy this page", "replicate this layout". Trigger keywords: clone, replicate, page-cloner, copy page, supabase page.
---

# Page Cloner

Clone Supabase.com pages into Export Arena's codebase with pixel-perfect design fidelity, mapping to existing components and sourcing content from NotebookLM.

## When to Use

- User provides a Supabase.com URL to replicate
- Building a new solution or landing page based on a reference design
- Need to extract CSS/design tokens from a live page
- Adapting an external page layout to Export Arena's component library

## Workflow Overview

| Phase | What | Tools |
|-------|------|-------|
| 1. Capture | Screenshot + DOM + CSS extraction | Playwright MCP |
| 2. Map | Match sections to existing components | Codebase search |
| 3. Content | Source from `_docs/` or NotebookLM | File reads, scripts |
| 4. Build | Create data file + page file | Write/Edit |
| 5. Verify | Visual diff + content validation | Playwright, scripts |

---

## Phase 1: Capture Target Page

Use Playwright MCP tools in this order:

### 1a. Navigate and Screenshot

```
browser_navigate -> target URL
browser_take_screenshot -> save to /tmp/page-cloner/{slug}-original.png
```

### 1b. Accessibility Snapshot

```
browser_snapshot -> structured DOM tree (sections, headings, links)
```

### 1c. Extract Design Data

Run `browser_evaluate` with the extraction script from `references/extraction-patterns.md`.

This captures in a single call:
- CSS custom properties (`:root` variables)
- Computed styles per section (background, padding, margin, gap, font-size, font-weight, line-height, color, border-radius)
- Section structure (ordered list with tag names, classes, dimensions)
- Color palette (all unique colors)
- Typography scale (font-size/weight/family combinations)
- Grid/flex layouts per section
- Image/SVG sources and dimensions

Save output to `/tmp/page-cloner/{slug}-extraction.json`.

### 1d. Optional: Content as Markdown

For content-heavy pages, also use Apify `rag-web-browser` or `WebFetch` to get the page text as clean markdown for content reference.

---

## Phase 2: Map to Export Arena Components

For each extracted section, find the closest existing component:

| Supabase Pattern | Export Arena Component | File |
|---|---|---|
| Hero with headline + CTAs | `ProductHeader2` | `components/Sections/ProductHeader2.tsx` |
| Stats/metrics row | `HighlightColumns` | `components/Sections/HighlightColumns.tsx` |
| Feature grid (2-3 cols) | `FeatureGrid` | `components/Solutions/FeatureGrid.tsx` |
| Features with icons + text | `FeaturesSection` | `components/Solutions/FeaturesSection.tsx` |
| Tabbed content panels | `VerticalsTabSection` | `components/Solutions/VerticalsTabSection.tsx` |
| Timed accordion with panels | `TimedAccordionPanels` | `components/Sections/TimedAccordionPanels.tsx` |
| Timed accordion sections | `TimedAccordionSection` | `components/Sections/TimedAccordionSection.tsx` |
| Quote/testimonial | `SingleQuote` | `components/Sections/SingleQuote.tsx` |
| Card carousel/use cases | `UseCasesCardsSection` | `components/Solutions/UseCasesCardsSection.tsx` |
| Enterprise use cases | `EnterpriseUseCases` | `components/Enterprise/UseCases.tsx` |
| CTA with form | `CTAForm` | `components/Enterprise/CTAForm.tsx` |
| CTA section (data-driven) | `CtaSection` | `components/Solutions/CtaSection.tsx` |
| Accordion/FAQ | `Accordion_Shadcn_` | `packages/ui` |
| Logo strip | `AIBuildersLogos` | `components/Solutions/AIBuildersLogos.tsx` |
| Two-column layout | `TwoColumnsSection` | `components/Solutions/TwoColumnsSection.tsx` |
| Results/ROI metrics | `ResultsSection` | `components/Solutions/ResultsSection.tsx` |
| Cards in grid | `Panel` | `components/Panel.tsx` |
| Platform integrations | `PlatformSection` | `components/Solutions/PlatformSection.tsx` |
| Developer experience | `DeveloperExperienceSection` | `components/Solutions/DeveloperExperienceSection.tsx` |
| Code window | `CodeWindow` | `components/CodeWindow.tsx` |

**Rules:**
- ALWAYS try to map to an existing component first
- Only create new components in `components/Solutions/` if no match exists
- Use `SectionContainer` for consistent padding on custom sections
- Wrap everything in `DefaultLayout` with `stickyNavbar={false}`

---

## Phase 3: Source Content

**MANDATORY: Content must trace back to `_docs/` or NotebookLM. Never fabricate.**

### 3a. Check Existing Content

```
Read _docs/content-research/solutions/answers-{slug}.txt
```

### 3b. Generate Missing Content

If content doesn't exist:

```bash
python3 scripts/content-pipeline/notebooklm-solution-page.py {slug}
```

Verify all 12 questions answered (no stubs like "Sifting through pages...").

Re-run failures:
```bash
python3 scripts/content-pipeline/notebooklm-solution-page.py --start N {slug}
```

### 3c. For Ad-Hoc Content

```bash
python3 scripts/content-pipeline/open-notebook.py
python3 scripts/content-pipeline/interact-notebook.py 'Topic' 'Question'
```

### 3d. Map Content to Sections

For each section identified in Phase 2, extract the relevant content from the answers file and adapt it to the component's data structure.

---

## Phase 4: Build the Page

### Option A: Solution Page Pattern (preferred)

Use when the page fits the existing solution page architecture.

**Step 1: Create data file** at `apps/www/data/solutions/{slug}.tsx`

Follow the pattern from existing data files. The export is a function:

```typescript
export default (isMobile?: boolean, onBookCall?: () => void) => ({
  metaTitle: '...',
  metaDescription: '...',
  canonicalPath: '/{category}/{slug}',

  heroSection: { /* HeroSection type */ },
  highlightsSection: { /* highlights array */ },
  resultsSection: { /* ResultsSection props */ },
  featureGridSection: { /* FeatureGrid props */ },
  quote: { /* Quote type */ },
  faq: [ /* { question, answer } */ ],
  ctaSection: { /* REQUIRED - page-specific heading + description */ },
})
```

**Step 2: Create page file** at `apps/www/pages/{category}/{slug}.tsx`

Follow the pattern from `pages/grow/speed-to-market.tsx`:
- Import `pageData` from data file
- Use `NextSeo` + `JsonLd` for SEO
- Wrap in `Layout` with `stickyNavbar={false}`
- Add `ScrollIndicator` + `SecondaryNav`
- Render sections in order, each wrapped in `SectionContainer`
- End with `CTAForm` inside `<div id="cta-form">`

**Step 3: Add to navigation** in `apps/www/data/Solutions.tsx` if needed.

### Option B: Standalone Page

Use when the page needs a fully custom layout.

1. Create page directly in `apps/www/pages/{slug}.tsx`
2. Create new section components in `components/Solutions/`
3. Use `SectionContainer` for padding consistency
4. Wrap in `DefaultLayout` with `stickyNavbar={false}`

### Design Fidelity Rules

- Match spacing: extraction px values -> Tailwind classes (e.g., 48px -> `py-12`, 64px -> `py-16`)
- Match grid: columns + gaps from extraction
- Match typography: sizes, weights, line-heights
- Adapt colors: Supabase colors -> Export Arena CSS variables (`--foreground-default`, `--background-default`, `--brand-default`)
- Dark theme ONLY - no light theme code
- Default background ONLY - no `bg-alternative` alternating zones
- Use Framer Motion for animations matching the original
- Every `ctaSection` MUST have page-specific `heading` and `description`

### Spacing Reference

| Supabase px | Tailwind | Usage |
|-------------|----------|-------|
| 16px | `p-4` / `gap-4` | Inner card padding, small gaps |
| 24px | `p-6` / `gap-6` | Medium padding |
| 32px | `p-8` / `gap-8` | Section inner padding |
| 40px-48px | `py-10` / `py-12` | Section vertical (mobile) |
| 64px | `py-16` | Section vertical (tablet) |
| 96px | `py-24` | Section vertical (desktop) |

---

## Phase 5: Verify

### 5a. Visual Check

```
# Start dev server if not running
pnpm dev --filter www

# Navigate Playwright to the built page
browser_navigate -> http://localhost:3000/{path}
browser_take_screenshot -> /tmp/page-cloner/{slug}-built.png
```

Compare `/tmp/page-cloner/{slug}-built.png` with `/tmp/page-cloner/{slug}-original.png`.

### 5b. Checklist

- [ ] Section order matches original
- [ ] Spacing/padding visually close
- [ ] Typography hierarchy preserved
- [ ] Grid layouts match column count
- [ ] No light theme or `bg-alternative` sections
- [ ] `ctaSection` has page-specific copy
- [ ] All content traces to `_docs/` or NotebookLM

### 5c. Content Validation

```bash
./scripts/validate-content.sh
```

---

## Type Reference

Key types from `data/solutions/solutions.utils.tsx`:

```typescript
interface HeroSection {
  title: string
  h1: JSX.Element
  subheader: JSX.Element[]
  image: JSX.Element | undefined
  ctas: { label: string; href: string; type: 'primary' | 'default' }[]
  footer?: React.ReactNode
  footerPosition?: 'left' | 'right' | 'bottom'
}

interface Quote {
  author: string
  authorTitle?: string
  quote: JSX.Element
  avatar: string
}

interface Feature {
  icon?: IconType | string
  heading: string | JSX.Element
  subheading: string | JSX.Element
  img?: JSX.Element
}

interface FeaturesSection {
  label?: string
  heading: JSX.Element
  subheading?: string
  features: Feature[]
}

interface CTASection {
  label: string
  heading: JSX.Element | string
  subheading: string
}
```

---

## References

- `references/extraction-patterns.md` - Playwright JS snippets for CSS/design extraction
- `scripts/extract-design.py` - Automated extraction script (standalone Playwright)
