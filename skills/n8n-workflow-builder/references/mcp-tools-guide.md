# n8n MCP Tools Guide

Complete reference for all 19 n8n MCP tools available.

## Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| Discovery | `search_nodes`, `search_templates`, `get_template` | Find nodes and templates |
| Configuration | `get_node` | Understand node configuration |
| Validation | `validate_node`, `validate_workflow` | Verify before deploy |
| API Management | 13 tools | Create, update, deploy, test workflows |

---

## Discovery Tools

### search_nodes

Find n8n nodes by keyword.

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| query | string | required | Search terms |
| mode | string | "OR" | "OR", "AND", or "FUZZY" |
| limit | number | 20 | Max results |
| includeExamples | boolean | false | Include template examples |

**Examples:**
```javascript
// Basic search
search_nodes({query: "slack"})

// Require all words
search_nodes({query: "http request", mode: "AND"})

// Typo-tolerant
search_nodes({query: "webhok", mode: "FUZZY"})

// With real examples from templates
search_nodes({query: "webhook", includeExamples: true})
```

**When to use:**
- "What node do I need for X?"
- "Is there a node for Y service?"
- Starting a new workflow

---

### search_templates

Find workflow templates.

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| searchMode | string | "keyword", "by_nodes", "by_task", "by_metadata" |
| query | string | For keyword search |
| nodeTypes | array | For by_nodes search |
| task | string | For by_task search |
| complexity | string | "simple", "medium", "complex" |
| maxSetupMinutes | number | Max setup time |
| limit | number | Max results (default 20) |

**Task Types:**
- `ai_automation`
- `data_sync`
- `webhook_processing`
- `email_automation`
- `slack_integration`
- `data_transformation`
- `file_processing`
- `scheduling`
- `api_integration`
- `database_operations`

**Examples:**
```javascript
// By task type
search_templates({searchMode: "by_task", task: "ai_automation"})

// By nodes used
search_templates({
  searchMode: "by_nodes",
  nodeTypes: ["n8n-nodes-base.slack", "n8n-nodes-base.webhook"]
})

// Simple workflows under 15 min setup
search_templates({
  searchMode: "by_metadata",
  complexity: "simple",
  maxSetupMinutes: 15
})

// Keyword search
search_templates({query: "lead capture crm"})
```

**When to use:**
- "Show me examples of X"
- "How do others do Y?"
- Learning new patterns

---

### get_template

Retrieve a specific template.

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| templateId | number | Template ID |
| mode | string | "nodes_only", "structure", "full" |

**Examples:**
```javascript
// Full workflow JSON
get_template({templateId: 123, mode: "full"})

// Just node list
get_template({templateId: 123, mode: "nodes_only"})

// Nodes + connections
get_template({templateId: 123, mode: "structure"})
```

---

## Configuration Tools

### get_node

Get node information and documentation. The most versatile tool.

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| nodeType | string | required | e.g., "nodes-base.httpRequest" |
| detail | string | "standard" | "minimal", "standard", "full" |
| mode | string | "info" | "info", "docs", "search_properties", "versions", "compare", "breaking", "migrations" |
| includeExamples | boolean | false | Real-world examples |
| includeTypeInfo | boolean | false | Type metadata |
| propertyQuery | string | - | For search_properties mode |
| fromVersion | string | - | For compare/breaking modes |
| toVersion | string | - | For compare mode |

**Detail Levels:**
- `minimal` (~200 tokens): Quick reference
- `standard` (~1-2K tokens): **Recommended** - essential properties
- `full` (~3-8K tokens): Complete schema

**Modes:**
- `info`: Node schema (default)
- `docs`: Readable markdown documentation
- `search_properties`: Find specific properties
- `versions`: Version history
- `compare`: Compare versions
- `breaking`: Breaking changes
- `migrations`: Migration guide

**Examples:**
```javascript
// Standard configuration (START HERE)
get_node({nodeType: "nodes-base.httpRequest", detail: "standard"})

// With examples from real templates
get_node({
  nodeType: "nodes-base.slack",
  detail: "standard",
  includeExamples: true
})

// Documentation
get_node({nodeType: "nodes-base.webhook", mode: "docs"})

// Find auth properties
get_node({
  nodeType: "nodes-base.httpRequest",
  mode: "search_properties",
  propertyQuery: "auth"
})

// Compare versions
get_node({
  nodeType: "nodes-base.httpRequest",
  mode: "compare",
  fromVersion: "1.0",
  toVersion: "2.0"
})
```

**Recommended Workflow:**
1. Start with `detail: "standard"`
2. Add `includeExamples: true` for patterns
3. Use `mode: "search_properties"` for specific fields
4. Use `mode: "docs"` for readable documentation

---

## Validation Tools

### validate_node

Validate a node configuration before building.

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| nodeType | string | required | Node type |
| config | object | required | Node parameters |
| mode | string | "full" | "full" or "minimal" |
| profile | string | "ai-friendly" | "minimal", "runtime", "ai-friendly", "strict" |

**Profiles:**
- `minimal`: Basic checks only
- `runtime`: Checks that would fail at runtime
- `ai-friendly`: **Recommended** - balanced for AI usage
- `strict`: All checks including style

