# Document Scrutineer Agent

AI agent for Letter of Credit validation and trade document compliance.

## Product Overview

**Name:** Document Scrutineer
**Pricing:** $1,000 - $2,000/month
**Target:** Exporters, banks, freight forwarders

## Value Proposition

- Pre-flight LC document checks before bank submission
- UCP 600 compliance validation
- Reduce discrepancy rates from 70% to < 10%
- Avoid $50-500 per discrepancy fees

## Job To Be Done

```
When preparing documents for LC payment,
I want to validate compliance before submission,
so I can avoid discrepancies and get paid on first presentation.
```

## Pain Points Addressed

1. **High Discrepancy Rate:** 70% of LC presentations have discrepancies
2. **Costly Fixes:** Each discrepancy costs $50-500 to correct
3. **Delayed Payment:** Discrepancies delay payment by weeks
4. **Complexity:** UCP 600 has 39 articles to comply with

## API Design

### Submit Documents for Review

```typescript
// POST /api/agents/document-scrutineer/review
interface ReviewRequest {
  lcReference: string
  lcDocument: File // The LC itself
  documents: {
    type: DocumentType
    file: File
  }[]
  beneficiary: {
    name: string
    address: string
  }
}

type DocumentType =
  | 'commercial_invoice'
  | 'packing_list'
  | 'bill_of_lading'
  | 'certificate_of_origin'
  | 'insurance_certificate'
  | 'inspection_certificate'
  | 'weight_certificate'
  | 'quality_certificate'
  | 'other'

interface ReviewResponse {
  reviewId: string
  status: 'compliant' | 'discrepancies_found' | 'review_needed'
  overallScore: number // 0-100
  lcRequirements: {
    requirement: string
    status: 'met' | 'not_met' | 'unclear'
    notes?: string
  }[]
  documentReviews: {
    documentType: DocumentType
    findings: {
      field: string
      issue: string
      lcRequirement: string
      severity: 'critical' | 'major' | 'minor'
      suggestion: string
      ucpArticle?: string
    }[]
  }[]
  crossChecks: {
    check: string
    documents: string[]
    status: 'pass' | 'fail' | 'warning'
    details: string
  }[]
  recommendations: string[]
}
```

### Parse LC

```typescript
// POST /api/agents/document-scrutineer/parse-lc
interface ParseLCRequest {
  lcDocument: File
}

interface ParseLCResponse {
  lcNumber: string
  issuingBank: string
  applicant: {
    name: string
    address: string
  }
  beneficiary: {
    name: string
    address: string
  }
  amount: {
    value: number
    currency: string
    tolerance?: string
  }
  expiryDate: string
  shipmentDate: string
  latestShipmentDate?: string
  partialShipments: 'allowed' | 'not_allowed'
  transhipment: 'allowed' | 'not_allowed'
  portOfLoading: string
  portOfDischarge: string
  goodsDescription: string
  documentsRequired: {
    type: string
    copies: number
    originals: number
    specifics: string[]
  }[]
  additionalConditions: string[]
}
```

## Implementation Architecture

```
┌─────────────────┐
│ LC + Documents  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OCR/Parsing     │ ← Extract text from all documents
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ LC Requirement Extraction           │
│ ├── Parse LC terms                  │
│ └── Build checklist                 │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Document-by-Document Review         │
│ ├── Check against LC requirements   │
│ ├── Apply UCP 600 rules             │
│ └── Validate formatting             │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Cross-Document Verification         │
│ ├── Quantity consistency            │
│ ├── Amount consistency              │
│ ├── Date consistency                │
│ └── Party name consistency          │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Report          │
└─────────────────┘
```

## Common Discrepancies

1. **Spelling Differences:** Names don't match exactly
2. **Quantity Mismatch:** Invoice vs packing list vs BL
3. **Late Shipment:** Beyond latest shipment date
4. **Missing Signature:** Required signatures absent
5. **Inconsistent Amounts:** Invoice vs LC amount
6. **Wrong Incoterms:** Different from LC specification
7. **Missing Documents:** Required docs not presented
8. **Outdated BL:** Older than 21 days
9. **Wrong Port:** Port of loading/discharge doesn't match
10. **Short Description:** Goods description incomplete

