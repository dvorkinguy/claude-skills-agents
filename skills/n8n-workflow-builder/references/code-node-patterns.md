# Code Node Patterns

JavaScript patterns for n8n Code nodes.

## Data Access

### Access Input Data

```javascript
// All items
const items = $input.all();

// First item only
const first = $input.first();

// Item at index
const third = $input.item(2);

// Current item (in runOnceForEachItem mode)
const current = $input.item;
```

### Access JSON Data

```javascript
// From first item
const name = $input.first().json.name;

// In loop
const items = $input.all();
items.forEach(item => {
  console.log(item.json.email);
});

// Using $json shorthand (current item)
const value = $json.fieldName;
```

### Access Previous Node Output

```javascript
// Named node
const data = $('HTTP Request').first().json;

// All items from node
const allItems = $('Webhook').all();
```

---

## Return Formats

### Single Item

```javascript
return {
  json: {
    result: 'success',
    data: processedData
  }
};
```

### Multiple Items

```javascript
return [
  { json: { id: 1, name: 'First' } },
  { json: { id: 2, name: 'Second' } }
];
```

### Transform All Items

```javascript
const items = $input.all();

return items.map(item => ({
  json: {
    ...item.json,
    processed: true,
    timestamp: new Date().toISOString()
  }
}));
```

### Filter Items

```javascript
const items = $input.all();

return items
  .filter(item => item.json.status === 'active')
  .map(item => ({ json: item.json }));
```

---

## Common Transformations

### Rename Fields

```javascript
const items = $input.all();

return items.map(item => ({
  json: {
    id: item.json.user_id,
    fullName: item.json.name,
    email: item.json.email_address
  }
}));
```

### Merge Fields

```javascript
const items = $input.all();

return items.map(item => ({
  json: {
    ...item.json,
    fullName: `${item.json.firstName} ${item.json.lastName}`,
    address: `${item.json.street}, ${item.json.city}`
  }
}));
```

### Group By Field

```javascript
const items = $input.all();

const grouped = items.reduce((acc, item) => {
  const key = item.json.category;
  if (!acc[key]) acc[key] = [];
  acc[key].push(item.json);
  return acc;
}, {});

return Object.entries(grouped).map(([category, items]) => ({
  json: { category, items, count: items.length }
}));
```

### Aggregate/Sum

```javascript
const items = $input.all();

const total = items.reduce((sum, item) => sum + (item.json.amount || 0), 0);
const count = items.length;
const average = count > 0 ? total / count : 0;

return {
  json: {
    total,
    count,
    average: average.toFixed(2)
  }
};
```

### Flatten Nested Data

```javascript
const items = $input.all();

return items.flatMap(item =>
  item.json.orders.map(order => ({
    json: {
      userId: item.json.id,
      userName: item.json.name,
      orderId: order.id,
      orderAmount: order.amount
    }
  }))
);
```

---

## Date Handling

### Current Date/Time

```javascript
// ISO string
const now = new Date().toISOString();

// Unix timestamp
const timestamp = Date.now();

// Using Luxon (built-in)
const { DateTime } = require('luxon');
const nowLuxon = DateTime.now().toISO();
```

### Format Dates

```javascript
const { DateTime } = require('luxon');

const items = $input.all();

return items.map(item => ({
  json: {
    ...item.json,
    formatted_date: DateTime.fromISO(item.json.created_at)
      .toFormat('dd/MM/yyyy HH:mm')
  }
}));
```

### Date Calculations

```javascript
const { DateTime } = require('luxon');

const now = DateTime.now();
const yesterday = now.minus({ days: 1 }).toISO();
const nextWeek = now.plus({ weeks: 1 }).toISO();
const startOfMonth = now.startOf('month').toISO();
```

---

## HTTP Requests

### Using $helpers

```javascript
const response = await $helpers.httpRequest({
  method: 'GET',
  url: 'https://api.example.com/data',
  headers: {
    'Authorization': `Bearer ${$env.API_KEY}`
  }
});

return { json: response };
```

### POST Request

