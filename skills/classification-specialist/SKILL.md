# Classification Specialist Agent

AI agent for HS/HTS code classification with Defense Memos.

## Product Overview

**Name:** Classification Specialist
**Pricing:** $1,500 - $2,500/month
**Target:** All traders (importers, exporters, customs brokers)

## Value Proposition

- Classify products in seconds (vs 15-30 min manual)
- 99.5% accuracy with AI + human validation
- Defense Memos for audit protection
- Historical classification database

## Job To Be Done

```
When I receive a new product for import/export,
I want to classify it with the correct HS code quickly,
so I can file customs entries accurately and avoid penalties.
```

## Pain Points Addressed

1. **Time:** Manual classification takes 15-30 min per SKU
2. **Accuracy:** Misclassification leads to penalties ($5K-$500K)
3. **Audit Risk:** No documentation trail for CBP audits
4. **Inconsistency:** Different classifiers, different codes

## API Design

### Classify Product

```typescript
// POST /api/agents/classification/classify
interface ClassifyRequest {
  description: string           // Product description
  countryOfOrigin: string       // ISO country code
  value?: number               // Declared value
  images?: string[]            // Product images (base64 or URLs)
  additionalInfo?: {
    material?: string
    intendedUse?: string
    dimensions?: string
    weight?: string
  }
}

interface ClassifyResponse {
  hsCode: string               // 6-digit HS code
  htsCode?: string             // 10-digit HTS (US specific)
  description: string          // Official description
  confidence: number           // 0-1 confidence score
  reasoning: string            // AI reasoning
  alternatives: {
    code: string
    description: string
    confidence: number
  }[]
  defenseMemo: {
    id: string
    generatedAt: string
    summary: string
    fullDocument: string       // PDF URL
  }
  dutyRate?: {
    general: string
    special?: string[]
  }
}
```

### Defense Memo

```typescript
// GET /api/agents/classification/memo/:id
interface DefenseMemo {
  id: string
  productDescription: string
  hsCode: string
  classificationDate: string
  validUntil: string

  sections: {
    productAnalysis: string     // Detailed product breakdown
    classificationRationale: string  // Why this code
    gri_analysis: string        // General Rules of Interpretation
    rulings_cited: string[]     // CBP rulings referenced
    binding_rulings: boolean    // Any binding rulings found
  }

  auditor_notes: string        // Notes for auditors
  signature: {
    classifier: string
    date: string
    qualifications: string
  }
}
```

## Implementation Architecture

```
┌─────────────────┐
│ Product Input   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Preprocessing   │ ← Clean description, extract features
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AI Classification│ ← GPT-4o + fine-tuned model
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Validation Layer                    │
│ ├── Ruling Database Check           │
│ ├── Historical Classification Match │
│ └── Confidence Threshold Check      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Defense Memo Gen│ ← Generate audit-ready documentation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Response        │
└─────────────────┘
```

## Database Schema

```typescript
// packages/database/schema/classifications.ts
export const classifications = pgTable('classifications', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  productDescription: text('product_description').notNull(),
  hsCode: text('hs_code').notNull(),
  htsCode: text('hts_code'),
  confidence: real('confidence').notNull(),
  reasoning: text('reasoning').notNull(),
  countryOfOrigin: text('country_of_origin'),
  value: decimal('value', { precision: 12, scale: 2 }),
  defenseMemoId: text('defense_memo_id'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})

export const defenseMemos = pgTable('defense_memos', {
  id: text('id').primaryKey(),
  classificationId: text('classification_id').references(() => classifications.id),
  content: jsonb('content').notNull(),
  pdfUrl: text('pdf_url'),
  validUntil: timestamp('valid_until').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})
```

## Prompt Engineering

```typescript
const CLASSIFICATION_SYSTEM_PROMPT = `You are an expert customs classifier with 20 years of experience.

Your task is to classify products according to the Harmonized System (HS).

Follow these rules:
1. Apply the General Rules of Interpretation (GRI) in order
2. Consider the principal use and essential character
3. Cite relevant CBP rulings when available
4. Provide confidence level based on clarity of classification
5. List alternative classifications if ambiguous

Output format:
- HS Code (6 digits minimum)
- Official description from HS nomenclature
- Reasoning citing specific GRI rules
- Confidence score (0-1)
- Alternative codes if applicable`

const DEFENSE_MEMO_PROMPT = `Generate a Defense Memo for customs audit.

Include:
1. Detailed product analysis
2. Classification rationale with GRI citations
3. Any relevant CBP rulings
4. Statement of good faith
5. Qualifications statement

Format for official review.`
```

## UI Components

### Classification Form

```tsx
export function ClassificationForm() {
  return (
    <form className="space-y-4">
      <div>
        <label>Product Description</label>
        <textarea
          name="description"
          placeholder="Describe the product in detail..."
          className="w-full h-32"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label>Country of Origin</label>
          <CountrySelect name="countryOfOrigin" />
        </div>
        <div>
          <label>Value (USD)</label>
          <input type="number" name="value" />
        </div>
      </div>

      <div>
        <label>Product Images (optional)</label>
        <ImageUpload name="images" multiple />
      </div>

      <button type="submit" className="w-full">
        Classify Product
      </button>
    </form>
  )
}
```

### Classification Result

```tsx
export function ClassificationResult({ result }: { result: ClassifyResponse }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">{result.hsCode}</h2>
          <p className="text-foreground-muted">{result.description}</p>
        </div>
        <ConfidenceBadge confidence={result.confidence} />
      </div>

      <div className="p-4 bg-surface-200 rounded-lg">
        <h3 className="font-medium mb-2">Classification Reasoning</h3>
        <p>{result.reasoning}</p>
      </div>

      {result.alternatives.length > 0 && (
        <div>
          <h3 className="font-medium mb-2">Alternative Classifications</h3>
          <ul className="space-y-2">
            {result.alternatives.map((alt) => (
              <li key={alt.code} className="flex justify-between">
                <span>{alt.code} - {alt.description}</span>
                <span className="text-foreground-muted">{Math.round(alt.confidence * 100)}%</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <a
        href={result.defenseMemo.fullDocument}
        className="block w-full py-3 text-center bg-brand-500 rounded-lg text-white"
      >
        Download Defense Memo (PDF)
      </a>
    </div>
  )
}
```

## Success Metrics

- Classification accuracy: > 99%
- Average classification time: < 10 seconds
- Defense memo generation: < 30 seconds
- Customer satisfaction: > 4.5/5
- Audit success rate: > 98%
