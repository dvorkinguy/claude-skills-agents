---
name: multi-brand-router
description: Route leads to the correct brand (guydvorkin, exportarena, afarsemon) based on language, source, geography, and campaign data. Use when user says "route this lead", "which brand", "brand detection", "assign brand", or when building any lead intake that needs brand routing.
---

# Multi-Brand Router

Detect and assign the correct business brand to incoming leads based on language, source, geography, and campaign data -- implemented as a reusable n8n sub-workflow and decision logic.

## When to Use

- "Which brand should this lead go to?"
- "Route this lead to the right brand"
- "Set up brand routing for a new intake"
- "Lead came in without a brand, assign one"
- Building any new lead capture that needs brand detection

## Brand Definitions

| Brand | Domain | Market | Language | Focus |
|-------|--------|--------|----------|-------|
| guydvorkin.com | guydvorkin.com | Global (US/EU primary) | English | AI Workforce consulting, thought leadership |
| exportarena.com | exportarena.com | Global trade | English | AI for import/export, trade automation |
| afarsemon.com | afarsemon.com | Israel | Hebrew | AI solutions for Israeli businesses |

## Detection Rules (Priority Order)

### Rule 1: Manual Override (Highest Priority)

If `business_brand` is already set on the record, keep it. Manual assignment always wins.

```javascript
if (lead.business_brand && lead.business_brand !== '') {
  return lead.business_brand;
}
```

### Rule 2: Source Domain Detection

| Source Contains | Brand |
|----------------|-------|
| `guydvorkin` | guydvorkin.com |
| `exportarena` | exportarena.com |
| `afarsemon` | afarsemon.com |

```javascript
const source = (lead.source_url || lead.utm_source || lead.referrer || '').toLowerCase();
if (source.includes('guydvorkin')) return 'guydvorkin.com';
if (source.includes('exportarena')) return 'exportarena.com';
if (source.includes('afarsemon')) return 'afarsemon.com';
```

### Rule 3: Campaign/UTM Detection

Campaign naming convention: `{brand}_{vertical}_{offer}_{date}`

```javascript
const campaign = (lead.utm_campaign || lead.campaign_name || '').toLowerCase();
const brandPrefix = campaign.split('_')[0];
const brandMap = {
  'guydvorkin': 'guydvorkin.com', 'gd': 'guydvorkin.com',
  'exportarena': 'exportarena.com', 'ea': 'exportarena.com',
  'afarsemon': 'afarsemon.com', 'af': 'afarsemon.com'
};
if (brandMap[brandPrefix]) return brandMap[brandPrefix];
```

### Rule 4: ManyChat Page Detection

| ManyChat Page/Bot | Brand |
|-------------------|-------|
| Guy Dvorkin Facebook page | guydvorkin.com |
| Export Arena Facebook page | exportarena.com |
| Afarsemon Facebook page | afarsemon.com |
| Afarsemon Instagram | afarsemon.com |

### Rule 5: Language Detection

Hebrew text strongly indicates afarsemon.com.

```javascript
function detectHebrew(text) {
  if (!text) return false;
  // Hebrew Unicode range: \u0590-\u05FF
  const hebrewChars = (text.match(/[\u0590-\u05FF]/g) || []).length;
  const totalChars = text.replace(/\s/g, '').length;
  return totalChars > 0 && (hebrewChars / totalChars) > 0.3;
}

if (detectHebrew(lead.message || lead.notes || lead.name)) {
  return 'afarsemon.com';
}
```

### Rule 6: Arabic Detection

Arabic text may also indicate Israeli market (Arabic-speaking Israelis).

```javascript
function detectArabic(text) {
  if (!text) return false;
  const arabicChars = (text.match(/[\u0600-\u06FF]/g) || []).length;
  const totalChars = text.replace(/\s/g, '').length;
  return totalChars > 0 && (arabicChars / totalChars) > 0.3;
}

if (detectArabic(lead.message || lead.notes)) {
  return 'afarsemon.com'; // Israeli market
}
```

### Rule 7: Geography Detection

| Geography Signal | Brand |
|-----------------|-------|
| Phone +972 | afarsemon.com |
| IP geo: Israel | afarsemon.com |
| Email domain .co.il | afarsemon.com |
| Timezone Asia/Jerusalem | afarsemon.com |

