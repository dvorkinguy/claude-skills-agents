---
name: ads-lead-capture
description: Capture leads from Meta, Google, and TikTok ad platforms into Attio CRM via n8n workflows. Use when user says "ad lead capture", "Facebook lead ads", "Google lead forms", "TikTok lead gen", "connect ads to CRM", or needs to set up ad-to-CRM pipelines.
---

# Ads Lead Capture

Capture leads from paid ad platforms (Meta Lead Ads, Google Ads Lead Forms, TikTok Lead Gen) and route them through validation, enrichment, scoring, and CRM upsert via n8n workflows.

## When to Use

- "Set up lead capture from Facebook/Meta ads"
- "Connect Google Ads to CRM"
- "TikTok lead gen integration"
- "Ad leads aren't syncing to Attio"
- "Track ad spend per lead" or "calculate CAC"
- Building any ad platform to CRM pipeline

## Platform Integration Patterns

### Meta Lead Ads (Facebook/Instagram)

**n8n Trigger Node:** `Facebook Lead Ads Trigger`

```json
{
  "node": "Facebook Lead Ads Trigger",
  "parameters": {
    "page": "={{$json.page_id}}",
    "form": "={{$json.form_id}}"
  },
  "credentials": {
    "facebookLeadAdsOAuth2Api": "Meta Ads"
  }
}
```

**Field Mapping:**
| Meta Field | CRM Field |
|-----------|-----------|
| `full_name` | Split to first_name + last_name |
| `email` | email_addresses |
| `phone_number` | phone_numbers |
| `company_name` | company association |
| `job_title` | job_title |
| Custom: "What's your biggest challenge?" | Note on record |

### Google Ads Lead Form Extensions

**n8n Trigger:** Webhook node (Google Ads sends to webhook URL)

```json
{
  "node": "Webhook",
  "parameters": {
    "path": "google-ads-lead",
    "httpMethod": "POST",
    "authentication": "headerAuth"
  }
}
```

**Google Ads Webhook Setup:**
1. Create lead form extension in Google Ads
2. Set webhook URL to n8n webhook endpoint
3. Add Google's webhook key for auth verification
4. Map: `user_column_data` array to CRM fields

### TikTok Lead Gen

**n8n Trigger:** Webhook node (TikTok Instant Form webhook)

```json
{
  "node": "Webhook",
  "parameters": {
    "path": "tiktok-lead",
    "httpMethod": "POST"
  }
}
```

**TikTok Field Mapping:**
| TikTok Field | CRM Field |
|-------------|-----------|
| `leads[].fields.name` | first_name + last_name |
| `leads[].fields.email` | email_addresses |
| `leads[].fields.phone_number` | phone_numbers |

## Common Workflow Pattern

```
Ad Platform Trigger/Webhook
  → Parse & Normalize Fields
    - Split full_name to first/last
    - Normalize phone (add country code)
    - Extract UTM parameters
  → Validate Email
    - Regex check
    - Disposable email detection
    - Skip if invalid (log reason)
  → Enrichment Sub-workflow
    - Google Search (Apify)
    - Perplexity Sonar research
    - Company enrichment
  → Lead Scoring Engine
    - Channel score: Ads = 10 points
    - Add ICP + enrichment scores
  → Upsert to Attio
    - Person record (match by email)
    - Set lead_source based on platform
    - Set business_brand based on campaign/UTM
  → Route by Brand
    - Multi-brand router sub-workflow
    - Add to correct sales list
  → Notify
    - Telegram: new lead captured with score
    - If Hot: immediate alert
```

## UTM Parameter Parsing

Extract attribution data from ad click URLs:

```javascript
// n8n Code Node: Parse UTMs
const url = new URL($input.item.json.landing_page_url || '');
const utm = {
  source: url.searchParams.get('utm_source'),      // facebook, google, tiktok
  medium: url.searchParams.get('utm_medium'),       // cpc, paid_social
  campaign: url.searchParams.get('utm_campaign'),   // campaign name
  content: url.searchParams.get('utm_content'),     // ad creative ID
  term: url.searchParams.get('utm_term')            // keyword (Google)
};

// Map source to lead_source enum
const sourceMap = {
  'facebook': 'Social Media',
  'instagram': 'Social Media',
  'google': 'Direct',
  'tiktok': 'Social Media'
};

return {
  ...utm,
  lead_source: sourceMap[utm.source] || 'Direct',
  campaign_name: utm.campaign
};
```

## Cost Tracking for CAC Calculation

### Data to Capture Per Lead

| Field | Source |
|-------|--------|
| `ad_platform` | UTM source or trigger type |
| `campaign_id` | UTM campaign or platform field |
| `ad_set_id` | Platform field |
| `ad_creative_id` | UTM content |
| `cost_per_lead` | Platform API (batch update daily) |

### Daily Cost Sync (n8n Workflow)

```
Schedule (daily 6am)
  → Meta Marketing API: get campaign spend by day
  → Google Ads API: get campaign cost by day
  → TikTok Ads API: get campaign cost by day
  → Calculate: total_spend / leads_captured = CPL
  → Store in Attio or Google Sheets for reporting
```

### CAC Formula

```
CAC = Total Ad Spend / Number of Customers Acquired
Target CAC: < $50 for SMB, < $200 for mid-market
```

## Retargeting Pixel Events

Fire pixel events at key conversion stages for ad platform optimization:

| Stage | Meta Pixel Event | Google Tag | TikTok Pixel |
|-------|-----------------|------------|--------------|
| Lead captured | `Lead` | `generate_lead` | `SubmitForm` |
| Lead qualified (score 60+) | `CompleteRegistration` | `sign_up` | `CompleteRegistration` |
| Proposal sent | `InitiateCheckout` | `begin_checkout` | `InitiateCheckout` |
| Deal won | `Purchase` | `purchase` | `PlaceAnOrder` |

### Implementation via n8n

```
Attio Webhook (deal stage changed)
  → Check new stage
  → If "qualified": fire Meta CAPI event, Google Offline Conversion
  → If "won": fire Purchase event with deal value
```

## Lead Source Mapping by Platform

| Platform | Campaign Naming Convention | Brand Detection |
|----------|--------------------------|-----------------|
| Meta | `{brand}_{vertical}_{offer}_{date}` | Extract from campaign name prefix |
| Google | `{brand}_{keyword_theme}_{match_type}` | Extract from campaign name prefix |
| TikTok | `{brand}_{content_type}_{audience}` | Extract from campaign name prefix |

## Quick Reference

| Task | Method |
|------|--------|
| Add Meta Lead Ads trigger | n8n: Facebook Lead Ads Trigger node |
| Add Google/TikTok trigger | n8n: Webhook node with platform-specific auth |
| Parse UTMs | Code node extracting URL search params |
| Track cost | Daily sync from platform APIs |
| Fire conversion events | n8n workflow on Attio stage change |

## Error Handling

- Invalid email: log to "rejected leads" sheet, do not upsert to CRM
- Duplicate lead: Attio upsert handles dedup by email, update existing record
- Webhook auth failure: return 401, alert via Telegram
- Enrichment timeout: upsert lead without enrichment, flag for re-enrichment
- Missing required fields: log partial data, create record with what's available
- Platform API rate limit: implement exponential backoff in n8n