**Examples:**
```javascript
// Full validation
validate_node({
  nodeType: "nodes-base.slack",
  config: {
    resource: "channel",
    operation: "create",
    name: "general"
  },
  mode: "full",
  profile: "strict"
})

// Quick check
validate_node({
  nodeType: "nodes-base.httpRequest",
  config: {method: "POST", url: "https://api.example.com"},
  mode: "minimal"
})
```

**Response includes:**
- `valid`: boolean
- `errors`: Critical issues
- `warnings`: Potential problems
- `suggestions`: Improvements

---

### validate_workflow

Validate a complete workflow.

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| workflow | object | required | Complete workflow JSON |
| options.validateNodes | boolean | true | Check node configs |
| options.validateConnections | boolean | true | Check flow |
| options.validateExpressions | boolean | true | Check n8n expressions |
| options.profile | string | "runtime" | Validation strictness |

**Examples:**
```javascript
validate_workflow({
  workflow: {
    name: "My Workflow",
    nodes: [...],
    connections: {...}
  },
  options: {
    validateNodes: true,
    validateConnections: true,
    validateExpressions: true,
    profile: "strict"
  }
})
```

**Checks:**
- Node configuration validity
- Connection integrity (no orphans)
- Expression syntax
- AI tool requirements
- Required fields

---

## API Management Tools

These require n8n API configuration (`N8N_API_URL`, `N8N_API_KEY`).

### Workflow Management

#### n8n_create_workflow
Create a new workflow.
```javascript
n8n_create_workflow({
  name: "My Workflow",
  nodes: [...],
  connections: {...},
  settings: {executionOrder: "v1"}
})
```

#### n8n_get_workflow
Get workflow details.
```javascript
// Full workflow
n8n_get_workflow({id: "workflow-id", mode: "full"})

// Just structure
n8n_get_workflow({id: "workflow-id", mode: "structure"})
```

#### n8n_update_partial_workflow
Incremental updates (preferred over full replacement).
```javascript
n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [
    {op: "add", path: "/nodes/-", value: newNode},
    {op: "replace", path: "/nodes/0/parameters/url", value: "new-url"}
  ]
})
```

#### n8n_update_full_workflow
Replace entire workflow.
```javascript
n8n_update_full_workflow({
  id: "workflow-id",
  workflow: {...completeWorkflow}
})
```

#### n8n_delete_workflow
Delete a workflow.
```javascript
n8n_delete_workflow({id: "workflow-id"})
```

#### n8n_list_workflows
List all workflows.
```javascript
n8n_list_workflows({active: true, limit: 50})
```

#### n8n_workflow_versions
Version history and rollback.
```javascript
n8n_workflow_versions({id: "workflow-id", action: "list"})
n8n_workflow_versions({id: "workflow-id", action: "rollback", version: 3})
```

### Execution & Testing

#### n8n_test_workflow
Test a workflow.
```javascript
// Trigger webhook
n8n_test_workflow({
  id: "workflow-id",
  mode: "webhook",
  data: {test: "payload"}
})

// Direct execute
n8n_test_workflow({
  id: "workflow-id",
  mode: "execute"
})
```

#### n8n_executions
Manage executions.
```javascript
// List recent
n8n_executions({action: "list", workflowId: "...", limit: 10})

// Get specific
n8n_executions({action: "get", executionId: "..."})

// Delete
n8n_executions({action: "delete", executionId: "..."})
```

### Deployment

#### n8n_deploy_template
Deploy a template directly.
```javascript
n8n_deploy_template({
  templateId: 123,
  name: "My Deployed Workflow",
  activate: true
})
```

#### n8n_autofix_workflow
Auto-fix common issues.
```javascript
n8n_autofix_workflow({id: "workflow-id"})
```

#### n8n_validate_workflow (API version)
Validate by workflow ID.
```javascript
n8n_validate_workflow({id: "workflow-id"})
```

### System

#### n8n_health_check
Check API connectivity.
```javascript
n8n_health_check()
```

---

## Performance Reference

| Tool | Speed | Tokens |
|------|-------|--------|
| search_nodes | <10ms | ~500 |
| get_node (minimal) | <10ms | ~200 |
| get_node (standard) | <10ms | ~1-2K |
| get_node (full) | <100ms | ~3-8K |
| validate_node | <100ms | ~500 |
| validate_workflow | 100-500ms | ~1K |
| n8n_* API tools | Variable | Network-dependent |

---

## Common Workflows

### Building a New Node
```javascript
// 1. Find the node
search_nodes({query: "slack"})

// 2. Get configuration
get_node({nodeType: "nodes-base.slack", detail: "standard", includeExamples: true})

// 3. Validate your config
validate_node({nodeType: "nodes-base.slack", config: {...}, mode: "full"})
```

### Finding Examples
```javascript
// 1. Search templates by task
search_templates({searchMode: "by_task", task: "webhook_processing"})

// 2. Get specific template
get_template({templateId: 123, mode: "full"})
```

### Deploying a Workflow
```javascript
// 1. Validate first
validate_workflow({workflow: myWorkflow, options: {profile: "strict"}})

// 2. Create or update
n8n_create_workflow({...myWorkflow})
// OR
n8n_update_partial_workflow({id: "...", operations: [...]})

// 3. Test
n8n_test_workflow({id: "...", mode: "execute"})
```
