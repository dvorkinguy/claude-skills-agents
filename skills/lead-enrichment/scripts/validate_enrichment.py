#!/usr/bin/env python3
"""Validate enrichment output against the schema."""

import json
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets" / "enrichment-schema.json"

REQUIRED_FIELDS = [
    "company", "context", "lead_score", "icp_tier", "enrichment_notes"
]

VALID_TIERS = {"hot", "warm", "cold"}


def validate(data: dict) -> list[str]:
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if "lead_score" in data:
        score = data["lead_score"]
        if not isinstance(score, (int, float)) or score < 0 or score > 10:
            errors.append(f"lead_score must be 0-10, got: {score}")

    if "icp_tier" in data and data["icp_tier"] not in VALID_TIERS:
        errors.append(f"icp_tier must be one of {VALID_TIERS}, got: {data['icp_tier']}")

    for list_field in ["export_markets", "import_sources", "trade_products", "recent_news", "tech_stack", "decision_makers"]:
        if list_field in data and not isinstance(data[list_field], list):
            errors.append(f"{list_field} must be a list")

    if data.get("error"):
        errors.append(f"Enrichment error: {data['error']}")

    return errors


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    errors = validate(data)
    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print("VALID")
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
