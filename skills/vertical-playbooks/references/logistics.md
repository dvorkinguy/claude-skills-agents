# Logistics Playbook

## Overview

**Target Profile:**
- 20+ deliveries/day minimum
- Sweet spot: 100-1000 deliveries/day
- Includes: Last-mile, Couriers, Distributors, Fleet operators

**Key Decision Makers:**
- Operations Manager
- Fleet Manager
- Founder/Owner (smaller companies)

---

## Top Pain Points

### 1. "Where's My Delivery?" Calls
**Symptoms:**
- High call volume to dispatch
- Customers calling multiple times
- Negative reviews about communication

**Questions:**
- "What percentage of calls are status inquiries?"
- "How do customers currently track deliveries?"
- "What happens when a delivery is delayed?"

**Automation:**
- Proactive ETA updates
- Real-time tracking links
- Delay notifications before customer asks

**ROI Calculation:**
```
WISMO calls/day × Cost per call × 30 days
Example: 50 calls × $5 × 30 = $7,500/month
```

---

### 2. Failed Deliveries
**Symptoms:**
- Re-delivery costs
- Angry customers
- Wasted driver time

**Questions:**
- "What's your failed delivery rate?"
- "What happens after a failed delivery?"
- "How do customers reschedule?"

**Automation:**
- Pre-delivery confirmation SMS
- Real-time "I'm here" notification
- Instant reschedule options
- Alternative delivery instructions

**ROI Calculation:**
```
Failed deliveries/month × Cost per re-delivery
Example: 200 failures × $15 = $3,000/month
```

---

### 3. Driver Communication
**Symptoms:**
- Radio/phone chaos
- Missed route changes
- Late updates from field

**Questions:**
- "How do you communicate with drivers?"
- "What happens when a route needs to change?"
- "How do drivers report issues?"

**Automation:**
- Automated dispatch notifications
- Real-time route updates
- Issue reporting workflow
- End-of-day summaries

**ROI Calculation:**
```
Dispatch coordination hours × Hourly rate
Plus: Missed deliveries from miscommunication × Cost
```

---

### 4. Proof of Delivery
**Symptoms:**
- Disputed deliveries
- Missing signatures
- Compliance issues

**Questions:**
- "How do you prove delivery happened?"
- "How many disputes do you handle monthly?"
- "What's your compliance requirement for POD?"

**Automation:**
- Photo capture at delivery
- Digital signature collection
- Automatic timestamping
- Instant availability in system

**ROI Calculation:**
```
Disputes/month × Cost per dispute + Compliance risk
Example: 20 disputes × $50 + regulatory exposure
```

---

## Workflow Bundles

### Quick Win Package ($400-600)
**Time to deliver:** 1-2 days

1. **Dispatch Confirmation**
   - Customer SMS when driver assigned
   - Driver name + vehicle info
   - Expected window

2. **ETA Update**
   - Automatic when driver nearby
   - "Driver arriving in 10 minutes"
   - Direct contact option

---

### Starter Bundle ($1,000-1,500)
**Time to deliver:** 3-5 days

1. Quick Win Package +
2. **Delivery Confirmation**
   - Real-time "Delivered" notification
   - Photo proof attached
   - Feedback request

3. **Delay Alert**
   - Proactive notification
   - New ETA provided
   - Apology + explanation

---

### Growth Bundle ($2,500-4,000)
**Time to deliver:** 1-2 weeks

1. Starter Bundle +
2. **Failed Delivery Workflow**
   - Instant "missed you" notification
   - Self-serve reschedule
   - Alternative instructions option
   - Auto-retry scheduling

3. **Driver App Integration**
   - Status updates from field
   - Issue reporting
   - Route confirmation
   - POD capture

4. **Daily Operations Report**
   - Deliveries completed
   - Failures and reasons
   - Driver performance
   - Customer feedback

---

### Enterprise Bundle ($5,000-20,000)
**Time to deliver:** 3-4 weeks

1. Growth Bundle +
2. **Full Route Optimization**
   - AI-powered routing
   - Dynamic re-routing
   - Capacity balancing
   - Multi-stop optimization

