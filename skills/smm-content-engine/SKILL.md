---
name: smm-content-engine
description: Social media content creation, scheduling, and performance tracking across multiple brands and platforms. Use when user says "create content", "social media post", "content calendar", "schedule posts", "what should I post", or needs to manage multi-brand social presence.
---

# SMM Content Engine

AI-powered social media content creation and scheduling for multiple brands across LinkedIn, Twitter/X, Instagram, TikTok, and Facebook -- with multi-brand voice management and engagement tracking.

## When to Use

- "Create a LinkedIn post about [topic]"
- "Build a content calendar for this week"
- "What should I post today?"
- "Generate a carousel about AI automation"
- "Schedule posts for exportarena"
- "Social media performance report"
- Any content creation or social media planning request

## Content Pillars

| Pillar | % of Content | Topics |
|--------|-------------|--------|
| Thought Leadership | 30% | AI trends, future of work, automation philosophy, industry predictions |
| Case Studies / Results | 25% | Client wins, before/after, ROI data, transformation stories |
| Industry Insights | 20% | Market data, trade trends, technology news, research findings |
| Behind the Scenes | 15% | Process reveals, tool stack, day-in-the-life, building in public |
| Engagement / Community | 10% | Polls, questions, hot takes, responses to trends |

## Platform-Specific Formats

### LinkedIn (Primary B2B)

**Post structure:**
```
Hook line (stop the scroll)

[empty line]

3-5 short paragraphs with key insight

[empty line]

Takeaway or CTA

#relevanthashtags (3-5 max)
```

**Content types:**
- Text posts (most reach): 1200-1500 chars optimal
- Carousels (highest engagement): 8-12 slides, bold headlines
- Articles: Long-form thought leadership, monthly
- Polls: Weekly, industry-relevant questions

### Twitter/X

**Format:** Thread or single tweet
- Single: < 280 chars, punchy insight
- Thread: 5-8 tweets, numbered, standalone value per tweet
- Quote tweets of industry news with hot take

### Instagram

**Format:** Carousel, Reel, or Story
- Carousel: 5-10 slides, educational or case study
- Reel: 30-60 sec, talking head or screen recording
- Story: Behind the scenes, polls, quick tips

### TikTok

**Format:** Short video (30-90 sec)
- "How I automated X for a client"
- Tool demos and walkthroughs
- Industry myth-busting
- Day-in-the-life of solo AI consultant

### Facebook

**Format:** Cross-post from LinkedIn with slight adaptation
- More casual tone
- Add relevant group shares
- Use for community engagement

## Multi-Brand Voice Guide

### guydvorkin.com (English, Global)

**Tone:** Authoritative expert. Confident, direct, no-nonsense.
**Perspective:** "I've built AI workforces for dozens of companies. Here's what actually works."
**Audience:** CEOs, COOs, operations leaders at mid-market companies
**Avoid:** Hype, buzzwords, overpromising

```
Example post:
Most companies don't have an AI problem.

They have a process problem.

I spent last week mapping a logistics company's operations.
12 people doing work that 3 people + AI agents could handle.

Not because the people aren't good.
Because nobody ever redesigned the workflow.

AI doesn't replace people. It replaces bad processes.
```

### exportarena.com (English, Trade-Focused)

**Tone:** Practical trade expert. Data-driven, specific, actionable.
**Perspective:** "The import/export industry is ripe for AI. Here's how smart traders are adapting."
**Audience:** Importers, exporters, freight forwarders, trade professionals
**Avoid:** Generic AI content, non-trade examples

```
Example post:
A freight forwarder I work with was spending 4 hours/day
on customs documentation.

We built an AI agent that:
- Reads commercial invoices
- Maps HS codes automatically
- Generates customs declarations
- Flags compliance issues

Time spent now: 20 minutes of review.

The ROI paid for itself in week 2.
```

### afarsemon.com (Hebrew, Israel Market)

**Tone:** Warm, relatable, advisor-friend. Uses Israeli business culture references.
**Perspective:** Trusted local expert making AI accessible to Israeli businesses.
**Audience:** Israeli SMB owners, managers, entrepreneurs
**Avoid:** Over-formal language, English jargon without Hebrew explanation
**Language:** Hebrew primary, with English tech terms when natural

