#!/usr/bin/env python3
"""
Initialize a new Apify Actor project with Crawlee.

Usage:
    python init_actor.py <name> --type <cheerio|playwright|puppeteer> [--path <dir>]

Examples:
    python init_actor.py my-scraper --type cheerio
    python init_actor.py product-scraper --type playwright --path ./actors
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Templates for each crawler type
CRAWLER_TEMPLATES = {
    "cheerio": {
        "dependencies": {
            "apify": "^3.0.0",
            "crawlee": "^3.0.0"
        },
        "main_code": '''import { Actor } from 'apify';
import { CheerioCrawler, Dataset } from 'crawlee';

interface Input {
    startUrls: { url: string }[];
    maxItems?: number;
    proxyConfig?: object;
}

await Actor.init();

const input = await Actor.getInput<Input>();

if (!input?.startUrls?.length) {
    throw new Error('startUrls is required');
}

const proxyConfiguration = await Actor.createProxyConfiguration(input.proxyConfig);

const crawler = new CheerioCrawler({
    proxyConfiguration,
    maxRequestsPerCrawl: input.maxItems || 100,

    async requestHandler({ request, $, enqueueLinks, log }) {
        log.info(`Processing ${request.url}`);

        // TODO: Implement your scraping logic here
        const title = $('h1').text().trim();

        await Dataset.pushData({
            url: request.url,
            title,
            scrapedAt: new Date().toISOString(),
        });

        // TODO: Enqueue more links if needed
        // await enqueueLinks({ selector: 'a.next-page' });
    },

    failedRequestHandler({ request, log }) {
        log.error(`Request ${request.url} failed`);
    },
});

await crawler.run(input.startUrls.map(u => u.url));

await Actor.exit();
'''
    },
    "playwright": {
        "dependencies": {
            "apify": "^3.0.0",
            "crawlee": "^3.0.0",
            "playwright": "^1.40.0"
        },
        "main_code": '''import { Actor } from 'apify';
import { PlaywrightCrawler, Dataset } from 'crawlee';

interface Input {
    startUrls: { url: string }[];
    maxItems?: number;
    proxyConfig?: object;
}

await Actor.init();

const input = await Actor.getInput<Input>();

if (!input?.startUrls?.length) {
    throw new Error('startUrls is required');
}

const proxyConfiguration = await Actor.createProxyConfiguration(input.proxyConfig);

const crawler = new PlaywrightCrawler({
    proxyConfiguration,
    maxRequestsPerCrawl: input.maxItems || 100,

    async requestHandler({ page, request, enqueueLinks, log }) {
        log.info(`Processing ${request.url}`);

        // Wait for content to load
        await page.waitForLoadState('networkidle');

        // TODO: Implement your scraping logic here
        const title = await page.title();
        const content = await page.$eval('body', el => el.textContent?.trim().slice(0, 500));

        await Dataset.pushData({
            url: request.url,
            title,
            content,
            scrapedAt: new Date().toISOString(),
        });

        // TODO: Enqueue more links if needed
        // await enqueueLinks({ selector: 'a.next-page' });
    },

    failedRequestHandler({ request, log }) {
        log.error(`Request ${request.url} failed`);
    },
});

await crawler.run(input.startUrls.map(u => u.url));

await Actor.exit();
'''
    },
    "puppeteer": {
        "dependencies": {
            "apify": "^3.0.0",
            "crawlee": "^3.0.0",
            "puppeteer": "^21.0.0"
        },
        "main_code": '''import { Actor } from 'apify';
import { PuppeteerCrawler, Dataset } from 'crawlee';

interface Input {
    startUrls: { url: string }[];
    maxItems?: number;
    proxyConfig?: object;
}

await Actor.init();

const input = await Actor.getInput<Input>();

if (!input?.startUrls?.length) {
    throw new Error('startUrls is required');
}

const proxyConfiguration = await Actor.createProxyConfiguration(input.proxyConfig);

const crawler = new PuppeteerCrawler({
    proxyConfiguration,
    maxRequestsPerCrawl: input.maxItems || 100,
    launchContext: {
        launchOptions: {
            headless: true,
        },
    },

    async requestHandler({ page, request, enqueueLinks, log }) {
        log.info(`Processing ${request.url}`);

        // Wait for content to load
        await page.waitForNetworkIdle();

        // TODO: Implement your scraping logic here
        const title = await page.title();
        const content = await page.$eval('body', el => el.textContent?.trim().slice(0, 500));

        await Dataset.pushData({
            url: request.url,
            title,
            content,
            scrapedAt: new Date().toISOString(),
        });

        // TODO: Enqueue more links if needed
        // await enqueueLinks({ selector: 'a.next-page' });
    },

    failedRequestHandler({ request, log }) {
        log.error(`Request ${request.url} failed`);
    },
});

await crawler.run(input.startUrls.map(u => u.url));

await Actor.exit();
'''
    }
}

DOCKERFILE_TEMPLATE = '''FROM apify/actor-node:20

COPY package*.json ./

RUN npm --quiet set progress=false \\
    && npm install --omit=dev --omit=optional \\
    && echo "Installed NPM packages:" \\
    && npm list || true \\
    && echo "Node.js version:" \\
    && node --version \\
    && echo "NPM version:" \\
    && npm --version

COPY . ./

CMD npm start
'''

PLAYWRIGHT_DOCKERFILE = '''FROM apify/actor-node-playwright-chrome:20

COPY package*.json ./

RUN npm --quiet set progress=false \\
    && npm install --omit=dev --omit=optional \\
    && echo "Installed NPM packages:" \\
    && npm list || true \\
    && echo "Node.js version:" \\
    && node --version \\
    && echo "NPM version:" \\
    && npm --version

COPY . ./

CMD npm start
'''

PUPPETEER_DOCKERFILE = '''FROM apify/actor-node-puppeteer-chrome:20

COPY package*.json ./

RUN npm --quiet set progress=false \\
    && npm install --omit=dev --omit=optional \\
    && echo "Installed NPM packages:" \\
    && npm list || true \\
    && echo "Node.js version:" \\
    && node --version \\
    && echo "NPM version:" \\
    && npm --version

COPY . ./

CMD npm start
'''

INPUT_SCHEMA_TEMPLATE = {
    "title": "Scraper Input",
    "type": "object",
    "schemaVersion": 1,
    "properties": {
        "startUrls": {
            "title": "Start URLs",
            "type": "array",
            "description": "URLs to start scraping from",
            "editor": "requestListSources",
            "prefill": [{"url": "https://example.com"}]
        },
        "maxItems": {
            "title": "Max Items",
            "type": "integer",
            "description": "Maximum number of items to scrape (0 = unlimited)",
            "default": 100,
            "minimum": 0
        },
        "proxyConfig": {
            "title": "Proxy Configuration",
            "type": "object",
            "description": "Proxy settings for the scraper",
            "editor": "proxy",
            "default": {"useApifyProxy": True}
        }
    },
    "required": ["startUrls"]
}

TSCONFIG = {
    "compilerOptions": {
        "target": "ES2022",
        "module": "NodeNext",
        "moduleResolution": "NodeNext",
        "outDir": "dist",
        "rootDir": "src",
        "strict": True,
        "esModuleInterop": True,
        "skipLibCheck": True
    },
    "include": ["src/**/*"]
}


def create_actor_json(name: str) -> dict:
    return {
        "actorSpecification": 1,
        "name": name,
        "version": "0.0",
        "buildTag": "latest",
        "minMemoryMbytes": 256,
        "maxMemoryMbytes": 4096,
        "dockerfile": "./Dockerfile",
        "input": "./input_schema.json"
    }


def create_package_json(name: str, crawler_type: str) -> dict:
    template = CRAWLER_TEMPLATES[crawler_type]
    return {
        "name": name,
        "version": "0.0.1",
        "type": "module",
        "main": "dist/main.js",
        "scripts": {
            "start": "node dist/main.js",
            "build": "tsc",
            "dev": "tsc && node dist/main.js"
        },
        "dependencies": template["dependencies"],
        "devDependencies": {
            "typescript": "^5.0.0",
            "@types/node": "^20.0.0"
        }
    }


def init_actor(name: str, crawler_type: str, base_path: str = ".") -> None:
    """Initialize a new Apify Actor project."""

    # Validate crawler type
    if crawler_type not in CRAWLER_TEMPLATES:
        print(f"Error: Invalid crawler type '{crawler_type}'")
        print(f"Valid types: {', '.join(CRAWLER_TEMPLATES.keys())}")
        sys.exit(1)

    # Create project directory
    project_path = Path(base_path) / name
    if project_path.exists():
        print(f"Error: Directory '{project_path}' already exists")
        sys.exit(1)

    # Create directory structure
    (project_path / ".actor").mkdir(parents=True)
    (project_path / "src").mkdir()

    # Select Dockerfile based on crawler type
    if crawler_type == "playwright":
        dockerfile = PLAYWRIGHT_DOCKERFILE
    elif crawler_type == "puppeteer":
        dockerfile = PUPPETEER_DOCKERFILE
    else:
        dockerfile = DOCKERFILE_TEMPLATE

    # Write files
    files_to_create = {
        ".actor/actor.json": json.dumps(create_actor_json(name), indent=4),
        ".actor/input_schema.json": json.dumps(INPUT_SCHEMA_TEMPLATE, indent=4),
        ".actor/Dockerfile": dockerfile,
        "package.json": json.dumps(create_package_json(name, crawler_type), indent=4),
        "tsconfig.json": json.dumps(TSCONFIG, indent=4),
        "src/main.ts": CRAWLER_TEMPLATES[crawler_type]["main_code"],
    }

    for file_path, content in files_to_create.items():
        full_path = project_path / file_path
        full_path.write_text(content)
        print(f"Created: {full_path}")

    # Create .gitignore
    gitignore = """node_modules/
dist/
storage/
.env
*.log
"""
    (project_path / ".gitignore").write_text(gitignore)
    print(f"Created: {project_path / '.gitignore'}")

    print(f"\n Actor '{name}' initialized successfully!")
    print(f"\nNext steps:")
    print(f"  cd {project_path}")
    print(f"  npm install")
    print(f"  npm run build")
    print(f"  apify run --purge")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new Apify Actor project with Crawlee"
    )
    parser.add_argument("name", help="Actor name (used for directory and actor.json)")
    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=["cheerio", "playwright", "puppeteer"],
        help="Crawler type to use"
    )
    parser.add_argument(
        "--path", "-p",
        default=".",
        help="Base path where to create the Actor directory (default: current directory)"
    )

    args = parser.parse_args()
    init_actor(args.name, args.type, args.path)


if __name__ == "__main__":
    main()
