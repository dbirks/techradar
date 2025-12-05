# MCP

## Links

Tech Radar: https://www.thoughtworks.com/radar/platforms/model-context-protocol-mcp

Website: https://modelcontextprotocol.io

Python SDK Github: https://github.com/modelcontextprotocol/python-sdk

## Described several ways

An MCP server...
  - Bundles together tools for an LLM to use
  - Gives you a way to put an English wrapper around API calls.

## Notes

MCP technically supports tools, resources, and prompts, but support for resources and prompts isn't very widespread, so we'll just ignore those for now. This compatibility chart helps with seeing which MCP client supports which features:

https://modelcontextprotocol.io/clients#feature-support-matrix

## Different types

Transport types:

- stdio
  - Standard input/output
  - Runs locally on your computer
- Streamable HTTP
  - A server you host

## Security




## The future

- OAuth introduced in the past couple months
- MCP as a bridge to the physical world
- Docker MCP Catalog: https://docs.docker.com/ai/mcp-catalog-and-toolkit/catalog/
- Librechat at clients, plus their internal APIs, plus MCP, equals ??