```javascript
const phone = lead.phone || '';
const email = lead.email || '';
const geo = lead.geo_country || '';

if (phone.startsWith('+972') || phone.startsWith('972') || phone.startsWith('05')) {
  return 'afarsemon.com';
}
if (email.endsWith('.co.il') || email.endsWith('.org.il')) {
  return 'afarsemon.com';
}
if (geo === 'IL' || geo === 'Israel') {
  return 'afarsemon.com';
}
```

### Rule 8: Industry Detection

| Industry Keywords | Brand |
|------------------|-------|
| import, export, trade, customs, freight, logistics, shipping | exportarena.com |
| Everything else | guydvorkin.com |

```javascript
const industry = (lead.industry || lead.company_category || '').toLowerCase();
const tradeKeywords = ['import', 'export', 'trade', 'customs', 'freight', 'logistics', 'shipping', 'forwarding'];
if (tradeKeywords.some(k => industry.includes(k))) {
  return 'exportarena.com';
}
```

### Rule 9: Default

If no rule matched: `guydvorkin.com` (broadest brand, catches all).

## AI Classification (Fallback for Ambiguous Cases)

When heuristic rules are inconclusive, use Gemini Flash:

```
Classify this lead into one of three brands:
1. guydvorkin.com — Global AI workforce consulting (English)
2. exportarena.com — AI for import/export and trade (English)
3. afarsemon.com — AI for Israeli businesses (Hebrew)

Lead data:
- Name: {{name}}
- Email: {{email}}
- Message: {{message}}
- Source: {{source}}
- Location: {{location}}

Respond with just the domain: guydvorkin.com, exportarena.com, or afarsemon.com
```

## n8n Sub-Workflow

### Input

```json
{
  "name": "Lead name",
  "email": "lead@example.com",
  "phone": "+972-50-123-4567",
  "message": "Optional message or notes",
  "source_url": "https://exportarena.com/landing",
  "utm_campaign": "ea_logistics_webinar_2026",
  "geo_country": "IL",
  "industry": "Freight forwarding"
}
```

### Output

```json
{
  "brand": "exportarena.com",
  "detection_method": "utm_campaign",
  "confidence": "high",
  "sales_list_slug": "sales_exportarena"
}
```

### Workflow Structure

```
Sub-workflow Start
  → Code Node: Run detection rules 1-9 in order
  → If confidence == "low": AI Classification node
  → Code Node: Map brand to sales list slug
  → Return: brand, method, confidence, list slug
```

## CRM Actions After Routing

| Action | Details |
|--------|---------|
| Set `business_brand` on person | Attio MCP: update_record |
| Add to brand sales list | Attio MCP: manage-list-entry (add to correct list) |
| Tag with detection method | Note on record for audit |

### Sales List Slugs

| Brand | List Slug |
|-------|-----------|
| guydvorkin.com | `sales_3` |
| exportarena.com | `sales_exportarena` (create if needed) |
| afarsemon.com | `sales_afarsemon` (create if needed) |

## Quick Reference

| Task | Method |
|------|--------|
| Route a single lead | Run detection rules in order, first match wins |
| Detect Hebrew text | Check for Unicode range \u0590-\u05FF > 30% of text |
| Map campaign to brand | Parse first segment of campaign name |
| Assign brand in CRM | Attio MCP: update_record + manage-list-entry |
| Override brand | Set business_brand manually, takes highest priority |
| Build into new intake | Call multi-brand-router as n8n sub-workflow |

## Testing Scenarios

| Input | Expected Brand | Rule |
|-------|---------------|------|
| Phone: +972-50-1234567 | afarsemon.com | Rule 7 (geo) |
| UTM: ea_logistics_q1 | exportarena.com | Rule 3 (campaign) |
| Message in Hebrew | afarsemon.com | Rule 5 (language) |
| Source: guydvorkin.com/blog | guydvorkin.com | Rule 2 (source) |
| Industry: "Customs brokerage" | exportarena.com | Rule 8 (industry) |
| No signals at all | guydvorkin.com | Rule 9 (default) |

## Error Handling

- All detection rules fail: default to guydvorkin.com, flag for manual review
- AI classification returns unexpected value: default to guydvorkin.com
- Sales list doesn't exist: create note on record, alert via Telegram
- Multiple brands match: use highest priority rule (lowest rule number wins)
- Brand field already set to invalid value: override with detected brand, note discrepancy
