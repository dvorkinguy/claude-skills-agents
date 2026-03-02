/**
 * Playwright E2E Test Template for CMS Blocks
 *
 * Usage:
 * 1. Copy to apps/www/e2e/cms/blocks/{{blockName}}.spec.ts
 * 2. Replace {{BlockName}}, {{blockName}} placeholders
 * 3. Run: npx playwright test e2e/cms/blocks/{{blockName}}.spec.ts
 */

import { test, expect } from '@playwright/test'

test.describe('{{BlockName}} Block', () => {
  // Test page that contains this block
  const testPageSlug = 'home' // Change to page with this block

  test.beforeEach(async ({ page }) => {
    // Navigate to page with block
    await page.goto(testPageSlug === 'home' ? '/' : `/${testPageSlug}`)

    // Wait for page to load
    await page.waitForLoadState('networkidle')
  })

  test('renders {{blockName}} section', async ({ page }) => {
    // Check section exists
    const section = page.locator('section').filter({
      has: page.locator('[data-block="{{blockName}}"]'),
    })

    // If using data attributes
    // await expect(section).toBeVisible()

    // Alternative: check for characteristic content
    // await expect(page.getByRole('heading', { level: 2 })).toBeVisible()
  })

  test('displays headline correctly', async ({ page }) => {
    // Check headline is visible
    const headline = page.getByRole('heading', { level: 2 }).first()
    await expect(headline).toBeVisible()

    // Check headline has content
    await expect(headline).not.toBeEmpty()
  })

  test('displays subheadline when present', async ({ page }) => {
    // Subheadline is optional, so check if section has one
    const subheadline = page.locator('section p.text-muted-foreground').first()

    // This may or may not exist depending on CMS content
    const count = await subheadline.count()
    if (count > 0) {
      await expect(subheadline).toBeVisible()
    }
  })

  test.describe('Style Variants', () => {
    test('default style renders correctly', async ({ page }) => {
      // Check default background
      const section = page.locator('section.bg-background').first()
      // May need to adjust selector based on actual implementation
    })

    test('alternate style renders correctly', async ({ page }) => {
      // Navigate to page with alternate style
      // await page.goto('/page-with-alternate-style')

      // Check alternate background
      // const section = page.locator('section.bg-muted').first()
      // await expect(section).toBeVisible()
    })
  })

  test.describe('Items/Features', () => {
    test('renders all items', async ({ page }) => {
      // Check items grid
      const items = page.locator('[data-block="{{blockName}}"] .grid > div')

      // Should have at least one item
      await expect(items.first()).toBeVisible()
    })

    test('each item has title', async ({ page }) => {
      const items = page.locator('[data-block="{{blockName}}"] .grid > div')
      const count = await items.count()

      for (let i = 0; i < count; i++) {
        const title = items.nth(i).locator('h3')
        await expect(title).toBeVisible()
        await expect(title).not.toBeEmpty()
      }
    })

    test('items have images when configured', async ({ page }) => {
      const items = page.locator('[data-block="{{blockName}}"] .grid > div')
      const firstItem = items.first()

      // Check if image exists
      const image = firstItem.locator('img')
      const hasImage = (await image.count()) > 0

      if (hasImage) {
        await expect(image).toHaveAttribute('src')
        await expect(image).toHaveAttribute('alt')
      }
    })
  })

  test.describe('CTA Buttons', () => {
    test('primary CTA is clickable', async ({ page }) => {
      const primaryCTA = page.locator('[data-block="{{blockName}}"] a.bg-primary')

      const hasPrimaryCTA = (await primaryCTA.count()) > 0
      if (hasPrimaryCTA) {
        await expect(primaryCTA).toBeVisible()
        await expect(primaryCTA).toHaveAttribute('href')
      }
    })

    test('secondary CTA is clickable', async ({ page }) => {
      const secondaryCTA = page.locator('[data-block="{{blockName}}"] a.border')

      const hasSecondaryCTA = (await secondaryCTA.count()) > 0
      if (hasSecondaryCTA) {
        await expect(secondaryCTA).toBeVisible()
        await expect(secondaryCTA).toHaveAttribute('href')
      }
    })
  })

  test.describe('Responsive Design', () => {
    test('renders correctly on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 })

      const section = page.locator('section').first()
      await expect(section).toBeVisible()

      // Check mobile-specific layout
      // Items should stack vertically on mobile
    })

    test('renders correctly on tablet', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 })

      const section = page.locator('section').first()
      await expect(section).toBeVisible()
    })

    test('renders correctly on desktop', async ({ page }) => {
      await page.setViewportSize({ width: 1440, height: 900 })

      const section = page.locator('section').first()
      await expect(section).toBeVisible()

      // Check desktop-specific layout
      // Items should be in grid
    })
  })

  test.describe('Accessibility', () => {
    test('has proper heading hierarchy', async ({ page }) => {
      // Check h2 exists within section
      const h2 = page.locator('section').first().getByRole('heading', { level: 2 })
      const hasH2 = (await h2.count()) > 0

      if (hasH2) {
        await expect(h2).toBeVisible()
      }
    })

    test('images have alt text', async ({ page }) => {
      const images = page.locator('section img')
      const count = await images.count()

      for (let i = 0; i < count; i++) {
        const alt = await images.nth(i).getAttribute('alt')
        expect(alt).toBeTruthy()
      }
    })

    test('links have descriptive text', async ({ page }) => {
      const links = page.locator('section a')
      const count = await links.count()

      for (let i = 0; i < count; i++) {
        const text = await links.nth(i).textContent()
        expect(text?.trim()).toBeTruthy()
      }
    })
  })

  test.describe('Performance', () => {
    test('images are lazy loaded', async ({ page }) => {
      const images = page.locator('section img[loading="lazy"]')
      // Images below the fold should have loading="lazy"
    })

    test('no layout shift on load', async ({ page }) => {
      // Check CLS by capturing layout
      const metrics = await page.evaluate(() => {
        return new Promise((resolve) => {
          new PerformanceObserver((list) => {
            const entries = list.getEntries()
            resolve(entries)
          }).observe({ type: 'layout-shift', buffered: true })

          // Timeout fallback
          setTimeout(() => resolve([]), 5000)
        })
      })

      // Layout shifts should be minimal
    })
  })
})

// ============================================
// Test Data Fixtures (optional)
// ============================================

/*
// e2e/cms/fixtures/test-data.ts
export const {{blockName}}TestData = {
  headline: 'Test Headline',
  subheadline: 'Test subheadline text',
  style: 'default',
  items: [
    { title: 'Item 1', description: 'Description 1' },
    { title: 'Item 2', description: 'Description 2' },
  ],
}
*/