3. **Customer Portal**
   - Real-time tracking
   - Delivery history
   - Schedule changes
   - Preferences management

4. **Partner/Vendor Integration**
   - Shipper notifications
   - Warehouse coordination
   - Cross-dock alerts
   - Exception management

---

## Node Patterns

### ETA Notification
```javascript
// When driver enters geofence → SMS customer
{
  "trigger": "webhook from GPS/fleet system",
  "condition": "distance < 2km",
  "action": [
    "Calculate ETA",
    "Send SMS: 'Driver arriving in X minutes'",
    "Log notification sent"
  ]
}
```

### Failed Delivery Flow
```javascript
// Driver marks failed → Customer flow
{
  "trigger": "delivery status = 'failed'",
  "flow": [
    "SMS: 'Sorry we missed you'",
    "Include reschedule link",
    "If no response in 4hr: email",
    "If no response in 24hr: call queue"
  ]
}
```

### POD Capture
```javascript
// Delivery complete → Process proof
{
  "trigger": "driver app 'delivered'",
  "flow": [
    "Receive photo + signature",
    "Timestamp + GPS tag",
    "Store in document system",
    "Notify customer with link",
    "Update order status"
  ]
}
```

---

## Integrations

### Common Stack
- **TMS:** Onfleet, Routific, Circuit, Tookan
- **Fleet GPS:** Samsara, Verizon Connect, GPS Trackit
- **Warehouse:** ShipHero, Fishbowl, Cin7
- **Communication:** Twilio, MessageBird, Vonage
- **Customer:** Shopify, WooCommerce (for D2C)
- **Enterprise:** SAP, Oracle, JDA

### Integration Complexity
| Integration | Difficulty | Time |
|-------------|------------|------|
| Onfleet | Easy | 1 hr |
| Twilio SMS | Easy | 30 min |
| Samsara | Medium | 2 hrs |
| Custom GPS | Hard | 4+ hrs |
| SAP | Very Hard | Days |

---

## Pricing Guide

### By Fleet Size
| Daily Deliveries | Quick Win | Full Suite | Retainer |
|------------------|-----------|------------|----------|
| 20-100 | $400 | $1,500 | $400/mo |
| 100-500 | $500 | $3,500 | $700/mo |
| 500-2000 | $600 | $8,000 | $1,200/mo |
| 2000+ | Custom | Custom | $2,000+/mo |

### Value Calculation
```
Delivery volume × Communication cost savings per delivery
Example: 500/day × $0.50 saved × 30 = $7,500/mo value
Price at: $750-1,500/mo
```

---

## Case Study Template

### Challenge
[Company] handles 400 deliveries/day in [city]. They struggled with:
- 80+ "where's my delivery?" calls daily
- 15% failed delivery rate
- No proactive customer updates

### Solution
1. **Smart ETA** - Automated proximity notifications
2. **Delivery Confirm** - Instant proof + feedback
3. **Rescue Flow** - Failed delivery self-reschedule

### Results
- WISMO calls reduced 75% (80 → 20/day)
- Failed deliveries down to 8%
- Customer satisfaction up 40 points
- 2 FTE redeployed from phone duty

### ROI
- Investment: $3,500 setup + $700/mo
- Monthly savings: $9,000
- Payback: 2 weeks

---

## Objection Handling

| Objection | Response |
|-----------|----------|
| "We have a TMS" | "Great - we add the customer communication layer it's missing." |
| "Drivers won't use it" | "They don't have to - it's automatic from existing GPS data." |
| "Our customers are businesses" | "B2B receivers want updates too - maybe more than consumers." |
| "Too many systems already" | "We connect what you have - no new systems to learn." |
| "Costs more than hiring" | "No training, no sick days, no turnover. Works 24/7." |

---

## Discovery Questions

1. "How do customers know when to expect delivery?"
2. "What percentage of calls are 'where's my package?'"
3. "What happens when a delivery fails?"
4. "How do you communicate with drivers?"
5. "What's your failed delivery rate?"
6. "How do you prove delivery happened?"
7. "How are delays communicated?"
8. "What's your biggest operational headache?"
9. "How many people handle customer calls?"
10. "What would zero WISMO calls mean for your operation?"
