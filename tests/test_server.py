"""Tests for server-level MCP operations."""

import pytest
from fastmcp import Client

@pytest.mark.asyncio
async def test_ping(mcp_client: Client):
    assert await mcp_client.ping() is True
