# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import logging
import os
from typing import Literal
from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from mcp import Tool
from fastmcp import Client


from tools.tools import list_indices_tool, ListIndicesArgs

if load_dotenv():
    print("Loaded .env file")
else:
    print("No .env file found")

logger = logging.getLogger("os_query_mcp")




async def main_http():
    # Connect via HTTP to the MCP server
    async with Client("http://localhost:8000/mcp/") as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        # all_indices = await client.read_resource("resource://all_indices")
        # indices = json.loads(all_indices[0].text)
        # all_indices = await client.read_resource_mcp("resource://all_indices")
        # print(f"Available tools: {tools}")
        # print(f"Available resources: {resources}")
        params = ListIndicesArgs(
            # opensearch_cluster_name=os.getenv("OPENSEARCHDOMAIN"),
            # index="people_01oct2025",
            include_detail=True
        )
        result = await client.call_tool("list_indices",arguments={"args": params.model_dump()})
        print(f"Result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(main_http())