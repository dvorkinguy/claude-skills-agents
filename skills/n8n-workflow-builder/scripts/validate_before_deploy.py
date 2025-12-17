#!/usr/bin/env python3
"""
n8n Workflow Validator - Pre-deployment validation script
Validates workflow JSON before deploying to n8n instance
"""

import json
import sys
import re
from pathlib import Path
from typing import Any

class WorkflowValidator:
    """Validates n8n workflow JSON files"""

    def __init__(self, workflow: dict):
        self.workflow = workflow
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """Run all validations"""
        self._validate_structure()
        self._validate_nodes()
        self._validate_connections()
        self._validate_expressions()
        self._validate_credentials()
        self._validate_ai_workflow()
        return len(self.errors) == 0

    def _validate_structure(self):
        """Validate basic workflow structure"""
        required_fields = ['name', 'nodes', 'connections']
        for field in required_fields:
            if field not in self.workflow:
                self.errors.append(f"Missing required field: {field}")

        if 'nodes' in self.workflow and not isinstance(self.workflow['nodes'], list):
            self.errors.append("'nodes' must be an array")

        if 'connections' in self.workflow and not isinstance(self.workflow['connections'], dict):
            self.errors.append("'connections' must be an object")

    def _validate_nodes(self):
        """Validate individual nodes"""
        nodes = self.workflow.get('nodes', [])
        node_names = set()
        has_trigger = False

        for i, node in enumerate(nodes):
            # Required node fields
            if 'name' not in node:
                self.errors.append(f"Node {i}: missing 'name'")
                continue

            name = node['name']

            if 'type' not in node:
                self.errors.append(f"Node '{name}': missing 'type'")

            if 'position' not in node:
                self.warnings.append(f"Node '{name}': missing 'position'")
            elif not isinstance(node['position'], list) or len(node['position']) != 2:
                self.errors.append(f"Node '{name}': position must be [x, y]")

            # Check for duplicate names
            if name in node_names:
                self.errors.append(f"Duplicate node name: '{name}'")
            node_names.add(name)

            # Check for trigger nodes
            node_type = node.get('type', '')
            if 'trigger' in node_type.lower() or node_type.endswith('Trigger'):
                has_trigger = True

            # Validate typeVersion
            if 'typeVersion' not in node:
                self.warnings.append(f"Node '{name}': missing 'typeVersion', may use default")

        if not has_trigger:
            self.warnings.append("No trigger node found - workflow won't start automatically")

    def _validate_connections(self):
        """Validate node connections"""
        connections = self.workflow.get('connections', {})
        node_names = {n['name'] for n in self.workflow.get('nodes', [])}

        for source_node, outputs in connections.items():
            if source_node not in node_names:
                self.errors.append(f"Connection from unknown node: '{source_node}'")
                continue

            if not isinstance(outputs, dict):
                self.errors.append(f"Invalid connection format for '{source_node}'")
                continue

            for output_type, connections_list in outputs.items():
                for conn_index, conn_array in enumerate(connections_list):
                    for conn in conn_array:
                        target = conn.get('node')
                        if target and target not in node_names:
                            self.errors.append(
                                f"Connection to unknown node: '{source_node}' -> '{target}'"
                            )

    def _validate_expressions(self):
        """Validate n8n expressions syntax"""
        expression_pattern = re.compile(r'\{\{.*?\}\}|\$\(.*?\)')

        def check_expressions(obj: Any, path: str = ""):
            if isinstance(obj, str):
                # Check for expression syntax
                if '{{' in obj or '$(' in obj:
                    # Basic validation - check for balanced braces
                    if obj.count('{{') != obj.count('}}'):
                        self.errors.append(f"Unbalanced {{{{ }}}} at {path}")
                    if obj.count('$(') != obj.count(')'):
                        self.warnings.append(f"Possible unbalanced $() at {path}")

                    # Check for common expression issues
                    if '$json' in obj and '$json.' not in obj and '$json[' not in obj:
                        self.warnings.append(f"$json without property access at {path}")
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    check_expressions(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_expressions(item, f"{path}[{i}]")

        check_expressions(self.workflow.get('nodes', []), 'nodes')

    def _validate_credentials(self):
        """Check for credential references"""
        nodes = self.workflow.get('nodes', [])

        for node in nodes:
            name = node.get('name', 'Unknown')
            params = node.get('parameters', {})

            # Check for hardcoded secrets
            param_str = json.dumps(params).lower()
            secret_patterns = ['password', 'api_key', 'apikey', 'secret', 'token']

            for pattern in secret_patterns:
                if pattern in param_str:
                    # Check if it's using env or credentials
                    if '$env.' not in param_str and 'credential' not in param_str:
                        self.warnings.append(
                            f"Node '{name}': possible hardcoded secret ({pattern})"
                        )

    def _validate_ai_workflow(self):
        """Validate AI agent workflow specifics"""
        nodes = self.workflow.get('nodes', [])
        connections = self.workflow.get('connections', {})

        ai_agent_nodes = [n for n in nodes if 'agent' in n.get('type', '').lower()]
        language_model_nodes = [n for n in nodes if 'languageModel' in n.get('type', '')]

        if ai_agent_nodes and not language_model_nodes:
            self.errors.append("AI Agent found but no Language Model node connected")

        # Check AI connection types (must flow TO the agent)
        for node in nodes:
            if 'agent' in node.get('type', '').lower():
                agent_name = node.get('name')
                has_lm_connection = False

                for source, outputs in connections.items():
                    for output_type, conns in outputs.items():
                        for conn_list in conns:
                            for conn in conn_list:
                                if conn.get('node') == agent_name:
                                    if conn.get('type') == 'ai_languageModel':
                                        has_lm_connection = True

                if not has_lm_connection and language_model_nodes:
                    self.warnings.append(
                        f"AI Agent '{agent_name}': Language Model not connected via ai_languageModel type"
                    )

        # Check tool descriptions (must be 15+ chars)
        for node in nodes:
            if node.get('type', '').startswith('@n8n/n8n-nodes-langchain.tool'):
                desc = node.get('parameters', {}).get('description', '')
                if len(desc) < 15:
                    self.errors.append(
                        f"Tool '{node.get('name')}': description must be 15+ characters for AI"
                    )

    def get_report(self) -> str:
        """Generate validation report"""
        lines = ["=" * 50, "n8n Workflow Validation Report", "=" * 50, ""]

        workflow_name = self.workflow.get('name', 'Unknown')
        lines.append(f"Workflow: {workflow_name}")
        lines.append(f"Nodes: {len(self.workflow.get('nodes', []))}")
        lines.append("")

        if self.errors:
            lines.append(f"ERRORS ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  [X] {error}")
            lines.append("")

        if self.warnings:
            lines.append(f"WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  [!] {warning}")
            lines.append("")

        if not self.errors and not self.warnings:
            lines.append("All checks passed!")

        status = "FAILED" if self.errors else ("WARNINGS" if self.warnings else "PASSED")
        lines.extend(["", "=" * 50, f"Status: {status}", "=" * 50])

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_before_deploy.py <workflow.json>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    try:
        with open(filepath) as f:
            workflow = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)

    validator = WorkflowValidator(workflow)
    is_valid = validator.validate()

    print(validator.get_report())

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
