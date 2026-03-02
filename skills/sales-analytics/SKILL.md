---
name: sales-analytics
description: Pipeline analytics, revenue tracking, funnel analysis, and automated reporting via Attio CRM data. Use when user says "pipeline report", "sales metrics", "conversion rates", "forecast", "CAC analysis", "weekly summary", or needs any sales performance data.
---

# Sales Analytics

Generate pipeline metrics, revenue forecasts, funnel analysis, and channel ROI reports from Attio CRM data -- delivered as Telegram summaries or structured reports.

## When to Use

- "How's the pipeline?" or "pipeline report"
- "What are my conversion rates?"
- "Weekly sales summary"
- "CAC by channel" or "which channel performs best?"
- "Revenue forecast" or "weighted pipeline"
- "Compare brands" or "brand performance"
- Any request for sales data, metrics, or trends

## Core Metrics

### Daily Pipeline Snapshot

| Metric | Calculation | Source |
|--------|------------|--------|
| New leads today | Count records created today | Attio People (created_at filter) |
| Qualified leads | Count with lead_score >= 60 | Attio Lead Nurturing list |
| Proposals sent | Count deals in "Proposal" stage | Attio Deals |
| Deals won | Count deals in "Won" stage (this period) | Attio Deals |
| Deals lost | Count deals in "Lost" stage (this period) | Attio Deals |
| Win rate | Won / (Won + Lost) | Calculated |
| Pipeline value | Sum of all active deal values | Attio Deals |
| Weighted forecast | Sum(deal_value * stage_probability) | Calculated |

### Stage Probabilities for Weighted Forecast

| Stage | Probability |
|-------|------------|
| Lead | 10% |
| Qualified | 25% |
| Discovery Call | 40% |
| Proposal Sent | 60% |
| Negotiation | 80% |
| Won | 100% |
| Lost | 0% |

### Funnel Analysis

```
Leads Captured    → Qualified         → Discovery Call    → Proposal    → Won
    100           →     40 (40%)      →     20 (50%)      →   12 (60%)  →  6 (50%)

Overall: 6% lead-to-win conversion
```

### Stage-to-Stage Conversion Rates

```javascript
// n8n Code Node: Calculate funnel metrics
function calculateFunnel(deals) {
  const stages = ['Lead', 'Qualified', 'Discovery Call', 'Proposal Sent', 'Negotiation', 'Won'];
  const counts = {};
  stages.forEach(s => counts[s] = deals.filter(d => d.stage === s || stageIndex(d.stage) > stageIndex(s)).length);

  const conversions = [];
  for (let i = 0; i < stages.length - 1; i++) {
    const from = counts[stages[i]];
    const to = counts[stages[i + 1]];
    conversions.push({
      from_stage: stages[i],
      to_stage: stages[i + 1],
      rate: from > 0 ? ((to / from) * 100).toFixed(1) + '%' : 'N/A'
    });
  }
  return conversions;
}
```

### Time in Stage

| Stage | Target | Alert If |
|-------|--------|----------|
| Lead → Qualified | < 3 days | > 7 days |
| Qualified → Discovery | < 5 days | > 10 days |
| Discovery → Proposal | < 3 days | > 7 days |
| Proposal → Decision | < 7 days | > 14 days |

## Channel ROI Analysis

### Cost per Acquisition (CAC) by Channel

| Channel | Typical Monthly Spend | Leads | Customers | CAC |
|---------|----------------------|-------|-----------|-----|
| Meta Ads | $X | from Attio | from Attio | Spend / Customers |
| Google Ads | $X | from Attio | from Attio | Spend / Customers |
| Cold Email (Smartlead) | $50/mo + enrichment | from Attio | from Attio | Total / Customers |
| LinkedIn | $0 (organic) + time | from Attio | from Attio | Time value / Customers |
| ManyChat | $15/mo | from Attio | from Attio | $15 / Customers |
| Referral | $0 | from Attio | from Attio | $0 |

### LTV:CAC Ratio

```
LTV = Average Deal Value * Average Customer Lifespan (months) * Monthly Revenue
CAC = Total Channel Spend / Customers Acquired

Target LTV:CAC > 3:1
```

## Brand Comparison

### Per-Brand Metrics Table

```
| Metric              | guydvorkin | exportarena | afarsemon |
|---------------------|-----------|-------------|-----------|
| Active leads        |           |             |           |
| Pipeline value      |           |             |           |
| Deals won (month)   |           |             |           |
| Win rate            |           |             |           |
| Avg deal size       |           |             |           |
| Top channel         |           |             |           |
```

