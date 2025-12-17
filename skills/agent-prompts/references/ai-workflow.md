# AI Workflow Agent Prompts

Use these prompts with the `llm-engineer` agent for AI-powered n8n workflows.

---

## Basic AI Workflow Prompt

```
Create an AI-powered workflow:

**AI Task:** [classify / summarize / generate / extract / analyze]
**Model:** Claude (fallback to Gemini if rate limited)
**Input:** [webhook payload / email / form / document]
**Output format:** [JSON / markdown / plain text]

Include:
- System prompt template with clear instructions
- Input variable placeholders
- Token usage estimation
- Fallback logic if primary model fails
- Response validation before using output
```

---

## Customer Support AI Agent

```
Build an AI customer support agent:

**Trigger:** [email / chat widget / form submission]
**Knowledge base:** [URL / documents / database]

Agent capabilities:
1. Answer FAQs using knowledge base
2. Classify ticket type: [list categories]
3. Determine sentiment: positive/neutral/negative
4. Extract key information: [customer ID, order number, etc.]

Response rules:
- Confident answer (>80%): Auto-respond
- Medium confidence (50-80%): Draft for human review
- Low confidence (<50%): Route to human immediately

Tone: [professional / friendly / formal]
Language: [English / Hebrew / detect and match]

Escalation triggers:
- Keywords: [angry, urgent, lawyer, refund, etc.]
- Sentiment: negative
- Repeat contact within 24 hours
```

---

## Document Processing AI

```
Build a document analysis workflow:

**Input:** [PDF / email attachment / uploaded file]
**Document types:** [invoices / contracts / receipts / forms]

Extract:
1. [Field 1]: [description]
2. [Field 2]: [description]
3. [Field 3]: [description]

Output:
- Structured JSON with extracted fields
- Confidence score for each field
- Flag items needing human review

Processing:
- Use Gemini for document vision (PDFs/images)
- Use Claude for text analysis
- Validate extracted data against schema

Post-processing:
- [Where to save extracted data]
- [Notification on completion]
- [Human review queue for low confidence]
```

---

## Lead Qualification AI

```
Build an AI lead scoring workflow:

**Trigger:** New lead from [source]

Scoring criteria:
- Company size: [scoring rules]
- Industry: [preferred industries +points]
- Budget indicated: [scoring rules]
- Urgency signals: [keywords to detect]
- Engagement level: [form fields completed, etc.]

AI tasks:
1. Enrich lead data (search company info)
2. Classify industry and company size
3. Detect buying signals in message
4. Generate personalized response suggestion
5. Assign score 1-100

Routing:
- Score 80+: Hot → Immediate sales alert
- Score 50-79: Warm → Nurture sequence
- Score <50: Cold → Monthly newsletter only

Output:
- Lead score with reasoning
- Recommended next action
- Personalized outreach draft
```

---

## Email Response Generator

```
Build an AI email assistant:

**Trigger:** [new email / tagged email / manual]
**Context:** [CRM data / conversation history / knowledge base]

Generate:
- Professional reply addressing all points
- Match sender's tone/formality
- Include relevant information from context
- Suggest follow-up actions

Constraints:
- Max length: [X] words
- Never commit to specific dates/times
- Always include [specific required elements]
- Forbidden topics: [list any]

Output:
- Draft email (not auto-sent)
- Suggested subject line
- Recommended CC recipients
- Confidence score

Review workflow:
- High confidence (>90%): Queue in drafts
- Medium: Show for quick edit
- Low: Route to human with AI notes
```

---

## Content Summarizer

```
Build a content summarization workflow:

**Input sources:**
- [URLs / RSS feeds / documents / meeting transcripts]

Summary types:
1. Executive summary: 2-3 sentences
2. Key points: Bullet list
3. Action items: Extracted tasks
4. Questions raised: Items needing clarification

Output format:
- Slack message to #[channel]
- And/or email to [recipient]
- And/or save to [Notion/database]

Scheduling:
- [Real-time / daily digest / weekly roundup]

Customization:
- Focus areas: [what to emphasize]
- Ignore: [what to skip]
- Flag if contains: [important keywords]
```

