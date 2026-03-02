# Extraction Patterns

Playwright `browser_evaluate` JavaScript snippets for extracting design data from Supabase.com pages.

## Complete Extraction Script

Use this as a single `browser_evaluate` call to extract all design data at once:

```javascript
(() => {
  const result = {
    url: window.location.href,
    title: document.title,
    viewport: { width: window.innerWidth, height: window.innerHeight },
    timestamp: new Date().toISOString(),
    cssVariables: {},
    sections: [],
    colorPalette: new Set(),
    typographyScale: [],
    gridLayouts: [],
  };

  // 1. Extract CSS custom properties from :root
  const rootStyles = getComputedStyle(document.documentElement);
  const sheets = Array.from(document.styleSheets);
  for (const sheet of sheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.selectorText === ':root' || rule.selectorText === '[data-theme="dark"]') {
          const text = rule.cssText;
          const varMatches = text.matchAll(/--([\w-]+)\s*:\s*([^;]+)/g);
          for (const m of varMatches) {
            result.cssVariables[`--${m[1]}`] = m[2].trim();
          }
        }
      }
    } catch (e) { /* cross-origin sheet, skip */ }
  }

  // 2. Extract sections
  const sectionSelectors = 'main > section, main > div, [data-section], .section-container, article';
  const sections = document.querySelectorAll(sectionSelectors);
  const mainEl = document.querySelector('main') || document.body;

  // Fallback: if no sections found, use direct children of main
  const elements = sections.length > 0
    ? Array.from(sections)
    : Array.from(mainEl.children).filter(el =>
        el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE' && el.tagName !== 'LINK'
      );

  elements.forEach((el, index) => {
    const styles = getComputedStyle(el);
    const rect = el.getBoundingClientRect();

    // Skip tiny or invisible elements
    if (rect.height < 20) return;

    const section = {
      index,
      tagName: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: Array.from(el.classList).join(' '),
      dimensions: {
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        top: Math.round(rect.top + window.scrollY),
      },
      styles: {
        display: styles.display,
        flexDirection: styles.flexDirection,
        gridTemplateColumns: styles.gridTemplateColumns,
        gap: styles.gap,
        padding: styles.padding,
        paddingTop: styles.paddingTop,
        paddingBottom: styles.paddingBottom,
        paddingLeft: styles.paddingLeft,
        paddingRight: styles.paddingRight,
        margin: styles.margin,
        background: styles.backgroundColor,
        color: styles.color,
        maxWidth: styles.maxWidth,
        borderRadius: styles.borderRadius,
        overflow: styles.overflow,
      },
      // Headings in this section
      headings: Array.from(el.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => {
        const hs = getComputedStyle(h);
        return {
          tag: h.tagName.toLowerCase(),
          text: h.textContent.trim().substring(0, 120),
          fontSize: hs.fontSize,
          fontWeight: hs.fontWeight,
          lineHeight: hs.lineHeight,
          color: hs.color,
          fontFamily: hs.fontFamily.split(',')[0].trim(),
        };
      }),
      // Paragraphs (first 3)
      paragraphs: Array.from(el.querySelectorAll('p')).slice(0, 3).map(p => {
        const ps = getComputedStyle(p);
        return {
          text: p.textContent.trim().substring(0, 200),
          fontSize: ps.fontSize,
          fontWeight: ps.fontWeight,
          lineHeight: ps.lineHeight,
          color: ps.color,
        };
      }),
      // Buttons/CTAs
      buttons: Array.from(el.querySelectorAll('a[class*="btn"], button, a[class*="cta"], a[class*="Button"]')).map(b => ({
        text: b.textContent.trim().substring(0, 80),
        href: b.href || null,
        classes: Array.from(b.classList).join(' '),
      })),
      // Images
      images: Array.from(el.querySelectorAll('img, svg')).slice(0, 5).map(img => ({
        tag: img.tagName.toLowerCase(),
        src: img.src || null,
        alt: img.alt || null,
        width: img.width || img.getBoundingClientRect().width,
        height: img.height || img.getBoundingClientRect().height,
      })),
      // Grid children count
      childCount: el.children.length,
      // Detect grid/flex patterns
      layoutPattern: null,
    };

    // Detect layout pattern
    if (styles.display === 'grid') {
      section.layoutPattern = {
        type: 'grid',
        columns: styles.gridTemplateColumns,
        rows: styles.gridTemplateRows,
        gap: styles.gap,
      };
    } else if (styles.display === 'flex') {
      section.layoutPattern = {
        type: 'flex',
        direction: styles.flexDirection,
        wrap: styles.flexWrap,
        gap: styles.gap,
        justifyContent: styles.justifyContent,
        alignItems: styles.alignItems,
      };
    }

    // Also check immediate children for grid/flex
    const firstChild = el.children[0];
    if (firstChild) {
      const cs = getComputedStyle(firstChild);
      if (cs.display === 'grid' || cs.display === 'flex') {
        section.innerLayout = {
          type: cs.display,
          columns: cs.gridTemplateColumns,
          direction: cs.flexDirection,
          gap: cs.gap,
        };
      }
    }

    result.sections.push(section);
  });

  // 3. Collect unique colors
  const allElements = document.querySelectorAll('*');
  const colorSet = new Set();
  const typographySet = new Map();

  for (let i = 0; i < Math.min(allElements.length, 500); i++) {
    const s = getComputedStyle(allElements[i]);
    colorSet.add(s.backgroundColor);
    colorSet.add(s.color);
    if (s.borderColor !== 'rgb(0, 0, 0)') colorSet.add(s.borderColor);

    // Typography
    const key = `${s.fontSize}|${s.fontWeight}|${s.fontFamily.split(',')[0].trim()}`;
    if (!typographySet.has(key)) {
      typographySet.set(key, {
        fontSize: s.fontSize,
        fontWeight: s.fontWeight,
        fontFamily: s.fontFamily.split(',')[0].trim(),
        lineHeight: s.lineHeight,
        letterSpacing: s.letterSpacing,
      });
    }
  }

  result.colorPalette = Array.from(colorSet).filter(c =>
    c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent'
  );
  result.typographyScale = Array.from(typographySet.values());

  // 4. Page-level metadata
  result.meta = {
    ogTitle: document.querySelector('meta[property="og:title"]')?.content || null,
    ogDescription: document.querySelector('meta[property="og:description"]')?.content || null,
    ogImage: document.querySelector('meta[property="og:image"]')?.content || null,
    description: document.querySelector('meta[name="description"]')?.content || null,
  };

  return JSON.stringify(result, null, 2);
})()
```

