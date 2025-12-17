// app/api/webhooks/stripe/route.ts
import { stripe } from '@/lib/stripe';
import { headers } from 'next/headers';
import { db } from '@/db';
import { users } from '@/db/schema';
import { eq } from 'drizzle-orm';
import type Stripe from 'stripe';

export async function POST(request: Request) {
  const body = await request.text();
  const signature = headers().get('stripe-signature');

  if (!signature) {
    return new Response('Missing signature', { status: 400 });
  }

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return new Response('Invalid signature', { status: 400 });
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutComplete(event.data.object as Stripe.Checkout.Session);
        break;

      case 'customer.subscription.created':
      case 'customer.subscription.updated':
        await handleSubscriptionChange(event.data.object as Stripe.Subscription);
        break;

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object as Stripe.Subscription);
        break;

      case 'invoice.payment_failed':
        await handlePaymentFailed(event.data.object as Stripe.Invoice);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }
  } catch (error) {
    console.error('Webhook handler error:', error);
    // Still return 200 to prevent retries for handled events
    return new Response('Webhook handler failed', { status: 500 });
  }

  return new Response('OK', { status: 200 });
}

async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  const userId = session.metadata?.userId;
  if (!userId) {
    console.error('No userId in session metadata');
    return;
  }

  await db.update(users).set({
    stripeCustomerId: session.customer as string,
    subscriptionId: session.subscription as string,
    subscriptionStatus: 'active',
  }).where(eq(users.id, userId));
}

async function handleSubscriptionChange(subscription: Stripe.Subscription) {
  const userId = subscription.metadata?.userId;
  if (!userId) return;

  await db.update(users).set({
    subscriptionStatus: subscription.status,
    subscriptionPriceId: subscription.items.data[0]?.price.id,
    subscriptionCurrentPeriodEnd: new Date(subscription.current_period_end * 1000),
  }).where(eq(users.id, userId));
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  const userId = subscription.metadata?.userId;
  if (!userId) return;

  await db.update(users).set({
    subscriptionStatus: 'canceled',
    subscriptionId: null,
  }).where(eq(users.id, userId));
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  // Send notification email, update UI, etc.
  console.log(`Payment failed for customer: ${invoice.customer}`);
}
