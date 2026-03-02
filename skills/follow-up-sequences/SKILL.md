---
name: follow-up-sequences
description: Multi-channel follow-up orchestration with AI message generation and CRM tracking. Use when user says "follow up", "sequence", "nurture leads", "re-engage stale leads", "outreach cadence", or needs to set up or manage follow-up campaigns.
---

# Follow-Up Sequences

Orchestrate multi-channel follow-up sequences across Email, WhatsApp, LinkedIn, and Telegram -- with AI-generated context-aware messages, timing rules, and full CRM tracking.

## When to Use

- "Set up follow-up sequences" or "create a nurture campaign"
- "Who needs follow-up today?"
- "Re-engage stale leads"
- "What's the follow-up cadence?"
- "Generate follow-up message for [lead]"
- After a batch of leads enters the pipeline

## Channel Priority

| Priority | Channel | Best For | Response Rate |
|----------|---------|----------|---------------|
| 1 | Email | First touch, formal, proposals | 5-15% |
| 2 | WhatsApp | Israel-based leads, warm leads | 30-50% |
| 3 | LinkedIn DM | B2B professionals, after connection | 15-25% |
| 4 | Telegram | Existing bot contacts | 20-30% |

### Channel Selection Logic

```javascript
function selectChannel(lead, touchNumber) {
  // Always start with email
  if (touchNumber === 1) return 'email';

  // Israel-based: WhatsApp after email
  if (lead.geo === 'IL' && lead.has_phone) {
    if (touchNumber === 2) return 'whatsapp';
    if (touchNumber === 3) return 'email';
    if (touchNumber === 4) return 'linkedin';
  }

  // International: LinkedIn after email
  if (touchNumber === 2) return 'linkedin';
  if (touchNumber === 3) return 'email';
  if (touchNumber === 4) return 'whatsapp';

  return 'email'; // fallback
}
```

## Timing Rules

| Rule | Value |
|------|-------|
| Min gap between touches | 2 days |
| Max touches per week | 3 |
| Business hours only | 8am-6pm recipient timezone |
| Blackout days | Friday (Israel), Saturday-Sunday (International) |
| Cool-off after sequence complete | 30 days before re-entering |

### Optimal Send Times

| Channel | Best Time | Worst Time |
|---------|-----------|------------|
| Email | Tue-Thu 9-11am | Friday afternoon, weekends |
| WhatsApp | Sun-Thu 10am-2pm (Israel) | After 8pm |
| LinkedIn | Tue-Wed 8-10am | Weekends |
| Telegram | Anytime (async) | - |

## Sequence Templates

### New Lead Sequence (3 touches)

**Goal:** Qualify and book discovery call

| Touch | Day | Channel | Message Type |
|-------|-----|---------|-------------|
| 1 | 0 | Email | Value-first intro + relevant insight |
| 2 | 3 | WhatsApp/LinkedIn | Short follow-up, reference email |
| 3 | 7 | Email | Case study + CTA for call |

### Qualified Lead Sequence (5 touches)

**Goal:** Move to proposal/meeting

| Touch | Day | Channel | Message Type |
|-------|-----|---------|-------------|
| 1 | 0 | Email | Personalized pain point + solution |
| 2 | 2 | WhatsApp | Quick voice note or short text |
| 3 | 5 | Email | Case study from their industry |
| 4 | 8 | LinkedIn | Share relevant content + soft ask |
| 5 | 12 | Email | Direct ask for meeting + Calendly |

### Proposal Sent Sequence (4 touches)

**Goal:** Close or get feedback

| Touch | Day | Channel | Message Type |
|-------|-----|---------|-------------|
| 1 | 2 | Email | "Any questions about the proposal?" |
| 2 | 5 | WhatsApp | Quick check-in, offer to walk through |
| 3 | 8 | Email | Add urgency (limited availability) |
| 4 | 12 | Email | Breakup: "Is this still a priority?" |

### Stale Lead Re-engagement (2 touches)

**Trigger:** 14+ days no interaction

