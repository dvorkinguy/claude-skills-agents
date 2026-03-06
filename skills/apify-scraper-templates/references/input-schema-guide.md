# Input Schema Guide

The input schema defines what parameters your Actor accepts and auto-generates a UI in Apify Console.

## Schema Structure

```json
{
    "title": "My Scraper Input",
    "type": "object",
    "schemaVersion": 1,
    "properties": {
        "propertyName": {
            "title": "Display Title",
            "type": "string",
            "description": "Tooltip text",
            "editor": "textfield",
            "default": "default value",
            "prefill": "example value"
        }
    },
    "required": ["propertyName"]
}
```

## Editor Types

### textfield
Single-line text input.

```json
{
    "name": {
        "title": "Name",
        "type": "string",
        "description": "Enter your name",
        "editor": "textfield",
        "prefill": "John Doe"
    }
}
```

### textarea
Multi-line text input.

```json
{
    "cssSelector": {
        "title": "CSS Selector",
        "type": "string",
        "description": "CSS selector for target elements",
        "editor": "textarea",
        "prefill": ".product-card h2"
    }
}
```

### requestListSources
URL list with labels, method, headers support.

```json
{
    "startUrls": {
        "title": "Start URLs",
        "type": "array",
        "description": "URLs to start scraping",
        "editor": "requestListSources",
        "prefill": [
            {"url": "https://example.com"},
            {"url": "https://example.com/page2", "method": "POST"}
        ]
    }
}
```

### proxy
Apify Proxy configuration.

```json
{
    "proxyConfig": {
        "title": "Proxy Configuration",
        "type": "object",
        "description": "Configure proxy settings",
        "editor": "proxy",
        "default": {
            "useApifyProxy": true,
            "apifyProxyGroups": ["RESIDENTIAL"]
        }
    }
}
```

### json
JSON object/array editor with syntax highlighting.

```json
{
    "customConfig": {
        "title": "Custom Configuration",
        "type": "object",
        "description": "Custom JSON configuration",
        "editor": "json",
        "prefill": {
            "timeout": 30000,
            "retries": 3
        }
    }
}
```

### select
Dropdown selection.

```json
{
    "country": {
        "title": "Country",
        "type": "string",
        "description": "Select target country",
        "editor": "select",
        "enum": ["US", "UK", "DE", "FR", "JP"],
        "enumTitles": ["United States", "United Kingdom", "Germany", "France", "Japan"],
        "default": "US"
    }
}
```

### checkbox
Boolean toggle.

```json
{
    "debugMode": {
        "title": "Debug Mode",
        "type": "boolean",
        "description": "Enable detailed logging",
        "editor": "checkbox",
        "default": false
    }
}
```

### number
Numeric input with min/max constraints.

```json
{
    "maxItems": {
        "title": "Max Items",
        "type": "integer",
        "description": "Maximum items to scrape",
        "editor": "number",
        "minimum": 1,
        "maximum": 10000,
        "default": 100
    }
}
```

### datepicker
Date selection.

```json
{
    "startDate": {
        "title": "Start Date",
        "type": "string",
        "description": "Filter from this date",
        "editor": "datepicker"
    }
}
```

### stringList
List of strings.

```json
{
    "keywords": {
        "title": "Keywords",
        "type": "array",
        "description": "List of search keywords",
        "editor": "stringList",
        "prefill": ["keyword1", "keyword2"]
    }
}
```

### keyValueList
List of key-value pairs.

```json
{
    "customHeaders": {
        "title": "Custom Headers",
        "type": "array",
        "description": "Additional HTTP headers",
        "editor": "keyValueList",
        "prefill": [
            {"key": "Accept", "value": "application/json"}
        ]
    }
}
```

### hidden
Hidden field (not shown in UI).

```json
{
    "internalConfig": {
        "title": "Internal Config",
        "type": "string",
        "editor": "hidden",
        "default": "internal-value"
    }
}
```

### javascript / python
Code editor with syntax highlighting.

```json
{
    "pageFunction": {
        "title": "Page Function",
        "type": "string",
        "description": "Custom extraction function",
        "editor": "javascript",
        "prefill": "async function pageFunction(context) {\n    return {};\n}"
    }
}
```

## Section Groups

Group related fields with `sectionCaption`:

```json
{
    "properties": {
        "startUrls": {
            "sectionCaption": "Input",
            "sectionDescription": "Configure data sources",
            "title": "Start URLs",
            "type": "array",
            "editor": "requestListSources"
        },
        "maxItems": {
            "title": "Max Items",
            "type": "integer"
        },
        "proxyConfig": {
            "sectionCaption": "Advanced",
            "sectionDescription": "Advanced settings",
            "title": "Proxy",
            "type": "object",
            "editor": "proxy"
        }
    }
}
```

## Conditional Fields

Show/hide fields based on other values:

```json
{
    "useCustomHeaders": {
        "title": "Use Custom Headers",
        "type": "boolean",
        "default": false
    },
    "customHeaders": {
        "title": "Custom Headers",
        "type": "array",
        "editor": "keyValueList",
        "conditions": {
            "showWhen": {
                "useCustomHeaders": true
            }
        }
    }
}
```

## Validation

### Required Fields
```json
{
    "required": ["startUrls", "maxItems"]
}
```

### String Patterns
```json
{
    "email": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    }
}
```

### Number Constraints
```json
{
    "timeout": {
        "type": "integer",
        "minimum": 1000,
        "maximum": 60000
    }
}
```

### Array Length
```json
{
    "urls": {
        "type": "array",
        "minItems": 1,
        "maxItems": 100
    }
}
```

## Complete Example

```json
{
    "title": "E-commerce Scraper",
    "type": "object",
    "schemaVersion": 1,
    "properties": {
        "startUrls": {
            "sectionCaption": "Input",
            "title": "Start URLs",
            "type": "array",
            "description": "Product listing pages to scrape",
            "editor": "requestListSources",
            "prefill": [{"url": "https://shop.example.com/products"}]
        },
        "maxItems": {
            "title": "Max Products",
            "type": "integer",
            "description": "Maximum products to scrape (0 = unlimited)",
            "default": 100,
            "minimum": 0
        },
        "category": {
            "title": "Category Filter",
            "type": "string",
            "description": "Filter by category",
            "editor": "select",
            "enum": ["all", "electronics", "clothing", "home"],
            "default": "all"
        },
        "proxyConfig": {
            "sectionCaption": "Proxy",
            "title": "Proxy Configuration",
            "type": "object",
            "description": "Proxy settings for avoiding blocks",
            "editor": "proxy",
            "default": {"useApifyProxy": true}
        },
        "debugMode": {
            "sectionCaption": "Advanced",
            "title": "Debug Mode",
            "type": "boolean",
            "description": "Enable detailed logging",
            "default": false
        }
    },
    "required": ["startUrls"]
}
```
