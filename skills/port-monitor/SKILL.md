# Port Monitor Agent

AI agent for tracking containers and preventing demurrage/detention.

## Product Overview

**Name:** Port Monitor
**Pricing:** $500 - $1,000/month
**Target:** Importers, freight forwarders

## Value Proposition

- Real-time container tracking across ports
- Proactive Last Free Day (LFD) alerts
- D&D cost prevention (avg $300-500/container/day)
- Multi-carrier, multi-port visibility

## Job To Be Done

```
When containers arrive at port,
I want proactive alerts about free time expiration,
so I can avoid demurrage and detention fees.
```

## Pain Points Addressed

1. **Visibility:** Tracking across multiple terminals/carriers
2. **Timing:** Missing pickup deadlines
3. **Cost:** D&D fees average $300-500/day per container
4. **Coordination:** Aligning trucking with port availability

## API Design

### Add Container to Monitor

```typescript
// POST /api/agents/port-monitor/containers
interface AddContainerRequest {
  containerNumber: string
  blNumber?: string
  carrier: string
  vessel?: string
  voyage?: string
  portOfDischarge: string
  eta?: string
  consignee?: string
  customsBroker?: string
  notifyEmails?: string[]
  notifyWebhook?: string
}

interface ContainerResponse {
  id: string
  containerNumber: string
  status: ContainerStatus
  location: {
    port: string
    terminal: string
    position?: string
  }
  timeline: {
    event: string
    timestamp: string
    location?: string
  }[]
  freeDays: {
    demurrage: {
      startDate: string
      lastFreeDay: string
      daysRemaining: number
      dailyRate: number
      estimatedCharges: number
    }
    detention: {
      startDate: string
      lastFreeDay: string
      daysRemaining: number
      dailyRate: number
      estimatedCharges: number
    }
  }
  holds: {
    type: string
    agency: string
    status: 'active' | 'released'
    releasedAt?: string
  }[]
  availability: {
    isAvailable: boolean
    reason?: string
    estimatedAvailable?: string
  }
}

type ContainerStatus =
  | 'in_transit'
  | 'arrived'
  | 'discharged'
  | 'available'
  | 'on_hold'
  | 'gated_out'
  | 'returned'
```

### Get Alerts

```typescript
// GET /api/agents/port-monitor/alerts
interface AlertsResponse {
  alerts: {
    id: string
    containerId: string
    containerNumber: string
    type: 'lfd_warning' | 'lfd_urgent' | 'hold_detected' | 'availability'
    severity: 'high' | 'medium' | 'low'
    message: string
    actionRequired: string
    createdAt: string
    acknowledgedAt?: string
  }[]
}
```

### Dashboard Stats

```typescript
// GET /api/agents/port-monitor/dashboard
interface DashboardResponse {
  activeContainers: number
  atRiskContainers: number
  totalPotentialCharges: number
  chargesAvoided: number
  byPort: {
    port: string
    count: number
    atRisk: number
  }[]
  upcoming: {
    today: number
    tomorrow: number
    thisWeek: number
  }
}
```

## Implementation Architecture

```
┌─────────────────┐
│ Container Added │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Data Aggregation                    │
│ ├── Terminal APIs (direct)         │
│ ├── Carrier APIs                    │
│ ├── Port Community Systems          │
│ └── Screen scraping (fallback)      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Status Engine   │ ← Calculate LFD, holds, availability
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Alert Engine    │ ← Generate alerts based on rules
└────────┬────────┘
         │
         ├──────────────┐
         ▼              ▼
┌──────────────┐ ┌──────────────┐
│ Email/SMS    │ │ Webhook      │
└──────────────┘ └──────────────┘
```

## Alert Rules

