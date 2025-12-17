# Pricing Page Template

## React/Tailwind Component

```tsx
import { Check } from 'lucide-react'

const tiers = [
  {
    name: 'Starter',
    price: 297,
    description: 'Perfect for small teams getting started with AI automation.',
    features: [
      '1 AI agent',
      '1,000 tasks/month',
      '2 integrations',
      'Email support',
      'Basic analytics',
    ],
    cta: 'Get Started',
    popular: false,
  },
  {
    name: 'Growth',
    price: 697,
    description: 'For growing businesses that need more power.',
    features: [
      '3 AI agents',
      '5,000 tasks/month',
      '5 integrations',
      'Priority support',
      'Advanced analytics',
      'Custom training',
      'API access',
    ],
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    name: 'Scale',
    price: 1997,
    description: 'For enterprises that need unlimited automation.',
    features: [
      '10 AI agents',
      'Unlimited tasks',
      'All integrations',
      'Dedicated support',
      'Custom development',
      'SLA guarantee',
      'On-prem option',
      'White-label',
    ],
    cta: 'Contact Sales',
    popular: false,
  },
]

export function PricingSection() {
  return (
    <section className="py-24 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Choose the plan that fits your needs. All plans include a 14-day free trial.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={`relative rounded-2xl bg-white p-8 shadow-lg ${
                tier.popular ? 'ring-2 ring-blue-600' : ''
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-blue-600 text-white text-sm font-semibold px-4 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="mb-8">
                <h3 className="text-2xl font-bold text-gray-900">{tier.name}</h3>
                <p className="text-gray-600 mt-2">{tier.description}</p>
                <div className="mt-6">
                  <span className="text-5xl font-bold text-gray-900">
                    ${tier.price}
                  </span>
                  <span className="text-gray-600">/month</span>
                </div>
              </div>

              <ul className="space-y-4 mb-8">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                className={`w-full py-3 px-6 rounded-lg font-semibold transition ${
                  tier.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                }`}
              >
                {tier.cta}
              </button>
            </div>
          ))}
        </div>

        {/* FAQ or Trust Signals */}
        <div className="mt-16 text-center">
          <p className="text-gray-600">
            All plans include: 14-day free trial • No credit card required • Cancel anytime
          </p>
        </div>
      </div>
    </section>
  )
}
```

## HTML/Plain CSS Version

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pricing</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f9fafb; }

    .pricing-section { padding: 6rem 1rem; max-width: 1200px; margin: 0 auto; }
    .pricing-header { text-align: center; margin-bottom: 4rem; }
    .pricing-header h2 { font-size: 2.5rem; color: #111; margin-bottom: 1rem; }
    .pricing-header p { font-size: 1.25rem; color: #666; max-width: 600px; margin: 0 auto; }

    .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }

    .pricing-card {
      background: white;
      border-radius: 1rem;
      padding: 2rem;
      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
      position: relative;
    }
    .pricing-card.popular { border: 2px solid #2563eb; }

    .popular-badge {
      position: absolute;
      top: -0.75rem;
      left: 50%;
      transform: translateX(-50%);
      background: #2563eb;
      color: white;
      padding: 0.25rem 1rem;
      border-radius: 9999px;
      font-size: 0.875rem;
      font-weight: 600;
    }

    .tier-name { font-size: 1.5rem; font-weight: 700; color: #111; }
    .tier-desc { color: #666; margin-top: 0.5rem; }
    .tier-price { margin-top: 1.5rem; }
    .tier-price .amount { font-size: 3rem; font-weight: 700; color: #111; }
    .tier-price .period { color: #666; }

    .features-list { list-style: none; margin: 2rem 0; }
    .features-list li { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0; color: #374151; }
    .features-list li::before { content: "✓"; color: #16a34a; font-weight: bold; }

    .cta-button {
      width: 100%;
      padding: 0.75rem 1.5rem;
      border-radius: 0.5rem;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
    }
    .cta-button.primary { background: #2563eb; color: white; }
    .cta-button.primary:hover { background: #1d4ed8; }
    .cta-button.secondary { background: #f3f4f6; color: #111; }
    .cta-button.secondary:hover { background: #e5e7eb; }

    .trust-signals { text-align: center; margin-top: 4rem; color: #666; }
  </style>
</head>
<body>
  <section class="pricing-section">
    <div class="pricing-header">
      <h2>Simple, Transparent Pricing</h2>
      <p>Choose the plan that fits your needs. All plans include a 14-day free trial.</p>
    </div>

    <div class="pricing-grid">
      <!-- Starter -->
      <div class="pricing-card">
        <h3 class="tier-name">Starter</h3>
        <p class="tier-desc">Perfect for small teams getting started with AI automation.</p>
        <div class="tier-price">
          <span class="amount">$297</span>
          <span class="period">/month</span>
        </div>
        <ul class="features-list">
          <li>1 AI agent</li>
          <li>1,000 tasks/month</li>
          <li>2 integrations</li>
          <li>Email support</li>
          <li>Basic analytics</li>
        </ul>
        <button class="cta-button secondary">Get Started</button>
      </div>

      <!-- Growth (Popular) -->
      <div class="pricing-card popular">
        <span class="popular-badge">Most Popular</span>
        <h3 class="tier-name">Growth</h3>
        <p class="tier-desc">For growing businesses that need more power.</p>
        <div class="tier-price">
          <span class="amount">$697</span>
          <span class="period">/month</span>
        </div>
        <ul class="features-list">
          <li>3 AI agents</li>
          <li>5,000 tasks/month</li>
          <li>5 integrations</li>
          <li>Priority support</li>
          <li>Advanced analytics</li>
          <li>Custom training</li>
          <li>API access</li>
        </ul>
        <button class="cta-button primary">Start Free Trial</button>
      </div>

      <!-- Scale -->
      <div class="pricing-card">
        <h3 class="tier-name">Scale</h3>
        <p class="tier-desc">For enterprises that need unlimited automation.</p>
        <div class="tier-price">
          <span class="amount">$1,997</span>
          <span class="period">/month</span>
        </div>
        <ul class="features-list">
          <li>10 AI agents</li>
          <li>Unlimited tasks</li>
          <li>All integrations</li>
          <li>Dedicated support</li>
          <li>Custom development</li>
          <li>SLA guarantee</li>
          <li>On-prem option</li>
          <li>White-label</li>
        </ul>
        <button class="cta-button secondary">Contact Sales</button>
      </div>
    </div>

    <div class="trust-signals">
      <p>All plans include: 14-day free trial • No credit card required • Cancel anytime</p>
    </div>
  </section>
</body>
</html>
```

## Israeli Market Version (NIS)

Replace prices with:
```javascript
const tiers = [
  { name: 'Starter', price: '₪1,290', priceNote: 'כולל מע״מ' },
  { name: 'Growth', price: '₪2,990', priceNote: 'כולל מע״מ' },
  { name: 'Scale', price: '₪7,990', priceNote: 'כולל מע״מ' },
]
```

Add RTL support:
```css
[dir="rtl"] .pricing-section { direction: rtl; }
[dir="rtl"] .features-list li { flex-direction: row-reverse; }
[dir="rtl"] .features-list li::before { content: "✓"; margin-left: 0.75rem; margin-right: 0; }
```
