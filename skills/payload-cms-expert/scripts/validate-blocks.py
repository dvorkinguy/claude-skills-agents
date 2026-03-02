#!/usr/bin/env python3
"""
Validate block configurations match between CMS and frontend.
Usage: python validate-blocks.py
"""

import os
import re
import sys
from pathlib import Path

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

def find_project_root():
    """Find the project root by looking for package.json with workspaces."""
    current = Path.cwd()
    while current != current.parent:
        if (current / 'package.json').exists() and (current / 'apps').exists():
            return current
        current = current.parent
    return Path.cwd()

def get_cms_blocks(cms_path):
    """Get list of blocks from CMS blocks directory."""
    blocks_dir = cms_path / 'src' / 'blocks'
    if not blocks_dir.exists():
        return []

    blocks = []
    for item in blocks_dir.iterdir():
        if item.is_dir():
            config_file = item / 'config.ts'
            if config_file.exists():
                content = config_file.read_text()
                # Extract slug from config
                match = re.search(r"slug:\s*['\"]([^'\"]+)['\"]", content)
                if match:
                    blocks.append({
                        'name': item.name,
                        'slug': match.group(1),
                        'path': str(config_file)
                    })
    return blocks

def get_pages_blocks(cms_path):
    """Get blocks registered in Pages collection."""
    pages_file = cms_path / 'src' / 'collections' / 'Pages' / 'index.ts'
    if not pages_file.exists():
        return []

    content = pages_file.read_text()
    # Find blocks array
    match = re.search(r'blocks:\s*\[([^\]]+)\]', content)
    if match:
        blocks_str = match.group(1)
        # Extract block names
        block_names = re.findall(r'\b([A-Z][a-zA-Z]+)\b', blocks_str)
        return block_names
    return []

def get_frontend_block_cases(www_path):
    """Get block cases from BlockRenderer."""
    renderer_file = www_path / 'components' / 'cms' / 'BlockRenderer.tsx'
    if not renderer_file.exists():
        return []

    content = renderer_file.read_text()

    # Try switch/case pattern first
    cases = re.findall(r"case\s+['\"]([^'\"]+)['\"]:", content)

    # Also try Record/object mapping pattern (e.g., `hero: HeroSection,`)
    if not cases:
        cases = re.findall(r"^\s*([a-zA-Z]+):\s*[A-Z][a-zA-Z]*Section", content, re.MULTILINE)

    return cases

def get_frontend_block_components(www_path):
    """Get frontend block components."""
    blocks_dir = www_path / 'components' / 'cms' / 'blocks'
    if not blocks_dir.exists():
        return []

    components = []
    for item in blocks_dir.iterdir():
        if item.is_file() and item.suffix in ['.tsx', '.ts']:
            name = item.stem
            if name.endswith('Section'):
                components.append(name)
    return components

def main():
    print("=" * 50)
    print("Block Configuration Validation")
    print("=" * 50)
    print()

    root = find_project_root()
    cms_path = root / 'apps' / 'cms'
    www_path = root / 'apps' / 'www'

    print(f"Project root: {root}")
    print(f"CMS path: {cms_path}")
    print(f"WWW path: {www_path}")
    print()

    issues = []

    # 1. Get CMS blocks
    print("1. Scanning CMS blocks...")
    cms_blocks = get_cms_blocks(cms_path)
    print(f"   Found {len(cms_blocks)} block configs:")
    for block in cms_blocks:
        print(f"     - {block['name']} (slug: {block['slug']})")

    # 2. Get Pages collection blocks
    print("\n2. Checking Pages collection...")
    pages_blocks = get_pages_blocks(cms_path)
    print(f"   Registered blocks: {', '.join(pages_blocks)}")

    # 3. Get frontend BlockRenderer cases
    print("\n3. Scanning BlockRenderer...")
    renderer_cases = get_frontend_block_cases(www_path)
    print(f"   Found {len(renderer_cases)} switch cases:")
    for case in renderer_cases:
        print(f"     - '{case}'")

    # 4. Get frontend components
    print("\n4. Scanning frontend components...")
    frontend_components = get_frontend_block_components(www_path)
    print(f"   Found {len(frontend_components)} block components:")
    for comp in frontend_components:
        print(f"     - {comp}")

    # Validation
    print("\n" + "=" * 50)
    print("VALIDATION RESULTS")
    print("=" * 50)

    # Check CMS blocks have frontend cases
    print("\n5. Checking CMS blocks have frontend handlers...")
    cms_slugs = [b['slug'] for b in cms_blocks]
    for block in cms_blocks:
        slug = block['slug']
        if slug in renderer_cases:
            check_pass(f"Block '{slug}' has frontend handler")
        else:
            check_fail(f"Block '{slug}' missing from BlockRenderer")
            issues.append(f"Add case '{slug}' to BlockRenderer.tsx")

    # Check Pages blocks are registered in config
    print("\n6. Checking Pages collection blocks...")
    cms_block_names = [b['name'] for b in cms_blocks]
    for name in pages_blocks:
        if name in cms_block_names:
            check_pass(f"Block '{name}' config exists")
        else:
            check_warn(f"Block '{name}' in Pages but no config found")

    # Check frontend cases have components
    print("\n7. Checking frontend components exist...")
    for case in renderer_cases:
        # Convert slug to component name (e.g., 'hero' -> 'HeroSection')
        expected_component = case.title().replace('_', '') + 'Section'
        if expected_component in frontend_components:
            check_pass(f"Component for '{case}' exists")
        else:
            check_warn(f"Component '{expected_component}' not found for case '{case}'")

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    print(f"\nCMS blocks: {len(cms_blocks)}")
    print(f"BlockRenderer cases: {len(renderer_cases)}")
    print(f"Frontend components: {len(frontend_components)}")

    if issues:
        print(f"\n{RED}Found {len(issues)} issue(s):{RESET}")
        for issue in issues:
            print(f"  → {issue}")
        return 1
    else:
        print(f"\n{GREEN}All blocks are properly configured!{RESET}")
        return 0

if __name__ == '__main__':
    sys.exit(main())
