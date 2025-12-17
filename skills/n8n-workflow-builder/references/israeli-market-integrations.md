# Israeli Market Integrations

Patterns for Israeli market: WhatsApp Business, Hebrew RTL, NIS payments.

## WhatsApp Business API

### Message Types

#### Text Message

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "972501234567",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "\u200Fשלום! איך אפשר לעזור לך היום?"
  }
}
```

#### Template Message (Pre-approved)

```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "template",
  "template": {
    "name": "order_confirmation",
    "language": {
      "code": "he"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {"type": "text", "text": "12345"},
          {"type": "text", "text": "₪299"}
        ]
      }
    ]
  }
}
```

#### Interactive Buttons

```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {
      "text": "\u200Fבחר אופציה:"
    },
    "action": {
      "buttons": [
        {"type": "reply", "reply": {"id": "opt1", "title": "אישור"}},
        {"type": "reply", "reply": {"id": "opt2", "title": "ביטול"}}
      ]
    }
  }
}
```

#### Interactive List

```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": {
      "text": "\u200Fבחר מהתפריט:"
    },
    "action": {
      "button": "הצג אפשרויות",
      "sections": [
        {
          "title": "שירותים",
          "rows": [
            {"id": "svc1", "title": "ייעוץ", "description": "פגישת ייעוץ ראשונית"},
            {"id": "svc2", "title": "תמיכה", "description": "תמיכה טכנית"}
          ]
        }
      ]
    }
  }
}
```

### n8n HTTP Request Node for WhatsApp

```json
{
  "name": "Send WhatsApp",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "=https://graph.facebook.com/v18.0/{{ $env.WHATSAPP_PHONE_ID }}/messages",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {"name": "Authorization", "value": "=Bearer {{ $env.WHATSAPP_ACCESS_TOKEN }}"},
        {"name": "Content-Type", "value": "application/json"}
      ]
    },
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {"name": "messaging_product", "value": "whatsapp"},
        {"name": "to", "value": "={{ $json.phone }}"},
        {"name": "type", "value": "text"},
        {"name": "text", "value": "={\"body\": \"\\u200F\" + $json.message}"}
      ]
    }
  }
}
```

### Rate Limits

| Tier | Messages/Day | Messages/Second | Requirements |
|------|-------------|-----------------|--------------|
| Unverified | 250 | 80 | New account |
| Verified | 1,000 | 80 | Business verification |
| Tier 1 | 10,000 | 80 | Quality rating |
| Tier 2 | 100,000 | 80 | Higher quality |
| Tier 3 | Unlimited | 80 | Best quality |

### Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 131047 | Re-engagement required | Use template message first |
| 131051 | Unsupported message type | Check message format |
| 131053 | Media upload failed | Check URL/size |
| 130429 | Rate limit hit | Implement backoff |
| 132000 | Template not found | Check template name/language |

---

## Hebrew RTL Handling

### Unicode Markers

```javascript
// Right-to-Left Mark (RLM) - forces RTL
const RTL_MARK = '\u200F';

// Left-to-Right Mark (LTM) - forces LTR
const LTR_MARK = '\u200E';

// Apply to Hebrew text
const hebrewText = RTL_MARK + "שלום עולם";

// Mixed content
const mixed = `${RTL_MARK}שלום ${LTR_MARK}John${RTL_MARK}!`;
```

### n8n Code Node for Hebrew

```javascript
// Process Hebrew text
const items = $input.all();

