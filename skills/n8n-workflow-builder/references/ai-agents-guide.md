# AI Agents Guide for n8n

Comprehensive guide for building AI agent workflows in n8n.

## Architecture Overview

AI workflows in n8n use a node chain architecture where:
1. **Trigger** starts the flow (Chat Trigger, Manual, Webhook)
2. **Language Model** provides AI capabilities
3. **AI Agent** orchestrates tool usage
4. **Tools** extend agent capabilities

```
┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ Chat Trigger│────▶│   AI Agent   │◀────│ LLM Node │
└─────────────┘     └──────────────┘     └──────────┘
                           ▲
                    ┌──────┴──────┐
                    │             │
              ┌─────┴─────┐ ┌─────┴─────┐
              │HTTP Tool  │ │Code Tool  │
              └───────────┘ └───────────┘
```

## Connection Types (CRITICAL)

AI connections flow **TO** the consumer node, not from.

| Type | From | To | Purpose |
|------|------|-----|---------|
| `ai_languageModel` | Language Model | AI Agent/Chain | **REQUIRED** - LLM provider |
| `ai_tool` | Tool Node | AI Agent | Capabilities |
| `ai_memory` | Memory Node | AI Agent | Conversation history |
| `ai_outputParser` | Parser | Chain | Structured output |
| `ai_retriever` | Retriever | Chain | RAG context |
| `ai_document` | Document Loader | Vector Store | Documents |
| `ai_embedding` | Embedding Model | Vector Store | Embeddings |
| `ai_vectorStore` | Vector Store | Retriever | Vector search |

### Connection Direction

```javascript
// CORRECT: Language Model connects TO AI Agent
{
  "connections": {
    "OpenAI Chat Model": {
      "ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]
    }
  }
}

// WRONG: Don't connect FROM AI Agent TO Language Model
```

## Minimal AI Agent Setup

### Required Nodes

1. **Trigger**: Chat Trigger or Manual Trigger
2. **Language Model**: OpenAI, Anthropic, or other
3. **AI Agent**: The orchestrator

### Minimal JSON

```json
{
  "name": "Minimal AI Agent",
  "nodes": [
    {
      "id": "chat-trigger",
      "name": "Chat Trigger",
      "type": "@n8n/n8n-nodes-langchain.chatTrigger",
      "typeVersion": 1.1,
      "position": [200, 300],
      "parameters": {}
    },
    {
      "id": "openai-model",
      "name": "OpenAI Chat Model",
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "typeVersion": 1.2,
      "position": [400, 400],
      "parameters": {
        "model": "gpt-4o-mini"
      },
      "credentials": {
        "openAiApi": {"id": "...", "name": "OpenAI"}
      }
    },
    {
      "id": "ai-agent",
      "name": "AI Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.7,
      "position": [400, 300],
      "parameters": {
        "options": {
          "systemMessage": "You are a helpful assistant."
        }
      }
    }
  ],
  "connections": {
    "Chat Trigger": {
      "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
    },
    "OpenAI Chat Model": {
      "ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]
    }
  }
}
```

## Adding Tools

Tools give the AI Agent capabilities to perform actions.

### Tool Types

| Tool | Use Case | Node Type |
|------|----------|-----------|
| HTTP Request | API calls | `@n8n/n8n-nodes-langchain.toolHttpRequest` |
| Code | Custom logic | `@n8n/n8n-nodes-langchain.toolCode` |
| Calculator | Math | `@n8n/n8n-nodes-langchain.toolCalculator` |
| Wikipedia | Knowledge | `@n8n/n8n-nodes-langchain.toolWikipedia` |
| Vector Store | RAG search | `@n8n/n8n-nodes-langchain.toolVectorStore` |
| Workflow | Call other workflow | `@n8n/n8n-nodes-langchain.toolWorkflow` |

### Tool Description Requirements

**CRITICAL**: Tool descriptions must be:
- Minimum 15 characters
- Clear about what the tool does
- Help the agent decide when to use it

```javascript
// GOOD
{
  "parameters": {
    "description": "Searches the product database for items matching the user's query"
  }
}

// BAD - too short
{
  "parameters": {
    "description": "Search"  // Will fail validation!
  }
}
```

### HTTP Request Tool

```json
{
  "name": "API Call Tool",
  "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
  "typeVersion": 1.1,
  "position": [600, 400],
  "parameters": {
    "description": "Calls the external API to fetch product information",
    "method": "GET",
    "url": "https://api.example.com/products",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth"
  }
}
```

Connect to AI Agent:
```json
{
  "API Call Tool": {
    "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
  }
}
```

### Code Tool

```json
{
  "name": "Data Processor",
  "type": "@n8n/n8n-nodes-langchain.toolCode",
  "typeVersion": 1.1,
  "position": [600, 500],
  "parameters": {
    "description": "Processes and transforms data based on user requirements",
    "code": "// Your JavaScript code here\nreturn { result: 'processed' };"
  }
}
```

## Memory (Conversation History)

Add memory to maintain conversation context.

### Buffer Memory (Simple)

```json
{
  "name": "Window Buffer Memory",
  "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
  "typeVersion": 1.3,
  "position": [200, 400],
  "parameters": {
    "contextWindowLength": 10
  }
}
```

