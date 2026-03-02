#!/usr/bin/env python3
"""
Diagnose CMS to WWW content sync issues.
Usage: python diagnose-sync.py --slug pricing
"""

import argparse
import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_pass(msg):
    print(f"{GREEN}✓ PASS{RESET}: {msg}")

def check_fail(msg):
    print(f"{RED}✗ FAIL{RESET}: {msg}")

def check_warn(msg):
    print(f"{YELLOW}⚠ WARN{RESET}: {msg}")

def check_info(msg):
    print(f"{BLUE}ℹ INFO{RESET}: {msg}")

def fetch_json(url):
    """Fetch JSON from URL."""
    try:
        req = Request(url, headers={'Accept': 'application/json'})
        with urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        return {'error': f'HTTP {e.code}', 'status': e.code}
    except URLError as e:
        return {'error': str(e.reason), 'status': 0}
    except Exception as e:
        return {'error': str(e), 'status': 0}

def fetch_html(url):
    """Fetch HTML from URL."""
    try:
        req = Request(url)
        with urlopen(req, timeout=10) as response:
            return response.read().decode(), response.status
    except HTTPError as e:
        return None, e.code
    except URLError as e:
        return None, 0
    except Exception as e:
        return None, 0

def main():
    parser = argparse.ArgumentParser(description='Diagnose CMS content sync')
    parser.add_argument('--slug', default='home', help='Page slug to check')
    parser.add_argument('--cms-url', default='http://localhost:3030', help='CMS URL')
    parser.add_argument('--www-url', default='http://localhost:3000', help='WWW URL')
    args = parser.parse_args()

    print("=" * 50)
    print("CMS Content Sync Diagnosis")
    print("=" * 50)
    print(f"\nSlug: {args.slug}")
    print(f"CMS: {args.cms_url}")
    print(f"WWW: {args.www_url}\n")

    issues = []

    # 1. Check CMS is accessible
    print("1. Checking CMS accessibility...")
    cms_data = fetch_json(f"{args.cms_url}/api/pages?limit=1")
    if 'error' in cms_data:
        check_fail(f"CMS not accessible: {cms_data['error']}")
        issues.append("CMS is not running or not accessible")
        print("\n→ Start CMS: pnpm dev --filter cms")
        return 1
    check_pass("CMS is accessible")

    # 2. Check page exists in CMS
    print("\n2. Checking page exists in CMS...")
    page_url = f"{args.cms_url}/api/pages?where[slug][equals]={args.slug}&depth=2"
    page_data = fetch_json(page_url)

    if 'error' in page_data:
        check_fail(f"API error: {page_data['error']}")
        issues.append("CMS API returned an error")
    elif page_data.get('totalDocs', 0) == 0:
        check_fail(f"Page '{args.slug}' not found in CMS")
        issues.append(f"Page '{args.slug}' does not exist in CMS")
        print(f"\n→ Create page with slug '{args.slug}' in CMS admin")
    else:
        check_pass(f"Page '{args.slug}' found in CMS")
        page = page_data['docs'][0]

        # Check status
        status = page.get('_status', 'unknown')
        if status == 'published':
            check_pass(f"Page status: {status}")
        else:
            check_warn(f"Page status: {status} (not published)")
            issues.append("Page is not published")

        # Check blocks
        blocks = page.get('content', [])
        check_info(f"Page has {len(blocks)} content blocks")
        for i, block in enumerate(blocks):
            block_type = block.get('blockType', 'unknown')
            print(f"    Block {i+1}: {block_type}")

    # 3. Check WWW is accessible
    print("\n3. Checking WWW accessibility...")
    www_html, www_status = fetch_html(args.www_url)
    if www_status != 200:
        check_fail(f"WWW not accessible (HTTP {www_status})")
        issues.append("WWW is not running or not accessible")
        print("\n→ Start WWW: pnpm dev --filter www")
    else:
        check_pass("WWW is accessible")

    # 4. Check page renders on WWW
    print("\n4. Checking page renders on WWW...")
    page_path = '/' if args.slug == 'home' else f'/{args.slug}'
    www_page_url = f"{args.www_url}{page_path}"
    page_html, page_status = fetch_html(www_page_url)

    if page_status == 200:
        check_pass(f"Page renders at {page_path}")

        # Check for common content
        if page_html:
            # Check for hero section (common block)
            if 'hero' in page_html.lower() or 'headline' in page_html.lower():
                check_info("Page contains hero-like content")
            # Check for error messages
            if '404' in page_html or 'not found' in page_html.lower():
                check_warn("Page may show 404 content")
                issues.append("Page shows 404-like content")
    elif page_status == 404:
        check_fail(f"Page returns 404 at {page_path}")
        issues.append("Page returns 404 on frontend")
    else:
        check_fail(f"Page returns HTTP {page_status}")
        issues.append(f"Page returns HTTP {page_status}")

    # 5. Compare CMS content with WWW render
    print("\n5. Content comparison...")
    if page_data.get('docs') and page_html:
        page = page_data['docs'][0]
        title = page.get('title', '')

        if title and title.lower() in page_html.lower():
            check_pass(f"Title '{title}' found in rendered page")
        else:
            check_warn(f"Title '{title}' not found in rendered HTML")
            issues.append("Page title not found in rendered content - possible sync issue")

        # Check first hero headline if exists
        blocks = page.get('content', [])
        for block in blocks:
            if block.get('blockType') == 'hero':
                headline = block.get('headline', '')
                if headline and headline in page_html:
                    check_pass(f"Hero headline found in page")
                else:
                    check_warn(f"Hero headline '{headline[:30]}...' not found")
                    issues.append("Hero headline not rendering - check BlockRenderer")
                break

    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSIS SUMMARY")
    print("=" * 50)

    if not issues:
        print(f"\n{GREEN}✓ No issues detected!{RESET}")
        print("Content appears to be syncing correctly.")
    else:
        print(f"\n{RED}Found {len(issues)} issue(s):{RESET}")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

        print("\nRecommended actions:")
        if "CMS is not running" in str(issues):
            print("  → pnpm dev --filter cms")
        if "WWW is not running" in str(issues):
            print("  → pnpm dev --filter www")
        if "not published" in str(issues):
            print("  → Publish page in CMS admin")
        if "404" in str(issues):
            print("  → Check catch-all route: apps/www/pages/[[...slug]].tsx")
        if "sync issue" in str(issues):
            print("  → Clear cache: rm -rf apps/www/.next/cache")
            print("  → Restart WWW: pnpm dev --filter www")

    return 0 if not issues else 1

if __name__ == '__main__':
    sys.exit(main())
