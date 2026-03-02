"""Tests for the MCP tools."""

import pytest
from fastmcp import Client



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 3),
        (0, 0, 0),
        (-3, -7, -10),
    ],
)
async def test_add(mcp_client: Client, a: int, b: int, expected: int):
    result = await mcp_client.call_tool("add", {"a": a, "b": b})
    assert result.data == expected