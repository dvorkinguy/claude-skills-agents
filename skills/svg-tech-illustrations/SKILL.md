# SVG Tech Illustrations Skill

Create professional, minimal SVG illustrations for tech/AI products. Inspired by Supabase, Vercel, and Linear's visual design language.

## CRITICAL: Research Before Design

**ALWAYS read content-research files before creating visuals:**

```bash
# Location: _docs/content-research/solutions/
answers-logistics-supply-chain.txt    # Freight, customs, D&D
answers-compliance-regulatory.txt     # Sanctions, classification
answers-trade-finance-payments.txt    # LC, payments
# ... etc for each solution page
```

These files contain:
- **Real industry numbers** (response times, error rates, penalties)
- **Specific value propositions** for each AI Worker
- **Domain terminology** and concepts
- **Customer pain points** that inform the visual story

**Example real data to use:**
- RFQ Response: "60 hour average → 15 minutes" (not generic "fast")
- Sanctions: "$1M per violation, 20 years prison" (real stakes)
- D&D fees: "Up to $63,000 per container" (specific numbers)
- Classification: "18%-40% error rate for complex goods"

**WHY this matters:**
Generic visuals (clocks, shields) are boring. Visuals that tell a STORY with real data are compelling.

## When to Use This Skill

Use when creating:
- Feature card illustrations for landing pages
- Product capability visuals
- Dashboard/app UI mockups
- Data flow diagrams
- Network/connection visualizations
- Abstract tech concepts

## Design Principles

### 1. Color Palette (Dark Theme)

**Standard Palette (rgba-based)**
```
Background:     #0a0a0a / #111111 (card backgrounds)
Primary:        rgba(255, 255, 255, 0.35) - main strokes
Secondary:      rgba(255, 255, 255, 0.15) - secondary/background elements
Subtle:         rgba(255, 255, 255, 0.05) - fills, grids
Accent:         #3ECF8E (green) - ONE focal highlight per illustration
Text:           rgba(255, 255, 255, 0.5) - labels inside SVGs
```

**Alternative Palette (hex-based, lighter for card visuals)**
```
Primary:        #9a9a9a - Main strokes, primary text
Secondary:      #8a8a8a - Labels, secondary elements
Background:     #7a7a7a - Background elements, zones
Disabled:       #6a6a6a - Inactive/disabled states
Accent:         #3ecf8e - SUCCESS STATES ONLY (see Green Usage below)
```

Use the lighter hex palette when:
- Visual needs to be clearly visible on dark cards
- Elements are small/detailed (under 200px viewBox)
- Text readability is critical
- You need precise control over opacity

