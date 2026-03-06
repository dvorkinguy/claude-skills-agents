---
name: youtube-content-ideator
description: Generate YouTube video ideas for AI Automation for Business channel. Scans trending tools, analyzes competitor channels, finds content gaps, and outputs ranked video ideas. Use when user says "youtube ideas", "video topics", "content ideation", "what should I film", or needs YouTube content strategy.
---

# YouTube Content Ideator

Generate 10 ranked video ideas for the **AI Automation for Business** YouTube channel by scanning trends, analyzing competitors, and finding content gaps.

## Quick Actions

| Need | Action |
|------|--------|
| Full ideation run | -> Run all 3 phases below |
| Quick trends only | -> Phase 1 only |
| Competitor check | -> Phase 2 only |
| Refresh ideas | -> Phase 3 with cached data |
| Video brief | -> `assets/templates/video-brief.md` |
| Competitor list | -> `references/competitors.md` |
| X influencers | -> `references/x-influencers.md` |

---

## Content Pillars

| Pillar | % | Topics |
|--------|---|--------|
| Tool Reviews & Demos | 30% | New AI tools, side-by-side comparisons, "I tried X for 7 days" |
| Tutorials & How-To | 25% | Build automations, integrate tools, step-by-step walkthroughs |
| Strategy & Business | 20% | AI agency models, pricing, client acquisition, scaling |
| News & Trends | 15% | Weekly AI news, product launches, industry shifts |
| Behind the Scenes | 10% | Client projects, revenue reports, workflow reveals |

---

## Phase 1: Trending Tools Scan

**Goal:** Identify top 15 AI trends from the last 7 days ranked by buzz + business relevance.

### Step 1A: Web Search (3 parallel calls)

Run these `WebSearch` queries in parallel:

1. `"new AI tool launch" OR "AI product launch" site:producthunt.com OR site:news.ycombinator.com` (last 7 days)
2. `"AI automation tool" OR "AI agent" new launch 2026` (last 7 days)
3. `"best new AI tools" OR "AI tools this week" 2026` (last 7 days)

### Step 1B: AI News Search (2 parallel calls)

4. `"AI news this week" OR "AI update" site:theverge.com OR site:techcrunch.com` (last 7 days)
5. `"artificial intelligence" announcement OR launch OR release` (last 7 days)

### Step 1C: X/Twitter Influencer Scan

Use `mcp__apify__call-actor` with a Twitter/X scraper actor to fetch the latest 5-10 tweets from each account listed in `references/x-influencers.md`.

**Apify actor options (try in order):**
- `apidojo/tweet-scraper` — scrape by username
- `quacker/twitter-scraper` — alternative
- Search Apify Store with `mcp__apify__search-actors` for "twitter scraper" if above unavailable

**Extract from tweets:**
- Tool/product mentions (look for links, @mentions, product names)
- Trending topics and recurring themes
- Hot takes and debates (potential contrarian content)

### Step 1D: Optional — Research Papers (only if AI research is trending)

If web searches reveal trending research (e.g., new model architectures, benchmarks):
- `mcp__plugin_bio-research_pubmed__search_articles` — search for trending AI/ML papers
- `mcp__plugin_bio-research_biorxiv__search_preprints` — search for AI preprints

### Step 1 Output

Compile a ranked list:

| # | Trend/Tool | Source | Buzz Score (1-5) | Business Relevance (1-5) | Total |
|---|-----------|--------|-----------------|------------------------|-------|
| 1 | [Tool/Trend] | [Web/X/News] | X | X | X |
| ... | ... | ... | ... | ... | ... |
| 15 | ... | ... | ... | ... | ... |

**Buzz Score:** Social mentions, news coverage, influencer attention
**Business Relevance:** Applicability to AI automation businesses and their clients

---

## Phase 2: Competitor Analysis

**Goal:** Build a content map of what competitors posted recently and identify gaps.