return items.map(item => {
  const text = item.json.message;

  // Add RTL marker for Hebrew
  const rtlText = '\u200F' + text;

  // Handle numbers (keep LTR)
  const withNumbers = rtlText.replace(/(\d+)/g, '\u200E$1\u200F');

  return {
    json: {
      ...item.json,
      formatted_message: withNumbers
    }
  };
});
```

### Common Hebrew Phrases

```json
{
  "greetings": {
    "hello": "\u200Fשלום",
    "good_morning": "\u200Fבוקר טוב",
    "good_evening": "\u200Fערב טוב",
    "goodbye": "\u200Fלהתראות"
  },
  "responses": {
    "thank_you": "\u200Fתודה רבה",
    "you_welcome": "\u200Fבבקשה",
    "sorry": "\u200Fסליחה",
    "understood": "\u200Fהבנתי"
  },
  "actions": {
    "confirm": "\u200Fאישור",
    "cancel": "\u200Fביטול",
    "continue": "\u200Fהמשך",
    "back": "\u200Fחזרה"
  },
  "status": {
    "processing": "\u200Fבטיפול",
    "completed": "\u200Fהושלם",
    "pending": "\u200Fממתין",
    "failed": "\u200Fנכשל"
  }
}
```

---

## Payment Integration

### Stripe with ILS

```json
{
  "name": "Create Stripe Checkout",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.stripe.com/v1/checkout/sessions",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpBasicAuth",
    "sendBody": true,
    "contentType": "form-urlencoded",
    "bodyParameters": {
      "parameters": [
        {"name": "payment_method_types[]", "value": "card"},
        {"name": "line_items[0][price_data][currency]", "value": "ils"},
        {"name": "line_items[0][price_data][unit_amount]", "value": "={{ $json.price * 100 }}"},
        {"name": "line_items[0][price_data][product_data][name]", "value": "={{ $json.product_name }}"},
        {"name": "line_items[0][quantity]", "value": "1"},
        {"name": "mode", "value": "payment"},
        {"name": "success_url", "value": "https://yoursite.com/success"},
        {"name": "cancel_url", "value": "https://yoursite.com/cancel"}
      ]
    }
  }
}
```

### Stripe Webhook Handler

```json
{
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "stripe-webhook",
    "responseMode": "onReceived"
  }
},
{
  "name": "Verify Stripe Signature",
  "type": "n8n-nodes-base.code",
  "parameters": {
    "jsCode": "const crypto = require('crypto');\nconst signature = $input.first().headers['stripe-signature'];\nconst payload = JSON.stringify($input.first().json);\nconst secret = $env.STRIPE_WEBHOOK_SECRET;\n\nconst elements = signature.split(',');\nconst timestamp = elements.find(e => e.startsWith('t=')).slice(2);\nconst sig = elements.find(e => e.startsWith('v1=')).slice(3);\n\nconst signedPayload = `${timestamp}.${payload}`;\nconst expected = crypto.createHmac('sha256', secret).update(signedPayload).digest('hex');\n\nif (sig !== expected) {\n  throw new Error('Invalid signature');\n}\n\nreturn $input.all();"
  }
}
```

### Israeli Payment Providers

#### PayPlus Integration

```json
{
  "name": "PayPlus Payment",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.payplus.co.il/payments",
    "authentication": "genericCredentialType",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {"name": "Authorization", "value": "={{ $env.PAYPLUS_API_KEY }}"},
        {"name": "Content-Type", "value": "application/json"}
      ]
    },
    "sendBody": true,
    "body": {
      "amount": "={{ $json.amount }}",
      "currency": "ILS",
      "description": "={{ $json.description }}",
      "customer": {
        "name": "={{ $json.customer_name }}",
        "email": "={{ $json.customer_email }}",
        "phone": "={{ $json.customer_phone }}"
      }
    }
  }
}
```

---

## Israeli SMS Providers

### Inforu (019)

```json
{
  "name": "Send SMS via Inforu",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.inforu.co.il/SendService/SendMessage",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {"name": "User", "value": "={{ $env.INFORU_USER }}"},
        {"name": "Password", "value": "={{ $env.INFORU_PASSWORD }}"},
        {"name": "SenderName", "value": "YourBrand"},
        {"name": "PhoneNumber", "value": "={{ $json.phone }}"},
        {"name": "Message", "value": "={{ $json.message }}"}
      ]
    }
  }
}
```

---

## Common Israeli Integrations

### Israeli CRM: Priority

```json
{
  "name": "Priority API",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://your-priority-server/odata/Priority/tabula.ini/company/CUSTOMERS",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpBasicAuth",
    "sendBody": true,
    "body": {
      "CUSTNAME": "={{ $json.customer_id }}",
      "CUSTDES": "={{ $json.customer_name }}",
      "PHONE": "={{ $json.phone }}",
      "EMAIL": "={{ $json.email }}"
    }
  }
}
```

### Israeli Accounting: Hashavshevet

```json
{
  "name": "Hashavshevet Invoice",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.hashavshevet.com/v1/invoices",
    "authentication": "genericCredentialType",
    "sendBody": true,
    "body": {
      "customer_id": "={{ $json.customer_id }}",
      "items": "={{ $json.items }}",
      "vat_included": true,
      "currency": "ILS"
    }
  }
}
```

---

## VAT Handling

Israeli VAT rate: **17%**

```javascript
// n8n Code Node for VAT calculation
const items = $input.all();

return items.map(item => {
  const priceWithoutVat = item.json.price;
  const vatRate = 0.17;
  const vatAmount = priceWithoutVat * vatRate;
  const totalPrice = priceWithoutVat + vatAmount;

  return {
    json: {
      ...item.json,
      price_without_vat: priceWithoutVat,
      vat_amount: vatAmount.toFixed(2),
      vat_rate: '17%',
      total_price: totalPrice.toFixed(2),
      currency: 'ILS',
      currency_symbol: '₪'
    }
  };
});
```

---

## Phone Number Formatting

```javascript
// Format Israeli phone numbers
function formatIsraeliPhone(phone) {
  // Remove all non-digits
  let cleaned = phone.replace(/\D/g, '');

  // Handle different formats
  if (cleaned.startsWith('972')) {
    return cleaned; // Already international
  }
  if (cleaned.startsWith('0')) {
    return '972' + cleaned.slice(1); // Convert local to international
  }
  return '972' + cleaned; // Assume local without leading 0
}

// Usage in n8n Code node
const items = $input.all();
return items.map(item => ({
  json: {
    ...item.json,
    formatted_phone: formatIsraeliPhone(item.json.phone)
  }
}));
```
