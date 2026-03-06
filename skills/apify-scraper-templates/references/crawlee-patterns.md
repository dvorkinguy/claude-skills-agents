# Crawlee Patterns

Common patterns for building Apify Actors with Crawlee.

## Crawler Selection Guide

| Crawler | Best For | Memory | Speed |
|---------|----------|--------|-------|
| **CheerioCrawler** | Static HTML, APIs, high volume | Low | Fastest |
| **PlaywrightCrawler** | JS-rendered, modern browsers | High | Medium |
| **PuppeteerCrawler** | Chrome-specific, legacy | High | Medium |

## CheerioCrawler

Fast HTTP-based scraper using Cheerio (jQuery-like syntax).

### Basic Pattern

```typescript
import { Actor } from 'apify';
import { CheerioCrawler, Dataset, RequestQueue } from 'crawlee';

await Actor.init();

const input = await Actor.getInput<{
    startUrls: { url: string }[];
    maxItems?: number;
    proxyConfig?: object;
}>();

const proxyConfiguration = await Actor.createProxyConfiguration(input?.proxyConfig);

const crawler = new CheerioCrawler({
    proxyConfiguration,
    maxRequestsPerCrawl: input?.maxItems || 100,
    maxConcurrency: 10,

    async requestHandler({ request, $, enqueueLinks, log }) {
        log.info(`Scraping ${request.url}`);

        // Extract data using jQuery-like syntax
        const title = $('h1').text().trim();
        const items = $('.item').map((_, el) => ({
            name: $(el).find('.name').text(),
            price: $(el).find('.price').text(),
        })).get();

        await Dataset.pushData({
            url: request.url,
            title,
            items,
            scrapedAt: new Date().toISOString(),
        });

        // Follow pagination
        await enqueueLinks({
            selector: 'a.next-page',
            label: 'PAGINATION',
        });
    },
});

await crawler.run(input?.startUrls?.map(u => u.url) || []);
await Actor.exit();
```

### With Request Labels

```typescript
const crawler = new CheerioCrawler({
    async requestHandler({ request, $, enqueueLinks }) {
        const { label } = request.userData;

        if (label === 'LIST') {
            // Extract links from listing page
            await enqueueLinks({
                selector: '.product-link',
                label: 'DETAIL',
            });
            // Handle pagination
            await enqueueLinks({
                selector: 'a.next',
                label: 'LIST',
            });
        } else if (label === 'DETAIL') {
            // Extract product details
            await Dataset.pushData({
                url: request.url,
                title: $('h1').text(),
                price: $('.price').text(),
            });
        }
    },
});

// Start with labeled requests
await crawler.run([
    { url: 'https://shop.example.com/products', userData: { label: 'LIST' } }
]);
```

## PlaywrightCrawler

Full browser automation with Playwright.

### Basic Pattern

```typescript
import { Actor } from 'apify';
import { PlaywrightCrawler, Dataset } from 'crawlee';

await Actor.init();

const input = await Actor.getInput<{
    startUrls: { url: string }[];
    maxItems?: number;
    proxyConfig?: object;
}>();

const proxyConfiguration = await Actor.createProxyConfiguration(input?.proxyConfig);

const crawler = new PlaywrightCrawler({
    proxyConfiguration,
    maxRequestsPerCrawl: input?.maxItems || 100,
    maxConcurrency: 5, // Lower for browser crawlers
    navigationTimeoutSecs: 60,

    async requestHandler({ page, request, enqueueLinks, log }) {
        log.info(`Processing ${request.url}`);

        // Wait for dynamic content
        await page.waitForSelector('.product-list', { timeout: 30000 });

        // Scroll to load lazy content
        await page.evaluate(() => {
            window.scrollTo(0, document.body.scrollHeight);
        });
        await page.waitForTimeout(1000);

        // Extract data
        const products = await page.$$eval('.product', items =>
            items.map(item => ({
                title: item.querySelector('h2')?.textContent?.trim(),
                price: item.querySelector('.price')?.textContent?.trim(),
                image: item.querySelector('img')?.src,
            }))
        );

        for (const product of products) {
            await Dataset.pushData({
                url: request.url,
                ...product,
            });
        }

        // Follow links
        await enqueueLinks({
            selector: 'a.pagination-next',
        });
    },
});

await crawler.run(input?.startUrls?.map(u => u.url) || []);
await Actor.exit();
```

### With Screenshots

```typescript
import { Actor } from 'apify';
import { PlaywrightCrawler, KeyValueStore } from 'crawlee';

const crawler = new PlaywrightCrawler({
    async requestHandler({ page, request }) {
        // Take screenshot
        const screenshot = await page.screenshot({ fullPage: true });

        // Save to key-value store
        const key = request.url.replace(/[^a-zA-Z0-9]/g, '_');
        await KeyValueStore.setValue(`screenshot_${key}`, screenshot, {
            contentType: 'image/png',
        });

        // Continue with scraping...
    },
});
```

### Handling Infinite Scroll

