#!/usr/bin/env python3
"""
Validate an Apify Actor project configuration.

Usage:
    python validate_actor.py <actor-path>

Examples:
    python validate_actor.py ./my-scraper
    python validate_actor.py /path/to/actor
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def add_error(self, msg: str):
        self.errors.append(f"ERROR: {msg}")

    def add_warning(self, msg: str):
        self.warnings.append(f"WARNING: {msg}")

    def add_info(self, msg: str):
        self.info.append(f"INFO: {msg}")

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_report(self):
        print("\n" + "=" * 50)
        print("ACTOR VALIDATION REPORT")
        print("=" * 50)

        if self.info:
            print("\n[INFO]")
            for msg in self.info:
                print(f"  {msg}")

        if self.warnings:
            print("\n[WARNINGS]")
            for msg in self.warnings:
                print(f"  {msg}")

        if self.errors:
            print("\n[ERRORS]")
            for msg in self.errors:
                print(f"  {msg}")

        print("\n" + "-" * 50)
        if self.is_valid:
            print("RESULT: VALID")
            if self.warnings:
                print(f"  (with {len(self.warnings)} warning(s))")
        else:
            print(f"RESULT: INVALID ({len(self.errors)} error(s))")
        print("-" * 50 + "\n")


def validate_actor_json(actor_path: Path, result: ValidationResult) -> dict | None:
    """Validate actor.json configuration."""
    actor_json_path = actor_path / ".actor" / "actor.json"

    if not actor_json_path.exists():
        result.add_error(f"Missing required file: {actor_json_path}")
        return None

    try:
        with open(actor_json_path) as f:
            actor_json = json.load(f)
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON in actor.json: {e}")
        return None

    result.add_info(f"Found actor.json at {actor_json_path}")

    # Check required fields
    if actor_json.get("actorSpecification") != 1:
        result.add_error("actor.json must have 'actorSpecification': 1")

    if not actor_json.get("name"):
        result.add_error("actor.json missing required field: 'name'")
    else:
        result.add_info(f"Actor name: {actor_json['name']}")

    if not actor_json.get("version"):
        result.add_error("actor.json missing required field: 'version'")
    else:
        version = actor_json["version"]
        # Validate version format (Number.Number)
        parts = version.split(".")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            result.add_warning(f"Version '{version}' should be in format 'N.N' (e.g., '0.0', '1.0')")

    # Check optional but recommended fields
    if not actor_json.get("dockerfile"):
        result.add_warning("actor.json missing 'dockerfile' field (will search default locations)")

    if not actor_json.get("input"):
        result.add_warning("actor.json missing 'input' field (no input schema defined)")

    # Check memory settings
    min_mem = actor_json.get("minMemoryMbytes", 256)
    max_mem = actor_json.get("maxMemoryMbytes", 4096)
    if min_mem > max_mem:
        result.add_error(f"minMemoryMbytes ({min_mem}) cannot be greater than maxMemoryMbytes ({max_mem})")

    return actor_json


def validate_dockerfile(actor_path: Path, actor_json: dict | None, result: ValidationResult):
    """Validate Dockerfile exists and uses proper base image."""

    # Check possible Dockerfile locations
    dockerfile_path = None
    if actor_json and actor_json.get("dockerfile"):
        dockerfile_path = actor_path / ".actor" / actor_json["dockerfile"]
    else:
        # Check default locations
        possible_paths = [
            actor_path / ".actor" / "Dockerfile",
            actor_path / "Dockerfile"
        ]
        for path in possible_paths:
            if path.exists():
                dockerfile_path = path
                break

    if not dockerfile_path or not dockerfile_path.exists():
        result.add_error("Missing Dockerfile (checked .actor/Dockerfile and ./Dockerfile)")
        return

    result.add_info(f"Found Dockerfile at {dockerfile_path}")

    content = dockerfile_path.read_text()

    # Check for Apify base image
    if "FROM apify/" not in content:
        result.add_warning("Dockerfile does not use an Apify base image (apify/actor-*)")
    else:
        # Extract base image
        for line in content.split("\n"):
            if line.strip().startswith("FROM apify/"):
                result.add_info(f"Base image: {line.strip().replace('FROM ', '')}")
                break


def validate_input_schema(actor_path: Path, actor_json: dict | None, result: ValidationResult):
    """Validate input_schema.json if present."""

    schema_path = None
    if actor_json and actor_json.get("input"):
        input_ref = actor_json["input"]
        if isinstance(input_ref, str):
            schema_path = actor_path / ".actor" / input_ref
        elif isinstance(input_ref, dict):
            # Embedded schema
            result.add_info("Input schema is embedded in actor.json")
            return

    if not schema_path:
        schema_path = actor_path / ".actor" / "input_schema.json"

    if not schema_path.exists():
        result.add_warning("No input_schema.json found (Actor will have no input UI)")
        return

    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON in input_schema.json: {e}")
        return

    result.add_info(f"Found input schema at {schema_path}")

    # Validate schema structure
    if schema.get("schemaVersion") != 1:
        result.add_warning("Input schema should have 'schemaVersion': 1")

    if schema.get("type") != "object":
        result.add_error("Input schema 'type' must be 'object'")

    properties = schema.get("properties", {})
    if not properties:
        result.add_warning("Input schema has no properties defined")
    else:
        result.add_info(f"Input schema defines {len(properties)} properties")

    # Check for common fields
    if "startUrls" not in properties:
        result.add_info("Consider adding 'startUrls' property for URL input")

    # Validate each property
    valid_editors = [
        "textfield", "textarea", "json", "requestListSources", "proxy",
        "datepicker", "number", "checkbox", "select", "schemaBased",
        "javascript", "python", "hidden", "keyValueList", "stringList"
    ]

    for prop_name, prop_config in properties.items():
        editor = prop_config.get("editor")
        if editor and editor not in valid_editors:
            result.add_warning(f"Property '{prop_name}' has unknown editor '{editor}'")


def validate_package_json(actor_path: Path, result: ValidationResult):
    """Validate package.json for Node.js projects."""

    package_path = actor_path / "package.json"
    if not package_path.exists():
        result.add_warning("No package.json found (required for Node.js Actors)")
        return

    try:
        with open(package_path) as f:
            package = json.load(f)
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON in package.json: {e}")
        return

    result.add_info(f"Found package.json")

    # Check for required scripts
    scripts = package.get("scripts", {})
    if "start" not in scripts:
        result.add_error("package.json missing 'start' script")

    # Check for Apify/Crawlee dependencies
    deps = package.get("dependencies", {})
    if "apify" not in deps:
        result.add_warning("package.json missing 'apify' dependency")
    if "crawlee" not in deps:
        result.add_warning("package.json missing 'crawlee' dependency")

    # Detect crawler type
    if "playwright" in deps:
        result.add_info("Detected: PlaywrightCrawler project")
    elif "puppeteer" in deps:
        result.add_info("Detected: PuppeteerCrawler project")
    else:
        result.add_info("Detected: CheerioCrawler project (or custom)")


def validate_source_files(actor_path: Path, result: ValidationResult):
    """Check for main source files."""

    # Check for TypeScript or JavaScript entry point
    possible_entries = [
        actor_path / "src" / "main.ts",
        actor_path / "src" / "main.js",
        actor_path / "main.ts",
        actor_path / "main.js",
    ]

    found = False
    for entry in possible_entries:
        if entry.exists():
            result.add_info(f"Found entry point: {entry}")
            found = True
            break

    if not found:
        result.add_warning("No main entry point found (src/main.ts, src/main.js, etc.)")


def validate_actor(actor_path: str) -> Tuple[bool, ValidationResult]:
    """Main validation function."""

    result = ValidationResult()
    path = Path(actor_path).resolve()

    if not path.exists():
        result.add_error(f"Path does not exist: {path}")
        return False, result

    if not path.is_dir():
        result.add_error(f"Path is not a directory: {path}")
        return False, result

    result.add_info(f"Validating Actor at: {path}")

    # Check for .actor directory
    actor_dir = path / ".actor"
    if not actor_dir.exists():
        result.add_error("Missing .actor directory")
        return False, result

    # Run validations
    actor_json = validate_actor_json(path, result)
    validate_dockerfile(path, actor_json, result)
    validate_input_schema(path, actor_json, result)
    validate_package_json(path, result)
    validate_source_files(path, result)

    return result.is_valid, result


def main():
    parser = argparse.ArgumentParser(
        description="Validate an Apify Actor project configuration"
    )
    parser.add_argument("path", help="Path to the Actor directory")

    args = parser.parse_args()

    is_valid, result = validate_actor(args.path)
    result.print_report()

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
