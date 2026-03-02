# Vetting Officer Agent

AI agent for supplier due diligence and fraud prevention.

## Product Overview

**Name:** Vetting Officer
**Pricing:** Per-check pricing (varies by depth)
**Target:** Procurement teams, sourcing managers

## Value Proposition

- Comprehensive supplier background checks
- Fraud detection and risk scoring
- Verify company legitimacy before doing business
- Reduce supplier-related losses

## Job To Be Done

```
When onboarding a new supplier,
I want to verify their legitimacy and assess risk,
so I can avoid fraud and protect my business.
```

## Pain Points Addressed

1. **Fraud Risk:** Fake companies, shell corporations
2. **Due Diligence Time:** Manual research takes hours
3. **Information Gaps:** Hard to find reliable data
4. **Red Flags:** Easy to miss warning signs

## Check Tiers

| Tier | Name | Includes | Price |
|------|------|----------|-------|
| 1 | Quick Check | Basic registration, sanctions | $25 |
| 2 | Standard | + Financials, ownership | $100 |
| 3 | Enhanced | + Site visits, references | $500 |
| 4 | Deep Dive | + Investigations, forensics | $2,000+ |

## API Design

### Submit Vetting Request

```typescript
// POST /api/agents/vetting-officer/vet
interface VettingRequest {
  company: {
    name: string
    registrationNumber?: string
    taxId?: string
    country: string
    address?: string
    website?: string
    contacts?: {
      name: string
      title: string
      email?: string
      phone?: string
    }[]
  }
  tier: 'quick' | 'standard' | 'enhanced' | 'deep'
  purpose: string
  urgency: 'normal' | 'rush'
  additionalChecks?: string[]
}

interface VettingResponse {
  vettingId: string
  status: 'processing' | 'completed' | 'needs_review'
  estimatedCompletion: string
  tier: string

  // Quick Check (always included)
  registration: {
    verified: boolean
    companyName: string
    registrationNumber: string
    incorporationDate: string
    status: 'active' | 'dissolved' | 'suspended' | 'unknown'
    registeredAddress: string
    companyType: string
  }

  sanctionsCheck: {
    status: 'clear' | 'match' | 'potential_match'
    matches: any[]
  }

  // Standard tier adds:
  financials?: {
    available: boolean
    latestYear?: number
    revenue?: number
    profit?: number
    assets?: number
    liabilities?: number
    employees?: number
    creditRating?: string
    paymentHistory?: string
  }

  ownership?: {
    directors: {
      name: string
      title: string
      appointedDate: string
      nationality?: string
      otherDirectorships?: number
    }[]
    shareholders: {
      name: string
      shareholding: string
      type: 'individual' | 'company'
    }[]
    ultimateBeneficialOwners?: {
      name: string
      nationality: string
      ownership: string
    }[]
  }

  // Enhanced tier adds:
  siteVerification?: {
    completed: boolean
    verifiedAddress: boolean
    photoEvidence: string[]
    operationalStatus: string
    notes: string
  }

  references?: {
    contacted: number
    verified: number
    summary: string
    details: {
      company: string
      contact: string
      relationship: string
      duration: string
      rating: number
      comments: string
    }[]
  }

  // Risk Assessment (all tiers)
  riskAssessment: {
    overallScore: number  // 0-100 (higher = safer)
    riskLevel: 'low' | 'medium' | 'high' | 'critical'
    flags: {
      category: string
      description: string
      severity: 'low' | 'medium' | 'high'
    }[]
    recommendations: string[]
  }
}
```

## Red Flags Detection

