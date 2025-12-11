# Pydantic AI Agent with AG-UI

A complete AI agent implementation using Pydantic AI, Claude 4.5, and the AG-UI protocol for streaming responses to frontends.

## Features

- **Anthropic Claude 4.5** - Latest Claude Sonnet model
- **Weather Tool** - Fetch weather data from wttr.in for any location
- **Context7 MCP Server** - Up-to-date code documentation (free tier)
- **AG-UI Protocol** - Stream responses to React/TypeScript frontends
- **Logfire Observability** - Built-in tracing and monitoring
- **PEP 723** - Single-file script with inline dependencies

## Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key:**
   ```env
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   LOGFIRE_TOKEN=your_logfire_token_here  # optional
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

**Note:** Uses free tier - no API key required!

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
│     AI)     │  - context7 (free tier)
└──────┬──────┘
       │
       ├─────► wttr.in (weather)
       │
       └─────► mcp.context7.com/mcp (code docs)
```

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"
Add your Anthropic API key to the `.env` file.

### "Optional MCP servers not configured"
Context7 MCP works on the free tier without requiring any tokens.

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
