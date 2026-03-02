---
name: ai-worker-creator
description: Autonomously create/edit AI Worker pages with content, images, workflows, and SEO. Use when creating or enhancing AI Worker pages, generating images via Gemini, extracting content from NotebookLM, or building n8n workflow diagrams. Triggers on: ai worker, create worker page, generate worker content, worker image, workflow diagram.
---

# AI Worker Creator

Autonomous skill for creating and editing Export Arena AI Worker pages with full content pipeline: NotebookLM content extraction, Gemini image generation, n8n workflow diagrams, and SEO optimization.

## When to Use

- Creating new AI Worker pages
- Enhancing existing AI Worker content (executiveSummary, keyMetric, valueOutcomes)
- Generating banner images for AI Workers
- Creating n8n workflow diagrams for visualization
- SEO optimization for AI Worker pages

## Quick Reference

| Task | Command |
|------|---------|
| Single worker | `python3 scripts/content-pipeline/ai-worker-orchestrator.py --worker hs-classifier` |
| Multiple workers | `python3 scripts/content-pipeline/ai-worker-orchestrator.py --workers hs-classifier,rfq-responder` |
| All workers | `python3 scripts/content-pipeline/ai-worker-orchestrator.py --all --batch-size 10` |
| Image only | `python3 scripts/content-pipeline/ai-worker-image-generator.py --worker hs-classifier` |

## Pipeline Phases

### Phase 1: Content Extraction (NotebookLM)

**Chrome Profile:** `~/.playwright-chrome-profile`
**URL:** `https://notebooklm.google.com/notebook/443e60ee-3661-4c82-86a6-b186684fb585`

**Prompt Template:**
```
Generate content for AI Worker: {worker.name}

Sections needed:
1. Executive Summary (2-3 sentences, value proposition)
2. Problem Statement (pain point this solves)
3. Solution Description (how it works)
4. Key Metric (quantified value: "Reduces X by Y%")
5. Value Outcomes (4 bullet points for sidebar)
6. SEO Title (50-60 chars with keyword)
7. SEO Description (150-160 chars)

Context: {worker.tagline}, {worker.description}
Category: {worker.category}
Target audience: {worker.pillar}
```

### Phase 2: Image Generation (Gemini)

**Chrome Profile:** `~/.playwright-chrome-profile-gemini`
**URL:** `https://gemini.google.com/app`
**Output:** `public/images/ai-workers/{slug}.webp`
**Size:** 800x450px WebP @ 75% quality

**Style: "Analog to Digital Transformation"**

| Category | Real-World Setting | Analog Objects |
|----------|-------------------|----------------|
| logistics | Freight office, containers visible | Shipping docs, rate sheets, tracking boards |
| compliance | Customs office, inspection area | HS code manuals, classification forms, stamps |
| trading | Trading floor, sales office | RFQ printouts, pricing catalogs, contracts |
| financial | Finance office, accounting desk | Invoices, ledgers, calculator, spreadsheets |
| infrastructure | Records room, server area | Filing cabinets, archive boxes, cables |
| technology | IT room with multiple screens | Tangled cables, integration manuals |
| government | Government office, customs border | Official forms, stamps, permits |

**Brand Colors:**
- Brand Teal: `#3ECF8E` (primary AI accent)
- Deep Teal: `#1D6B4D` (secondary)
- Space Navy: `#0F1419` (dark base)

### Phase 3: Workflow Creation

**Location:** `apps/www/data/workflows/{slug}.ts`
**Visualization:** ReactFlow with custom N8nNode components

**Node Types → Colors:**
| Type | Background | Border |
|------|------------|--------|
| trigger/webhook | `#1a472a` | `#22c55e` (green) |
| code | `#422006` | `#f59e0b` (amber) |
| http | `#172554` | `#3b82f6` (blue) |
| ai/langchain | `#4a1d96` | `#a855f7` (purple) |

**Workflow Patterns:**
```python
WORKFLOW_PATTERNS = {
    'document-processing': ['Webhook', 'Extract Data (AI)', 'Validate', 'Store', 'Notify'],
    'monitoring': ['Schedule', 'Fetch Data', 'Analyze (AI)', 'Alert', 'Log'],
    'automation': ['Webhook', 'Parse', 'Process (AI)', 'Execute', 'Confirm'],
}
```

### Phase 4: Data Update

**File:** `apps/www/data/ai-workers.ts`

**Enhanced Fields:**
```typescript
{
  executiveSummary: string,      // 2-3 sentence value prop
  problem: string,               // Pain point statement
  solution: string,              // How it works
  keyMetric: {
    value: string,               // e.g., "85%"
    label: string,               // e.g., "Time Saved"
    context: string,             // e.g., "on manual classification"
  },
  valueOutcomes: [
    { outcome: string, description: string, metric: string }
  ],
  seoTitle: string,              // 50-60 chars with keyword
  seoDescription: string,        // 150-160 chars
  relatedWorkers: string[],      // Auto-detect from same category
}
```

### Phase 5: SEO Optimization

**Rules from global-trade-seo skill:**
- Title: `{Worker Name} | AI Workforce | Export Arena`
- Primary keyword in first paragraph
- Meta description 150-160 chars
- JSON-LD SoftwareApplication schema

### Phase 6: Verification

1. Build check: `pnpm build --filter www`
2. Playwright screenshots:
   - Desktop detail page
   - Mobile detail page
   - Desktop listing page
3. Content validation:
   - All required fields populated
   - Image exists and loads
   - Workflow diagram renders
   - No console errors

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/content-pipeline/ai-worker-orchestrator.py` | Main autonomous script |
| `scripts/content-pipeline/ai-worker-image-generator.py` | Gemini image generation |
| `apps/www/data/ai-workers.ts` | Worker definitions (63 total) |
| `apps/www/data/workflows/{slug}.ts` | Workflow definitions per worker |
| `apps/www/data/workflows/index.ts` | Workflow registry |
| `apps/www/pages/ai-workforce/[slug].tsx` | Detail page template |
| `apps/www/pages/ai-workforce/index.tsx` | Listing page |

## Image Display Rules

**Listing Page (`/ai-workforce`):**
- Mobile: Always show icons
- Desktop: Show images with fallback to icons

**Detail Page (`/ai-workforce/[slug]`):**
- All screens: Show image with 3-tier fallback
  1. `/images/ai-workers/{slug}.webp`
  2. `worker.heroImage`
  3. Icon placeholder with brand color

## Troubleshooting

| Issue | Solution |
|-------|----------|
| NotebookLM login required | Run script once, login manually, session persists |
| Gemini rate limit | Add 30-second delay between generations |
| Image download fails | Retry 2x, then skip and log |
| Build fails | Check TypeScript errors in ai-workers.ts |

## References

- `references/content-extraction.md` - NotebookLM patterns
- `references/image-generation.md` - Gemini "Analog to Digital" style
- `references/workflow-patterns.md` - n8n workflow templates
- `references/seo-checklist.md` - Export Arena SEO rules
