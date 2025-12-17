# Workflow Builder Agent Prompts

Use these prompts with the `automation-architect` agent for consistent, production-ready n8n workflows.

---

## Basic Workflow Prompt

```
Build an n8n workflow for [CLIENT_NAME]:

**Problem:** [describe the pain point they have]
**Trigger:** [webhook / schedule / manual]
**Data sources:** [list integrations needed]
**Output:** [Slack / email / database / API callback]

Requirements:
- Error handling with notifications to [channel]
- Rate limiting for external APIs (if applicable)
- Audit logging of all actions
- Include test webhook URL for development
```

---

## Lead Capture Workflow

```
Build a lead capture workflow:

**Form source:** [Typeform / Google Forms / Website form / etc.]
**CRM destination:** [HubSpot / Pipedrive / Salesforce / etc.]

Flow:
1. Receive form webhook
2. Validate required fields (name, email, phone)
3. Check for duplicate in CRM
4. If new: Create contact with tags [list tags]
5. If existing: Update and add note
6. Send Slack notification to #[channel]
7. Send welcome email to lead

Error handling:
- If CRM fails: Queue and retry
- Alert on 3 consecutive failures
```

---

## Data Sync Workflow

```
Build a bidirectional data sync:

**System A:** [e.g., Shopify]
**System B:** [e.g., NetSuite]
**Data type:** [orders / inventory / customers]

Sync rules:
- Direction: [A→B / B→A / bidirectional]
- Frequency: [real-time / every X minutes / daily]
- Conflict resolution: [newest wins / System A wins / manual review]

Include:
- Change detection (don't sync unchanged records)
- Batch processing for large datasets
- Error logging with record IDs
- Daily sync summary report
```

---

## Notification Hub Workflow

```
Build a multi-channel notification hub:

**Trigger events:**
1. [Event 1] → notify [channels]
2. [Event 2] → notify [channels]
3. [Event 3] → notify [channels]

Channels available:
- Slack: #[channel-name]
- Email: [recipient]
- SMS: [phone number]
- WhatsApp: [if applicable]

Message format:
- Include: [what data to include]
- Priority levels: [urgent/normal/low]
- Business hours: [timezone, hours]

Out-of-hours handling: [queue / escalate / send anyway]
```

---

## Report Generator Workflow

```
Build an automated report workflow:

**Schedule:** [daily at 9am / weekly Monday / monthly 1st]
**Timezone:** [timezone]

Data sources:
1. [Source 1]: Get [what data]
2. [Source 2]: Get [what data]
3. [Source 3]: Get [what data]

Report format:
- Summary metrics at top
- Comparison to previous period
- Charts/visualizations: [if needed]
- Export format: [PDF / Google Sheet / Email body]

Recipients: [list emails or Slack channels]
```

---

## E-commerce Order Workflow

```
Build an order processing workflow:

**Platform:** [Shopify / WooCommerce / etc.]
**Fulfillment:** [ShipStation / manual / 3PL]

Flow:
1. Order webhook received
2. Validate order (fraud check rules: [describe])
3. Check inventory
4. If in stock: Create fulfillment
5. Send confirmation to customer
6. Notify warehouse/team
7. Track until delivered
8. Request review 7 days post-delivery

Special handling:
- High value orders (>$[X]): [extra step]
- International orders: [extra step]
- Pre-orders: [extra step]
```

---

## Customer Support Workflow

```
Build a support ticket workflow:

**Intake sources:**
- Email: [support email]
- Form: [contact form webhook]
- Chat: [if applicable]

Routing rules:
- Contains "[keyword1]": Route to [team/person]
- Contains "[keyword2]": Route to [team/person]
- VIP customer: Escalate immediately
- Default: [default routing]

SLA tracking:
- First response: [X] hours
- Resolution: [X] hours
- Escalation after: [X] hours

Auto-responses:
- Acknowledgment email
- Out of hours message
- Ticket closed confirmation
```

---

## Scheduled Batch Process

```
Build a scheduled batch workflow:

**Schedule:** [cron expression or description]
**Timezone:** [timezone]

Process:
1. Get records from [source] where [condition]
2. For each record:
   - [Action 1]
   - [Action 2]
   - [Action 3]
3. Batch size: [X] records per run
4. On completion: Send summary

Monitoring:
- Log progress every [X] records
- Alert if processing time > [X] minutes
- Alert if error rate > [X]%

Recovery:
- Track last processed ID
- Resume from failure point
```

---

## Approval Workflow

```
Build an approval workflow:

**Trigger:** [what initiates approval request]
**Approver(s):** [who approves]

Flow:
1. Request submitted
2. Send approval request to [approver]
3. Wait for response (timeout: [X] hours)
4. If approved: [action]
5. If rejected: [action]
6. If timeout: [escalate / remind / auto-reject]

Approval interface:
- Email with approve/reject buttons
- Or: Slack interactive message
- Or: Custom form

Audit trail:
- Log who approved/rejected
- Timestamp all actions
- Store comments/reasons
```

---

## Integration Pattern

```
Build an API integration workflow:

**External API:** [API name and documentation URL]
**Authentication:** [API key / OAuth / Basic]

Operations needed:
1. [GET/POST/etc.] [endpoint]: [purpose]
2. [GET/POST/etc.] [endpoint]: [purpose]

Rate limits:
- [X] requests per [minute/hour]
- Implement queuing if needed

Error handling:
- 429 (rate limit): Wait and retry
- 401 (auth): Alert and stop
- 500 (server error): Retry with backoff
- Timeout: [X] seconds, then retry

Response validation:
- Expected fields: [list]
- Alert if schema changes
```

---

## How to Use These Prompts

1. **Copy the relevant template**
2. **Fill in the bracketed sections** with specifics
3. **Run with automation-architect agent:**
   ```
   Use the automation-architect agent to: [paste your filled prompt]
   ```
4. **Review the generated workflow**
5. **Use n8n-workflow-builder skill** to validate and deploy

---

## Tips for Better Results

- Be specific about error handling requirements
- Always specify notification channels
- Include timezone for anything scheduled
- Mention compliance/security requirements upfront
- Provide sample data formats if complex
