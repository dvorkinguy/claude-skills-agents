---
name: sdr-bdr-automation
description: Automated SDR/BDR agent for prospect discovery, enrichment, multi-channel outreach, and meeting booking. Use when user says "automate prospecting", "SDR workflow", "BDR automation", "find and reach prospects", "automated outreach", or needs an end-to-end prospecting pipeline.
---

# SDR/BDR Automation

End-to-end automated sales development: discover prospects, enrich and score them, run multi-channel outreach (cold email, LinkedIn, WhatsApp), and book meetings -- all orchestrated via n8n workflows.

## When to Use

- "Automate my SDR process" or "build a prospecting pipeline"
- "Find and reach out to prospects automatically"
- "Multi-channel outreach automation"
- "I need an automated BDR"
- Setting up cold outreach at scale for any brand

## Pipeline Overview

```
Discovery → Enrichment → Scoring → Outreach → Follow-up → Meeting Booking
```

## Step 1: Prospect Discovery

### Sources

| Source | Tool | Best For |
|--------|------|----------|
| LinkedIn search | Apify `curious_coder/linkedin-search-scraper` | Job title + industry targeting |
| Google Maps | Apify `compass/crawler-google-places` | Local businesses by category |
| Industry directories | Apify `web-scraper` | Niche B2B lists |
| Google search | Apify `apify/google-search-scraper` | "CEO" + "logistics" + "company" |
| Existing CRM (stale leads) | Attio API filter | Re-engage cold leads |

### Discovery Queries by Vertical

```javascript
const queries = {
  logistics: '"logistics company" OR "freight forwarder" OR "supply chain" CEO OR founder site:linkedin.com/in/',
  manufacturing: '"manufacturing" OR "factory" OR "production" CEO OR "operations manager" site:linkedin.com/in/',
  professional_services: '"consulting firm" OR "accounting firm" OR "law firm" managing partner site:linkedin.com/in/',
  import_export: '"import export" OR "international trade" OR "customs broker" CEO OR owner site:linkedin.com/in/'
};
```

## Step 2: Enrichment Pipeline

```
Raw prospect data
  → Apify Google Search (company + person name)
  → Perplexity Sonar (deep company research via OpenRouter)
  → Apify Company Enrichment (structured data)
  → Gemini Flash synthesis (combine all sources into profile)
```

### Enriched Profile Output

```json
{
  "person": {
    "name": "John Smith",
    "role": "CEO",
    "email": "john@acmecorp.com",
    "phone": "+1-555-123-4567",
    "linkedin": "linkedin.com/in/johnsmith"
  },
  "company": {
    "name": "Acme Corp",
    "domain": "acmecorp.com",
    "industry": "Logistics",
    "size": "50-200",
    "location": "New York, US",
    "recent_news": "Expanded to 3 new markets in Q4 2025"
  },
  "personalization": {
    "pain_points": ["manual dispatch", "driver scheduling"],
    "trigger_event": "Recent expansion to new markets",
    "talking_point": "How AI can scale operations without proportional headcount growth"
  }
}
```

## Step 3: ICP Scoring and Filtering

Use the lead-scoring-engine skill. Filter thresholds:

| Score | Action |
|-------|--------|
| 60+ (Hot) | Priority outreach, all channels |
| 40-59 (Warm) | Standard sequence, email + LinkedIn |
| 20-39 (Cold) | Email-only nurture, low priority |
| <20 | Skip, do not outreach |

## Step 4: Multi-Channel Outreach

### Channel Priority and Sequencing

```
Day 1: Cold email (Smartlead) — personalized first line + value prop
Day 3: LinkedIn connection request (if no email open)
Day 4: Email follow-up #1 (if opened but no reply)
Day 6: LinkedIn DM (if connected)
Day 8: Email follow-up #2 (breakup angle)
Day 10: WhatsApp (if phone available and Israel-based)
Day 14: Final breakup email
```

### Channel Selection Logic

```javascript
// n8n Code Node: Select next channel
function selectChannel(lead) {
  const { email_sent, email_opened, linkedin_connected,
          has_phone, geo, days_since_last } = lead;

  if (!email_sent) return 'cold_email';
  if (email_opened && !lead.replied && days_since_last >= 3) return 'email_followup';
  if (!linkedin_connected && days_since_last >= 2) return 'linkedin_connect';
  if (linkedin_connected && days_since_last >= 3) return 'linkedin_dm';
  if (has_phone && geo === 'IL' && days_since_last >= 5) return 'whatsapp';
  if (days_since_last >= 7) return 'breakup_email';
  return 'wait';
}
```

