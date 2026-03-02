# AI Chat UI

Chat interface components for Export Arena with dark theme.

## Triggers

Use when:
- Building chat interfaces
- Creating message bubbles
- Implementing typing indicators
- Designing AI assistant UIs

## Components

### ChatWidget (Floating)

```tsx
'use client'

import { useState } from 'react'
import { IconMessageCircle, IconX } from 'icons'
import { ChatWindow } from './ChatWindow'

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-brand-500 hover:bg-brand-600 text-white shadow-lg transition-all"
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? <IconX size={24} /> : <IconMessageCircle size={24} />}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 h-[500px] rounded-lg shadow-2xl overflow-hidden border border-default bg-surface-100">
          <ChatWindow onClose={() => setIsOpen(false)} />
        </div>
      )}
    </>
  )
}
```

### ChatWindow

```tsx
'use client'

import { useChat } from 'ai/react'
import { ChatHeader } from './ChatHeader'
import { ChatMessages } from './ChatMessages'
import { ChatInput } from './ChatInput'

interface ChatWindowProps {
  onClose: () => void
}

export function ChatWindow({ onClose }: ChatWindowProps) {
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    error,
  } = useChat({
    api: '/api/chat',
  })

  return (
    <div className="flex flex-col h-full">
      <ChatHeader onClose={onClose} />

      <ChatMessages messages={messages} isLoading={isLoading} />

      {error && (
        <div className="px-4 py-2 bg-red-500/10 text-red-400 text-sm">
          {error.message || 'An error occurred'}
        </div>
      )}

      <ChatInput
        input={input}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  )
}
```

### ChatHeader

```tsx
import { IconX, IconRefresh } from 'icons'

interface ChatHeaderProps {
  onClose: () => void
  onReset?: () => void
}

export function ChatHeader({ onClose, onReset }: ChatHeaderProps) {
  return (
    <div className="flex items-center justify-between px-4 py-3 border-b border-default bg-surface-200">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center">
          <span className="text-white text-sm font-medium">EA</span>
        </div>
        <div>
          <h3 className="font-medium text-foreground">Export Arena</h3>
          <p className="text-xs text-foreground-muted">AI Assistant</p>
        </div>
      </div>

      <div className="flex gap-2">
        {onReset && (
          <button
            onClick={onReset}
            className="p-2 rounded-lg hover:bg-surface-300 text-foreground-muted"
            title="New conversation"
          >
            <IconRefresh size={16} />
          </button>
        )}
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-surface-300 text-foreground-muted"
          title="Close"
        >
          <IconX size={16} />
        </button>
      </div>
    </div>
  )
}
```

### ChatMessages

```tsx
import { useRef, useEffect } from 'react'
import type { Message } from 'ai'
import { ChatMessage } from './ChatMessage'
import { TypingIndicator } from './TypingIndicator'

interface ChatMessagesProps {
  messages: Message[]
  isLoading: boolean
}

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto p-4 space-y-4"
    >
      {/* Welcome message if no messages */}
      {messages.length === 0 && (
        <div className="text-center py-8">
          <p className="text-foreground-muted">
            Hi! I&apos;m your Export Arena assistant. How can I help with
            your global trade operations today?
          </p>
        </div>
      )}

      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}

      {isLoading && <TypingIndicator />}
    </div>
  )
}
```

### ChatMessage

```tsx
import type { Message } from 'ai'
import { cn } from 'ui/lib/utils'
import ReactMarkdown from 'react-markdown'

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-3',
          isUser
            ? 'bg-brand-500 text-white'
            : 'bg-surface-200 text-foreground'
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
```

### ChatInput

