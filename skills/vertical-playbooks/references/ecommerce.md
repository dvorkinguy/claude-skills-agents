# E-commerce Playbook

## Overview

**Target Profile:**
- 100+ orders/month minimum
- Sweet spot: 500-5000 orders/month
- Platforms: Shopify, WooCommerce, BigCommerce, Magento

**Key Decision Makers:**
- Founder/Owner (small)
- Operations Manager (mid)
- Director of E-commerce (enterprise)

---

## Top Pain Points

### 1. Order Management Chaos
**Symptoms:**
- Manual copy-paste between systems
- Missed orders
- Shipping delays

**Questions:**
- "How many platforms do you sell on?"
- "How do orders get from [platform] to fulfillment?"
- "What happens when an order falls through the cracks?"

**Automation:**
- Multi-channel order aggregation
- Auto-fulfillment triggers
- Status sync across platforms

**ROI Calculation:**
```
Orders/month × Manual minutes/order × Hourly rate / 60
Example: 1000 orders × 5 min × $25/hr / 60 = $2,083/month
```

---

### 2. Inventory Nightmares
**Symptoms:**
- Overselling
- Stockouts on bestsellers
- Manual inventory counts

**Questions:**
- "Have you ever sold something you didn't have?"
- "How do you know when to reorder?"
- "How long does it take to update inventory across channels?"

**Automation:**
- Real-time inventory sync
- Low stock alerts
- Auto-purchase orders

**ROI Calculation:**
```
Oversells/month × Average order value × 1.5 (reputation cost)
Example: 20 oversells × $75 × 1.5 = $2,250/month
```

---

### 3. Customer Communication Gaps
**Symptoms:**
- "Where's my order?" tickets
- No proactive updates
- Negative reviews

**Questions:**
- "What percentage of support tickets are about order status?"
- "How do customers find out about delays?"
- "What's your review/rating trend?"

**Automation:**
- Proactive shipping notifications
- Delay alerts before customer asks
- Post-delivery review requests

**ROI Calculation:**
```
WISMO tickets/month × Cost per ticket + Lost customers × LTV
Example: 200 tickets × $10 + 5 lost × $200 = $3,000/month
```

---

### 4. Abandoned Carts
**Symptoms:**
- 70%+ cart abandonment
- No follow-up system
- Lost revenue

**Questions:**
- "Do you know your cart abandonment rate?"
- "What happens after someone abandons?"
- "Have you tried recovery emails?"

**Automation:**
- Abandoned cart sequences (1hr, 24hr, 72hr)
- Dynamic cart contents in email
- SMS follow-up option

**ROI Calculation:**
```
Abandoned carts × Recovery rate improvement × Average cart
Example: 500 carts × 5% improvement × $80 = $2,000/month
```

---

## Workflow Bundles

### Quick Win Package ($300-500)
**Time to deliver:** 1-2 days

1. **New Order Slack Alert**
   - Instant notification
   - Order details summary
   - Link to admin

2. **Low Stock Alert**
   - Daily inventory check
   - Alert when below threshold
   - Reorder reminder

---

### Starter Bundle ($800-1,200)
**Time to deliver:** 3-5 days

1. Quick Win Package +
2. **Order Status Sync**
   - Shopify → Email/SMS updates
   - Tracking number notification
   - Delivery confirmation

3. **Review Request Flow**
   - Trigger 7 days post-delivery
   - Link to review platform
   - Thank you message

---

### Growth Bundle ($2,000-3,500)
**Time to deliver:** 1-2 weeks

1. Starter Bundle +
2. **Abandoned Cart Recovery**
   - 3-email sequence
   - Dynamic cart contents
   - Discount on final email

3. **Multi-Channel Inventory Sync**
   - Shopify ↔ Amazon
   - Real-time updates
   - Buffer stock settings

4. **Customer Segmentation**
   - Tag by purchase behavior
   - VIP identification
   - Lapsed customer alerts

---

### Enterprise Bundle ($5,000-15,000)
**Time to deliver:** 3-4 weeks

