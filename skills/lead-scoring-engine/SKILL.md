---
name: lead-scoring-engine
description: AI-powered lead scoring with ICP fit, engagement signals, enrichment quality, and channel quality. Use when user says "score this lead", "what's the lead score", "prioritize leads", "rank prospects", or needs to calculate/update lead temperatures.
---

# Lead Scoring Engine

Calculate and maintain lead scores (0-100) based on ICP fit, engagement signals, enrichment quality, and acquisition channel -- then sync scores and temperature labels to Attio CRM.

## When to Use

- "Score this lead" or "score these leads"
- "What's the lead temperature?"
- "Prioritize my pipeline" or "rank prospects"
- "Update lead scores" or "re-score leads"
- After new engagement data comes in (email reply, meeting booked, website visit)
- When routing leads to determine outreach priority

## Scoring Rubric

### 1. ICP Fit (0-30 points)

| Criteria | Points | Details |
|----------|--------|---------|
| Company size 10-500 employees | 10 | Sweet spot for AI Workforce solutions |
| Company size 500+ | 5 | Enterprise = longer sales cycle |
| Company size <10 | 2 | Limited budget |
| Target industry (logistics, manufacturing, professional services, import/export) | 10 | Primary verticals |
| Adjacent industry (retail, construction, tech) | 5 | Secondary verticals |
| Decision maker role (CEO, COO, VP Ops, Head of Digital) | 10 | Budget authority |
| Manager/Director | 6 | Influencer, not buyer |
| Individual contributor | 2 | Low purchase authority |

### 2. Engagement Signals (0-25 points)

| Signal | Points |
|--------|--------|
| Email reply (positive/interested) | 10 |
| Email reply (objection/question) | 7 |
| Meeting booked | 15 |
| Email opened 3+ times | 5 |
| Email link clicked | 8 |
| Website visit (tracked) | 5 |
| Downloaded resource | 7 |
| Social media interaction (liked/commented) | 3 |

Points are additive but capped at 25.

### 3. Enrichment Quality (0-15 points)

| Data Available | Points |
|----------------|--------|
| Has LinkedIn profile URL | 5 |
| Has verified company domain | 4 |
| Has phone number | 3 |
| Has company size/industry data | 3 |

### 4. Channel Quality (0-30 points)

| Acquisition Channel | Points | Rationale |
|---------------------|--------|-----------|
| Referral | 30 | Highest trust, highest close rate |
| Cold email reply | 20 | Showed active interest |
| ManyChat (bot engagement) | 15 | Engaged with content |
| Ads (Meta/Google/TikTok) | 10 | Paid intent signal |
| Cold outreach (no reply yet) | 5 | Unvalidated |
| Scraped/purchased list | 2 | Lowest quality |

## Temperature Mapping

| Score Range | Temperature | Action |
|-------------|-------------|--------|
| 0-30 | Cold | Nurture sequence, low priority |
| 31-60 | Warm | Active follow-up, personalized outreach |
| 61-100 | Hot | Immediate action, book meeting, send proposal |

## Workflow

### Step 1: Gather Lead Data

Collect from Attio CRM via MCP:
- Person record: name, email, phone, LinkedIn, company association
- Company record: size, industry, domain
- List entry data: lead_source, business_brand
- Notes and interaction history

### Step 2: Calculate Score

```javascript
// n8n Code Node — Lead Score Calculator
function calculateScore(lead) {
  let score = 0;

  // ICP Fit (0-30)
  const companySize = lead.company_size || 0;
  if (companySize >= 10 && companySize <= 500) score += 10;
  else if (companySize > 500) score += 5;
  else score += 2;

  const targetIndustries = ['logistics', 'manufacturing', 'professional services', 'import', 'export', 'trade'];
  if (targetIndustries.some(i => (lead.industry || '').toLowerCase().includes(i))) score += 10;

  const decisionRoles = ['ceo', 'coo', 'founder', 'owner', 'vp', 'head of', 'director of operations'];
  if (decisionRoles.some(r => (lead.role || '').toLowerCase().includes(r))) score += 10;

  // Engagement (0-25)
  let engagement = 0;
  if (lead.replied_positive) engagement += 10;
  if (lead.meeting_booked) engagement += 15;
  if (lead.email_opened_3plus) engagement += 5;
  if (lead.link_clicked) engagement += 8;
  score += Math.min(engagement, 25);

  // Enrichment Quality (0-15)
  if (lead.linkedin_url) score += 5;
  if (lead.company_domain) score += 4;
  if (lead.phone) score += 3;
  if (lead.company_size && lead.industry) score += 3;

  // Channel Quality (0-30)
  const channelScores = {
    'Referral': 30, 'Cold Email': 20, 'ManyChat': 15,
    'Social Media': 10, 'Direct': 5
  };
  score += channelScores[lead.lead_source] || 5;

  return Math.min(score, 100);
}

const temperature = score <= 30 ? 'Cold' : score <= 60 ? 'Warm' : 'Hot';
```

### Step 3: Update CRM

Use Attio MCP to update:
- `lead_score` field on person record
- `lead_temperature` field (Cold/Warm/Hot) if available
- Add note with score breakdown for audit trail

### Step 4: Route Based on Temperature

| Temperature | Next Action |
|-------------|-------------|
| Hot | Notify via Telegram, assign to active follow-up |
| Warm | Add to follow-up sequence, prioritize in daily batch |
| Cold | Add to nurture sequence, re-score in 14 days |

## n8n Integration Pattern

```
Trigger (schedule/webhook)
  → Fetch leads from Attio (filter: score_updated_at > 7 days ago)
  → Loop: for each lead
    → Gather engagement data
    → Calculate score (Code Node)
    → Update Attio lead_score
    → Route by temperature
  → Send summary to Telegram
```

## Re-Scoring Triggers

| Event | Action |
|-------|--------|
| Email reply received | Re-score immediately, add engagement points |
| Meeting booked | Re-score, likely jump to Hot |
| 14 days no interaction | Re-score, likely drop temperature |
| New enrichment data added | Re-score, update enrichment quality points |
| Manual override | Set score directly, add note explaining why |

## Quick Reference

| Task | Method |
|------|--------|
| Score single lead | Attio MCP: get record -> calculate -> update |
| Batch re-score | n8n workflow: scheduled daily at 8am |
| Check score | Attio MCP: get_record_details |
| Override score | Attio MCP: update_record with manual score + note |

## Error Handling

- Missing company data: score ICP fit as 0, note in breakdown
- Missing engagement data: default to channel score only
- Attio API failure: log error, retry in next batch
- Score exceeds 100: cap at 100
