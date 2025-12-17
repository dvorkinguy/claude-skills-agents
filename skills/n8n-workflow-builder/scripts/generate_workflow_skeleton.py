#!/usr/bin/env python3
"""
n8n Workflow Skeleton Generator
Generates workflow JSON skeletons for common patterns
"""

import json
import sys
from datetime import datetime
from typing import Any

WORKFLOW_TYPES = {
    "webhook": "Webhook-triggered workflow",
    "schedule": "Scheduled/cron workflow",
    "whatsapp": "WhatsApp Business bot",
    "ai-agent": "AI Agent with tools",
    "lead-capture": "Lead capture to CRM",
    "rails-integration": "Rails app integration",
}

def create_node(name: str, node_type: str, position: list,
                params: dict = None, type_version: float = None) -> dict:
    """Create a node definition"""
    node = {
        "name": name,
        "type": node_type,
        "position": position,
        "parameters": params or {}
    }
    if type_version:
        node["typeVersion"] = type_version
    return node


def create_connection(source: str, target: str,
                     conn_type: str = "main", index: int = 0) -> dict:
    """Create a connection entry"""
    return {
        source: {
            conn_type: [[{"node": target, "type": conn_type, "index": index}]]
        }
    }


def merge_connections(*connection_dicts) -> dict:
    """Merge multiple connection dictionaries"""
    result = {}
    for conn in connection_dicts:
        for source, outputs in conn.items():
            if source not in result:
                result[source] = {}
            for output_type, conns in outputs.items():
                if output_type not in result[source]:
                    result[source][output_type] = []
                result[source][output_type].extend(conns)
    return result


def generate_webhook_workflow(name: str) -> dict:
    """Generate webhook-triggered workflow skeleton"""
    nodes = [
        create_node("Webhook", "n8n-nodes-base.webhook", [250, 300], {
            "httpMethod": "POST",
            "path": "webhook-path",
            "responseMode": "responseNode",
            "options": {}
        }, 2),
        create_node("Validate Input", "n8n-nodes-base.code", [450, 300], {
            "mode": "runOnceForAllItems",
            "jsCode": """// Validate incoming data
const data = $input.first().json;

if (!data.required_field) {
  throw new Error('Missing required_field');
}

return { json: { validated: true, ...data } };"""
        }, 2),
        create_node("Process Data", "n8n-nodes-base.code", [650, 300], {
            "mode": "runOnceForAllItems",
            "jsCode": """// Process the validated data
const data = $input.first().json;

// Add your processing logic here
const result = {
  processed: true,
  timestamp: new Date().toISOString(),
  data: data
};

return { json: result };"""
        }, 2),
        create_node("Respond to Webhook", "n8n-nodes-base.respondToWebhook", [850, 300], {
            "respondWith": "json",
            "responseBody": "={{ $json }}"
        }, 1),
    ]

    connections = merge_connections(
        create_connection("Webhook", "Validate Input"),
        create_connection("Validate Input", "Process Data"),
        create_connection("Process Data", "Respond to Webhook"),
    )

    return {"name": name, "nodes": nodes, "connections": connections}


def generate_schedule_workflow(name: str) -> dict:
    """Generate scheduled workflow skeleton"""
    nodes = [
        create_node("Schedule Trigger", "n8n-nodes-base.scheduleTrigger", [250, 300], {
            "rule": {
                "interval": [{"field": "hours", "hoursInterval": 1}]
            }
        }, 1.2),
        create_node("Fetch Data", "n8n-nodes-base.httpRequest", [450, 300], {
            "method": "GET",
            "url": "https://api.example.com/data",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth"
        }, 4.2),
        create_node("Transform", "n8n-nodes-base.code", [650, 300], {
            "mode": "runOnceForAllItems",
            "jsCode": """// Transform fetched data
const items = $input.all();

return items.map(item => ({
  json: {
    ...item.json,
    processedAt: new Date().toISOString()
  }
}));"""
        }, 2),
        create_node("Send Notification", "n8n-nodes-base.slack", [850, 300], {
            "resource": "message",
            "operation": "post",
            "channel": {"__rl": True, "mode": "name", "value": "#notifications"},
            "text": "=Scheduled task completed: {{ $json }}"
        }, 2.2),
    ]

    connections = merge_connections(
        create_connection("Schedule Trigger", "Fetch Data"),
        create_connection("Fetch Data", "Transform"),
        create_connection("Transform", "Send Notification"),
    )

    return {"name": name, "nodes": nodes, "connections": connections}