**Green (#3ecf8e) Usage Rules - CRITICAL**
```
✅ USE green for:
   - Success values on hover (e.g., savings amounts)
   - Status changes (e.g., "CLEARED", "MATCHED")
   - Glow effects via SVG filter
   - Small indicator arrows on hover

❌ DO NOT use green for:
   - Base/default state elements
   - Static text or labels
   - Borders or strokes
   - Background fills
   - More than 1-2 elements per visual
```

### 2. Stroke Standards

- **Primary strokes**: 1-1.5px width
- **Secondary strokes**: 0.5-1px width
- **Consistent weights** throughout illustration
- **Rounded corners**: rx="2-4" for rectangles
- **No hard shadows** - use subtle opacity fills instead

### 3. Visual Types

#### A. UI Mockups (Authentication, Forms)
Show abstract interfaces with:
- Input fields as rounded rectangles
- Placeholder text as gray bars
- User avatars as circles with simple heads
- Cards with subtle borders

```svg
<!-- Example: User card -->
<rect x="20" y="20" width="80" height="30" rx="4"
  stroke="rgba(255,255,255,0.35)" fill="rgba(255,255,255,0.05)" />
<rect x="30" y="30" width="40" height="6" rx="1"
  fill="rgba(255,255,255,0.2)" /> <!-- text placeholder -->
```

#### B. Network/Graph Diagrams (Edge Functions, Connections)
Show relationships with:
- Circles for nodes (8-12px radius)
- Lines for connections
- Dashed lines for optional/async connections
- One node highlighted with accent color

```svg
<!-- Example: Network node -->
<circle cx="100" cy="60" r="10"
  stroke="rgba(255,255,255,0.35)" fill="rgba(255,255,255,0.05)" />
<!-- Highlighted hub -->
<circle cx="100" cy="60" r="10"
  fill="rgba(62,207,142,0.2)" stroke="#3ECF8E" />
```

#### C. Icon Grids (Storage, Files)
Show collections with:
- 3x3 or 4x3 grids of small icons
- Consistent spacing (gap: 8-12px)
- Simple icon shapes (document, image, video)
- Slight opacity variation for depth

```svg
<!-- Example: File icon -->
<rect x="20" y="20" width="24" height="30" rx="2"
  stroke="rgba(255,255,255,0.2)" fill="none" />
<path d="M 20,27 L 35,27" stroke="rgba(255,255,255,0.15)" /> <!-- fold line -->
```

#### D. 3D Isometric Elements (Vector, Cubes)
Show dimensionality with:
- 30° isometric angles
- Subtle face fills with different opacities
- Floating dots/particles around object
- Clean edge lines

```svg
<!-- Example: Isometric cube face -->
<path d="M 100,40 L 130,55 L 130,85 L 100,70 Z"
  fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.3)" />
```

#### E. Data Flow/Pipeline (APIs, Processing)
Show transformations with:
- Rectangles for stages/endpoints
- Arrows or dashed lines for flow
- Labels inside or beside elements
- Accent color for active/highlighted stage

```svg
<!-- Example: API endpoint -->
<rect x="20" y="50" width="60" height="20" rx="10"
  fill="rgba(62,207,142,0.15)" stroke="#3ECF8E" />
<text x="50" y="63" text-anchor="middle" font-size="8"
  fill="#3ECF8E">/v1/data</text>
```

#### F. Symbolic/Logo (Database, Brand Elements)
Show concepts with:
- Large central icon (40-60% of canvas)
- Thin line art style
- Recognizable silhouette
- Accent color optional

### 4. Animation Guidelines (Hover-Only)

**DO NOT** use continuous animations. Instead:
- Use CSS `group-hover:` classes or `isHovered` prop
- Fade in elements: `opacity-0 group-hover:opacity-100`
- Translate elements: `group-hover:translate-x-2`
- Rotate elements: `group-hover:rotate-45`
- Always include `transition-all duration-500`

```tsx
<g className="opacity-0 transition-all duration-500 group-hover:opacity-100">
  {/* Elements that appear on hover */}
</g>
```

**isHovered Prop Pattern (preferred for complex visuals)**
```tsx
interface Props {
  className?: string
  isHovered?: boolean  // Passed from parent component
}

const Visual: React.FC<Props> = ({ className, isHovered = false }) => {
  return (
    <svg>
      <g className={cn(
        'transition-all duration-500',
        isHovered ? 'opacity-100' : 'opacity-40'
      )}>
        {/* Elements that change on hover */}
      </g>
    </svg>
  )
}
```

**Animation Timing Guidelines**
- **Transition duration**: 500-1500ms (slow, deliberate feel)
- **Transition easing**: `ease-out` for natural deceleration
- **Staggered delays**: 200-400ms between sequential elements
- **No looping animations** except subtle pulses on hover

### 4a. Number/Value Transition Pattern

For values that change on hover (savings, percentages, counters), use the **dual text crossfade** pattern:

```tsx
{/* Base value - fades out on hover */}
<text
  x="100"
  y="50"
  fill="#9a9a9a"
  className={cn(
    'transition-all duration-1000 ease-out',
    isHovered ? 'opacity-0' : 'opacity-100'
  )}
>
  $2,450
</text>

{/* Hover value - fades in with delay */}
<text
  x="100"
  y="50"
  fill="#3ecf8e"
  className={cn(
    'transition-all duration-1000 ease-out',
    isHovered ? 'opacity-100' : 'opacity-0'
  )}
  style={{ transitionDelay: isHovered ? '400ms' : '0ms' }}
  filter={isHovered ? 'url(#glow-filter)' : undefined}
>
  $3,120
</text>
```

Key points:
- Both text elements at same position (overlap)
- Base uses gray, hover uses green (for positive changes)
- Delay on hover-in prevents jarring instant change
- Optional glow filter on success value

### 5. Composition Rules (Supabase-Inspired)

**The "One Hero" Rule**
```
WRONG: Multiple equal-weight elements (boxes + lines + hub + counter + labels)
RIGHT: ONE dominant visual + supporting elements at lower visual weight

Each card needs a HERO - the single element your eye goes to first.
```

**Story-Driven Design (CRITICAL)**
```
WRONG: Generic symbol (clock for speed, shield for security)
RIGHT: Visual that shows BEFORE → AFTER transformation

Every visual should tell a mini-story:
1. Show the PROBLEM (pain point from content-research)
2. Show the SOLUTION (what the AI Worker does)
3. Use REAL NUMBERS from content-research

Examples:
- RFQ Responder: "60hr email delay" → "15m response" (not just a clock)
- Sanctions Sentry: "Hidden ownership chains" → "Risk detected" (not just a shield)
- Rate Auditor: "$4,250 invoiced" vs "$4,100 contracted" → "Recovered $150"
```

**Unique Visual Language Per Card Set**
When creating multiple cards in a section, EACH card MUST use a DIFFERENT visual metaphor:
```
✅ Good variety:
   - Tree/branching structure (Classification)
   - Timeline/zone layout (Port Monitor)
   - Floating UI cards (Document Digitizer)
   - Inbox/email transformation (RFQ Responder)
   - Ownership network graph (Sanctions Sentry)
   - Two-column comparison (Rate Auditor)
   - 3D geometric shape
   - Icon grid
   - Network constellation

❌ BAD: All cards using "boxes connected by lines to center hub"
❌ BAD: Generic symbols without story (clock, shield, magnifying glass)
```

**Visual Zone Separation**
```
┌─────────────────────────┐
│ TEXT ZONE               │ ← Title, description (z-10)
│ (top 40%, always clear) │    NEVER overlap with visual
├─────────────────────────┤
│                         │
│    VISUAL ZONE          │ ← Hero element lives here
│    (bottom 55-60%)      │    Positioned absolutely
│    Extends beyond edges │    Fades at card boundaries
└─────────────────────────┘
```

**Overflow & Fade**
- Extend visuals 10-20% beyond card boundaries
- Use `overflow-hidden` on card, position visual to overflow
- Fade edges with gradient opacity or mask-image
- Creates sense of infinite space

**Traditional Composition Principles**
1. **Single focal point** - One element draws the eye (green accent)
2. **Negative space** - Don't fill every corner, leave breathing room
3. **Layered depth**:
   - Background: subtle grid/pattern (5% opacity)
   - Midground: main shapes (20-40% opacity)
   - Foreground: highlighted elements (green accent)
4. **Asymmetric balance** - Avoid perfect symmetry, feels more natural
5. **Text as decoration** - Small labels add context without dominating

### 6. ViewBox Standards

```svg
<!-- Standard card illustration -->
<svg viewBox="0 0 200 120" className="w-full h-full">

<!-- Larger hero illustration -->
<svg viewBox="0 0 400 300" className="w-full h-full">
```

## Example Templates

### Network Diagram Template
```tsx
<svg viewBox="0 0 200 120" fill="none">
  {/* Background grid */}
  <defs>
    <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.5" fill="white" opacity="0.03" />
    </pattern>
  </defs>
  <rect width="200" height="120" fill="url(#grid)" />

  {/* Nodes */}
  <circle cx="40" cy="40" r="8" stroke="rgba(255,255,255,0.35)" fill="rgba(255,255,255,0.05)" />
  <circle cx="160" cy="40" r="8" stroke="rgba(255,255,255,0.35)" fill="rgba(255,255,255,0.05)" />
  <circle cx="40" cy="80" r="8" stroke="rgba(255,255,255,0.35)" fill="rgba(255,255,255,0.05)" />
  <circle cx="160" cy="80" r="8" stroke="rgba(255,255,255,0.35)" fill="rgba(255,255,255,0.05)" />

  {/* Central hub (accent) */}
  <circle cx="100" cy="60" r="14" fill="rgba(62,207,142,0.15)" stroke="#3ECF8E" strokeWidth="1.5" />

  {/* Connections */}
  <line x1="48" y1="44" x2="88" y2="56" stroke="rgba(255,255,255,0.2)" />
  <line x1="152" y1="44" x2="112" y2="56" stroke="rgba(255,255,255,0.2)" />
  <line x1="48" y1="76" x2="88" y2="64" stroke="rgba(255,255,255,0.2)" />
  <line x1="152" y1="76" x2="112" y2="64" stroke="rgba(255,255,255,0.2)" />
</svg>
```

### Data Table Template
```tsx
<svg viewBox="0 0 200 120" fill="none">
  {/* Table container */}
  <rect x="20" y="15" width="160" height="90" rx="4"
    stroke="rgba(255,255,255,0.35)" fill="rgba(255,255,255,0.05)" />

  {/* Header row */}
  <rect x="20" y="15" width="160" height="18" rx="4" fill="rgba(255,255,255,0.06)" />
  <line x1="20" y1="33" x2="180" y2="33" stroke="rgba(255,255,255,0.15)" />

  {/* Row 1 - highlighted */}
  <rect x="22" y="36" width="156" height="20" rx="2" fill="rgba(62,207,142,0.1)" />
  <circle cx="32" cy="46" r="4" fill="#3ECF8E" />
  <rect x="42" y="43" width="50" height="6" rx="1" fill="rgba(255,255,255,0.3)" />

  {/* Row 2 */}
  <circle cx="32" cy="66" r="4" stroke="rgba(255,255,255,0.35)" fill="none" />
  <rect x="42" y="63" width="45" height="6" rx="1" fill="rgba(255,255,255,0.2)" />

  {/* Row 3 */}
  <circle cx="32" cy="86" r="4" stroke="rgba(255,255,255,0.35)" fill="none" />
  <rect x="42" y="83" width="55" height="6" rx="1" fill="rgba(255,255,255,0.2)" />
</svg>
```

### Icon Grid Template
```tsx
<svg viewBox="0 0 200 120" fill="none">
  {/* 3x3 icon grid */}
  {[0, 1, 2].map(row =>
    [0, 1, 2].map(col => (
      <rect
        key={`${row}-${col}`}
        x={30 + col * 50}
        y={15 + row * 35}
        width="35"
        height="28"
        rx="3"
        stroke="rgba(255,255,255,0.2)"
        fill="rgba(255,255,255,0.03)"
      />
    ))
  )}

  {/* Icon symbols inside (simplified) */}
  {/* Image icon */}
  <path d="M 40,28 L 55,28 M 47,23 L 47,33" stroke="rgba(255,255,255,0.25)" />

  {/* Document icon */}
  <path d="M 92,25 L 92,37 L 103,37 L 103,28 L 100,25 Z"
    stroke="rgba(255,255,255,0.25)" fill="none" />
</svg>
```

## Solution-Specific Visual Guidelines

### Classification Specialist (HS Code Classification)

**Domain Context:**
- Harmonized System: 97 chapters, 5,205 commodity groups
- Classification: 6-12 digit codes (e.g., 8471.30.0100)
- GRI: General Rules of Interpretation (legal framework)
- Defense Memos: Legal justification documents
- 95-99% accuracy up to 11th digit

**Visual Concept: Code Matching/Search Tree**
- Vertical decision tree from product → HS code
- Chapters (84-XX) as branch nodes
- Final code as highlighted terminal node
- Path illumination shows classification journey

**Elements to Include:**
```
- Product icon at top (box/package shape)
- Tree branches representing chapter splits
- Chapter labels: CH (Chapter), HD (Heading), SH (Subheading)
- HS code at terminal node (e.g., "8471.30")
- Category codes floating subtly (84, 85, 73)
```

**Hover Behavior:**
```tsx
// Path illuminates sequentially from top to bottom
<line
  className={cn(
    'transition-all duration-500',
    isHovered ? 'stroke-[#9a9a9a] opacity-70' : 'stroke-[#6a6a6a] opacity-30'
  )}
  style={{ transitionDelay: isHovered ? `${nodeIndex * 150}ms` : '0ms' }}
/>

// Terminal node shows success (HS code found)
<text fill="#3ecf8e" className={isHovered ? 'opacity-80' : 'opacity-0'}>
  8471.30
</text>
```

**Don'ts:**
- No continuous dot animations along path
- No pulsing rings (use opacity fade instead)
- Don't show too many HS codes at once

---

## Development Workflow

**Always navigate to the page being developed:**
- Solution visuals: `http://localhost:3000/solutions/{solution-slug}`
- AI Workers: `http://localhost:3000/ai-workers/{worker-slug}`
- Check dev server is running before starting new one

**Screenshot on the fly** - verify visuals after each change, don't wait.

---

## Checklist Before Delivery

- [ ] Single accent color (green #3ECF8E)
- [ ] No continuous animations
- [ ] Consistent stroke widths (1-1.5px)
- [ ] Sufficient negative space
- [ ] Labels are subtle (0.4-0.5 opacity)
- [ ] ViewBox matches use case
- [ ] Hover effects use CSS classes
- [ ] Dark theme optimized
- [ ] One clear focal point

## Common Mistakes to Avoid

1. **Too much green** - Use sparingly, one element per illustration
2. **Inconsistent stroke widths** - Stick to 1px or 1.5px
3. **Hard edges** - Use rx="2-4" for rounded corners
4. **Continuous animations** - Only animate on hover
5. **Too dense** - Leave 30-40% negative space
6. **Realistic renders** - Keep abstract and diagrammatic
7. **Multiple colors** - Monochrome with ONE accent
8. **Instant value changes** - Use slow crossfade (1000ms) for number transitions
9. **Too dark grays** - Use #9a9a9a range for readable card visuals
10. **Generic numbers** - Research realistic industry data from content-research files
11. **Green in base state** - Green should only appear on hover for success states
12. **Same visual language** - Each card in a set needs UNIQUE metaphor (not all "boxes + lines")
13. **Multiple equal-weight elements** - Use ONE hero element, rest are supporting
14. **Visual overlapping text** - Keep text zone (top 40%) clear of visuals
15. **Generic symbols without story** - Don't use clock for speed, shield for security without context
16. **Skipping content-research** - ALWAYS read _docs/content-research before designing
17. **No before/after** - Show transformation, not static state
18. **Fake numbers** - Use real data ("60hr → 15m") not made-up values
