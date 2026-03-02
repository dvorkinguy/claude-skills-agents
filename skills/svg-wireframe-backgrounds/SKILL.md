---
name: svg-wireframe-backgrounds
description: Create large-scale wireframe SVG hero backgrounds for solution pages. Use when building hero images, page backgrounds, or oversized wireframe objects. Trigger keywords: wireframe, hero background, globe svg, shield svg, solution hero, background svg.
---

# SVG Wireframe Backgrounds

Create oversized, monochrome wireframe renderings of **recognizable real-world objects** for solution page hero sections. These are NOT abstract patterns - they are identifiable objects (globes, ships, vaults, cranes) drawn large enough to overflow the viewport, creating a cinematic "bigger than the screen" feel.

## When to Use

- Creating hero background images for solution pages
- Building wireframe object SVGs that fill the hero section
- Replacing placeholder hero images with domain-specific wireframes
- Any large-scale SVG background that needs the Export Arena wireframe style

## CRITICAL Design Rules

### What These Are
- **Recognizable real-world objects** rendered as wireframes (globe, shield, ship, vault, crane)
- **Oversized** - deliberately larger than the viewport, edges fade via radial mask
- **Monochrome gray** - no color, no fills on structural elements
- **Stroke-only** construction from basic SVG primitives

### What These Are NOT
- NOT abstract geometric patterns or generative art
- NOT small feature-card illustrations (use `svg-tech-illustrations` skill for those)
- NOT animated or interactive (pure static SVG files)
- NOT colorful or branded - strictly gray wireframe on dark backgrounds

## Style Specification

### Colors & Opacities

| Element | Value | Usage |
|---------|-------|-------|
| Primary stroke | `#707070` | All wireframe lines, curves, connections |
| Hero element stroke | `#808080` - `#909090` | Central/focal object borders (shield, ship hull) |
| Node dots fill | `#707070` | Small circles scattered on structural lines |
| Group opacity | `0.6` | Applied to the main `<g>` element wrapping everything |
| Fill | `none` | NO fills on wireframe paths (stroke-only) |

### Stroke Widths

| Width | Usage |
|-------|-------|
| `1.4` | Primary structural curves (ellipses, major arcs) |
| `1.8` | Hero element borders (shield outline, ship hull) |
| `1.2` | Inner hero detail (inner shield border, deck lines) |
| `0.8` | Connection lines between nodes |
| `0.6` | Secondary/ambient connections for mesh density |
| `2.0` | Special emphasis (checkmarks, key symbols inside hero) |

### Node Dots

Scatter small filled circles along structural lines to create a network/constellation feel:
```svg
<!-- Outer nodes: larger -->
<circle cx="148" cy="260" r="3.5" fill="#707070"/>
<circle cx="507" cy="40" r="4" fill="#707070"/>

<!-- Inner nodes: smaller -->
<circle cx="410" cy="240" r="2.5" fill="#707070"/>
<circle cx="600" cy="260" r="2.5" fill="#707070"/>
```

- Outer rings/structures: `r="3"` to `r="4"`
- Inner rings/structures: `r="2.5"` to `r="3"`
- Place nodes at intersections and along curves, NOT on a grid

## SVG Scaffold Template

Every wireframe background MUST use this exact structure:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1015" height="679" fill="none" viewBox="0 0 1015 679">
  <defs>
    <radialGradient id="fade" cx="507" cy="340" r="480" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#fff"/>
      <stop offset="0.65" stop-color="#fff"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <mask id="edgeFade" width="1015" height="679" x="0" y="0" maskUnits="userSpaceOnUse" style="mask-type:alpha">
      <rect x="0" y="0" width="1015" height="679" fill="url(#fade)"/>
    </mask>
  </defs>
  <g mask="url(#edgeFade)" opacity="0.6">

    <!-- LAYER 1: Background structure (rings, grids, orbits) -->
    <!-- ... ellipses, circles, arcs that extend to/beyond edges ... -->

    <!-- LAYER 2: Connection lines (node-to-node mesh) -->
    <!-- ... lines between nodes creating network feel ... -->

    <!-- LAYER 3: Central hero object (the recognizable thing) -->
    <!-- ... the ship/vault/crane/scale drawn with slightly brighter strokes ... -->

  </g>
