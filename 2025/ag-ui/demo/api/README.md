# Pydantic AI Agent with AG-UI

A complete AI agent implementation using Pydantic AI, Claude 4.5, and the AG-UI protocol for streaming responses to frontends.

## Features

- **Anthropic Claude 4.5** - Latest Claude Sonnet model
- **Weather Tool** - Fetch weather data from wttr.in for any location
- **Context7 MCP Server** - Up-to-date code documentation and context
- **E-gineering MCP Server** - Additional MCP capabilities with OAuth
- **AG-UI Protocol** - Stream responses to React/TypeScript frontends
- **Logfire Observability** - Built-in tracing and monitoring
- **PEP 723** - Single-file script with inline dependencies

## Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your credentials:**
   ```env
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   CONTEXT7_API_KEY=your_context7_key_here
   MCP_OAUTH_TOKEN=your_oauth_token_here
   LOGFIRE_TOKEN=your_logfire_token_here
   ```

3. **Run the agent:**
   ```bash
   uv run agent.py
   ```

The server will start on `http://localhost:8000`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key from https://console.anthropic.com/ |
| `CONTEXT7_API_KEY` | No | Context7 API key (works on free tier without key) |
| `MCP_OAUTH_TOKEN` | No | OAuth token for mcp.e-gineering.com/mcp |
| `LOGFIRE_TOKEN` | No | Logfire token for observability (optional) |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 8000) |

## Available Tools

### 1. Weather Tool (`get_weather`)
Fetches current weather information for any location using wttr.in.

**Example:** "What's the weather in Paris?"

### 2. Context7 MCP Server (`context7`)
Provides up-to-date code documentation and context from the Context7 service.

**Features:**
- Code documentation lookup
- Context-aware code explanations
- Repository insights

**Note:** Works on free tier without an API key! Add `CONTEXT7_API_KEY` for higher rate limits.

### 3. E-gineering MCP Server (`eg_mcp`)
Connects to the E-gineering MCP server for additional capabilities.

**Note:** Requires `MCP_OAUTH_TOKEN` to be set.

## MCP Server Authentication

**Important:** Pydantic AI's `MCPServerTool` currently only supports **static token authentication**. Dynamic Client Registration (DCR) is not yet supported.

### Context7 Setup

**Good news:** Context7 works out of the box without an API key on the free tier!

For higher rate limits (optional):
1. Create an account at https://context7.com/dashboard
2. Generate an API key
3. Add it to your `.env` file as `CONTEXT7_API_KEY`

### E-gineering MCP Setup
1. Obtain an OAuth token for mcp.e-gineering.com/mcp
2. Add it to your `.env` file as `MCP_OAUTH_TOKEN`
3. The E-gineering tool will automatically be enabled

Both MCP servers are optional. The agent will work with just the weather tool if no MCP tokens are provided.

## Observability with Logfire

The agent is instrumented with Logfire for comprehensive observability:
- Trace all LLM calls
- Monitor tool invocations
- Track errors and performance
- View spans in the Logfire dashboard

To enable Logfire:
1. Sign up at https://logfire.pydantic.dev/
2. Add your `LOGFIRE_TOKEN` to `.env`
3. View traces in your Logfire dashboard

## Frontend Integration

This agent uses the AG-UI protocol, which means you can connect it to frontends using:

- **CopilotKit** (React/Next.js)
- **@ag-ui/client** (TypeScript)
- Any HTTP client supporting Server-Sent Events (SSE)

### Example Frontend Connection

```typescript
import { HttpAgent } from "@ag-ui/client";

const agent = new HttpAgent({
  url: "http://localhost:8000"
});

// Use with CopilotKit
<CopilotKit runtimeUrl="http://localhost:8000">
  {/* Your app */}
</CopilotKit>
```

## Development

The script is a single PEP 723 file with inline dependencies. This means:
- No separate `requirements.txt` needed
- `uv` automatically manages dependencies
- Easy to share and run

### Dependencies

```toml
pydantic-ai[anthropic,logfire]>=0.0.1
pydantic-ai-ui[ag-ui]>=0.0.1
httpx>=0.27.0
uvicorn>=0.30.0
python-dotenv>=1.0.0
```

## Testing

Test the weather tool:
```bash
# Start the server in one terminal
uv run agent.py

# In another terminal, use the AG-UI endpoint
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What'\''s the weather in Tokyo?"}]}'
```

## Architecture

```
┌─────────────┐
│  Frontend   │  React/TypeScript with AG-UI client
│  (AG-UI)    │
└──────┬──────┘
       │ HTTP/SSE
       ▼
┌─────────────┐
│   AGUIApp   │  Pydantic AI AG-UI adapter
│  (FastAPI)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Agent    │  Claude 4.5 with tools
│  (Pydantic  │  - get_weather
│     AI)     │  - context7 (if token set)
└──────┬──────┘  - eg_mcp (if token set)
       │
       ├─────► wttr.in (weather)
       │
       ├─────► mcp.context7.com/mcp (code docs)
       │
       └─────► mcp.e-gineering.com/mcp
```

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"
Add your Anthropic API key to the `.env` file.

### "Optional MCP servers not configured"
This is just a warning. The agent will work without MCP tools if no tokens are provided. You can add Context7 and/or E-gineering MCP tokens at any time.

### Logfire not logging
Make sure `LOGFIRE_TOKEN` is set in your `.env` file, or omit it to skip observability.

## Resources

- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [Context7 MCP Server](https://github.com/upstash/context7)
- [Logfire Observability](https://logfire.pydantic.dev/)
- [wttr.in Weather API](https://wttr.in/)

## References

Based on Context7 MCP server documentation:
- [Context7 GitHub Repository](https://github.com/upstash/context7)
- [Context7 API Guide](https://context7.com/docs/api-guide)
- [Context7 on MCP Servers](https://mcpservers.org/servers/lrstanley/context7-http)
