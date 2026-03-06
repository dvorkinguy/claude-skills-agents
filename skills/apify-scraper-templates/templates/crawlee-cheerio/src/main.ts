/**
 * Cheerio Crawler Template
 *
 * Fast HTTP-based scraper for static HTML pages.
 * Best for: High-volume scraping of pages without JavaScript rendering.
 */

import { Actor } from 'apify';
import { CheerioCrawler, Dataset, log } from 'crawlee';

// Define input interface
interface Input {
    startUrls: { url: string }[];
    maxItems?: number;
    proxyConfig?: object;
    maxConcurrency?: number;
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

log.info('Starting Cheerio Crawler', {
    startUrls: input.startUrls.length,
    maxItems: input.maxItems || 'unlimited',
});

// Create proxy configuration
const proxyConfiguration = await Actor.createProxyConfiguration(input.proxyConfig);

// Initialize the crawler
const crawler = new CheerioCrawler({
    proxyConfiguration,
    maxRequestsPerCrawl: input.maxItems || undefined,
    maxConcurrency: input.maxConcurrency || 10,

    async requestHandler({ request, $, enqueueLinks, log }) {
        log.info(`Processing ${request.url}`);

        // ============================================
        // TODO: Implement your scraping logic here
        // ============================================

        // Example: Extract page title and links
        const title = $('h1').first().text().trim() || $('title').text().trim();

        // Example: Extract items from a list
        const items = $('.item, .product, .card')
            .map((_, el) => ({
                name: $(el).find('h2, .title, .name').text().trim(),
                description: $(el).find('p, .description').text().trim(),
                link: $(el).find('a').attr('href'),
            }))
            .get()
            .filter(item => item.name); // Filter empty items

        // Save data to dataset
        await Dataset.pushData({
            url: request.url,
            title,
            itemCount: items.length,
            items,
            scrapedAt: new Date().toISOString(),
        });

        // ============================================
        // TODO: Configure pagination/link following
        // ============================================

        // Example: Follow pagination links
        // await enqueueLinks({
        //     selector: 'a.next-page, .pagination a',
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