### Step 2A: Fetch Competitor Videos

Use `mcp__apify__call-actor` with `streamers/youtube-scraper` to fetch recent videos from channels listed in `references/competitors.md`.

**Tiered scraping:**

| Tier | Videos to fetch | When |
|------|----------------|------|
| Tier 1 (core competitors) | 5 most recent | Every run |
| Tier 2 (adjacent) | 3 most recent | Every run |
| Tier 3 (inspiration) | 3 most recent | Full runs only |

**Actor input pattern:**
```json
{
  "searchKeywords": "",
  "maxResults": 5,
  "channelUrls": ["https://www.youtube.com/@nateherk"]
}
```

Retrieve results with `mcp__apify__get-actor-output`.

### Step 2B: Build Content Map

For each competitor video, extract:
- Title
- Topic category (map to content pillars)
- Upload date
- View count (if available)

### Step 2 Output

**Competitor Content Map:**

| Topic | Covered By | Times Covered (7d) | Avg Views | Saturation |
|-------|-----------|-------------------|-----------|------------|
| [Topic] | [Channels] | X | X | High/Med/Low |

**Gap Analysis:**
- Topics trending (Phase 1) but NOT covered by competitors
- Topics covered poorly (low views relative to channel size)
- Emerging tools no one has reviewed yet

---

## Phase 3: Cross-Reference & Generate Ideas

**Goal:** Match Phase 1 trends against Phase 2 gaps. Score and rank 10 video ideas.

### Scoring Criteria

Each idea scored out of /40:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Trend Momentum | /10 | How hot is this trend right now? Rising or peaked? |
| Gap Score | /10 | How underserved is this topic by competitors? |
| Business Relevance | /10 | How relevant to AI automation business audience? |
| Evergreen Potential | /10 | Will this still get views in 6 months? |

### Idea Categories

Categorize each idea:

- **Quick Wins** (score 30+, easy to produce, ride a trend wave)
- **Deep Dives** (score 25+, longer format, high evergreen potential)
- **Contrarian Takes** (score 20+, counter-narrative to popular opinion)

### Output Format

For each of the 10 ideas, use the template from `assets/templates/video-brief.md`:

1. **Title** (3 options: curiosity, direct, contrarian)
2. **Hook** (first 5 seconds script)
3. **Trend Driver** (which trend from Phase 1)
4. **Gap Analysis** (why competitors missed this)
5. **Format** (tutorial / review / strategy / reaction / listicle)
6. **Thumbnail Concept** (visual description)
7. **Target Keywords** (3-5 for SEO)
8. **Score Breakdown** (Trend/Gap/Biz/Evergreen = Total)

### Final Output

```
============================================
  TOP 10 VIDEO IDEAS — [Date]
  AI Automation for Business
============================================

QUICK WINS (Film This Week)
----------------------------
#1. [Title] — Score: XX/40
#2. ...

DEEP DIVES (Schedule for Next 2 Weeks)
----------------------------------------
#3. [Title] — Score: XX/40
#4. ...

CONTRARIAN TAKES (High Risk / High Reward)
-------------------------------------------
#5. [Title] — Score: XX/40
#6. ...
```

---

## Error Handling

| Issue | Fallback |
|-------|----------|
| Apify YouTube scraper fails | Use `WebSearch` for "[channel name] youtube recent videos" |
| Apify Twitter scraper fails | Use `WebSearch` for "site:x.com [handle] AI tool" |
| Too few trends found | Expand date range to 14 days |
| Competitor channel unavailable | Skip and note in output |
| PubMed/bioRxiv timeout | Skip research phase entirely |

---

## Tips

- Run weekly (ideally Monday/Tuesday) for freshest ideas
- Compare output against your own recent uploads to avoid repeats
- Quick Wins should be filmed within 48 hours of trend peak
- Deep Dives can be batched and scheduled
- Save unused ideas to a backlog for slow news weeks
