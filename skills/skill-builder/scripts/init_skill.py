#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path>

Examples:
    init_skill.py my-new-skill --path ~/.claude/skills
    init_skill.py n8n-workflow --path ./skills
"""

import sys
from pathlib import Path


SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Clear explanation of what this skill does and WHEN to use it. Include trigger scenarios, file types, or keywords. Max 1024 chars.]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Workflow

[TODO: Define the main workflow. Choose a pattern:

**Workflow-Based** (sequential processes)
1. Step one → description
2. Step two → description

**Task-Based** (tool collections)
### Task A
[instructions]
### Task B
[instructions]

**Reference-Based** (standards/guidelines)
### Guidelines
### Specifications
]

## Resources

- `scripts/` → Executable code for automation
- `references/` → Documentation loaded on-demand
- `assets/` → Templates and files for output

Delete unused directories.
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example script for {skill_name}
Replace with actual implementation or delete if not needed.
"""

def main():
    print("Example script for {skill_name}")
    # TODO: Add implementation

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference for {skill_title}

[TODO: Add detailed documentation here]

## When to Use References

- API documentation
- Complex workflow guides  
- Information too long for SKILL.md
- Content needed only for specific use cases
"""


def title_case_skill_name(skill_name):
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def init_skill(skill_name, path):
    skill_dir = Path(path).expanduser().resolve() / skill_name

    if skill_dir.exists():
        print(f"❌ Error: Directory exists: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created: {skill_dir}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    try:
        (skill_dir / 'SKILL.md').write_text(skill_content)
        print("✅ Created SKILL.md")

        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        script_file = scripts_dir / 'example.py'
        script_file.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
        script_file.chmod(0o755)
        print("✅ Created scripts/example.py")

        refs_dir = skill_dir / 'references'
        refs_dir.mkdir(exist_ok=True)
        (refs_dir / 'reference.md').write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
        print("✅ Created references/reference.md")

        assets_dir = skill_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        print("✅ Created assets/")

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    print(f"\n✅ Skill '{skill_name}' initialized at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md - complete TODOs and description")
    print("2. Add scripts/references/assets as needed")
    print("3. Run quick_validate.py to check")
    print("4. Run package_skill.py to create .skill file")

    return skill_dir


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: init_skill.py <skill-name> --path <path>")
        print("\nExamples:")
        print("  init_skill.py my-skill --path ~/.claude/skills")
        print("  init_skill.py n8n-workflow --path ./skills")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    print(f"🚀 Initializing: {skill_name}")
    print(f"   Path: {path}\n")

    result = init_skill(skill_name, path)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
