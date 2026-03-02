#!/usr/bin/env python3
"""
Lead Enrichment Orchestrator
Parallel API calls to Apify + OpenRouter, then LLM synthesis.
Mirrors the n8n shared.13 + shared.14 pipeline.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp required. Install with: pip install aiohttp", file=sys.stderr)
    sys.exit(1)


def load_env():
    """Load env vars from .env files."""
    for env_path in [
        Path.cwd() / ".env",
        Path.home() / "Documents/_projects/n8n-automations/.env",
        Path.home() / ".env",
        Path(__file__).resolve().parents[3] / ".env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    if key:
                        os.environ[key] = value


load_env()

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
ATTIO_KEY = os.environ.get("ATTIO_API_KEY", "")

APIFY_BASE = "https://api.apify.com/v2/acts"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
ATTIO_BASE = "https://api.attio.com/v2"

TIMEOUT = aiohttp.ClientTimeout(total=60)


async def google_search(session: aiohttp.ClientSession, query: str) -> dict | None:
    """Search Google via Apify scraper."""
    if not query or not APIFY_TOKEN:
        return None
    url = f"{APIFY_BASE}/apify~google-search-scraper/run-sync-get-dataset-items"
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}
    payload = {"queries": query, "maxPagesPerQuery": 1, "resultsPerPage": 5}
    try:
        async with session.post(url, json=payload, headers=headers, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
    except Exception as e:
        return {"error": str(e)}
    return None


async def perplexity_research(session: aiohttp.ClientSession, query: str, system_prompt: str) -> str | None:
    """Query Perplexity Sonar Pro via OpenRouter."""
    if not query or not OPENROUTER_KEY:
        return None
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "perplexity/sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "max_tokens": 2000,
    }
    try:
        async with session.post(OPENROUTER_URL, json=payload, headers=headers, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception as e:
        return f"Error: {e}"
    return None


async def linkedin_scrape(session: aiohttp.ClientSession, linkedin_url: str) -> dict | None:
    """Scrape LinkedIn profile via Apify."""
    if not linkedin_url or not APIFY_TOKEN:
        return None
    url = f"{APIFY_BASE}/anchor~linkedin-profile-scraper/run-sync-get-dataset-items"
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}
    payload = {"profileUrls": [linkedin_url]}
    try:
        async with session.post(url, json=payload, headers=headers, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data[0] if isinstance(data, list) and data else data
    except Exception as e:
        return {"error": str(e)}
    return None


async def company_enrichment(session: aiohttp.ClientSession, company: str, domain: str) -> dict | None:
    """Enrich company data via Apify."""
    if not company or not APIFY_TOKEN:
        return None
    url = f"{APIFY_BASE}/vivid_astronaut~company-enrichment/run-sync-get-dataset-items"
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}
    payload = {"companies": [{"name": company, "domain": domain or ""}]}
    try:
        async with session.post(url, json=payload, headers=headers, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data[0] if isinstance(data, list) and data else data
    except Exception as e:
        return {"error": str(e)}
    return None


async def synthesize(session: aiohttp.ClientSession, raw_data: dict) -> dict:
    """Synthesize all research into structured lead profile via Gemini 2.5 Flash."""
    if not OPENROUTER_KEY:
        return {"error": "OPENROUTER_API_KEY not set"}

    system_prompt = (
        "You are creating a comprehensive lead profile by merging data from multiple sources.\n\n"
        "Create a unified lead profile with these rules:\n"
        "1. Original input takes priority over research for direct facts (name, email, phone)\n"
        "2. Enrich with research data: company size, funding, LinkedIn, social links, recent news\n"
        "3. Generate a 2-3 sentence \"context\" summary useful for first outreach\n"
        "4. Adjust lead_score based on enrichment (company size, funding = higher score)\n"
        "5. Score using Export Arena ICP: export/import companies, AI readiness, 50-500 employees = highest scores\n\n"
        "Return JSON:\n"
        "{\n"
        '  "first_name": "",\n'
        '  "last_name": "",\n'
        '  "company": "",\n'
        '  "job_title": "",\n'
        '  "email": "",\n'
        '  "phone": "",\n'
        '  "website": "",\n'
        '  "linkedin": "",\n'
        '  "industry": "",\n'
        '  "company_size": "",\n'
        '  "context": "enriched summary for outreach",\n'
        '  "lead_score": 0,\n'
        '  "lead_source": "",\n'
        '  "business_brand": "",\n'
        '  "enrichment_notes": "full research notes for CRM",\n'
        '  "icp_tier": "hot|warm|cold",\n'
        '  "export_markets": [],\n'
        '  "import_sources": [],\n'
        '  "trade_products": [],\n'
        '  "recent_news": [],\n'
        '  "tech_stack": [],\n'
        '  "decision_makers": []\n'
        "}"
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Lead data: {json.dumps(raw_data, default=str)}"},
        ],
        "max_tokens": 1500,
        "temperature": 0,
    }

    try:
        async with session.post(OPENROUTER_URL, json=payload, headers=headers, timeout=TIMEOUT) as resp:
            body = await resp.text()
            if resp.status != 200:
                return {"error": f"OpenRouter returned {resp.status}: {body[:200]}"}
            data = json.loads(body)
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "LLM returned invalid JSON", "raw": content}
    except Exception as e:
        return {"error": f"Synthesis failed: {e}"}


async def enrich(company: str, domain: str, email: str, linkedin: str, name: str, write_crm: bool) -> dict:
    """Main enrichment pipeline."""
    # Build search queries
    search_parts = [company or "", domain or ""]
    if name:
        search_parts.append(name)
    google_query = " ".join(p for p in search_parts if p)

    perplexity_query = (
        f"Deep research on this person/company for enterprise sales outreach. "
        f"Find: complete company profile, key decision makers, recent funding/acquisitions, "
        f"competitive landscape, technology stack, company culture, pain points that our "
        f"export/import automation services could address. Query: {google_query}"
    )

    trade_query = (
        f"Research the international trade activity for company: {company or domain}. "
        f"Find: export markets, import sources, trade volume estimates, key products traded, "
        f"trade partnerships, customs/regulatory considerations. If not a trading company, "
        f"analyze their supply chain for import/export opportunities. "
        f"Return JSON with fields: export_markets[], import_sources[], trade_products[], "
        f"trade_volume_estimate, trade_opportunities[]"
    )

    trade_system = "You are an international trade analyst. Return structured JSON with export/import data relevant to the company."
    perplexity_system = (
        "You are a premium business intelligence researcher. Provide comprehensive, "
        "structured analysis useful for B2B sales outreach. Include specific facts, numbers, "
        "and recent developments."
    )

    async with aiohttp.ClientSession() as session:
        # Run all sources in parallel
        results = await asyncio.gather(
            google_search(session, google_query),
            perplexity_research(session, perplexity_query, perplexity_system),
            linkedin_scrape(session, linkedin),
            company_enrichment(session, company, domain),
            perplexity_research(session, trade_query, trade_system),
            return_exceptions=True,
        )

        raw_data = {
            "input": {"company": company, "domain": domain, "email": email, "linkedin_url": linkedin, "name": name},
            "google_results": results[0] if not isinstance(results[0], Exception) else None,
            "perplexity_results": results[1] if not isinstance(results[1], Exception) else None,
            "linkedin_data": results[2] if not isinstance(results[2], Exception) else None,
            "company_data": results[3] if not isinstance(results[3], Exception) else None,
            "trade_data": results[4] if not isinstance(results[4], Exception) else None,
        }

        # Synthesize
        enriched = await synthesize(session, raw_data)

        # Optional CRM write-back
        if write_crm and ATTIO_KEY and enriched.get("company"):
            crm_result = await write_to_attio(session, enriched)
            enriched["_crm_write"] = crm_result

        return enriched


async def write_to_attio(session: aiohttp.ClientSession, lead: dict) -> dict:
    """Upsert lead data to Attio CRM."""
    headers = {
        "Authorization": f"Bearer {ATTIO_KEY}",
        "Content-Type": "application/json",
    }

    results = {}

    # Upsert company
    if lead.get("company"):
        company_payload = {
            "data": {
                "values": {
                    "name": [{"value": lead["company"]}],
                    **({"domains": [{"domain": lead["website"]}]} if lead.get("website") else {}),
                }
            }
        }
        try:
            async with session.put(
                f"{ATTIO_BASE}/objects/companies/records?matching_attribute=domains",
                json=company_payload,
                headers=headers,
            ) as resp:
                results["company"] = "ok" if resp.status in (200, 201) else f"error:{resp.status}"
        except Exception as e:
            results["company"] = f"error:{e}"

    # Upsert person
    if lead.get("email"):
        person_payload = {
            "data": {
                "values": {
                    "email_addresses": [{"email_address": lead["email"]}],
                    **({"name": [{"full_name": f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()}]} if lead.get("first_name") else {}),
                }
            }
        }
        try:
            async with session.put(
                f"{ATTIO_BASE}/objects/people/records?matching_attribute=email_addresses",
                json=person_payload,
                headers=headers,
            ) as resp:
                results["person"] = "ok" if resp.status in (200, 201) else f"error:{resp.status}"
        except Exception as e:
            results["person"] = f"error:{e}"

    return results


def main():
    parser = argparse.ArgumentParser(description="Enrich a lead with multi-source intelligence")
    parser.add_argument("--company", default="", help="Company name")
    parser.add_argument("--domain", default="", help="Company domain")
    parser.add_argument("--email", default="", help="Contact email")
    parser.add_argument("--linkedin", default="", help="LinkedIn URL")
    parser.add_argument("--name", default="", help="Contact person name")
    parser.add_argument("--write-crm", action="store_true", help="Write results to Attio CRM")
    parser.add_argument("--raw", action="store_true", help="Output raw data before synthesis")
    args = parser.parse_args()

    if not any([args.company, args.domain, args.email, args.linkedin]):
        parser.error("At least one of --company, --domain, --email, or --linkedin is required")

    result = asyncio.run(enrich(args.company, args.domain, args.email, args.linkedin, args.name, args.write_crm))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