```tsx
import { FormEvent } from 'react'
import { IconSend } from 'icons'

interface ChatInputProps {
  input: string
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  onSubmit: (e: FormEvent<HTMLFormElement>) => void
  isLoading: boolean
}

export function ChatInput({ input, onChange, onSubmit, isLoading }: ChatInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSubmit(e as any)
    }
  }

  return (
    <form onSubmit={onSubmit} className="p-4 border-t border-default">
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={onChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask about global trade..."
          disabled={isLoading}
          rows={1}
          className="flex-1 resize-none rounded-lg bg-surface-200 px-4 py-3 text-foreground placeholder:text-foreground-muted focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="p-3 rounded-lg bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <IconSend size={20} />
        </button>
      </div>
    </form>
  )
}
```

### TypingIndicator

```tsx
export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-surface-200 rounded-lg px-4 py-3">
        <div className="flex gap-1">
          <span className="w-2 h-2 bg-foreground-muted rounded-full animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 bg-foreground-muted rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 bg-foreground-muted rounded-full animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  )
}
```

## Lead Capture Form

```tsx
'use client'

import { useState } from 'react'
import { z } from 'zod'

const LeadSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
  company: z.string().optional(),
  message: z.string().optional(),
})

interface LeadCaptureProps {
  onSubmit: (data: z.infer<typeof LeadSchema>) => Promise<void>
  onSkip: () => void
}

export function LeadCapture({ onSubmit, onSkip }: LeadCaptureProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = Object.fromEntries(formData)

    const result = LeadSchema.safeParse(data)
    if (!result.success) {
      setErrors(
        result.error.issues.reduce(
          (acc, issue) => ({ ...acc, [issue.path[0]]: issue.message }),
          {}
        )
      )
      return
    }

    setIsLoading(true)
    try {
      await onSubmit(result.data)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-4 border border-brand-500/30 rounded-lg bg-brand-500/5">
      <h4 className="font-medium mb-2">Want to learn more?</h4>
      <p className="text-sm text-foreground-muted mb-4">
        Leave your details and we&apos;ll reach out with more information.
      </p>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <input
            name="name"
            placeholder="Your name"
            className="w-full px-3 py-2 rounded-lg bg-surface-200 text-foreground placeholder:text-foreground-muted"
          />
          {errors.name && <p className="text-red-400 text-xs mt-1">{errors.name}</p>}
        </div>

        <div>
          <input
            name="email"
            type="email"
            placeholder="Work email"
            className="w-full px-3 py-2 rounded-lg bg-surface-200 text-foreground placeholder:text-foreground-muted"
          />
          {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
        </div>

        <input
          name="company"
          placeholder="Company (optional)"
          className="w-full px-3 py-2 rounded-lg bg-surface-200 text-foreground placeholder:text-foreground-muted"
        />

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 py-2 rounded-lg bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-50"
          >
            {isLoading ? 'Sending...' : 'Get in touch'}
          </button>
          <button
            type="button"
            onClick={onSkip}
            className="px-4 py-2 rounded-lg bg-surface-200 text-foreground-muted hover:bg-surface-300"
          >
            Skip
          </button>
        </div>
      </form>
    </div>
  )
}
```

## Suggested Questions

```tsx
interface SuggestedQuestionsProps {
  questions: string[]
  onSelect: (question: string) => void
}

export function SuggestedQuestions({ questions, onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="space-y-2">
      <p className="text-xs text-foreground-muted">Suggested questions:</p>
      <div className="flex flex-wrap gap-2">
        {questions.map((question) => (
          <button
            key={question}
            onClick={() => onSelect(question)}
            className="px-3 py-1.5 text-sm rounded-full border border-default hover:border-brand-500 hover:bg-brand-500/10 transition-colors"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}
```

## Dark Theme Colors

Use these Tailwind classes for consistency:

```tsx
// Backgrounds
'bg-surface-100'  // Main chat background
'bg-surface-200'  // Message bubbles (assistant)
'bg-surface-300'  // Hover states
'bg-brand-500'    // User messages, buttons

// Text
'text-foreground'        // Primary text
'text-foreground-muted'  // Secondary text
'text-white'             // On brand backgrounds

// Borders
'border-default'  // Standard borders
```
