#!/usr/bin/env python3
"""
Grafana Dashboard JSON Validator

Validates dashboard JSON structure, panels, and common issues.
Usage: python validate_dashboard.py <dashboard.json>
"""

import json
import sys
from pathlib import Path
from typing import Any


class DashboardValidator:
    """Validates Grafana dashboard JSON."""

    def __init__(self, dashboard: dict):
        self.dashboard = dashboard
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """Run all validations. Returns True if valid."""
        self._validate_structure()
        self._validate_panels()
        self._validate_datasources()
        self._validate_variables()
        self._validate_time_settings()
        return len(self.errors) == 0

    def _validate_structure(self):
        """Validate basic dashboard structure."""
        required_fields = ["title", "panels"]
        for field in required_fields:
            if field not in self.dashboard:
                self.errors.append(f"Missing required field: {field}")

        if "uid" not in self.dashboard:
            self.warnings.append("No UID set - will be auto-generated")

        if "schemaVersion" not in self.dashboard:
            self.warnings.append("No schemaVersion - may cause compatibility issues")

    def _validate_panels(self):
        """Validate panel configurations."""
        panels = self.dashboard.get("panels", [])

        if not panels:
            self.warnings.append("Dashboard has no panels")
            return

        panel_ids = []
        for i, panel in enumerate(panels):
            panel_id = panel.get("id")

            # Check for duplicate IDs
            if panel_id in panel_ids:
                self.errors.append(f"Duplicate panel ID: {panel_id}")
            elif panel_id is not None:
                panel_ids.append(panel_id)

            # Check panel type
            panel_type = panel.get("type")
            if not panel_type:
                self.errors.append(f"Panel {i} missing type")

            # Check for title
            if not panel.get("title"):
                self.warnings.append(f"Panel {panel_id or i} has no title")

            # Check for targets (queries)
            targets = panel.get("targets", [])
            if panel_type not in ["row", "text"] and not targets:
                self.warnings.append(f"Panel '{panel.get('title', i)}' has no queries")

            # Validate each target
            for j, target in enumerate(targets):
                self._validate_target(target, panel.get("title", f"Panel {i}"), j)

    def _validate_target(self, target: dict, panel_name: str, target_idx: int):
        """Validate query target."""
        # Check for datasource
        if "datasource" not in target:
            self.warnings.append(
                f"{panel_name} target {target_idx}: No datasource specified"
            )

        # Check for expression
        expr = target.get("expr") or target.get("query")
        if not expr:
            self.warnings.append(
                f"{panel_name} target {target_idx}: Empty query expression"
            )

    def _validate_datasources(self):
        """Validate datasource references."""
        datasources_used = set()

        # Collect from panels
        for panel in self.dashboard.get("panels", []):
            ds = panel.get("datasource")
            if ds and isinstance(ds, dict):
                datasources_used.add(ds.get("uid", ds.get("type", "unknown")))

            for target in panel.get("targets", []):
                ds = target.get("datasource")
                if ds and isinstance(ds, dict):
                    datasources_used.add(ds.get("uid", ds.get("type", "unknown")))

        if not datasources_used:
            self.warnings.append("No datasources referenced - using defaults")

    def _validate_variables(self):
        """Validate template variables."""
        templating = self.dashboard.get("templating", {})
        variables = templating.get("list", [])

        var_names = []
        for var in variables:
            name = var.get("name")
            if not name:
                self.errors.append("Variable without name found")
                continue

            if name in var_names:
                self.errors.append(f"Duplicate variable name: {name}")
            var_names.append(name)

            # Check for query variables without datasource
            if var.get("type") == "query" and not var.get("datasource"):
                self.warnings.append(f"Variable '{name}' has no datasource")

    def _validate_time_settings(self):
        """Validate time settings."""
        time = self.dashboard.get("time", {})
        if not time:
            self.warnings.append("No time range set - will use Grafana defaults")

        refresh = self.dashboard.get("refresh")
        if not refresh:
            self.warnings.append("No auto-refresh set")

    def report(self) -> str:
        """Generate validation report."""
        lines = [f"Dashboard: {self.dashboard.get('title', 'Untitled')}", ""]

        if self.errors:
            lines.append(f"ERRORS ({len(self.errors)}):")
            for err in self.errors:
                lines.append(f"  - {err}")
            lines.append("")

        if self.warnings:
            lines.append(f"WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings:
                lines.append(f"  - {warn}")
            lines.append("")

        if not self.errors and not self.warnings:
            lines.append("No issues found.")

        status = "INVALID" if self.errors else ("VALID (with warnings)" if self.warnings else "VALID")
        lines.append(f"\nStatus: {status}")

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_dashboard.py <dashboard.json>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    try:
        with open(filepath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)

    # Handle wrapped dashboard (from API response)
    dashboard = data.get("dashboard", data)

    validator = DashboardValidator(dashboard)
    is_valid = validator.validate()
    print(validator.report())

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