| Touch | Day | Channel | Message Type |
|-------|-----|---------|-------------|
| 1 | 0 | Email | New value: fresh case study or insight |
| 2 | 5 | LinkedIn/WhatsApp | "Saw this and thought of you" + relevant link |

## AI Message Generation

### Context-Aware Prompt

```
You are writing a follow-up message for {{channel}}.

Lead context:
- Name: {{firstName}} {{lastName}}
- Company: {{companyName}}
- Role: {{role}}
- Industry: {{industry}}
- Previous interactions: {{interaction_summary}}
- Last message sent: {{last_message_summary}}
- Days since last touch: {{days_since_last}}
- Sequence type: {{sequence_type}}
- Touch number: {{touch_number}} of {{total_touches}}

Brand voice: {{brand_voice_description}}

Rules:
- {{channel}} format constraints (email: subject + body, WhatsApp: max 3 sentences, LinkedIn: max 300 chars)
- Reference previous interaction if applicable
- Include one clear CTA
- Sound human and conversational
- No generic filler
- If final touch: use breakup angle (respectful close)

Output format:
Subject: (email only)
Message: [the message]
```

### Brand Voice Descriptions

| Brand | Voice |
|-------|-------|
| guydvorkin.com | Authoritative but approachable. Expert who simplifies complexity. Direct, confident, no fluff. |
| exportarena.com | Practical and trade-focused. Speaks the language of importers/exporters. Data-driven, results-oriented. |
| afarsemon.com | Warm and relatable. Hebrew-first. Conversational, uses local references. Trustworthy advisor. |

## CRM Field Updates

### Fields Updated Per Touch

| Field | Value |
|-------|-------|
| `last_outreach_date` | Current timestamp |
| `sequence_status` | active / paused / completed / replied |
| `sequence_type` | new_lead / qualified / proposal / re_engagement |
| `sequence_step` | Current touch number |
| `interaction_count` | Increment by 1 |
| `next_followup_date` | Calculated based on timing rules |

### Status Transitions

```
pending → active (first touch sent)
active → replied (lead responds on any channel)
active → completed (all touches sent, no reply)
active → paused (manual pause or rate limit)
replied → (exit sequence, manual handling)
completed → re_engagement (after 30-day cool-off)
```

## n8n Orchestrator Workflow

```
Schedule Trigger (daily 8am)
  → Attio Query: leads where next_followup_date <= today AND sequence_status = active
  → Loop each lead:
    → Determine channel (Code Node)
    → Fetch interaction history from Attio
    → AI Generate message (Gemini Flash via OpenRouter)
    → Switch by channel:
      → email: Send via Smartlead API
      → whatsapp: Send via WhatsApp Business API
      → linkedin: Queue for manual send (compliance)
      → telegram: Send via Telegram Bot API
    → Update Attio: touch sent, next date, step increment
    → If final touch: set sequence_status = completed
  → Telegram summary: "Follow-ups sent: 8 email, 3 WhatsApp, 2 LinkedIn queued"
```

### Reply Detection

```
Smartlead Webhook (reply received)
  → Parse reply email
  → Match to Attio record by email
  → Update sequence_status = "replied"
  → Notify via Telegram: "Reply from {{name}} at {{company}}"
  → Create Attio note with reply content
```

## Quick Reference

| Task | Method |
|------|--------|
| Check who needs follow-up | Attio MCP: filter by next_followup_date |
| Generate follow-up message | AI prompt with lead context |
| Send email follow-up | Smartlead API |
| Send WhatsApp follow-up | WhatsApp Business API |
| Pause a sequence | Attio MCP: update sequence_status = "paused" |
| Re-engage stale leads | Filter 14+ days inactive, start re-engagement sequence |
| View sequence history | Attio MCP: get_record_details + list_notes |

## Error Handling

- Lead replied but not detected: daily scan for unmatched replies in Smartlead
- WhatsApp delivery failed: fall back to email, note failure in CRM
- AI message too long for channel: truncate and add "..." or regenerate with stricter constraint
- Rate limit on any channel: pause channel, continue others, alert via Telegram
- Sequence stuck (no status update in 7 days): flag for manual review
- Duplicate sequence: check sequence_status before starting, skip if already active
