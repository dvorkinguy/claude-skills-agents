# Node Configuration Patterns

Common node configurations by category.

## Trigger Nodes

### Webhook Trigger

```json
{
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2,
  "position": [250, 300],
  "parameters": {
    "httpMethod": "POST",
    "path": "my-webhook",
    "authentication": "headerAuth",
    "responseMode": "onReceived",
    "options": {
      "rawBody": true
    }
  },
  "webhookId": "unique-id"
}
```

**Authentication Options:**
- `none` - No auth
- `basicAuth` - Basic authentication
- `headerAuth` - Custom header (X-API-Key, etc.)

**Response Modes:**
- `onReceived` - Respond immediately
- `lastNode` - Respond with last node output
- `responseNode` - Use Respond to Webhook node

### Schedule Trigger

```json
{
  "name": "Schedule Trigger",
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1.2,
  "position": [250, 300],
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 9 * * *"
        }
      ]
    }
  }
}
```

**Common Cron Expressions:**
- `0 9 * * *` - Daily at 9 AM
- `0 */2 * * *` - Every 2 hours
- `0 9 * * 1` - Monday at 9 AM
- `0 9 1 * *` - First of month at 9 AM

### Manual Trigger

```json
{
  "name": "Manual Trigger",
  "type": "n8n-nodes-base.manualTrigger",
  "typeVersion": 1,
  "position": [250, 300],
  "parameters": {}
}
```

---

## Data Processing Nodes

### Set Node

```json
{
  "name": "Set Fields",
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "position": [450, 300],
  "parameters": {
    "mode": "manual",
    "duplicateItem": false,
    "assignments": {
      "assignments": [
        {
          "name": "name",
          "value": "={{ $json.first_name }} {{ $json.last_name }}",
          "type": "string"
        },
        {
          "name": "timestamp",
          "value": "={{ $now.toISO() }}",
          "type": "string"
        }
      ]
    }
  }
}
```

### Code Node (JavaScript)

```json
{
  "name": "Transform Data",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [450, 300],
  "parameters": {
    "mode": "runOnceForAllItems",
    "jsCode": "const items = $input.all();\n\nreturn items.map(item => ({\n  json: {\n    ...item.json,\n    processed: true,\n    timestamp: new Date().toISOString()\n  }\n}));"
  }
}
```

**Modes:**
- `runOnceForAllItems` - Process all items at once
- `runOnceForEachItem` - Process each item separately

### IF Node

```json
{
  "name": "IF",
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "position": [450, 300],
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "strict"
      },
      "conditions": [
        {
          "leftValue": "={{ $json.status }}",
          "rightValue": "active",
          "operator": {
            "type": "string",
            "operation": "equals"
          }
        }
      ],
      "combinator": "and"
    }
  }
}
```

**Operators:**
- String: `equals`, `notEquals`, `contains`, `startsWith`, `endsWith`, `regex`
- Number: `equals`, `notEquals`, `gt`, `gte`, `lt`, `lte`
- Boolean: `true`, `false`
- Array: `contains`, `notContains`, `lengthEquals`, `lengthGt`, `lengthLt`

### Switch Node

```json
{
  "name": "Switch",
  "type": "n8n-nodes-base.switch",
  "typeVersion": 3,
  "position": [450, 300],
  "parameters": {
    "mode": "rules",
    "rules": {
      "rules": [
        {
          "output": 0,
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{ $json.type }}",
                "rightValue": "email",
                "operator": {"type": "string", "operation": "equals"}
              }
            ]
          }
        },
        {
          "output": 1,
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{ $json.type }}",
                "rightValue": "sms",
                "operator": {"type": "string", "operation": "equals"}
              }
            ]
          }
        }
      ],
      "fallbackOutput": 2
    }
  }
}
```

### Merge Node

```json
{
  "name": "Merge",
  "type": "n8n-nodes-base.merge",
  "typeVersion": 3,
  "position": [650, 300],
  "parameters": {
    "mode": "combine",
    "mergeByFields": {
      "values": [
        {"field1": "id", "field2": "user_id"}
      ]
    },
    "options": {}
  }
}
```

**Modes:**
- `append` - Append all items
- `combine` - Merge matching items
- `chooseBranch` - Select one branch

---

