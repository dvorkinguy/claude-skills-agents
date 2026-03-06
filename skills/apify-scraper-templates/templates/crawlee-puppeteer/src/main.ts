/**
 * Puppeteer Crawler Template
 *
 * Chrome-specific browser automation with Puppeteer.
 * Best for: Legacy sites, Chrome DevTools Protocol features, specific Chrome behavior.
 */

import { Actor } from 'apify';
import { PuppeteerCrawler, Dataset, log } from 'crawlee';

// Define input interface
interface Input {
    startUrls: { url: string }[];
    maxItems?: number;
    proxyConfig?: object;
    maxConcurrency?: number;
    navigationTimeoutSecs?: number;
    headless?: boolean;
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

log.info('Starting Puppeteer Crawler', {
    startUrls: input.startUrls.length,
    maxItems: input.maxItems || 'unlimited',
    headless: input.headless ?? true,
});

// Create proxy configuration
const proxyConfiguration = await Actor.createProxyConfiguration(input.proxyConfig);

// Initialize the crawler
const crawler = new PuppeteerCrawler({
    proxyConfiguration,
    maxRequestsPerCrawl: input.maxItems || undefined,
    maxConcurrency: input.maxConcurrency || 5,
    navigationTimeoutSecs: input.navigationTimeoutSecs || 60,

    // Browser launch options
    launchContext: {
        launchOptions: {
            headless: input.headless ?? true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ],
        },
    },

    async requestHandler({ page, request, enqueueLinks, log }) {
        log.info(`Processing ${request.url}`);

        // Wait for network to be idle
        await page.waitForNetworkIdle({ idleTime: 500 });

        // ============================================
        // TODO: Wait for specific content if needed
        // ============================================
        // await page.waitForSelector('.content', { timeout: 30000 });

        // ============================================
        // TODO: Handle interactions if needed
        // ============================================
        // await page.click('button.load-more');
        // await page.type('input[name="search"]', 'query');

        // ============================================
        // TODO: Implement your scraping logic here
        // ============================================

        // Example: Extract page title
        const title = await page.title();

        // Example: Extract data using page.evaluate
        const data = await page.evaluate(() => {
            const items = Array.from(document.querySelectorAll('.item, .product, .card'));
            return items.map(el => ({
                name: el.querySelector('h2, .title, .name')?.textContent?.trim(),
                description: el.querySelector('p, .description')?.textContent?.trim(),
                link: el.querySelector('a')?.getAttribute('href'),
            })).filter(item => item.name);
        });

        // Example: Get page metrics (Puppeteer-specific)
        const metrics = await page.metrics();

        // Save data to dataset
        await Dataset.pushData({
            url: request.url,
            title,
            itemCount: data.length,
            items: data,
            metrics: {
                jsHeapUsedSize: metrics.JSHeapUsedSize,
                documents: metrics.Documents,
            },
            scrapedAt: new Date().toISOString(),
        });

        // ============================================
        // TODO: Configure pagination/link following
        // ============================================

        // Example: Follow pagination links
        // await enqueueLinks({
        //     selector: 'a.next-page',
        //     label: 'PAGINATION',
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
