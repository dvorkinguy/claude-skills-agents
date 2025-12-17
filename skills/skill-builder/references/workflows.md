# Workflow Patterns

## Sequential Workflows

For complex tasks, break into clear steps:

```markdown
## PDF Form Filling

1. Analyze form → `scripts/analyze_form.py`
2. Create field mapping → edit `fields.json`
3. Validate mapping → `scripts/validate.py`
4. Fill form → `scripts/fill_form.py`
5. Verify output → `scripts/verify.py`
```

## Conditional Workflows

For branching logic:

```markdown
## Workflow

1. Determine type:
   **Creating new?** → See "Creation" below
   **Editing existing?** → See "Editing" below

### Creation
1. Initialize template
2. Add content
3. Export

### Editing
1. Load file
2. Parse structure
3. Apply changes
4. Save
```

## Decision Trees

For complex decisions:

```markdown
## File Type Decision

Is it a spreadsheet?
├── Yes → Use xlsx skill
└── No → Is it a document?
    ├── Yes → Use docx skill
    └── No → Is it a presentation?
        ├── Yes → Use pptx skill
        └── No → Handle as text
```

## Error Recovery

Include fallback paths:

```markdown
## Processing

1. Try primary method
2. If fails:
   - Log error
   - Try fallback method
3. If still fails:
   - Notify user
   - Provide manual steps
```
