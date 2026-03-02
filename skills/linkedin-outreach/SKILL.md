---
name: linkedin-outreach
description: LinkedIn prospecting automation with Apify scrapers, ICP filtering, connection sequences, and CRM sync. Use when user says "find prospects on LinkedIn", "LinkedIn outreach", "scrape LinkedIn", "connection request", or needs to build a LinkedIn prospecting pipeline.
---

# LinkedIn Outreach

Automated LinkedIn prospecting pipeline: discover prospects via Apify scrapers, filter by ICP, generate personalized connection requests and DM sequences, and sync everything to Attio CRM.

## When to Use

- "Find prospects on LinkedIn" or "scrape LinkedIn for leads"
- "LinkedIn outreach sequence" or "connection request template"
- "Build a LinkedIn prospecting list"
- "DM sequence for LinkedIn"
- Targeting specific job titles, industries, or company sizes on LinkedIn

## Apify Actors for LinkedIn

| Actor | Purpose | Input |
|-------|---------|-------|
| `apify/linkedin-profile-scraper` | Scrape individual profiles | Profile URLs |
| `apify/linkedin-company-scraper` | Scrape company pages | Company URLs |
| `curious_coder/linkedin-search-scraper` | Search results scraping | Search query, filters |
| `apify/google-search-scraper` | Find LinkedIn profiles via Google | `site:linkedin.com/in/ "job title" "industry"` |

### Google-to-LinkedIn Search Pattern

More reliable than LinkedIn's native search for large-scale prospecting:

```bash
# Apify Google Search actor input
{
  "queries": "site:linkedin.com/in/ \"CEO\" OR \"founder\" \"logistics\" \"Israel\"",
  "maxPagesPerQuery": 3,
  "resultsPerPage": 10
}
```

## ICP Targeting Criteria

| Filter | Values for AI Workforce |
|--------|------------------------|
| Job titles | CEO, COO, VP Operations, Head of Digital, Founder, Owner, Managing Director |
| Company size | 10-500 employees |
| Industries | Logistics, Manufacturing, Professional Services, Import/Export, Construction |
| Geography | Israel (afarsemon), US/EU (guydvorkin/exportarena) |
| Exclude | Students, job seekers, competitors, consultants |

## Connection Request Templates (300 char max)

### Template A: Mutual Interest
```
Hi {{firstName}}, I noticed we're both in the {{industry}} space. I'm working on AI workforce solutions that help companies like {{companyName}} automate operations. Would love to connect and exchange ideas.
```

### Template B: Specific Trigger
```
Hi {{firstName}}, saw {{companyName}}'s recent {{trigger}} — impressive growth. We help similar companies cut operational costs 40% with AI automation. Happy to share how if you're open to connecting.
```

### Template C: Value-First
```
Hi {{firstName}}, I put together a guide on how {{industry}} companies are using AI to handle {{painPoint}}. Happy to share it — thought it might be relevant for {{companyName}}.
```

## DM Sequence (Post-Connection)

### Day 0: Connection Accepted
No message. Let the connection breathe.

### Day 2: Value Message
```
Thanks for connecting, {{firstName}}! I've been researching how {{industry}} companies
are adopting AI for operations. Here's a quick insight:

[1-2 sentence insight relevant to their industry]

Curious — is {{companyName}} exploring any automation initiatives?
```

### Day 5: Case Study
```
{{firstName}}, quick follow-up — we recently helped a {{similarCompany}}
in {{industry}} reduce their [specific metric] by [percentage] using AI workers.

Here's the 2-min case study: [link]

Would something like this be relevant for {{companyName}}?
```

### Day 8: Soft CTA
```
Hi {{firstName}}, last message from me on this — I know you're busy.

If automating [specific process] at {{companyName}} is on your radar for 2026,
I'd love to show you what's possible in a quick 15-min call.

Here's my calendar if it's easier: [Calendly link]

Either way, happy to stay connected and share insights.
```

### Day 15: Break-up (if no reply)
```
{{firstName}}, I'll take the hint :)

If AI automation ever comes up on your priority list, feel free to reach out.
Always happy to help.
```

## n8n Workflow Pattern

```
Schedule Trigger (every 4 hours, business days only)
  → Apify: Run Google-to-LinkedIn search
  → Code Node: Parse results, extract profile URLs
  → Apify: Scrape profiles (batch of 20)
  → Code Node: Filter by ICP criteria
  → Enrichment Sub-workflow (parallel: company data + Perplexity research)
  → Lead Scoring Engine (calculate score)
  → Filter: score >= 40 (Warm+)
  → Attio: Upsert person record (acquisition_channel=LinkedIn)
  → Attio: Add to Lead Nurturing list
  → Code Node: Generate personalized connection request
  → Queue: Add to outreach queue (daily limit: 20 connections)
  → Telegram: Send daily summary
```

## LinkedIn Platform Limits

| Action | Daily Limit | Weekly Limit | Notes |
|--------|-------------|--------------|-------|
| Connection requests | 20-25 | 100 | Lower for new accounts |
| Messages (1st degree) | 50 | 150 | InMail separate |
| Profile views | 100 | 500 | Can trigger notifications |
| Search results pages | 100 | - | Use Google search instead |

### Safety Guidelines

- Spread actions throughout the day (not bursts)
- Warm up new accounts: start with 5-10/day, increase over 2 weeks
- Personalize every connection request (no generic messages)
- Mix manual and automated actions
- Pause on weekends and holidays
- If account restricted: stop all automation for 7 days

## CRM Sync Fields

| Attio Field | Value |
|-------------|-------|
| `acquisition_channel` | "LinkedIn" |
| `linkedin_url` | Profile URL |
| `sequence_status` | pending / connection_sent / connected / messaged / replied / meeting_booked |
| `sequence_step` | 0-4 (which DM in sequence) |
| `last_outreach_date` | Date of last message |

## Personalization Variables

| Variable | Source |
|----------|--------|
| `{{firstName}}` | LinkedIn profile |
| `{{companyName}}` | LinkedIn profile or enrichment |
| `{{industry}}` | Company data enrichment |
| `{{trigger}}` | Recent news via Perplexity Sonar |
| `{{painPoint}}` | Industry-specific from vertical playbooks |
| `{{similarCompany}}` | Case study match from same vertical |

## Quick Reference

| Task | Method |
|------|--------|
| Find prospects | Apify Google search with site:linkedin.com filter |
| Scrape profiles | Apify LinkedIn profile scraper |
| Generate connection msg | AI (Gemini Flash) with enrichment context |
| Track sequence | Attio: sequence_status + sequence_step fields |
| Daily outreach batch | n8n: filter queue, send up to 20, update status |

## Error Handling

- Apify actor timeout: retry once, then skip and log
- LinkedIn rate limit hit: pause outreach for 24 hours, alert via Telegram
- Profile scrape returns empty: mark as "scrape_failed", try Google enrichment instead
- Duplicate detection: check Attio by LinkedIn URL before creating new record
