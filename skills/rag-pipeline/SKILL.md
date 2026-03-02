# RAG Pipeline

Retrieval-Augmented Generation patterns with Neon pgvector.

## Triggers

Use when:
- Building knowledge-base chat
- Implementing document Q&A
- Creating semantic search
- Indexing documents for AI retrieval

## Architecture

```
Documents → Chunking → Embedding → Vector DB (pgvector)
                                        │
Query → Embedding ──────────────────────┤
                                        ▼
                                    Retrieval
                                        │
                                        ▼
                              Context + Query → LLM → Response
```

## Database Schema

```typescript
// packages/database/schema/documents.ts
import { pgTable, text, timestamp, vector, index } from 'drizzle-orm/pg-core'

export const documents = pgTable('documents', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  content: text('content').notNull(),
  metadata: text('metadata').$type<Record<string, any>>(),
  embedding: vector('embedding', { dimensions: 1536 }),
  createdAt: timestamp('created_at').defaultNow().notNull(),
}, (table) => ({
  embeddingIdx: index('embedding_idx').using('hnsw', table.embedding.op('vector_cosine_ops')),
}))
```

### Enable pgvector

```sql
-- Run in Neon SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

## Document Ingestion

### Chunking

```typescript
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter'

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
  separators: ['\n\n', '\n', '. ', ' ', ''],
})

async function chunkDocument(content: string) {
  return splitter.splitText(content)
}
```

### Embedding

```typescript
import OpenAI from 'openai'

const openai = new OpenAI()

async function getEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  })
  return response.data[0].embedding
}

async function getEmbeddings(texts: string[]): Promise<number[][]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: texts,
  })
  return response.data.map((d) => d.embedding)
}
```

### Full Ingestion Pipeline

```typescript
import { db, documents } from 'database'

async function ingestDocument(
  content: string,
  metadata: Record<string, any>
) {
  // 1. Chunk the document
  const chunks = await chunkDocument(content)

  // 2. Get embeddings for all chunks
  const embeddings = await getEmbeddings(chunks)

  // 3. Store in database
  const records = chunks.map((chunk, i) => ({
    content: chunk,
    metadata: { ...metadata, chunkIndex: i },
    embedding: embeddings[i],
  }))

  await db.insert(documents).values(records)

  return { chunksCreated: chunks.length }
}
```

## Retrieval

### Similarity Search

```typescript
import { sql } from 'drizzle-orm'
import { db, documents } from 'database'

async function searchDocuments(
  query: string,
  limit: number = 5
): Promise<typeof documents.$inferSelect[]> {
  // 1. Get query embedding
  const queryEmbedding = await getEmbedding(query)

  // 2. Search by similarity
  const results = await db.execute(sql`
    SELECT
      id,
      content,
      metadata,
      1 - (embedding <=> ${JSON.stringify(queryEmbedding)}::vector) as similarity
    FROM documents
    ORDER BY embedding <=> ${JSON.stringify(queryEmbedding)}::vector
    LIMIT ${limit}
  `)

  return results.rows as any[]
}
```

### Hybrid Search (Semantic + Keyword)

```typescript
async function hybridSearch(
  query: string,
  limit: number = 5
) {
  const queryEmbedding = await getEmbedding(query)

  // Combine vector similarity with full-text search
  const results = await db.execute(sql`
    SELECT
      id,
      content,
      metadata,
      (
        0.7 * (1 - (embedding <=> ${JSON.stringify(queryEmbedding)}::vector))
        + 0.3 * ts_rank(to_tsvector('english', content), plainto_tsquery('english', ${query}))
      ) as score
    FROM documents
    WHERE
      to_tsvector('english', content) @@ plainto_tsquery('english', ${query})
      OR embedding <=> ${JSON.stringify(queryEmbedding)}::vector < 0.5
    ORDER BY score DESC
    LIMIT ${limit}
  `)

  return results.rows
}
```

## RAG Chat API

```typescript
// app/api/chat/route.ts
import { streamText } from 'ai'
import { openai } from '@ai-sdk/openai'

export async function POST(req: Request) {
  const { messages } = await req.json()

  // Get the latest user message
  const lastMessage = messages[messages.length - 1]

  // Retrieve relevant context
  const relevantDocs = await searchDocuments(lastMessage.content, 5)
  const context = relevantDocs
    .map((doc) => doc.content)
    .join('\n\n---\n\n')

  const result = await streamText({
    model: openai('gpt-4o'),
    system: `You are a helpful assistant for Export Arena.

Use the following context to answer questions. If the context doesn't contain
relevant information, say "I don't have information about that in my knowledge base."

Context:
${context}

Always cite which part of the context you're using when answering.`,
    messages,
  })

  return result.toDataStreamResponse()
}
```

## Document Sources

### PDF Ingestion

```typescript
import pdf from 'pdf-parse'

async function ingestPDF(buffer: Buffer, filename: string) {
  const data = await pdf(buffer)

  await ingestDocument(data.text, {
    source: 'pdf',
    filename,
    pages: data.numpages,
  })
}
```

### Web Page Ingestion

```typescript
import { load } from 'cheerio'

async function ingestWebPage(url: string) {
  const response = await fetch(url)
  const html = await response.text()
  const $ = load(html)

  // Extract main content
  const content = $('article, main, .content').text()
    || $('body').text()

  await ingestDocument(content, {
    source: 'web',
    url,
    title: $('title').text(),
  })
}
```

### Markdown Ingestion

```typescript
import { marked } from 'marked'

async function ingestMarkdown(content: string, filename: string) {
  // Convert to plain text
  const plainText = marked.parse(content, { async: false })
    .replace(/<[^>]*>/g, '') // Strip HTML

  await ingestDocument(plainText, {
    source: 'markdown',
    filename,
  })
}
```

## API for Document Management

```typescript
// app/api/documents/route.ts

// Upload document
export async function POST(req: Request) {
  const formData = await req.formData()
  const file = formData.get('file') as File

  if (file.type === 'application/pdf') {
    const buffer = Buffer.from(await file.arrayBuffer())
    await ingestPDF(buffer, file.name)
  } else if (file.type === 'text/markdown') {
    const text = await file.text()
    await ingestMarkdown(text, file.name)
  }

  return Response.json({ success: true })
}

// Search documents
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const query = searchParams.get('q')

  if (!query) {
    return Response.json({ error: 'Query required' }, { status: 400 })
  }

  const results = await searchDocuments(query)
  return Response.json({ results })
}
```

## Performance Tips

1. **Batch embeddings** - Send multiple texts in one API call
2. **Use HNSW index** - Faster than IVFFlat for most cases
3. **Tune chunk size** - 500-1000 tokens is typical
4. **Cache embeddings** - Don't re-embed unchanged docs
5. **Filter before search** - Use metadata to narrow results

```sql
-- Filtered search example
SELECT * FROM documents
WHERE metadata->>'source' = 'pdf'
ORDER BY embedding <=> $1::vector
LIMIT 5;
```
