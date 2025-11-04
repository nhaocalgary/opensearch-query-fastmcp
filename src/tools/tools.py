# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import json
from .tool_params import (
    GetAllocationArgs,
    GetClusterStateArgs,
    GetIndexInfoArgs,
    GetIndexMappingArgs,
    GetIndexStatsArgs,
    GetLongRunningTasksArgs,
    CatNodesArgs,
    GetNodesArgs,
    GetNodesHotThreadsArgs,
    GetQueryInsightsArgs,
    GetSegmentsArgs,
    GetShardsArgs,
    ListIndicesArgs,
    SearchIndexArgs,
    baseToolArgs,
)
from .utils import is_tool_compatible
from opensearch.helper import (
    get_allocation,
    get_cluster_state,
    get_index,
    get_index_info,
    get_index_mapping,
    get_index_stats,
    get_long_running_tasks,
    get_nodes,
    get_nodes_info,
    get_nodes_hot_threads,
    get_opensearch_version,
    get_query_insights,
    get_segments,
    get_shards,
    list_indices,
    search_index,
)


def check_tool_compatibility(tool_name: str, args: baseToolArgs = None):
    opensearch_version = get_opensearch_version(args)
    if not is_tool_compatible(opensearch_version, TOOL_REGISTRY[tool_name]):
        tool_display_name = TOOL_REGISTRY[tool_name].get('display_name', tool_name)
        min_version = TOOL_REGISTRY[tool_name].get('min_version', '')
        max_version = TOOL_REGISTRY[tool_name].get('max_version', '')

        version_info = (
            f'{min_version} to {max_version}'
            if min_version and max_version
            else f'{min_version} or later'
            if min_version
            else f'up to {max_version}'
            if max_version
            else None
        )

        error_message = f"Tool '{tool_display_name}' is not supported for this OpenSearch version (current version: {opensearch_version})."
        if version_info:
            error_message += f' Supported version: {version_info}.'

        raise Exception(error_message)


async def list_indices_tool(args: ListIndicesArgs) -> json:
    try:
        check_tool_compatibility('ListIndexTool', args)

        # If index is provided, always return detailed information for that specific index
        if args.index:
            index_info = get_index(args)
            return index_info

        # Otherwise, list all indices
        indices = list_indices(args)

        # If include_detail is False, return only pure list of index names
        if not args.include_detail:
            index_names = [
                item.get('index')
                for item in indices
                if isinstance(item, dict) and 'index' in item
            ]
            return index_names

        return indices
    except Exception as e:
        return [{'type': 'text', 'Error listing indices': {str(e)}}]


async def get_index_mapping_tool(args: GetIndexMappingArgs) -> json:
    try:
        check_tool_compatibility('IndexMappingTool', args)
        mapping = get_index_mapping(args)

        return mapping
    except Exception as e:
        return [{'type': 'text', 'text': f'Error getting mapping: {str(e)}'}]


async def search_index_tool(args: SearchIndexArgs) -> json:
    try:
        check_tool_compatibility('SearchIndexTool', args)
        result = search_index(args)

        return result
    except Exception as e:
        return [{'type': 'text', 'text': f'Error searching index: {str(e)}'}]


async def get_cluster_state_tool(args: GetClusterStateArgs) -> json:
    """Tool to get the current state of the cluster.
    
    Args:
        args: GetClusterStateArgs containing optional metric and index filters
        
    Returns:
        list[dict]: Cluster state information in MCP format
    """
    try:
        check_tool_compatibility('GetClusterStateTool', args)
        result = get_cluster_state(args)
            
        return result
    except Exception as e:
        return [{'type': 'text', 'text': f'Error getting cluster state: {str(e)}'}]



async def get_index_info_tool(args: GetIndexInfoArgs) -> json:
    """Tool to get detailed information about an index including mappings, settings, and aliases.
    
    Args:
        args: GetIndexInfoArgs containing the index name
        
    Returns:
        list[dict]: Index information in MCP format
    """
    try:
        check_tool_compatibility('GetIndexInfoTool', args)
        result = get_index_info(args)
        
        
        return result
    except Exception as e:
        return [{'type': 'text', 'text': f'Error getting index information: {str(e)}'}]