def generate_whatsapp_workflow(name: str) -> dict:
    """Generate WhatsApp bot workflow skeleton"""
    RTL = "\\u200F"

    nodes = [
        create_node("WhatsApp Webhook", "n8n-nodes-base.webhook", [250, 300], {
            "httpMethod": "POST",
            "path": "whatsapp-webhook",
            "responseMode": "responseNode"
        }, 2),
        create_node("Parse Message", "n8n-nodes-base.code", [450, 300], {
            "mode": "runOnceForAllItems",
            "jsCode": f"""// Parse WhatsApp webhook
const data = $input.first().json;
const entry = data.entry?.[0];
const changes = entry?.changes?.[0];
const value = changes?.value;
const message = value?.messages?.[0];

if (!message) {{
  return {{ json: {{ type: 'status_update', skip: true }} }};
}}

return {{
  json: {{
    from: message.from,
    phone_id: value.metadata.phone_number_id,
    message_id: message.id,
    type: message.type,
    text: message.text?.body
  }}
}};"""
        }, 2),
        create_node("Route Message", "n8n-nodes-base.switch", [650, 300], {
            "dataType": "string",
            "value1": "={{ $json.text }}",
            "rules": {
                "rules": [
                    {"value2": "שלום", "output": 0},
                    {"value2": "עזרה", "output": 1}
                ]
            },
            "fallbackOutput": 2
        }, 3),
        create_node("Send Response", "n8n-nodes-base.httpRequest", [850, 200], {
            "method": "POST",
            "url": "=https://graph.facebook.com/v18.0/{{ $json.phone_id }}/messages",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": f"""={{{{
  "messaging_product": "whatsapp",
  "to": "{{{{ $json.from }}}}",
  "type": "text",
  "text": {{ "body": "{RTL}שלום! איך אפשר לעזור?" }}
}}}}"""
        }, 4.2),
        create_node("Respond OK", "n8n-nodes-base.respondToWebhook", [1050, 300], {
            "respondWith": "text",
            "responseBody": "OK"
        }, 1),
    ]

    connections = merge_connections(
        create_connection("WhatsApp Webhook", "Parse Message"),
        create_connection("Parse Message", "Route Message"),
        {"Route Message": {"main": [
            [{"node": "Send Response", "type": "main", "index": 0}],
            [{"node": "Send Response", "type": "main", "index": 0}],
            [{"node": "Respond OK", "type": "main", "index": 0}]
        ]}},
        create_connection("Send Response", "Respond OK"),
    )

    return {"name": name, "nodes": nodes, "connections": connections}


def generate_ai_agent_workflow(name: str) -> dict:
    """Generate AI Agent workflow skeleton"""
    nodes = [
        create_node("Chat Trigger", "@n8n/n8n-nodes-langchain.chatTrigger", [250, 300], {
            "options": {}
        }, 1.1),
        create_node("OpenAI Chat Model", "@n8n/n8n-nodes-langchain.lmChatOpenAi", [450, 500], {
            "model": "gpt-4o-mini",
            "options": {"temperature": 0.7}
        }, 1.2),
        create_node("AI Agent", "@n8n/n8n-nodes-langchain.agent", [650, 300], {
            "agent": "conversationalAgent",
            "systemMessage": "You are a helpful assistant.",
            "options": {}
        }, 1.7),
        create_node("Calculator Tool", "@n8n/n8n-nodes-langchain.toolCalculator", [850, 500], {
            "description": "Performs mathematical calculations. Use for any math operations."
        }, 1),
    ]

    # AI connections flow TO the consumer
    connections = {
        "Chat Trigger": {"main": [[{"node": "AI Agent", "type": "main", "index": 0}]]},
        "OpenAI Chat Model": {"ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]},
        "Calculator Tool": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]}
    }

    return {"name": name, "nodes": nodes, "connections": connections}


def generate_lead_capture_workflow(name: str) -> dict:
    """Generate lead capture workflow skeleton"""
    nodes = [
        create_node("Lead Webhook", "n8n-nodes-base.webhook", [250, 300], {
            "httpMethod": "POST",
            "path": "lead-capture",
            "responseMode": "responseNode"
        }, 2),
        create_node("Validate Lead", "n8n-nodes-base.code", [450, 300], {
            "mode": "runOnceForAllItems",
            "jsCode": """// Validate lead data
const lead = $input.first().json;
const errors = [];

if (!lead.email || !lead.email.includes('@')) {
  errors.push('Invalid email');
}
if (!lead.name || lead.name.length < 2) {
  errors.push('Name required');
}

if (errors.length > 0) {
  throw new Error(errors.join(', '));
}

return { json: { valid: true, ...lead } };"""
        }, 2),
        create_node("Add to CRM", "n8n-nodes-base.httpRequest", [650, 300], {
            "method": "POST",
            "url": "={{ $env.CRM_API_URL }}/contacts",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": """={
  "email": "{{ $json.email }}",
  "name": "{{ $json.name }}",
  "phone": "{{ $json.phone }}",
  "source": "website"
}"""
        }, 4.2),
        create_node("Notify Sales", "n8n-nodes-base.slack", [850, 300], {
            "resource": "message",
            "operation": "post",
            "channel": {"__rl": True, "mode": "name", "value": "#sales-leads"},
            "text": "=:sparkles: New lead: {{ $json.name }} ({{ $json.email }})"
        }, 2.2),
        create_node("Respond Success", "n8n-nodes-base.respondToWebhook", [1050, 300], {
            "respondWith": "json",
            "responseBody": "={{ { success: true, message: 'Lead captured' } }}"
        }, 1),
    ]

    connections = merge_connections(
        create_connection("Lead Webhook", "Validate Lead"),
        create_connection("Validate Lead", "Add to CRM"),
        create_connection("Add to CRM", "Notify Sales"),
        create_connection("Notify Sales", "Respond Success"),
    )

    return {"name": name, "nodes": nodes, "connections": connections}


def generate_rails_integration_workflow(name: str) -> dict:
    """Generate Rails app integration workflow skeleton"""
    nodes = [
        create_node("Rails Webhook", "n8n-nodes-base.webhook", [250, 300], {
            "httpMethod": "POST",
            "path": "rails-webhook",
            "responseMode": "responseNode"
        }, 2),
        create_node("Verify Signature", "n8n-nodes-base.code", [450, 300], {
            "mode": "runOnceForAllItems",
            "jsCode": """// Verify Rails webhook signature
const crypto = require('crypto');
const payload = JSON.stringify($input.first().json);
const signature = $input.first().headers['x-webhook-signature'];
const secret = $env.RAILS_WEBHOOK_SECRET;

const expected = crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

if (signature !== expected) {
  throw new Error('Invalid signature');
}

return { json: { verified: true, ...$input.first().json } };"""
        }, 2),
        create_node("Route Event", "n8n-nodes-base.switch", [650, 300], {
            "dataType": "string",
            "value1": "={{ $json.event_type }}",
            "rules": {
                "rules": [
                    {"value2": "user.created", "output": 0},
                    {"value2": "order.completed", "output": 1}
                ]
            },
            "fallbackOutput": 2
        }, 3),
        create_node("Process Event", "n8n-nodes-base.code", [850, 300], {
            "mode": "runOnceForAllItems",
            "jsCode": """// Process the event
const event = $input.first().json;

return {
  json: {
    processed: true,
    event_type: event.event_type,
    result: 'Event processed successfully'
  }
};"""
        }, 2),
        create_node("Callback to Rails", "n8n-nodes-base.httpRequest", [1050, 300], {
            "method": "POST",
            "url": "={{ $env.RAILS_CALLBACK_URL }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": """={
  "execution_id": "{{ $execution.id }}",
  "status": "completed",
  "result": {{ JSON.stringify($json) }}
}"""
        }, 4.2),
        create_node("Respond", "n8n-nodes-base.respondToWebhook", [1250, 300], {
            "respondWith": "json",
            "responseBody": "={{ { received: true } }}"
        }, 1),
    ]

    connections = merge_connections(
        create_connection("Rails Webhook", "Verify Signature"),
        create_connection("Verify Signature", "Route Event"),
        {"Route Event": {"main": [
            [{"node": "Process Event", "type": "main", "index": 0}],
            [{"node": "Process Event", "type": "main", "index": 0}],
            [{"node": "Respond", "type": "main", "index": 0}]
        ]}},
        create_connection("Process Event", "Callback to Rails"),
        create_connection("Callback to Rails", "Respond"),
    )

    return {"name": name, "nodes": nodes, "connections": connections}


GENERATORS = {
    "webhook": generate_webhook_workflow,
    "schedule": generate_schedule_workflow,
    "whatsapp": generate_whatsapp_workflow,
    "ai-agent": generate_ai_agent_workflow,
    "lead-capture": generate_lead_capture_workflow,
    "rails-integration": generate_rails_integration_workflow,
}


def main():
    if len(sys.argv) < 2:
        print("n8n Workflow Skeleton Generator")
        print("=" * 40)
        print("\nUsage: python generate_workflow_skeleton.py <type> [name]")
        print("\nAvailable types:")
        for type_name, description in WORKFLOW_TYPES.items():
            print(f"  {type_name:20} - {description}")
        sys.exit(0)

    workflow_type = sys.argv[1].lower()
    workflow_name = sys.argv[2] if len(sys.argv) > 2 else f"Generated {workflow_type} workflow"

    if workflow_type not in GENERATORS:
        print(f"Error: Unknown workflow type '{workflow_type}'")
        print(f"Available: {', '.join(GENERATORS.keys())}")
        sys.exit(1)

    workflow = GENERATORS[workflow_type](workflow_name)
    workflow["meta"] = {
        "generatedAt": datetime.now().isoformat(),
        "generator": "n8n-workflow-skeleton-generator",
        "type": workflow_type
    }

    print(json.dumps(workflow, indent=2))


if __name__ == "__main__":
    main()
