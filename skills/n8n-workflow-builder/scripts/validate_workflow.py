#!/usr/bin/env python3
"""Validate n8n workflow JSON structure."""
import json
import sys

def validate_workflow(filepath):
    with open(filepath, 'r') as f:
        workflow = json.load(f)

    errors = []

    # Check required fields
    if 'name' not in workflow:
        errors.append("Missing 'name' field")
    if 'nodes' not in workflow:
        errors.append("Missing 'nodes' field")
    if 'connections' not in workflow:
        errors.append("Missing 'connections' field")

    # Check nodes have required fields
    for i, node in enumerate(workflow.get('nodes', [])):
        if 'name' not in node:
            errors.append(f"Node {i}: missing 'name'")
        if 'type' not in node:
            errors.append(f"Node {i}: missing 'type'")
        if 'position' not in node:
            errors.append(f"Node {i}: missing 'position'")

    # Check for orphan nodes (no connections)
    connected_nodes = set()
    for source, targets in workflow.get('connections', {}).items():
        connected_nodes.add(source)
        for output in targets.values():
            for conn in output:
                connected_nodes.add(conn.get('node', ''))

    node_names = {n['name'] for n in workflow.get('nodes', [])}
    orphans = node_names - connected_nodes

    # Trigger nodes are allowed to be orphans
    trigger_types = ['webhook', 'schedule', 'manual']
    for node in workflow.get('nodes', []):
        if node['name'] in orphans:
            if not any(t in node.get('type', '').lower() for t in trigger_types):
                errors.append(f"Orphan node: {node['name']}")

    if errors:
        print("❌ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("✅ Workflow is valid")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_workflow.py <workflow.json>")
        sys.exit(1)

    valid = validate_workflow(sys.argv[1])
    sys.exit(0 if valid else 1)
