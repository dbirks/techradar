#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydantic-ai[anthropic,logfire]>=0.0.1",
#     "pydantic-ai-ui[ag-ui]>=0.0.1",
#     "httpx>=0.27.0",
#     "uvicorn>=0.30.0",
#     "python-dotenv>=1.0.0",
# ]
# ///

"""
Pydantic AI Agent with AG-UI Integration

This script demonstrates a complete Pydantic AI agent setup with:
- Anthropic Claude 4.5 as the LLM
- Weather lookup tool (wttr.in)
- Context7 MCP server (up-to-date code documentation)
- E-gineering MCP server (additional capabilities)
- AG-UI integration for streaming responses to a frontend
- Logfire observability integration

Run with: uv run agent.py
Then access the API at: http://localhost:8000

Note: MCPServerTool currently only supports static token authentication.
Dynamic Client Registration (DCR) is not yet supported by pydantic-ai.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_ai import Agent, MCPServerTool
from pydantic_ai.ui.ag_ui.app import AGUIApp
import httpx
import logfire

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configure Logfire for observability
logfire.configure()
logfire.info("Initializing Pydantic AI Agent with AG-UI")


# Build list of MCP server tools based on available tokens
mcp_tools = []
enabled_tools = ["get_weather"]

# Context7 MCP Server - Up-to-date code documentation (works without API key)
context7_key = os.getenv("CONTEXT7_API_KEY", "")
mcp_tools.append(
    MCPServerTool(
        id="context7",
        url="https://mcp.context7.com/mcp",
        authorization_token=context7_key,
        allowed_tools=["*"],
        description="Context7 MCP server for up-to-date code documentation and context",
        headers={
            "Authorization": f"Bearer {context7_key}",
            "Content-Type": "application/json",
        } if context7_key else {"Content-Type": "application/json"}
    )
)
enabled_tools.append("context7")

# E-gineering MCP Server
if os.getenv("MCP_OAUTH_TOKEN"):
    mcp_tools.append(
        MCPServerTool(
            id="eg_mcp",
            url="https://mcp.e-gineering.com/mcp",
            authorization_token=os.getenv("MCP_OAUTH_TOKEN", ""),
            allowed_tools=["*"],
            description="E-gineering MCP server with various capabilities",
            headers={
                "Authorization": f"Bearer {os.getenv('MCP_OAUTH_TOKEN', '')}",
                "Content-Type": "application/json",
            }
        )
    )
    enabled_tools.append("eg_mcp")


# Initialize the agent with Anthropic Claude 4.5
# Logfire will automatically instrument the agent
agent = Agent(
    "anthropic:claude-sonnet-4-5",
    instructions="""You are a helpful assistant with access to:
    1. Weather information via wttr.in for any location
    2. Context7 MCP server for up-to-date code documentation
    3. E-gineering MCP server for additional capabilities

    Be concise and helpful in your responses.""",
    builtin_tools=mcp_tools
)

logfire.info("Agent initialized", tools=enabled_tools)


@agent.tool_plain
async def get_weather(location: str) -> str:
    """Fetch current weather for the given location using WTTR.in.

    Args:
        location: The city or location name to get weather for

    Returns:
        A formatted weather string with temperature and conditions
    """
    with logfire.span("get_weather", location=location):
        try:
            async with httpx.AsyncClient() as client:
                # Use format=3 for a concise one-line weather summary
                resp = await client.get(
                    f"https://wttr.in/{location}",
                    params={"format": "3"},
                    timeout=10.0
                )
                resp.raise_for_status()
                weather = resp.text.strip()
                logfire.info("Weather fetched successfully", location=location, weather=weather)
                return weather
        except httpx.HTTPError as e:
            error_msg = f"Error fetching weather for {location}: {str(e)}"
            logfire.error("Weather fetch failed", location=location, error=str(e))
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error getting weather: {str(e)}"
            logfire.error("Unexpected weather error", location=location, error=str(e))
            return error_msg


# Wrap the agent in an AG-UI ASGI application
app = AGUIApp(agent)


if __name__ == "__main__":
    import uvicorn

    # Check for required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  WARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("   Set it with: export ANTHROPIC_API_KEY=your_key_here")
        print("   Or add it to demo/api/.env file")
        logfire.warn("ANTHROPIC_API_KEY not set")

    # Check for optional MCP server tokens
    if not os.getenv("CONTEXT7_API_KEY"):
        print("\n💡 TIP: Context7 is running without an API key (free tier)")
        print("   For higher rate limits, add CONTEXT7_API_KEY to demo/api/.env")

    if not os.getenv("MCP_OAUTH_TOKEN"):
        print("\n⚠️  Optional: E-gineering MCP server not configured")
        print("   Add MCP_OAUTH_TOKEN to demo/api/.env to enable it")
        print("   Note: DCR (Dynamic Client Registration) is not yet supported by pydantic-ai")

    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    print("\n🚀 Starting AG-UI Agent Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print("\n💡 Available tools:")
    print("   - get_weather: Fetch weather for any location")
    print("   - context7: Up-to-date code documentation (free tier)")
    if os.getenv("MCP_OAUTH_TOKEN"):
        print("   - eg_mcp: E-gineering MCP server capabilities")
    print("\n📊 Logfire observability: https://logfire.pydantic.dev/")
    print("\nPress Ctrl+C to stop the server\n")

    logfire.info("Starting server", host=host, port=port)

    # Instrument uvicorn with logfire
    logfire.instrument_httpx()
    uvicorn.run(app, host=host, port=port)
