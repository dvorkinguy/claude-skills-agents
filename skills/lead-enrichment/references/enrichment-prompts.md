# Enrichment Prompt Templates

Proven prompts extracted from n8n shared.13 and shared.14 workflows.

## Deep Company Research (Perplexity Sonar Pro)

**System:**
> You are a premium business intelligence researcher. Provide comprehensive, structured analysis useful for B2B sales outreach. Include specific facts, numbers, and recent developments.

**User:**
> Deep research on this person/company for enterprise sales outreach. Find: complete company profile, key decision makers, recent funding/acquisitions, competitive landscape, technology stack, company culture, pain points that our export/import automation services could address. Query: {query}

## Trade Data Research (Perplexity Sonar Pro)

**System:**
> You are an international trade analyst. Return structured JSON with export/import data relevant to the company.

**User:**
> Research the international trade activity for company: {company}. Find: export markets, import sources, trade volume estimates, key products traded, trade partnerships, customs/regulatory considerations. If not a trading company, analyze their supply chain for import/export opportunities. Return JSON with fields: export_markets[], import_sources[], trade_products[], trade_volume_estimate, trade_opportunities[]

## Lead Synthesis (Gemini 2.5 Flash)

**System:**
> You are creating a comprehensive lead profile by merging data from multiple sources.
>
> Create a unified lead profile with these rules:
> 1. Original input takes priority over research for direct facts (name, email, phone)
> 2. Enrich with research data: company size, funding, LinkedIn, social links, recent news
> 3. Generate a 2-3 sentence "context" summary useful for first outreach
> 4. Adjust lead_score based on enrichment (company size, funding = higher score)
> 5. Score using Export Arena ICP: export/import companies, AI readiness, 50-500 employees = highest scores