1. Growth Bundle +
2. **Full Order Orchestration**
   - Any channel → Central hub
   - Fulfillment routing
   - Returns automation

3. **AI Customer Support**
   - Order status bot
   - FAQ automation
   - Human handoff

4. **Advanced Analytics**
   - Daily/weekly reports
   - Anomaly detection
   - Performance dashboards

---

## Node Patterns

### Order Webhook
```javascript
// Shopify Order Created Webhook
{
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "path": "shopify-order",
    "httpMethod": "POST",
    "authentication": "headerAuth"
  }
}
```

### Inventory Check
```javascript
// Check Shopify Inventory
{
  "type": "n8n-nodes-base.shopify",
  "parameters": {
    "resource": "product",
    "operation": "get",
    "productId": "={{ $json.product_id }}"
  }
}
```

### Multi-Channel Sync
```javascript
// Update inventory across platforms
// Shopify → Amazon flow
{
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "https://sellingpartnerapi.amazon.com/...",
    "method": "PATCH",
    "body": {
      "quantity": "={{ $json.inventory_quantity }}"
    }
  }
}
```

---

## Integrations

### Common Stack
- **Platform:** Shopify, WooCommerce, BigCommerce
- **Fulfillment:** ShipStation, ShipBob, Fulfillment by Amazon
- **Email:** Klaviyo, Mailchimp, Omnisend
- **SMS:** Postscript, Attentive, SMSBump
- **Reviews:** Yotpo, Judge.me, Stamped
- **Support:** Gorgias, Zendesk, Re:amaze

### Integration Complexity
| Integration | Difficulty | Time |
|-------------|------------|------|
| Shopify | Easy | 30 min |
| WooCommerce | Medium | 1 hr |
| Amazon | Hard | 3+ hrs |
| Klaviyo | Easy | 30 min |
| ShipStation | Medium | 1 hr |

---

## Pricing Guide

### By Store Size
| Monthly Orders | Quick Win | Full Suite | Retainer |
|----------------|-----------|------------|----------|
| 100-500 | $300 | $1,200 | $300/mo |
| 500-2000 | $400 | $2,500 | $500/mo |
| 2000-5000 | $500 | $4,000 | $800/mo |
| 5000+ | $600 | Custom | $1,200+/mo |

### Value Calculation
```
Monthly revenue × 2% improvement potential = Automation value
$100,000/mo × 2% = $2,000/mo value → Price at $400-600/mo
```

---

## Case Study Template

### Challenge
[Brand] was processing 2,000+ orders/month across Shopify and Amazon. Their team spent 4 hours daily on:
- Manual order exports
- Inventory updates
- Customer status inquiries

### Solution
1. **Order Hub** - Unified order feed from all channels
2. **Smart Inventory** - Real-time sync with safety stock
3. **Proactive Notify** - Automated shipping updates

### Results
- 85% reduction in manual order handling
- Zero oversells (down from 15/month)
- 60% fewer "where's my order" tickets
- 3 hours/day saved

### ROI
- Investment: $2,500 setup + $500/mo
- Monthly savings: $3,200
- Payback: 3 weeks

---

## Objection Handling

| Objection | Response |
|-----------|----------|
| "Shopify has apps for this" | "Apps solve one problem. We connect everything so orders flow automatically." |
| "We're too small" | "Perfect time to automate - before you scale and it gets messy." |
| "Too expensive" | "What does one oversell cost you? One angry customer?" |
| "We tried automation before" | "What went wrong? We'll make sure that doesn't happen." |
| "Our products are complex" | "More reason to automate - less room for human error." |

---

## Discovery Questions

1. "Walk me through what happens when an order comes in."
2. "How many channels do you sell on?"
3. "What's your biggest headache during peak season?"
4. "How do you handle inventory across channels?"
5. "What percentage of support is 'where's my order?'"
6. "What's your cart abandonment rate?"
7. "How do you get reviews?"
8. "What happens when you oversell?"
9. "How long to update inventory across all platforms?"
10. "What would you do with 20 extra hours/month?"
