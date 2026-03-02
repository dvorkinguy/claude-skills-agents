---
name: cold-email-outreach
description: Design and execute cold email campaigns with Smartlead, sending infrastructure, and CRM integration. Use when user says "cold email", "outreach campaign", "email sequence", "Smartlead", "cold outreach", "sending domains", or "email warmup".
metadata:
  author: crm-global
  version: 2.0.0
---

# Cold Email Outreach

## When to Use
- Setting up cold email campaigns that feed leads into Attio
- Designing email sequences with follow-ups
- Configuring Smartlead campaigns and webhooks
- Setting up sending infrastructure (domains, mailboxes)
- Integrating cold email replies with CRM via n8n
- A/B testing subject lines and email copy
- Building AI-personalized outreach at scale

## Recommended Stack

| Component | Tool | Cost |
|-----------|------|------|
| Sequencing | Smartlead | $39/mo (base: 6,000 emails/mo, 2,000 active contacts) |
| Domains | Cloudflare Registrar | ~$10/domain/year |
| Mailboxes | SmartSenders | $4.50/mailbox/month |
| Enrichment | Apify + Perplexity (via OpenRouter) | ~$0.01/lead |
| AI Personalization | Gemini Flash (via OpenRouter) | ~$0.001/email |
| CRM | Attio (via n8n webhook) | included |

## Sending Infrastructure Setup

### Domain Strategy

Buy separate sending domains per brand to protect your main domains. Never send cold email from your primary domain.

| Brand | Primary Domain | Sending Domains |
|-------|---------------|-----------------|
| guydvorkin.com | guydvorkin.com | guydvorkin.co, guydvorkin.io, gdvorkin.com |
| exportarena.com | exportarena.com | exportarena.co, exportarena.io, exparena.com |
| afarsemon.com | afarsemon.com | afarsemon.co, afarsemon.io, afarsemon.net |
| cranianity.com | cranianity.com | cranianity.co, cranianity.io, cranianity.net |

### Mailbox Setup (per sending domain)

3 mailboxes per domain, each sending max 30 emails/day:

```
guy@guydvorkin.co
hello@guydvorkin.co
team@guydvorkin.co
```

Total per brand: 3 domains x 3 mailboxes = 9 mailboxes = 270 emails/day = ~8,100/month

### DNS Configuration (per sending domain)

Set these records in Cloudflare for each sending domain:

```
SPF:  TXT  @  "v=spf1 include:smartsenders.io ~all"
DKIM: TXT  (provided by SmartSenders after mailbox creation)
DMARC: TXT _dmarc  "v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com"
MX:   MX   @  (provided by SmartSenders)
```

### Warmup Protocol

1. Add all mailboxes to Smartlead warmup pool
2. Warmup for 14 days minimum before sending campaigns
3. Start at 5 emails/day, ramp up by 3/day
4. Target warmup settings: 30-40 emails/day, 30% reply rate
5. Keep warmup running even during active campaigns

## Email Sequence Template

### 4-Step AI Workforce Outreach Sequence

**Step 1: Initial Outreach (Day 0)**

Subject A: `{{first_name}}, quick question about {{company}}'s workflow`
Subject B: `AI is changing {{industry}} - here's how`

```
Hi {{first_name}},

{{ai_personalized_first_line}}

We help companies like {{company}} automate repetitive workflows using AI agents -- think of it as hiring a digital workforce that works 24/7 without the overhead.

One of our clients in {{industry}} cut their manual processing time by 70% in the first month.

Worth a 15-min call to see if something similar could work for {{company}}?

Best,
{{sender_name}}
{{brand}}
```

**Step 2: Value-Add Follow-Up (Day 3)**

Subject: `Re: {{previous_subject}}`

```
Hi {{first_name}},

Wanted to share a quick example that might be relevant.

We recently helped a {{industry}} company automate their {{pain_point_area}} process. The result: what used to take their team 20 hours/week now runs automatically.

The ROI broke even in week 2.

Happy to walk you through how it could work for {{company}} -- no pressure, just showing you what's possible.

{{sender_name}}
```

