## Setting Up a Pydantic AI Assistant UI with AG-UI Integration

In this guide, we will walk through configuring a **Pydantic AI** agent and integrating it with the **AG-UI** (Agent-User Interaction) protocol. This will enable a rich Assistant UI that can use tools like a weather service (via WTTR.in) and connect to an internal **MCP** (Model Context Protocol) server. We’ll cover setting up the agent with Anthropic’s Claude model, adding the weather lookup tool, attaching an MCP server tool (with OAuth), and launching the AG-UI backend to communicate with a React/TypeScript frontend.

### Overview and Prerequisites

Before diving in, ensure you have the following:

- **Pydantic AI** library installed (with AG-UI support) and a Python environment ready.
- An API key for your model provider (e.g. an **Anthropic** API key if using Claude). Set it as an environment variable (e.g. ANTHROPIC\_API\_KEY) so Pydantic AI can pick it up [[1]](https:/ai.pydantic.dev/models/anthropic/#:~:text=Environment%20variable) [[2]](https:/ai.pydantic.dev/models/anthropic/#:~:text=agent%20%3D%20Agent%28%27gateway%2Fanthropic%3Aclaude) .
- (Optional) Credentials or tokens for your internal MCP server (if it requires OAuth or API keys).
- A frontend environment (e.g. created with Vite + React + TypeScript) ready to integrate the AG-UI client library.

**Note:** AG-UI is a protocol that streams structured JSON events (like messages, tool calls, state updates) over HTTP to synchronize the AI agent with a frontend UI [[3]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=different%20kinds%20of%20events,a%20simple%20rundown) [[4]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,tool%27s%20done%2C%20here%27s%20the%20result) . Pydantic AI’s integration with AG-UI will let us easily stream the agent’s responses and tool usage events to the frontend.

### Defining the Pydantic AI Agent and Tools

First, set up the Pydantic AI agent with the desired model and integrate the necessary tools. In our example, we’ll use Anthropic’s Claude model (Claude 4.5). We’ll attach two tools to the agent:

1. **MCP Server Tool:** This built-in tool allows the agent to query a remote MCP server (e.g. an internal knowledge base or data service) via the model’s context window [[5]](https:/ai.pydantic.dev/builtin-tools/#:~:text=MCP%20Server%20Tool) . We configure it with the server’s URL and any required auth tokens.
2. **Weather Lookup Tool:** A custom tool (function) that fetches weather info from WTTR.in for a given location.

Below is a Python code snippet illustrating the setup:

from pydantic\_ai import Agent, MCPServerTool
from pydantic\_ai.ui.ag\_ui.app import AGUIApp
import httpx  # we'll use httpx for async HTTP calls in the tool

# Initialize the agent with Anthropic Claude 4.5 model (ensure API key is set in env)
agent = Agent(
    "anthropic:claude-sonnet-4-5",  # Claude 4.5 model (sonnet version)
    instructions="You are a helpful assistant.",  # optional system prompt/instructions
    builtin\_tools=[
        # Attach an MCP server tool for the internal server
        MCPServerTool(
            id="internal\_mcp", 
            url="https://api.myinternalmcp.com/mcp",   # Your MCP server endpoint
            authorization\_token="YOUR\_OAUTH\_TOKEN\_HERE",  # OAuth token for MCP (if required)
            allowed\_tools=["*"],  # e.g. list specific tool names or "*" for all
            description="Internal knowledge base MCP server",
            headers={"Authorization": "Bearer YOUR\_OAUTH\_TOKEN\_HERE"}  # any custom headers if needed
        )
    ]
)

# Define a custom tool to get weather from WTTR.in
@agent.tool\_plain
async def get\_weather(location: str) -&gt; str:
    """Fetch current weather for the given location using WTTR.in."""
    # WTTR.in provides a simple text weather report. Use format=3 for a one-line summary.
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://wttr.in/{location}?format=3")
        resp.raise\_for\_status()
        return resp.text  # e.g. "Location: ☀️ +25°C"

Let’s break down what’s happening in the code:

- We create an Agent with the Anthropic Claude model. The model is specified by the string "anthropic:claude-sonnet-4-5". (Pydantic AI uses model strings like "anthropic:claude-sonnet-4-5" for Claude 4.5. Ensure your ANTHROPIC\_API\_KEY is set as an env variable so this works [[1]](https:/ai.pydantic.dev/models/anthropic/#:~:text=Environment%20variable) [[2]](https:/ai.pydantic.dev/models/anthropic/#:~:text=agent%20%3D%20Agent%28%27gateway%2Fanthropic%3Aclaude) .) We also pass an instructions string to set the assistant’s system behavior (optional).
- We attach an **MCPServerTool** in builtin\_tools. The MCPServerTool is a built-in tool that enables the agent to query a remote MCP server through the model’s API [[5]](https:/ai.pydantic.dev/builtin-tools/#:~:text=MCP%20Server%20Tool) . In the configuration above, we give it:
- an id (e.g. "internal\_mcp") which serves as the tool name the agent will use.
- the url of our MCP server’s endpoint.
- an authorization\_token and an Authorization header with a Bearer token, since our MCP server is protected by OAuth. (Pydantic AI will include this token when the model provider communicates with the MCP server.)
- allowed\_tools: you can restrict which specific sub-tools from the MCP server are exposed to the agent. In this example, we used "*" (assuming all tools or endpoints on the MCP server are allowed). You could list specific tool names if needed.
- a description for clarity (this may help the model understand what the MCP server is) [[6]](https:/ai.pydantic.dev/builtin-tools/#:~:text=agent%20%3D%20Agent%28%20%27gateway%2Fopenai,%281%29%20allowed_tools%3D%5B%27search_repositories%27%2C%20%27list_commits) .

**How MCPServerTool works:** Under the hood, the agent’s LLM (Claude, in this case) will handle calls to the MCP server via special context directives. The Pydantic AI framework communicates with the MCP endpoint through the model provider (Anthropic supports this tool-use pattern) [[7]](https:/ai.pydantic.dev/builtin-tools/#:~:text=The%20MCPServerTool%20allows%20your%20agent,handled%20by%20the%20model%20provider) [[8]](https:/ai.pydantic.dev/builtin-tools/#:~:text=Provider%20Supported%20Notes%20OpenAI%20Responses,supported%20Mistral%20%E2%9D%8C%20Not%20supported) . This setup allows the model to retrieve information from your server without a direct round-trip through your backend, which can optimize context usage and latency [[9]](https:/ai.pydantic.dev/builtin-tools/#:~:text=communication%20handled%20by%20the%20model,provider) . (Make sure your MCP server is accessible at a public URL if using a provider like Anthropic or OpenAI to reach it.)

- We then define a custom tool function get\_weather using the @agent.tool\_plain decorator. This function takes a location string and returns a string with the weather. It uses the WTTR.in API by making an HTTP GET request. We use **httpx** for an asynchronous HTTP call (since our tool function is async). WTTR.in returns a plaintext weather summary; in this case we use format=3 to get a concise one-line summary. The function returns the text directly, which will be given back to the agent.

*Example:* If the user asks “What’s the weather in **Paris** ?”, the agent can call get\_weather("Paris"), and it might get a response like "Paris: 🌦️ +18°C", which the agent can then use in its reply.

By defining these tools, the agent is now equipped to: - Call internal\_mcp tool for complex queries or data from your MCP server. - Call get\_weather for weather queries.

Pydantic AI automatically incorporates tool definitions into the model’s prompt or function-calling interfaces, so the model knows these tools are available to use when needed.

### Launching the Agent with AG-UI Adapter (Backend Setup)

With the agent and tools defined, the next step is to expose this agent through the AG-UI protocol so a frontend UI can interact with it. Pydantic AI provides an **AGUIApp** adapter that turns your agent into an ASGI application serving the AG-UI event stream [[10]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=from%20pydantic_ai%20import%20Agent%20from,app%20import%20AGUIApp) .

We can create an AGUIApp and run it using an ASGI server (like Uvicorn). For example:

# Wrap the agent in an AG-UI app (ASGI application)
app = AGUIApp(agent)

# If running this module directly, use Uvicorn to serve on an HTTP port
if \_\_name\_\_ == "\_\_main\_\_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

A few notes on this setup:

- AGUIApp(agent) creates an ASGI-compatible web app that will handle AG-UI protocol requests. Under the hood, it defines the routes and logic to accept a **RunAgentInput** (which includes user message, optional state, etc.) and stream back a sequence of events (SSE) representing the agent’s response [[11]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=The%20integration%20receives%20messages%20in,history%2C%20state%2C%20and%20available%20tools) [[12]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=These%20are%20converted%20to%20Pydantic,Sent%20Events%20%28SSE) . These events include the agent’s message content chunks, tool call events, state updates, etc., following the AG-UI standard.
- Running uvicorn on this app will start a server (in this case on port 8000). The AGUIApp by default will listen for requests on the root path (or you can mount it under a specific route if integrating into a larger FastAPI app). The example above uses if \_\_name\_\_ == "\_\_main\_\_" so that you can run the Python file directly to start the server.
- Once the server is running, your **frontend can send requests to it and receive a live event stream** . According to the Pydantic AI docs, you can use any ASGI server to host the AGUIApp; for example, running:

uvicorn my\_agent\_module:app --host 0.0.0.0 --port 8000

will serve the agent over HTTP [[13]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=Since%20,used%20with%20any%20ASGI%20server) . The frontend can then initiate a conversation by making a request to this server.

**How the AG-UI protocol works in this context:** When the frontend sends a user message, the AGUIApp will feed that into the agent. The agent (Claude model) processes it, possibly using the tools we defined. If a tool is needed: - The agent’s response (per the AG-UI spec) will include a tool invocation event, which the AGUIApp will execute by calling our Python function (for example, get\_weather or the MCP server proxy). - The result of the tool call is sent back into the model’s context or returned as an event, and the model continues or concludes its answer. - Throughout this process, AGUIApp streams events back to the client: events for text chunks as the answer is being generated, events when tools are called and when they return, and so on [[14]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,%28all%20done) [[4]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,tool%27s%20done%2C%20here%27s%20the%20result) . This means on the frontend, the user will see the assistant “typing” streaming text, and if the assistant uses a tool, the UI can react (for example, showing that it’s fetching data or updating UI state).

Pydantic AI’s AG-UI integration supports **frontend tools and state sharing** as well, but if you don’t have custom frontend components, you can primarily treat it like a streaming chat API. The key advantage is that the protocol is structured and supports complex interactions (including multi-step tool use and even human-in-the-loop confirmations) out of the box [[15]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=,loop%20checkpoints%20%2A%20Frontend%20tools) [[16]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=,tool%20inputs%2Foutputs%20to%20UI%20state) .

### Connecting the Frontend UI (React + TypeScript with AG-UI)

On the frontend side, you will use the AG-UI protocol to communicate with the backend we just set up. CopilotKit (the organization behind AG-UI) provides a client library to simplify this. If you are building a React app (Next.js or Vite), you can use the **AG-UI TypeScript SDK** or **CopilotKit’s React components** to handle the conversation.

Here’s a high-level outline to integrate the frontend:

- **Include the AG-UI client library:** Install the @ag-ui/client (and optionally CopilotKit’s React UI components). For example, CopilotKit’s library provides an HttpAgent class that represents a connection to an AG-UI backend [[17]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=%2F%2F%20AG%20UI%20client%20for,ui%2Fclient) .
- **Configure the HttpAgent to point to your backend:** In your frontend code, create an instance of HttpAgent with the URL of your running backend. For example, if your backend is at http://localhost:8000, you might do:

import { HttpAgent } from "@ag-ui/client";
const agentConnection = new HttpAgent({ url: "http://localhost:8000" });

(If your AGUIApp is mounted at a path, include it; e.g., url: "http://localhost:8000/myagent" if you mounted on /myagent. In our simple case, the root is serving the agent.)

CopilotKit’s examples often show configuring this in a Next.js API route and then using a context provider. For instance, they register the agent under a name and set up a runtime that can handle requests [[18]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=%2F%2F%20Step%201%3A%20Configure%20the,agent) [[19]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=agents%3A%20%7B%20%2F%2F%20%40ts,) . But for a basic setup, the HttpAgent alone can be used to send a message and get events.

- **Stream messages in the UI:** You can use the HttpAgent to send a user message and receive events. If not using CopilotKit’s higher-level abstractions, you could directly use the browser’s EventSource or fetch API to handle the SSE (server-sent events). However, using the provided SDK is easier. CopilotKit’s runtime and React components (like &lt;CopilotChat&gt; or &lt;CopilotKit&gt; provider) can manage the streaming and state for you [[20]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=match%20at%20L761%20HttpAgent%20is,compatible%20AI%20agent%E2%80%99s%20server) [[21]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,progress%20and%20intermediate%20results) .

*Example:* If using CopilotKit in a React app, you might wrap your app in a &lt;CopilotKit runtimeUrl="/api/copilotkit" agent="pydanticAgent"&gt; provider (where the runtimeUrl is a Next.js API that forwards to your backend) [[22]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=match%20at%20L995%20frontend%20UI,state%20system%20allows%20you%20to) [[23]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=app%20,%7Bchildren%7D%20%3C%2FCopilotKit%3E%20%3C%2Fbody%3E%20%3C%2Fhtml) . Inside, you can use &lt;CopilotChat /&gt; or custom UI that hooks into the agent’s state and events.

- **Frontend Tooling (Optional):** AG-UI also supports frontend “tools” – meaning the agent can send an event to trigger some action in the UI (like rendering a chart, or changing the background color). For example, in Pydantic AI’s demo, they had a tool named background that the agent could call to change the UI color [[24]](https:/ai.pydantic.dev/examples/ag-ui/#:~:text=) . Implementing these involves registering the tool on the frontend and handling the event. If your use-case needs it (for instance, the agent might want to display an image or require user confirmation), you would define those in the AG-UI client configuration. This is more advanced, so we’ll omit detailed code here, but be aware it’s possible.

In summary, once the backend is running with AGUIApp, the frontend will make requests to it following the AG-UI protocol. Using the CopilotKit/AG-UI SDK: - The user’s question is sent (as a JSON payload) to the backend, and an SSE connection is established. - As the backend agent processes the question (streaming the answer, possibly using tools), events are pushed over SSE. The AG-UI client library receives these and updates the React state or components accordingly (e.g., appending text to the chat, or handling a tool event). - The end result is a smooth, real-time chat UI where the assistant can utilize both server-side tools (our weather and MCP tools) and potentially frontend capabilities, all synchronized via the protocol.

### Putting It All Together

To recap, here are the steps to get your assistant UI working:

- **Backend (Python)** : Define your Pydantic AI Agent with the desired model (Claude 4.5 in our case). Attach the MCPServerTool for your internal MCP server (include the URL and auth token) [[5]](https:/ai.pydantic.dev/builtin-tools/#:~:text=MCP%20Server%20Tool) [[6]](https:/ai.pydantic.dev/builtin-tools/#:~:text=agent%20%3D%20Agent%28%20%27gateway%2Fopenai,%281%29%20allowed_tools%3D%5B%27search_repositories%27%2C%20%27list_commits) . Also define any custom function tools (like get\_weather). Then wrap the agent with AGUIApp and run a Uvicorn server to serve it [[13]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=Since%20,used%20with%20any%20ASGI%20server) .
- **Frontend (JavaScript/TypeScript)** : Use the AG-UI protocol client to connect. For instance, instantiate an HttpAgent pointing to your backend URL [[18]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=%2F%2F%20Step%201%3A%20Configure%20the,agent) . If you use CopilotKit’s React components, set up the &lt;CopilotKit&gt; provider with the agent. Otherwise, manage an EventSource to handle incoming SSE events manually. Ensure your UI can display streaming messages and any interactive prompts/events coming from the agent.
- **Test the flow** : Open your frontend app, ask a question (e.g. “What’s the weather in New York today?”). The frontend sends this to the backend; the backend agent will decide to use the get\_weather tool, call WTTR.in, get the result, and stream back the answer. You should see the assistant’s response appear word-by-word in the UI, possibly after a brief indication that it fetched data. Likewise, if you ask something that requires the MCP server (e.g. an internal knowledge query), the agent will call the internal\_mcp tool, and Claude (via the provider’s API) will fetch that info from your MCP server and include it in the answer.

By following these steps with the provided code examples, you set up a full-stack AI assistant: **Pydantic AI** powers the agent and tool usage on the backend, and **AG-UI/CopilotKit** bridges it to a responsive frontend UI. This architecture allows rich interactions (streaming responses, tool usage, and stateful conversations) with minimal glue code [[16]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=,tool%20inputs%2Foutputs%20to%20UI%20state) , since the protocol and libraries handle most of the heavy lifting. Happy coding with your new Assistant UI!

**Sources:**

- Pydantic AI Documentation – *Built-in Tools: MCPServerTool* [[5]](https:/ai.pydantic.dev/builtin-tools/#:~:text=MCP%20Server%20Tool) [[6]](https:/ai.pydantic.dev/builtin-tools/#:~:text=agent%20%3D%20Agent%28%20%27gateway%2Fopenai,%281%29%20allowed_tools%3D%5B%27search_repositories%27%2C%20%27list_commits)
- Pydantic AI Documentation – *AG-UI Integration and Usage* [[10]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=from%20pydantic_ai%20import%20Agent%20from,app%20import%20AGUIApp) [[13]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=Since%20,used%20with%20any%20ASGI%20server)
- *CopilotKit Blog:* Introducing Pydantic AI Integration with AG-UI [[25]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=Pydantic%20AI%20is%20now%20natively,UI) [[26]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=,tool%20inputs%2Foutputs%20to%20UI%20state) (background on the integration)
- *AG-UI Protocol Overview* (CopilotKit Docs) – Explanation of streaming events and tools [[14]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,%28all%20done) [[4]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,tool%27s%20done%2C%20here%27s%20the%20result)
- *CopilotKit Dev Tutorial:* Full-Stack AI Agent with Pydantic + AG-UI – Frontend integration example [[18]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=%2F%2F%20Step%201%3A%20Configure%20the,agent) [[19]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=agents%3A%20%7B%20%2F%2F%20%40ts,)

[[1]](https:/ai.pydantic.dev/models/anthropic/#:~:text=Environment%20variable) [[2]](https:/ai.pydantic.dev/models/anthropic/#:~:text=agent%20%3D%20Agent%28%27gateway%2Fanthropic%3Aclaude) Anthropic - Pydantic AI

[https://ai.pydantic.dev/models/anthropic/](https:/ai.pydantic.dev/models/anthropic)

[[3]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=different%20kinds%20of%20events,a%20simple%20rundown) [[4]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,tool%27s%20done%2C%20here%27s%20the%20result) [[14]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,%28all%20done) [[17]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=%2F%2F%20AG%20UI%20client%20for,ui%2Fclient) [[18]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=%2F%2F%20Step%201%3A%20Configure%20the,agent) [[19]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=agents%3A%20%7B%20%2F%2F%20%40ts,) [[20]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=match%20at%20L761%20HttpAgent%20is,compatible%20AI%20agent%E2%80%99s%20server) [[21]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=,progress%20and%20intermediate%20results) [[22]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=match%20at%20L995%20frontend%20UI,state%20system%20allows%20you%20to) [[23]](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e#:~:text=app%20,%7Bchildren%7D%20%3C%2FCopilotKit%3E%20%3C%2Fbody%3E%20%3C%2Fhtml) Build a Stock Portfolio AI Agent (Fullstack, Pydantic AI + AG-UI) - DEV Community

[https://dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e](https:/dev.to/copilotkit/build-a-fullstack-stock-portfolio-ai-agent-with-pydantic-ai-ag-ui-3e2e)

[[5]](https:/ai.pydantic.dev/builtin-tools/#:~:text=MCP%20Server%20Tool) [[6]](https:/ai.pydantic.dev/builtin-tools/#:~:text=agent%20%3D%20Agent%28%20%27gateway%2Fopenai,%281%29%20allowed_tools%3D%5B%27search_repositories%27%2C%20%27list_commits) [[7]](https:/ai.pydantic.dev/builtin-tools/#:~:text=The%20MCPServerTool%20allows%20your%20agent,handled%20by%20the%20model%20provider) [[8]](https:/ai.pydantic.dev/builtin-tools/#:~:text=Provider%20Supported%20Notes%20OpenAI%20Responses,supported%20Mistral%20%E2%9D%8C%20Not%20supported) [[9]](https:/ai.pydantic.dev/builtin-tools/#:~:text=communication%20handled%20by%20the%20model,provider) Built-in Tools - Pydantic AI

[https://ai.pydantic.dev/builtin-tools/](https:/ai.pydantic.dev/builtin-tools)

[[10]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=from%20pydantic_ai%20import%20Agent%20from,app%20import%20AGUIApp) [[11]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=The%20integration%20receives%20messages%20in,history%2C%20state%2C%20and%20available%20tools) [[12]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=These%20are%20converted%20to%20Pydantic,Sent%20Events%20%28SSE) [[13]](https:/ai.pydantic.dev/ui/ag-ui/#:~:text=Since%20,used%20with%20any%20ASGI%20server) AG-UI - Pydantic AI

[https://ai.pydantic.dev/ui/ag-ui/](https:/ai.pydantic.dev/ui/ag-ui)

[[15]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=,loop%20checkpoints%20%2A%20Frontend%20tools) [[16]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=,tool%20inputs%2Foutputs%20to%20UI%20state) [[25]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=Pydantic%20AI%20is%20now%20natively,UI) [[26]](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui#:~:text=,tool%20inputs%2Foutputs%20to%20UI%20state) Introducing Pydantic AI Integration with AG-UI | Blog | CopilotKit

[https://www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui](https:/www.copilotkit.ai/blog/introducing-pydantic-ai-integration-with-ag-ui)

[[24]](https:/ai.pydantic.dev/examples/ag-ui/#:~:text=) Agent User Interaction (AG-UI) - Pydantic AI

[https://ai.pydantic.dev/examples/ag-ui/](https:/ai.pydantic.dev/examples/ag-ui)