# Professional Services Playbook

## Overview

**Target Profile:**
- 10+ active clients minimum
- Sweet spot: 50-500 clients
- Includes: Consultants, Agencies, Accountants, Coaches

**Key Decision Makers:**
- Founder/Owner (small firms)
- Operations Manager
- Managing Partner

---

## Top Pain Points

### 1. Lead Leakage
**Symptoms:**
- Leads sit in inbox for hours/days
- No systematic follow-up
- Lost track of inquiries

**Questions:**
- "How do leads typically reach you?"
- "What happens when a lead comes in at 10pm?"
- "How many leads do you think you've lost to slow response?"

**Automation:**
- Instant lead alerts (Slack/SMS)
- Auto-reply with next steps
- CRM auto-entry

**ROI Calculation:**
```
Monthly leads × % lost to slow response × Average deal value
Example: 20 leads × 25% lost × $3,000 = $15,000/month opportunity
```

---

### 2. Onboarding Chaos
**Symptoms:**
- Chasing clients for documents
- Repeated setup tasks
- Delayed project starts

**Questions:**
- "Walk me through onboarding a new client."
- "How long from signed contract to project start?"
- "What documents do you need from every client?"

**Automation:**
- Welcome sequence
- Document request workflow
- Auto-reminders until complete
- Internal checklist tracking

**ROI Calculation:**
```
New clients/month × Hours on onboarding × Hourly rate
Example: 5 clients × 4 hours × $150 = $3,000/month
```

---

### 3. Invoicing & Collections
**Symptoms:**
- Late invoices
- Manual payment follow-ups
- Cash flow gaps

**Questions:**
- "How do you track billable hours?"
- "What's your average days-to-payment?"
- "Who chases overdue invoices?"

**Automation:**
- Auto-invoice generation
- Payment reminders (3/7/14 day)
- Thank you on payment
- Overdue escalation

**ROI Calculation:**
```
Monthly revenue × (Current DSO - Target DSO) / 365 × Cost of capital
Plus: Hours/month on collections × Hourly rate
```

---

### 4. Communication Gaps
**Symptoms:**
- Client asks for updates
- Internal handoff issues
- "I thought you were handling that"

**Questions:**
- "How do clients know what's happening with their project?"
- "How does your team share client info?"
- "What falls through the cracks?"

**Automation:**
- Automated status updates
- Internal milestone alerts
- Client portal updates
- Team notifications

**ROI Calculation:**
```
Client complaints/month × Time to resolve × Hourly rate
Plus: Churn risk × Client LTV
```

---

## Workflow Bundles

### Quick Win Package ($200-400)
**Time to deliver:** 1 day

1. **New Lead Alert**
   - Instant Slack/email
   - Lead details summary
   - One-click add to CRM

2. **Meeting Reminder**
   - 24hr + 1hr before
   - Include prep materials
   - Reschedule link

---

### Starter Bundle ($600-1,000)
**Time to deliver:** 2-3 days

1. Quick Win Package +
2. **Lead Auto-Response**
   - Instant reply
   - Calendar booking link
   - "What to expect" info

3. **Invoice Reminder Sequence**
   - Due date reminder
   - 3-day overdue
   - 7-day escalation
   - Thank you on payment

---

### Growth Bundle ($1,500-2,500)
**Time to deliver:** 1 week

1. Starter Bundle +
2. **Client Onboarding Flow**
   - Welcome email sequence
   - Document request
   - Auto-reminders
   - Completion notification

3. **Project Status Updates**
   - Milestone notifications
   - Weekly summary emails
   - Client-facing portal sync

4. **Referral Request Flow**
   - Trigger after project success
   - Easy referral mechanism
   - Thank you automation

---

### Enterprise Bundle ($3,000-10,000)
**Time to deliver:** 2-3 weeks

1. Growth Bundle +
2. **Full Practice Management**
   - Time tracking integration
   - Project milestone automation
   - Resource allocation alerts

3. **AI Email Assistant**
   - Draft responses to inquiries
   - Proposal generation help
   - Meeting notes summary

