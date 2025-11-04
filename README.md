

## OpenSearch Query MCP Server

**opensearch-Query-mcp-server** is a Model Context Protocol (MCP) server forked from [opensearch-project/opensearch-mcp-server-py](https://github.com/opensearch-project/opensearch-mcp-server-py) with following focus

**Key features:**

- Remove all cluster admin, state management tools
- Soly focus on search query context
- Wrap all tool call using FastMCP
- Server context to hold static data like indexes list and index mappings
- Provide indexes and index mapping as MCP resources to avoid subsequent unnesscery Agent tool call
- Docker/docker-compose deployment option