</svg>
```

### Scaffold Rules

- **viewBox**: Always `0 0 1015 679` for hero backgrounds
- **Center point**: Main object centered at approximately `(507, 340)`
- **Mask**: Radial gradient mask fades edges - center is opaque, edges transparent
- **Layering order**: Background structure -> Connection mesh -> Hero object (foreground)
- **Overflow**: Objects SHOULD extend beyond viewBox edges - the mask fades them naturally

## Construction Technique Guide

### Building Recognizable Objects

Use only these SVG primitives - no complex path data or Bezier splines:

| Primitive | Best For | Example |
|-----------|----------|---------|
| `<ellipse>` | Rings, orbits, hulls, domes | Ship cross-sections, vault door rings |
| `<circle>` | Nodes, wheels, portholes, rivets | Network dots, vault dial |
| `<polygon>` | Shields, hull panels, roof shapes | `points="507,270 557,305 557,375 507,410 457,375 457,305"` |
| `<polyline>` | Checkmarks, masts, crane arms | Open shapes, non-closed paths |
| `<line>` | Connections, structural beams, rigging | Node-to-node links |
| `<rect>` | Containers, building segments, panels | With `rx` for rounded edges |
| `<path>` | Complex curves (arcs, wave profiles) | Use `M`, `L`, `A`, `Q` commands only |

### Layering Strategy

```
LAYER 1 - Background Structure (extends to edges and beyond)
  Purpose: Creates depth and context
  Elements: 4-6 concentric ellipses, slightly rotated
  Stroke: #707070, width 1.4
  Example: Scan rings around a radar, orbit lines around a globe

LAYER 2 - Connection Mesh (mid-density)
  Purpose: Creates network/tech feel
  Elements: 30-50 lines connecting scattered node dots
  Stroke: #707070, width 0.8 (primary) and 0.6 (secondary)
  Pattern: Connect nodes across rings, NOT in a grid pattern

LAYER 3 - Hero Object (center, 20-30% of viewport)
  Purpose: The recognizable real-world object
  Stroke: #808080 to #909090 (slightly brighter than background)
  Width: 1.8 for borders, 1.2 for inner detail
  Position: Centered at (507, 340), occupying roughly 100-200px radius
```

### Node Placement Rules

- Scatter 40-60 nodes total across all structural rings
- Outer rings: 8-11 nodes each, spaced irregularly
- Inner rings: 5-7 nodes each
- Place nodes WHERE structural lines naturally intersect or curve
- NOT on a regular grid - organic, slightly random placement
- Each node connects to 2-4 other nodes via lines

## Object Catalog

Domain-specific wireframe objects for each Export Arena solution page:

### GROW Category

| Page | Object | Key Elements |
|------|--------|--------------|
| Market Expansion | Globe with trade routes | Wireframe earth with latitude/longitude curves + shipping lane arcs (reference: `globe.svg`) |
| Speed to Market | Cargo vessel (side view) | Wireframe container ship hull, deck lines, crane outlines, container stacks |
| Growth Without Headcount | Industrial robot arm | Wireframe robotic arm with joint circles, grip mechanism, base pivot |
| Trade Finance | Bank vault door | Wireframe circular vault face with bolt circles, handle mechanism, locking bars |
| Operational Intelligence | Radar dish / Control tower | Wireframe parabolic dish with sweep rings, support struts, signal arcs |
| AI Tsunami 2026 | Tidal wave | Wireframe wave with spray particles, curl profile, foam nodes |

### PROTECT Category

| Page | Object | Key Elements |
|------|--------|--------------|
| Trade Compliance | Balance scale / Gavel | Wireframe scales of justice with beam, chains, pans - or gavel with sound block |
| Risk & Audit Defense | Shield with network | **Already exists** (`risk-shield.svg`) - hexagonal shield + concentric scan rings + checkmark |
| Margin Protection | Safe with dial | Wireframe safe front panel with combination dial, handle, hinges, bolt pattern |
| Logistics Automation | Gantry crane | Wireframe port crane with trolley rail, container hook, support legs, cables |
| Supply Chain Resilience | Anchor with chain | Wireframe anchor with flukes, shank, ring + chain links extending outward |
| Cash Flow Optimization | Hourglass | Wireframe hourglass with frame, glass bulbs (ellipses), sand particles (dots) |

### INDUSTRIES Category

| Page | Object | Key Elements |
|------|--------|--------------|
| Exporters & Manufacturers | Factory with smokestacks | Wireframe factory silhouette, sawtooth roof, smokestacks, loading dock |
| Importers & Distribution | Warehouse interior | Wireframe racking/shelving, forklift outline, pallet stacks |
| Logistics & Supply Chain | Container terminal | Wireframe stacked containers, reach stacker, terminal layout |
| Financial Services | Classical bank facade | Wireframe columns, pediment, steps, portico structure |
| Government & G2B | Capitol/institutional building | Wireframe dome, wings, columns, steps, flagpole |

## Sizing & Overflow Rules

```
viewBox:        0 0 1015 679
Center:         (507, 340)
Hero object:    Occupies ~20-30% of viewport center (~100-200px radius)
Background:     Extends TO and BEYOND viewBox edges
Mask radius:    480px from center - fully opaque at center, fades to transparent

