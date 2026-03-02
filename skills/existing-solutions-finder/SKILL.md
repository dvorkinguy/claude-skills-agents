# Existing Solutions Finder

Find ready-made code, APIs, and tools before building from scratch.

## Triggers

Use when:
- Starting any new feature
- Implementing common functionality
- Integrating third-party services
- Looking for libraries or packages

## Search Priority Order

1. **Existing codebase** - Already built?
2. **Package ecosystem** - npm, pip, etc.
3. **shadcn/ui components** - UI primitives
4. **Vercel templates** - Full starters
5. **GitHub** - Open source implementations
6. **APIs** - Third-party services

## Search Commands

### 1. Check Existing Codebase

```bash
# Search for similar implementations
grep -r "keyword" --include="*.ts" --include="*.tsx"

# Find related components
find . -name "*ComponentName*" -type f

# Check package.json for installed packages
cat package.json | grep "package-name"
```

### 2. Package Ecosystem

```bash
# Search npm
npm search keyword

# Check package info
npm info package-name

# View package docs
npx pkginfo package-name
```

### 3. shadcn/ui Components

Available components to install:
```bash
# Check available components
npx shadcn@latest add --help

# Install component
npx shadcn@latest add button
npx shadcn@latest add dialog
npx shadcn@latest add form
npx shadcn@latest add table
npx shadcn@latest add toast
```

Full list: https://ui.shadcn.com/docs/components

### 4. Vercel Templates

```
https://vercel.com/templates
https://vercel.com/templates/next.js
```

Categories:
- AI/ML applications
- E-commerce
- SaaS starters
- Dashboards
- Blogs

### 5. GitHub Search

```
# Search repositories
site:github.com "nextjs authentication clerk"
site:github.com "drizzle orm postgres example"

# Search code
https://github.com/search?type=code&q=keyword
```

### 6. Third-Party APIs

For common needs, prefer APIs over building:

| Need | API |
|------|-----|
| Auth | Clerk, Auth0 |
| Payments | Stripe |
| Email | Resend, SendGrid |
| SMS | Twilio |
| File Storage | S3, Cloudflare R2 |
| Search | Algolia, Typesense |
| Analytics | Posthog, Mixpanel |
| Feature Flags | LaunchDarkly, Vercel Flags |
| AI/LLM | OpenAI, Anthropic, Vercel AI SDK |
| Vector DB | Pinecone, Neon pgvector |

## Pre-Implementation Checklist

Before writing any code, ask:

- [ ] Does this exist in our codebase already?
- [ ] Is there a well-maintained npm package for this?
- [ ] Is there a shadcn/ui component for this?
- [ ] Is there a Vercel template for this pattern?
- [ ] Is there an API that solves this better?
- [ ] Is there an open-source implementation to reference?

## Package Quality Checks

Before adding a dependency:

```bash
# Check weekly downloads
npm info package-name

# Check last publish date
npm view package-name time

# Check bundle size
npx bundlephobia package-name

# Check security
npm audit
```

Red flags:
- Last updated > 1 year ago
- < 1,000 weekly downloads
- No TypeScript types
- Many open security issues

## Common Solutions

### Authentication
- Already have: **Clerk** (use it!)
- Don't rebuild auth

### Forms
- Use: **react-hook-form** + **zod**
- Already in project dependencies

### Data Tables
- Use: **@tanstack/react-table**
- Or: shadcn/ui data-table

### Date Handling
- Use: **date-fns** (already installed)
- Not: moment.js (deprecated, large)

### HTTP Requests
- Server: Native **fetch**
- Client: **swr** or **@tanstack/query**

### State Management
- Local: **useState**, **useReducer**
- Global: **Zustand** (if needed)
- Server: **@tanstack/query**

### Animations
- Use: **framer-motion** (already installed)

### Icons
- Use: **lucide-react** (already in packages/icons)

### Rich Text
- CMS: **Payload Lexical** (already configured)
- App: Consider **tiptap**

### Charts
- Use: **recharts** (React-friendly)

### AI/LLM
- Use: **Vercel AI SDK** (ai package)
- Already planned for chat feature

## Quick Reference URLs

```
shadcn/ui:        https://ui.shadcn.com
Vercel AI SDK:    https://sdk.vercel.ai
Clerk:            https://clerk.com/docs
Drizzle:          https://orm.drizzle.team
Neon:             https://neon.tech/docs
Stripe:           https://stripe.com/docs
```

## Anti-Patterns

1. **NIH Syndrome**: Building what exists
2. **Dependency Hoarding**: Adding packages for one-liners
3. **Wrong Abstraction**: Using heavy library for simple need
4. **Ignoring Types**: Choosing JS package when TS exists

## Decision Tree

```
Need feature?
    │
    ├─ Already in codebase? → Use it
    │
    ├─ Standard UI? → shadcn/ui
    │
    ├─ Common pattern? → npm package
    │
    ├─ Complex domain? → Third-party API
    │
    └─ Truly unique? → Build it
```
