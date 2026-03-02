# Stripe MCP Integration

Reference for Stripe payments with Export Arena.

## MCP Server

Stripe provides an official MCP server:

```json
{
  "mcpServers": {
    "stripe": {
      "type": "http",
      "url": "https://mcp.stripe.com"
    }
  }
}
```

## Dashboard

- **Stripe Dashboard:** https://dashboard.stripe.com
- **Test Mode:** Use for development
- **Live Mode:** Production only

## Environment Variables

```bash
# API Keys
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Webhook Secret
STRIPE_WEBHOOK_SECRET=whsec_...

# Price IDs (from Stripe Dashboard)
STRIPE_PRICE_AUTOMATE=price_...
STRIPE_PRICE_SCALE=price_...
STRIPE_PRICE_DOMINATE=price_...
```

## Products & Pricing

### Create Products in Stripe

| Tier | Name | Monthly | Price ID |
|------|------|---------|----------|
| 1 | Automate | $497 | `price_automate` |
| 2 | Scale | $1,497 | `price_scale` |
| 3 | Dominate | $3,997 | `price_dominate` |

### Sync Prices to Database

```typescript
// packages/database/schema/subscriptions.ts
export const subscriptions = pgTable('subscriptions', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  stripeCustomerId: text('stripe_customer_id'),
  stripeSubscriptionId: text('stripe_subscription_id'),
  stripePriceId: text('stripe_price_id'),
  status: text('status'), // active, canceled, past_due, etc.
  currentPeriodStart: timestamp('current_period_start'),
  currentPeriodEnd: timestamp('current_period_end'),
  cancelAtPeriodEnd: boolean('cancel_at_period_end'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
})
```

## Checkout Session

```typescript
// pages/api/checkout/route.ts
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(req: Request) {
  const { priceId, userId } = await req.json()

  // Get or create customer
  let customerId = await getStripeCustomerId(userId)
  if (!customerId) {
    const customer = await stripe.customers.create({
      metadata: { userId },
    })
    customerId = customer.id
    await saveStripeCustomerId(userId, customerId)
  }

  // Create checkout session
  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    mode: 'subscription',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/dashboard?success=true`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/pricing`,
    metadata: { userId },
  })

  return Response.json({ url: session.url })
}
```

## Webhook Handler

```typescript
// pages/api/webhooks/stripe.ts
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(req: Request) {
  const body = await req.text()
  const signature = req.headers.get('stripe-signature')!

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (err) {
    return new Response('Invalid signature', { status: 400 })
  }

  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object as Stripe.Checkout.Session
      await handleCheckoutComplete(session)
      break

    case 'customer.subscription.updated':
      const subscription = event.data.object as Stripe.Subscription
      await handleSubscriptionUpdate(subscription)
      break

    case 'customer.subscription.deleted':
      const deleted = event.data.object as Stripe.Subscription
      await handleSubscriptionCancel(deleted)
      break

    case 'invoice.payment_failed':
      const invoice = event.data.object as Stripe.Invoice
      await handlePaymentFailed(invoice)
      break
  }

  return new Response('OK')
}
```

## Customer Portal

```typescript
export async function POST(req: Request) {
  const { userId } = await req.json()

  const customerId = await getStripeCustomerId(userId)
  if (!customerId) {
    return new Response('No customer', { status: 404 })
  }

  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_URL}/dashboard`,
  })

  return Response.json({ url: session.url })
}
```

## Subscription Status Check

```typescript
import { db, subscriptions, eq } from 'database'

export async function hasActiveSubscription(userId: string): Promise<boolean> {
  const sub = await db.query.subscriptions.findFirst({
    where: eq(subscriptions.userId, userId),
  })

  return sub?.status === 'active' || sub?.status === 'trialing'
}

export async function getSubscriptionTier(userId: string): Promise<string | null> {
  const sub = await db.query.subscriptions.findFirst({
    where: eq(subscriptions.userId, userId),
  })

  if (!sub || sub.status !== 'active') return null

  // Map price ID to tier
  const tiers: Record<string, string> = {
    [process.env.STRIPE_PRICE_AUTOMATE!]: 'automate',
    [process.env.STRIPE_PRICE_SCALE!]: 'scale',
    [process.env.STRIPE_PRICE_DOMINATE!]: 'dominate',
  }

  return tiers[sub.stripePriceId || ''] || null
}
```

## Usage Metering

For agents with usage-based pricing:

```typescript
// Record usage
await stripe.subscriptionItems.createUsageRecord(
  subscriptionItemId,
  {
    quantity: 1,
    timestamp: Math.floor(Date.now() / 1000),
    action: 'increment',
  }
)
```

## Testing

```bash
# Stripe CLI for webhook testing
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
```

## Test Cards

```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0027 6000 3184
```

## Security

- Never expose `STRIPE_SECRET_KEY` to client
- Always verify webhook signatures
- Use HTTPS in production
- Store minimal PII, reference Stripe Customer ID
