---
name: whatsapp-integration
description: Build WhatsApp Business API integrations with message templates, webhook handlers, and Hebrew/Arabic RTL support. Use when creating WhatsApp bots, sending messages, or processing WhatsApp webhooks.
---

# WhatsApp Business Integration

## Message Types

### Text Message
```json
{
  "messaging_product": "whatsapp",
  "to": "{{phone}}",
  "type": "text",
  "text": { "body": "שלום! 👋" }
}
```

### Template Message
```json
{
  "messaging_product": "whatsapp",
  "to": "{{phone}}",
  "type": "template",
  "template": {
    "name": "your_template",
    "language": { "code": "he" },
    "components": [{
      "type": "body",
      "parameters": [{ "type": "text", "text": "{{name}}" }]
    }]
  }
}
```

### Interactive Buttons
```json
{
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": { "text": "בחר אפשרות:" },
    "action": {
      "buttons": [
        { "type": "reply", "reply": { "id": "opt1", "title": "אפשרות 1" }},
        { "type": "reply", "reply": { "id": "opt2", "title": "אפשרות 2" }}
      ]
    }
  }
}
```

## Webhook Handler

```python
def handle_webhook(payload):
    entry = payload.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    
    # Handle incoming message
    if "messages" in value:
        msg = value["messages"][0]
        phone = msg["from"]
        text = msg.get("text", {}).get("body", "")
        return {"phone": phone, "text": text}
    
    # Handle status update
    if "statuses" in value:
        status = value["statuses"][0]
        return {"status": status["status"], "id": status["id"]}
```

## RTL Support (Hebrew/Arabic)

- Text automatically renders RTL
- For mixed content, use Unicode marks: `\u200F` (RTL) `\u200E` (LTR)
- Button titles: max 20 chars
- List items: max 24 chars

## Rate Limits

| Tier | Messages/day |
|------|-------------|
| Unverified | 250 |
| Verified | 1,000 |
| Tier 1 | 10,000 |
| Tier 2 | 100,000 |

## Error Codes

- 131047: Re-engagement required (24h window)
- 131051: Unsupported message type
- 130429: Rate limit exceeded