Connect to AI Agent:
```json
{
  "Window Buffer Memory": {
    "ai_memory": [[{"node": "AI Agent", "type": "ai_memory", "index": 0}]]
  }
}
```

### Session-Based Memory

For multi-user scenarios:
```json
{
  "parameters": {
    "sessionIdType": "fromInput",
    "sessionKey": "={{ $json.sessionId }}"
  }
}
```

## RAG (Retrieval-Augmented Generation)

### Architecture

```
Documents → Document Loader → Vector Store ← Embedding Model
                                  ↓
                              Retriever
                                  ↓
                              AI Agent
```

### Vector Store Tool

```json
{
  "name": "Knowledge Search",
  "type": "@n8n/n8n-nodes-langchain.toolVectorStore",
  "typeVersion": 1,
  "parameters": {
    "description": "Searches company knowledge base for relevant information"
  }
}
```

Connect:
```json
{
  "Vector Store": {
    "ai_vectorStore": [[{"node": "Knowledge Search", "type": "ai_vectorStore", "index": 0}]]
  },
  "Knowledge Search": {
    "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
  }
}
```

## Streaming

Enable real-time response streaming.

### Chat Trigger with Streaming

```json
{
  "name": "Chat Trigger",
  "type": "@n8n/n8n-nodes-langchain.chatTrigger",
  "parameters": {
    "options": {
      "streaming": true
    }
  }
}
```

### Important Streaming Rules

1. **No main outputs from AI Agent** - responses go directly to trigger
2. Memory is handled automatically
3. Can't use post-processing nodes in streaming mode

## Advanced Patterns

### Multi-Agent System

```javascript
// Agent 1: Researcher
{
  "name": "Research Agent",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "options": {
      "systemMessage": "You are a research specialist. Find relevant information."
    }
  }
}

// Agent 2: Writer
{
  "name": "Writer Agent",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "options": {
      "systemMessage": "You are a content writer. Create content based on research."
    }
  }
}

// Connect sequentially
connections: {
  "Research Agent": {
    "main": [[{"node": "Writer Agent", "type": "main", "index": 0}]]
  }
}
```

### Fallback Model

Use a cheaper model with fallback to better model:

```json
{
  "name": "OpenAI Chat Model",
  "parameters": {
    "model": "gpt-4o-mini",
    "options": {
      "fallbackModel": "gpt-4o"
    }
  }
}
```

### Structured Output

Use output parser for structured responses:

```json
{
  "name": "Structured Output Parser",
  "type": "@n8n/n8n-nodes-langchain.outputParserStructured",
  "parameters": {
    "schema": {
      "type": "object",
      "properties": {
        "sentiment": {"type": "string"},
        "confidence": {"type": "number"}
      }
    }
  }
}
```

## Validation Checklist

### Before Building

- [ ] Language Model node added
- [ ] AI Agent node added
- [ ] Model connected to Agent (ai_languageModel)

### Tools

- [ ] Each tool has description (15+ characters)
- [ ] Tools connected to Agent (ai_tool)
- [ ] Tool credentials configured

### Memory (if needed)

- [ ] Memory node added
- [ ] Connected to Agent (ai_memory)
- [ ] Session handling configured for multi-user

### Streaming (if enabled)

- [ ] Chat Trigger streaming option enabled
- [ ] No main output connections from AI Agent
- [ ] Post-processing handled differently

### Final

- [ ] Run `validate_workflow` with strict profile
- [ ] Test with sample input
- [ ] Check for orphan nodes

## Common Issues

### "Language model not connected"
Ensure the connection goes FROM model TO agent:
```json
"OpenAI Chat Model": {
  "ai_languageModel": [[{"node": "AI Agent", ...}]]
}
```

### "Tool description too short"
Minimum 15 characters describing what the tool does.

### "Memory not persisting"
Check session ID configuration for multi-user scenarios.

### "Streaming not working"
Remove any main output connections from AI Agent.

## Node Types Reference

### Language Models
- `@n8n/n8n-nodes-langchain.lmChatOpenAi`
- `@n8n/n8n-nodes-langchain.lmChatAnthropic`
- `@n8n/n8n-nodes-langchain.lmChatGoogleGemini`
- `@n8n/n8n-nodes-langchain.lmChatOllama`

### Agents
- `@n8n/n8n-nodes-langchain.agent`
- `@n8n/n8n-nodes-langchain.chainRetrievalQa`

### Memory
- `@n8n/n8n-nodes-langchain.memoryBufferWindow`
- `@n8n/n8n-nodes-langchain.memoryPostgresChat`
- `@n8n/n8n-nodes-langchain.memoryRedisChat`

### Tools
- `@n8n/n8n-nodes-langchain.toolHttpRequest`
- `@n8n/n8n-nodes-langchain.toolCode`
- `@n8n/n8n-nodes-langchain.toolCalculator`
- `@n8n/n8n-nodes-langchain.toolVectorStore`
- `@n8n/n8n-nodes-langchain.toolWorkflow`

### Vector Stores
- `@n8n/n8n-nodes-langchain.vectorStorePinecone`
- `@n8n/n8n-nodes-langchain.vectorStoreSupabase`
- `@n8n/n8n-nodes-langchain.vectorStorePgVector`

### Embeddings
- `@n8n/n8n-nodes-langchain.embeddingsOpenAi`
- `@n8n/n8n-nodes-langchain.embeddingsCohere`
