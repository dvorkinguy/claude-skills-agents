---
name: lead-enrichment
description: Enrich leads with company intelligence via Apify + OpenRouter + Attio CRM. Use when user says "enrich this lead", "research this company", "score this prospect", gives a company name/domain, or asks for "competitive intelligence".
---

# Lead Enrichment Skill

Orchestrate multi-source lead enrichment using Apify scrapers, OpenRouter LLMs, and Attio CRM — all from the CLI.

## Trigger Phrases

- "enrich this lead", "enrich [company]"
- "research this company", "research [domain]"
- "score this prospect"
- Company name or domain provided for enrichment
- "competitive intelligence on [company]"

## Workflow

### Step 1: Extract Lead Identifiers

Parse the user's input for:
- **company** — company name (Hebrew or English)
- **domain** — website domain
- **email** — contact email (extract domain for company research)
- **linkedin_url** — LinkedIn profile or company page URL
- **name** — contact person name

If only a company name is given, proceed without the rest.

### Step 2: Run Enrichment Script

```bash
python3 ~/.claude/skills/lead-enrichment/scripts/enrich_lead.py \
  --company "CompanyName" \
  --domain "example.com" \
  --email "contact@example.com" \
  --linkedin "https://linkedin.com/in/person"
```

The script runs parallel API calls to:
1. **Apify Google Search** — top 5 results for company query
2. **OpenRouter Perplexity Sonar Pro** — deep company research
3. **OpenRouter Perplexity Sonar Pro** — trade/industry data
4. **Apify Company Enrichment** — structured company data (if company name provided)
5. **Apify LinkedIn Scraper** — profile data (if LinkedIn URL provided)

Then synthesizes all results via **Gemini 2.5 Flash** (OpenRouter) into a structured JSON profile.

### Step 3: Validate Output

```bash
python3 ~/.claude/skills/lead-enrichment/scripts/validate_enrichment.py < output.json
```

### Step 4: Present Results

Display the enrichment brief to the user in a readable format:

```
## Lead Brief: [Company Name]

**Score:** 8/10 (Hot)
**Industry:** Import/Export, Technology
**Company Size:** 50-200 employees

### Context
[2-3 sentence summary for outreach]

### Key Intelligence
- Recent news/developments
- Decision makers identified
- Technology stack signals
- Export/import activity

### Recommended Action
[Based on ICP score]
```

### Step 5: Optional CRM Write-back

Ask the user: "Write this to Attio CRM?" If yes, use the Attio API to upsert:
- Company record
- Person record (if contact info available)
- Note with enrichment details

## Reference Files

| File | Purpose |
|------|---------|
| `references/icp-criteria.md` | ICP scoring rubric for Export Arena |
| `references/enrichment-prompts.md` | Proven prompt templates from n8n workflows |
| `references/api-patterns.md` | API endpoints, actor IDs, models used |
| `assets/enrichment-schema.json` | Output JSON schema |

## Environment Variables Required

All read from `~/.env` or project `.env`:
- `APIFY_API_TOKEN` — Apify platform token
- `OPENROUTER_API_KEY` — OpenRouter API key
- `ATTIO_API_KEY` — Attio CRM API key (optional, for write-back)

## Error Handling

- Each API call has a 60s timeout and continues on failure
- Missing data sources are noted in `enrichment_notes`
- If all sources fail, return partial results with error context
- Never block on a single failed source