## AI Content Generation

### Generation Prompt

```
You are a social media content creator for {{brand}}.

Brand voice: {{voice_description}}
Platform: {{platform}}
Content pillar: {{pillar}}
Topic: {{topic}}

Recent posts (avoid repetition):
{{last_5_posts_summary}}

Audience: {{target_audience}}

Rules:
- {{platform_specific_constraints}}
- Include a hook in the first line
- One key insight or takeaway
- End with engagement driver (question, CTA, or bold statement)
- No generic advice -- be specific and opinionated
- Write in {{language}}

Output:
- Post text
- Suggested hashtags (if applicable)
- Best posting time
- Suggested visual (description for designer/AI image gen)
```

### Carousel Generation Prompt

```
Create a {{slide_count}}-slide carousel for {{platform}}.

Topic: {{topic}}
Brand: {{brand}}

Slide structure:
1. Title slide (bold claim or question)
2-{{n-1}}. Content slides (one key point per slide, large text, minimal words)
{{n}}. CTA slide (follow, save, share, or link)

Rules:
- Max 30 words per slide
- Each slide standalone valuable
- Progressive reveal (build argument)
- Use numbers and data when possible
```

## Content Calendar

### Weekly Schedule Template

| Day | Platform | Pillar | Type |
|-----|----------|--------|------|
| Sunday | LinkedIn | Thought Leadership | Text post |
| Monday | Twitter/X | Industry Insights | Thread |
| Tuesday | LinkedIn | Case Study | Carousel |
| Wednesday | Instagram | Behind the Scenes | Reel/Story |
| Thursday | LinkedIn | Engagement | Poll or question |
| Friday | - | - | Rest / engage only |

### Posting Frequency by Brand

| Brand | LinkedIn | Twitter | Instagram | TikTok |
|-------|----------|---------|-----------|--------|
| guydvorkin | 4/week | 5/week | 2/week | 1/week |
| exportarena | 3/week | 3/week | 1/week | - |
| afarsemon | 3/week | - | 2/week | 1/week |

## n8n Workflow: Weekly Content Generation

```
Schedule Trigger (Sunday 7am)
  → Code Node: Generate content calendar for the week
    - Select topics from pillar rotation
    - Check what was posted last week (avoid repeats)
  → Loop each day:
    → AI Node (Gemini Flash): Generate post for platform + brand
    → Code Node: Format and validate (length, hashtags, etc.)
    → Store in queue (Google Sheets or Notion)
  → Telegram: Send weekly calendar preview for review
  → Daily at scheduled time:
    → Fetch today's approved post
    → Auto-publish via platform API or Buffer/Typefully
    → Log to CRM (activity tracking)
```

## Engagement Tracking

### Metrics to Monitor

| Metric | LinkedIn | Twitter | Instagram |
|--------|----------|---------|-----------|
| Impressions | API | API | API |
| Engagement rate | (likes+comments+shares)/impressions | (likes+retweets+replies)/impressions | (likes+comments+saves)/reach |
| Profile visits | API | API | API |
| Follower growth | Weekly delta | Weekly delta | Weekly delta |
| Link clicks | UTM tracking | UTM tracking | Link in bio tracking |

### Feed into Lead Scoring

```
Social engagement → Lead signal:
- Commented on post: +3 points (engagement signal)
- Shared/reposted: +5 points
- Visited profile after post: +2 points
- Clicked link: +8 points
- DM'd after seeing content: +10 points
```

## Quick Reference

| Task | Method |
|------|--------|
| Generate a post | AI prompt with brand voice + platform constraints |
| Create carousel | AI prompt with slide structure |
| Plan weekly calendar | n8n workflow or manual using template |
| Schedule posts | Buffer, Typefully, or platform-native scheduling |
| Track performance | Platform APIs or analytics dashboards |
| Feed engagement to CRM | n8n webhook on engagement → update Attio |

## Error Handling

- AI generates off-brand content: regenerate with stronger voice constraints
- Post exceeds platform limit: truncate intelligently, split into thread
- Scheduling API failure: fall back to draft queue, alert for manual posting
- Engagement data unavailable: skip metrics update, note gap in reporting
- Content calendar conflict (same topic twice): dedup check against last 14 days of posts
- Hebrew content on English brand: language detection check before posting
