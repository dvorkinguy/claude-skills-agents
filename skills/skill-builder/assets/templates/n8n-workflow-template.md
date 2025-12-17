---
name: n8n-workflow
description: Build n8n automation workflows with webhook handling, error management, and API integrations. Use when creating n8n nodes, workflows, webhook receivers, or debugging n8n automations.
---

# n8n Workflow Builder

## Quick Patterns

### Webhook Trigger
```json
{
  "nodes": [{
    "name": "Webhook",
    "type": "n8n-nodes-base.webhook",
    "parameters": {
      "httpMethod": "POST",
      "path": "your-endpoint",
      "responseMode": "onReceived"
    }
  }]
}
```

### Error Handling
Always include Error Trigger node:
```json
{
  "name": "Error Trigger",
  "type": "n8n-nodes-base.errorTrigger"
}
```

### HTTP Request
```json
{
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "={{ $json.url }}",
    "authentication": "genericCredentialType",
    "options": {
      "timeout": 30000
    }
  }
}
```

## Best Practices

1. **Error handling** - Always add error workflow
2. **Retries** - Set retry on failure for HTTP nodes
3. **Logging** - Add Set node to log key data points
4. **Credentials** - Never hardcode; use n8n credentials

## Common Integrations

- WhatsApp Business API
- Google Sheets
- Supabase
- OpenAI/Claude API

## References

See `references/n8n-nodes.md` for full node documentation.
