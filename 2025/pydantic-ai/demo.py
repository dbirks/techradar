# /// script
# requires-python = "~=3.13"
# dependencies = [
#     "duckduckgo-search==8.0.2",
#     "pydantic-ai-slim[anthropic,logfire,mcp]",
#     "python-dotenv==1.1.0",
#     "rich",
# ]
# ///

import subprocess
from textwrap import dedent

import logfire
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from pydantic import BaseModel
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.tools import Tool
from pydantic_ai.usage import UsageLimits
from rich.console import Console
from rich.table import Table


# Define a tool that the agent can use to search the web
def find_package_published_date(dependency_name: str, version: str = "") -> str:
    """
    Use this to search the web for information about a package, specifically a published date for the specific version.

    Args:
        dependency_name: The name of the package to search for.
        version: The version of the package to search for.

    Returns:
        Raw text from the top 3 results of the web search.
        You can then search this text for the published date for the specific version.
    """
    try:
        results: str = DDGS().text(
            keywords=f"published date for version {version} of {dependency_name}",
            max_results=3,
        )
    except Exception as e:
        raise ModelRetry(
            f'Couldn\'t find results for package: "{dependency_name}"'
        ) from e
    return results


def search_current_directory_for_string(search_string: str) -> str:
    """
    Use this to search the current directory for a specific string with ripgrep.

    Args:
        search_string: The string to search for.

    Returns:
        The results of the ripgrep search.
    """

    # run rg with the string
    try:
        result = subprocess.run(
            ["rg", "--", search_string],
            check=True,
            text=True,
            capture_output=True,
        )
    except Exception as e:
        raise ModelRetry(f'Couldn\'t find results for string: "{search_string}"') from e

    return result.stdout


# Define the exact type we want the agent to output
class Dependency(BaseModel):
    name: str
    version: str
    published_date: str


class AgentOutput(BaseModel):
    dependencies: list[Dependency]


async def main():
    load_dotenv(override=True)

    logfire.configure()
    logfire.instrument_pydantic_ai()
    # logfire.instrument_mcp()
    logfire.instrument_anthropic()

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
            You are a helpful assistant who is trying to help the user do a quick search of a repo to find dependencies to upgrade.

            First, get a list of the directory structure you're in.

            Then read in files like pom.xml, Dockerfile, or anything similar that might contain dependency information.

            That will give you a list of dependencies and each one's version if it has one.

            Then for each one that you have an exact version for, use the `find_package_published_date` tool to try to find the published date for each dependency.
        """),
        mcp_servers=[
            filesystem_search,
        ],
        tools=[
            Tool(find_package_published_date),
            Tool(search_current_directory_for_string),
        ],
        usage_limits=UsageLimits(request_limit=100),
        output_type=AgentOutput,
        retries=200,
    )

    # Run the agent
    async with agent.run_mcp_servers():
        result = await agent.run(
            "Search for any dependencies in the current directory."
        )

    print(result)

    # Display the results in a table
    print()
    console = Console()
    table = Table(title="Dependency List")
    table.add_column("Name", style="green")
    table.add_column("Version", style="blue")
    table.add_column("Published Date", style="orange")
    for dependency in result.output.dependencies:
        table.add_row(dependency.name, dependency.version, dependency.published_date)
    console.print(table)
    print()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
