---
name: mcp-builder
description: Build MCP (Model Context Protocol) servers with tools, resources, and prompts
---

# MCP Builder Skill

Build Model Context Protocol (MCP) servers that extend LLM capabilities with custom tools, resources, and prompts.

## What is MCP?

MCP is a protocol for connecting LLMs to external data and tools. An MCP server exposes:
- **Tools**: Functions the LLM can call (like API calls, computations)
- **Resources**: Data the LLM can read (files, DB records, API responses)
- **Prompts**: Reusable prompt templates

## Project Structure

```
my-mcp-server/
├── src/
│   └── index.ts          # server entry point
├── package.json
├── tsconfig.json
└── README.md
```

## Step-by-Step: Build an MCP Server

### 1. Initialize Project

```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node
```

### 2. Define the Server

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-server",
  version: "1.0.0",
});
```

### 3. Add Tools

Tools let the LLM take actions:

```typescript
server.tool(
  "fetch_weather",                          // tool name
  "Get weather for a city",                // description
  { city: z.string() },                    // input schema (Zod)
  async ({ city }) => {                    // handler
    const data = await fetch(`https://api.weather.com/${city}`);
    return {
      content: [{ type: "text", text: JSON.stringify(data) }],
    };
  }
);
```

Tool design rules:
- **Clear name**: verb_noun format (e.g., `search_files`, `create_issue`)
- **Helpful description**: what it does, when to use it
- **Strict schema**: use Zod for input validation
- **Error handling**: return errors as content, don't throw

### 4. Add Resources

Resources expose data the LLM can read:

```typescript
server.resource(
  "config",                                 // resource name
  "config://app",                           // URI pattern
  async (uri) => ({
    contents: [{
      uri: uri.href,
      mimeType: "application/json",
      text: JSON.stringify({ theme: "dark", lang: "en" }),
    }],
  })
);
```

### 5. Add Prompts

Reusable prompt templates:

```typescript
server.prompt(
  "code_review",                            // prompt name
  "Review code for issues",                // description
  { code: z.string() },                    // arguments
  ({ code }) => ({
    messages: [{
      role: "user",
      content: { type: "text", text: `Review this code:\n\n${code}` },
    }],
  })
);
```

### 6. Start the Server

```typescript
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP server running on stdio");
}

main().catch(console.error);
```

### 7. Configure in Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["dist/index.js"]
    }
  }
}
```

## Common Patterns

### Database Access Tool
```typescript
server.tool("query_db", "Execute read-only SQL query",
  { sql: z.string() },
  async ({ sql }) => {
    // validate: only SELECT statements
    if (!sql.trim().toUpperCase().startsWith("SELECT")) {
      return { content: [{ type: "text", text: "Error: only SELECT allowed" }] };
    }
    const rows = await db.query(sql);
    return { content: [{ type: "text", text: JSON.stringify(rows) }] };
  }
);
```

### File Search Tool
```typescript
server.tool("search_files", "Search files by pattern",
  { pattern: z.string(), directory: z.string().optional() },
  async ({ pattern, directory }) => {
    const { execSync } = require("child_process");
    const dir = directory || ".";
    const result = execSync(`grep -r "${pattern}" ${dir}`).toString();
    return { content: [{ type: "text", text: result }] };
  }
);
```

## Testing Checklist

- [ ] Server starts without errors
- [ ] Each tool returns valid content
- [ ] Input validation works (bad inputs rejected)
- [ ] Errors are returned as content, not thrown
- [ ] Resources return correct MIME types
- [ ] Prompts produce expected messages

## Key Principles

1. **Minimal scope**: Each server does one thing well
2. **Safe defaults**: Read-only unless explicitly destructive
3. **Clear errors**: Always return human-readable error messages
4. **Input validation**: Validate everything with Zod schemas
5. **Idempotency**: Tools should be safe to retry
