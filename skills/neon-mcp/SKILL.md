# Neon MCP Integration

Reference for using Neon PostgreSQL with Export Arena.

## Connection Details

Export Arena uses Neon PostgreSQL as the primary database.

### Environment Variables

```bash
# Database URL (pooled connection)
DATABASE_URL=postgresql://neondb_owner:...@ep-xxx-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require

# Direct connection (for migrations)
DATABASE_URL_UNPOOLED=postgresql://neondb_owner:...@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

### Drizzle Configuration

```typescript
// packages/database/drizzle.config.ts
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  schema: './schema/index.ts',
  out: './migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
})
```

### Database Client

```typescript
// packages/database/client.ts
import { drizzle } from 'drizzle-orm/neon-http'
import { neon } from '@neondatabase/serverless'
import * as schema from './schema'

const sql = neon(process.env.DATABASE_URL!)
export const db = drizzle(sql, { schema })
```

## Common Operations

### Query

```typescript
import { db, users, eq } from 'database'

// Find one
const user = await db.query.users.findFirst({
  where: eq(users.id, userId),
})

// Find many
const allUsers = await db.query.users.findMany({
  limit: 10,
})
```

### Insert

```typescript
await db.insert(users).values({
  id: clerkUserId,
  email: 'user@example.com',
  firstName: 'John',
  lastName: 'Doe',
})
```

### Update

```typescript
await db.update(users)
  .set({ firstName: 'Jane' })
  .where(eq(users.id, userId))
```

### Delete

```typescript
await db.delete(users).where(eq(users.id, userId))
```

## Schema Management

### Push Schema

```bash
cd packages/database
pnpm db:push
```

### Generate Migration

```bash
cd packages/database
pnpm db:generate
```

### Run Migrations

```bash
cd packages/database
pnpm db:migrate
```

### Open Drizzle Studio

```bash
cd packages/database
pnpm db:studio
```

## pgvector for RAG

### Enable Extension

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Vector Column

```typescript
import { pgTable, text, vector } from 'drizzle-orm/pg-core'

export const documents = pgTable('documents', {
  id: text('id').primaryKey(),
  content: text('content').notNull(),
  embedding: vector('embedding', { dimensions: 1536 }),
})
```

### Similarity Search

```typescript
import { sql } from 'drizzle-orm'

const results = await db.execute(sql`
  SELECT id, content,
    1 - (embedding <=> ${JSON.stringify(queryEmbedding)}::vector) as similarity
  FROM documents
  ORDER BY embedding <=> ${JSON.stringify(queryEmbedding)}::vector
  LIMIT 5
`)
```

## Neon Console

- **Dashboard:** https://console.neon.tech
- **Project:** exportarena
- **Branch:** main

## Connection Pooling

Neon provides connection pooling by default:

- Pooled: `...-pooler.eu-central-1.aws.neon.tech` (use for app)
- Direct: `...eu-central-1.aws.neon.tech` (use for migrations)

### Pool Configuration

```typescript
db: postgresAdapter({
  pool: {
    connectionString: process.env.DATABASE_URL,
    max: 25,  // Max connections (keep low for serverless)
    min: 0,
    idleTimeoutMillis: 0,
  },
})
```

## Branching (Dev/Staging)

Neon supports database branching:

```bash
# Create branch
neon branches create --name feature-123

# Connect to branch
DATABASE_URL=postgresql://...@ep-feature-123-pooler.../neondb
```

## Monitoring

- Connection count in Neon Console
- Query performance in Drizzle Studio
- Logs in Neon Console → Activity
