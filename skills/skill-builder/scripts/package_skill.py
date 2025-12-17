#!/usr/bin/env python3
"""
Skill Packager - Creates distributable .skill file

Usage:
    package_skill.py <skill-folder> [output-directory]

Examples:
    package_skill.py my-skill
    package_skill.py my-skill ./dist
"""

import sys
import zipfile
from pathlib import Path

# Import validation from same directory
from quick_validate import validate_skill


def package_skill(skill_path, output_dir=None):
    """Package a skill folder into a .skill file."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"❌ Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Not a directory: {skill_path}")
        return None

    if not (skill_path / "SKILL.md").exists():
        print(f"❌ SKILL.md not found in {skill_path}")
        return None

    # Validate first
    print("🔍 Validating...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ {message}")
        return None
    print(f"{message}\n")

    # Determine output
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create .skill (zip) file
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  + {arcname}")

        print(f"\n✅ Packaged: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: package_skill.py <skill-folder> [output-directory]")
        print("\nExamples:")
        print("  package_skill.py my-skill")
        print("  package_skill.py my-skill ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📦 Packaging: {skill_path}")
    if output_dir:
        print(f"   Output: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