```javascript
const response = await $helpers.httpRequest({
  method: 'POST',
  url: 'https://api.example.com/endpoint',
  headers: {
    'Content-Type': 'application/json'
  },
  body: {
    name: $json.name,
    email: $json.email
  }
});

return { json: response };
```

---

## Error Handling

### Try-Catch

```javascript
try {
  const items = $input.all();

  const results = items.map(item => {
    if (!item.json.email) {
      throw new Error('Email is required');
    }
    return { json: { ...item.json, validated: true } };
  });

  return results;
} catch (error) {
  return {
    json: {
      error: true,
      message: error.message
    }
  };
}
```

### Validation

```javascript
const items = $input.all();

return items.map(item => {
  const errors = [];

  if (!item.json.email) errors.push('Email required');
  if (!item.json.name) errors.push('Name required');
  if (item.json.age && item.json.age < 18) errors.push('Must be 18+');

  return {
    json: {
      ...item.json,
      valid: errors.length === 0,
      errors: errors.length > 0 ? errors : undefined
    }
  };
});
```

---

## Environment Variables

```javascript
// Access env vars
const apiKey = $env.API_KEY;
const baseUrl = $env.BASE_URL;

// Use in request
const response = await $helpers.httpRequest({
  url: `${$env.BASE_URL}/api/data`,
  headers: {
    'Authorization': `Bearer ${$env.API_KEY}`
  }
});
```

---

## Workflow Context

```javascript
// Workflow info
const workflowId = $workflow.id;
const workflowName = $workflow.name;

// Execution info
const executionId = $execution.id;
const mode = $execution.mode; // 'test' or 'production'

// Current node
const nodeName = $node.name;
```

---

## Hebrew/RTL Handling

```javascript
const RTL_MARK = '\u200F';
const LTR_MARK = '\u200E';

const items = $input.all();

return items.map(item => ({
  json: {
    ...item.json,
    // Add RTL mark for Hebrew text
    hebrew_text: RTL_MARK + item.json.message,
    // Mixed content
    mixed: `${RTL_MARK}שלום ${LTR_MARK}${item.json.name}${RTL_MARK}!`
  }
}));
```

---

## Webhook Data Extraction

### Parse Webhook Body

```javascript
const webhookData = $input.first().json;

// Common webhook structures
const body = webhookData.body || webhookData;
const headers = webhookData.headers || {};
const query = webhookData.query || {};

return {
  json: {
    payload: body,
    contentType: headers['content-type'],
    queryParams: query
  }
};
```

### WhatsApp Webhook

```javascript
const data = $input.first().json;

// Extract message from WhatsApp webhook
const entry = data.entry?.[0];
const changes = entry?.changes?.[0];
const value = changes?.value;
const message = value?.messages?.[0];

if (!message) {
  return { json: { type: 'status_update', data: value } };
}

return {
  json: {
    type: 'message',
    from: message.from,
    messageId: message.id,
    timestamp: message.timestamp,
    messageType: message.type,
    text: message.text?.body || null,
    interactive: message.interactive || null
  }
};
```

---

## Binary Data

### Create Binary from Text

```javascript
const text = 'Hello, World!';
const binary = await $helpers.prepareBinaryData(
  Buffer.from(text),
  'hello.txt',
  'text/plain'
);

return {
  json: {},
  binary: { data: binary }
};
```

### Read Binary Data

```javascript
const binaryData = $input.first().binary.data;
const buffer = await $helpers.getBinaryDataBuffer(binaryData);
const text = buffer.toString('utf-8');

return { json: { content: text } };
```

---

## Deduplication

```javascript
const items = $input.all();

const seen = new Set();
const unique = items.filter(item => {
  const key = item.json.email; // Dedupe by email
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});

return unique.map(item => ({ json: item.json }));
```

---

## Pagination Handler

```javascript
// Collect all pages
const allResults = [];
let page = 1;
let hasMore = true;

while (hasMore) {
  const response = await $helpers.httpRequest({
    url: `https://api.example.com/items?page=${page}&limit=100`
  });

  allResults.push(...response.data);
  hasMore = response.has_more;
  page++;

  if (page > 10) break; // Safety limit
}

return allResults.map(item => ({ json: item }));
```
