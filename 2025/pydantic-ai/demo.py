# /// script
# requires-python = "~=3.13"
# dependencies = [
#     "duckduckgo-search==8.0.2",
#     "pydantic-ai-slim[anthropic,logfire,mcp]",
#     "rich",
# ]
# ///

import subprocess
from textwrap import dedent

import logfire
from duckduckgo_search import DDGS
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.tools import Tool


# Define a tool that the agent can use to search the web
def find_package_published_date(dependency_name: str, version: str) -> str:
    """
    Use this to search the web for information about a package, specifically a published date for the specific version.

    Args:
        dependency_name: The name of the package to search for.
        version: The version of the package to search for.

    Returns:
        Raw text from the top 3 results of the web search.
        You can then search this text for the published date for the specific version.
    """
    results: str = DDGS().text(
        keywords=f"published date for version {version} of {dependency_name}",
        max_results=3,
    )
    return results


def search_current_directory_for_string(string: str) -> str:
    """
    Use this to search the current directory for a specific string with ripgrep.

    Args:
        string: The string to search for.

    Returns:
        Raw text from the top 3 results of the web search.
    """
    results = subprocess.check_output(["rg", string])
    return results.decode("utf-8")


# Define the exact type we want the agent to output
class Dependency(BaseModel):
    name: str
    version: str
    published_date: str


class AgentOutput(BaseModel):
    dependencies: list[Dependency]


async def main():
    logfire.configure(send_to_logfire=False)
    logfire.instrument_pydantic_ai()
    logfire.mcp()

    # Use an MCP server to search the filesystem, restricted to just the current directory you're in.
    # This MCP server provides many tools for the agent to use.
    filesystem_search = MCPServerStdio(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem@2025.3.28", "."],
    )

    # Init the agent
    agent = Agent(
        model="claude-sonnet-4-20250514",
        instructions=dedent("""
            You are a helpful assistant who is trying to help the user upgrade packages in a repo.

            Do a thorough search of the current directory you're in to find any and all dependencies, with their version number.

            Then, use the `find_package_published_date` tool to try to find the published date for each dependency.
        """),
        mcp_servers=[
            filesystem_search,
        ],
        tools=[
            Tool(find_package_published_date),
            Tool(search_current_directory_for_string),
        ],
        output_type=AgentOutput,
    )

    # Run the agent
    async with agent.run_mcp_servers():
        await agent.run("Search for any dependencies in the current directory.")

    print(agent.output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
