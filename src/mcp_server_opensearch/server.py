# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

"""MCP server for OpenSearch querying only, no state management, no persistence."""

import asyncio
import json
import logging
import os
from typing import Literal
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from mcp import Tool


from tools.tools import ListIndicesArgs, GetIndexMappingArgs, SearchIndexArgs, GetClusterStateArgs, GetIndexInfoArgs, GetIndexStatsArgs
from tools.tools import list_indices_tool, get_index_mapping_tool, search_index_tool, get_cluster_state_tool , get_index_info_tool, get_index_stats_tool   

if load_dotenv():
    print("Loaded .env file")
else:
    print("No .env file found")

logger = logging.getLogger("os_query_mcp")

class OpenSearchConnectionContext:
    """Context for OpenSearch cluster level static details."""
    def __init__(self):
        self._all_indices = None
        self._index_mappings = None

    @property
    async def all_indices(self):
        if self._all_indices is None:
            # Lazy initialization
            self._all_indices = await list_indices_tool(ListIndicesArgs(include_detail=True))
        return self._all_indices


    @property
    def index_mappings(self):
        if not hasattr(self, '_index_mappings'):
            self._index_mappings = {}
        return self._index_mappings



def create_mcp_server(namespace: str = "") -> FastMCP:
    """Create an MCP server instance for data modeling."""

    # Create a singleton context for static data
    static_ctx = OpenSearchConnectionContext()

    mcp: FastMCP = FastMCP(
        name= "os-query-mcp MCP server",        
        stateless_http=True
    )

    # @mcp.resource("resource://all_indices")
    # async def get_all_indices(        
    #     args: ListIndicesArgs,
    #     ctx: Context
    # ) -> str:
    #     """List all indices in the OpenSearch cluster."""
    #     result = [
    #             {
    #                 "index": item["index"],
    #                 "docs.count": item.get("docs.count"),
    #                 "store.size": item.get("store.size")
    #             }
    #             for item in static_ctx.all_indices
    #         ]
        
    #     return result

    # @mcp.resource("resource://{indice}/index_mappings")
    # async def get_index_mappings(indice: str, ctx: Context) -> str:
    #     """Get the mapping for a specific index."""
    #     mapping = static_ctx.get_index_mapping(indice)
    #     if mapping is None:
    #         arg = GetIndexMappingArgs(index=indice)
    #         mapping = await get_index_mapping_tool(arg)
    #         static_ctx.set_index_mapping(indice, mapping)
    #     return json.dumps(mapping, separators=(',', ':'))

    @mcp.tool()
    async def list_indices(
        args: ListIndicesArgs,
    ) -> json:
        """List all indices in the OpenSearch cluster."""
        return await static_ctx.all_indices
    
    @mcp.tool()
    async def get_index_mapping(
        args: GetIndexMappingArgs,
    ) -> dict:
        """Get the mapping for a specific index."""
        return await get_index_mapping_tool(args)
        
    @mcp.tool()
    async def search_index(
        args: SearchIndexArgs,
    ) -> json:
        """Search for documents in the OpenSearch cluster."""
        return await search_index_tool(args)

    @mcp.tool()
    async def get_cluster_state(
        args: GetClusterStateArgs,
    ) -> dict:
        """Get the cluster state of the OpenSearch cluster."""
        return await get_cluster_state_tool(args)
    
    @mcp.tool()
    async def get_index_info(   
        args: GetIndexInfoArgs,
    ) -> dict:
        """Get information about a specific index."""
        return await get_index_info_tool(args)
    
    @mcp.tool()
    async def get_index_stats(
        args: GetIndexStatsArgs,
    ) -> dict:
        """Get statistics about a specific index."""
        return await get_index_stats_tool(args)
    
    return mcp

async def main(
    transport: Literal["stdio", "sse", "http"] = "stdio",
    namespace: str = "",
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp/",
    allow_origins: list[str] = [],
    allowed_hosts: list[str] = [],
) -> None:
    logger.info("Starting OpenSearch query MCP Server")

    custom_middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        ),
        Middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts),
    ]

    mcp = create_mcp_server(namespace=namespace)

    match transport:
        case "http":
            logger.info(
                f"Running OS query mcp Server with HTTP transport on {host}:{port}..."
            )
            await mcp.run_http_async(
                host=host, port=port, path=path, middleware=None
            )
        case "stdio":
            logger.info(
                "Running OS query mcp Server with stdio transport..."
            )
            await mcp.run_stdio_async()
        case "sse":
            logger.info(
                f"Running OS query mcp Server with SSE transport on {host}:{port}..."
            )
            await mcp.run_http_async(
                host=host,
                port=port,
                path=path,
                middleware=custom_middleware,
                transport="sse",
            )

def main_cli():
    asyncio.run(
        main(
            transport=os.getenv("OSQUERYMCP_TRANSPORT", "http"),
            namespace=os.getenv("OSQUERYMCP_NAMESPACE", "opensearch_query"),

        )
    )

    
if __name__ == "__main__":
    asyncio.run(
        main(
            transport=os.getenv("OSQUERYMCP_TRANSPORT", "http"),
            namespace=os.getenv("OSQUERYMCP_NAMESPACE", "opensearch_query"),

        )
    )