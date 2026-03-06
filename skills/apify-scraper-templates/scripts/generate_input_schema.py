#!/usr/bin/env python3
"""
Generate an Apify Actor input_schema.json from a description.

Usage:
    python generate_input_schema.py "<description>" [--output <path>]

Examples:
    python generate_input_schema.py "Scrape product pages with URLs, max items, and proxy"
    python generate_input_schema.py "Crawl news sites with date range filter" --output ./input_schema.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


# Common field patterns and their configurations
FIELD_PATTERNS = {
    # URL-related
    r"url|urls|start.*url|link": {
        "name": "startUrls",
        "config": {
            "title": "Start URLs",
            "type": "array",
            "description": "URLs to start scraping from",
            "editor": "requestListSources",
            "prefill": [{"url": "https://example.com"}]
        },
        "required": True
    },

    # Limits
    r"max.*item|item.*limit|limit.*item|max.*result|result.*limit": {
        "name": "maxItems",
        "config": {
            "title": "Max Items",
            "type": "integer",
            "description": "Maximum number of items to scrape (0 = unlimited)",
            "default": 100,
            "minimum": 0
        }
    },
    r"max.*page|page.*limit|limit.*page": {
        "name": "maxPages",
        "config": {
            "title": "Max Pages",
            "type": "integer",
            "description": "Maximum number of pages to crawl",
            "default": 10,
            "minimum": 1
        }
    },
    r"max.*depth|crawl.*depth|depth": {
        "name": "maxCrawlDepth",
        "config": {
            "title": "Max Crawl Depth",
            "type": "integer",
            "description": "Maximum link depth to follow from start URLs",
            "default": 1,
            "minimum": 0
        }
    },

    # Proxy
    r"proxy|proxies": {
        "name": "proxyConfig",
        "config": {
            "title": "Proxy Configuration",
            "type": "object",
            "description": "Proxy settings for the scraper",
            "editor": "proxy",
            "default": {"useApifyProxy": True}
        }
    },

    # Date range
    r"date.*range|start.*date|from.*date|date.*from": {
        "name": "startDate",
        "config": {
            "title": "Start Date",
            "type": "string",
            "description": "Start date for filtering (YYYY-MM-DD)",
            "editor": "datepicker"
        }
    },
    r"end.*date|to.*date|date.*to|until": {
        "name": "endDate",
        "config": {
            "title": "End Date",
            "type": "string",
            "description": "End date for filtering (YYYY-MM-DD)",
            "editor": "datepicker"
        }
    },

    # Search/keywords
    r"search|query|keyword|term": {
        "name": "searchQuery",
        "config": {
            "title": "Search Query",
            "type": "string",
            "description": "Search query or keywords",
            "editor": "textfield"
        }
    },

    # Categories/filters
    r"categor|filter|type": {
        "name": "category",
        "config": {
            "title": "Category",
            "type": "string",
            "description": "Category or type filter",
            "editor": "textfield"
        }
    },

    # Location/country
    r"countr|location|region|geo": {
        "name": "country",
        "config": {
            "title": "Country",
            "type": "string",
            "description": "Country or region filter",
            "editor": "textfield",
            "prefill": "US"
        }
    },

    # Language
    r"language|lang|locale": {
        "name": "language",
        "config": {
            "title": "Language",
            "type": "string",
            "description": "Language code (e.g., en, es, de)",
            "editor": "textfield",
            "default": "en"
        }
    },

    # Debug/verbose
    r"debug|verbose": {
        "name": "debug",
        "config": {
            "title": "Debug Mode",
            "type": "boolean",
            "description": "Enable debug logging",
            "editor": "checkbox",
            "default": False
        }
    },

    # Wait/delay
    r"wait|delay|timeout|pause": {
        "name": "pageWaitMs",
        "config": {
            "title": "Page Wait (ms)",
            "type": "integer",
            "description": "Time to wait after page load in milliseconds",
            "default": 1000,
            "minimum": 0
        }
    },

    # CSS selectors
    r"selector|css|xpath": {
        "name": "customSelectors",
        "config": {
            "title": "Custom Selectors",
            "type": "object",
            "description": "Custom CSS selectors for data extraction",
            "editor": "json",
            "prefill": {"title": "h1", "price": ".price"}
        }
    },

    # Pagination
    r"pagination|next.*page|paging": {
        "name": "handlePagination",
        "config": {
            "title": "Handle Pagination",
            "type": "boolean",
            "description": "Automatically follow pagination links",
            "editor": "checkbox",
            "default": True
        }
    },

    # Output format
    r"output.*format|format|export": {
        "name": "outputFormat",
        "config": {
            "title": "Output Format",
            "type": "string",
            "description": "Format for output data",
            "editor": "select",
            "enum": ["json", "csv", "xlsx"],
            "default": "json"
        }
    },

    # Concurrency
    r"concurrent|parallel|thread": {
        "name": "maxConcurrency",
        "config": {
            "title": "Max Concurrency",
            "type": "integer",
            "description": "Maximum concurrent requests",
            "default": 5,
            "minimum": 1,
            "maximum": 100
        }
    },

    # Screenshots
    r"screenshot|capture|image": {
        "name": "saveScreenshots",
        "config": {
            "title": "Save Screenshots",
            "type": "boolean",
            "description": "Save screenshots of each page",
            "editor": "checkbox",
            "default": False
        }
    },

    # Login/auth
    r"login|auth|credential|user.*pass": {
        "name": "loginCredentials",
        "config": {
            "title": "Login Credentials",
            "type": "object",
            "description": "Credentials for authenticated scraping",
            "editor": "json",
            "prefill": {"username": "", "password": ""}
        }
    }
}


def detect_fields(description: str) -> List[Dict[str, Any]]:
    """Detect fields from description using pattern matching."""
    description_lower = description.lower()
    detected = []
    seen_names = set()

    for pattern, field_info in FIELD_PATTERNS.items():
        if re.search(pattern, description_lower):
            name = field_info["name"]
            if name not in seen_names:
                detected.append(field_info)
                seen_names.add(name)

    return detected


def generate_schema(description: str, title: str = "Scraper Input") -> Dict[str, Any]:
    """Generate an input schema from a description."""

    detected_fields = detect_fields(description)

    # Always include startUrls if no URL field detected
    has_urls = any(f["name"] == "startUrls" for f in detected_fields)
    if not has_urls:
        detected_fields.insert(0, FIELD_PATTERNS[r"url|urls|start.*url|link"])

    # Always include proxy if not detected
    has_proxy = any(f["name"] == "proxyConfig" for f in detected_fields)
    if not has_proxy:
        detected_fields.append(FIELD_PATTERNS[r"proxy|proxies"])

    # Build properties
    properties = {}
    required = []

    for field in detected_fields:
        name = field["name"]
        properties[name] = field["config"].copy()
        if field.get("required"):
            required.append(name)

    schema = {
        "title": title,
        "type": "object",
        "schemaVersion": 1,
        "properties": properties,
        "required": required if required else ["startUrls"]
    }

    return schema


def main():
    parser = argparse.ArgumentParser(
        description="Generate an Apify Actor input_schema.json from a description"
    )
    parser.add_argument(
        "description",
        help="Description of what the scraper needs (e.g., 'Scrape products with URL list, max items, and proxy')"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: prints to stdout)"
    )
    parser.add_argument(
        "--title", "-t",
        default="Scraper Input",
        help="Schema title (default: 'Scraper Input')"
    )

    args = parser.parse_args()

    schema = generate_schema(args.description, args.title)
    json_output = json.dumps(schema, indent=4)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json_output)
        print(f"Schema written to: {output_path}")
    else:
        print(json_output)

    # Print summary
    print(f"\n--- Summary ---", file=sys.stderr)
    print(f"Detected {len(schema['properties'])} properties:", file=sys.stderr)
    for name in schema['properties']:
        required_marker = "*" if name in schema.get('required', []) else ""
        print(f"  - {name}{required_marker}", file=sys.stderr)
    print(f"Required fields: {schema.get('required', [])}", file=sys.stderr)


if __name__ == "__main__":
    main()
