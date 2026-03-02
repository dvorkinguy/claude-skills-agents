# API Patterns Reference

## Apify Actors

| Actor | ID | Purpose | Timeout |
|-------|----|---------|---------|
| Google Search | `apify~google-search-scraper` | Top search results | 60s |
| LinkedIn Profile | `anchor~linkedin-profile-scraper` | Profile data | 60s |
| Company Enrichment | `vivid_astronaut~company-enrichment` | Structured company data | 60s |

### Apify Run Pattern
```
POST https://api.apify.com/v2/acts/{actorId}/run-sync-get-dataset-items
Authorization: Bearer {APIFY_API_TOKEN}
Content-Type: application/json
```

## OpenRouter

**Endpoint:** `https://openrouter.ai/api/v1/chat/completions`

| Model | Use Case |
|-------|----------|
| `perplexity/sonar-pro` | Deep research with citations |
| `google/gemini-2.5-flash` | Synthesis (fast, structured JSON) |

### OpenRouter Pattern
```
POST https://openrouter.ai/api/v1/chat/completions
Authorization: Bearer {OPENROUTER_API_KEY}
Content-Type: application/json
```

## Attio CRM

**Base:** `https://api.attio.com/v2`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/objects/companies/records?matching_attribute=domains` | PUT | Upsert company |
| `/objects/people/records?matching_attribute=email_addresses` | PUT | Upsert person |
| `/notes` | POST | Create note |
| `/lists/{list_id}/entries` | POST | Add record to list |

### Attio Upsert Pattern
```
PUT https://api.attio.com/v2/objects/{object}/records?matching_attribute={attr}
Authorization: Bearer {ATTIO_API_KEY}
Content-Type: application/json
```

### Key Attio Gotchas
- `name` attribute requires `full_name` field
- Phone: use `original_phone_number`, must be E.164
- Israeli numbers: strip non-digits, prefix `0XX` with `+972`
- Use `JSON.stringify()` for body — string concat breaks with special chars