The object should feel BIGGER than the screen:
- Outermost ring/structure should have rx/ry extending past 507/340 from center
- Connection lines should reach into corners
- The mask naturally fades everything at edges - let it do the work
```

## Integration Pattern

### In Solution Data Files

```tsx
// apps/www/data/solutions/[page-slug].tsx
heroSection: {
  title: 'Page Title',
  h1: ( ... ),
  subheader: [ ... ],
  image: (
    <div className="relative w-full aspect-[16/10] flex items-center justify-center">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/images/solutions/[page-slug]/hero-wireframe.svg"
        alt="Descriptive alt text for the wireframe object"
        width={1015}
        height={679}
        className="w-full h-auto"
      />
    </div>
  ),
  // ...
}
```

### File Location Convention

```
apps/www/public/images/solutions/[page-slug]/[object-name].svg

Examples:
  /images/solutions/compliance/risk-shield.svg        (exists)
  /images/solutions/speed-to-market/cargo-vessel.svg  (new)
  /images/solutions/trade-finance/vault-door.svg      (new)
  /images/solutions/logistics/gantry-crane.svg        (new)
```

## Complete Example: risk-shield.svg (Reference Implementation)

This is the canonical example. All new wireframe backgrounds should match this visual weight and density:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1015" height="679" fill="none" viewBox="0 0 1015 679">
  <defs>
    <radialGradient id="fade" cx="507" cy="340" r="480" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#fff"/>
      <stop offset="0.65" stop-color="#fff"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <mask id="edgeFade" width="1015" height="679" x="0" y="0"
          maskUnits="userSpaceOnUse" style="mask-type:alpha">
      <rect x="0" y="0" width="1015" height="679" fill="url(#fade)"/>
    </mask>
  </defs>
  <g mask="url(#edgeFade)" opacity="0.6">

    <!-- LAYER 1: Concentric elliptical scan rings -->
    <ellipse cx="507" cy="340" rx="460" ry="300" stroke="#707070"
             stroke-width="1.4" fill="none" transform="rotate(-6,507,340)"/>
    <ellipse cx="507" cy="340" rx="390" ry="255" stroke="#707070"
             stroke-width="1.4" fill="none" transform="rotate(4,507,340)"/>
    <ellipse cx="507" cy="340" rx="320" ry="210" stroke="#707070"
             stroke-width="1.4" fill="none" transform="rotate(-3,507,340)"/>
    <ellipse cx="507" cy="340" rx="250" ry="165" stroke="#707070"
             stroke-width="1.4" fill="none" transform="rotate(7,507,340)"/>
    <ellipse cx="507" cy="340" rx="180" ry="120" stroke="#707070"
             stroke-width="1.4" fill="none" transform="rotate(-5,507,340)"/>
    <ellipse cx="507" cy="340" rx="115" ry="78" stroke="#707070"
             stroke-width="1.4" fill="none" transform="rotate(3,507,340)"/>

    <!-- LAYER 3: Central hexagonal shield -->
    <polygon points="507,270 557,305 557,375 507,410 457,375 457,305"
             stroke="#909090" stroke-width="1.8" fill="none"/>
    <polygon points="507,282 548,311 548,369 507,398 466,369 466,311"
             stroke="#808080" stroke-width="1.2" fill="none"/>
    <polyline points="486,340 501,358 530,318"
              stroke="#909090" stroke-width="2" fill="none"
              stroke-linecap="round" stroke-linejoin="round"/>

    <!-- LAYER 1 continued: Network nodes (40-60 total) -->
    <!-- Ring 1 (outermost) - 11 nodes -->
    <circle cx="148" cy="260" r="3.5" fill="#707070"/>
    <circle cx="290" cy="100" r="3" fill="#707070"/>
    <circle cx="507" cy="40" r="4" fill="#707070"/>
    <!-- ... more nodes per ring ... -->

    <!-- LAYER 2: Connection lines -->
    <!-- Cross-ring connections: stroke-width 0.8 -->
    <line x1="148" y1="260" x2="200" y2="180" stroke="#707070" stroke-width="0.8"/>
    <!-- Secondary connections: stroke-width 0.6 -->
    <line x1="200" y1="180" x2="270" y2="175" stroke="#707070" stroke-width="0.6"/>
    <!-- Inner connections to hero element: stroke-width 0.8 -->
    <line x1="410" y1="240" x2="466" y2="305" stroke="#707070" stroke-width="0.8"/>

  </g>
</svg>
```