```typescript
const ALERT_RULES = {
  lfd_3_days: {
    condition: (c) => c.freeDays.demurrage.daysRemaining <= 3,
    severity: 'medium',
    message: 'Last Free Day in 3 days',
  },
  lfd_1_day: {
    condition: (c) => c.freeDays.demurrage.daysRemaining <= 1,
    severity: 'high',
    message: 'URGENT: Last Free Day tomorrow',
  },
  lfd_expired: {
    condition: (c) => c.freeDays.demurrage.daysRemaining < 0,
    severity: 'high',
    message: 'Demurrage charges accumulating',
  },
  hold_detected: {
    condition: (c) => c.holds.some((h) => h.status === 'active'),
    severity: 'high',
    message: 'Container has active holds',
  },
  now_available: {
    condition: (c) => c.availability.isAvailable && c.status === 'available',
    severity: 'low',
    message: 'Container now available for pickup',
  },
}
```

## Database Schema

```typescript
export const monitoredContainers = pgTable('monitored_containers', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id),
  containerNumber: text('container_number').notNull(),
  blNumber: text('bl_number'),
  carrier: text('carrier').notNull(),
  portOfDischarge: text('port_of_discharge').notNull(),
  status: text('status').notNull(),
  eta: timestamp('eta'),
  arrived: timestamp('arrived'),
  discharged: timestamp('discharged'),
  lastFreeDay: timestamp('last_free_day'),
  gatedOut: timestamp('gated_out'),
  currentData: jsonb('current_data'),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
})

export const containerEvents = pgTable('container_events', {
  id: text('id').primaryKey(),
  containerId: text('container_id').references(() => monitoredContainers.id),
  event: text('event').notNull(),
  location: text('location'),
  timestamp: timestamp('timestamp').notNull(),
  rawData: jsonb('raw_data'),
  createdAt: timestamp('created_at').defaultNow(),
})

export const containerAlerts = pgTable('container_alerts', {
  id: text('id').primaryKey(),
  containerId: text('container_id').references(() => monitoredContainers.id),
  type: text('type').notNull(),
  severity: text('severity').notNull(),
  message: text('message').notNull(),
  actionRequired: text('action_required'),
  sentAt: timestamp('sent_at'),
  acknowledgedAt: timestamp('acknowledged_at'),
  createdAt: timestamp('created_at').defaultNow(),
})
```

## UI Components

### Container Dashboard

```tsx
export function PortMonitorDashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <StatCard title="Active Containers" value="45" />
        <StatCard title="At Risk" value="7" color="red" />
        <StatCard title="LFD Today" value="3" color="yellow" />
        <StatCard title="Charges Avoided" value="$12,450" color="green" />
      </div>

      <AlertBanner alerts={urgentAlerts} />

      <ContainerTable />
    </div>
  )
}
```

### LFD Countdown

```tsx
export function LFDCountdown({ daysRemaining }: { daysRemaining: number }) {
  return (
    <div className={cn(
      'px-3 py-1 rounded-full text-sm font-medium',
      daysRemaining > 3 && 'bg-green-500/20 text-green-400',
      daysRemaining <= 3 && daysRemaining > 1 && 'bg-yellow-500/20 text-yellow-400',
      daysRemaining <= 1 && 'bg-red-500/20 text-red-400 animate-pulse',
    )}>
      {daysRemaining > 0
        ? `${daysRemaining} day${daysRemaining !== 1 ? 's' : ''} remaining`
        : `${Math.abs(daysRemaining)} day${Math.abs(daysRemaining) !== 1 ? 's' : ''} overdue`
      }
    </div>
  )
}
```

### Container Timeline

```tsx
export function ContainerTimeline({ events }: { events: ContainerEvent[] }) {
  return (
    <div className="relative pl-8 space-y-4">
      <div className="absolute left-3 top-2 bottom-2 w-0.5 bg-surface-300" />

      {events.map((event, i) => (
        <div key={i} className="relative">
          <div className="absolute -left-5 w-4 h-4 rounded-full bg-brand-500" />
          <div>
            <p className="font-medium">{event.event}</p>
            <p className="text-sm text-foreground-muted">
              {event.location} • {formatDate(event.timestamp)}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
```

## Success Metrics

- D&D charges avoided per month
- Average LFD alert lead time: 3+ days
- Container visibility coverage: 100%
- Alert delivery time: < 5 minutes
- User engagement with alerts: > 80%