**Step 3: Social Proof (Day 8)**

Subject: `Re: {{previous_subject}}`

```
Hi {{first_name}},

I know you're busy, so I'll keep this short.

Here's what {{similar_company}} said after 3 months with our AI Workforce:

"We eliminated 2 full-time positions worth of manual data entry and redirected that budget to growth."

If {{company}} has any processes that feel repetitive or bottlenecked, that's exactly what we solve.

Open to a quick chat this week?

{{sender_name}}
```

**Step 4: Break-Up (Day 15)**

Subject: `Should I close your file, {{first_name}}?`

```
Hi {{first_name}},

I've reached out a few times and haven't heard back -- totally understand if the timing isn't right.

I'll assume this isn't a priority for {{company}} right now and won't follow up again.

But if AI automation is ever on your radar, just reply to this email and I'll be here.

All the best,
{{sender_name}}
```

### Personalization Variables

| Variable | Source | How to Get |
|----------|--------|-----------|
| `{{first_name}}` | Lead list | CSV import |
| `{{company}}` | Lead list | CSV import |
| `{{industry}}` | Enrichment | Apify company data |
| `{{ai_personalized_first_line}}` | AI | Gemini Flash via OpenRouter |
| `{{pain_point_area}}` | Enrichment | Perplexity research |
| `{{similar_company}}` | Manual | Match to case study |
| `{{sender_name}}` | Campaign config | Per brand |
| `{{brand}}` | Campaign config | Per brand |

### AI First-Line Personalization (via n8n)

Use the enrichment sub-workflow output to generate a personalized opening line:

```json
{
  "type": "@n8n/n8n-nodes-langchain.openAi",
  "parameters": {
    "model": "google/gemini-2.5-flash-preview",
    "baseUrl": "https://openrouter.ai/api/v1",
    "prompt": "Write a personalized first line for a cold email to {{first_name}} at {{company}}. Use this research:\n\n{{enrichment_summary}}\n\nRules:\n- One sentence only\n- Reference something specific about their company or role\n- Sound natural, not salesy\n- No generic compliments\n- Connect to AI/automation if possible",
    "options": {
      "temperature": 0.7,
      "maxTokens": 100
    }
  }
}
```

## Smartlead Configuration

### Campaign Settings

```
Daily send limit per mailbox: 30
Time between emails: 8-15 minutes (randomized)
Sending window: 8am-6pm recipient timezone
Track opens: Yes
Track clicks: Yes
Stop on reply: Yes
Stop on auto-reply: No (filter auto-replies separately)
```

### Smartlead API Integration (for n8n)

Base URL: `https://server.smartlead.ai/api/v1`

**Create Campaign:**
```bash
curl -X POST "https://server.smartlead.ai/api/v1/campaigns/create?api_key=$SMARTLEAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Q1 Export Arena - Manufacturing AI",
    "timezone": "America/New_York"
  }'
```

**Add Leads to Campaign:**
```bash
curl -X POST "https://server.smartlead.ai/api/v1/campaigns/$CAMPAIGN_ID/leads?api_key=$SMARTLEAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_list": [
      {
        "email": "john@acme.com",
        "first_name": "John",
        "last_name": "Doe",
        "company": "Acme Corp",
        "custom_fields": {
          "industry": "Manufacturing",
          "ai_first_line": "Saw Acme just expanded their logistics team..."
        }
      }
    ]
  }'
```

**Get Campaign Stats:**
```bash
curl "https://server.smartlead.ai/api/v1/campaigns/$CAMPAIGN_ID/analytics?api_key=$SMARTLEAD_API_KEY"
```

### Smartlead Webhook Events

Configure webhooks in Smartlead Settings to POST to your n8n webhook:

