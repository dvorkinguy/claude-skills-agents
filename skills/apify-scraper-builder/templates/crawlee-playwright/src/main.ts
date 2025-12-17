/**
 * Playwright Crawler Template
 *
 * Full browser automation for JavaScript-rendered pages.
 * Best for: SPAs, dynamic content, modern websites with heavy JS.
 */

import { Actor } from 'apify';
import { PlaywrightCrawler, Dataset, KeyValueStore, log } from 'crawlee';

// Define input interface
interface Input {
    startUrls: { url: string }[];
    maxItems?: number;
    proxyConfig?: object;
    maxConcurrency?: number;
    navigationTimeoutSecs?: number;
    saveScreenshots?: boolean;
    debugMode?: boolean;
}

await Actor.init();

// Get and validate input
const input = await Actor.getInput<Input>();

if (!input?.startUrls?.length) {
    throw new Error('Input must include at least one start URL');
}

// Configure logging
if (input.debugMode) {
    log.setLevel(log.LEVELS.DEBUG);
}

log.info('Starting Playwright Crawler', {
    startUrls: input.startUrls.length,
    maxItems: input.maxItems || 'unlimited',
    saveScreenshots: input.saveScreenshots,
});

// Create proxy configuration
const proxyConfiguration = await Actor.createProxyConfiguration(input.proxyConfig);

// Initialize the crawler
const crawler = new PlaywrightCrawler({
    proxyConfiguration,
    maxRequestsPerCrawl: input.maxItems || undefined,
    maxConcurrency: input.maxConcurrency || 5,
    navigationTimeoutSecs: input.navigationTimeoutSecs || 60,

    // Browser launch options
    launchContext: {
        launchOptions: {
            args: ['--disable-dev-shm-usage'],
        },
    },

    async requestHandler({ page, request, enqueueLinks, log }) {
        log.info(`Processing ${request.url}`);

        // Wait for the page to fully load
        await page.waitForLoadState('networkidle');

        // ============================================
        // TODO: Wait for specific content if needed
        // ============================================
        // await page.waitForSelector('.content-loaded', { timeout: 30000 });

        // ============================================
        // TODO: Handle infinite scroll if needed
        // ============================================
        // let previousHeight = 0;
        // for (let i = 0; i < 5; i++) {
        //     await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        //     await page.waitForTimeout(2000);
        //     const currentHeight = await page.evaluate(() => document.body.scrollHeight);
        //     if (currentHeight === previousHeight) break;
        //     previousHeight = currentHeight;
        // }

        // ============================================
        // TODO: Implement your scraping logic here
        // ============================================

        // Example: Extract page title
        const title = await page.title();

        // Example: Extract items using page.evaluate
        const items = await page.$$eval('.item, .product, .card', elements =>
            elements.map(el => ({
                name: el.querySelector('h2, .title, .name')?.textContent?.trim(),
                description: el.querySelector('p, .description')?.textContent?.trim(),
                link: el.querySelector('a')?.getAttribute('href'),
            })).filter(item => item.name)
        );

        // Example: Extract single elements
        const pageContent = await page.$eval('main, .content, article', el => ({
            text: el.textContent?.trim().slice(0, 500),
            html: el.innerHTML.slice(0, 1000),
        })).catch(() => null);

        // Save screenshot if enabled
        if (input.saveScreenshots) {
            const screenshot = await page.screenshot({ fullPage: true });
            const key = `screenshot_${request.url.replace(/[^a-zA-Z0-9]/g, '_').slice(0, 50)}`;
            await KeyValueStore.setValue(key, screenshot, { contentType: 'image/png' });
            log.debug(`Saved screenshot: ${key}`);
        }

        // Save data to dataset
        await Dataset.pushData({
            url: request.url,
            title,
            itemCount: items.length,
            items,
            content: pageContent,
            scrapedAt: new Date().toISOString(),
        });

        // ============================================
        // TODO: Configure pagination/link following
        // ============================================

        // Example: Follow pagination links
        // await enqueueLinks({
        //     selector: 'a.next-page, .pagination a[href]',
        //     label: 'PAGINATION',
        // });

        // Example: Follow detail page links
        // await enqueueLinks({
        //     selector: '.product-link',
        //     label: 'DETAIL',
        // });
    },

    // Handle failed requests
    async failedRequestHandler({ request, log, error }) {
        log.error(`Request failed: ${request.url}`, { error: error.message });

        await Dataset.pushData({
            url: request.url,
            error: error.message,
            status: 'failed',
            failedAt: new Date().toISOString(),
        });
    },
});

// Run the crawler
await crawler.run(input.startUrls.map(item => item.url));

log.info('Crawl finished');
await Actor.exit();