### AI Personalization (First Lines)

```
Prompt to Gemini Flash (via OpenRouter):

You are a sales copywriter. Write a personalized first line for a cold email.

Context:
- Prospect: {{name}}, {{role}} at {{company}}
- Industry: {{industry}}
- Recent trigger: {{trigger_event}}
- Pain points: {{pain_points}}

Rules:
- Max 20 words
- Reference something specific about them or their company
- No generic compliments
- Sound human, not salesy

Output just the first line, nothing else.
```

### Smartlead Integration

```bash
# Add lead to Smartlead campaign via API
curl -X POST "https://server.smartlead.ai/api/v1/campaigns/{{campaign_id}}/leads" \
  -H "Authorization: Bearer {{SMARTLEAD_API_KEY}}" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_list": [{
      "email": "{{email}}",
      "first_name": "{{first_name}}",
      "last_name": "{{last_name}}",
      "company_name": "{{company}}",
      "custom_fields": {
        "personalized_line": "{{ai_first_line}}",
        "pain_point": "{{pain_point}}",
        "brand": "{{business_brand}}"
      }
    }]
  }'
```

## Step 5: Meeting Booking

### Final Touch CTA

```
{{firstName}}, I've shared a few ideas on how AI can help {{companyName}}
with {{painPoint}}.

If you'd like to see what this looks like for your specific workflow,
here's a quick 15-min slot: {{calendly_link}}

No prep needed — I'll walk through a relevant example.
```

### Calendly/Cal.com Links by Brand

| Brand | Calendar Link |
|-------|---------------|
| guydvorkin.com | `https://cal.com/guydvorkin/15min` |
| exportarena.com | `https://cal.com/exportarena/discovery` |
| afarsemon.com | `https://cal.com/afarsemon/15min` |

## n8n Master Workflow

```
Schedule Trigger (every 4 hours, Sun-Thu for Israel, Mon-Fri for US/EU)
  → Fetch outreach queue from Attio (filter: needs_outreach=true, limit 20)
  → Loop each lead:
    → Determine next channel (Code Node)
    → Switch node by channel:
      → cold_email: Generate personalized email → Smartlead API
      → linkedin_connect: Queue connection request
      → linkedin_dm: Generate DM → queue
      → whatsapp: Generate message → WhatsApp API
      → email_followup: Generate follow-up → Smartlead API
      → breakup_email: Generate breakup → Smartlead API
    → Update Attio: last_outreach_date, sequence_step, channel_used
  → Summary to Telegram: "Processed 18 leads: 5 emails, 4 LinkedIn, 2 WhatsApp"
```

## Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Prospects discovered/week | 100+ | Apify run count |
| Outreach sent/day | 20-30 | Smartlead + LinkedIn + WhatsApp |
| Email open rate | >50% | Smartlead analytics |
| Reply rate | >5% | Smartlead + manual tracking |
| Meetings booked/week | 3-5 | Calendly/Cal.com webhook |
| Discovery-to-meeting rate | >3% | End-to-end conversion |

## Quick Reference

| Task | Method |
|------|--------|
| Discover prospects | Apify actors (LinkedIn, Google, Maps) |
| Enrich leads | Enrichment sub-workflow (Apify + Perplexity + Gemini) |
| Score leads | Lead Scoring Engine skill |
| Send cold email | Smartlead API |
| LinkedIn outreach | LinkedIn Outreach skill |
| WhatsApp message | WhatsApp Business API or manual queue |
| Track sequences | Attio: sequence_step, last_outreach_date |
| Book meetings | Calendly/Cal.com links in final touches |

## Error Handling

- Smartlead API error: retry once, then queue for next batch
- LinkedIn rate limit: pause LinkedIn channel for 24h, continue other channels
- Invalid email bounce: remove from sequence, update Attio status
- Phone number invalid: skip WhatsApp, continue email/LinkedIn
- Enrichment failure: proceed with available data, lower confidence score
- Duplicate across brands: check Attio before outreach, skip if already in sequence