| Event | Webhook Payload Key | CRM Action |
|-------|-------------------|------------|
| `REPLY` | `event_type: "REPLY"` | sequence_status=Replied, lead_temperature=Hot, lead_score+=30 |
| `OPEN` | `event_type: "OPEN"` | lead_temperature=Warm (if Cold), lead_score+=5 |
| `CLICK` | `event_type: "CLICK"` | lead_temperature=Warm, lead_score+=10 |
| `BOUNCE` | `event_type: "BOUNCE"` | sequence_status=Paused, lead_score=0 |
| `UNSUBSCRIBE` | `event_type: "UNSUBSCRIBE"` | sequence_status=Completed, add note |

### Webhook Payload Example (Reply)

```json
{
  "event_type": "REPLY",
  "email": "john@acme.com",
  "first_name": "John",
  "last_name": "Doe",
  "campaign_id": 12345,
  "campaign_name": "Q1 Export Arena - Manufacturing AI",
  "reply_text": "Thanks for reaching out. Can we schedule a call next week?",
  "reply_date": "2026-03-01T14:30:00Z"
}
```

## CRM Integration Flow

### Smartlead Webhook to n8n to Attio

```
Smartlead Event → n8n Webhook (POST /smartlead-events)
  → Switch on event_type
    → REPLY:
        1. search_records (people, email)
        2. update_record: sequence_status=Replied, lead_temperature=Hot, lead_score+=30
        3. create_note: "Replied to cold email campaign: {campaign_name}. Reply: {reply_text}"
        4. Telegram notification: "Hot lead reply from {name}!"
    → OPEN:
        1. search_records (people, email)
        2. update_record: lead_score+=5, lead_temperature=Warm (if currently Cold)
    → CLICK:
        1. search_records (people, email)
        2. update_record: lead_score+=10, lead_temperature=Warm
    → BOUNCE:
        1. search_records (people, email)
        2. update_record: sequence_status=Paused, lead_score=0
        3. create_note: "Email bounced in campaign: {campaign_name}"
    → UNSUBSCRIBE:
        1. search_records (people, email)
        2. update_record: sequence_status=Completed
        3. create_note: "Unsubscribed from campaign: {campaign_name}"
```

### n8n Workflow Node Structure

```
[Webhook Trigger] → [Switch: event_type]
  → [HTTP Request: Attio search] → [HTTP Request: Attio update] → [Telegram notify]
```

## A/B Testing Strategy

Test these elements in order of impact:

1. **Subject lines** (biggest impact on open rate)
   - Test 2 variants per step, 50/50 split
   - Winner after 200+ sends with statistical significance
   - Target: 40%+ open rate

2. **First line** (impact on reply rate)
   - AI-personalized vs template-based
   - Target: 3-5% reply rate

3. **CTA** (impact on conversion)
   - "15-min call" vs "quick question" vs "send you a case study"

4. **Sequence length**
   - 3 steps vs 4 steps vs 5 steps

## Campaign Checklist

- [ ] Sending domains purchased and DNS configured
- [ ] Mailboxes created in SmartSenders (3 per domain)
- [ ] Mailboxes added to Smartlead and warmup started (14+ days)
- [ ] Lead list enriched with company data and AI first lines
- [ ] Email copy written with A/B subject lines
- [ ] Smartlead campaign created with correct sending settings
- [ ] Smartlead webhooks configured to POST to n8n
- [ ] n8n workflow deployed: Smartlead webhook to Attio sync
- [ ] Test webhook payload sent and verified in Attio
- [ ] Brand-specific sender signature configured

## Cost Breakdown (per brand)

| Item | Monthly Cost |
|------|-------------|
| Smartlead (shared across brands) | $39 / 4 = ~$10 |
| 3 sending domains | $30/year = $2.50 |
| 9 mailboxes ($4.50 each) | $40.50 |
| Enrichment (~200 leads) | ~$2 |
| AI personalization | ~$0.20 |
| **Total per brand** | **~$55/month** |

## References
- See `docs/guides/cold-email/` for tool-specific documentation
- See `docs/skills/n8n-crm-workflows.md` for workflow #8 (Cold Email Sequencer)
- See `docs/skills/attio-crm-setup.md` for CRM field definitions