```typescript
const crawler = new PlaywrightCrawler({
    async requestHandler({ page, request, log }) {
        let previousHeight = 0;
        let scrollAttempts = 0;
        const maxScrolls = 10;

        while (scrollAttempts < maxScrolls) {
            // Scroll to bottom
            await page.evaluate(() => {
                window.scrollTo(0, document.body.scrollHeight);
            });

            // Wait for new content
            await page.waitForTimeout(2000);

            const currentHeight = await page.evaluate(() => document.body.scrollHeight);

            if (currentHeight === previousHeight) {
                log.info('Reached end of infinite scroll');
                break;
            }

            previousHeight = currentHeight;
            scrollAttempts++;
        }

        // Now extract all loaded content
        const items = await page.$$eval('.item', /* ... */);
    },
});
```

## PuppeteerCrawler

Chrome-specific automation with Puppeteer.

### Basic Pattern

```typescript
import { Actor } from 'apify';
import { PuppeteerCrawler, Dataset } from 'crawlee';

await Actor.init();

const input = await Actor.getInput<{
    startUrls: { url: string }[];
}>();

const proxyConfiguration = await Actor.createProxyConfiguration(input?.proxyConfig);

const crawler = new PuppeteerCrawler({
    proxyConfiguration,
    maxConcurrency: 5,
    launchContext: {
        launchOptions: {
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
        },
    },

    async requestHandler({ page, request, log }) {
        log.info(`Processing ${request.url}`);

        await page.waitForNetworkIdle();

        const data = await page.evaluate(() => ({
            title: document.querySelector('h1')?.textContent,
            content: document.querySelector('.content')?.innerHTML,
        }));

        await Dataset.pushData({
            url: request.url,
            ...data,
        });
    },
});

await crawler.run(input?.startUrls?.map(u => u.url) || []);
await Actor.exit();
```

## Common Patterns

### Error Handling

```typescript
const crawler = new CheerioCrawler({
    maxRequestRetries: 3,

    async requestHandler({ request, $, log }) {
        // Your scraping logic
    },

    async failedRequestHandler({ request, log, error }) {
        log.error(`Request ${request.url} failed: ${error.message}`);

        // Save failed URL for debugging
        await Dataset.pushData({
            url: request.url,
            error: error.message,
            status: 'failed',
        });
    },
});
```

### Rate Limiting

```typescript
const crawler = new CheerioCrawler({
    maxConcurrency: 5,
    minConcurrency: 1,
    maxRequestsPerMinute: 60, // 1 request per second

    async requestHandler({ request, $, log }) {
        // Your scraping logic
    },
});
```

### Request Queue Management

```typescript
import { RequestQueue } from 'crawlee';

const requestQueue = await RequestQueue.open();

// Add requests with priority
await requestQueue.addRequest({
    url: 'https://example.com/important',
    userData: { priority: 1 },
});

// Add batch of requests
await requestQueue.addRequests([
    { url: 'https://example.com/page1' },
    { url: 'https://example.com/page2' },
]);

const crawler = new CheerioCrawler({
    requestQueue,
    // ...
});
```

### Custom Headers and Cookies

```typescript
const crawler = new CheerioCrawler({
    preNavigationHooks: [
        async ({ request }) => {
            request.headers = {
                ...request.headers,
                'Accept-Language': 'en-US,en;q=0.9',
                'User-Agent': 'Custom User Agent',
            };
        },
    ],

    async requestHandler({ request, $, session }) {
        // Set cookies for session
        session?.setCookies([
            { name: 'session', value: 'abc123', domain: 'example.com' },
        ], request.url);
    },
});
```

### Session Management

```typescript
import { SessionPool } from 'crawlee';

const sessionPool = await SessionPool.open({
    maxPoolSize: 100,
    sessionOptions: {
        maxUsageCount: 50, // Rotate after 50 uses
    },
});

const crawler = new CheerioCrawler({
    sessionPoolOptions: {
        maxPoolSize: 100,
    },
    useSessionPool: true,

    async requestHandler({ session, request }) {
        if (session?.isBlocked()) {
            session.retire();
            throw new Error('Session blocked, retrying with new session');
        }

        // Track successful requests
        session?.markGood();
    },
});
```

### Data Transformation

```typescript
const crawler = new CheerioCrawler({
    async requestHandler({ $, request }) {
        const rawPrice = $('.price').text(); // "$1,234.56"

        // Clean and transform data
        const cleanPrice = parseFloat(
            rawPrice.replace(/[$,]/g, '')
        );

        await Dataset.pushData({
            url: request.url,
            price: cleanPrice,
            currency: 'USD',
            scrapedAt: new Date().toISOString(),
        });
    },
});
```

### Exporting Data

```typescript
import { Dataset } from 'crawlee';

// At the end of crawl
const dataset = await Dataset.open();

// Get all data
const { items } = await dataset.getData();

// Export to key-value store
await Actor.setValue('OUTPUT', items);

// Or push final summary
await Dataset.pushData({
    type: 'summary',
    totalItems: items.length,
    completedAt: new Date().toISOString(),
});
```

## Performance Tips

1. **Use CheerioCrawler when possible** - 10x faster than browser crawlers
2. **Set appropriate maxConcurrency** - Start low (5-10), increase if stable
3. **Use session rotation** - Prevents IP blocks
4. **Enable proxy rotation** - `useApifyProxy: true` with residential proxies
5. **Filter unnecessary requests** - Block images, fonts, analytics
6. **Batch data pushes** - Collect items, push in batches of 100+