```typescript
const RED_FLAGS = {
  // Registration
  recently_incorporated: {
    condition: (days: number) => days < 180,
    severity: 'medium',
    message: 'Company incorporated less than 6 months ago',
  },
  no_registered_address: {
    condition: (address: string) => !address,
    severity: 'high',
    message: 'No registered address on file',
  },
  virtual_office: {
    condition: (address: string) => isVirtualOffice(address),
    severity: 'medium',
    message: 'Address appears to be a virtual office',
  },

  // Financial
  no_financials: {
    condition: (available: boolean) => !available,
    severity: 'medium',
    message: 'No financial statements available',
  },
  negative_equity: {
    condition: (equity: number) => equity < 0,
    severity: 'high',
    message: 'Company has negative equity',
  },

  // Ownership
  shell_company_indicators: {
    condition: (ownership: any) => hasShellIndicators(ownership),
    severity: 'high',
    message: 'Ownership structure has shell company characteristics',
  },
  director_disqualified: {
    condition: (directors: any[]) => hasDisqualifiedDirector(directors),
    severity: 'critical',
    message: 'Director has been disqualified',
  },

  // Online Presence
  no_website: {
    condition: (website: string) => !website,
    severity: 'low',
    message: 'No company website found',
  },
  new_domain: {
    condition: (domainAge: number) => domainAge < 90,
    severity: 'medium',
    message: 'Website domain registered recently',
  },

  // Behavioral
  refuses_documentation: {
    condition: (refused: boolean) => refused,
    severity: 'critical',
    message: 'Company refuses to provide documentation',
  },
  inconsistent_information: {
    condition: (inconsistencies: number) => inconsistencies > 2,
    severity: 'high',
    message: 'Multiple information inconsistencies detected',
  },
}
```

## Database Schema

```typescript
export const vettingRequests = pgTable('vetting_requests', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  companyName: text('company_name').notNull(),
  country: text('country').notNull(),
  tier: text('tier').notNull(),
  status: text('status').notNull(),
  requestData: jsonb('request_data'),
  results: jsonb('results'),
  riskScore: integer('risk_score'),
  riskLevel: text('risk_level'),
  completedAt: timestamp('completed_at'),
  createdAt: timestamp('created_at').defaultNow(),
})

export const supplierProfiles = pgTable('supplier_profiles', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  companyName: text('company_name').notNull(),
  country: text('country').notNull(),
  latestVettingId: text('latest_vetting_id').references(() => vettingRequests.id),
  approvalStatus: text('approval_status'), // approved, conditional, rejected
  riskLevel: text('risk_level'),
  notes: text('notes'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
})
```

## UI Components

### Vetting Dashboard

```tsx
export function VettingDashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <StatCard title="Suppliers Vetted" value="234" />
        <StatCard title="High Risk" value="12" color="red" />
        <StatCard title="Pending Review" value="5" />
        <StatCard title="Approved" value="189" color="green" />
      </div>

      <div className="flex gap-4">
        <Button>New Vetting</Button>
        <Button variant="secondary">Bulk Import</Button>
      </div>

      <VettingTable />
    </div>
  )
}
```

### Risk Score Display

```tsx
export function RiskScore({ score, level }: { score: number; level: string }) {
  const colors = {
    low: 'bg-green-500',
    medium: 'bg-yellow-500',
    high: 'bg-orange-500',
    critical: 'bg-red-500',
  }

  return (
    <div className="text-center">
      <div className="relative w-32 h-32 mx-auto">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            className="text-surface-300"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            strokeDasharray={`${(score / 100) * 352} 352`}
            className={colors[level as keyof typeof colors]}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-3xl font-bold">{score}</span>
        </div>
      </div>
      <p className={cn(
        'mt-2 font-medium capitalize',
        level === 'low' && 'text-green-400',
        level === 'medium' && 'text-yellow-400',
        level === 'high' && 'text-orange-400',
        level === 'critical' && 'text-red-400',
      )}>
        {level} Risk
      </p>
    </div>
  )
}
```

### Red Flag Alert

```tsx
export function RedFlagAlert({ flag }: { flag: RedFlag }) {
  return (
    <div className={cn(
      'flex items-start gap-3 p-3 rounded-lg',
      flag.severity === 'critical' && 'bg-red-500/20 border border-red-500',
      flag.severity === 'high' && 'bg-orange-500/20 border border-orange-500',
      flag.severity === 'medium' && 'bg-yellow-500/20 border border-yellow-500',
      flag.severity === 'low' && 'bg-blue-500/20 border border-blue-500',
    )}>
      <IconAlertTriangle className={cn(
        'flex-shrink-0',
        flag.severity === 'critical' && 'text-red-400',
        flag.severity === 'high' && 'text-orange-400',
        flag.severity === 'medium' && 'text-yellow-400',
        flag.severity === 'low' && 'text-blue-400',
      )} />
      <div>
        <p className="font-medium">{flag.category}</p>
        <p className="text-sm text-foreground-muted">{flag.description}</p>
      </div>
    </div>
  )
}
```

## Success Metrics

- Fraud detection rate: > 95%
- Average vetting time (quick): < 5 minutes
- Average vetting time (standard): < 24 hours
- False positive rate: < 5%
- Customer fraud losses prevented: Track $