### Attio Queries for Brand Data

```javascript
// Filter leads by brand
// Use Attio MCP: filter-list-entries on lead_nurturing_v2
// Filter by business_brand field value
```

## Telegram Report Format

### Daily Report (sent at 9am)

```
Sales Dashboard - March 1, 2026

Pipeline Snapshot
  New leads: 5
  Qualified: 2
  Proposals: 1
  Won: 0 | Lost: 0

Active Pipeline
  Total deals: 12
  Pipeline value: $45,000
  Weighted forecast: $18,500

Today's Priority
  3 follow-ups overdue
  1 proposal needs sending
  2 leads need qualification

Top Lead: John Smith (Acme Corp) - Score: 85 Hot
```

### Weekly Executive Summary (sent Sunday/Monday)

```
Weekly Sales Report - Feb 23-Mar 1, 2026

Key Numbers
  Leads captured: 23 (up 15% vs last week)
  Meetings booked: 4
  Proposals sent: 3
  Deals won: 1 ($8,500)
  Deals lost: 1
  Win rate: 50%

Funnel Health
  Lead to Qualified: 35% (target: 40%)
  Qualified to Meeting: 50% (target: 50%)
  Meeting to Proposal: 75% (target: 60%)
  Proposal to Won: 33% (target: 30%)

Channel Performance
  Best: Referral (2 leads, 1 won)
  Growing: Cold Email (8 leads, 2 qualified)
  Underperforming: Meta Ads (10 leads, 0 qualified) -- review targeting

Brand Breakdown
  guydvorkin: 10 leads, $8,500 won
  exportarena: 8 leads, $0 won (3 in proposal)
  afarsemon: 5 leads, $0 won

Recommendations
  1. Double down on referral program
  2. Review Meta Ads targeting (high volume, low quality)
  3. Follow up on 3 stale proposals (> 7 days)
```

## n8n Workflow Pattern

### Daily Report Workflow

```
Schedule Trigger (daily 9am Israel time)
  → Attio API: Fetch pipeline data
    - GET deals (all active stages)
    - GET lead nurturing entries (created today)
    - GET deals (stage changed today)
  → Code Node: Calculate all metrics
  → Code Node: Format Telegram message
  → Telegram: Send to admin chat
```

### Weekly Report Workflow

```
Schedule Trigger (Sunday 8am)
  → Attio API: Fetch 7-day data
    - Deals created, won, lost this week
    - Leads captured this week
    - Stage transitions this week
  → Code Node: Calculate funnel, conversions, trends
  → AI Node (Gemini Flash): Generate recommendations
  → Code Node: Format executive summary
  → Telegram: Send report
```

## Querying Attio for Metrics

### Via MCP Tools

| Data Needed | MCP Tool | Filter |
|-------------|----------|--------|
| All active deals | `search_records_advanced` (deals) | stage != Won, stage != Lost |
| New leads today | `filter-list-entries` (lead_nurturing_v2) | created_at = today |
| Leads by brand | `filter-list-entries` (lead_nurturing_v2) | business_brand = X |
| Deals by stage | `search_records_advanced` (deals) | stage = X |
| Won deals this month | `search_records_advanced` (deals) | stage = Won, closed_at >= month start |

### Via Attio REST API (for n8n)

```bash
# Active deals
curl -s "https://api.attio.com/v2/objects/deals/records/query" \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"stage": {"$not_in": ["Won", "Lost"]}}, "limit": 500}'

# Leads created this week
curl -s "https://api.attio.com/v2/lists/lead_nurturing_v2/entries/query" \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"created_at": {"$gte": "2026-02-23T00:00:00Z"}}, "limit": 500}'
```

## Quick Reference

| Task | Method |
|------|--------|
| Pipeline snapshot | Attio MCP: search deals, calculate metrics |
| Funnel analysis | Attio MCP: count deals by stage, calculate conversions |
| Channel ROI | Attio MCP: group leads by source + ad spend data |
| Brand comparison | Attio MCP: filter by business_brand |
| Daily report | n8n scheduled workflow → Telegram |
| Weekly summary | n8n scheduled workflow → AI recommendations → Telegram |

## Error Handling

- Attio API timeout: retry once, send partial report with note
- No deals data: report "No active deals" rather than empty
- Division by zero: handle in conversion rate calculations, show "N/A"
- Missing date fields: use record created_at as fallback
- Telegram send failure: log to file, retry in 5 minutes
