#!/usr/bin/env python3
"""
Quick validation for Claude Code skills

Usage:
    quick_validate.py <skill-directory>
"""

import sys
import re
import yaml
from pathlib import Path


def validate_skill(skill_path):
    """Validate a skill directory. Returns (bool, message)."""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    
    # Check frontmatter exists
    if not content.startswith('---'):
        return False, "No YAML frontmatter (must start with ---)"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    # Parse YAML
    try:
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {e}"

    # Check allowed properties
    ALLOWED = {'name', 'description', 'license', 'allowed-tools', 'metadata'}
    unexpected = set(frontmatter.keys()) - ALLOWED
    if unexpected:
        return False, f"Unexpected keys: {', '.join(sorted(unexpected))}. Allowed: {', '.join(sorted(ALLOWED))}"

    # Validate name
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be string, got {type(name).__name__}"
    
    name = name.strip()
    if name:
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' must be hyphen-case (a-z, 0-9, hyphens)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or have consecutive hyphens"
        if len(name) > 64:
            return False, f"Name too long ({len(name)} chars). Max 64."

    # Validate description
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"
    
    desc = frontmatter.get('description', '')
    if not isinstance(desc, str):
        return False, f"Description must be string, got {type(desc).__name__}"
    
    desc = desc.strip()
    if desc:
        if '<' in desc or '>' in desc:
            return False, "Description cannot contain < or >"
        if len(desc) > 1024:
            return False, f"Description too long ({len(desc)} chars). Max 1024."

    return True, "✅ Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: quick_validate.py <skill-directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
