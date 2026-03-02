# Sanctions Sentry Agent

AI agent for sanctions and denied party screening.

## Product Overview

**Name:** Sanctions Sentry
**Pricing:** $800 - $1,500/month
**Target:** All traders, compliance departments

## Value Proposition

- Screen against 300+ sanctions and denied party lists
- Real-time monitoring of trading partners
- Reduce compliance risk and penalties
- Audit-ready screening records

## Job To Be Done

```
When entering business relationships,
I want to screen parties against sanctions lists,
so I can avoid violations and regulatory penalties.
```

## Pain Points Addressed

1. **Complexity:** 300+ lists across multiple jurisdictions
2. **Updates:** Lists change daily
3. **Penalties:** Violations can result in millions in fines
4. **Documentation:** Need audit trail for compliance

## Screening Lists Included

### US Lists
- OFAC SDN (Specially Designated Nationals)
- OFAC Consolidated (Non-SDN)
- BIS Entity List
- BIS Denied Persons List
- BIS Unverified List

### EU Lists
- EU Consolidated Sanctions List
- EU Terrorism List

### UK Lists
- UK Sanctions List
- HMRC Financial Sanctions

### UN Lists
- UN Security Council Consolidated List

### Other Lists
- World Bank Debarment List
- Interpol Red Notices
- PEP (Politically Exposed Persons)
- Adverse Media

## API Design

### Screen Party

```typescript
// POST /api/agents/sanctions-sentry/screen
interface ScreenRequest {
  name: string
  type: 'individual' | 'organization' | 'vessel'
  alternateNames?: string[]
  dateOfBirth?: string  // For individuals
  nationality?: string
  country?: string
  address?: string
  identifiers?: {
    type: string  // passport, tax_id, imo_number, etc.
    value: string
  }[]
  watchlistCategories?: string[]  // Specific lists to check
}

interface ScreenResponse {
  screeningId: string
  timestamp: string
  status: 'clear' | 'potential_match' | 'match'
  matchScore: number  // 0-100
  matches: {
    listName: string
    listCategory: string
    matchedName: string
    matchScore: number
    matchType: 'exact' | 'fuzzy' | 'alias'
    entityType: string
    details: {
      programs?: string[]
      reasons?: string[]
      dateAdded?: string
      dateUpdated?: string
      addresses?: string[]
      identifiers?: { type: string; value: string }[]
      aliases?: string[]
    }
    sourceUrl: string
  }[]
  recommendations: string[]
  nextSteps: string[]
}
```

### Batch Screening

```typescript
// POST /api/agents/sanctions-sentry/batch
interface BatchScreenRequest {
  parties: ScreenRequest[]
  callbackUrl?: string  // Webhook for async results
}

interface BatchScreenResponse {
  batchId: string
  totalParties: number
  status: 'processing' | 'completed'
  estimatedCompletion?: string
  resultsUrl?: string
}
```

### Monitor Party

```typescript
// POST /api/agents/sanctions-sentry/monitor
interface MonitorRequest {
  partyId: string  // Reference from your system
  name: string
  type: 'individual' | 'organization' | 'vessel'
  frequency: 'daily' | 'weekly' | 'monthly'
  notifyEmail: string
  notifyWebhook?: string
}

interface MonitorResponse {
  monitoringId: string
  partyId: string
  status: 'active'
  nextCheck: string
}
```

## Implementation Architecture

```
┌─────────────────┐
│ Screen Request  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Name Preprocessing                  │
│ ├── Normalize (lowercase, trim)     │
│ ├── Remove titles/suffixes          │
│ ├── Transliterate non-Latin chars   │
│ └── Generate phonetic variations    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Multi-List Search                   │
│ ├── Exact match                     │
│ ├── Fuzzy match (Levenshtein)       │
│ ├── Phonetic match (Soundex)        │
│ └── Alias matching                  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Match Scoring                       │
│ ├── Name similarity score           │
│ ├── Secondary data matching         │
│ └── Risk assessment                 │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Response        │
└─────────────────┘
```

## Database Schema

