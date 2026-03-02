---
name: scrape-to-crm
description: "LinkedIn scrape → transform → Attio CRM pipeline. Use when user says 'scrape LinkedIn to CRM', 'pipeline LinkedIn leads', 'scrape and push to Attio', 'scrape-to-crm', or wants to scrape LinkedIn profiles/companies and push them to Attio."
argument-hint: "[LinkedIn URL, company name, or keyword]"
---

# Scrape-to-CRM Pipeline

End-to-end pipeline: **LinkedIn scrape (Apify) → data transform → n8n workflow → Attio CRM upsert**.

## Trigger Phrases

- "scrape LinkedIn to CRM", "scrape to Attio"
- "pipeline LinkedIn leads"
- "scrape and push to Attio"
- LinkedIn URL + "push to CRM"
- `/scrape-to-crm [target]`

## Pipeline Steps

### Step 1: Gather Requirements

Ask the user (if not provided via arguments):

1. **What to scrape** — one of:
   - LinkedIn search URL (e.g., `https://www.linkedin.com/search/results/people/?keywords=...`)
   - LinkedIn company page URL (e.g., `https://www.linkedin.com/company/acme/`)
   - Company name or keyword (e.g., "fintech Tel Aviv")

2. **Attio target** — which object and optional list:
   - Object: `people` (default) or `companies`
   - List: optional Attio list name to add records to

3. **Geography** (if adding to a list with Country/City attributes):
   - Country: e.g., "Israel", "Turkey", "Greece"
   - City: e.g., "Haifa", "Tel Aviv", "Ashdod", "Istanbul"

4. **Source** — how this lead was sourced (default: "Scraped"):
   - Options: Scraped, Referral, Manual

5. **Limit** — max records to scrape (default: 25, max: 100)

### Step 2: Apify — Find and Run LinkedIn Actor

Use MCP Apify tools in sequence:

#### 2a. Search for the best actor

```
Tool: mcp__apify__search-actors
Query: "linkedin" + context (e.g., "linkedin profile scraper", "linkedin company scraper", "linkedin search")
```

**Preferred actors by use case:**
| Use Case | Preferred Actor | Fallback |
|----------|----------------|----------|
| Profile scraping | `anchor~linkedin-profile-scraper` | Search for "linkedin profile" |
| Company page | `apify~linkedin-company-scraper` | Search for "linkedin company" |
| Search results | `curious_coder~linkedin-search` | Search for "linkedin search scraper" |
| People search | `bebity~linkedin-people-search` | Search for "linkedin people" |

#### 2b. Fetch actor details and input schema

```
Tool: mcp__apify__fetch-actor-details
Actor ID: [from search results]
```

Review the input schema to understand required fields.

#### 2c. Run the actor

```
Tool: mcp__apify__call-actor
Actor ID: [selected actor]
Input: {
  // Varies by actor — always check schema from step 2b
  // Common patterns:
  "startUrls": [{"url": "<linkedin_url>"}],  // or "searchUrl", "urls"
  "maxResults": <limit>,
  "proxy": {"useApifyProxy": true}
}
```

**Important:** Set `async: false` for small runs (<50 records), `async: true` for larger runs.

#### 2d. Get results

```
Tool: mcp__apify__get-actor-output
Run ID: [from call-actor response]
Format: "json"
```

### Step 3: Transform Scraped Data

Map Apify output fields to Attio-compatible format. Use the field mapping from `references/field-mapping.md`.

**Core transformation logic** (execute in a Code node or inline):

```javascript
function transformProfiles(items) {
  return items.map(item => ({
    // People fields
    full_name: item.fullName || item.name || `${item.firstName || ''} ${item.lastName || ''}`.trim(),
    email: item.email || item.emailAddress || null,
    phone: normalizePhone(item.phone || item.phoneNumber || null),
    title: item.title || item.headline || item.position || null,
    company_name: item.companyName || item.company || null,
    linkedin_url: item.linkedInUrl || item.profileUrl || item.url || null,
    location: item.location || item.geoLocation || null,
    // Company fields (if scraping companies)
    domain: item.website || item.companyUrl || null,
    industry: item.industry || null,
    employee_count: item.employeeCount || item.staffCount || null,
    description: item.description || item.about || null,
  }));
}

function normalizePhone(phone) {
  if (!phone) return null;
  let digits = phone.replace(/\D/g, '');
  // Israeli numbers: 05X or 0X → +972
  if (/^0[2-9]/.test(digits) && digits.length === 10) {
    digits = '972' + digits.slice(1);
  }
  return '+' + digits;
}
```

### Step 4: n8n Workflow (Optional)

If the user wants a persistent/repeatable pipeline, build an n8n workflow:

Use the `n8n-workflow-builder` skill patterns. The workflow should have:

