# Rate Auditor Agent

AI agent for freight invoice reconciliation and rate recovery.

## Product Overview

**Name:** Rate Auditor
**Pricing:** 2-5% of recovered savings (performance-based)
**Target:** Logistics companies, large importers/exporters

## Value Proposition

- Automatically audit freight invoices against contracts
- Identify overcharges and billing errors
- Recover 3-8% of freight spend on average
- No savings = no fee (risk-free)

## Job To Be Done

```
When I receive freight invoices,
I want to verify they match contracted rates,
so I can avoid overpaying and recover overcharges.
```

## Pain Points Addressed

1. **Volume:** Thousands of invoices monthly, impossible to audit manually
2. **Complexity:** Multiple carriers, rate types, accessorials
3. **Hidden Errors:** Overcharges often go unnoticed
4. **Time:** Manual audit takes 15-30 min per invoice

## API Design

### Submit Invoice for Audit

```typescript
// POST /api/agents/rate-auditor/audit
interface AuditRequest {
  invoice: {
    id: string
    carrierId: string
    invoiceNumber: string
    invoiceDate: string
    totalAmount: number
    currency: string
    lineItems: {
      description: string
      quantity: number
      rate: number
      amount: number
      chargeType: 'base' | 'accessorial' | 'fuel' | 'other'
    }[]
  }
  shipment: {
    origin: string
    destination: string
    weight: number
    pieces: number
    mode: 'ocean' | 'air' | 'truck' | 'rail' | 'intermodal'
    containerType?: string
    serviceLevel?: string
    shipDate: string
    deliveryDate?: string
  }
  contractId?: string // Reference to uploaded contract
}

interface AuditResponse {
  auditId: string
  status: 'pass' | 'fail' | 'review'
  totalBilled: number
  expectedAmount: number
  variance: number
  variancePercent: number
  findings: {
    lineItem: string
    issue: string
    billedAmount: number
    expectedAmount: number
    variance: number
    severity: 'high' | 'medium' | 'low'
    evidence: string
  }[]
  recommendations: string[]
  recoveryPotential: number
}
```

### Upload Contract

```typescript
// POST /api/agents/rate-auditor/contracts
interface ContractUploadRequest {
  carrierId: string
  carrierName: string
  contractFile: File // PDF or Excel
  effectiveDate: string
  expirationDate: string
}

interface ContractResponse {
  contractId: string
  carrierId: string
  parsedRates: {
    origin: string
    destination: string
    mode: string
    rateType: string
    rate: number
    currency: string
    unit: string
    minCharge?: number
    maxWeight?: number
  }[]
  accessorials: {
    chargeType: string
    rate: number
    unit: string
    conditions?: string
  }[]
  fuelSurcharge?: {
    type: 'fixed' | 'index'
    rate?: number
    indexName?: string
  }
}
```

## Implementation Architecture

```
┌─────────────────┐     ┌─────────────────┐
│ Invoice Upload  │     │ Contract Upload │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │ Contract Parser │ ← AI extracts rates
         │              └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│ Rate Matching Engine                    │
│ ├── Match shipment to contract          │
│ ├── Calculate expected charges          │
│ └── Apply accessorials & fuel           │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Variance Analysis│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Audit Report    │
└─────────────────┘
```

## Database Schema

```typescript
export const contracts = pgTable('contracts', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  carrierId: text('carrier_id').notNull(),
  carrierName: text('carrier_name').notNull(),
  effectiveDate: date('effective_date').notNull(),
  expirationDate: date('expiration_date').notNull(),
  fileUrl: text('file_url'),
  parsedData: jsonb('parsed_data'),
  createdAt: timestamp('created_at').defaultNow(),
})

export const invoiceAudits = pgTable('invoice_audits', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  contractId: text('contract_id').references(() => contracts.id),
  invoiceNumber: text('invoice_number').notNull(),
  carrierId: text('carrier_id').notNull(),
  totalBilled: decimal('total_billed', { precision: 12, scale: 2 }),
  expectedAmount: decimal('expected_amount', { precision: 12, scale: 2 }),
  variance: decimal('variance', { precision: 12, scale: 2 }),
  status: text('status').notNull(), // pass, fail, review
  findings: jsonb('findings'),
  createdAt: timestamp('created_at').defaultNow(),
})

export const recoveries = pgTable('recoveries', {
  id: text('id').primaryKey(),
  auditId: text('audit_id').references(() => invoiceAudits.id),
  claimAmount: decimal('claim_amount', { precision: 12, scale: 2 }),
  recoveredAmount: decimal('recovered_amount', { precision: 12, scale: 2 }),
  status: text('status').notNull(), // pending, approved, rejected, paid
  carrierResponse: text('carrier_response'),
  resolvedAt: timestamp('resolved_at'),
  createdAt: timestamp('created_at').defaultNow(),
})
```

## Common Billing Errors

1. **Incorrect Weight/Dims:** Dimensional weight vs actual weight
2. **Wrong Rate Applied:** Using non-contract rate
3. **Duplicate Charges:** Same accessorial billed twice
4. **Fuel Surcharge Errors:** Wrong index or calculation
5. **Zone Errors:** Incorrect origin/destination zone
6. **Service Level Mismatch:** Premium rate for standard service
7. **Minimum Charge Violations:** Below minimum not applied
8. **Currency Conversion Errors:** Wrong exchange rate
9. **Date-Based Errors:** Expired contract rates used
10. **Accessorial Overcharges:** Fees not in contract

## UI Components

### Audit Dashboard

```tsx
export function AuditDashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <StatCard title="Invoices Audited" value="1,234" />
        <StatCard title="Total Variance Found" value="$45,678" color="red" />
        <StatCard title="Recovered This Month" value="$12,345" color="green" />
        <StatCard title="Pending Claims" value="23" />
      </div>

      <div className="flex gap-4">
        <Button>Upload Invoice</Button>
        <Button variant="secondary">Upload Contract</Button>
        <Button variant="secondary">Bulk Import</Button>
      </div>

      <AuditResultsTable />
    </div>
  )
}
```

### Variance Alert

```tsx
export function VarianceAlert({ finding }: { finding: AuditFinding }) {
  return (
    <div className={cn(
      'p-4 rounded-lg border',
      finding.severity === 'high' && 'border-red-500 bg-red-500/10',
      finding.severity === 'medium' && 'border-yellow-500 bg-yellow-500/10',
      finding.severity === 'low' && 'border-blue-500 bg-blue-500/10',
    )}>
      <div className="flex justify-between items-start">
        <div>
          <h4 className="font-medium">{finding.lineItem}</h4>
          <p className="text-sm text-foreground-muted">{finding.issue}</p>
        </div>
        <span className="text-lg font-bold text-red-400">
          +${finding.variance.toFixed(2)}
        </span>
      </div>
      <p className="mt-2 text-sm">{finding.evidence}</p>
    </div>
  )
}
```

## Success Metrics

- Average recovery rate: 3-8% of audited spend
- Audit accuracy: > 99%
- Processing time: < 5 seconds per invoice
- Contract parsing accuracy: > 95%
- Claim success rate: > 85%