async def get_index_stats_tool(args: GetIndexStatsArgs) -> json:
    """Tool to get statistics about an index.
    
    Args:
        args: GetIndexStatsArgs containing the index name and optional metric filter
        
    Returns:
        list[dict]: Index statistics in MCP format
    """
    try:
        check_tool_compatibility('GetIndexStatsTool', args)
        result = get_index_stats(args)
        return result
    except Exception as e:
        return [{'type': 'text', 'text': f'Error getting index statistics: {str(e)}'}]


async def get_query_insights_tool(args: GetQueryInsightsArgs) -> json:
    """Tool to get query insights from the /_insights/top_queries endpoint.
    
    Args:
        args: GetQueryInsightsArgs containing connection parameters
        
    Returns:
        list[dict]: Query insights in MCP format
    """
    try:
        check_tool_compatibility('GetQueryInsightsTool', args)
        result = get_query_insights(args)
        return result
    except Exception as e:
        return [{'type': 'text', 'text': f'Error getting query insights: {str(e)}'}]


from .generic_api_tool import GenericOpenSearchApiArgs, generic_opensearch_api_tool


# Registry of available OpenSearch tools with their metadata
TOOL_REGISTRY = {
    'ListIndexTool': {
        'display_name': 'ListIndexTool',
        'description': 'Lists indices in the OpenSearch cluster. By default, returns a filtered list of index names only to minimize response size. Set include_detail=true to return full metadata from cat.indices (docs.count, store.size, etc.). If an index parameter is provided, returns detailed information for that specific index including mappings and settings.',
        'input_schema': ListIndicesArgs.model_json_schema(),
        'function': list_indices_tool,
        'args_model': ListIndicesArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET',
    },
    'IndexMappingTool': {
        'display_name': 'IndexMappingTool',
        'description': 'Retrieves index mapping and setting information for an index in OpenSearch',
        'input_schema': GetIndexMappingArgs.model_json_schema(),
        'function': get_index_mapping_tool,
        'args_model': GetIndexMappingArgs,
        'http_methods': 'GET',
    },
    'SearchIndexTool': {
        'display_name': 'SearchIndexTool',
        'description': 'Searches an index using a query written in query domain-specific language (DSL) in OpenSearch',
        'input_schema': SearchIndexArgs.model_json_schema(),
        'function': search_index_tool,
        'args_model': SearchIndexArgs,
        'http_methods': 'GET, POST',
    },
    'GetClusterStateTool': {
        'display_name': 'GetClusterStateTool',
        'description': 'Gets the current state of the cluster including node information, index settings, and more. Can be filtered by specific metrics and indices.',
        'input_schema': GetClusterStateArgs.model_json_schema(),
        'function': get_cluster_state_tool,
        'args_model': GetClusterStateArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET',
    },
    'GetIndexInfoTool': {
        'display_name': 'GetIndexInfoTool',
        'description': 'Gets detailed information about an index including mappings, settings, and aliases. Supports wildcards in index names.',
        'input_schema': GetIndexInfoArgs.model_json_schema(),
        'function': get_index_info_tool,
        'args_model': GetIndexInfoArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET',
    },
    'GetIndexStatsTool': {
        'display_name': 'GetIndexStatsTool',
        'description': 'Gets statistics about an index including document count, store size, indexing and search performance metrics. Can be filtered to specific metrics.',
        'input_schema': GetIndexStatsArgs.model_json_schema(),
        'function': get_index_stats_tool,
        'args_model': GetIndexStatsArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET',
    },
    'GetQueryInsightsTool': {
        'display_name': 'GetQueryInsightsTool',
        'description': 'Gets query insights from the /_insights/top_queries endpoint, showing information about query patterns and performance.',
        'input_schema': GetQueryInsightsArgs.model_json_schema(),
        'function': get_query_insights_tool,
        'args_model': GetQueryInsightsArgs,
        'min_version': '2.12.0',  # Query insights feature requires OpenSearch 2.12+
        'http_methods': 'GET',
    },
    'GenericOpenSearchApiTool': {
        'display_name': 'GenericOpenSearchApiTool',
        'description': 'A flexible tool for calling any OpenSearch API endpoint. Supports all HTTP methods with custom paths, query parameters, request bodies, and headers. Use this when you need to access OpenSearch APIs that don\'t have dedicated tools, or when you need more control over the request. Leverages your knowledge of OpenSearch API documentation to construct appropriate requests.',
        'input_schema': GenericOpenSearchApiArgs.model_json_schema(),
        'function': generic_opensearch_api_tool,
        'args_model': GenericOpenSearchApiArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET, POST, PUT, DELETE, HEAD, PATCH',
    },
}
