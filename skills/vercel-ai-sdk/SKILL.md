# Vercel AI SDK

Patterns for building AI applications with the Vercel AI SDK.

## Triggers

Use when:
- Building AI chat interfaces
- Implementing streaming responses
- Working with OpenAI, Anthropic, or other LLM providers
- Creating AI-powered features

## Installation

```bash
pnpm add ai @ai-sdk/openai @ai-sdk/anthropic
```

## Core Concepts

### Providers

```typescript
import { openai } from '@ai-sdk/openai'
import { anthropic } from '@ai-sdk/anthropic'

// OpenAI
const model = openai('gpt-4o')

// Anthropic
const model = anthropic('claude-3-5-sonnet-20241022')
```

### Text Generation

```typescript
import { generateText } from 'ai'

const { text } = await generateText({
  model: openai('gpt-4o'),
  prompt: 'Write a haiku about programming',
})

console.log(text)
```

### Streaming Text

```typescript
import { streamText } from 'ai'

const result = await streamText({
  model: openai('gpt-4o'),
  prompt: 'Write a story about AI',
})

for await (const chunk of result.textStream) {
  process.stdout.write(chunk)
}
```

## Chat API Route

### Basic Chat Route

```typescript
// app/api/chat/route.ts
import { streamText } from 'ai'
import { openai } from '@ai-sdk/openai'

export async function POST(req: Request) {
  const { messages } = await req.json()

  const result = await streamText({
    model: openai('gpt-4o'),
    messages,
    system: `You are a helpful assistant for Export Arena,
             an AI workforce platform for global trade.`,
  })

  return result.toDataStreamResponse()
}
```

### With Tool Calling

```typescript
import { streamText, tool } from 'ai'
import { z } from 'zod'

export async function POST(req: Request) {
  const { messages } = await req.json()

  const result = await streamText({
    model: openai('gpt-4o'),
    messages,
    tools: {
      classifyProduct: tool({
        description: 'Classify a product with HS code',
        parameters: z.object({
          productDescription: z.string(),
          countryOfOrigin: z.string(),
        }),
        execute: async ({ productDescription, countryOfOrigin }) => {
          // Call classification API
          return { hsCode: '8471.30', confidence: 0.95 }
        },
      }),
      getShipmentStatus: tool({
        description: 'Get status of a shipment',
        parameters: z.object({
          trackingNumber: z.string(),
        }),
        execute: async ({ trackingNumber }) => {
          // Call tracking API
          return { status: 'in transit', eta: '2024-12-25' }
        },
      }),
    },
  })

  return result.toDataStreamResponse()
}
```

## React Hooks

### useChat Hook

```tsx
'use client'

import { useChat } from 'ai/react'

export function ChatWidget() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
  })

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`p-3 rounded-lg ${
              message.role === 'user' ? 'bg-blue-600 ml-auto' : 'bg-gray-700'
            } max-w-[80%]`}
          >
            {message.content}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Ask about global trade..."
            className="flex-1 bg-gray-800 rounded-lg px-4 py-2"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-600 px-4 py-2 rounded-lg"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  )
}
```

### useCompletion Hook

```tsx
'use client'

import { useCompletion } from 'ai/react'

export function ProductClassifier() {
  const { completion, input, handleInputChange, handleSubmit, isLoading } = useCompletion({
    api: '/api/classify',
  })

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={handleInputChange}
          placeholder="Describe your product..."
        />
        <button type="submit" disabled={isLoading}>
          Classify
        </button>
      </form>

      {completion && (
        <div className="mt-4">
          <h3>Classification Result:</h3>
          <pre>{completion}</pre>
        </div>
      )}
    </div>
  )
}
```

## RAG Integration

```typescript
import { streamText } from 'ai'
import { openai } from '@ai-sdk/openai'
import { db } from 'database'

export async function POST(req: Request) {
  const { messages } = await req.json()

  // Get the last user message for RAG
  const lastMessage = messages[messages.length - 1]

  // Retrieve relevant documents
  const relevantDocs = await db.execute(sql`
    SELECT content, metadata
    FROM documents
    ORDER BY embedding <=> ${await getEmbedding(lastMessage.content)}
    LIMIT 5
  `)

  // Build context from retrieved docs
  const context = relevantDocs
    .map((doc) => doc.content)
    .join('\n\n')

  const result = await streamText({
    model: openai('gpt-4o'),
    system: `You are a helpful assistant. Use the following context to answer questions:

${context}

If the context doesn't contain relevant information, say so.`,
    messages,
  })

  return result.toDataStreamResponse()
}
```

## Structured Output

```typescript
import { generateObject } from 'ai'
import { z } from 'zod'

const ProductClassification = z.object({
  hsCode: z.string().describe('6-digit HS code'),
  description: z.string().describe('Official description'),
  confidence: z.number().min(0).max(1),
  reasoning: z.string().describe('Classification reasoning'),
})

const result = await generateObject({
  model: openai('gpt-4o'),
  schema: ProductClassification,
  prompt: `Classify this product: ${productDescription}`,
})

console.log(result.object) // Typed object
```

## Error Handling

```typescript
import { streamText, APICallError, RetryError } from 'ai'

export async function POST(req: Request) {
  try {
    const { messages } = await req.json()

    const result = await streamText({
      model: openai('gpt-4o'),
      messages,
    })

    return result.toDataStreamResponse()
  } catch (error) {
    if (error instanceof APICallError) {
      console.error('API Error:', error.message)
      return new Response('AI service unavailable', { status: 503 })
    }
    if (error instanceof RetryError) {
      console.error('Retry exhausted:', error.message)
      return new Response('Request failed after retries', { status: 500 })
    }
    throw error
  }
}
```

## Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

## Best Practices

1. **Stream responses** for better UX
2. **Use structured output** for reliable parsing
3. **Implement rate limiting** on API routes
4. **Log usage** for cost monitoring
5. **Handle errors gracefully** with fallbacks
6. **Cache common queries** when appropriate
