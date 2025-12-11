# CopilotKit UI - AG-UI Frontend

A production-ready AI chat interface built with **CopilotKit** and **React**, connecting to a Pydantic AI backend via the AG-UI protocol.

## Overview

This frontend demonstrates the **native integration** between CopilotKit and the AG-UI protocol. CopilotKit is the official, production-ready frontend solution for AG-UI, built by the creators of the AG-UI protocol.

### Tech Stack

- **Frontend Framework:** React 19 + TypeScript
- **Build Tool:** Vite
- **UI Library:** CopilotKit (`@copilotkit/react-core` + `@copilotkit/react-ui`)
- **Protocol:** AG-UI (Server-Sent Events)
- **Backend:** Pydantic AI (AGUIApp on port 8000)

## Features

- ✅ **Zero Configuration** - Native AG-UI support, just point to backend URL
- ✅ **Streaming Responses** - Real-time streaming of AI responses
- ✅ **Tool Call Visualization** - See weather lookups and MCP calls in action
- ✅ **Production-Ready** - Battle-tested components from CopilotKit
- ✅ **Auto-Handles** - SSE connection, message state, error handling

## Quick Start

### Prerequisites

- Node.js 18+ and pnpm installed
- Backend running at `http://localhost:8000` (see `../api/README.md`)

### Installation

```bash
# Install dependencies
pnpm install
```

### Running

```bash
# Start development server
pnpm dev
```

The UI will be available at `http://localhost:5173`

### Building for Production

```bash
# Build for production
pnpm build

# Preview production build
pnpm preview
```

## Architecture

### Connection Flow

```
User Input
    ↓
CopilotKit Component
    ↓
HTTP POST → http://localhost:8000
    ↓
AGUIApp (Pydantic AI)
    ↓
SSE Stream ← AG-UI Events
    ↓
CopilotKit (auto-handles)
    ↓
UI Update (streaming)
```

### AG-UI Protocol

The backend streams these events over SSE:

- `text` - Streaming text chunks from Claude
- `tool_call` - Weather or MCP server invocation
- `tool_result` - Tool execution results
- `complete` - Stream finished
- `error` - Error occurred

CopilotKit automatically handles all these events and updates the UI accordingly.

## Key Files

```
src/
├── App.tsx          # CopilotKit integration
├── App.css          # Layout styles
├── index.css        # Global styles
└── main.tsx         # React entry point
```

## Configuration

### Backend URL

The backend URL is configured in `src/App.tsx`:

```typescript
<CopilotKit runtimeUrl="http://localhost:8000">
```

To use a different backend:
1. Update the `runtimeUrl` prop in `App.tsx`
2. Ensure the backend implements the AG-UI protocol

### Vite Configuration

`vite.config.ts` enables CORS for the backend connection:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    cors: true,
  },
});
```

## Available Tools

The AI assistant has access to:

1. **Weather Tool** - Get weather for any location (via wttr.in)
   ```
   Try: "What's the weather in Tokyo?"
   ```

2. **Context7 MCP** - Up-to-date code documentation (free tier)
   ```
   Try: "How do React hooks work?"
   ```

3. **E-gineering MCP** - Additional capabilities (if configured)

## Customization

### Labels

Customize chat labels in `App.tsx`:

```typescript
<CopilotChat
  labels={{
    title: "Your Custom Title",
    initial: "Your welcome message here",
  }}
/>
```

### Styling

CopilotKit provides default styles via `@copilotkit/react-ui/styles.css`. Override them in `App.css` or `index.css`.

## Testing the Integration

1. **Start the backend:**
   ```bash
   cd ../api
   uv run agent.py
   ```

2. **Start this frontend:**
   ```bash
   pnpm dev
   ```

3. **Test queries:**
   - "What's the weather in Paris?"
   - "How does async/await work in JavaScript?"
   - "Tell me about the Claude API"

You should see:
- Streaming text responses
- Tool call indicators when weather or MCP is used
- Complete responses with context from external tools

## Comparison: CopilotKit vs assistant-ui

| Feature | CopilotKit (this UI) | assistant-ui |
|---------|---------------------|--------------|
| AG-UI Support | ✅ Native | ⚠️ Custom adapter required |
| Setup Complexity | ⭐ Simple | ⭐⭐⭐ Advanced |
| Configuration | Zero config | Manual adapter coding |
| Best For | Quick setup, production use | Custom requirements |

For the assistant-ui implementation, see `../ui-assistant/` (if implemented).

## Troubleshooting

### Backend Connection Failed

**Error:** "Failed to fetch" or CORS errors

**Solution:**
1. Ensure backend is running: `cd ../api && uv run agent.py`
2. Verify backend is on port 8000
3. Check CORS is enabled in Vite config

### No Streaming

**Error:** Messages don't stream, appear all at once

**Solution:**
1. Check backend is using AGUIApp (not plain Agent)
2. Verify SSE is working: `curl -N http://localhost:8000`
3. Check browser DevTools → Network tab for SSE connection

### Tool Calls Not Working

**Error:** Weather or MCP queries fail

**Solution:**
1. Check backend logs for tool errors
2. Verify ANTHROPIC_API_KEY is set in backend `.env`
3. For Context7: Optional key, works on free tier
4. For E-gineering: Requires MCP_OAUTH_TOKEN

## Resources

- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [CopilotKit GitHub](https://github.com/CopilotKit/CopilotKit)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [Pydantic AI Docs](https://ai.pydantic.dev/)
- [Backend README](../api/README.md)

## License

Part of the AG-UI + assistant-ui tech radar demonstration project.
