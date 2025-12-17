# Complete Skill Creation Guide

## Table of Contents
1. [What Skills Provide](#what-skills-provide)
2. [Core Principles](#core-principles)
3. [Skill Anatomy](#skill-anatomy)
4. [Degrees of Freedom](#degrees-of-freedom)
5. [Progressive Disclosure](#progressive-disclosure)
6. [Description Writing](#description-writing)
7. [Testing Strategy](#testing-strategy)
8. [Common Mistakes](#common-mistakes)

---

## What Skills Provide

Skills are modular packages that extend Claude's capabilities:

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex tasks

Think of skills as "onboarding guides" that transform Claude from general-purpose to specialized.

---

## Core Principles

### Concise is Key

The context window is shared. Skills compete with:
- System prompt
- Conversation history
- Other skills' metadata
- User requests

**Default assumption: Claude is already very smart.**

Challenge each piece of information:
- "Does Claude really need this explanation?"
- "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Token Budget Guidelines

| Resource | Target | Max |
|----------|--------|-----|
| Description | ~100 words | 1024 chars |
| SKILL.md body | <2k words | 500 lines |
| References | As needed | Split at 10k words |

---

## Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown body (required)
└── Bundled Resources (optional)
    ├── scripts/      - Executable code
    ├── references/   - On-demand documentation
    └── assets/       - Output files (templates, images)
```

### Scripts (`scripts/`)

**When to include:**
- Same code rewritten repeatedly
- Deterministic reliability needed
- Complex file operations

**Best practices:**
- Test before packaging
- Include shebang: `#!/usr/bin/env python3`
- Make executable: `chmod +x script.py`
- Handle errors gracefully

**Example use cases:**
- PDF rotation/manipulation
- File format conversion
- Data validation
- API calls with specific auth

### References (`references/`)

**When to include:**
- Documentation Claude should reference while working
- Content too long for SKILL.md
- Domain-specific knowledge

**Best practices:**
- Add table of contents for >100 lines
- Split by domain for >500 lines
- No duplication with SKILL.md
- Reference clearly from SKILL.md

**Example use cases:**
- Database schemas
- API documentation
- Company policies
- Detailed workflow guides

### Assets (`assets/`)

**When to include:**
- Files used in output (not loaded into context)
- Templates to copy/modify

**Example use cases:**
- Brand logos
- PowerPoint templates
- HTML/React boilerplate
- Fonts

---

## Degrees of Freedom

Match specificity to task fragility:

### High Freedom (Text Instructions)

Use when:
- Multiple approaches are valid
- Decisions depend on context
- Heuristics guide the approach

```markdown
## Writing Style
Adapt tone to audience. Professional for B2B, casual for consumer apps.
```

### Medium Freedom (Pseudocode/Parameters)

Use when:
- A preferred pattern exists
- Some variation is acceptable
- Configuration affects behavior

```markdown
## API Response Format
Return JSON with structure:
{
  "status": "success|error",
  "data": <result or null>,
  "message": <human-readable description>
}
```

### Low Freedom (Specific Scripts)

Use when:
- Operations are fragile
- Consistency is critical
- Specific sequence required

```markdown
## PDF Rotation
ALWAYS use: `python scripts/rotate_pdf.py <file> <degrees>`
Do not attempt manual rotation.
```

---

## Progressive Disclosure

Three-level loading system:

| Level | What | When Loaded | Size Target |
|-------|------|-------------|-------------|
| 1 | name + description | Always | ~100 words |
| 2 | SKILL.md body | On trigger | <5k words |
| 3 | References/scripts | On demand | Unlimited |

### Pattern 1: High-level with References

```markdown
# PDF Processing

## Quick Start
Extract text: `pdfplumber.open(file).pages[0].extract_text()`

## Advanced
- **Forms**: See `references/forms.md`
- **API**: See `references/api.md`
```

### Pattern 2: Domain Organization

```
bigquery-skill/
├── SKILL.md (overview)
└── references/
    ├── finance.md
    ├── sales.md
    └── product.md
```

Claude loads only relevant domain file.

### Pattern 3: Variant Organization

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude loads only chosen provider.

---

## Description Writing

The description is the **primary trigger mechanism**. Claude uses it to decide when to load the skill.

### Good Description Template

```
[What it does]. Use when [specific trigger 1], [specific trigger 2], or [specific trigger 3]. Supports [capability list].
```

### Examples

**Bad:**
```
Helps with documents.
```

**Good:**
```
Comprehensive document creation, editing, and analysis with tracked changes and comments. Use when working with .docx files for: (1) Creating new documents, (2) Modifying content, (3) Working with tracked changes, or (4) Adding comments.
```

**Bad:**
```
PDF skill for various tasks.
```

**Good:**
```
PDF manipulation toolkit for text extraction, form filling, merging, and splitting. Use when processing PDF files, filling PDF forms, extracting tables from PDFs, or combining multiple PDFs.
```

### Description Checklist

- [ ] States what the skill does
- [ ] Lists specific triggers/scenarios
- [ ] Mentions file types if relevant
- [ ] Under 1024 characters
- [ ] No `<` or `>` characters

---

## Testing Strategy

### Before Packaging

1. **Script testing** - Run each script with sample inputs
2. **Trigger testing** - Verify description triggers correctly
3. **Workflow testing** - Walk through each documented workflow
4. **Edge case testing** - Test error scenarios

### Iteration Workflow

1. Use skill on real tasks
2. Notice struggles or inefficiencies
3. Identify needed updates
4. Implement changes
5. Retest

---

## Common Mistakes

### 1. Over-documenting

**Wrong:** Long explanations of basic concepts
**Right:** Concise instructions, examples over explanations

### 2. Poor Description

**Wrong:** "Helps with code"
**Right:** "Code review for Python with security and performance checks. Use for PR reviews, security audits, or performance analysis of .py files."

### 3. Duplicate Content

**Wrong:** Same info in SKILL.md and references/
**Right:** Core workflow in SKILL.md, details in references/

### 4. Unnecessary Files

**Wrong:** README.md, CHANGELOG.md, INSTALLATION.md
**Right:** Only SKILL.md and required resources

### 5. Hardcoded Paths

**Wrong:** `/Users/john/projects/...`
**Right:** Relative paths or user-provided paths

### 6. Untested Scripts

**Wrong:** Write and package without running
**Right:** Test with sample inputs, handle errors

### 7. Missing Triggers in Description

**Wrong:** Description only says what skill does
**Right:** Description says what AND when to use

---

## Quick Reference

### Frontmatter Template

```yaml
---
name: my-skill-name
description: [What it does]. Use when [trigger 1], [trigger 2], [trigger 3]. Supports [capabilities].
---
```

### Body Template

```markdown
# Skill Name

Brief overview (1-2 sentences).

## Quick Start
Essential workflow or command.

## Workflow
1. Step one
2. Step two
3. Step three

## References
- `references/detailed.md` - Extended documentation
```

### Validation Checklist

- [ ] name: hyphen-case, max 64 chars
- [ ] description: max 1024 chars, no `<>`, includes triggers
- [ ] SKILL.md: under 500 lines
- [ ] Scripts: tested and executable
- [ ] References: no duplication with SKILL.md
- [ ] No unnecessary files (README, CHANGELOG)
