# Validation Checklist

Pre-deployment validation for n8n workflows.

## MCP Tool Validation

### Validate Single Node

```javascript
validate_node({
  nodeType: "nodes-base.slack",
  config: {
    resource: "message",
    operation: "post",
    channel: "#general",
    text: "Hello"
  },
  mode: "full",
  profile: "strict"
})
```

### Validate Full Workflow

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

---

## Pre-Build Checklist

### Discovery Phase
- [ ] Used `search_nodes` to find correct node type
- [ ] Used `get_node` to understand configuration
- [ ] Checked template examples with `search_templates`

### Node Selection
- [ ] Node type is correct (check with `search_nodes`)
- [ ] Node version is current
- [ ] Credentials type matches requirements

---

## Node-Level Validation

### Required Fields
- [ ] `id` - Unique identifier
- [ ] `name` - Descriptive name
- [ ] `type` - Valid node type
- [ ] `typeVersion` - Current version
- [ ] `position` - [x, y] coordinates
- [ ] `parameters` - Required parameters filled

### Credentials
- [ ] Credentials referenced (not hardcoded)
- [ ] Credential type matches node requirement
- [ ] Credentials exist in n8n instance

### Parameters
- [ ] All required parameters populated
- [ ] Parameter types correct (string, number, boolean)
- [ ] Expressions valid (if using `={{ }}`)
- [ ] URLs valid format
- [ ] Enum values from allowed list

---

## Workflow-Level Validation

### Structure
- [ ] `name` is set
- [ ] `nodes` array is not empty
- [ ] `connections` object exists
- [ ] `settings.executionOrder` is "v1"

### Connections
- [ ] All nodes connected (no orphans)
- [ ] Connections reference valid node names
- [ ] Connection types correct (main, ai_languageModel, ai_tool, etc.)
- [ ] No circular references

### Triggers
- [ ] At least one trigger node exists
- [ ] Webhook paths are unique
- [ ] Schedule triggers have valid cron expressions

### Error Handling
- [ ] Error Trigger node present (recommended)
- [ ] Error handling branch exists
- [ ] Stop and Error node for validation failures

---

## AI Workflow Validation

### Required Connections
- [ ] Language Model node exists
- [ ] AI Agent/Chain node exists
- [ ] Language Model → AI Agent connection (ai_languageModel type)

### Tool Requirements
- [ ] Each tool has description (minimum 15 characters)
- [ ] Tool descriptions clearly explain purpose
- [ ] Tools connected with ai_tool type

### Memory (if used)
- [ ] Memory node configured
- [ ] Connected with ai_memory type
- [ ] Session handling for multi-user (if applicable)

### Streaming (if enabled)
- [ ] Chat Trigger has streaming enabled
- [ ] No main output connections from AI Agent
- [ ] Response handled by trigger

---

## Expression Validation

### Syntax
- [ ] Expressions start with `={{ ` and end with ` }}`
- [ ] No unescaped special characters
- [ ] Variable paths valid (`$json.field`, `$input.first()`)

### Common Patterns
```javascript
// Valid
={{ $json.name }}
={{ $input.first().json.email }}
={{ $('Previous Node').first().json.data }}
={{ $env.API_KEY }}

// Invalid
={{ $json.name }  // Missing closing brace
={{ $json name }} // Space in path
{{ $json.name }}  // Missing =
```

### Data References
- [ ] Referenced fields exist in input
- [ ] Node names in `$('NodeName')` are correct
- [ ] Environment variables exist

---

## Security Checklist

### Credentials
- [ ] No hardcoded API keys
- [ ] No hardcoded passwords
- [ ] Using n8n credentials system

### Webhooks
- [ ] Authentication configured (if public)
- [ ] Response doesn't leak sensitive data
- [ ] Rate limiting considered

### Data Handling
- [ ] PII handled appropriately
- [ ] Sensitive data not logged
- [ ] HTTPS for all external requests

---

## Performance Checklist

### Efficiency
- [ ] Batch processing for large datasets
- [ ] Pagination for API calls
- [ ] No unnecessary loops

### Timeouts
- [ ] HTTP request timeouts set
- [ ] Long-running operations have limits
- [ ] Wait nodes have reasonable durations

### Error Recovery
- [ ] Retry logic for transient failures
- [ ] Graceful degradation
- [ ] Error notifications configured

---

## Pre-Deployment Final Check

### Testing
- [ ] Tested with sample data
- [ ] Edge cases handled
- [ ] Error paths tested

### Documentation
- [ ] Workflow description filled
- [ ] Node names are descriptive
- [ ] Complex logic commented

### Environment
- [ ] All credentials configured in target
- [ ] Environment variables set
- [ ] Webhook URLs accessible

---

## Validation Profiles

| Profile | Use Case | Strictness |
|---------|----------|------------|
| `minimal` | Quick check | Required fields only |
| `runtime` | Pre-deploy | Runtime errors |
| `ai-friendly` | AI building | Balanced (recommended) |
| `strict` | Production | All checks |

### Recommended Usage

```javascript
// During development
validate_node({..., mode: "full", profile: "ai-friendly"})

// Before production
validate_workflow({..., options: {profile: "strict"}})
```

---

## Common Validation Errors

### "Node not connected"
- Ensure node appears in connections object
- Check node name matches exactly (case-sensitive)

### "Invalid expression"
- Check syntax: `={{ expression }}`
- Verify field paths exist
- Use proper escaping for special chars

### "Missing required parameter"
- Run `get_node` to see required fields
- Check parameter names match schema

### "Credential not found"
- Verify credential exists in n8n
- Check credential type matches node

### "Tool description too short"
- AI tools need 15+ character descriptions
- Make description helpful for agent decision

### "Language model not connected"
- AI connection goes FROM model TO agent
- Use `ai_languageModel` connection type
