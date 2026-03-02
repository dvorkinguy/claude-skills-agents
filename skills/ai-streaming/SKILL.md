# AI Streaming Patterns

Server-Sent Events and streaming response patterns for AI applications.

## Triggers

Use when:
- Building real-time AI chat
- Implementing streaming responses
- Creating long-running AI operations
- Showing progress indicators

## Server-Sent Events (SSE)

### Basic SSE Endpoint

```typescript
// pages/api/stream.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache, no-transform')
  res.setHeader('Connection', 'keep-alive')

  // Send events
  for (let i = 0; i < 10; i++) {
    res.write(`data: ${JSON.stringify({ count: i })}\n\n`)
    await new Promise((resolve) => setTimeout(resolve, 1000))
  }

  // End stream
  res.write('data: [DONE]\n\n')
  res.end()
}
```

### App Router SSE

```typescript
// app/api/stream/route.ts
export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        const data = `data: ${JSON.stringify({ count: i })}\n\n`
        controller.enqueue(encoder.encode(data))
        await new Promise((resolve) => setTimeout(resolve, 1000))
      }
      controller.enqueue(encoder.encode('data: [DONE]\n\n'))
      controller.close()
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  })
}
```

## Streaming AI Responses

### With Vercel AI SDK

```typescript
// app/api/chat/route.ts
import { streamText } from 'ai'
import { openai } from '@ai-sdk/openai'

export async function POST(req: Request) {
  const { messages } = await req.json()

  const result = await streamText({
    model: openai('gpt-4o'),
    messages,
  })

  // Returns properly formatted SSE stream
  return result.toDataStreamResponse()
}
```

### Manual OpenAI Streaming

```typescript
import OpenAI from 'openai'

const openai = new OpenAI()

export async function POST(req: Request) {
  const { messages } = await req.json()

  const stream = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages,
    stream: true,
  })

  const encoder = new TextEncoder()

  const readableStream = new ReadableStream({
    async start(controller) {
      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content || ''
        if (content) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ content })}\n\n`))
        }
      }
      controller.enqueue(encoder.encode('data: [DONE]\n\n'))
      controller.close()
    },
  })

  return new Response(readableStream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  })
}
```

## Client-Side Consumption

### Using EventSource

```typescript
function streamChat(message: string, onChunk: (text: string) => void) {
  return new Promise((resolve, reject) => {
    const eventSource = new EventSource(`/api/stream?message=${encodeURIComponent(message)}`)

    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        eventSource.close()
        resolve(undefined)
        return
      }

      const data = JSON.parse(event.data)
      onChunk(data.content)
    }

    eventSource.onerror = (error) => {
      eventSource.close()
      reject(error)
    }
  })
}

// Usage
await streamChat('Hello', (chunk) => {
  console.log(chunk)
})
```

### Using Fetch with ReadableStream

```typescript
async function streamChat(messages: Message[]) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
  })

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()

  if (!reader) throw new Error('No reader')

  let result = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') return result
        const parsed = JSON.parse(data)
        result += parsed.content
        // Update UI here
      }
    }
  }

  return result
}
```

### React Hook Pattern

```tsx
'use client'

import { useState, useCallback } from 'react'

export function useStreamingChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)

  const sendMessage = useCallback(async (content: string) => {
    const userMessage = { role: 'user', content }
    setMessages((prev) => [...prev, userMessage])

    setIsStreaming(true)
    let assistantContent = ''

    // Add placeholder assistant message
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }])

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMessage] }),
      })

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) throw new Error('No reader')

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        // Parse SSE format
        const lines = chunk.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ') && line !== 'data: [DONE]') {
            const data = JSON.parse(line.slice(6))
            assistantContent += data.content || ''
            // Update the last message
            setMessages((prev) => {
              const newMessages = [...prev]
              newMessages[newMessages.length - 1] = {
                role: 'assistant',
                content: assistantContent,
              }
              return newMessages
            })
          }
        }
      }
    } finally {
      setIsStreaming(false)
    }
  }, [messages])

  return { messages, sendMessage, isStreaming }
}
```

## Progress Streaming

For long-running operations:

```typescript
// API Route
export async function POST(req: Request) {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      const sendProgress = (step: string, progress: number) => {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ step, progress })}\n\n`)
        )
      }

      sendProgress('Analyzing document', 0)
      await analyzeDocument()
      sendProgress('Analyzing document', 100)

      sendProgress('Classifying product', 0)
      const result = await classifyProduct()
      sendProgress('Classifying product', 100)

      controller.enqueue(
        encoder.encode(`data: ${JSON.stringify({ result, done: true })}\n\n`)
      )
      controller.close()
    },
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
}
```

## Error Handling

```typescript
export async function POST(req: Request) {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Stream content...
      } catch (error) {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ error: 'An error occurred' })}\n\n`)
        )
      } finally {
        controller.close()
      }
    },
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
}
```

## Best Practices

1. **Always close streams** - Prevent memory leaks
2. **Handle disconnections** - Clean up on client disconnect
3. **Send heartbeats** - For long connections (every 30s)
4. **Parse SSE correctly** - Handle multi-line data
5. **Implement retry logic** - For failed connections
6. **Buffer appropriately** - Don't send too many small chunks
