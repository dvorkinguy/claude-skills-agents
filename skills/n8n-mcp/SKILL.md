# n8n MCP Integration

Reference for n8n workflow automation with Export Arena.

## Overview

n8n is used for:
- Webhook handling and automation
- Integration with third-party services
- Lead routing and notifications
- Background processing

## Existing Skill

See `/n8n-workflow-builder` skill for workflow building guidance.

## n8n Instance

- **URL:** Self-hosted or n8n cloud
- **API:** REST API for programmatic access

## Environment Variables

```bash
# n8n API
N8N_API_URL=https://n8n.exportarena.com/api/v1
N8N_API_KEY=...

# Webhook Base URL
N8N_WEBHOOK_URL=https://n8n.exportarena.com/webhook
```

## Common Workflows

### Lead Capture Webhook

```typescript
// Trigger from chat widget
const response = await fetch(`${process.env.N8N_WEBHOOK_URL}/lead-capture`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: lead.name,
    email: lead.email,
    company: lead.company,
    source: 'chat_widget',
    message: lead.message,
    timestamp: new Date().toISOString(),
  }),
})
```

n8n workflow:
1. Receive webhook
2. Add to CRM (HubSpot/Pipedrive)
3. Send notification (Slack/Email)
4. Add to email sequence

### New User Onboarding

Trigger: Clerk webhook → n8n

1. Create CRM contact
2. Send welcome email
3. Add to onboarding sequence
4. Notify sales if qualified

### Subscription Events

Trigger: Stripe webhook → n8n

1. Update user status
2. Send confirmation email
3. Enable/disable features
4. Notify team of upgrades

### Port Monitor Alerts

Trigger: Port Monitor Agent

1. Check container status
2. Send email/SMS alert
3. Create task in project management
4. Log alert history

## API Integration

### Execute Workflow

```typescript
async function executeWorkflow(workflowId: string, data: any) {
  const response = await fetch(
    `${process.env.N8N_API_URL}/workflows/${workflowId}/execute`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-N8N-API-KEY': process.env.N8N_API_KEY!,
      },
      body: JSON.stringify({ data }),
    }
  )

  return response.json()
}
```

### List Workflows

```typescript
async function listWorkflows() {
  const response = await fetch(
    `${process.env.N8N_API_URL}/workflows`,
    {
      headers: {
        'X-N8N-API-KEY': process.env.N8N_API_KEY!,
      },
    }
  )

  return response.json()
}
```

## Webhook Security

### Signature Verification

```typescript
import crypto from 'crypto'

function verifyN8NWebhook(body: string, signature: string, secret: string): boolean {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(body)
    .digest('hex')

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  )
}
```

### API Route Handler

```typescript
export async function POST(req: Request) {
  const body = await req.text()
  const signature = req.headers.get('x-n8n-signature')

  if (!signature || !verifyN8NWebhook(body, signature, process.env.N8N_WEBHOOK_SECRET!)) {
    return new Response('Invalid signature', { status: 401 })
  }

  const data = JSON.parse(body)
  // Process webhook
}
```

## Common Nodes

### Used in Export Arena

| Node | Purpose |
|------|---------|
| Webhook | Receive data from app |
| HTTP Request | Call external APIs |
| Postgres | Database operations |
| Gmail/SMTP | Send emails |
| Slack | Team notifications |
| HubSpot | CRM integration |
| OpenAI | AI processing |
| If/Switch | Conditional logic |
| Set | Transform data |
| Merge | Combine data streams |

## Workflow Templates

### Lead Qualification

```json
{
  "nodes": [
    { "type": "n8n-nodes-base.webhook", "name": "Lead Webhook" },
    { "type": "n8n-nodes-base.set", "name": "Enrich Data" },
    { "type": "n8n-nodes-base.if", "name": "Check Score" },
    { "type": "n8n-nodes-base.hubspot", "name": "Create Contact" },
    { "type": "n8n-nodes-base.slack", "name": "Notify Sales" }
  ]
}
```

### Alert Router

```json
{
  "nodes": [
    { "type": "n8n-nodes-base.webhook", "name": "Alert Webhook" },
    { "type": "n8n-nodes-base.switch", "name": "Alert Type" },
    { "type": "n8n-nodes-base.gmail", "name": "Email Alert" },
    { "type": "n8n-nodes-base.slack", "name": "Slack Alert" },
    { "type": "n8n-nodes-base.twilio", "name": "SMS Alert" }
  ]
}
```

## Credentials Management

Store credentials in n8n:
- Stripe API Key
- OpenAI API Key
- SMTP Settings
- Slack Bot Token
- HubSpot API Key

## Error Handling

```typescript
// n8n Error Trigger workflow
// Monitors all workflow failures
// Sends notification on error

// In API: Check workflow execution status
const result = await executeWorkflow(workflowId, data)
if (result.status === 'error') {
  // Handle failure
  console.error('Workflow failed:', result.error)
}
```

## Best Practices

1. **Use environment variables** for all credentials
2. **Enable webhook authentication**
3. **Log all executions** for debugging
4. **Set up error notifications**
5. **Use retry logic** for external APIs
6. **Test with n8n CLI** locally