1. **Webhook Trigger** — receives scraped data as POST body
2. **Code Node** — transforms data using the mapping from Step 3
3. **HTTP Request Node** — upserts each record to Attio

```
Tool: mcp__n8n__search_nodes
Query: "webhook"
```

For one-time runs, skip n8n and push directly to Attio from Step 5.

### Step 5: Attio CRM — Upsert Records

Push transformed records to Attio using the API.

#### People upsert

```bash
curl -X PUT "https://api.attio.com/v2/objects/people/records?matching_attribute=email_addresses" \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(cat <<'BODY'
{
  "data": {
    "values": {
      "name": [{"full_name": "<full_name>"}],
      "email_addresses": [{"email_address": "<email>"}],
      "phone_numbers": [{"original_phone_number": "<phone_e164>"}],
      "job_title": [{"value": "<title>"}],
      "linkedin": [{"value": "<linkedin_url>"}]
    }
  }
}
BODY
)"
```

#### Companies upsert

```bash
curl -X PUT "https://api.attio.com/v2/objects/companies/records?matching_attribute=domains" \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(cat <<'BODY'
{
  "data": {
    "values": {
      "name": [{"value": "<company_name>"}],
      "domains": [{"domain": "<domain>"}],
      "description": [{"value": "<description>"}]
    }
  }
}
BODY
)"
```

#### Link person to company

After upserting both, link via:
```
PUT /v2/objects/people/records?matching_attribute=email_addresses
Include "company" attribute with company record ID
```

### Step 5b: Add Records to List (if list specified)

If the user specified an Attio list in Step 1, add each upserted record to that list.

#### Create list (if it doesn't exist)

```bash
curl -X POST "https://api.attio.com/v2/lists" \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "<list_name>",
      "api_slug": "<snake_case_slug>",
      "parent_object": "companies",
      "workspace_access": "full-access",
      "workspace_member_access": []
    }
  }'
```

#### Add record to list

For each upserted record, create a list entry using the `record_id` from the upsert response:

```bash
curl -X POST "https://api.attio.com/v2/lists/{list_id}/entries" \
  -H "Authorization: Bearer $ATTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "parent_record_id": "<record_id from upsert response>",
      "parent_object": "companies",
      "entry_values": {
        "country": "<country from Step 1>",
        "city": "<city from Step 1>",
        "source": "<source from Step 1, default: Scraped>"
      }
    }
  }'
```

**Note:** If the list has Country/City/Source select attributes, always populate `entry_values` with the geography and source from Step 1. Omit any field that wasn't provided by the user.

**Critical:** `parent_object` is **required** — omitting it causes a silent failure where the API accepts the call but no entry appears in the list. Set it to `"companies"` or `"people"` matching the list's `parent_object` setting.

**Scopes needed:** `list_entry:read-write`, `list_configuration:read`

**Notes:**
- Multiple entries for the same parent record are allowed
- Throws on unique attribute conflicts if the list has unique constraints

### Step 6: Report Results

Present a summary table:

```
## Scrape-to-CRM Results

**Source:** [LinkedIn URL or search query]
**Actor:** [actor name used]
**Records scraped:** X
**Records pushed to Attio:** Y (Z new, W updated)
**Failures:** N

| Name | Title | Company | Email | Status |
|------|-------|---------|-------|--------|
| ... | ... | ... | ... | Created/Updated/Failed |
```

## Attio API Gotchas

Reference: `~/.claude/skills/lead-enrichment/references/api-patterns.md`

- **`name` attribute** → must use `full_name` field, NOT `value`
- **Phone numbers** → use `original_phone_number` field, must be E.164 format
- **Israeli numbers** → strip non-digits, replace leading `0` with `+972`
- **Body serialization** → always use `JSON.stringify()` — string concat breaks with special chars
- **Matching attributes** → People: `email_addresses`, Companies: `domains`
- **Rate limits** → Attio allows ~10 req/s; add 100ms delay between upserts for bulk

## Environment Variables

Read from `~/.env` or project `.env`:
- `APIFY_API_TOKEN` — required for Apify actor runs
- `ATTIO_API_KEY` — required for CRM upserts
- `N8N_API_KEY` — optional, only if building n8n workflow

## Error Handling

- **Apify actor fails** → show error, suggest alternative actor via `search-actors`
- **No email in scraped data** → skip Attio People upsert for that record, note in report
- **Attio upsert fails** → log the record and error, continue with remaining records
- **Rate limit hit** → back off with exponential delay (100ms → 200ms → 400ms)
- **Partial results** → always report what succeeded vs. failed; never silently drop records

## Testing

Run `/scrape-to-crm test` to execute a dry-run:
1. Asks for a small LinkedIn URL (company page with <10 employees)
2. Runs Apify scrape with `maxResults: 5`
3. Transforms data and displays mapped fields (no CRM push)
4. User confirms → pushes to Attio
5. Verifies records exist via Attio API GET
