#!/usr/bin/env python3
"""
Page Cloner - Design Extraction Script

Extracts design data (screenshot, DOM structure, CSS properties, layout info)
from a target URL using Playwright.

Usage:
    python3 extract-design.py <url> [--slug <slug>] [--output-dir <dir>]

Examples:
    python3 extract-design.py https://supabase.com/auth
    python3 extract-design.py https://supabase.com/storage --slug storage-clone
    python3 extract-design.py https://supabase.com/edge-functions --output-dir /tmp/my-extraction

Output:
    /tmp/page-cloner/{slug}-original.png     Full-page screenshot
    /tmp/page-cloner/{slug}-extraction.json  Design data (sections, CSS, colors, typography)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


EXTRACTION_JS = """
(() => {
  const result = {
    url: window.location.href,
    title: document.title,
    viewport: { width: window.innerWidth, height: window.innerHeight },
    timestamp: new Date().toISOString(),
    cssVariables: {},
    sections: [],
    colorPalette: [],
    typographyScale: [],
    meta: {},
  };

  // 1. CSS custom properties from :root
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.selectorText === ':root' || (rule.selectorText && rule.selectorText.includes('[data-theme'))) {
          const matches = rule.cssText.matchAll(/--([\w-]+)\s*:\s*([^;]+)/g);
          for (const m of matches) {
            result.cssVariables['--' + m[1]] = m[2].trim();
          }
        }
      }
    } catch (e) {}
  }

  // 2. Sections
  const main = document.querySelector('main') || document.body;
  const sectionEls = main.querySelectorAll(':scope > section, :scope > div, :scope > article');
  const elements = sectionEls.length > 0
    ? Array.from(sectionEls)
    : Array.from(main.children).filter(el =>
        !['SCRIPT', 'STYLE', 'LINK', 'META'].includes(el.tagName)
      );

  elements.forEach((el, index) => {
    const styles = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
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
        background: styles.backgroundColor,
        color: styles.color,
        maxWidth: styles.maxWidth,
        borderRadius: styles.borderRadius,
      },
      headings: Array.from(el.querySelectorAll('h1,h2,h3,h4,h5,h6')).map(h => {
        const hs = getComputedStyle(h);
        return {
          tag: h.tagName.toLowerCase(),
          text: h.textContent.trim().substring(0, 120),
          fontSize: hs.fontSize,
          fontWeight: hs.fontWeight,
          lineHeight: hs.lineHeight,
          color: hs.color,
        };
      }),
      paragraphs: Array.from(el.querySelectorAll('p')).slice(0, 3).map(p => {
        const ps = getComputedStyle(p);
        return {
          text: p.textContent.trim().substring(0, 200),
          fontSize: ps.fontSize,
          color: ps.color,
        };
      }),
      buttons: Array.from(el.querySelectorAll('a[class*="btn"], button, a[class*="cta"], a[class*="Button"]')).map(b => ({
        text: b.textContent.trim().substring(0, 80),
        href: b.href || null,
      })),
      images: Array.from(el.querySelectorAll('img, svg')).slice(0, 5).map(img => ({
        tag: img.tagName.toLowerCase(),
        src: img.src || null,
        alt: img.alt || null,
        width: Math.round(img.getBoundingClientRect().width),
        height: Math.round(img.getBoundingClientRect().height),
      })),
      childCount: el.children.length,
      layoutPattern: null,
    };

    if (styles.display === 'grid') {
      section.layoutPattern = { type: 'grid', columns: styles.gridTemplateColumns, gap: styles.gap };
    } else if (styles.display === 'flex') {
      section.layoutPattern = { type: 'flex', direction: styles.flexDirection, gap: styles.gap };
    }

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

  // 3. Colors
  const colorSet = new Set();
  const allEls = document.querySelectorAll('*');
  for (let i = 0; i < Math.min(allEls.length, 500); i++) {
    const s = getComputedStyle(allEls[i]);
    colorSet.add(s.backgroundColor);
    colorSet.add(s.color);
  }
  result.colorPalette = Array.from(colorSet).filter(c =>
    c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent'
  );

  // 4. Typography
  const typo = new Map();
  document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,span,a,li').forEach(el => {
    const s = getComputedStyle(el);
    const key = s.fontSize + '|' + s.fontWeight + '|' + s.fontFamily.split(',')[0];
    if (!typo.has(key)) {
      typo.set(key, {
        fontSize: s.fontSize,
        fontWeight: s.fontWeight,
        fontFamily: s.fontFamily.split(',')[0].trim(),
        lineHeight: s.lineHeight,
      });
    }
  });
  result.typographyScale = Array.from(typo.values());

  // 5. Meta
  result.meta = {
    ogTitle: document.querySelector('meta[property="og:title"]')?.content || null,
    ogDescription: document.querySelector('meta[property="og:description"]')?.content || null,
    ogImage: document.querySelector('meta[property="og:image"]')?.content || null,
    description: document.querySelector('meta[name="description"]')?.content || null,
  };

  return JSON.stringify(result, null, 2);
})()
"""


def slug_from_url(url: str) -> str:
    """Derive a slug from a URL path."""
    path = urlparse(url).path.strip("/")
    if not path:
        return "homepage"
    return re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")


def extract_design(url: str, slug: str | None = None, output_dir: str | None = None):
    """Run Playwright to extract design data from the given URL."""
    slug = slug or slug_from_url(url)
    output_dir = Path(output_dir or "/tmp/page-cloner")
    output_dir.mkdir(parents=True, exist_ok=True)

    screenshot_path = output_dir / f"{slug}-original.png"
    json_path = output_dir / f"{slug}-extraction.json"

    print(f"Extracting design from: {url}")
    print(f"Slug: {slug}")
    print(f"Output: {output_dir}/")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            color_scheme="dark",
        )
        page = context.new_page()

        # Navigate
        print("  Navigating...")
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Wait for content to settle
        page.wait_for_timeout(2000)

        # Full-page screenshot
        print(f"  Taking screenshot -> {screenshot_path}")
        page.screenshot(path=str(screenshot_path), full_page=True)

        # Extract design data
        print("  Extracting design data...")
        raw = page.evaluate(EXTRACTION_JS)
        data = json.loads(raw)

        # Save JSON
        print(f"  Saving extraction -> {json_path}")
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)

        browser.close()

    # Summary
    print(f"\nExtraction complete!")
    print(f"  Sections found: {len(data.get('sections', []))}")
    print(f"  Colors found: {len(data.get('colorPalette', []))}")
    print(f"  Typography variants: {len(data.get('typographyScale', []))}")
    print(f"  CSS variables: {len(data.get('cssVariables', {}))}")
    print(f"\nFiles:")
    print(f"  Screenshot: {screenshot_path}")
    print(f"  Data: {json_path}")

    return data


def main():
    parser = argparse.ArgumentParser(
        description="Extract design data from a web page using Playwright"
    )
    parser.add_argument("url", help="Target URL to extract design from")
    parser.add_argument("--slug", help="Override the auto-generated slug")
    parser.add_argument(
        "--output-dir",
        default="/tmp/page-cloner",
        help="Output directory (default: /tmp/page-cloner)",
    )

    args = parser.parse_args()
    extract_design(args.url, args.slug, args.output_dir)


if __name__ == "__main__":
    main()
