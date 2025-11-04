





# Unit tests for server.py
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import types
import asyncio

sys.path.insert(0, '../../src')
from mcp_server_opensearch import server

class TestServer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Patch tool functions to avoid real OpenSearch calls
        patcher1 = patch('mcp_server_opensearch.server.list_indices_tool', new_callable=AsyncMock)
        patcher2 = patch('mcp_server_opensearch.server.get_index_mapping_tool', new_callable=AsyncMock)
        patcher3 = patch('mcp_server_opensearch.server.search_index_tool', new_callable=AsyncMock)
        patcher4 = patch('mcp_server_opensearch.server.get_cluster_state_tool', new_callable=AsyncMock)
        patcher5 = patch('mcp_server_opensearch.server.get_index_info_tool', new_callable=AsyncMock)
        patcher6 = patch('mcp_server_opensearch.server.get_index_stats_tool', new_callable=AsyncMock)
        self.patchers = [patcher1, patcher2, patcher3, patcher4, patcher5, patcher6]
        for p in self.patchers:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self.patchers])

    async def test_create_mcp_server(self):
        mcp = server.create_mcp_server()
        self.assertIsNotNone(mcp)
        self.assertTrue(hasattr(mcp, 'resources'))
        self.assertTrue(hasattr(mcp, 'tools'))

    async def test_resource_registration(self):
        mcp = server.create_mcp_server()
        # Check that resources are registered
        resource_names = [r.name for r in mcp.resources]
        self.assertIn('resource://all_indices', resource_names)
        self.assertTrue(any('index_mappings' in r for r in resource_names))

    async def test_tool_registration(self):
        mcp = server.create_mcp_server()
        tool_names = [t.name for t in mcp.tools]
        self.assertIn('list_indices', tool_names)
        self.assertIn('get_index_mapping', tool_names)
        self.assertIn('search_index', tool_names)
        self.assertIn('get_cluster_state', tool_names)
        self.assertIn('get_index_info', tool_names)
        self.assertIn('get_index_stats', tool_names)

    async def test_get_all_indices_resource(self):
        mcp = server.create_mcp_server()
        # Patch static_ctx to simulate indices
        with patch.object(server.OpenSearchConnectionContext, 'get_all_indices', return_value=[{"index": "test", "docs.count": 1, "store.size": "1kb"}]):
            resource = next(r for r in mcp.resources if r.name == 'resource://all_indices')
            result = await resource.func(MagicMock())
            self.assertIsInstance(result, list)
            self.assertEqual(result[0]["index"], "test")

    async def test_get_index_mappings_resource(self):
        mcp = server.create_mcp_server()
        with patch.object(server.OpenSearchConnectionContext, 'get_index_mapping', return_value={"mapping": "value"}):
            resource = next(r for r in mcp.resources if 'index_mappings' in r.name)
            result = await resource.func("test_index", MagicMock())
            self.assertIn('mapping', result)

if __name__ == "__main__":
    unittest.main()
