# Component Scaffold

Generate Export Arena components with proper structure, types, and tests.

## Triggers

Use when:
- Creating new React components
- Generating component boilerplate
- Setting up component tests
- Following project conventions

## Component Template

### Basic Component

```typescript
// packages/ui/src/components/{ComponentName}/{ComponentName}.tsx
import { cn } from '../../lib/utils'
import type { ComponentProps } from 'react'

export interface {ComponentName}Props extends ComponentProps<'div'> {
  /** Optional variant */
  variant?: 'default' | 'primary' | 'secondary'
  /** Optional size */
  size?: 'sm' | 'md' | 'lg'
}

export function {ComponentName}({
  className,
  variant = 'default',
  size = 'md',
  children,
  ...props
}: {ComponentName}Props) {
  return (
    <div
      className={cn(
        // Base styles
        'rounded-lg border border-default',
        // Variant styles
        variant === 'default' && 'bg-surface-100',
        variant === 'primary' && 'bg-brand-500',
        variant === 'secondary' && 'bg-surface-200',
        // Size styles
        size === 'sm' && 'p-2 text-sm',
        size === 'md' && 'p-4 text-base',
        size === 'lg' && 'p-6 text-lg',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
```

### Index Export

```typescript
// packages/ui/src/components/{ComponentName}/index.ts
export { {ComponentName} } from './{ComponentName}'
export type { {ComponentName}Props } from './{ComponentName}'
```

### Package Export

```typescript
// packages/ui/src/index.ts
export * from './components/{ComponentName}'
```

## Compound Component Pattern

```typescript
// packages/ui/src/components/Card/Card.tsx
import { cn } from '../../lib/utils'
import { createContext, useContext } from 'react'

const CardContext = createContext<{ variant: string }>({ variant: 'default' })

export interface CardProps {
  variant?: 'default' | 'elevated'
  children: React.ReactNode
  className?: string
}

export function Card({ variant = 'default', children, className }: CardProps) {
  return (
    <CardContext.Provider value={{ variant }}>
      <div className={cn('rounded-lg border border-default', className)}>
        {children}
      </div>
    </CardContext.Provider>
  )
}

export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('px-4 py-3 border-b border-default', className)}>{children}</div>
}

export function CardContent({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('px-4 py-4', className)}>{children}</div>
}

export function CardFooter({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('px-4 py-3 border-t border-default', className)}>{children}</div>
}

Card.Header = CardHeader
Card.Content = CardContent
Card.Footer = CardFooter
```

## Test Template

```typescript
// packages/ui/src/components/{ComponentName}/{ComponentName}.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { {ComponentName} } from './{ComponentName}'

describe('{ComponentName}', () => {
  it('renders children', () => {
    render(<{ComponentName}>Test content</{ComponentName}>)
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<{ComponentName} className="custom-class">Content</{ComponentName}>)
    expect(screen.getByText('Content')).toHaveClass('custom-class')
  })

  it('renders with default variant', () => {
    render(<{ComponentName}>Content</{ComponentName}>)
    expect(screen.getByText('Content')).toHaveClass('bg-surface-100')
  })

  it('renders with primary variant', () => {
    render(<{ComponentName} variant="primary">Content</{ComponentName}>)
    expect(screen.getByText('Content')).toHaveClass('bg-brand-500')
  })

  it('handles click events', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<{ComponentName} onClick={onClick}>Clickable</{ComponentName}>)

    await user.click(screen.getByText('Clickable'))
    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
```

## Storybook Story Template

```typescript
// packages/ui/src/components/{ComponentName}/{ComponentName}.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { {ComponentName} } from './{ComponentName}'

const meta = {
  title: 'Components/{ComponentName}',
  component: {ComponentName},
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'primary', 'secondary'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
  },
} satisfies Meta<typeof {ComponentName}>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    children: 'Default {ComponentName}',
  },
}

export const Primary: Story = {
  args: {
    children: 'Primary {ComponentName}',
    variant: 'primary',
  },
}

export const AllSizes: Story = {
  render: () => (
    <div className="flex gap-4">
      <{ComponentName} size="sm">Small</{ComponentName}>
      <{ComponentName} size="md">Medium</{ComponentName}>
      <{ComponentName} size="lg">Large</{ComponentName}>
    </div>
  ),
}
```

## Page Component Template

```tsx
// apps/www/app/{route}/page.tsx
import { Metadata } from 'next'
import { {ComponentName} } from '@/components/{ComponentName}'

export const metadata: Metadata = {
  title: 'Page Title | Export Arena',
  description: 'Page description for SEO',
}

export default function {PageName}Page() {
  return (
    <main className="container py-12">
      <h1 className="text-3xl font-bold mb-8">Page Title</h1>
      <{ComponentName} />
    </main>
  )
}
```

## API Route Template

```typescript
// apps/www/pages/api/{endpoint}.ts
import type { NextApiRequest, NextApiResponse } from 'next'
import { getAuth } from '@clerk/nextjs/server'

type ResponseData = {
  success: boolean
  data?: unknown
  error?: string
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  // Only allow specific methods
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method not allowed' })
  }

  // Authenticate
  const { userId } = getAuth(req)
  if (!userId) {
    return res.status(401).json({ success: false, error: 'Unauthorized' })
  }

  try {
    // Handle request
    const data = await processRequest(req.body)
    return res.status(200).json({ success: true, data })
  } catch (error) {
    console.error('API Error:', error)
    return res.status(500).json({ success: false, error: 'Internal server error' })
  }
}
```

## Scaffold Script

```bash
#!/bin/bash
# scripts/scaffold-component.sh

COMPONENT_NAME=$1
COMPONENT_DIR="packages/ui/src/components/$COMPONENT_NAME"

mkdir -p "$COMPONENT_DIR"

# Create component file
cat > "$COMPONENT_DIR/$COMPONENT_NAME.tsx" << EOF
// Component template here
EOF

# Create index
cat > "$COMPONENT_DIR/index.ts" << EOF
export { $COMPONENT_NAME } from './$COMPONENT_NAME'
export type { ${COMPONENT_NAME}Props } from './$COMPONENT_NAME'
EOF

# Create test
cat > "$COMPONENT_DIR/$COMPONENT_NAME.test.tsx" << EOF
// Test template here
EOF

echo "Created $COMPONENT_NAME at $COMPONENT_DIR"
```