4. **Client Success Dashboard**
   - Engagement scoring
   - Churn risk alerts
   - Upsell triggers

---

## Node Patterns

### Lead Capture
```javascript
// Form submission → CRM + Alert
{
  "trigger": "webhook",
  "flow": [
    "Parse form data",
    "Create CRM contact",
    "Send Slack alert",
    "Send auto-reply email"
  ]
}
```

### Invoice Reminder
```javascript
// Check overdue invoices daily
{
  "trigger": "schedule (daily 9am)",
  "flow": [
    "Get invoices from Stripe/QB",
    "Filter overdue",
    "Send reminder email",
    "Update CRM task"
  ]
}
```

### Onboarding Sequence
```javascript
// New client → Welcome flow
{
  "trigger": "deal marked 'Closed Won'",
  "flow": [
    "Day 0: Welcome email + docs request",
    "Day 2: Reminder if no docs",
    "Day 5: Call scheduling",
    "Day 7: Kickoff prep"
  ]
}
```

---

## Integrations

### Common Stack
- **CRM:** HubSpot, Pipedrive, Salesforce, Close
- **Scheduling:** Calendly, Acuity, Cal.com
- **Invoicing:** Stripe, QuickBooks, FreshBooks, Xero
- **Contracts:** PandaDoc, DocuSign, HelloSign
- **Project:** Asana, Monday, ClickUp, Notion
- **Email:** Gmail, Outlook, Front

### Integration Complexity
| Integration | Difficulty | Time |
|-------------|------------|------|
| HubSpot | Easy | 30 min |
| Calendly | Easy | 15 min |
| Stripe | Easy | 30 min |
| QuickBooks | Medium | 1 hr |
| Salesforce | Hard | 2+ hrs |

---

## Pricing Guide

### By Firm Size
| Team Size | Quick Win | Full Suite | Retainer |
|-----------|-----------|------------|----------|
| 1-5 | $200 | $800 | $250/mo |
| 6-15 | $300 | $1,500 | $400/mo |
| 16-50 | $400 | $2,500 | $700/mo |
| 50+ | $500 | Custom | $1,000+/mo |

### Value Calculation
```
Billable hours lost to admin × Hourly rate = Waste
Example: 10 hrs/week × $200/hr = $8,000/month
Capture 25% = $2,000/mo value → Price at $400-600/mo
```

---

## Case Study Template

### Challenge
[Firm] is a 12-person consulting firm handling 80+ active clients. Partners were:
- Missing lead responses (2+ day average)
- Chasing invoices manually
- Losing 15 hours/week to admin

### Solution
1. **Lead Response Bot** - Instant reply + CRM entry
2. **Smart Invoicing** - Auto-generate + reminder sequence
3. **Client Portal** - Status updates without email

### Results
- Lead response: 2 days → 5 minutes
- DSO reduced from 45 to 28 days
- 12 hours/week reclaimed per partner
- 3 additional clients closed (attributed to speed)

### ROI
- Investment: $1,500 setup + $400/mo
- Monthly value: $6,400
- Payback: 1 week

---

## Objection Handling

| Objection | Response |
|-----------|----------|
| "We're relationship-based" | "Exactly - automation handles admin so you focus on relationships." |
| "Our process is unique" | "That's why we custom-build. Cookie-cutter doesn't work here." |
| "Clients expect personal touch" | "They'll get MORE personal attention when you're not buried in admin." |
| "We tried software before" | "Software requires you to use it. Automation works in the background." |
| "Can't afford it now" | "You're already paying more in lost leads and admin time." |

---

## Discovery Questions

1. "How do new clients typically find you?"
2. "What happens when a lead comes in on a weekend?"
3. "Walk me through signing a new client to kickoff."
4. "How do you track your time?"
5. "What's your invoicing process?"
6. "How do you handle overdue payments?"
7. "How do clients know what's happening with their project?"
8. "What admin tasks do you hate most?"
9. "How many hours per week on non-billable work?"
10. "What would you do with 10 extra hours per week?"