---

## Meeting Notes AI

```
Build an AI meeting notes processor:

**Input:** [Transcript from Zoom/Teams / Audio file / Manual paste]

Extract:
1. Meeting summary (3-5 sentences)
2. Key decisions made
3. Action items with owners
4. Open questions/parking lot
5. Next steps and timeline

Output:
- Formatted notes document
- Tasks auto-created in [Asana/Notion/etc.]
- Calendar events for follow-ups
- Email summary to participants

Additional AI tasks:
- Identify speakers (if transcript allows)
- Detect sentiment/concerns
- Link to previous meeting notes (context)
```

---

## Multi-Model Fallback Pattern

```
Build a workflow with AI fallback:

**Primary model:** Claude (claude-sonnet-4-20250514)
**Fallback model:** Gemini (gemini-1.5-flash)

Fallback triggers:
- Rate limit (429 response)
- Timeout (>30 seconds)
- Error response (5xx)
- Content filter block

Implementation:
1. Try primary model
2. If failed: Log reason, try fallback
3. If fallback fails: Queue for retry + alert
4. Track model usage for cost monitoring

Response normalization:
- Ensure same output format regardless of model
- Log which model was used
- Track quality differences (optional)
```

---

## AI Agent with Tools

```
Build an AI agent with tool access:

**Agent purpose:** [describe what the agent does]
**Model:** Claude (required for complex tool use)

Available tools:
1. **[Tool Name]**: [description of what it does]
   - When to use: [clear criteria]
   - Input: [what it needs]
   - Output: [what it returns]

2. **[Tool Name]**: [description]
   - When to use: [criteria]
   - Input: [needs]
   - Output: [returns]

Agent instructions:
- [Specific guidance for the agent]
- [Boundaries - what NOT to do]
- [Required confirmations before actions]

Human handoff:
- Trigger when: [conditions]
- How: [Slack message / email / queue]
- Include: [context to pass to human]
```

---

## Data Extraction Prompt Template

```
You are a data extraction specialist. Extract the following information from the provided [document type].

EXTRACT THESE FIELDS:
1. [field_name]: [description and format]
2. [field_name]: [description and format]
3. [field_name]: [description and format]

RULES:
- If a field is not found, return null
- If uncertain, include confidence score (0-100)
- Dates should be in ISO 8601 format (YYYY-MM-DD)
- Currency should include symbol and amount as number
- Extract exactly as written, don't interpret

OUTPUT FORMAT (JSON):
{
  "field_name": "value",
  "field_name": "value",
  "_confidence": {
    "field_name": 95,
    "field_name": 80
  },
  "_notes": "Any relevant observations"
}

DOCUMENT:
{{ $json.document_content }}
```

---

## Classification Prompt Template

```
You are a classifier. Categorize the following [item type] into exactly one of these categories:

CATEGORIES:
1. [Category A]: [description of what belongs here]
2. [Category B]: [description]
3. [Category C]: [description]
4. [Other]: Only if truly doesn't fit any category

RULES:
- Choose the single best category
- If borderline, prefer [preference]
- Consider [specific factors]

OUTPUT FORMAT (JSON):
{
  "category": "[chosen category]",
  "confidence": [0-100],
  "reasoning": "[one sentence explanation]"
}

INPUT:
{{ $json.content }}
```

---

## Tips for AI Workflows

1. **Always validate AI output** before using it downstream
2. **Include confidence scores** for decision making
3. **Log prompts and responses** for debugging
4. **Set token limits** to control costs
5. **Use structured output** (JSON) when possible
6. **Plan for model failures** with fallbacks
7. **Monitor costs** - AI calls add up
8. **Test with edge cases** before production