---

## Individual Extraction Snippets

### CSS Variables Only

```javascript
(() => {
  const vars = {};
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.selectorText === ':root') {
          const matches = rule.cssText.matchAll(/--([\w-]+)\s*:\s*([^;]+)/g);
          for (const m of matches) vars[`--${m[1]}`] = m[2].trim();
        }
      }
    } catch (e) {}
  }
  return JSON.stringify(vars, null, 2);
})()
```

### Section Structure Only

```javascript
(() => {
  const main = document.querySelector('main') || document.body;
  return JSON.stringify(
    Array.from(main.children)
      .filter(el => el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE')
      .map((el, i) => {
        const r = el.getBoundingClientRect();
        return {
          index: i,
          tag: el.tagName.toLowerCase(),
          id: el.id || null,
          classes: el.className,
          height: Math.round(r.height),
          headings: Array.from(el.querySelectorAll('h1,h2,h3')).map(h => ({
            tag: h.tagName, text: h.textContent.trim().substring(0, 100)
          })),
        };
      }),
    null, 2
  );
})()
```

### Color Palette Only

```javascript
(() => {
  const colors = new Set();
  document.querySelectorAll('*').forEach(el => {
    const s = getComputedStyle(el);
    colors.add(s.backgroundColor);
    colors.add(s.color);
  });
  return JSON.stringify(
    Array.from(colors).filter(c => c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent'),
    null, 2
  );
})()
```

### Typography Scale Only

```javascript
(() => {
  const typo = new Map();
  document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,span,a,li,td,th,label').forEach(el => {
    const s = getComputedStyle(el);
    const key = `${s.fontSize}|${s.fontWeight}|${s.fontFamily.split(',')[0]}`;
    if (!typo.has(key)) {
      typo.set(key, {
        fontSize: s.fontSize, fontWeight: s.fontWeight,
        fontFamily: s.fontFamily.split(',')[0].trim(),
        lineHeight: s.lineHeight, letterSpacing: s.letterSpacing,
      });
    }
  });
  return JSON.stringify(Array.from(typo.values()), null, 2);
})()
```

---

## Supabase-Specific Selectors

Supabase.com uses these common patterns:

| Element | Selector |
|---------|----------|
| Main content | `main`, `#__next > div > main` |
| Nav | `nav`, `header` |
| Hero section | `section:first-of-type`, `[class*="hero"]` |
| Feature cards | `[class*="grid"] > div`, `[class*="card"]` |
| CTA buttons | `a[class*="button"], button[class*="btn"]` |
| Code blocks | `pre code`, `[class*="code"]` |
| Dark background | Elements with `bg-gray-900`, `bg-[#1C1C1C]`, `bg-background` |

---

## Color Mapping: Supabase to Export Arena

| Supabase Color | Export Arena Variable | Usage |
|----------------|----------------------|-------|
| `#3ECF8E` (brand green) | `hsl(var(--brand-default))` | Primary accent |
| `#1C1C1C` / `#111` (bg dark) | `hsl(var(--background-default))` | Page background |
| `#171717` (surface) | `hsl(var(--background-surface-100))` | Card backgrounds |
| `#EDEDED` / `#F8F8F8` (text) | `hsl(var(--foreground-default))` | Primary text |
| `#8F8F8F` (muted text) | `hsl(var(--foreground-lighter))` | Secondary text |
| `#2E2E2E` (border) | `hsl(var(--border-default))` | Borders, dividers |

Use Export Arena's CSS variable classes (Tailwind):
- `text-foreground` (primary text)
- `text-foreground-light` (secondary)
- `text-foreground-lighter` (muted)
- `bg-default` / `bg-background` (page bg)
- `bg-surface-100` (card bg)
- `bg-alternative` (avoid per CLAUDE.md rules)
- `border-default` (borders)
- `text-brand` / `bg-brand` (accent)