## Integration Nodes

### HTTP Request

```json
{
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [450, 300],
  "parameters": {
    "method": "POST",
    "url": "https://api.example.com/endpoint",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {"name": "Content-Type", "value": "application/json"}
      ]
    },
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ JSON.stringify($json) }}",
    "options": {
      "timeout": 30000,
      "response": {
        "response": {
          "responseFormat": "json"
        }
      }
    }
  }
}
```

**Authentication Types:**
- `none`
- `genericCredentialType` → `httpBasicAuth`, `httpHeaderAuth`, `oAuth2Api`
- `predefinedCredentialType` → Service-specific credentials

### Slack

```json
{
  "name": "Slack",
  "type": "n8n-nodes-base.slack",
  "typeVersion": 2.2,
  "position": [450, 300],
  "parameters": {
    "resource": "message",
    "operation": "post",
    "channel": {
      "__rl": true,
      "mode": "name",
      "value": "#general"
    },
    "text": "={{ $json.message }}",
    "otherOptions": {
      "mrkdwn": true
    }
  },
  "credentials": {
    "slackApi": {"id": "...", "name": "Slack"}
  }
}
```

### Google Sheets

```json
{
  "name": "Google Sheets",
  "type": "n8n-nodes-base.googleSheets",
  "typeVersion": 4.4,
  "position": [450, 300],
  "parameters": {
    "operation": "appendOrUpdate",
    "documentId": {
      "__rl": true,
      "mode": "url",
      "value": "https://docs.google.com/spreadsheets/d/..."
    },
    "sheetName": {
      "__rl": true,
      "mode": "name",
      "value": "Sheet1"
    },
    "columns": {
      "mappingMode": "autoMapInputData",
      "value": {}
    },
    "options": {
      "cellFormat": "USER_ENTERED"
    }
  },
  "credentials": {
    "googleSheetsOAuth2Api": {"id": "...", "name": "Google"}
  }
}
```

---

## Error Handling

### Error Trigger

```json
{
  "name": "Error Trigger",
  "type": "n8n-nodes-base.errorTrigger",
  "typeVersion": 1,
  "position": [250, 500],
  "parameters": {}
}
```

### Stop and Error

```json
{
  "name": "Stop and Error",
  "type": "n8n-nodes-base.stopAndError",
  "typeVersion": 1,
  "position": [650, 300],
  "parameters": {
    "errorMessage": "Validation failed: {{ $json.error }}"
  }
}
```

### No Operation (Placeholder)

```json
{
  "name": "No Operation",
  "type": "n8n-nodes-base.noOp",
  "typeVersion": 1,
  "position": [650, 300],
  "parameters": {}
}
```

---

## Response Nodes

### Respond to Webhook

```json
{
  "name": "Respond to Webhook",
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.1,
  "position": [850, 300],
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ $json }}",
    "options": {
      "responseCode": 200,
      "responseHeaders": {
        "entries": [
          {"name": "Content-Type", "value": "application/json"}
        ]
      }
    }
  }
}
```

---

## Utility Nodes

### Wait

```json
{
  "name": "Wait",
  "type": "n8n-nodes-base.wait",
  "typeVersion": 1.1,
  "position": [450, 300],
  "parameters": {
    "amount": 5,
    "unit": "seconds"
  }
}
```

### Date & Time

```json
{
  "name": "Date & Time",
  "type": "n8n-nodes-base.dateTime",
  "typeVersion": 2,
  "position": [450, 300],
  "parameters": {
    "operation": "format",
    "date": "={{ $json.created_at }}",
    "format": "custom",
    "customFormat": "dd/MM/yyyy HH:mm"
  }
}
```

### Split In Batches

```json
{
  "name": "Split In Batches",
  "type": "n8n-nodes-base.splitInBatches",
  "typeVersion": 3,
  "position": [450, 300],
  "parameters": {
    "batchSize": 10,
    "options": {}
  }
}
```

---

## Position Guidelines

Standard layout positions:
- Trigger: `[250, 300]`
- First processing: `[450, 300]`
- Second processing: `[650, 300]`
- Response/Output: `[850, 300]`
- Error branch: `[450, 500]` (below main flow)
- Parallel branches: Add 200 to Y position

Connections flow left to right, errors flow down.