```typescript
export const screenings = pgTable('screenings', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  name: text('name').notNull(),
  type: text('type').notNull(),
  status: text('status').notNull(),
  matchScore: integer('match_score'),
  requestData: jsonb('request_data'),
  results: jsonb('results'),
  createdAt: timestamp('created_at').defaultNow(),
})

export const monitoredParties = pgTable('monitored_parties', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  partyId: text('party_id'),
  name: text('name').notNull(),
  type: text('type').notNull(),
  frequency: text('frequency').notNull(),
  lastChecked: timestamp('last_checked'),
  nextCheck: timestamp('next_check'),
  currentStatus: text('current_status'),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
})

export const screeningAlerts = pgTable('screening_alerts', {
  id: text('id').primaryKey(),
  monitoredPartyId: text('monitored_party_id').references(() => monitoredParties.id),
  alertType: text('alert_type').notNull(),
  listName: text('list_name'),
  details: jsonb('details'),
  acknowledgedAt: timestamp('acknowledged_at'),
  createdAt: timestamp('created_at').defaultNow(),
})
```

## Matching Algorithms

```typescript
// Fuzzy name matching
function calculateMatchScore(name1: string, name2: string): number {
  const exactScore = name1.toLowerCase() === name2.toLowerCase() ? 100 : 0
  const levenshteinScore = levenshteinSimilarity(name1, name2) * 100
  const soundexScore = soundexMatch(name1, name2) ? 70 : 0
  const jaroWinklerScore = jaroWinkler(name1, name2) * 100

  return Math.max(exactScore, levenshteinScore, soundexScore, jaroWinklerScore)
}

// Match threshold configuration
const MATCH_THRESHOLDS = {
  exact: 100,
  strong: 90,
  moderate: 75,
  weak: 60,
  review: 50,
}
```

## UI Components

### Screening Form

```tsx
export function ScreeningForm() {
  return (
    <form className="space-y-4">
      <div>
        <label>Party Name</label>
        <input
          name="name"
          placeholder="Enter name to screen..."
          className="w-full"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label>Type</label>
          <select name="type">
            <option value="individual">Individual</option>
            <option value="organization">Organization</option>
            <option value="vessel">Vessel</option>
          </select>
        </div>
        <div>
          <label>Country</label>
          <CountrySelect name="country" />
        </div>
      </div>

      <button type="submit" className="w-full">
        Screen Now
      </button>
    </form>
  )
}
```

### Match Result

```tsx
export function MatchResult({ match }: { match: Match }) {
  return (
    <div className="p-4 border border-red-500 bg-red-500/10 rounded-lg">
      <div className="flex justify-between items-start">
        <div>
          <h4 className="font-medium text-red-400">
            {match.matchedName}
          </h4>
          <p className="text-sm text-foreground-muted">{match.listName}</p>
        </div>
        <MatchScoreBadge score={match.matchScore} />
      </div>

      <div className="mt-3 space-y-2">
        {match.details.programs?.map((program) => (
          <span key={program} className="inline-block px-2 py-1 bg-red-500/20 rounded text-xs mr-2">
            {program}
          </span>
        ))}
      </div>

      {match.details.reasons && (
        <div className="mt-3">
          <p className="text-sm font-medium">Reasons:</p>
          <ul className="text-sm text-foreground-muted">
            {match.details.reasons.map((reason, i) => (
              <li key={i}>• {reason}</li>
            ))}
          </ul>
        </div>
      )}

      <a
        href={match.sourceUrl}
        target="_blank"
        className="mt-3 text-sm text-brand-400 hover:underline"
      >
        View on source list →
      </a>
    </div>
  )
}
```

### Clear Result

```tsx
export function ClearResult({ screening }: { screening: ScreenResponse }) {
  return (
    <div className="text-center py-8">
      <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
        <IconCheck className="w-8 h-8 text-green-400" />
      </div>
      <h3 className="text-xl font-medium text-green-400">No Matches Found</h3>
      <p className="text-foreground-muted mt-2">
        Screened against {listsCount} lists
      </p>
      <p className="text-sm text-foreground-muted mt-1">
        Screening ID: {screening.screeningId}
      </p>
      <button className="mt-4">
        Download Certificate
      </button>
    </div>
  )
}
```

## Success Metrics

- Screening speed: < 2 seconds
- List coverage: 300+ lists
- Update frequency: Daily
- False positive rate: < 10%
- Audit report generation: < 5 seconds