### Key Metrics From Reference

| Metric | Value |
|--------|-------|
| Total ellipse rings | 6 |
| Total node dots | ~45 |
| Total connection lines | ~35 |
| Ring rotations | Small angles (-6 to +7 degrees) for organic feel |
| Hero element size | ~140px tall, ~100px wide (polygon bounding box) |
| Outermost ring | rx=460, ry=300 (extends near viewBox edges) |

## Checklist Before Delivery

- [ ] viewBox is `0 0 1015 679`
- [ ] Uses radial gradient mask with `r="480"` centered at `(507, 340)`
- [ ] Main `<g>` has `opacity="0.6"`
- [ ] All strokes use `#707070` (background) or `#808080`-`#909090` (hero only)
- [ ] NO fills on structural elements (stroke-only wireframe)
- [ ] Hero object is recognizable - you can tell what it is at a glance
- [ ] Object overflows viewport edges (mask handles the fade)
- [ ] 4-6 concentric rings/structures with slight rotation offsets
- [ ] 40-60 scattered node dots with irregular spacing
- [ ] 30-50 connection lines creating mesh density
- [ ] Hero element uses slightly brighter strokes than background
- [ ] File saved to `/images/solutions/[page-slug]/[object-name].svg`
- [ ] Visual weight matches `risk-shield.svg` reference

## Common Mistakes

1. **Abstract patterns** - Draw a REAL OBJECT, not generative art or random geometry
2. **Too small** - The object should feel like it extends beyond the screen
3. **Regular grid nodes** - Scatter nodes organically along curves, not on a grid
4. **Using fills** - Wireframe means stroke-only (except node dots which are filled)
5. **Too bright** - The `opacity="0.6"` on the group + gray strokes should feel subtle
6. **Missing mask** - Without the radial fade mask, edges look clipped/harsh
7. **Symmetric rotations** - Vary ring rotations by small random angles (-7 to +7 degrees)
8. **Hero too large** - The central object should be 20-30% of viewport, not 50%+
9. **No connections to hero** - Inner nodes should connect to the hero element via lines
10. **Using color** - These are strictly monochrome gray. No green, no brand colors