## UCP 600 Reference

```typescript
const UCP_600_KEY_ARTICLES = {
  article_14: 'Standard for Examination of Documents',
  article_16: 'Discrepant Documents, Waiver and Notice',
  article_17: 'Original Documents and Copies',
  article_18: 'Commercial Invoice',
  article_19: 'Transport Document Covering Multiple Modes',
  article_20: 'Bill of Lading',
  article_23: 'Air Transport Document',
  article_28: 'Insurance Document and Coverage',
  article_30: 'Tolerance in Credit Amount, Quantity and Unit Prices',
}
```

## Database Schema

```typescript
export const lcReviews = pgTable('lc_reviews', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  lcReference: text('lc_reference').notNull(),
  status: text('status').notNull(),
  overallScore: integer('overall_score'),
  lcData: jsonb('lc_data'),
  findings: jsonb('findings'),
  createdAt: timestamp('created_at').defaultNow(),
})

export const reviewedDocuments = pgTable('reviewed_documents', {
  id: text('id').primaryKey(),
  reviewId: text('review_id').references(() => lcReviews.id),
  documentType: text('document_type').notNull(),
  fileUrl: text('file_url'),
  extractedData: jsonb('extracted_data'),
  findings: jsonb('findings'),
  createdAt: timestamp('created_at').defaultNow(),
})
```

## UI Components

### Review Dashboard

```tsx
export function LCReviewDashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <StatCard title="Reviews Today" value="12" />
        <StatCard title="Discrepancies Found" value="34" />
        <StatCard title="Savings This Month" value="$8,500" color="green" />
      </div>

      <UploadZone
        accept=".pdf,.jpg,.png"
        onUpload={handleDocumentUpload}
      />

      <ReviewHistory />
    </div>
  )
}
```

### Finding Card

```tsx
export function FindingCard({ finding }: { finding: Finding }) {
  return (
    <div className={cn(
      'p-4 rounded-lg border-l-4',
      finding.severity === 'critical' && 'border-red-500 bg-red-500/10',
      finding.severity === 'major' && 'border-yellow-500 bg-yellow-500/10',
      finding.severity === 'minor' && 'border-blue-500 bg-blue-500/10',
    )}>
      <div className="flex justify-between items-start">
        <div>
          <h4 className="font-medium">{finding.field}</h4>
          <p className="text-sm text-foreground-muted">{finding.issue}</p>
        </div>
        <Badge severity={finding.severity} />
      </div>

      <div className="mt-3 p-3 bg-surface-200 rounded">
        <p className="text-sm">
          <strong>LC Requirement:</strong> {finding.lcRequirement}
        </p>
        {finding.ucpArticle && (
          <p className="text-sm text-foreground-muted mt-1">
            Reference: UCP 600 {finding.ucpArticle}
          </p>
        )}
      </div>

      <div className="mt-3">
        <p className="text-sm text-green-400">
          <strong>Suggestion:</strong> {finding.suggestion}
        </p>
      </div>
    </div>
  )
}
```

### Compliance Score

```tsx
export function ComplianceScore({ score }: { score: number }) {
  const getColor = () => {
    if (score >= 90) return 'text-green-400'
    if (score >= 70) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className="text-center">
      <div className={cn('text-5xl font-bold', getColor())}>
        {score}%
      </div>
      <p className="text-foreground-muted">Compliance Score</p>
      <p className="text-sm mt-2">
        {score >= 90 && 'Ready for presentation'}
        {score >= 70 && score < 90 && 'Minor corrections needed'}
        {score < 70 && 'Significant issues found'}
      </p>
    </div>
  )
}
```

## Success Metrics

- Discrepancy detection rate: > 95%
- False positive rate: < 5%
- Average review time: < 2 minutes
- Customer discrepancy rate reduction: 70% → < 10%
- Cost savings per presentation: $50-500
